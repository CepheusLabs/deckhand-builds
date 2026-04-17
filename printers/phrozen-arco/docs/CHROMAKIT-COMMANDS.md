# ChromaKit (MMU) Command Reference

Mapping between the Phrozen OrcaSlicer plugin operations, the GCode commands
sent to Klipper, and the serial protocol commands sent to the ChromaKit hardware.

## Source

Derived from:
- Phrozen OrcaSlicer fork plugin (`phrozen3d/PhrozenOrca`)
- `phrozen_dev/cmds.py` registered commands
- Live serial protocol captures from the printer

## Print Control

| OrcaSlicer Action | GCode Command | Description |
|-------------------|---------------|-------------|
| Pause | `PRZ_PAUSE` | Pause with ChromaKit state save |
| Resume | `PRZ_RESUME` | Resume with ChromaKit state restore |
| Cancel | `PRZ_CANCEL` | Cancel with ChromaKit cleanup |

## ChromaKit Slot Operations (per-slot)

Slots are numbered 0-3 per unit (A1-A4), 4-7 for second unit (A5-A8).
Tool changes use `T0`-`T15` (up to 16 slots with 4 units theoretical).

| OrcaSlicer Action | GCode | P-Command | Serial Cmd | Description |
|-------------------|-------|-----------|------------|-------------|
| Tool change | `T0`-`T15` | (orchestrates P-commands) | Multiple | Full tool change sequence |
| Load | `P1 En` | P1 | `En` (n=slot) | Load filament from slot n |
| Unload | `P1 In` | P1 | `In` (n=slot) | Unload/retract filament from slot n |
| Park | `P1 Gn` | P1 | `Gn` (n=slot) | Park filament to standby position |
| Force feed | `P1 En` (forced) | P1 | `En` | Force feed filament into extruder |
| Retract | `P1 In` | P1 | `In` | Retract filament from extruder |
| Special refill | `P1 Hn` | P1 | `Hn` (n=slot) | Special refill stage |
| Manual spit | `P1 Jn` | P1 | `Jn` (n=slot) | Manual spit/purge operation |
| Auto change | `P8` | P8 | (sequence) | Auto-change to specified channel |

## ChromaKit Unit-Level Operations

| OrcaSlicer Action | GCode | Description |
|-------------------|-------|-------------|
| Connect | `P28` | Open serial port to ChromaKit (19200 baud) |
| Disconnect | `P29` | Close serial port |
| Status query | `P114` | Full binary status query (16-byte response) |
| Set mode | `P0 M=n` | Set operating mode (0=unknown, 1=MC, 2=MA, 3=runout) |
| LED control | `P0 LED_State=n` | Set LED state (0=off, 1=on) |
| LED query | `P0 LED_GetState` | Query current LED state |
| Emergency stop | `P29` + reset | Disconnect and reset state |
| Ready all | `P10` | Prime/spit all channels |
| Unload all | (sequence of P1 In) | Unload all slots |
| Park all | (sequence of P1 Gn) | Park all slots |
| Cut | `P4` | Filament cut at toolhead |
| Manual extrude | `P2` | Manual extrude with amount parameter |
| Clear error | `PRZ_RESTORE` | Clear error state, restore to idle |
| Debug/serial | `P30` | Serial debug command |
| ADC query | `PRZ_ADC` | Read filament sensor ADC value |
| Version | `PRZ_VERSION` | Report firmware version string |
| Bed mesh | `PRZ_BM0` / `PRZ_BM1` | Bed mesh operations |
| Print start | `PRZ_PRINT_START` | Print start handler (sets mode, reads config) |
| Idle | `PRZ_IDLE` | Set ChromaKit to idle state |

## ChromaKit Serial Protocol

Binary protocol over USB serial at **19200 baud**.

### Connection
- ChromaKit units appear as `/dev/ttyACM*` or `/dev/ttyUSB*`
- Serial port 1: First ChromaKit unit (4 slots, A1-A4)
- Serial port 2: Second ChromaKit unit (4 slots, A5-A8) - optional

### Send Commands (ASCII)
| Command | Description |
|---------|-------------|
| `SD` | Status/detail query |
| `E0`-`E3` | Load filament from slot 0-3 |
| `G0`-`G3` | Park filament to slot 0-3 |
| `H0`-`H3` | Special refill for slot 0-3 |
| `I2` | Extruder retract |
| `J0`-`J3` | Manual spit from slot 0-3 |
| `M0` | Reset to idle state |

### Receive Response (Binary, 16 bytes)
```
Offset  Field           Type    Description
0       header          u8      0x52 ('R') = valid response
1       dev_id          u8      Device ID (0xFF = broadcast)
2       active_dev_id   u8      Currently active slot
3       dev_mode        u8      Operating mode
4-5     (flags)         u16     cache_empty, cache_full, cache_exist
6       (reserved)      u8
7       (reserved)      u8
8       mc_state        u8      Multi-color state machine
9       (reserved)      u8
10      ma_state        u8      Multi-material state machine
11      (reserved)      u8
12      entry_state     u8      Entry sensor state
13      (reserved)      u8
14      park_state      u8      Park sensor state
15      (reserved)      u8
```

Parsed via `ctypes.LittleEndianStructure` in `cmds.py`:
- `AMSSimpleInfoSt` / `AMSSimpleInfoBytes` (simple status)
- `AMSDetailInfoSt` / `AMSDetailInfoBytes` (detailed status)

### State Machine Values
From OrcaSlicer telemetry:
- `mc_state` / `ma_state`: 10 = idle/standby
- `entry_state`: 15 = entry sensor clear
- `park_state`: 13 = parked

## Operating Modes

| Mode | Constant | Description |
|------|----------|-------------|
| 0 | `AMS_WORK_MODE_UNKNOW` | Unknown/uninitialized (idle default) |
| 1 | `AMS_WORK_MODE_MC` | Multi-color mode |
| 2 | `AMS_WORK_MODE_MA` | Multi-material mode |
| 3 | `AMS_WORK_MODE_FILA_RUNOUT` | Filament runout detection mode |

## OrcaSlicer Polling

The slicer plugin polls ChromaKit status:
- **Interval**: Every 10 seconds (NOT the 2s used by the firmware timer)
- **Queries**: ChromaKit status (P114) + LED state (P0 LED_GetState)
- **Console parsing**: Monitors `respond_info` output for:
  - Load/unload completion signals
  - Pause codes
  - Connection state changes
  - Filament presence
  - Calibration progress

## Error Codes (from OrcaSlicer plugin)

| Error | Severity | Description |
|-------|----------|-------------|
| Motor stall | HIGH | ChromaKit motor stalled during operation |
| Load timeout | HIGH | Filament failed to load within timeout |
| Entry timeout | HIGH | Filament failed to reach entry sensor |
| Buffer full | MEDIUM | Filament buffer cache is full |
| Cutter error | HIGH | Filament cutter mechanism failure |
| Filament break | HIGH | Filament broke during operation |
| Nozzle clog | HIGH | Nozzle clog detected via ADC sensor |
| Discharge fail | MEDIUM | Failed to discharge filament |
| Temp warning | LOW | ChromaKit temperature out of range |
| Disconnect | HIGH | ChromaKit lost connection |
| User pause | INFO | User-initiated pause |
| Firmware pause | INFO | Firmware-initiated pause |

## GCode Macros (in printer_gcode_macro.cfg)

These macros support ChromaKit operations from the printer config side:

| Macro | Purpose |
|-------|---------|
| `PRZ_SPITTING` | Purge/prime filament at purge area (110mm extrude, cool, wipe) |
| `PRZ_SPITTING_START` | Initial purge at print start (60mm extrude) |
| `PRZ_SPITTING_NORMAL` | Normal purge during tool change |
| `PRZ_SPITTING_END` | Final purge at print end |
| `PRZ_WIPEMOUTH` | Nozzle wipe sequence (4x back-and-forth at Y=322) |
| `PRZ_WAITINGAREA` | Move to waiting/parking area |
| `PRZ_CUT_WAITINGAREA` | Move to cut position waiting area |
| `PRZ_PAUSE_WAITINGAREA` | Move to pause waiting area |
| `GLOBAL_PARAM` | Global variables: temperatures, positions, speeds |

### Purge Area Coordinates (from GLOBAL_PARAM)
- Wipe start X: 140, Y: 322 (bottom of bed)
- Spitting start X: 127, Y: 322
- Waiting area X: 140
- Bottom print Y: 295, X: 169
