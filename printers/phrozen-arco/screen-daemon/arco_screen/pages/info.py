"""Info and status page handlers."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler, _make_stub


class InfoPage(PageHandler):
    """Components: NAME, ams_sum, pwifi, t0, vv_1-vv_5, vv_sum"""
    PAGE_NAME = "printerinfo"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_txt("printerinfo.t0", self.config.machine.name)
        await self.nx.set_txt("printerinfo.ams_sum", str(self.ams.connected_count))
        await self.nx.set_txt("printerinfo.vv_sum", "v0.2.0")
        for i, unit in enumerate(self.ams.units[:4], 1):
            sn = unit.serial_number if unit.connected else "--"
            await self.nx.set_txt(f"printerinfo.vv_{i}", sn)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class StatesPage(PageHandler):
    """Components: STA, edata"""
    PAGE_NAME = "states"

    async def on_enter(self) -> None:
        pass

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


# Stubs
HistoryPage = _make_stub("history")
LocalPage = _make_stub("local")
PolychromePage = _make_stub("polychrome")
SocialPage = _make_stub("social")
InfoNavPage = _make_stub("info")
