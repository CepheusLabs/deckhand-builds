"""Touch event sniffer / component ID mapper.

Run this standalone on the printer to build the page_id → page_name
and (page_id, component_id) → action mapping by tapping the screen
and recording what comes through.

Usage:
    python -m arco_screen.sniffer                      # interactive mode
    python -m arco_screen.sniffer --dump map.json      # dump current map
    python -m arco_screen.sniffer --load map.json      # preload map, continue

Workflow:
    1. Run the sniffer
    2. It tells you to navigate to a page on the screen
    3. Type the page name (e.g. "home")
    4. Tap every button on that page
    5. For each touch, type what the button does (e.g. "navigate:temperature")
    6. Repeat for all pages
    7. The sniffer writes a JSON map file that pages.py consumes

The map file format:
{
    "page_ids": {
        "0": "home",
        "1": "printing",
        ...
    },
    "touch_map": {
        "home": {
            "3": {"action": "navigate", "target": "temperature"},
            "5": {"action": "gcode", "command": "G28"},
            ...
        }
    },
    "component_names": {
        "home": {
            "3": "temp_button",
            "5": "home_button",
            ...
        }
    }
}
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

from .nextion import Nextion, TouchData, TouchEvent

log = logging.getLogger(__name__)

DEFAULT_MAP_FILE = Path("screen_map.json")


class ScreenMap:
    """Accumulated mapping data from sniffing sessions."""

    def __init__(self) -> None:
        self.page_ids: dict[int, str] = {}
        self.touch_map: dict[str, dict[int, dict]] = {}
        self.component_names: dict[str, dict[int, str]] = {}

    def load(self, path: Path) -> None:
        try:
            data = json.loads(path.read_text())
            self.page_ids = {int(k): v for k, v in data.get("page_ids", {}).items()}
            self.touch_map = {
                page: {int(cid): action for cid, action in comps.items()}
                for page, comps in data.get("touch_map", {}).items()
            }
            self.component_names = {
                page: {int(cid): name for cid, name in comps.items()}
                for page, comps in data.get("component_names", {}).items()
            }
            log.info("Loaded map with %d pages from %s", len(self.page_ids), path)
        except FileNotFoundError:
            log.info("No existing map at %s, starting fresh", path)
        except (json.JSONDecodeError, KeyError) as e:
            log.warning("Failed to load map from %s: %s", path, e)

    def save(self, path: Path) -> None:
        data = {
            "page_ids": {str(k): v for k, v in sorted(self.page_ids.items())},
            "touch_map": {
                page: {str(cid): action for cid, action in sorted(comps.items())}
                for page, comps in sorted(self.touch_map.items())
            },
            "component_names": {
                page: {str(cid): name for cid, name in sorted(comps.items())}
                for page, comps in sorted(self.component_names.items())
            },
        }
        path.write_text(json.dumps(data, indent=2))
        total_touches = sum(len(v) for v in self.touch_map.values())
        log.info("Saved map: %d pages, %d touch mappings → %s", len(self.page_ids), total_touches, path)

    def record_page(self, page_id: int, page_name: str) -> None:
        self.page_ids[page_id] = page_name
        if page_name not in self.touch_map:
            self.touch_map[page_name] = {}
        if page_name not in self.component_names:
            self.component_names[page_name] = {}

    def record_touch(
        self, page_name: str, component_id: int, label: str, action: dict
    ) -> None:
        if page_name not in self.touch_map:
            self.touch_map[page_name] = {}
        if page_name not in self.component_names:
            self.component_names[page_name] = {}
        self.touch_map[page_name][component_id] = action
        self.component_names[page_name][component_id] = label

    def summary(self) -> str:
        lines = [f"Pages mapped: {len(self.page_ids)}"]
        for pid, pname in sorted(self.page_ids.items()):
            n_touch = len(self.touch_map.get(pname, {}))
            lines.append(f"  [{pid:2d}] {pname} ({n_touch} touches)")
        total = sum(len(v) for v in self.touch_map.values())
        lines.append(f"Total touch mappings: {total}")
        return "\n".join(lines)


async def input_async(prompt: str) -> str:
    """Non-blocking input using asyncio."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: input(prompt))


async def run_sniffer(
    port: str = "/dev/ttyS1",
    baud: int = 115200,
    map_file: Path = DEFAULT_MAP_FILE,
) -> None:
    """Interactive sniffing session."""

    screen_map = ScreenMap()
    screen_map.load(map_file)

    nextion = Nextion(port=port, baudrate=baud)
    current_page_name: str | None = None
    current_page_id: int | None = None
    pending_touches: asyncio.Queue[TouchData] = asyncio.Queue()

    async def on_touch(touch: TouchData) -> None:
        await pending_touches.put(touch)

    async def on_page(page_id: int) -> None:
        nonlocal current_page_id
        current_page_id = page_id
        known = screen_map.page_ids.get(page_id, "???")
        print(f"\n  📄 Page report: id={page_id} (known as: {known})")

    nextion.on_touch(on_touch)
    nextion.on_page_change(on_page)

    print("=" * 60)
    print("  arco_screen Touch Sniffer")
    print("=" * 60)
    print()
    print("This tool helps you build the touch event mapping.")
    print("It records which (page_id, component_id) pairs correspond")
    print("to which buttons on the screen.")
    print()
    print(f"Serial: {port} @ {baud}")
    print(f"Map file: {map_file}")
    print()

    if screen_map.page_ids:
        print("Existing map:")
        print(screen_map.summary())
        print()

    await nextion.connect()
    print("Connected to screen. Waiting for events...\n")

    print("Commands:")
    print("  page <name>    — Set the name for the current page")
    print("  save           — Save map to disk")
    print("  summary        — Show current map")
    print("  quit           — Save and exit")
    print("  (or just type a label when a touch event appears)")
    print()

    try:
        while True:
            # Check for touch events (non-blocking)
            try:
                touch = pending_touches.get_nowait()
                page_name = screen_map.page_ids.get(touch.page_id, f"page_{touch.page_id}")
                event_str = "PRESS" if touch.event == TouchEvent.PRESS else "RELEASE"

                # Check if we already have this mapped
                existing = screen_map.touch_map.get(page_name, {}).get(touch.component_id)
                existing_name = screen_map.component_names.get(page_name, {}).get(touch.component_id)

                if existing:
                    print(
                        f"  👆 {event_str}: page={touch.page_id}({page_name}) "
                        f"cid={touch.component_id} → {existing_name}: {existing}"
                    )
                else:
                    print(
                        f"  👆 {event_str}: page={touch.page_id}({page_name}) "
                        f"cid={touch.component_id} → UNMAPPED"
                    )
                    if touch.event == TouchEvent.PRESS:
                        label = await input_async(
                            f"    Label this button (or Enter to skip): "
                        )
                        if label.strip():
                            action_str = await input_async(
                                f"    Action? [navigate:<page> | gcode:<cmd> | setting:<key> | skip]: "
                            )
                            action = _parse_action(action_str.strip())
                            if action:
                                screen_map.record_touch(
                                    page_name, touch.component_id, label.strip(), action
                                )
                                print(f"    ✅ Recorded: {label.strip()} → {action}")
                continue
            except asyncio.QueueEmpty:
                pass

            # Check for user input
            try:
                cmd = await asyncio.wait_for(
                    input_async("arco> "), timeout=0.1
                )
            except asyncio.TimeoutError:
                await asyncio.sleep(0.05)
                continue

            cmd = cmd.strip()
            if not cmd:
                continue

            if cmd.startswith("page "):
                name = cmd[5:].strip()
                if current_page_id is not None:
                    screen_map.record_page(current_page_id, name)
                    print(f"  Mapped page_id={current_page_id} → '{name}'")
                else:
                    print("  No page ID received yet. Navigate on the screen first.")

            elif cmd == "save":
                screen_map.save(map_file)
                print(f"  Saved to {map_file}")

            elif cmd == "summary":
                print(screen_map.summary())

            elif cmd == "quit":
                screen_map.save(map_file)
                print("Saved and exiting.")
                break

            elif cmd == "help":
                print("Commands: page <name>, save, summary, quit, help")

            else:
                print(f"  Unknown command: {cmd}. Type 'help' for commands.")

    except KeyboardInterrupt:
        print("\nInterrupted.")
        screen_map.save(map_file)
        print(f"Saved to {map_file}")
    finally:
        await nextion.close()


def _parse_action(action_str: str) -> dict | None:
    """Parse an action string into a dict."""
    if not action_str or action_str == "skip":
        return None

    if ":" in action_str:
        kind, value = action_str.split(":", 1)
        kind = kind.strip().lower()
        value = value.strip()

        if kind == "navigate":
            return {"action": "navigate", "target": value}
        elif kind == "gcode":
            return {"action": "gcode", "command": value}
        elif kind == "setting":
            return {"action": "setting", "key": value}
        else:
            return {"action": kind, "value": value}

    # Bare string — treat as a gcode command
    return {"action": "gcode", "command": action_str}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Screen touch event sniffer")
    parser.add_argument("--port", default="/dev/ttyS1", help="Serial port")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("--map", default="screen_map.json", help="Map file path")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(run_sniffer(port=args.port, baud=args.baud, map_file=Path(args.map)))


if __name__ == "__main__":
    main()
