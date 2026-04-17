"""Settings page handlers: system, wifi, time, cooling, update, etc."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler, _make_stub, _get_local_ip


class SystemPage(PageHandler):
    """Components: NAME, pwifi, sys_data, temname, time"""
    PAGE_NAME = "system"

    async def on_enter(self) -> None:
        await self._common_enter()
        ams_val = 1 if self.config.ams.chromakit_enabled else 0
        await self.nx.set_val("system.sys_data", ams_val)
        await self.nx.set_txt("system.time", f"{self.config.machine.standby_timeout_min} min")
        await self.nx.set_txt("system.temname", self.config.machine.name)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class SetTimePage(PageHandler):
    """Components: NAME, min, min_num, pwifi, setime"""
    PAGE_NAME = "settime"

    async def on_enter(self) -> None:
        await self._common_enter()
        t = self.config.machine.standby_timeout_min
        await self.nx.set_txt("settime.min", f"{t} min")
        await self.nx.set_val("settime.min_num", t)
        await self.nx.set_val("settime.setime", t)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class WifiPage(PageHandler):
    """Components: NAME, ip, pwifi, wifi1/wifi1pic/wifi1st (x3)"""
    PAGE_NAME = "setwifi"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_txt("setwifi.ip", _get_local_ip())
        for i in range(1, 4):
            for suffix in ("", "pic", "st"):
                await self.nx.set_vis(f"wifi{i}{suffix}", False)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class CoolingPage(PageHandler):
    """Components: CFAN_NUM, NAME, pwifi"""
    PAGE_NAME = "Chamber_fan"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_val("Chamber_fan.CFAN_NUM", int(self.mr.state.chamber_fan_speed * 100))

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "fan_generic Chamber_fan" in status:
            await self.nx.set_val("Chamber_fan.CFAN_NUM", int(self.mr.state.chamber_fan_speed * 100))


class UpdatePage(PageHandler):
    """Components: L_update, dev, j0, n0"""
    PAGE_NAME = "update"

    async def on_enter(self) -> None:
        await self.nx.set_val("update.dev", 1)
        await self.nx.set_val("update.n0", 0)
        await self.nx.set_val("update.j0", 0)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


# Simple stub pages
ToolPage = _make_stub("tool")
PrintToolPage = _make_stub("print_tool")
SetSdPage = _make_stub("setsd")
LanguagePage = _make_stub("language")
UpdateCheckPage = _make_stub("update_check")
ChoosePage = _make_stub("choose")
HerdwarePage = _make_stub("herdware")
SettingPage = _make_stub("setting")
