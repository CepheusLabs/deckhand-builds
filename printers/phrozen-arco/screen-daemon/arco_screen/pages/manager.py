"""PageManager — orchestrates page lifecycle, touch routing, and status dispatch."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

from ..nextion import TouchData, TouchEvent
from ._base import PageContext, PageHandler

# Import all page handler classes
from .home import HomePage, StandbyPage
from .printing import PrintingPage, PrintPlanPage, PrintFinishPage, GetreadyPage, WaitPage
from .temperature_pages import TemperaturePage, SetTemPage
from .controls import ManualPage, ExtruderPage, SetSpeedPage, SetFlowPage, OffdetPage
from .filament import FilamentPage, MonochromePage
from .files import PrintFileBrowserPage, UsbPage
from .settings import (
    SystemPage, SetTimePage, WifiPage, CoolingPage, UpdatePage,
    ToolPage, PrintToolPage, SetSdPage, LanguagePage,
    UpdateCheckPage, ChoosePage, HerdwarePage, SettingPage,
)
from .calibration import (
    AutoLevelPage, CalibrationCailPage, CuttArcoPage, CuttCailPage,
    CheckPage, CuttCheckingPage,
)
from .dialogs import Popup1Page, Popup2Page, IfReprintPage, NoButLoadPage
from .setup import (
    FirstnamePage, FirstwificonPage, WificonPage, HomekeyPage,
    LiftingPage, FirstPage, FirstwifiPage,
)
from .info import InfoPage, StatesPage, HistoryPage, LocalPage, PolychromePage, SocialPage, InfoNavPage

log = logging.getLogger(__name__)

# All page classes in registration order
ALL_PAGE_CLASSES: list[type[PageHandler]] = [
    HomePage, PrintingPage, TemperaturePage, SetTemPage, ManualPage,
    ExtruderPage, FilamentPage, MonochromePage, SystemPage,
    SetSpeedPage, SetFlowPage, StandbyPage, PrintPlanPage,
    PrintFinishPage, GetreadyPage, AutoLevelPage, InfoPage,
    OffdetPage, PrintFileBrowserPage, Popup1Page, Popup2Page,
    SetTimePage, WifiPage, CoolingPage, CheckPage, WaitPage,
    UpdatePage, UsbPage, CalibrationCailPage, CuttArcoPage,
    CuttCailPage, NoButLoadPage, IfReprintPage, FirstnamePage,
    FirstwificonPage, WificonPage, HomekeyPage, LiftingPage,
    StatesPage,
    ToolPage, PrintToolPage, HistoryPage, SetSdPage,
    LanguagePage, UpdateCheckPage, LocalPage, ChoosePage,
    CuttCheckingPage, HerdwarePage, FirstPage,
    FirstwifiPage, PolychromePage, SettingPage, SocialPage,
    InfoNavPage,
]


def _build_binary_touch_map() -> dict[int, dict]:
    """Touch dispatch table from voronFDM binary — DISABLED.

    IMPORTANT: voronFDM uses custom 0x99/0x01 frame types with its own
    page numbering (pages 1-15), NOT the standard TJC 0x65/0x66 page IDs
    (pages 1-61) that our daemon receives. The packed values below use
    voronFDM's numbering and will NEVER match standard TJC touch events.

    The ACTION definitions are preserved in BINARY_ANALYSIS.md as a
    reference for what each button SHOULD do. Use the screen_map.json
    touch_map (name-based) to add new button handlers as CIDs are
    discovered through live testing.

    Known voronFDM → TFT page ID correspondences (confirmed):
      voronFDM page 12 = TFT home (page 12)  — happens to match
      voronFDM page 14 = TFT tool (page 14)  — happens to match
      All other voronFDM pages use different IDs from TFT standard.

    Key actions from binary (use in screen_map.json when CIDs are found):
      extruder extrude: M83 G1 E{1,10,20,50} F300
      extruder retract: M83 G1 E-{1,10,20,50} F300
      manual jog X: G91 G1 X{±1,±10,±50} F6000-F7800
      manual jog Y: G91 G1 Y{±1,±10,±50} F6000-F7800
      manual jog Z: G91 G1 Z{±0.05,±0.1,±1,±10} F600
      calibration entry: G91 G1 Z10 G90, G28 Y, G28 X → page c_cail
      nozzle wipe: retract → fan on → move → fan off → home → disable
      speed presets: M220 S{50,80,100,120,150}
      print pause: PRZ_PAUSE
      print resume: PRZ_RESUME
      print cancel: PRZ_CANCEL
    """
    m: dict[int, dict] = {}
    log.info("Binary touch map disabled (voronFDM page IDs ≠ TJC page IDs)")
    return m


class PageManager:
    """Manages page lifecycle, touch routing, and status update dispatch."""

    def __init__(self, ctx: PageContext, map_file: Path | None = None) -> None:
        self.ctx = ctx
        self.nx = ctx.nextion
        self.mr = ctx.moonraker
        self.config = ctx.config
        self._pages: dict[str, PageHandler] = {}
        self._page_id_map: dict[int, str] = {}
        self._touch_map: dict[str, dict[int, dict]] = {}
        self._active_page: PageHandler | None = None
        self._active_page_name: str | None = None
        self._standby_timer: asyncio.Task | None = None
        self._last_touch_time: float = time.monotonic()
        self._temp_target_heater: str = "extruder"  # tracks which heater settem is editing
        self._pending_temp: int = 0  # last numpad value seen on settem
        self._temp_debounce_task: asyncio.Task | None = None
        self._jog_step: float = 1.0  # current manual jog step size (mm)

        # Touch dispatch by (touch_page_id, component_id) from voronFDM binary.
        # Touch events carry TFT-internal page IDs that differ from the 0x66
        # page report IDs.  This table is keyed by the packed value
        # (touch_page_id << 8 | component_id) extracted from the binary's
        # Uart_pthread_cmd switch statement.
        self._binary_touch_map = _build_binary_touch_map()

        self._register_all_pages()
        if map_file:
            self.load_screen_map(map_file)

    def _register_all_pages(self) -> None:
        for cls in ALL_PAGE_CLASSES:
            handler = cls(self.ctx)
            self._pages[handler.PAGE_NAME] = handler

    def load_screen_map(self, path: Path) -> None:
        try:
            data = json.loads(path.read_text())
            self._page_id_map = {int(k): v for k, v in data.get("page_ids", {}).items()}
            self._touch_map = {
                page: {int(cid): action for cid, action in comps.items()}
                for page, comps in data.get("touch_map", {}).items()
            }
            total = sum(len(v) for v in self._touch_map.values())
            log.info("Loaded screen map: %d pages, %d touch mappings from %s",
                     len(self._page_id_map), total, path)
        except FileNotFoundError:
            log.warning("No screen map at %s", path)
        except (json.JSONDecodeError, KeyError) as e:
            log.error("Failed to load screen map from %s: %s", path, e)

    def get_page(self, name: str) -> PageHandler | None:
        return self._pages.get(name)

    async def navigate(self, page_name: str) -> None:
        if page_name not in self._pages:
            log.warning("Unknown page: %s", page_name)
            return
        self._active_page_name = page_name
        self._active_page = self._pages[page_name]
        await self.nx.set_page(page_name)
        try:
            await self._active_page.on_enter()
        except Exception as e:
            log.error("Page enter error on %s: %s", page_name, e)
        log.info("Navigated to page: %s", page_name)

    async def handle_touch(self, touch: TouchData) -> None:
        # Accept both PRESS and RELEASE — some TFT buttons only fire RELEASE
        # (e.g., confirm/enter buttons on numpad pages).
        self._last_touch_time = time.monotonic()
        self._reset_standby_timer()

        if self._active_page_name == "standby":
            await self.ctx.led.restore_from_standby()
            await self.navigate("home")
            return

        # Detect page changes from touch event page_ids.
        # The TFT handles nav bar navigation internally without sending 0x66
        # page reports. Touch events carry the REAL page_id, so if it differs
        # from our tracked page, update our active page tracking.
        #
        # FILTER: page_id=1 cid=1 is generic nav bar noise (fires on most
        # nav taps). page_id=0 cid=0 is background noise. Skip these to
        # avoid false page switches.
        is_nav_noise = (touch.page_id <= 1 and touch.component_id <= 1)
        touch_page_name = self._page_id_map.get(touch.page_id)
        if (not is_nav_noise
                and touch_page_name
                and touch_page_name != self._active_page_name
                and touch_page_name in self._pages):
            prev = self._active_page_name
            self._active_page_name = touch_page_name
            self._active_page = self._pages[touch_page_name]
            log.info("Page change detected from touch event: %s -> %s (page_id=%d)",
                     prev, touch_page_name, touch.page_id)
            try:
                await self._active_page.on_enter()
            except Exception as e:
                log.error("Page enter error on %s: %s", touch_page_name, e)

        # Primary dispatch: name-based from screen_map.json (real-world mappings)
        page_map = self._touch_map.get(self._active_page_name or "", {})
        action = page_map.get(touch.component_id)
        if action:
            log.debug("screen_map dispatch: page=%s cid=%d -> %s",
                      self._active_page_name, touch.component_id, action)
            await self._execute_action(action)
            return

        # Fallback: binary dispatch from voronFDM disassembly
        packed = (touch.page_id << 8) | touch.component_id
        binary_action = self._binary_touch_map.get(packed)
        if binary_action:
            log.debug("Binary touch dispatch: 0x%04x -> %s", packed, binary_action)
            await self._execute_binary_action(binary_action)
            return

        # No mapping found — log at INFO for touch discovery, then pass to page handler
        log.info("Unmapped touch: page_name=%s page_id=%d cid=%d event=%s "
                 "(add to screen_map.json touch_map.%s.%d)",
                 self._active_page_name, touch.page_id, touch.component_id,
                 touch.event.name, self._active_page_name or "?", touch.component_id)
        if self._active_page:
            await self._active_page.on_touch(touch)

    async def _execute_action(self, action: dict) -> None:
        kind = action.get("action", "")
        if kind == "navigate":
            # Track heater context for temp-setting pages
            if "heater" in action:
                self._temp_target_heater = action["heater"]
            await self.navigate(action.get("target", "home"))
        elif kind == "gcode":
            cmd = action.get("command", "")
            if cmd:
                try:
                    await self.mr.send_gcode(cmd)
                except Exception as e:
                    log.error("GCode action failed: %s — %s", cmd, e)
        elif kind == "emergency_stop":
            await self.mr.emergency_stop()
        elif kind == "setting":
            await self._handle_setting(action.get("key", ""), action)
        elif kind == "internal":
            pass  # TFT firmware handles this button internally
        else:
            log.warning("Unknown action type: %s", action)

    async def _handle_setting(self, key: str, action: dict) -> None:
        if key == "led_toggle":
            await self.ctx.led.toggle()
            await self.ctx.led.update_screen_icon(self._active_page_name or "home")
        elif key == "speed_preset":
            await self.mr.send_gcode(f"M220 S{action.get('value', 100)}")
        elif key == "speed_up":
            new = min(300, int(self.mr.state.speed_factor * 100) + 5)
            await self.mr.send_gcode(f"M220 S{new}")
        elif key == "speed_down":
            new = max(10, int(self.mr.state.speed_factor * 100) - 5)
            await self.mr.send_gcode(f"M220 S{new}")
        elif key == "flow_set":
            await self.mr.send_gcode(f"M221 S{action.get('value', 100)}")
        elif key == "flow_up":
            new = min(200, int(self.mr.state.extrude_factor * 100) + 5)
            await self.mr.send_gcode(f"M221 S{new}")
        elif key == "flow_down":
            new = max(50, int(self.mr.state.extrude_factor * 100) - 5)
            await self.mr.send_gcode(f"M221 S{new}")
        elif key == "extrude":
            await self.mr.send_gcode(f"M83\nG1 E{action.get('value', 10)} F300")
        elif key == "retract":
            await self.mr.send_gcode(f"M83\nG1 E-{action.get('value', 10)} F300")
        elif key == "z_offset_up":
            amt = action.get("value", 0.05)
            await self.mr.send_gcode(f"SET_GCODE_OFFSET Z_ADJUST=+{amt:.3f} MOVE=1")
        elif key == "z_offset_down":
            amt = action.get("value", 0.05)
            await self.mr.send_gcode(f"SET_GCODE_OFFSET Z_ADJUST=-{amt:.3f} MOVE=1")
        elif key == "fan_speed":
            s_val = int(int(action.get("value", 0)) * 255 / 100)
            await self.mr.send_gcode(f"M106 S{s_val}")
        elif key == "fan_off":
            await self.mr.send_gcode("M106 S0")
        elif key == "fan_assist":
            await self.mr.send_gcode(f"SET_PIN PIN=fan_assist VALUE={float(action.get('value', 0)):.0f}")
        elif key == "nozzle_temp":
            await self.ctx.temperature.set_nozzle_target(int(action.get("value", 0)))
        elif key == "bed_temp":
            await self.ctx.temperature.set_bed_target(int(action.get("value", 0)))
        elif key == "led_set":
            await self.mr.send_gcode(f"P0 LED_State={int(action.get('value', 0))}")
        elif key == "pause_print":
            await self.mr.send_gcode("PRZ_PAUSE")
        elif key == "resume_print":
            await self.mr.send_gcode("PRZ_RESUME")
        elif key == "cancel_print":
            await self.mr.send_gcode("PRZ_CANCEL")
        elif key == "home_all":
            await self.mr.send_gcode("G28")
        elif key == "home_x":
            await self.mr.send_gcode("G28 X")
        elif key == "home_y":
            await self.mr.send_gcode("G28 Y")
        elif key == "jog_step":
            self._jog_step = float(action.get("value", 1))
            log.info("Jog step size set to %.2f mm", self._jog_step)
        elif key == "jog_x_left":
            step = self._jog_step
            feed = 7800 if step >= 50 else 6000
            await self.mr.send_gcode(f"G91\nG1 X-{step} F{feed}\nG90")
        elif key == "jog_x_right":
            step = self._jog_step
            feed = 7800 if step >= 50 else 6000
            await self.mr.send_gcode(f"G91\nG1 X{step} F{feed}\nG90")
        elif key == "jog_y_back":
            step = self._jog_step
            feed = 7800 if step >= 50 else 6000
            await self.mr.send_gcode(f"G91\nG1 Y-{step} F{feed}\nG90")
        elif key == "jog_y_forward":
            step = self._jog_step
            feed = 7800 if step >= 50 else 6000
            await self.mr.send_gcode(f"G91\nG1 Y{step} F{feed}\nG90")
        elif key == "jog_z_up":
            step = self._jog_step
            await self.mr.send_gcode(f"G91\nG1 Z{step} F600\nG90")
        elif key == "jog_z_down":
            step = self._jog_step
            await self.mr.send_gcode(f"G91\nG1 Z-{step} F600\nG90")
        elif key == "disable_steppers":
            await self.mr.send_gcode("M84")
        elif key == "bed_mesh_calibrate":
            await self.mr.send_gcode("BED_MESH_CALIBRATE PROFILE=phrozen")
        elif key == "bed_mesh_clear":
            await self.mr.send_gcode("BED_MESH_CLEAR")
        elif key == "pid_nozzle":
            await self.mr.send_gcode("M303")
        elif key == "pid_bed":
            await self.mr.send_gcode("M304")
        elif key == "wipe_nozzle":
            await self.mr.send_gcode("PRZ_WIPEMOUTH")
        elif key == "purge":
            await self.mr.send_gcode("PRZ_SPITTING")
        elif key == "start_print":
            await self.mr.send_gcode("PRZ_PRINTING_START")
        elif key == "restore":
            await self.mr.send_gcode("PRZ_RESTORE")
        elif key == "set_kinematic_z":
            z = float(action.get("value", 100))
            await self.mr.send_gcode(f"SET_KINEMATIC_POSITION Z={z:.3f}")
        elif key == "version_query":
            await self.mr.send_gcode("prz_version")
        elif key == "temp_confirm":
            # Explicit confirm button (cid=18) — apply immediately
            await self._apply_temp_value()
        elif key == "temp_numpad_update":
            # cid=170 fires on every numpad interaction. The enter/back buttons
            # on settem don't send UART events, so we debounce: after 1.5s of
            # no more cid=170 events, auto-apply the last value.
            raw = self.nx.last_string_data
            if raw:
                try:
                    self._pending_temp = int(raw.strip())
                except (ValueError, TypeError):
                    pass
            # Cancel any previous debounce timer
            if self._temp_debounce_task and not self._temp_debounce_task.done():
                self._temp_debounce_task.cancel()
            self._temp_debounce_task = asyncio.ensure_future(self._temp_debounce())
        else:
            log.info("Setting action: %s = %s", key, action.get("value"))

    async def _apply_temp_value(self) -> None:
        """Apply the pending temperature value and navigate home.

        The TFT's enter button has an internal press animation; we wait
        800ms for it to finish before sending our page command.
        """
        await self._apply_temp_value_no_nav()
        await asyncio.sleep(0.8)
        await self.navigate("home")

    async def _apply_temp_value_no_nav(self) -> None:
        """Apply the pending temperature value (don't navigate — caller handles that)."""
        temp = self._pending_temp
        heater = self._temp_target_heater
        log.info("Temp confirm: %s -> %d°C", heater, temp)
        if temp > 0:
            try:
                await self.mr.send_gcode(
                    f"SET_HEATER_TEMPERATURE HEATER={heater} TARGET={temp}"
                )
            except Exception as e:
                log.error("Failed to set %s temp: %s", heater, e)
        self._pending_temp = 0

    async def _temp_debounce(self) -> None:
        """Safety-net: if no page report fires within 3s of the last numpad
        event, apply the pending temp anyway.  The primary path is
        handle_page_report detecting the TFT's own navigation away from settem."""
        await asyncio.sleep(3.0)
        if self._pending_temp > 0 and self._active_page_name == "settem":
            log.info("Temp debounce expired — applying pending temp (safety net)")
            await self._apply_temp_value_no_nav()

    async def _execute_binary_action(self, action: dict) -> None:
        """Execute an action from the binary touch dispatch table."""
        kind = action.get("type", "")

        if kind == "gcode":
            cmds = action.get("commands", [])
            for cmd in cmds:
                try:
                    await self.mr.send_gcode(cmd)
                except Exception as e:
                    log.error("Binary touch GCode failed: %s — %s", cmd, e)

        elif kind == "navigate":
            target = action.get("target", "")
            if target in self._pages:
                await self.navigate(target)
            else:
                # Send raw page command for pages we don't manage
                await self.nx.set_page(target)

        elif kind == "sequence":
            # Multi-step handler: run a series of GCode + navigations
            for step in action.get("steps", []):
                step_type = step.get("type", "")
                if step_type == "gcode":
                    try:
                        await self.mr.send_gcode(step["command"])
                    except Exception as e:
                        log.error("Sequence GCode failed: %s — %s", step["command"], e)
                elif step_type == "navigate":
                    if step["target"] in self._pages:
                        await self.navigate(step["target"])
                    else:
                        await self.nx.set_page(step["target"])
                elif step_type == "screen":
                    # Raw Nextion command
                    await self.nx.send_command(step["command"])
                elif step_type == "setting":
                    await self._handle_setting(step["key"], step)

        elif kind == "setting":
            await self._handle_setting(action.get("key", ""), action)

    async def handle_page_report(self, page_id: int) -> None:
        prev_page = self._active_page_name
        page_name = self._page_id_map.get(page_id)

        # If we were on a temp-setting page and the TFT navigated away
        # (user hit enter/back), apply the pending temperature value.
        if prev_page in ("settem", "extruder") and page_name != prev_page and self._pending_temp > 0:
            log.info("Left settem via TFT nav — applying pending temp")
            await self._apply_temp_value_no_nav()

        if page_name and page_name in self._pages:
            self._active_page_name = page_name
            self._active_page = self._pages[page_name]
            try:
                await self._active_page.on_enter()
            except Exception as e:
                log.error("Page enter error on %s: %s", page_name, e)
            log.info("Screen reported page change: id=%d name=%s", page_id, page_name)
        else:
            log.debug("Unknown page ID report: %d", page_id)

    async def handle_status_update(self, status: dict[str, Any]) -> None:
        if self._active_page:
            try:
                await self._active_page.on_status_update(status)
            except Exception as e:
                log.error("Page status update error on %s: %s", self._active_page_name, e)

        if "print_stats" in status and "state" in status["print_stats"]:
            new_state = status["print_stats"]["state"]
            if new_state == "printing" and self._active_page_name != "printing":
                await self.navigate("printing")
            elif new_state == "paused" and self._active_page_name == "printing":
                await self.navigate("wait")
            elif new_state == "complete" and self._active_page_name in ("printing", "wait"):
                await self.navigate("printfinish")
            elif new_state == "standby" and self._active_page_name in ("printing", "printfinish", "wait"):
                await self.navigate("home")

    def _reset_standby_timer(self) -> None:
        if self._standby_timer:
            self._standby_timer.cancel()
        timeout = self.config.machine.standby_timeout_min * 60
        if timeout > 0:
            self._standby_timer = asyncio.ensure_future(self._standby_countdown(timeout))

    async def _standby_countdown(self, seconds: float) -> None:
        await asyncio.sleep(seconds)
        if self.mr.state.print_state not in ("printing", "paused"):
            log.info("Standby timeout reached")
            await self.navigate("standby")

    async def startup(self) -> None:
        await self.navigate("home")
        self._reset_standby_timer()
