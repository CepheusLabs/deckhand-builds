"""File browser and USB page handlers."""

from __future__ import annotations

import logging
from typing import Any

from ._base import PageContext, PageHandler, PIC_USB_INACTIVE, PIC_USB_DEVICE

log = logging.getLogger(__name__)


class PrintFileBrowserPage(PageHandler):
    """Components: NAME, j0, pwifi, t0 (size), usb (pic)"""
    PAGE_NAME = "print"

    def __init__(self, ctx: PageContext) -> None:
        super().__init__(ctx)
        self._files: list[dict] = []
        self._page_offset: int = 0

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_pic("print.usb", PIC_USB_INACTIVE)
        await self._load_files()
        await self._show_storage()

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass

    async def _load_files(self) -> None:
        try:
            result = await self.mr.get_file_list()
            if isinstance(result, dict):
                self._files = result.get("files", [])
                self._files.sort(key=lambda f: f.get("modified", 0), reverse=True)
            self._page_offset = 0
            await self._render_page()
        except Exception as e:
            log.error("Failed to fetch file list: %s", e)

    async def _render_page(self) -> None:
        page_files = self._files[self._page_offset:self._page_offset + 3]
        for i in range(1, 4):
            has = (i - 1) < len(page_files)
            await self.nx.set_vis(f"lol{i}", has)

    async def _show_storage(self) -> None:
        try:
            result = await self.mr._request(None, "server.files.get_directory",
                                            {"root": "gcodes", "extended": False})
            if isinstance(result, dict):
                disk = result.get("disk_usage", {})
                used_gb = disk.get("used", 0) / (1024 ** 3)
                total_gb = disk.get("total", 0) / (1024 ** 3)
                await self.nx.set_txt("print.t0", f"{used_gb:.1f}G / {total_gb:.1f}G")
                if disk.get("total", 0) > 0:
                    await self.nx.set_val("print.j0", int(disk["used"] / disk["total"] * 100))
        except Exception:
            pass


class UsbPage(PageHandler):
    """Components: NAME, path, pwifi, usbno"""
    PAGE_NAME = "usb"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_pic("usb.usbno", PIC_USB_DEVICE)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass
