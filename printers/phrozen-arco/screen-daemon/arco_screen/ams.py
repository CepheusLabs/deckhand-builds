"""AMS (ChromaKit) live state tracking.

Parses GCode responses from Klipper's phrozen_dev module to track
AMS connection state, filament tray status, serial numbers, and errors.

voronFDM tracks:
  - G_AMSstate: overall AMS connection state
  - G_AmsData: per-tray filament data
  - v_AMS_SN1-SN4: serial numbers for up to 4 AMS units
  - +AMSERROR:N: error codes from AMS
  - +P114:N: tray selection responses
  - +Mode:N,XX: AMS operating mode

GCode responses come via Moonraker's notify_gcode_response and are
prefixed with "//" or "// " by Klipper.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)

# Max AMS units supported
MAX_AMS_UNITS = 4
# Max trays per AMS unit
TRAYS_PER_UNIT = 4
# Total possible trays
MAX_TRAYS = MAX_AMS_UNITS * TRAYS_PER_UNIT


@dataclass
class AMSTray:
    """State of a single filament tray in an AMS unit."""

    index: int = 0
    present: bool = False
    color: str = ""  # hex color e.g. "FF0000"
    material: str = ""  # e.g. "PLA", "PETG"
    temperature: int = 0  # nozzle temp for this material
    remaining: int = -1  # percentage remaining, -1 = unknown


@dataclass
class AMSUnit:
    """State of a single AMS (ChromaKit) unit."""

    index: int = 0
    connected: bool = False
    serial_number: str = ""
    firmware_version: str = ""
    trays: list[AMSTray] = field(default_factory=lambda: [
        AMSTray(index=i) for i in range(TRAYS_PER_UNIT)
    ])
    error_code: int = 0


class AMSManager:
    """Tracks live AMS state from GCode responses.

    Wire this up to MoonrakerClient.on_gcode_response() to receive
    AMS-related responses from Klipper's phrozen_dev module.

    Usage:
        ams = AMSManager()
        moonraker.on_gcode_response(ams.handle_gcode_response)

        # Query state
        if ams.any_connected:
            for unit in ams.units:
                if unit.connected:
                    ...
    """

    def __init__(self) -> None:
        self.units: list[AMSUnit] = [
            AMSUnit(index=i) for i in range(MAX_AMS_UNITS)
        ]
        self.active_tray: int = -1  # Currently selected tray (-1 = none)
        self.mode: str = ""  # Operating mode string
        self.mode_id: int = 0
        self.state: str = "idle"  # idle, loading, unloading, error
        self._listeners: list = []

    @property
    def any_connected(self) -> bool:
        """True if any AMS unit is connected."""
        return any(u.connected for u in self.units)

    @property
    def connected_count(self) -> int:
        """Number of connected AMS units."""
        return sum(1 for u in self.units if u.connected)

    def get_tray(self, tray_index: int) -> AMSTray | None:
        """Get tray by global index (0-15)."""
        if 0 <= tray_index < MAX_TRAYS:
            unit_idx = tray_index // TRAYS_PER_UNIT
            local_idx = tray_index % TRAYS_PER_UNIT
            return self.units[unit_idx].trays[local_idx]
        return None

    async def handle_gcode_response(self, response: str) -> None:
        """Parse a GCode response line for AMS-related data.

        Called from MoonrakerClient's notify_gcode_response handler.
        Responses from phrozen_dev are typically prefixed with "// ".
        """
        # Strip Klipper's prefix
        line = response.strip()
        if line.startswith("// "):
            line = line[3:]
        elif line.startswith("//"):
            line = line[2:]

        # +P114:N — tray selection response
        m = re.match(r"\+P114:(\d+)", line)
        if m:
            self.active_tray = int(m.group(1))
            log.info("AMS: Active tray set to %d", self.active_tray)
            return

        # +Mode:N,XX — operating mode
        m = re.match(r"\+Mode:(\d+),(\w+)", line)
        if m:
            self.mode_id = int(m.group(1))
            self.mode = m.group(2)
            log.info("AMS: Mode %d (%s)", self.mode_id, self.mode)
            return

        # +AMSERROR:N — error code
        m = re.match(r"\+AMSERROR:(\d+)", line)
        if m:
            error_code = int(m.group(1))
            self.state = "error"
            log.warning("AMS: Error code %d", error_code)
            # Set error on all connected units
            for unit in self.units:
                if unit.connected:
                    unit.error_code = error_code
            return

        # AMSCONNECT:N — unit connected/disconnected
        m = re.match(r"AMSCONNECT:(\d+),(\d+)", line)
        if m:
            unit_idx = int(m.group(1))
            connected = int(m.group(2)) == 1
            if 0 <= unit_idx < MAX_AMS_UNITS:
                self.units[unit_idx].connected = connected
                log.info(
                    "AMS: Unit %d %s",
                    unit_idx,
                    "connected" if connected else "disconnected",
                )
            return

        # AMS_SN:N,XXXX — serial number report
        m = re.match(r"AMS_SN:(\d+),(\S+)", line)
        if m:
            unit_idx = int(m.group(1))
            sn = m.group(2)
            if 0 <= unit_idx < MAX_AMS_UNITS:
                self.units[unit_idx].serial_number = sn
                log.info("AMS: Unit %d SN=%s", unit_idx, sn)
            return

        # AMS_TRAY:unit,tray,present,color,material,temp,remaining
        m = re.match(
            r"AMS_TRAY:(\d+),(\d+),(\d+),([0-9A-Fa-f]*),(\w*),(\d+),(-?\d+)",
            line,
        )
        if m:
            unit_idx = int(m.group(1))
            tray_idx = int(m.group(2))
            if 0 <= unit_idx < MAX_AMS_UNITS and 0 <= tray_idx < TRAYS_PER_UNIT:
                tray = self.units[unit_idx].trays[tray_idx]
                tray.present = int(m.group(3)) == 1
                tray.color = m.group(4)
                tray.material = m.group(5)
                tray.temperature = int(m.group(6))
                tray.remaining = int(m.group(7))
                log.debug(
                    "AMS: Unit %d Tray %d: present=%s material=%s color=%s",
                    unit_idx, tray_idx, tray.present, tray.material, tray.color,
                )
            return

    def to_screen_data(self) -> dict[str, Any]:
        """Export state for screen page handlers.

        Returns a dict suitable for updating Nextion components:
          - ams_connected: bool
          - ams_count: int
          - active_tray: int
          - trays: list of tray dicts
        """
        trays = []
        for unit in self.units:
            if unit.connected:
                for tray in unit.trays:
                    trays.append({
                        "present": tray.present,
                        "color": tray.color,
                        "material": tray.material,
                        "temp": tray.temperature,
                        "remaining": tray.remaining,
                    })
        return {
            "ams_connected": self.any_connected,
            "ams_count": self.connected_count,
            "active_tray": self.active_tray,
            "mode": self.mode,
            "mode_id": self.mode_id,
            "state": self.state,
            "trays": trays,
        }
