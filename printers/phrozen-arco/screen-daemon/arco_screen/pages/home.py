"""Home and standby page handlers."""

from __future__ import annotations

import logging
from typing import Any

from ..nextion import TouchData
from ._base import (
    PageContext, PageHandler,
    PIC_STANDBY_LED_OFF, PIC_STANDBY_LED_ON, _get_local_ip,
)

log = logging.getLogger(__name__)


class HomePage(PageHandler):
    """Components: NAME, pwifi, t0 (bed temp), t1 (nozzle temp)"""
    PAGE_NAME = "home"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self._update_temps()
        await self.led.update_screen_icon("home")

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status or "heater_bed" in status:
            await self._update_temps()

    async def on_touch(self, touch: TouchData) -> None:
        if touch.component_id == 9:  # LED toggle
            await self.led.toggle()
            await self.led.update_screen_icon("home")

    async def _update_temps(self) -> None:
        s = self.mr.state
        await self.nx.set_txt("home.t0", self.temp_mgr.format_temp(s.bed_temp))
        await self.nx.set_txt("home.t1", self.temp_mgr.format_temp(s.extruder_temp))


class StandbyPage(PageHandler):
    """Components: NAME, PRINT_IP, b1, n0, n1, pwifi, sname"""
    PAGE_NAME = "standby"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_txt("standby.sname", self.config.machine.name)
        await self.nx.set_txt("standby.PRINT_IP", _get_local_ip())
        await self.nx.set_pic("standby.b1",
                              PIC_STANDBY_LED_ON if self.led.is_on else PIC_STANDBY_LED_OFF)
        self.led.save_standby_state()

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass

    async def on_touch(self, touch: TouchData) -> None:
        log.info("Standby wake-up touch")
