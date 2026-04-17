"""Filament and AMS page handlers."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler


class FilamentPage(PageHandler):
    """Components: NAME, ams1-4, bex, ex, fil_num (-2 to 4), pwifi"""
    PAGE_NAME = "filament"

    async def on_enter(self) -> None:
        await self._common_enter()
        s = self.mr.state
        await self.nx.set_val("filament.ex", int(s.extruder_target))
        await self.nx.set_txt("filament.bex", self.temp_mgr.format_temp(s.extruder_temp))
        for i in range(1, 5):
            active = 1 if self.ams.units[i - 1].connected else 0
            await self.nx.set_val(f"filament.ams{i}", active)
        await self.nx.set_val("filament.fil_num", self.ams.active_tray)
        for i in range(1, 5):
            c = self.ams.units[i - 1].connected
            await self.nx.set_vis(f"A{i}", c)
            await self.nx.set_vis(f"BA{i}", c)
            await self.nx.set_vis(f"CA{i}", c)
        await self.nx.set_vis("BA", self.ams.any_connected)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status:
            s = self.mr.state
            await self.nx.set_val("filament.ex", int(s.extruder_target))
            await self.nx.set_txt("filament.bex", self.temp_mgr.format_temp(s.extruder_temp))


class MonochromePage(PageHandler):
    """Components: NAME, bex, ex, pwifi"""
    PAGE_NAME = "monochrome"

    async def on_enter(self) -> None:
        await self._common_enter()
        s = self.mr.state
        await self.nx.set_val("monochrome.ex", int(s.extruder_target))
        await self.nx.set_txt("monochrome.bex", self.temp_mgr.format_temp(s.extruder_temp))

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status:
            s = self.mr.state
            await self.nx.set_val("monochrome.ex", int(s.extruder_target))
            await self.nx.set_txt("monochrome.bex", self.temp_mgr.format_temp(s.extruder_temp))
