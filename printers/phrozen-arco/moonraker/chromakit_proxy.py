# ChromaKit Proxy - Moonraker Component
#
# Intercepts ChromaKit polling commands (P114, P0 LED_*) and responds
# from cache to prevent Klipper reactor flooding. All other commands
# pass through to Klipper normally.
#
# Install: copy to ~/moonraker/moonraker/components/chromakit_proxy.py
# Config:  add [chromakit_proxy] to moonraker.conf
#
# Copyright (C) 2026 CepheusLabs

from __future__ import annotations
import logging
import json
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..confighelper import ConfigHelper
    from ..common import WebRequest
    from .klippy_apis import KlippyAPI as APIComp


class ChromaKitProxy:
    def __init__(self, config: ConfigHelper) -> None:
        self.server = config.get_server()
        self.klippy_apis: APIComp = self.server.lookup_component("klippy_apis")

        # Cache for ChromaKit state
        self._p114_state: str = json.dumps({
            "dev_id": -1, "active_dev_id": -1, "dev_mode": -1,
            "cache_empty": -1, "cache_full": -1, "cache_exist": -1,
            "mc_state": -1, "ma_state": -1, "entry_state": -1,
            "park_state": -1,
        })
        self._mode_str: str = "+Mode:0,unkown"
        self._version_str: str = "V-H16-I16-F25384"
        self._led_state: int = 0
        self._cache_populated: bool = False

        # Commands to intercept (respond from cache)
        self._intercept_commands = {"P114", "P0 LED_GetState"}

        # Commands to block entirely
        self._block_prefixes = ["PRZ_OTA", "PRZ_UPDATE"]

        # Wrap the gcode script handler
        self._original_run_gcode = self.klippy_apis.run_gcode
        self.klippy_apis.run_gcode = self._intercepted_run_gcode

        # Listen for gcode responses to update cache
        self.server.register_event_handler(
            "server:gcode_response", self._handle_gcode_response
        )

        # Populate cache on first klippy connect
        self.server.register_event_handler(
            "server:klippy_ready", self._on_klippy_ready
        )

        logging.info("ChromaKit Proxy: loaded")

    async def _on_klippy_ready(self) -> None:
        """Send initial P114 to populate cache when Klipper starts."""
        if not self._cache_populated:
            logging.info("ChromaKit Proxy: populating initial cache...")
            try:
                await self._original_run_gcode("P114")
                self._cache_populated = True
            except Exception as e:
                logging.warning(f"ChromaKit Proxy: initial P114 failed: {e}")

    def _handle_gcode_response(self, response: str) -> None:
        """Update cache from gcode responses that flow through."""
        if not response:
            return

        # Capture P114 JSON state
        if response.startswith("{") and "dev_id" in response:
            self._p114_state = response

        # Capture mode
        elif response.startswith("+Mode:"):
            self._mode_str = response

        # Capture version
        elif response.startswith("V-H") and "-I" in response and "-F" in response:
            self._version_str = response

    async def _intercepted_run_gcode(
        self,
        script: str,
        default: Any = None,
    ) -> str:
        """Intercept gcode commands before they reach Klipper."""
        cmd = script.strip()

        # Block OTA commands
        for prefix in self._block_prefixes:
            if cmd.startswith(prefix):
                logging.info(f"ChromaKit Proxy: blocked {cmd}")
                return "ok"

        # Intercept polling commands
        if cmd in self._intercept_commands:
            return await self._handle_cached(cmd)

        # Everything else passes through to Klipper
        return await self._original_run_gcode(script, default)

    async def _handle_cached(self, cmd: str) -> str:
        """Respond to intercepted commands from cache."""

        if cmd == "P114":
            # Send cached responses as gcode_response events
            self.server.send_event(
                "server:gcode_response", "+P114:0"
            )
            self.server.send_event(
                "server:gcode_response", self._mode_str
            )
            self.server.send_event(
                "server:gcode_response", self._p114_state
            )
            self.server.send_event(
                "server:gcode_response", "+P114:1"
            )
            return "ok"

        elif cmd == "P0 LED_GetState":
            self.server.send_event(
                "server:gcode_response", self._version_str
            )
            return "ok"

        return "ok"


def load_component(config: ConfigHelper) -> ChromaKitProxy:
    return ChromaKitProxy(config)
