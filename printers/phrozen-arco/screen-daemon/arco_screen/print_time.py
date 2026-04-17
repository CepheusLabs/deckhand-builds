"""Print time estimation.

Estimates remaining print time from:
  1. Slicer-embedded time estimates in GCode comments
  2. File progress + elapsed time extrapolation
  3. Layer-based estimation when layer info is available

voronFDM parses gcode files at print start to extract the slicer's
estimated total time, then uses elapsed time and progress to refine
the remaining time estimate during printing.
"""

from __future__ import annotations

import logging
import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .moonraker import MoonrakerClient

log = logging.getLogger(__name__)

# Patterns for slicer time estimates in GCode comments
# PrusaSlicer: ; estimated printing time (normal mode) = 1h 23m 45s
# Cura: ;TIME:5025
# OrcaSlicer: ; estimated printing time = 1h 23m 45s
# SuperSlicer: ; estimated printing time (normal mode) = 1h 23m 45s
SLICER_TIME_PATTERNS = [
    # PrusaSlicer / OrcaSlicer / SuperSlicer
    re.compile(
        r";\s*estimated printing time.*?=\s*"
        r"(?:(\d+)d\s*)?(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s)?",
        re.IGNORECASE,
    ),
    # Cura ;TIME:seconds
    re.compile(r";\s*TIME:(\d+)", re.IGNORECASE),
    # Simplify3D ;   Build time: 1 hours 23 minutes
    re.compile(
        r";\s*Build time:.*?(?:(\d+)\s*hours?)?\s*(?:(\d+)\s*minutes?)?",
        re.IGNORECASE,
    ),
]


def parse_slicer_time(line: str) -> int | None:
    """Try to parse a slicer time estimate from a GCode comment line.

    Returns estimated total print time in seconds, or None.
    """
    # PrusaSlicer/OrcaSlicer style
    m = SLICER_TIME_PATTERNS[0].search(line)
    if m:
        days = int(m.group(1) or 0)
        hours = int(m.group(2) or 0)
        mins = int(m.group(3) or 0)
        secs = int(m.group(4) or 0)
        total = days * 86400 + hours * 3600 + mins * 60 + secs
        if total > 0:
            return total

    # Cura style
    m = SLICER_TIME_PATTERNS[1].search(line)
    if m:
        return int(m.group(1))

    # Simplify3D style
    m = SLICER_TIME_PATTERNS[2].search(line)
    if m and (m.group(1) or m.group(2)):
        hours = int(m.group(1) or 0)
        mins = int(m.group(2) or 0)
        return hours * 3600 + mins * 60

    return None


class PrintTimeEstimator:
    """Estimates and tracks print time.

    Usage:
        estimator = PrintTimeEstimator(moonraker)
        await estimator.on_print_start("test.gcode")
        estimator.update(progress=0.45, elapsed=1200.0)
        remaining = estimator.remaining_seconds
        formatted = estimator.remaining_formatted
    """

    def __init__(self, moonraker: "MoonrakerClient") -> None:
        self._mr = moonraker
        self._slicer_total: int | None = None  # From gcode file
        self._print_start_time: float = 0.0
        self._progress: float = 0.0  # 0.0 - 1.0
        self._elapsed: float = 0.0  # seconds
        self._filename: str = ""

    @property
    def estimated_total(self) -> int:
        """Best estimate of total print time in seconds."""
        if self._slicer_total:
            return self._slicer_total
        # Extrapolate from elapsed + progress
        if self._progress > 0.01:
            return int(self._elapsed / self._progress)
        return 0

    @property
    def remaining_seconds(self) -> int:
        """Estimated seconds remaining."""
        if self._slicer_total and self._progress > 0.01:
            # Weighted blend: slicer estimate adjusted by actual pace
            slicer_remaining = max(0, self._slicer_total - self._elapsed)
            pace_remaining = max(0, (self._elapsed / self._progress) - self._elapsed)
            # Weight towards pace as print progresses
            w = min(self._progress * 2, 1.0)  # 0→0, 0.5→1.0
            return int(slicer_remaining * (1 - w) + pace_remaining * w)
        elif self._progress > 0.01:
            return max(0, int((self._elapsed / self._progress) - self._elapsed))
        elif self._slicer_total:
            return max(0, self._slicer_total - int(self._elapsed))
        return 0

    @property
    def remaining_formatted(self) -> str:
        """Human-readable remaining time: '1H 23M' or '< 1M'."""
        secs = self.remaining_seconds
        if secs < 60:
            return "< 1M"
        hours = secs // 3600
        mins = (secs % 3600) // 60
        if hours > 0:
            return f"{hours}H {mins:02d}M"
        return f"{mins}M"

    @property
    def elapsed_formatted(self) -> str:
        """Human-readable elapsed time."""
        secs = int(self._elapsed)
        hours = secs // 3600
        mins = (secs % 3600) // 60
        if hours > 0:
            return f"{hours}H {mins:02d}M"
        return f"{mins}M"

    async def on_print_start(self, filename: str) -> None:
        """Called when a print starts. Fetches slicer time estimate from gcode metadata."""
        self._filename = filename
        self._print_start_time = time.monotonic()
        self._progress = 0.0
        self._elapsed = 0.0
        self._slicer_total = None

        # Try to get estimated time from Moonraker's file metadata
        try:
            result = await self._mr._request(
                None,
                "server.files.metadata",
                {"filename": filename},
            )
            if isinstance(result, dict):
                est = result.get("estimated_time")
                if est and est > 0:
                    self._slicer_total = int(est)
                    log.info(
                        "Print time: Slicer estimate for '%s': %s",
                        filename, self._format_seconds(self._slicer_total),
                    )
                    return
        except Exception as e:
            log.debug("Print time: Could not get metadata for '%s': %s", filename, e)

        log.info("Print time: No slicer estimate available, will extrapolate from progress")

    def update(self, progress: float, elapsed: float) -> None:
        """Update with current print progress and elapsed time.

        Args:
            progress: 0.0 to 1.0 file progress
            elapsed: seconds since print started (from print_stats.print_duration)
        """
        self._progress = max(0.0, min(1.0, progress))
        self._elapsed = elapsed

    def reset(self) -> None:
        """Reset estimator state (print finished or cancelled)."""
        self._slicer_total = None
        self._progress = 0.0
        self._elapsed = 0.0
        self._filename = ""

    @staticmethod
    def _format_seconds(secs: int) -> str:
        hours = secs // 3600
        mins = (secs % 3600) // 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
