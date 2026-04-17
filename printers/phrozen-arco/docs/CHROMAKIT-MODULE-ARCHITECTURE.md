# ChromaKit Module Architecture

## Overview

The `phrozen_dev` Klipper extras module controls the ChromaKit (MMU) multi-material
system. Originally a single 15,000-line `cmds.py` and 3,600-line `dev.py`, it has
been split into focused mixin modules.

## Module Hierarchy

```
__init__.py          Entry point -> dev.load_config()
    |
    v
dev.py               PhrozenDev class (main Klipper extension)
    |-- dev_runout.py        Filament runout detection timer
    |-- dev_uart_handler.py  Serial response parsing & dispatch
    |-- dev_uart_recv.py     Raw serial port read (port 1 & 2)
    |
    v  (inherits via)
cwebsocketapis.py    Websocket API registration
    |
    v
cmds.py              Commands class (GCode command registration + state)
    |-- cmds_structs.py      Binary protocol structures (ctypes)
    |-- cmds_serial.py       Serial port management & helpers
    |-- cmds_filament.py     Filament load/unload/cut operations
    |-- cmds_pause.py        Pause/resume/cancel state machine
    |-- cmds_channel.py      Tool change (channel switching)
    |-- cmds_orca.py         OrcaSlicer T0-T15 command handlers
    |-- cmds_system.py       System commands (version, ADC, bed mesh, mode)
    |-- cmds_pcmds.py        P-commands (P0, P2, P4, P8-P12, P28-P30, P114)
    |
    v
base.py              Base class, constants, serial port definitions
```

## Data Flow

### Idle (no print)
```
voronFDM --[P114 gcode]--> Klipper --> cmds_pcmds.Cmds_CmdP114()
    |                                      |
    |                                      v
    |                              cmds_serial._serial_send("SD")
    |                                      |
    |                                      v
    |                              ChromaKit hardware (19200 baud)
    |                                      |
    |                                      v
    |                              dev_uart_recv.Device_TimmerUart1Recv()
    |                                      |
    |                                      v
    |                              dev_uart_handler.Device_TimmerUartRecvHandler()
    |                                      |
    |                                      v  (parses 16-byte binary response)
    |                              respond_info("+P114:1", JSON state)
    |                                      |
    v <----[console response]-------------+
voronFDM updates touchscreen
```

### Print with Tool Change
```
Slicer gcode: T1
    |
    v
cmds_orca.Cmds_CmdT1()
    |-- cmds_orca.Cmds_CmdOrcaPre()     # pre-change setup
    |-- cmds_channel.Cmds_P1CnAutoChangeChannel(1)
    |       |-- cmds_filament.Cmds_MoveToCutFilaAction()     # cut current filament
    |       |-- cmds_serial.Cmds_AMSSerial1Send("T1")        # tell ChromaKit: switch to slot 1
    |       |-- (wait for ChromaKit to complete)
    |       |-- cmds_filament.Cmds_P1EnForceForward(1)       # push new filament into extruder
    |       |-- (purge sequence via gcode macros)
    |       +-- resume print
    |
    v
Slicer gcode continues
```

## Module Details

### cmds_structs.py - Binary Protocol Structures
**What it does:** Defines the ctypes structures for parsing ChromaKit serial responses.

| Structure | Size | Purpose |
|-----------|------|---------|
| `AMSSimpleInfoSt` | 5 bytes | Quick status: device ID, mode, mc/ma state |
| `AMSDetailInfoSt` | 16 bytes | Full status: all of above + buffer sensors, entry/park sensors |

**ChromaKit Response Format (16 bytes):**
```
Byte 0:  info_flag (0x52 'R' = valid response)
Byte 1:  dev_id
Byte 2:  end_dev_id
Byte 3:  active_dev_id
Byte 4:  target_dev_id
Byte 5:  others
Byte 6:  [2bit mode] [1bit motor_running] [1bit cache_empty] [1bit cache_full] [1bit cache_exist] [2bit reserved]
Byte 7:  [4bit mc_state] [4bit ma_state]
Byte 8-11: entry_state (32bit bitmask)
Byte 12-15: park_state (32bit bitmask)
```

### cmds_serial.py - Serial Port Management
**What it does:** Manages the serial connections to ChromaKit units.

| Method | Purpose |
|--------|---------|
| `_serial_reinit(port)` | Reinitialize a serial port (flush, reopen) |
| `_serial_send(port, cmd)` | Send ASCII command to ChromaKit |
| `_serial_send_wait_rsp(port, cmd, len)` | Send and wait for response |
| `Cmds_AMSSerial1Send(cmd)` | Send to ChromaKit unit 1 |
| `Cmds_AMSSerial2Send(cmd)` | Send to ChromaKit unit 2 |
| `Cmds_USBConnectErrorCheck()` | Verify USB serial connections are alive |
| `Cmds_CutFilaIfNormalCheck()` | Verify cutter is operational |

**Serial Commands Sent to ChromaKit:**
| Command | Purpose |
|---------|---------|
| `SD` | Status detail query (returns 16-byte binary) |
| `SB` | Status brief query (returns 5-byte binary) |
| `MC` | Enter multi-color mode |
| `MA` | Enter multi-material (auto-refill) mode |
| `M0` | Reset to idle |
| `E0`-`E15` | Force feed filament from slot N |
| `G0`-`G15` | Retract filament to park position for slot N |
| `H0`-`H15` | Special refill for slot N |
| `I2` | Manual extrude |
| `J0`-`J15` | Manual purge from slot N |
| `T0`-`T15` | Switch to slot N |
| `B0`-`B15` | Full retract out for slot N |
| `D0`-`D15` | Retract to park standby for slot N |
| `SP` | Emergency stop |
| `RD` | Ready all slots (park position) |
| `AP` | All park (retract all to park) |
| `CL` | Clear all (full retract out all) |
| `FA` | Auto refill |
| `AT+SB=0` | Query ChromaKit firmware version |
| `AT+IDLE` | Set ChromaKit to idle |

**What we CAN'T do (limitations):**
- Can't change the serial protocol (hardware firmware)
- Can't add new commands (ChromaKit firmware is closed)
- Can't control individual motors directly
- Can't read raw sensor values (only processed state)

### cmds_filament.py - Filament Operations
**What it does:** Physical filament movement operations.

| Method | Serial Cmd | Purpose |
|--------|-----------|---------|
| `Cmds_P1EnForceForward(n)` | `En` | Force push filament from slot N into extruder |
| `Cmds_P1GnExtruderBack(n)` | `Gn` | Retract filament some distance |
| `Cmds_P1HnSpecialInfila(n)` | `Hn` | Special refill (buffer not full then refill) |
| `Cmds_P1InExtruderBack(val)` | `I2` | Manual extrude/retract |
| `Cmds_P1JnManualSpitFila(n)` | `Jn` | Manual purge from slot N |
| `Cmds_P1BnWholeRollbackAction(n)` | `Bn` | Complete filament retract from slot N |
| `Cmds_P1DnMoveToParkPositonAction(n)` | `Dn` | Retract to park position |
| `Cmds_MoveToCutFilaPrepare()` | (gcode) | Move toolhead to cutter position |
| `Cmds_MoveToCutFilaAction()` | (gcode) | Execute filament cut at toolhead |
| `Cmds_MoveToCutFilaAndHomingXY()` | (gcode) | Cut then home X/Y |

**What we CAN do:**
- Control which slot loads/unloads
- Trigger purge sequences
- Cut filament at the toolhead
- All physical filament movement

**What we CAN'T do:**
- Control motor speed (fixed in ChromaKit firmware)
- Adjust buffer tube tension
- Read individual motor current/stall status

### cmds_pause.py - Pause/Resume State Machine
**What it does:** Complex state machine for pausing/resuming prints with ChromaKit.

This is the most complex module. ChromaKit pauses are triggered by:
- User pressing pause (screen or Fluidd)
- STM32 reporting filament runout
- Filament change timeout
- Toolhead cutter failure
- Buffer sensor errors

Each pause type has different behavior:
| Pause Type | Method | Behavior |
|------------|--------|----------|
| Screen pause | `Cmds_PhrozenKlipperPauseScreen()` | Standard Klipper pause |
| Filament runout (M2/M3) | `Cmds_PhrozenKlipperPauseM2M3ToSTM32()` | Pause + notify ChromaKit |
| Auto-refill pause | `Cmds_PhrozenKlipperPauseMAToSTM32()` | Pause + trigger refill |
| Cutter failure | `Cmds_PhrozenKlipperPauseToolheadCutFailsure()` | Pause + error state |
| Change timeout | `Cmds_PhrozenKlipperPauseChangeChannelTimeout()` | Pause + timeout handling |

**What we CAN do:**
- Intercept and modify pause behavior
- Add custom pause recovery sequences
- Change timeout values

**What we CAN'T do:**
- The ChromaKit firmware makes its own pause decisions independently
- STM32 can trigger pauses that bypass Klipper

### cmds_channel.py - Tool Change Logic
**What it does:** Orchestrates full tool changes (switching between filament slots).

| Method | Purpose |
|--------|---------|
| `Cmds_P1TnManualChangeChannel(n)` | Manual tool change to slot N |
| `Cmds_P1CnAutoChangeChannel(n)` | Automatic tool change (includes cut, change, purge) |

Auto change sequence:
1. Record current position
2. Move to waiting area
3. Cut current filament
4. Send `Tn` to ChromaKit (switch slot)
5. Wait for ChromaKit completion
6. Force feed new filament (`En`)
7. Purge at purge area (PRZ_SPITTING macros)
8. Wipe nozzle (PRZ_WIPEMOUTH macro)
9. Return to print position

**What we CAN do:**
- Modify the purge amount/location
- Change waiting area coordinates
- Adjust timeout values
- Add custom pre/post change actions

### cmds_orca.py - OrcaSlicer Integration
**What it does:** Handles T0-T15 tool change commands from OrcaSlicer.

Each `Cmds_CmdTn()` calls `_Cmds_CmdTn(n, gcmd)` which:
1. Runs `Cmds_CmdOrcaPre()` (pre-change setup)
2. Calls `Cmds_P1CnAutoChangeChannel(n)` (the actual change)

The OrcaSlicer plugin sends `P0 M1` at print start to set multi-color mode,
then `T0`, `T1`, etc. for each tool change.

### cmds_system.py - System Commands
**What it does:** Version queries, ADC sensor, bed mesh, mode management.

| Method | GCode | Purpose |
|--------|-------|---------|
| `Cmds_PhrozenVersion()` | PRZ_VERSION | Report firmware version |
| `Cmds_PhrozenAdc()` | PRZ_ADC | Read filament sensor ADC value |
| `Cmds_PhrozenBM1()` | PRZ_BM1 | Bed mesh operation |
| `Cmds_PhrozenBM0()` | PRZ_BM0 | Bed mesh operation |
| `Cmds_PrzPrintStart()` | PRZ_PRINT_START | Print start handler |
| `Cmds_PrintMode(mode)` | (internal) | Write mode to JSON config |
| `Cmds_PrzATRestore()` | PRZ_RESTORE | Clear error state |
| `Cmds_PrzATIdle()` | PRZ_IDLE | Set to idle |

### cmds_pcmds.py - P-Commands
**What it does:** The P-numbered commands that control ChromaKit directly.

| Command | Method | Purpose |
|---------|--------|---------|
| P0 | `Cmds_CmdP0()` | Mode control, LED, config read |
| P1 | `Cmds_CmdP1()` | Filament operations dispatcher (routes to filament.py) |
| P2 | `Cmds_CmdP2()` | Bulk operations (park all, retract all, cut) |
| P4 | `Cmds_CmdP4()` | Emergency stop |
| P8 | `Cmds_CmdP8()` | Auto refill |
| P9 | `Cmds_CmdP9()` | Configure waiting area |
| P10 | `Cmds_CmdP10()` | Purge count control |
| P11 | `Cmds_CmdP11()` | Cutter test |
| P12 | `Cmds_CmdP12()` | Cutter loop test |
| P28 | `Cmds_CmdP28()` | Connect ChromaKit (open serial) |
| P29 | `Cmds_CmdP29()` | Disconnect ChromaKit (close serial) |
| P30 | `Cmds_CmdP30()` | Auto-assign device IDs |
| P114 | `Cmds_CmdP114()` | Full status query |

### dev_runout.py - Filament Runout Timer
**What it does:** Periodic timer (every 2s) that monitors filament state.

The `Device_TimmerRunoutCheck()` method:
- Checks ChromaKit work mode
- In UNKNOW mode: returns immediately (idle)
- In MC/MA mode: monitors filament sensor, triggers pause on runout
- Handles single-color and multi-color runout differently

### dev_uart_recv.py - Serial Port Receivers
**What it does:** Reads raw bytes from ChromaKit serial ports.

| Method | Port | Purpose |
|--------|------|---------|
| `Device_TimmerUart1Recv()` | /dev/ttyACM1 (unit 1) | Read serial data from ChromaKit unit 1 |
| `Device_TimmerUart2Recv()` | (unit 2 port) | Read serial data from ChromaKit unit 2 |

Registered as Klipper reactor timers. When data is available, reads
all bytes and passes to the handler.

### dev_uart_handler.py - Serial Response Parser
**What it does:** Parses ChromaKit serial responses and dispatches actions.

`Device_TimmerUartRecvHandler()` handles:
- **Binary response (0x52 header, 16 bytes):** Parse via AMSDetailInfoSt, update state, respond with JSON
- **ASCII response (firmware version):** Parse version string, update DriveCodeFile.dat
- **Status codes (+MCM1, +P2A1, etc.):** Parse and dispatch to appropriate handler

## Dead Code Files (*_dead.py)

Files suffixed with `_dead` contain code that was identified as unused, 
commented out, or related to removed features (OTA, other printer models).
Kept for reference during the migration but not loaded by the module.

## What We Can Change vs What We Can't

### We Control (software side):
- Tool change sequences and timing
- Purge amounts and locations
- Pause/resume behavior
- Timeout values
- Waiting area coordinates
- Which gcode commands are registered
- How status is reported to the UI
- Polling frequency and logging

### ChromaKit Firmware Controls (can't change without reflashing):
- Motor speeds and acceleration
- Serial protocol and command set
- Internal state machine transitions
- Sensor thresholds and debouncing
- Buffer tube management logic
- Error detection and reporting
- LED behavior on the ChromaKit board itself
