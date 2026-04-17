"""Nextion/TJC serial protocol handler.

Handles async serial communication with the TJC touchscreen over /dev/ttyS1.
Nextion protocol: all commands terminated with 0xFF 0xFF 0xFF.

Outgoing commands:
    page <name>           - Navigate to page
    <page>.<comp>.val=N   - Set numeric value
    <page>.<comp>.txt="S" - Set text value
    <page>.<comp>.pic=N   - Set picture index

Incoming events:
    0x65 PAGE CID EVENT FF FF FF  - Touch event (press/release)
    0x66 PAGE FF FF FF            - Current page ID
    0x70 <string> FF FF FF        - String data return
    0x71 <4 bytes> FF FF FF       - Numeric data return
    0x00-0x23 FF FF FF            - Various error/status codes
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Awaitable

import serial_asyncio

log = logging.getLogger(__name__)

TERMINATOR = b"\xff\xff\xff"
NEXTION_RESET_STRING = b"DRAKJHSUYDGBNCJHGJKSHBDN"
DEFAULT_PORT = "/dev/ttyS1"
DEFAULT_BAUD = 115200
INIT_CONNECT_DELAY = 0.2  # seconds between connect attempts
INIT_CONNECT_RETRIES = 5  # number of connect attempts before giving up

# Nextion return codes
NEXTION_TOUCH_EVENT = 0x65
NEXTION_PAGE_ID = 0x66
NEXTION_STRING_DATA = 0x70
NEXTION_NUMERIC_DATA = 0x71
NEXTION_STARTUP = 0x00
NEXTION_INVALID_INSTRUCTION = 0x00
NEXTION_SUCCESS = 0x01


class TouchEvent(IntEnum):
    PRESS = 0x01
    RELEASE = 0x00


@dataclass
class TouchData:
    """Decoded touch event from the screen."""

    page_id: int
    component_id: int
    event: TouchEvent


# Type alias for touch event callbacks
TouchCallback = Callable[[TouchData], Awaitable[None]]


class NextionProtocol(asyncio.Protocol):
    """Low-level protocol handler for serial data framing.

    Buffers incoming bytes and splits on the 0xFF 0xFF 0xFF terminator,
    dispatching complete frames to the parent Nextion instance.

    During initialization, raw_mode=True buffers all incoming data without
    frame parsing so the handshake can inspect raw bytes. After init
    completes, raw_mode is set to False and normal frame dispatch resumes.
    """

    def __init__(self, nextion: "Nextion") -> None:
        self._nextion = nextion
        self._buf = bytearray()
        self._transport: asyncio.Transport | None = None
        self.raw_mode = True  # Start in raw mode for init handshake
        self._raw_event: asyncio.Event = asyncio.Event()

    def connection_made(self, transport: asyncio.Transport) -> None:
        self._transport = transport
        log.info("Serial connection established")

    def connection_lost(self, exc: Exception | None) -> None:
        log.warning("Serial connection lost: %s", exc)
        self._nextion._on_disconnect()

    def data_received(self, data: bytes) -> None:
        self._buf.extend(data)
        if self.raw_mode:
            # Signal that new data arrived for the init handshake to check
            self._raw_event.set()
            return
        # Normal frame dispatch mode
        while True:
            idx = self._buf.find(TERMINATOR)
            if idx == -1:
                break
            frame = bytes(self._buf[:idx])
            self._buf = self._buf[idx + 3 :]
            if frame:
                self._nextion._on_frame(frame)

    def read_raw(self) -> bytes:
        """Return and clear the raw buffer (used during init handshake)."""
        data = bytes(self._buf)
        self._buf.clear()
        return data

    def peek_raw(self) -> bytes:
        """Peek at the raw buffer without clearing."""
        return bytes(self._buf)

    async def wait_for_data(self, timeout: float = 5.0) -> bool:
        """Wait for new data to arrive. Returns False on timeout."""
        self._raw_event.clear()
        try:
            await asyncio.wait_for(self._raw_event.wait(), timeout)
            return True
        except asyncio.TimeoutError:
            return False

    def write(self, data: bytes) -> None:
        if self._transport and not self._transport.is_closing():
            self._transport.write(data)


class Nextion:
    """High-level async interface to a TJC/Nextion display.

    Usage:
        nextion = Nextion("/dev/ttyS1")
        nextion.on_touch(my_handler)
        await nextion.connect()

        await nextion.set_page("home")
        await nextion.set_value("home.t0", "txt", '"25"')
        await nextion.set_value("printing.j0", "val", 42)
    """

    def __init__(
        self,
        port: str = DEFAULT_PORT,
        baudrate: int = DEFAULT_BAUD,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._protocol: NextionProtocol | None = None
        self._touch_handlers: list[TouchCallback] = []
        self._page_handlers: list[Callable[[int], Awaitable[None]]] = []
        self._string_handlers: list[Callable[[str], Awaitable[None]]] = []
        self._numeric_handlers: list[Callable[[int], Awaitable[None]]] = []
        self._connected = asyncio.Event()
        self.last_string_data: str | None = None
        self.last_numeric_data: int | None = None
        self._reconnect_task: asyncio.Task | None = None
        self._current_page: str | None = None
        self._component_cache: dict[str, Any] = {}  # dedup redundant writes
        self._loop: asyncio.AbstractEventLoop | None = None

    def on_touch(self, handler: TouchCallback) -> None:
        """Register a callback for touch events."""
        self._touch_handlers.append(handler)

    def on_page_change(self, handler: Callable[[int], Awaitable[None]]) -> None:
        """Register a callback for page change reports (0x66)."""
        self._page_handlers.append(handler)

    async def connect(self) -> None:
        """Open the serial port, perform the TJC/Nextion init handshake, and start reading."""
        self._loop = asyncio.get_running_loop()
        await self._do_connect()

    @staticmethod
    def _wake_uart(port: str) -> None:
        """Ensure the UART's runtime PM is active and clocks are enabled.

        On the RK3328 (MKS-PI), UART1's runtime PM can leave the peripheral
        suspended with clocks gated.  The kernel's 8250 driver doesn't always
        wake it on open, so we force it by toggling the driver unbind/bind
        and setting the power control to 'on'.  This is idempotent — if the
        UART is already awake the unbind/bind is harmless.

        Requires the systemd service to run ExecStartPre with root privileges
        or a sudoers rule for the unbind/bind paths.  If those aren't available
        the function will try direct sysfs writes (works if the service has
        CAP_SYS_ADMIN or the files are group-writable).
        """
        # Map /dev/ttySN to the platform device name
        port_num = port.rstrip("/").split("ttyS")[-1] if "ttyS" in port else None
        if port_num is None:
            return  # not a platform UART, skip

        uart_map = {"0": "ff110000.serial", "1": "ff120000.serial", "2": "ff130000.serial"}
        dev_name = uart_map.get(port_num)
        if dev_name is None:
            return

        sysfs_power = Path(f"/sys/devices/platform/{dev_name}/power")
        driver_path = Path("/sys/bus/platform/drivers/dw-apb-uart")

        # Check if already active
        try:
            runtime_status = (sysfs_power / "runtime_status").read_text().strip()
        except OSError:
            runtime_status = "unknown"

        if runtime_status == "active":
            log.debug("UART %s already active", dev_name)
            return

        log.warning("UART %s is %s — forcing driver rebind to wake clocks", dev_name, runtime_status)
        try:
            def _write_sysfs(path: Path, value: str) -> bool:
                """Write to a sysfs file, trying direct write first, then sudo."""
                try:
                    path.write_text(value)
                    return True
                except PermissionError:
                    r = subprocess.run(
                        ["sudo", "-n", "bash", "-c", f"echo {value} > {path}"],
                        capture_output=True, timeout=5,
                    )
                    return r.returncode == 0

            # Unbind the driver (releases the ttyS device)
            unbind = driver_path / "unbind"
            if unbind.exists():
                _write_sysfs(unbind, dev_name)
                import time; time.sleep(0.5)

            # Rebind (re-creates ttyS device with clocks enabled)
            bind = driver_path / "bind"
            if bind.exists():
                _write_sysfs(bind, dev_name)
                import time; time.sleep(0.5)

            # Pin power control to 'on' to prevent re-suspension
            power_control = sysfs_power / "control"
            if power_control.exists():
                _write_sysfs(power_control, "on")

            log.info("UART %s rebind complete", dev_name)
        except Exception as e:
            log.error("Failed to wake UART %s: %s", dev_name, e)

    async def _do_connect(self) -> None:
        """Establish serial connection and perform init handshake."""
        try:
            # Ensure the UART hardware is awake (RK3328 runtime PM workaround)
            await asyncio.get_running_loop().run_in_executor(
                None, self._wake_uart, self._port
            )

            _, protocol = await serial_asyncio.create_serial_connection(
                asyncio.get_running_loop(),
                lambda: NextionProtocol(self),
                self._port,
                baudrate=self._baudrate,
            )
            self._protocol = protocol
            log.info("Serial opened on %s @ %d, starting init handshake...", self._port, self._baudrate)

            # Perform the TJC/Nextion initialization handshake.
            #
            # NOTE: voronFDM's main_ScreenUpdate sends the DRAKJH reset string,
            # but that is a TFT *firmware upload* init — NOT normal startup.
            # For normal operation we just need to flush + connect.
            #
            # Sequence:
            #   1. Send 0xFF 0xFF 0xFF (flush any pending state)
            #   2. Send "connect" + terminator (retry a few times)
            #   3. Look for "comok " in response
            #   4. Send initial page command

            # Step 1: Flush — send a few terminators to clear any partial command
            for _ in range(3):
                self._protocol.write(TERMINATOR)
            await asyncio.sleep(0.5)

            # Drain any boot/wakeup noise
            self._protocol.read_raw()

            # Step 2: Send "connect" and look for "comok "
            connected = False
            for attempt in range(1, INIT_CONNECT_RETRIES + 1):
                log.info("Sending 'connect' (attempt %d/%d)...", attempt, INIT_CONNECT_RETRIES)
                self._protocol.write(b"connect" + TERMINATOR)

                # Wait for response
                got_data = await self._protocol.wait_for_data(timeout=2.0)
                if got_data:
                    raw = self._protocol.peek_raw()
                    raw_str = raw.decode("utf-8", errors="replace")
                    log.debug("Init response: %r", raw_str)
                    if "comok " in raw_str:
                        log.info("Got 'comok' response — screen is alive!")
                        self._protocol.read_raw()  # Clear the buffer
                        connected = True
                        break
                    # Not the response we wanted, clear and retry
                    self._protocol.read_raw()

                await asyncio.sleep(INIT_CONNECT_DELAY)

            if not connected:
                log.warning(
                    "Did not receive 'comok' after %d attempts — "
                    "proceeding anyway (screen may be in a non-standard state)",
                    INIT_CONNECT_RETRIES,
                )

            # Step 3: Configure screen and navigate to home page
            log.info("Sending initial commands...")
            self._protocol.write(b"bkcmd=0" + TERMINATOR)  # Suppress success returns
            await asyncio.sleep(0.1)
            self._protocol.write(b"page home" + TERMINATOR)
            await asyncio.sleep(0.5)

            # Drain any remaining init responses
            self._protocol.read_raw()

            # Switch from raw mode to frame dispatch mode
            self._protocol.raw_mode = False
            log.info("Init handshake complete, switching to normal frame dispatch")

            self._connected.set()

        except Exception as e:
            log.error("Failed to connect to %s: %s", self._port, e)
            self._schedule_reconnect()

    def _on_disconnect(self) -> None:
        """Handle serial disconnection."""
        self._connected.clear()
        self._protocol = None
        self._schedule_reconnect()

    def _schedule_reconnect(self) -> None:
        """Schedule a reconnection attempt."""
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.ensure_future(self._reconnect_loop())

    async def _reconnect_loop(self) -> None:
        """Retry connection with backoff."""
        delay = 1.0
        while not self._connected.is_set():
            log.info("Reconnecting to %s in %.1fs...", self._port, delay)
            await asyncio.sleep(delay)
            await self._do_connect()
            delay = min(delay * 2, 30.0)

    def _on_frame(self, frame: bytes) -> None:
        """Dispatch a complete frame from the screen."""
        if not frame:
            return

        log.debug("RAW frame [%d bytes]: %s", len(frame), frame.hex())
        code = frame[0]

        if code == NEXTION_TOUCH_EVENT and len(frame) >= 4:
            raw_event = frame[3]
            try:
                event = TouchEvent(raw_event)
            except ValueError:
                # TFT sometimes sends event values outside 0/1 — treat as PRESS
                log.debug("Unknown touch event value %d, treating as PRESS", raw_event)
                event = TouchEvent.PRESS
            # Check if there are ASCII digits before the 0x65 marker — that's
            # numpad input embedded in the data stream by the TFT.
            touch = TouchData(
                page_id=frame[1],
                component_id=frame[2],
                event=event,
            )
            log.debug("Touch: page=%d cid=%d event=%s", touch.page_id, touch.component_id, touch.event.name)
            for handler in self._touch_handlers:
                asyncio.ensure_future(handler(touch))

        elif code == NEXTION_PAGE_ID and len(frame) >= 2:
            page_id = frame[1]
            log.debug("Page report: %d", page_id)
            for handler in self._page_handlers:
                asyncio.ensure_future(handler(page_id))

        elif code == NEXTION_STRING_DATA:
            text = frame[1:].decode("utf-8", errors="replace")
            log.debug("String data: %s", text)
            self.last_string_data = text
            for handler in self._string_handlers:
                asyncio.ensure_future(handler(text))

        elif code == NEXTION_NUMERIC_DATA and len(frame) >= 5:
            value = int.from_bytes(frame[1:5], "little", signed=True)
            log.debug("Numeric data: %d", value)
            self.last_numeric_data = value
            for handler in self._numeric_handlers:
                asyncio.ensure_future(handler(value))

        elif code == NEXTION_SUCCESS:
            pass  # Command acknowledgment, ignore

        else:
            # Check for numpad pattern: ASCII digits + embedded touch event (0x65)
            # e.g., b"250\x65\x20\xAA\x02" = numpad value "250" + touch page=32 cid=170
            idx65 = frame.find(b'\x65')
            if idx65 > 0 and len(frame) >= idx65 + 4:
                prefix = frame[:idx65]
                if all(0x30 <= b <= 0x39 for b in prefix):  # all ASCII digits
                    numpad_val = prefix.decode("ascii")
                    log.debug("Numpad value: %s", numpad_val)
                    self.last_string_data = numpad_val
                    for handler in self._string_handlers:
                        asyncio.ensure_future(handler(numpad_val))
                    # Process the embedded touch event
                    embedded = frame[idx65:]
                    self._on_frame(embedded)
                    return
            log.debug("Unknown frame: %s", frame.hex())

    # --- Outgoing commands ---

    async def _send(self, cmd: str) -> None:
        """Send a command string to the display."""
        if not self._connected.is_set():
            log.warning("Not connected, dropping command: %s", cmd)
            return
        raw = cmd.encode("utf-8") + TERMINATOR
        log.debug("TX: %s", cmd)
        self._protocol.write(raw)

    async def send_command(self, cmd: str) -> None:
        """Send a raw Nextion command string (public wrapper around _send)."""
        await self._send(cmd)

    async def set_page(self, page_name: str) -> None:
        """Navigate to a named page."""
        self._current_page = page_name
        self._component_cache.clear()  # new page, new state
        await self._send(f"page {page_name}")

    async def set_val(self, component: str, value: int) -> None:
        """Set a numeric .val property. Skips write if unchanged."""
        cache_key = f"{component}.val"
        if self._component_cache.get(cache_key) == value:
            return
        self._component_cache[cache_key] = value
        await self._send(f"{component}.val={value}")

    async def set_txt(self, component: str, text: str) -> None:
        """Set a text .txt property. Skips write if unchanged."""
        cache_key = f"{component}.txt"
        if self._component_cache.get(cache_key) == text:
            return
        self._component_cache[cache_key] = text
        escaped = text.replace('"', '\\"')
        await self._send(f'{component}.txt="{escaped}"')

    async def set_pic(self, component: str, pic_id: int) -> None:
        """Set a picture .pic property. Skips write if unchanged."""
        cache_key = f"{component}.pic"
        if self._component_cache.get(cache_key) == pic_id:
            return
        self._component_cache[cache_key] = pic_id
        await self._send(f"{component}.pic={pic_id}")

    async def set_picc(self, component: str, pic_id: int) -> None:
        """Set a cropped picture .picc property. Skips write if unchanged."""
        cache_key = f"{component}.picc"
        if self._component_cache.get(cache_key) == pic_id:
            return
        self._component_cache[cache_key] = pic_id
        await self._send(f"{component}.picc={pic_id}")

    async def get_val(self, component: str) -> None:
        """Request a numeric value (response comes as 0x71 frame)."""
        await self._send(f"get {component}.val")

    async def get_txt(self, component: str) -> None:
        """Request a text value (response comes as 0x70 frame)."""
        await self._send(f"get {component}.txt")

    async def set_vis(self, component: str, visible: bool) -> None:
        """Set component visibility."""
        await self._send(f"vis {component},{1 if visible else 0}")

    async def send_raw(self, cmd: str) -> None:
        """Send an arbitrary Nextion command."""
        await self._send(cmd)

    @property
    def current_page(self) -> str | None:
        return self._current_page

    @property
    def connected(self) -> bool:
        return self._connected.is_set()

    async def close(self) -> None:
        """Close the serial connection."""
        if self._reconnect_task:
            self._reconnect_task.cancel()
        if self._protocol and self._protocol._transport:
            self._protocol._transport.close()
        self._connected.clear()
        log.info("Nextion connection closed")
