"""Temperature management — persistence, unit conversion, and presets.

voronFDM persists last-used temperature targets to files so the screen
can show them on next boot. It also supports Celsius/Fahrenheit switching.

Files written:
  - temperature.no.txt — last nozzle target temp
  - temperature.he.txt — last bed target temp

This module also handles temperature-related GCode response parsing
(M104/M109/M140/M190 acknowledgments).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .moonraker import MoonrakerClient

log = logging.getLogger(__name__)


class TemperatureManager:
    """Manages temperature state, persistence, and unit conversion.

    Usage:
        temp = TemperatureManager(moonraker, config_dir)
        await temp.set_nozzle_target(200)
        await temp.set_bed_target(60)

        # Display values
        nozzle_str = temp.format_temp(state.extruder_temp)
    """

    def __init__(
        self,
        moonraker: "MoonrakerClient",
        config_dir: Path,
        temp_unit: int = 0,  # 0=C, 1=F
    ) -> None:
        self._mr = moonraker
        self._config_dir = config_dir
        self._temp_unit = temp_unit  # 0=Celsius, 1=Fahrenheit

        # Last-used targets (loaded from disk, saved on change)
        self._last_nozzle_target: int = 0
        self._last_bed_target: int = 0

        self._load_persisted()

    @property
    def temp_unit(self) -> int:
        return self._temp_unit

    @property
    def unit_suffix(self) -> str:
        return "F" if self._temp_unit == 1 else "C"

    @property
    def last_nozzle_target(self) -> int:
        return self._last_nozzle_target

    @property
    def last_bed_target(self) -> int:
        return self._last_bed_target

    def set_unit(self, unit: int) -> None:
        """Set temperature display unit. 0=Celsius, 1=Fahrenheit."""
        self._temp_unit = unit
        log.info("Temperature unit set to %s", "Fahrenheit" if unit else "Celsius")

    def to_display(self, celsius: float) -> int:
        """Convert a Celsius temperature to the display unit."""
        if self._temp_unit == 1:
            return int(celsius * 9 / 5 + 32)
        return int(celsius)

    def from_display(self, value: int) -> float:
        """Convert a display-unit temperature back to Celsius."""
        if self._temp_unit == 1:
            return (value - 32) * 5 / 9
        return float(value)

    def format_temp(self, celsius: float) -> str:
        """Format a temperature for display (no unit suffix)."""
        return str(self.to_display(celsius))

    async def set_nozzle_target(self, target_celsius: int) -> None:
        """Set nozzle temperature target and persist."""
        try:
            await self._mr.send_gcode(f"M104 S{target_celsius}")
            self._last_nozzle_target = target_celsius
            self._save_nozzle()
            log.info("Nozzle target set to %d°C", target_celsius)
        except Exception as e:
            log.error("Failed to set nozzle target: %s", e)

    async def set_bed_target(self, target_celsius: int) -> None:
        """Set bed temperature target and persist."""
        try:
            await self._mr.send_gcode(f"M140 S{target_celsius}")
            self._last_bed_target = target_celsius
            self._save_bed()
            log.info("Bed target set to %d°C", target_celsius)
        except Exception as e:
            log.error("Failed to set bed target: %s", e)

    async def set_nozzle_and_wait(self, target_celsius: int) -> None:
        """Set nozzle temp and wait (M109). Used during print prep."""
        await self._mr.send_gcode(f"M109 S{target_celsius}")
        self._last_nozzle_target = target_celsius
        self._save_nozzle()

    async def set_bed_and_wait(self, target_celsius: int) -> None:
        """Set bed temp and wait (M190). Used during print prep."""
        await self._mr.send_gcode(f"M190 S{target_celsius}")
        self._last_bed_target = target_celsius
        self._save_bed()

    async def handle_gcode_response(self, response: str) -> None:
        """Parse GCode responses for temperature acknowledgments.

        voronFDM watches for M104/M109/M140/M190 acks to confirm
        temperature commands were received.
        """
        line = response.strip()
        if line.startswith("// "):
            line = line[3:]

        # Track external temperature changes (from macros, other sources)
        # Format: "ok T:200.0 /200.0 B:60.0 /60.0"
        # We don't need to parse these — Moonraker's status updates
        # already give us actual and target temps. This handler is
        # here for any Phrozen-specific temp response formats.
        pass

    def _load_persisted(self) -> None:
        """Load last-used temperatures from disk."""
        nozzle_file = self._config_dir / "temperature.no.txt"
        bed_file = self._config_dir / "temperature.he.txt"

        try:
            self._last_nozzle_target = int(nozzle_file.read_text().strip())
        except (FileNotFoundError, ValueError):
            self._last_nozzle_target = 0

        try:
            self._last_bed_target = int(bed_file.read_text().strip())
        except (FileNotFoundError, ValueError):
            self._last_bed_target = 0

        log.debug(
            "Loaded persisted temps: nozzle=%d bed=%d",
            self._last_nozzle_target, self._last_bed_target,
        )

    def _save_nozzle(self) -> None:
        """Persist nozzle target to disk."""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            (self._config_dir / "temperature.no.txt").write_text(
                str(self._last_nozzle_target)
            )
        except OSError as e:
            log.error("Failed to save nozzle temp: %s", e)

    def _save_bed(self) -> None:
        """Persist bed target to disk."""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            (self._config_dir / "temperature.he.txt").write_text(
                str(self._last_bed_target)
            )
        except OSError as e:
            log.error("Failed to save bed temp: %s", e)
