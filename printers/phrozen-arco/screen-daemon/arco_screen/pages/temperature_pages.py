"""Temperature page handlers."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler


class TemperaturePage(PageHandler):
    """Components: NAME, he, he1, no, no1, nozz, pwifi"""
    PAGE_NAME = "temperature"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self._update_temps()

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status or "heater_bed" in status:
            await self._update_temps()

    async def _update_temps(self) -> None:
        s = self.mr.state
        await self.nx.set_txt("temperature.no", self.temp_mgr.format_temp(s.extruder_temp))
        await self.nx.set_txt("temperature.no1", self.temp_mgr.format_temp(s.extruder_target))
        await self.nx.set_txt("temperature.he", self.temp_mgr.format_temp(s.bed_temp))
        await self.nx.set_txt("temperature.he1", self.temp_mgr.format_temp(s.bed_target))
        await self.nx.set_val("temperature.nozz", int(s.extruder_target))


class SetTemPage(PageHandler):
    """Components: t0"""
    PAGE_NAME = "settem"

    async def on_enter(self) -> None:
        await self.nx.set_txt("settem.t0", self.temp_mgr.format_temp(self.mr.state.extruder_temp))

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status:
            await self.nx.set_txt("settem.t0", self.temp_mgr.format_temp(self.mr.state.extruder_temp))
