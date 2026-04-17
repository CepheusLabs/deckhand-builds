"""Control page handlers: manual movement, extruder, speed, flow, z-offset."""

from __future__ import annotations

from typing import Any

from ._base import PageHandler, PIC_XY_PLANE, PIC_Z_AXIS


class ManualPage(PageHandler):
    """Components: NAME, pwifi, xy (pic=100), z (pic=98)"""
    PAGE_NAME = "manual"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_pic("manual.xy", PIC_XY_PLANE)
        await self.nx.set_pic("manual.z", PIC_Z_AXIS)

    async def on_status_update(self, status: dict[str, Any]) -> None:
        pass


class ExtruderPage(PageHandler):
    """Components: NAME, bex, ex, pwifi"""
    PAGE_NAME = "extruder"

    async def on_enter(self) -> None:
        await self._common_enter()
        s = self.mr.state
        await self.nx.set_val("extruder.ex", int(s.extruder_target))
        await self.nx.set_txt("extruder.bex", self.temp_mgr.format_temp(s.extruder_temp))

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "extruder" in status:
            s = self.mr.state
            await self.nx.set_val("extruder.ex", int(s.extruder_target))
            await self.nx.set_txt("extruder.bex", self.temp_mgr.format_temp(s.extruder_temp))


class SetSpeedPage(PageHandler):
    """Components: NAME, pwifi, sp, sp1, spdata, spdata1"""
    PAGE_NAME = "setsp"

    async def on_enter(self) -> None:
        await self._common_enter()
        s = self.mr.state
        speed = int(s.speed_factor * 100)
        flow = int(s.extrude_factor * 100)
        await self.nx.set_val("setsp.sp", speed)
        await self.nx.set_val("setsp.sp1", flow)
        await self.nx.set_txt("setsp.spdata", f"{speed}%")
        await self.nx.set_txt("setsp.spdata1", f"{flow}%")

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "gcode_move" in status:
            s = self.mr.state
            speed = int(s.speed_factor * 100)
            flow = int(s.extrude_factor * 100)
            await self.nx.set_val("setsp.sp", speed)
            await self.nx.set_val("setsp.sp1", flow)
            await self.nx.set_txt("setsp.spdata", f"{speed}%")
            await self.nx.set_txt("setsp.spdata1", f"{flow}%")


class SetFlowPage(PageHandler):
    """Components: NAME, flowdata, pwifi, sp"""
    PAGE_NAME = "flow"

    async def on_enter(self) -> None:
        await self._common_enter()
        flow = int(self.mr.state.extrude_factor * 100)
        await self.nx.set_val("flow.sp", flow)
        await self.nx.set_txt("flow.flowdata", f"{flow}%")

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "gcode_move" in status:
            flow = int(self.mr.state.extrude_factor * 100)
            await self.nx.set_val("flow.sp", flow)
            await self.nx.set_txt("flow.flowdata", f"{flow}%")


class OffdetPage(PageHandler):
    """Components: NAME, pwifi, z_offset"""
    PAGE_NAME = "offdet"

    async def on_enter(self) -> None:
        await self._common_enter()
        await self.nx.set_txt("offdet.z_offset", f"{self.mr.state.z_offset:.3f}")

    async def on_status_update(self, status: dict[str, Any]) -> None:
        if "gcode_move" in status:
            await self.nx.set_txt("offdet.z_offset", f"{self.mr.state.z_offset:.3f}")
