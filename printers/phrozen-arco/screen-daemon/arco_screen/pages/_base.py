"""Base classes, shared context, and constants for page handlers.

Every page handler module imports from here to get PageContext,
PageHandler, the pic-ID constants, and the _get_local_ip helper.
"""

from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from ..nextion import Nextion, TouchData
from ..moonraker import MoonrakerClient

if TYPE_CHECKING:
    from ..config import ScreenDaemonConfig
    from ..ams import AMSManager
    from ..led import LEDManager
    from ..temperature import TemperatureManager
    from ..print_time import PrintTimeEstimator

log = logging.getLogger(__name__)

# --- Pic ID constants (from voronFDM binary) ---
PIC_WIFI_DISCONNECTED = 11
PIC_WIFI_CONNECTED = 12
PIC_BTN_PAUSE = 52       # printing.b1 pause state
PIC_BTN_RESUME = 53      # printing.b1 resume state
PIC_BTN2_STATE1 = 102    # printing.b2 state 1
PIC_BTN2_STATE2 = 103    # printing.b2 state 2
PIC_USB_INACTIVE = 71
PIC_USB_ACTIVE = 72
PIC_USB_SECONDARY = 134
PIC_Z_AXIS = 98
PIC_XY_PLANE = 100
PIC_PLAN_INACTIVE = 168
PIC_PLAN_ACTIVE = 169
PIC_PLAN_BUTTON = 281
PIC_WIFI_LIST = 76
PIC_WIFI_STATUS = 81
PIC_WIFI_PICTURE = 84
PIC_USB_DEVICE = 151
PIC_STANDBY_LED_OFF = 52
PIC_STANDBY_LED_ON = 53


def _get_local_ip() -> str:
    """Get the printer's local IP address."""
    try:
        result = subprocess.run(
            ["hostname", "-I"],
            capture_output=True, text=True, timeout=2,
        )
        ip = result.stdout.strip().split()[0]
        return f"IP:{ip}"
    except Exception:
        return "IP:--"


@dataclass
class PageContext:
    """Shared context passed to all page handlers."""
    nextion: Nextion
    moonraker: MoonrakerClient
    config: "ScreenDaemonConfig"
    ams: "AMSManager"
    led: "LEDManager"
    temperature: "TemperatureManager"
    print_time: "PrintTimeEstimator"


class PageHandler(ABC):
    """Base class for screen page handlers."""
    PAGE_NAME: str = ""

    def __init__(self, ctx: PageContext) -> None:
        self.nx = ctx.nextion
        self.mr = ctx.moonraker
        self.config = ctx.config
        self.ams = ctx.ams
        self.led = ctx.led
        self.temp_mgr = ctx.temperature
        self.print_time = ctx.print_time
        self.ctx = ctx

    @abstractmethod
    async def on_enter(self) -> None:
        """Called when this page becomes active."""

    @abstractmethod
    async def on_status_update(self, status: dict[str, Any]) -> None:
        """Called when Klipper status changes while this page is active."""

    async def on_touch(self, touch: TouchData) -> None:
        """Called when a touch event occurs on this page."""
        log.debug("%s: unhandled touch cid=%d event=%s",
                  self.PAGE_NAME, touch.component_id, touch.event.name)

    async def _set_wifi_icon(self) -> None:
        pic = PIC_WIFI_CONNECTED if self.mr.connected else PIC_WIFI_DISCONNECTED
        await self.nx.set_pic(f"{self.PAGE_NAME}.pwifi", pic)

    async def _set_name(self) -> None:
        await self.nx.set_txt(f"{self.PAGE_NAME}.NAME", self.config.machine.name)

    async def _common_enter(self) -> None:
        await self._set_wifi_icon()
        await self._set_name()


class _StubPage(PageHandler):
    """Minimal handler for pages that only need NAME + pwifi."""

    async def on_enter(self) -> None:
        await self._common_enter()

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


def _make_stub(name: str) -> type:
    """Create a stub page handler class for simple NAME+pwifi pages."""
    return type(f"{name.title()}Page", (_StubPage,), {"PAGE_NAME": name})
