"""Main daemon entry point.

Wires together Nextion, Moonraker, PageManager, AMS, LED, Temperature,
PrintTime, and PLR into a single asyncio event loop. Runs as a systemd service.

Usage:
    python -m arco_screen                    # default config
    python -m arco_screen --port /dev/ttyS1  # override serial port
    python -m arco_screen --debug            # verbose logging
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
from pathlib import Path

from .nextion import Nextion
from .moonraker import MoonrakerClient
from .pages import PageManager, PageContext  # now from pages/ package
from .plr import PLRManager
from .config import ScreenDaemonConfig
from .ams import AMSManager
from .led import LEDManager
from .temperature import TemperatureManager
from .print_time import PrintTimeEstimator

log = logging.getLogger("arco_screen")


class ArcoScreenDaemon:
    """The main daemon that ties everything together."""

    def __init__(self, config: ScreenDaemonConfig, map_file: Path | None = None, dry_run: bool = False) -> None:
        self.config = config
        self.nextion = Nextion(port=config.serial_port, baudrate=config.serial_baud)
        self.moonraker = MoonrakerClient(url=config.moonraker_url, dry_run=dry_run)
        self.ams = AMSManager()
        self.led = LEDManager(self.moonraker, self.nextion)
        self.temperature = TemperatureManager(
            self.moonraker, config.config_dir, config.machine.temp_unit,
        )
        self.print_time = PrintTimeEstimator(self.moonraker)
        self.plr = PLRManager(self.moonraker, plr_dir=config.config_dir)

        # Build shared context for page handlers
        ctx = PageContext(
            nextion=self.nextion,
            moonraker=self.moonraker,
            config=config,
            ams=self.ams,
            led=self.led,
            temperature=self.temperature,
            print_time=self.print_time,
        )
        self.pages = PageManager(ctx, map_file=map_file)

        self._shutdown_event = asyncio.Event()
        self._status_poll_task: asyncio.Task | None = None

        # Wire up event handlers
        self.nextion.on_touch(self.pages.handle_touch)
        self.nextion.on_page_change(self.pages.handle_page_report)
        self.moonraker.on_status_update(self._on_status_update)

        # Wire up GCode response handlers
        self.moonraker.on_gcode_response(self.ams.handle_gcode_response)
        self.moonraker.on_gcode_response(self.led.handle_gcode_response)
        self.moonraker.on_gcode_response(self.temperature.handle_gcode_response)

    async def _on_status_update(self, status: dict) -> None:
        """Dispatch status updates to pages, PLR, and print time."""
        await self.pages.handle_status_update(status)

        # Update print time estimator
        if "virtual_sdcard" in status or "print_stats" in status:
            s = self.moonraker.state
            self.print_time.update(s.progress, s.print_duration)

        # Track print state transitions for PLR and print time
        if "print_stats" in status and "state" in status["print_stats"]:
            new_state = status["print_stats"]["state"]
            if new_state == "printing":
                self.plr.start_tracking()
                # Kick off print time estimation
                filename = self.moonraker.state.filename
                if filename:
                    try:
                        await self.print_time.on_print_start(filename)
                    except Exception as e:
                        log.error("Print time init error: %s", e)
            elif new_state in ("complete", "cancelled", "error", "standby"):
                self.plr.stop_tracking()
                self.print_time.reset()
                if new_state in ("complete", "cancelled"):
                    self.plr.clear()

    async def start(self) -> None:
        """Start the daemon."""
        log.info("arco_screen v0.2.0 starting...")
        log.info("Serial: %s @ %d", self.config.serial_port, self.config.serial_baud)
        log.info("Moonraker: %s", self.config.moonraker_url)
        log.info("Machine: %s", self.config.machine.name)
        log.info("Temp unit: %s", "Fahrenheit" if self.config.machine.temp_unit else "Celsius")

        if self.moonraker._dry_run:
            log.info("DRY-RUN mode — using mock printer state")
            s = self.moonraker.state
            s.extruder_temp = 23.5
            s.extruder_target = 0.0
            s.bed_temp = 22.0
            s.bed_target = 0.0
            s.klipper_state = "ready"
            s.print_state = "standby"
            s.speed_factor = 1.0
            s.extrude_factor = 1.0
            s.fan_speed = 0.0

        # Connect to both endpoints concurrently
        await asyncio.gather(
            self.nextion.connect(),
            self.moonraker.connect(),
        )

        # Give Moonraker a moment to deliver initial state
        log.info("Waiting for connections...")
        await asyncio.sleep(1.0)

        # Check for power loss recovery
        plr_state = self.plr.check_pending()
        if plr_state:
            log.info("PLR: Pending reprint detected for '%s'", plr_state.print_file_name)
            await self.pages.navigate("if_reprint")
            self._pending_plr = plr_state
        else:
            await self.pages.startup()

        log.info("arco_screen running")

        # Run until shutdown
        await self._shutdown_event.wait()

    async def stop(self) -> None:
        """Clean shutdown."""
        log.info("arco_screen shutting down...")
        self.plr.stop_tracking()
        # Save config on exit
        try:
            self.config.save()
        except Exception as e:
            log.error("Failed to save config: %s", e)
        await self.nextion.close()
        await self.moonraker.close()
        self._shutdown_event.set()
        log.info("arco_screen stopped")

    def request_shutdown(self) -> None:
        """Request shutdown from a signal handler."""
        asyncio.ensure_future(self.stop())


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    logging.basicConfig(level=level, format=fmt, stream=sys.stdout)
    logging.getLogger("websockets").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phrozen Arco screen daemon")
    parser.add_argument(
        "--port", default="/dev/ttyS1",
        help="Serial port for TJC screen (default: /dev/ttyS1)",
    )
    parser.add_argument(
        "--baud", type=int, default=115200,
        help="Serial baud rate (default: 115200)",
    )
    parser.add_argument(
        "--moonraker-url", default="ws://localhost:7125/websocket",
        help="Moonraker WebSocket URL",
    )
    parser.add_argument(
        "--config-dir", default=None,
        help="Config directory path (default: auto-detect)",
    )
    parser.add_argument(
        "--screen-map", default=None,
        help="Path to screen_map.json (from sniffer tool)",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Log GCode commands instead of sending to Klipper",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    setup_logging(debug=args.debug)

    # Load config
    config_dir = Path(args.config_dir) if args.config_dir else None
    config = ScreenDaemonConfig.load(config_dir)
    config.serial_port = args.port
    config.serial_baud = args.baud
    config.moonraker_url = args.moonraker_url

    map_file = Path(args.screen_map) if args.screen_map else None
    daemon = ArcoScreenDaemon(config, map_file=map_file, dry_run=args.dry_run)

    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, daemon.request_shutdown)

    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()
    except Exception as e:
        log.exception("Fatal error: %s", e)
        await daemon.stop()
        sys.exit(1)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
