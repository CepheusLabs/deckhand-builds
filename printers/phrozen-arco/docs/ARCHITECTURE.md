# Phrozen Arco - Kalico Mainline Architecture

## Overview

This repo contains the configuration, custom Klipper extras, macros, and deployment
tooling needed to run a Phrozen Arco FDM printer on [Kalico](https://github.com/KalicoCrew/kalico)
(formerly Danger Klipper) instead of the stock Phrozen firmware stack.

## Hardware

| Component | Details |
|-----------|---------|
| SBC | Rockchip RK3328 (aarch64), Armbian 22.05 Buster |
| Main MCU | STM32F407VET6 via USB (`/dev/serial/by-id/usb-Klipper_stm32f407xx_550027...`) |
| Toolhead MCU | STM32F103CBT6 via UART (`/dev/ttyS0`, aliased `MKS_THR`) |
| Kinematics | CoreXY, 330x330x303mm |
| Steppers X/Y | TMC5160 (SPI, 1.6A, sensorless homing capable) |
| Steppers Z/Z1 | TMC2209 (UART, 0.9A, dual Z) |
| Extruder | TMC2209 (UART, 0.707A), gear ratio 1517:170 |
| Probe | Motorized deploy/retract via `probe_up`/`probe_off` macros, shared pin with Z endstop |
| Accelerometer | ADXL345 on toolhead MCU (SPI) |
| Display | TJC serial touchscreen on `/dev/ttyS1` (Nextion protocol) |
| AMS | Phrozen multi-material system, 1-2 units, 4 slots each, 19200 baud serial over USB |
| Fans | Hotend fan (always on), part cooling (generic), chamber fan, assist fan (output_pin) |
| Sensors | Extruder NTC, bed NTC, chamber NTC, filament ADC sensor on `MKS_THR:PA2` |

## Software Stack

```
┌─────────────────────────────────────────────┐
│                  Fluidd UI                   │
├─────────────────────────────────────────────┤
│               Moonraker API                  │
├─────────────────────────────────────────────┤
│  Kalico (Klipper)                            │
│  ├── klippy/extras/phrozen_dev/  (AMS)       │
│  ├── klippy/extras/CatchIP.py    (IP helper) │
│  └── danger_options (config overrides)       │
├─────────────────────────────────────────────┤
│  voronFDM  (serial screen daemon)            │
│  └── TJC touchscreen (/dev/ttyS1)           │
├─────────────────────────────────────────────┤
│  STM32F407 MCU  │  STM32F103 Toolhead MCU   │
└─────────────────┴───────────────────────────┘
```

## Phrozen Custom Code - What It Does

### phrozen_dev/ Klipper Extras Module

A self-contained Klipper extras module providing AMS (Automatic Material System)
multi-material support. Loaded via `[phrozen_dev]` config section.

| File | Size | Purpose |
|------|------|---------|
| `__init__.py` | 0.5KB | Entry point, calls `dev.load_config()` |
| `base.py` | 37KB | Base class, constants, serial port definitions, firmware version tracking |
| `cmds.py` | 800KB | AMS commands: T0-T15 tool changes, P-commands (serial protocol), filament handling |
| `dev.py` | 239KB | Main class: AMS connect/disconnect, filament runout daemon, serial port management |
| `cwebsocketapis.py` | 1.6KB | WebSocket API endpoint (`phrozen/soft_ver`) |

#### Key GCode Commands Registered

| Command | Purpose |
|---------|---------|
| `T0`-`T15` | Tool change (select AMS slot) |
| `P0` | AMS mode control, LED state, config read |
| `P1` | Filament forward/retract/spit operations |
| `P2` | AMS manual operations |
| `P4` | Filament cut |
| `P8` | Filament infeed |
| `P9` | AMS status query |
| `P10` | AMS spitting/priming |
| `P11`/`P12` | AMS auxiliary commands |
| `P28` | Connect AMS (open serial port) |
| `P29` | Disconnect AMS (close serial port) |
| `P30` | AMS serial debug |
| `P114` | AMS full status query (binary protocol) |
| `PRZ_PAUSE` | Phrozen pause (with AMS state save) |
| `PRZ_RESUME` | Phrozen resume (with AMS state restore) |
| `PRZ_CANCEL` | Phrozen cancel (with AMS cleanup) |
| `PRZ_VERSION` | Report firmware version |
| `PRZ_PRINT_START` | Print start handler |
| `PRZ_ADC` | Filament sensor ADC reading |
| `PRZ_TEST` | Debug test command |
| `PRZ_BM0`/`PRZ_BM1` | Bed mesh operations |
| `PRZ_RESTORE` | AMS state restore (power loss recovery) |
| `PRZ_IDLE` | AMS idle state |
| `K109` | Alias for M109 (used by serial screen) |

#### AMS Serial Protocol

Binary protocol over USB serial at 19200 baud. The AMS boards appear as `/dev/ttyACM*`
or `/dev/ttyUSB*`. Communication uses a simple command/response pattern:

- **Send**: ASCII command strings (`SD`, `E0`-`E3`, `G0`-`G3`, `H0`-`H3`, `I2`, `J0`-`J3`, `M0`)
- **Receive**: 16-byte binary response parsed via `ctypes.LittleEndianStructure`
- **Response header**: First byte `0x52` ('R') indicates valid response
- **State fields**: dev_id, active_dev_id, dev_mode, cache_empty/full/exist, mc_state, ma_state, entry_state, park_state

### Serial Screen (voronFDM)

Closed-source ARM binary that bridges the TJC serial touchscreen to Moonraker's
websocket API. Speaks Nextion protocol over `/dev/ttyS1` (`.val=`, `.txt=`, `.pic=`
commands to update display elements).

**Kept as-is** - the TJC screen firmware and voronFDM are a matched pair. Replacing
one without the other would break the display.

### Removed Components

| Component | What it was | Why removed |
|-----------|-------------|-------------|
| `phrozen_master` | HDL Zigbee gateway, connects to hdlcontrol.com cloud | Phone-home, not needed for printing |
| `frpc` | FRP tunnel to 42.193.239.84 (Phrozen server) | Remote access backdoor |
| `phrozen_slave_ota` | OTA firmware updater | Uncontrolled updates from Phrozen cloud |
| `ota_control` | OTA controller daemon | Same |
| `hdlDat/rsa_priv.txt` | Plaintext RSA private key | Security risk |
| `hdlDat/` (Zigbee files) | HDL gateway data | Not needed without phrozen_master |

## Why Kalico Over Mainline Klipper

| Feature | Mainline Klipper | Kalico |
|---------|-----------------|--------|
| `gcode_shell_command` | Not available | Built-in |
| `danger_options` | Not available | Config overrides for safety limits |
| `allow_plugin_override` | Not available | Lets phrozen_dev register commands cleanly |
| `dockable_probe` | Not available | Better probe deploy/retract support |
| `trad_rack` | Not available | Multi-material reference (future) |
| Development pace | Conservative | Active, weekly commits |
| Base version | N/A | Tracks mainline + extras |

## Upstream Tracking

### Kalico (primary upstream)
- Remote: `https://github.com/KalicoCrew/kalico`
- Track: `main` branch
- Update frequency: monthly rebase recommended

### Phrozen (AMS protocol updates)
- Remote: `https://github.com/phrozen3d/klipper`
- Track: `phrozen-stable` branch
- Last known commit: `cb087013` (2026-01-13)
- Update frequency: ~2 commits per year, manual review each
