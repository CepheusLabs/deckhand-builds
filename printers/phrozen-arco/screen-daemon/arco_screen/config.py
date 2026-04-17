"""Configuration management.

Handles persistent settings (machine name, standby timeout, language, etc.)
and AMS slot mapping. Replaces use_conf.txt and plr_print_precfg.json.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path

log = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = Path("/home/mks/printer_data/config/arco_screen")


@dataclass
class MachineConfig:
    """Machine configuration, persisted to JSON."""

    number: int = 1
    name: str = "Arco"
    standby_timeout_min: int = 10
    language: int = 0  # 0=English, 1=Chinese, ...
    temp_unit: int = 0  # 0=Celsius, 1=Fahrenheit
    z_position: float = 2.0
    cutting_blade_position: int = 0

    @classmethod
    def load(cls, path: Path) -> "MachineConfig":
        try:
            data = json.loads(path.read_text())
            return cls(
                number=data.get("number", 1),
                name=data.get("name", "Arco"),
                standby_timeout_min=data.get("SetWaitTime", 10),
                language=data.get("Language", 0),
                temp_unit=data.get("Tempunit", 0),
                z_position=data.get("G_printer_position_z", 2.0),
                cutting_blade_position=data.get("G_Cutting_blade_position", 0),
            )
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            log.warning("Failed to load config from %s: %s, using defaults", path, e)
            return cls()

    def save(self, path: Path) -> None:
        data = {
            "number": self.number,
            "name": self.name,
            "SetWaitTime": self.standby_timeout_min,
            "Update_states": 0,
            "Language": self.language,
            "Tempunit": self.temp_unit,
            "G_printer_position_z": self.z_position,
            "G_Cutting_blade_position": self.cutting_blade_position,
        }
        path.write_text(json.dumps(data))
        log.debug("Config saved to %s", path)


@dataclass
class AMSConfig:
    """AMS (ChromaKit) slot mapping for multi-material prints."""

    auto_replace: bool = False
    chromakit_enabled: bool = False
    chromakit_count: int = 0
    # Slot access map: T0-T15 → AMS unit index (-1 = not assigned)
    slot_map: dict[str, int] = field(default_factory=lambda: {
        f"T{i}": -1 for i in range(16)
    })

    @classmethod
    def load(cls, path: Path) -> "AMSConfig":
        try:
            data = json.loads(path.read_text())
            slot_map = data.get("Chroma_Kit_access", {f"T{i}": -1 for i in range(16)})
            return cls(
                auto_replace=bool(data.get("Auto_Replace_state", 0)),
                chromakit_enabled=bool(data.get("Chroma_Kit_state", 0)),
                chromakit_count=data.get("Chroma_Kit_num", 0),
                slot_map=slot_map,
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.warning("Failed to load AMS config from %s: %s", path, e)
            return cls()

    def save(self, path: Path) -> None:
        data = {
            "Auto_Replace_state": int(self.auto_replace),
            "Chroma_Kit_state": int(self.chromakit_enabled),
            "Chroma_Kit_num": self.chromakit_count,
            "Chroma_Kit_access": self.slot_map,
        }
        path.write_text(json.dumps(data, indent="\t"))


@dataclass
class ScreenDaemonConfig:
    """Top-level config container for the screen daemon."""

    config_dir: Path = DEFAULT_CONFIG_DIR
    serial_port: str = "/dev/ttyS1"
    serial_baud: int = 115200
    moonraker_url: str = "ws://localhost:7125/websocket"

    machine: MachineConfig = field(default_factory=MachineConfig)
    ams: AMSConfig = field(default_factory=AMSConfig)

    @classmethod
    def load(cls, config_dir: Path | None = None) -> "ScreenDaemonConfig":
        """Load all config files from the config directory."""
        d = config_dir or DEFAULT_CONFIG_DIR
        cfg = cls(config_dir=d)
        cfg.machine = MachineConfig.load(d / "use_conf.txt")
        cfg.ams = AMSConfig.load(d / "plr_print_precfg.json")
        return cfg

    def save(self) -> None:
        """Persist all config files."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.machine.save(self.config_dir / "use_conf.txt")
        self.ams.save(self.config_dir / "plr_print_precfg.json")
