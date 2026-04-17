"""LED state management.

Controls the printer's LED strip and tracks its state. voronFDM uses
LED_GetState/LED_SetState and persists the state for standby mode.

The LED is controlled via GCode: the phrozen_dev Klipper module exposes
a custom command (typically SET_LED_STATE or output_pin) that toggles
the LED strip.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .moonraker import MoonrakerClient
    from .nextion import Nextion

log = logging.getLogger(__name__)

# Nextion pic IDs for the LED toggle button
LED_ON_PIC = 52
LED_OFF_PIC = 53


class LEDManager:
    """Tracks and controls the printer LED strip.

    Usage:
        led = LEDManager(moonraker, nextion)
        await led.toggle()
        await led.set_state(True)
        await led.update_screen_icon("home")
    """

    def __init__(self, moonraker: "MoonrakerClient", nextion: "Nextion") -> None:
        self._mr = moonraker
        self._nx = nextion
        self._on: bool = True  # LED defaults to on
        self._standby_state: bool = True  # State to restore after standby

    @property
    def is_on(self) -> bool:
        return self._on

    async def set_state(self, on: bool) -> None:
        """Set the LED on or off and send the GCode command."""
        self._on = on
        # Phrozen uses output_pin or a custom macro for LED control
        value = 1.0 if on else 0.0
        try:
            await self._mr.send_gcode(
                f"SET_PIN PIN=led_pin VALUE={value}"
            )
            log.info("LED: %s", "ON" if on else "OFF")
        except Exception as e:
            log.error("LED: Failed to set state: %s", e)

    async def toggle(self) -> None:
        """Toggle LED state."""
        await self.set_state(not self._on)

    async def update_screen_icon(self, page_name: str) -> None:
        """Update the LED toggle icon on the specified page.

        voronFDM shows the LED status as a toggle button (pic 52=on, 53=off)
        on the home and printing pages.
        """
        pic = LED_ON_PIC if self._on else LED_OFF_PIC
        # The LED toggle button component name varies by page
        component = f"{page_name}.pled"
        try:
            await self._nx.set_pic(component, pic)
        except Exception:
            pass  # Component may not exist on this page

    def save_standby_state(self) -> None:
        """Save current state before entering standby."""
        self._standby_state = self._on

    async def restore_from_standby(self) -> None:
        """Restore LED state when waking from standby."""
        if self._standby_state != self._on:
            await self.set_state(self._standby_state)

    async def handle_gcode_response(self, response: str) -> None:
        """Parse GCode responses for LED state changes.

        If another source (e.g., macro, manual command) changes the LED,
        we update our tracking state.
        """
        line = response.strip()
        if line.startswith("// "):
            line = line[3:]

        # Look for LED state reports from phrozen_dev
        if "LED_STATE:" in line:
            try:
                state = int(line.split("LED_STATE:")[-1].strip())
                self._on = state == 1
                log.info("LED: External state change -> %s", "ON" if self._on else "OFF")
            except (ValueError, IndexError):
                pass
