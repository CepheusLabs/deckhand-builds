# Console Spam Analysis

## Problem

The Phrozen stock firmware floods the Fluidd/Mainsail console with debug messages
every ~2 seconds, even when idle and not printing.

## Root Cause

Two independent polling loops both use `gcode.respond_info()` for debug logging,
which writes directly to the UI console:

### Loop 1: voronFDM Serial Screen Daemon

The `voronFDM` binary (TJC touchscreen daemon) polls Klipper over Moonraker's
websocket API, sending `P114` and `P0` gcode commands to fetch AMS status for
the touchscreen display. This runs continuously to keep the screen updated.

Each P114 cycle generates ~15 console lines:
- Serial port reinitialization messages
- Send/receive debug logs
- Raw hex byte dumps
- Parsed JSON state response
- Success/failure indicators

Each P0 cycle generates ~5 console lines:
- Version string
- Mode query
- LED state

### Loop 2: Internal Filament Runout Timer

`Device_TimmerRunoutCheck` is registered unconditionally at Klipper startup
(`dev.py:175`) and fires every 2 seconds (`AMS_FILA_RUNOUT_TIMER = 2.0`).

When mode is `AMS_WORK_MODE_UNKNOW` (idle), it returns early but the timer
keeps firing.

### Scale of the Problem

- **4,054 `respond_info()` calls** across the phrozen_dev module
  - 3,296 in `cmds.py`
  - 751 in `dev.py`
  - 7 in `base.py`
- At 2-second intervals: ~30+ console messages per cycle
- Serial port 2 always fails with error message (only 1 AMS connected)

## Fix Strategy (for Kalico port)

### 1. Logging Tiers

Replace `G_PhrozenFluiddRespondInfo()` calls with tiered logging:

| Tier | Method | Goes to | Use for |
|------|--------|---------|---------|
| SILENT | `logging.debug()` | klippy.log only | Hex dumps, byte counts, serial init |
| INFO | `logging.info()` | klippy.log only | State transitions, connection events |
| RESPONSE | `gcode.respond_info()` | UI console | Parseable responses voronFDM needs (e.g. `+P114:1`, JSON state) |
| ERROR | `gcode.respond_info()` | UI console | Actual errors requiring user attention |

### 2. Config Option

Add `log_level` to `[phrozen_dev]` config section:

```ini
[phrozen_dev]
# ... existing options ...
log_level: 0  # 0=errors only, 1=info, 2=debug (console), 3=verbose
```

### 3. Idle Polling Reduction

When mode is `AMS_WORK_MODE_UNKNOW` and no print is active, increase the timer
interval from 2s to 10s or disable it entirely until a print starts.

### 4. Suppress Known Failures

Serial port 2 ("tty2") failure message should only appear once at startup if the
port doesn't exist, not on every polling cycle.

## Messages voronFDM Needs (DO NOT suppress)

The serial screen parses these responses from `respond_info`:
- `+P114:0`, `+P114:1`, `+P114:2` (status query result codes)
- `+Mode:N,name` (current AMS mode)
- `V-H16-I16-F25384` (version string)
- JSON state objects: `{"dev_id": ..., "mc_state": ..., ...}`
- `P114成功` / `P114失败` (success/failure for screen status indicator)

These MUST remain as `respond_info()` calls.
