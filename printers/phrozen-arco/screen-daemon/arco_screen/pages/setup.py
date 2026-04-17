"""First-run setup page handlers."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler, _make_stub, _get_local_ip


class FirstnamePage(PageHandler):
    """Components: NAME, pwifi, t0"""
    PAGE_NAME = "firstname"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_txt("firstname.t0", self.config.machine.name)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class FirstwificonPage(PageHandler):
    """Components: t1"""
    PAGE_NAME = "firstwificon"

    async def on_enter(self) -> None:
        await self.nx.set_txt("firstwificon.t1", _get_local_ip())

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class WificonPage(PageHandler):
    """Components: t1"""
    PAGE_NAME = "wificon"

    async def on_enter(self) -> None:
        await self.nx.set_txt("wificon.t1", _get_local_ip())

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class HomekeyPage(PageHandler):
    """Components: t0"""
    PAGE_NAME = "homekey"

    async def on_enter(self) -> None:
        pass

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class LiftingPage(PageHandler):
    """Components: firstnum"""
    PAGE_NAME = "lifting"

    async def on_enter(self) -> None:
        await self.nx.set_val("lifting.firstnum", 3)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


# Stubs
FirstPage = _make_stub("first")
FirstwifiPage = _make_stub("firstwifi")
