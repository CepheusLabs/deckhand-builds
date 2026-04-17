"""Calibration page handlers: auto-level, c_cail, cutt_arco, cutt_cail, check."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler, _make_stub


class AutoLevelPage(PageHandler):
    """Components: NAME, pwifi, t0, t1, temp_data"""
    PAGE_NAME = "auto"

    async def on_enter(self) -> None:
        await self._common_enter()
        s = self.mr.state
        await self.nx.set_txt("auto.t0", self.temp_mgr.format_temp(s.bed_temp))
        await self.nx.set_txt("auto.t1", self.temp_mgr.format_temp(s.extruder_temp))
        await self.nx.set_txt("auto.temp_data", self.temp_mgr.format_temp(s.extruder_temp))

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status or "heater_bed" in status:
            s = self.mr.state
            await self.nx.set_txt("auto.t0", self.temp_mgr.format_temp(s.bed_temp))
            await self.nx.set_txt("auto.t1", self.temp_mgr.format_temp(s.extruder_temp))
            await self.nx.set_txt("auto.temp_data", self.temp_mgr.format_temp(s.extruder_temp))


class CalibrationCailPage(PageHandler):
    """Components: NAME, c_cail_num, pwifi, setorfirst"""
    PAGE_NAME = "c_cail"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_val("c_cail.c_cail_num", 1)
        await self.nx.set_val("c_cail.setorfirst", 1)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class CuttArcoPage(PageHandler):
    """Components: NAME, cutt_arco_num, pwifi"""
    PAGE_NAME = "cutt_arco"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_val("cutt_arco.cutt_arco_num", 1)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class CuttCailPage(PageHandler):
    """Components: NAME, ams_num_cail, cutt_cail_num, pwifi"""
    PAGE_NAME = "cutt_cail"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_val("cutt_cail.cutt_cail_num", 1)
        await self.nx.set_val("cutt_cail.ams_num_cail", 1 if self.ams.any_connected else 0)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class CheckPage(PageHandler):
    """Components: NAME, p0, p1, p2, pwifi"""
    PAGE_NAME = "check"

    async def on_enter(self) -> None:
        await self._common_enter()

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


# Stub
CuttCheckingPage = _make_stub("cutt_checking")
