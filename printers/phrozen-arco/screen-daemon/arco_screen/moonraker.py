"""Moonraker WebSocket client.

Connects to Moonraker's WebSocket API to:
- Subscribe to printer object status updates
- Send GCode commands
- Query file listings, print history, server info
- Start/pause/cancel prints

The client auto-reconnects on disconnect and re-subscribes to objects.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

import websockets
from websockets.exceptions import ConnectionClosed

log = logging.getLogger(__name__)

DEFAULT_URL = "ws://localhost:7125/websocket"

# Moonraker JSON-RPC request IDs — use distinct ranges so we can identify
# response types without tracking every request.
_ID_SUBSCRIBE = 73705  # matches stock voronFDM for compatibility
_ID_PRINTER_INFO = 84848
_ID_SERVER_INFO = 12567
_ID_COUNTER_START = 100000

# The full set of Klipper objects to subscribe to, matching stock voronFDM.
# Non-existent objects are silently ignored by Klipper, so we can list
# everything without worrying about which modules are loaded.
SUBSCRIBE_OBJECTS = {
    "webhooks": None,
    "mcu": None,
    "mcu MKS_THR": None,
    "heaters": None,
    "fan_generic cooling_fan": None,
    "output_pin fan_assist": None,
    "heater_bed": None,
    "temperature_sensor Chamber_sensor": None,
    "fan_generic Chamber_fan": None,
    "stepper_enable": None,
    "controller_fan board_fan": None,
    "fan": None,
    "idle_timeout": None,
    "gcode_move": None,
    "probe": None,
    "bed_mesh": None,
    "print_stats": None,
    "virtual_sdcard": None,
    "pause_resume": None,
    "display_status": None,
    "motion_report": None,
    "query_endstops": None,
    "toolhead": None,
    "extruder": None,
    # TMC steppers (for stepper status/diagnostics)
    "tmc2209 stepper_x": None,
    "tmc2209 stepper_y": None,
    "tmc2209 stepper_z": None,
    "tmc2209 stepper_z1": None,
    "tmc2209 extruder": None,
    # Timelapse macros (from voronFDM binary)
    "gcode_macro GET_TIMELAPSE_SETUP": None,
    "gcode_macro _SET_TIMELAPSE_SETUP": None,
    "gcode_macro TIMELAPSE_TAKE_FRAME": None,
    "gcode_macro _TIMELAPSE_NEW_FRAME": None,
    "gcode_macro HYPERLAPSE": None,
    "gcode_macro TIMELAPSE_RENDER": None,
    "gcode_macro TEST_STREAM_DELAY": None,
}

# Type for status update callbacks
StatusCallback = Callable[[dict[str, Any]], Awaitable[None]]
# Type for gcode response callbacks
GCodeResponseCallback = Callable[[str], Awaitable[None]]


@dataclass
class PrinterState:
    """Cached printer state from Moonraker subscriptions."""

    # Temperatures
    extruder_temp: float = 0.0
    extruder_target: float = 0.0
    bed_temp: float = 0.0
    bed_target: float = 0.0
    chamber_temp: float = 0.0

    # Fans
    fan_speed: float = 0.0  # Part cooling (0-1)
    fan_assist_value: float = 0.0  # Aux fan (0-1)
    chamber_fan_speed: float = 0.0

    # Print state
    print_state: str = "standby"  # standby, printing, paused, complete, cancelled, error
    filename: str = ""
    progress: float = 0.0  # 0.0 - 1.0
    print_duration: float = 0.0  # seconds
    filament_used: float = 0.0  # mm
    total_duration: float = 0.0

    # Position
    x_position: float = 0.0
    y_position: float = 0.0
    z_position: float = 0.0
    z_offset: float = 0.0

    # Movement
    speed_factor: float = 1.0  # M220 factor
    extrude_factor: float = 1.0  # M221 factor

    # System
    klipper_state: str = "disconnected"  # ready, error, shutdown, startup, disconnected
    is_paused: bool = False

    # Raw data for anything we haven't parsed
    raw: dict = field(default_factory=dict)

    def update_from_status(self, status: dict[str, Any]) -> None:
        """Update state from a Moonraker status notification."""
        self.raw.update(status)

        if "extruder" in status:
            ext = status["extruder"]
            if "temperature" in ext:
                self.extruder_temp = ext["temperature"]
            if "target" in ext:
                self.extruder_target = ext["target"]

        if "heater_bed" in status:
            bed = status["heater_bed"]
            if "temperature" in bed:
                self.bed_temp = bed["temperature"]
            if "target" in bed:
                self.bed_target = bed["target"]

        if "temperature_sensor Chamber_sensor" in status:
            ch = status["temperature_sensor Chamber_sensor"]
            if "temperature" in ch:
                self.chamber_temp = ch["temperature"]

        if "fan" in status:
            f = status["fan"]
            if "speed" in f:
                self.fan_speed = f["speed"]

        if "output_pin fan_assist" in status:
            fa = status["output_pin fan_assist"]
            if "value" in fa:
                self.fan_assist_value = fa["value"]

        if "fan_generic Chamber_fan" in status:
            cf = status["fan_generic Chamber_fan"]
            if "speed" in cf:
                self.chamber_fan_speed = cf["speed"]

        if "print_stats" in status:
            ps = status["print_stats"]
            if "state" in ps:
                self.print_state = ps["state"]
            if "filename" in ps:
                self.filename = ps["filename"]
            if "print_duration" in ps:
                self.print_duration = ps["print_duration"]
            if "filament_used" in ps:
                self.filament_used = ps["filament_used"]
            if "total_duration" in ps:
                self.total_duration = ps["total_duration"]

        if "virtual_sdcard" in status:
            vs = status["virtual_sdcard"]
            if "progress" in vs:
                self.progress = vs["progress"]

        if "display_status" in status:
            ds = status["display_status"]
            if "progress" in ds:
                self.progress = ds["progress"]

        if "gcode_move" in status:
            gm = status["gcode_move"]
            if "gcode_position" in gm:
                pos = gm["gcode_position"]
                if len(pos) >= 3:
                    self.x_position = pos[0]
                    self.y_position = pos[1]
                    self.z_position = pos[2]
            if "homing_origin" in gm:
                origin = gm["homing_origin"]
                if len(origin) >= 3:
                    self.z_offset = origin[2]
            if "speed_factor" in gm:
                self.speed_factor = gm["speed_factor"]
            if "extrude_factor" in gm:
                self.extrude_factor = gm["extrude_factor"]

        if "toolhead" in status:
            th = status["toolhead"]
            if "position" in th:
                pos = th["position"]
                if len(pos) >= 3:
                    self.x_position = pos[0]
                    self.y_position = pos[1]
                    self.z_position = pos[2]

        if "pause_resume" in status:
            pr = status["pause_resume"]
            if "is_paused" in pr:
                self.is_paused = pr["is_paused"]

        if "webhooks" in status:
            wh = status["webhooks"]
            if "state" in wh:
                self.klipper_state = wh["state"]


class MoonrakerClient:
    """Async WebSocket client for Moonraker API.

    Usage:
        client = MoonrakerClient()
        client.on_status_update(my_handler)
        await client.connect()

        await client.send_gcode("G28")
        files = await client.get_file_list()
        await client.start_print("test.gcode")
    """

    def __init__(self, url: str = DEFAULT_URL, dry_run: bool = False) -> None:
        self._url = url
        self._dry_run = dry_run
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._connected = asyncio.Event()
        self._status_handlers: list[StatusCallback] = []
        self._gcode_response_handlers: list[GCodeResponseCallback] = []
        self._pending: dict[int, asyncio.Future] = {}
        self._id_counter = _ID_COUNTER_START
        self._recv_task: asyncio.Task | None = None
        self._reconnect_task: asyncio.Task | None = None
        self.state = PrinterState()

    def on_status_update(self, handler: StatusCallback) -> None:
        """Register a callback for printer status updates."""
        self._status_handlers.append(handler)

    def on_gcode_response(self, handler: GCodeResponseCallback) -> None:
        """Register a callback for GCode console responses.

        voronFDM uses this to parse temperature acknowledgments (M104/M109/M140/M190),
        AMS responses (+P114, +AMSERROR, +Mode), and custom Phrozen responses.
        """
        self._gcode_response_handlers.append(handler)

    async def connect(self) -> None:
        """Connect to Moonraker and subscribe to printer objects."""
        await self._do_connect()

    async def _do_connect(self) -> None:
        try:
            self._ws = await websockets.connect(
                self._url,
                ping_interval=10,
                ping_timeout=30,
                close_timeout=5,
            )
            self._connected.set()
            log.info("Connected to Moonraker at %s", self._url)

            # Start receive loop
            self._recv_task = asyncio.ensure_future(self._recv_loop())

            # Subscribe to printer objects
            await self._subscribe()

            # Get initial printer info
            await self._request(_ID_PRINTER_INFO, "printer.info")

        except Exception as e:
            log.error("Failed to connect to Moonraker: %s", e)
            self._connected.clear()
            self._schedule_reconnect()

    async def _subscribe(self) -> None:
        """Subscribe to printer object updates."""
        await self._request(
            _ID_SUBSCRIBE,
            "printer.objects.subscribe",
            {"objects": SUBSCRIBE_OBJECTS},
        )

    async def _recv_loop(self) -> None:
        """Read messages from the WebSocket."""
        try:
            async for raw in self._ws:
                try:
                    msg = json.loads(raw)
                    await self._handle_message(msg)
                except json.JSONDecodeError:
                    log.warning("Invalid JSON from Moonraker: %s", raw[:200])
        except ConnectionClosed as e:
            log.warning("Moonraker WebSocket closed: %s", e)
        except Exception as e:
            log.error("Moonraker recv error: %s", e)
        finally:
            self._connected.clear()
            self._ws = None
            self._schedule_reconnect()

    async def _handle_message(self, msg: dict) -> None:
        """Dispatch incoming WebSocket messages."""
        # JSON-RPC notification (status update)
        if "method" in msg:
            method = msg["method"]
            params = msg.get("params", [{}])

            if method == "notify_status_update" and params:
                status = params[0] if isinstance(params, list) else params
                self.state.update_from_status(status)
                for handler in self._status_handlers:
                    try:
                        await handler(status)
                    except Exception as e:
                        log.error("Status handler error: %s", e)

            elif method == "notify_klippy_ready":
                self.state.klipper_state = "ready"
                log.info("Klipper is ready")
                # Re-subscribe after Klipper restart
                await self._subscribe()

            elif method == "notify_klippy_shutdown":
                self.state.klipper_state = "shutdown"
                log.warning("Klipper shutdown")

            elif method == "notify_klippy_disconnected":
                self.state.klipper_state = "disconnected"
                log.warning("Klipper disconnected")

            elif method == "notify_gcode_response":
                # GCode console output — this is how phrozen_dev reports
                # AMS status back (e.g. +P114:0, +Mode:1,MC, etc.)
                if params:
                    response = params[0] if isinstance(params, list) else str(params)
                    log.debug("GCode response: %s", response)
                    for handler in self._gcode_response_handlers:
                        try:
                            await handler(response)
                        except Exception as e:
                            log.error("GCode response handler error: %s", e)

        # JSON-RPC response (to our requests)
        elif "id" in msg:
            req_id = msg["id"]
            if req_id in self._pending:
                future = self._pending.pop(req_id)
                if "error" in msg:
                    future.set_exception(
                        MoonrakerError(msg["error"].get("message", str(msg["error"])))
                    )
                else:
                    result = msg.get("result", {})
                    future.set_result(result)

                    # Handle subscription response — contains initial state
                    if req_id == _ID_SUBSCRIBE and isinstance(result, dict):
                        status = result.get("status", {})
                        if status:
                            self.state.update_from_status(status)

    def _schedule_reconnect(self) -> None:
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.ensure_future(self._reconnect_loop())

    async def _reconnect_loop(self) -> None:
        delay = 1.0
        while not self._connected.is_set():
            log.info("Reconnecting to Moonraker in %.1fs...", delay)
            await asyncio.sleep(delay)
            await self._do_connect()
            delay = min(delay * 2, 30.0)

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    async def _request(
        self,
        req_id: int | None,
        method: str,
        params: dict | None = None,
    ) -> Any:
        """Send a JSON-RPC request and wait for the response."""
        if not self._connected.is_set():
            raise MoonrakerError("Not connected to Moonraker")

        if req_id is None:
            req_id = self._next_id()

        msg: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "id": req_id,
        }
        if params:
            msg["params"] = params

        future: asyncio.Future = asyncio.get_running_loop().create_future()
        self._pending[req_id] = future

        await self._ws.send(json.dumps(msg))
        return await asyncio.wait_for(future, timeout=30.0)

    # --- Public API ---

    async def send_gcode(self, script: str) -> Any:
        """Send a GCode command to Klipper.

        Args:
            script: GCode string (can be multi-line with \\n)
        """
        log.info("GCode: %s", script.replace("\n", " | "))
        if self._dry_run:
            log.info("DRY-RUN: %s", script.replace("\n", " | "))
            # Update mock state for temp commands so the screen reflects changes
            upper = script.upper()
            if "SET_HEATER_TEMPERATURE" in upper:
                import re
                heater_m = re.search(r'HEATER=(\S+)', script, re.IGNORECASE)
                target_m = re.search(r'TARGET=(\d+)', script, re.IGNORECASE)
                if heater_m and target_m:
                    heater = heater_m.group(1)
                    target = float(target_m.group(1))
                    if heater == "extruder":
                        self.state.extruder_target = target
                    elif heater == "heater_bed":
                        self.state.bed_target = target
                    # Fire status update so pages refresh
                    status = {heater: {"target": target}}
                    for handler in self._status_handlers:
                        asyncio.ensure_future(handler(status))
            return None
        return await self._request(
            None, "printer.gcode.script", {"script": script}
        )

    async def emergency_stop(self) -> Any:
        """Trigger an emergency stop."""
        log.warning("EMERGENCY STOP")
        return await self._request(None, "printer.emergency_stop")

    async def restart_klipper(self) -> Any:
        """Restart Klipper service."""
        return await self._request(
            None, "machine.services.restart", {"service": "klipper"}
        )

    async def firmware_restart(self) -> Any:
        """Firmware restart (MCU reset)."""
        return await self._request(None, "printer.firmware_restart")

    async def start_print(self, filename: str) -> Any:
        """Start printing a file.

        Args:
            filename: Path relative to gcodes root
        """
        log.info("Starting print: %s", filename)
        return await self._request(
            None, "printer.print.start", {"filename": filename}
        )

    async def pause_print(self) -> Any:
        """Pause the current print via Klipper's PAUSE command."""
        return await self.send_gcode("PRZ_PAUSE")

    async def resume_print(self) -> Any:
        """Resume a paused print via Klipper's RESUME command."""
        return await self.send_gcode("PRZ_RESUME")

    async def cancel_print(self) -> Any:
        """Cancel the current print."""
        return await self.send_gcode("PRZ_CANCEL")

    async def get_file_list(self, path: str = "gcodes") -> dict:
        """Get directory listing from Moonraker.

        Args:
            path: Directory path (default "gcodes")
        """
        return await self._request(
            None,
            "server.files.get_directory",
            {"root": "gcodes", "path": path, "extended": True},
        )

    async def get_print_history(self, limit: int = 50) -> dict:
        """Get print job history."""
        return await self._request(
            None, "server.history.list", {"limit": limit}
        )

    async def delete_history(self) -> dict:
        """Clear all print history."""
        return await self._request(
            None, "server.history.delete_job", {"all": True}
        )

    async def get_server_info(self) -> dict:
        """Get Moonraker server info."""
        return await self._request(_ID_SERVER_INFO, "server.info")

    async def get_printer_info(self) -> dict:
        """Get Klipper printer info."""
        return await self._request(_ID_PRINTER_INFO, "printer.info")

    async def copy_file(self, source: str, dest: str) -> dict:
        """Copy a file within the gcodes directory."""
        return await self._request(
            None, "server.files.copy", {"source": source, "dest": dest}
        )

    async def delete_file(self, path: str) -> dict:
        """Delete a file."""
        return await self._request(
            None, "server.files.delete_file", {"path": path}
        )

    @property
    def connected(self) -> bool:
        return self._connected.is_set()

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self._reconnect_task:
            self._reconnect_task.cancel()
        if self._recv_task:
            self._recv_task.cancel()
        if self._ws:
            await self._ws.close()
        self._connected.clear()
        log.info("Moonraker connection closed")


class MoonrakerError(Exception):
    """Error from Moonraker API."""

    pass
