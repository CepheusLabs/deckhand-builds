"""Printing-related page handlers: active print, plan, finish, getready, wait."""

from __future__ import annotations

import logging
from typing import Any

from ._base import (
    PageContext, PageHandler,
    PIC_BTN_PAUSE, PIC_BTN_RESUME, PIC_BTN2_STATE1,
    PIC_PLAN_INACTIVE, PIC_PLAN_ACTIVE, PIC_PLAN_BUTTON,
    _get_local_ip,
)

log = logging.getLogger(__name__)


class PrintingPage(PageHandler):
    """Components: NAME, PRINT_IP, b1, b2, cname, j0, mm, num1-num6,
    pwifi, t1-t6, t15, t16"""
    PAGE_NAME = "printing"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self._full_update()

    async def on_status_update(self, status: dict[str, Any]) -> None:
        s = self.mr.state
        if "virtual_sdcard" in status or "display_status" in status:
            pct = int(s.progress * 100)
            await self.nx.set_val("printing.j0", pct)
            self.print_time.update(s.progress, s.print_duration)
            await self._update_time()

        if "print_stats" in status:
            if s.filename:
                await self.nx.set_txt("printing.cname", self._trim_filename(s.filename))

        if "extruder" in status:
            await self.nx.set_txt("printing.t1", self.temp_mgr.format_temp(s.extruder_temp))
            await self.nx.set_txt("printing.t2", self.temp_mgr.format_temp(s.extruder_target))

        if "heater_bed" in status:
            await self.nx.set_txt("printing.t5", self.temp_mgr.format_temp(s.bed_temp))
            await self.nx.set_txt("printing.t6", self.temp_mgr.format_temp(s.bed_target))

        if "fan" in status:
            await self.nx.set_txt("printing.t3", str(int(s.fan_speed * 100)))

        if "gcode_move" in status:
            await self.nx.set_txt("printing.t4", str(int(s.speed_factor * 100)))

        if "toolhead" in status:
            await self.nx.set_txt("printing.t15", str(int(s.z_position)))
            await self.nx.set_txt("printing.t16", f"{s.z_position:.2f}")

    async def _full_update(self) -> None:
        s = self.mr.state
        pct = int(s.progress * 100)
        await self.nx.set_val("printing.j0", pct)
        await self.nx.set_txt("printing.t1", self.temp_mgr.format_temp(s.extruder_temp))
        await self.nx.set_txt("printing.t2", self.temp_mgr.format_temp(s.extruder_target))
        await self.nx.set_txt("printing.t5", self.temp_mgr.format_temp(s.bed_temp))
        await self.nx.set_txt("printing.t6", self.temp_mgr.format_temp(s.bed_target))
        await self.nx.set_txt("printing.t3", str(int(s.fan_speed * 100)))
        await self.nx.set_txt("printing.t4", str(int(s.speed_factor * 100)))
        await self.nx.set_txt("printing.t15", str(int(s.z_position)))
        await self.nx.set_txt("printing.t16", f"{s.z_position:.2f}")

        if s.filename:
            await self.nx.set_txt("printing.cname", self._trim_filename(s.filename))

        self.print_time.update(s.progress, s.print_duration)
        await self._update_time()

        if s.is_paused:
            await self.nx.set_pic("printing.b1", PIC_BTN_RESUME)
        else:
            await self.nx.set_pic("printing.b1", PIC_BTN_PAUSE)
        await self.nx.set_pic("printing.b2", PIC_BTN2_STATE1)

        await self.led.update_screen_icon("printing")
        await self.nx.set_txt("printing.PRINT_IP", _get_local_ip())
        await self.nx.set_txt("printing.mm", f"({int(s.z_position)}")
        await self.nx.set_vis("pams", self.ams.any_connected)

    async def _update_time(self) -> None:
        remaining = self.print_time.remaining_seconds
        hours = remaining // 3600
        mins = (remaining % 3600) // 60
        await self.nx.set_val("printing.num1", hours)
        await self.nx.set_val("printing.num2", mins)

    @staticmethod
    def _trim_filename(filename: str) -> str:
        name = filename.rsplit("/", 1)[-1]
        if name.endswith(".gcode"):
            name = name[:-6]
        return name


class PrintPlanPage(PageHandler):
    """Components: au, but, plan_judge, t0-t4, t7, xz"""
    PAGE_NAME = "printplan"

    async def on_enter(self) -> None:
        await self.nx.set_val("printplan.plan_judge", 0)
        await self.nx.set_pic("printplan.au", PIC_PLAN_INACTIVE)
        await self.nx.set_pic("printplan.xz", PIC_PLAN_INACTIVE)
        await self.nx.set_pic("printplan.but", PIC_PLAN_BUTTON)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass

    async def set_file_info(self, filename: str, est_time_sec: int = 0,
                            est_height_mm: float = 0, source: str = "local") -> None:
        name = filename.rsplit("/", 1)[-1]
        if name.endswith(".gcode"):
            name = name[:-6]
        await self.nx.set_txt("printplan.t0", name)
        if est_time_sec > 0:
            h, m = est_time_sec // 3600, (est_time_sec % 3600) // 60
            await self.nx.set_txt("printplan.t1", f"{h} H {m} M")
        else:
            await self.nx.set_txt("printplan.t1", "-- H -- M")
        if est_height_mm > 0:
            await self.nx.set_txt("printplan.t2", f"{est_height_mm:.2f} M")
        else:
            await self.nx.set_txt("printplan.t2", "-- M")
        await self.nx.set_txt("printplan.t7", source)
        await self.nx.set_val("printplan.plan_judge", 1)
        await self.nx.set_pic("printplan.au", PIC_PLAN_ACTIVE)
        await self.nx.set_pic("printplan.xz", PIC_PLAN_ACTIVE)


class PrintFinishPage(PageHandler):
    """Components: NAME, fname, pwifi, t1, t2"""
    PAGE_NAME = "printfinish"

    async def on_enter(self) -> None:
        await self._common_enter()
        s = self.mr.state
        if s.filename:
            name = s.filename.rsplit("/", 1)[-1]
            if name.endswith(".gcode"):
                name = name[:-6]
            await self.nx.set_txt("printfinish.fname", name)
        total = int(s.total_duration)
        await self.nx.set_txt("printfinish.t1", f"{total // 3600} H {(total % 3600) // 60} M")
        cm = s.filament_used / 10.0
        if cm >= 100:
            await self.nx.set_txt("printfinish.t2", f"{int(cm) // 100}.{int(cm) % 100:02d}m")
        else:
            await self.nx.set_txt("printfinish.t2", f"{int(cm)}.{int((cm - int(cm)) * 10)}cm")

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class GetreadyPage(PageHandler):
    """Components: get_num (1-7)"""
    PAGE_NAME = "getready"

    async def on_enter(self) -> None:
        await self.nx.set_val("getready.get_num", 1)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass

    async def set_stage(self, stage: int) -> None:
        await self.nx.set_val("getready.get_num", max(1, min(7, stage)))


class WaitPage(PageHandler):
    """Components: update_j, wait_data"""
    PAGE_NAME = "wait"

    async def on_enter(self) -> None:
        await self.nx.set_val("wait.wait_data", 1)
        await self.nx.set_val("wait.update_j", int(self.mr.state.progress * 100))

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "virtual_sdcard" in status or "display_status" in status:
            await self.nx.set_val("wait.update_j", int(self.mr.state.progress * 100))
