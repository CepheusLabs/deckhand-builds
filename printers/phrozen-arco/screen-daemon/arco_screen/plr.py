"""Power Loss Recovery (PLR).

Persists the current print state to disk so that after a power failure
and reboot, the daemon can offer to resume the interrupted print.

Uses A/B file rotation for corruption resistance — if power is lost
mid-write, at least one file is intact.

State is saved periodically (every N seconds) during printing, and
cleared when a print completes or is cancelled normally.

On startup, if a PLR state file exists with if_need_reprint=True,
the daemon navigates to the reprint confirmation page.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

from .moonraker import MoonrakerClient, PrinterState

log = logging.getLogger(__name__)

DEFAULT_PLR_DIR = Path("/home/mks/printer_data/config/arco_screen")
PLR_FILE_A = "plr_data_A.json"
PLR_FILE_B = "plr_data_B.json"
PLR_SAVE_INTERVAL = 5.0  # seconds between state saves during printing


@dataclass
class PLRState:
    """Snapshot of print state for recovery."""

    if_need_reprint: bool = False
    print_file_name: str = ""
    print_file_path: str = ""
    file_position: int = 0
    extruder_target: float = 0.0
    heater_bed_target: float = 0.0
    x_position: float = 0.0
    y_position: float = 0.0
    z_position: float = 0.0
    e_position: float = 0.0
    absolute_e: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent="\t")

    @classmethod
    def from_json(cls, text: str) -> "PLRState":
        data = json.loads(text)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_printer_state(cls, state: PrinterState) -> "PLRState":
        """Capture current print state for PLR."""
        return cls(
            if_need_reprint=True,
            print_file_name=state.filename.rsplit("/", 1)[-1] if state.filename else "",
            print_file_path=state.filename,
            file_position=0,  # Updated from virtual_sdcard
            extruder_target=state.extruder_target,
            heater_bed_target=state.bed_target,
            x_position=state.x_position,
            y_position=state.y_position,
            z_position=state.z_position,
            e_position=0.0,  # Would need gcode_move.extrude_position
            absolute_e=False,
        )


class PLRManager:
    """Manages power loss recovery state persistence.

    Usage:
        plr = PLRManager(moonraker_client)

        # On startup
        pending = plr.check_pending()
        if pending:
            # Show reprint dialog on screen
            ...

        # During printing
        plr.start_tracking()

        # On print complete/cancel
        plr.stop_tracking()
        plr.clear()
    """

    def __init__(
        self,
        moonraker: MoonrakerClient,
        plr_dir: Path = DEFAULT_PLR_DIR,
    ) -> None:
        self._mr = moonraker
        self._dir = plr_dir
        self._file_a = plr_dir / PLR_FILE_A
        self._file_b = plr_dir / PLR_FILE_B
        self._save_task: asyncio.Task | None = None
        self._tracking = False
        self._write_to_a = True  # Alternate between A and B

    def check_pending(self) -> PLRState | None:
        """Check if there's a pending reprint from a power loss.

        Returns PLRState if recovery is needed, None otherwise.
        Called once at daemon startup.
        """
        for path in (self._file_a, self._file_b):
            try:
                text = path.read_text()
                state = PLRState.from_json(text)
                if state.if_need_reprint:
                    log.info(
                        "PLR: Found pending reprint for '%s' in %s",
                        state.print_file_name, path.name,
                    )
                    return state
            except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
                log.debug("PLR: Cannot read %s: %s", path.name, e)
                continue
        return None

    def start_tracking(self) -> None:
        """Begin periodic state saves (call when print starts)."""
        if self._tracking:
            return
        self._tracking = True
        self._save_task = asyncio.ensure_future(self._save_loop())
        log.info("PLR: Started tracking print state")

    def stop_tracking(self) -> None:
        """Stop periodic state saves (call when print ends)."""
        self._tracking = False
        if self._save_task:
            self._save_task.cancel()
            self._save_task = None
        log.info("PLR: Stopped tracking")

    def clear(self) -> None:
        """Clear PLR state files (print completed normally)."""
        default = PLRState()
        text = default.to_json()
        try:
            self._file_a.write_text(text)
            self._file_b.write_text(text)
            log.info("PLR: Cleared recovery state")
        except OSError as e:
            log.error("PLR: Failed to clear state: %s", e)

    async def _save_loop(self) -> None:
        """Periodically save print state while tracking."""
        while self._tracking:
            await asyncio.sleep(PLR_SAVE_INTERVAL)
            if not self._tracking:
                break
            await self._save_current_state()

    async def _save_current_state(self) -> None:
        """Snapshot and write the current print state."""
        state = self._mr.state
        if state.print_state != "printing":
            return

        plr = PLRState.from_printer_state(state)

        # Get file position from virtual_sdcard if available
        vs = state.raw.get("virtual_sdcard", {})
        if "file_position" in vs:
            plr.file_position = vs["file_position"]

        # A/B rotation: write to one file, then the other
        target = self._file_a if self._write_to_a else self._file_b
        self._write_to_a = not self._write_to_a

        try:
            target.write_text(plr.to_json())
            log.debug("PLR: Saved state to %s (pos=%d)", target.name, plr.file_position)
        except OSError as e:
            log.error("PLR: Failed to save to %s: %s", target.name, e)

    async def resume_print(self, plr_state: PLRState) -> None:
        """Resume an interrupted print using saved PLR state.

        This sends the GCode sequence to restore temperatures, position,
        and resume from the saved file position.
        """
        log.info(
            "PLR: Resuming print '%s' at position %d",
            plr_state.print_file_name, plr_state.file_position,
        )

        # Heat up
        if plr_state.heater_bed_target > 0:
            await self._mr.send_gcode(
                f"SET_HEATER_TEMPERATURE HEATER=heater_bed TARGET={int(plr_state.heater_bed_target)}"
            )
        if plr_state.extruder_target > 0:
            await self._mr.send_gcode(
                f"SET_HEATER_TEMPERATURE HEATER=extruder TARGET={int(plr_state.extruder_target)}"
            )

        # Wait for temps
        if plr_state.heater_bed_target > 0:
            await self._mr.send_gcode(f"M190 S{int(plr_state.heater_bed_target)}")
        if plr_state.extruder_target > 0:
            await self._mr.send_gcode(f"M109 S{int(plr_state.extruder_target)}")

        # Home
        await self._mr.send_gcode("G28")

        # Move to last known position
        await self._mr.send_gcode("G90")
        await self._mr.send_gcode(
            f"G1 X{plr_state.x_position:.3f} Y{plr_state.y_position:.3f} F6000"
        )
        await self._mr.send_gcode(f"G1 Z{plr_state.z_position:.3f} F600")

        # Use PRZ_RESTORE if available (handles AMS state)
        await self._mr.send_gcode("PRZ_RESTORE")

        # Clear PLR state now that we've resumed
        self.clear()
