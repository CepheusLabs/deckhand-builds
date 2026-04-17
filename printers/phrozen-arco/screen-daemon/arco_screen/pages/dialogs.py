"""Dialog page handlers: popup1, popup2, if_reprint, NoButLoad."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler, _get_local_ip


class Popup1Page(PageHandler):
    """Components: pop_num"""
    PAGE_NAME = "popup1"

    async def on_enter(self) -> None:
        pass

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass

    async def show_dialog(self, dialog_type: int) -> None:
        await self.nx.set_val("popup1.pop_num", dialog_type)


class Popup2Page(PageHandler):
    """Components: ch, pop2_num, pop_txt, update_txt"""
    PAGE_NAME = "popup2"

    async def on_enter(self) -> None:
        pass

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass

    async def show_notification(self, ntype: int, text: str = "") -> None:
        await self.nx.set_val("popup2.pop2_num", ntype)
        if text:
            await self.nx.set_txt("popup2.pop_txt", text)


class IfReprintPage(PageHandler):
    PAGE_NAME = "if_reprint"

    async def on_enter(self) -> None:
        pass

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class NoButLoadPage(PageHandler):
    """Components: NAME, No_ip, pwifi"""
    PAGE_NAME = "NoButLoad"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_txt("NoButLoad.No_ip", _get_local_ip())

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass
