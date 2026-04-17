# arco_screen — Open-Source voronFDM Replacement

## Overview

`arco_screen` is a Python asyncio daemon that replaces the closed-source `voronFDM`
binary. It bridges the TJC/Nextion TFT touchscreen to Klipper via Moonraker's
WebSocket API.

## Architecture

```
TJC TFT Screen (/dev/ttyS1, Nextion protocol)
        ↕
┌──────────────────────────────┐
│       arco_screen            │
│  ┌────────────┐              │
│  │  nextion    │  serial R/W │
│  └─────┬──────┘              │
│        ↕                     │
│  ┌────────────┐              │
│  │  pages      │  page state │
│  │  handlers   │  machine    │
│  └─────┬──────┘              │
│        ↕                     │
│  ┌────────────┐              │
│  │  moonraker  │  WS client  │
│  └─────┬──────┘              │
│        ↕                     │
│  ┌────────────┐              │
│  │  plr        │  power loss │
│  └────────────┘  recovery    │
└──────────────────────────────┘
        ↕
Moonraker (WebSocket :7125)
        ↕
Klipper + phrozen_dev extras
        ↕
ChromaKit AMS hardware
```

## Modules

### nextion.py — Serial Protocol Layer
- Async serial I/O on /dev/ttyS1 (115200 baud, Nextion default)
- Sends: `page X`, `X.Y.val=Z`, `X.Y.txt="Z"`, `X.Y.pic=Z`
- Receives: touch events (0x65), page ID reports (0x66), string returns (0x70)
- All commands terminated with 0xFF 0xFF 0xFF
- Handles reconnection on serial errors

### moonraker.py — Moonraker WebSocket Client
- Connects to ws://localhost:7125/websocket
- Subscribes to printer objects (extruder, heater_bed, fans, print_stats, etc.)
- Sends GCode commands via printer.gcode.script
- Handles Moonraker API calls (file listing, print start, history, etc.)
- Auto-reconnects on disconnect

### pages.py — Screen Page Handlers
- One handler class per TFT page (home, printing, temperature, etc.)
- Each handler knows:
  - What Klipper state to display on that page
  - What touch events to handle and what GCode to send
  - What Nextion components to update and how
- State machine tracks current page, updates only active page

### plr.py — Power Loss Recovery
- Persists print state to JSON (filename, position, temps, coordinates)
- On startup, checks for interrupted print and offers resume
- Dual-file write (A/B) for corruption resistance

### config.py — Configuration
- Machine name, standby timeout, language, temp units
- Persisted to use_conf.json
- AMS slot mapping from plr_print_precfg.json

### daemon.py — Main Entry Point
- Starts asyncio event loop
- Initializes all modules
- Handles SIGTERM/SIGINT for clean shutdown
- Systemd service integration

## Nextion Page Map (from TFT firmware)

| Page | Purpose | Key Components |
|------|---------|---------------|
| home | Main idle screen | t0 (bed temp), t1 (nozzle temp), NAME (machine name), pwifi (wifi icon) |
| printing | Active print display | j0 (progress %), t1-t6 (temps/speeds), cname (filename), PRINT_IP |
| printplan | Pre-print confirmation | t0 (name), t1 (time est), t2 (filament), t3/t4 (temps) |
| printfinish | Print complete | fname, t1 (duration), t2 (filament used) |
| temperature | Temp control | he/he1 (bed actual/target), no/no1 (nozzle actual/target), nozz (slider) |
| extruder | Extruder control | ex (temp slider), bex (temp text) |
| filament | Filament/AMS | ams1-4 (slot status), fil_num (selected), ex/bex (temp) |
| manual | Manual movement | xy (XY pad pic), z (Z pad pic) |
| auto | Auto leveling | t0 (bed temp), t1 (nozzle temp), temp_data |
| tool | Tool menu | — |
| print | File browser | j0 (progress), t0 (file sizes), usb (USB icon) |
| system | System settings | sys_data (AMS mode), temname, time |
| setsp | Speed override | sp (slider val), spdata (% text) |
| settem | Temp presets | t0 (temp value) |
| settime | Standby timeout | min (text), min_num (val), setime (val) |
| setwifi | WiFi settings | ip (IP text), wifi icons |
| standby | Standby/screensaver | sname (machine name), PRINT_IP, b1 (LED icon) |
| update | Firmware update | j0 (progress), L_update (status) |
| printerinfo | About/info | vv_1-5 (version strings), ams_sum, t0 (name) |
| history | Print history | — |
| popup1 | Alert popup | pop_num (alert type ID) |
| popup2 | Confirmation popup | pop2_num (type), ch (channel), pop_txt/update_txt |
| check | AMS check | p0-p2 (slot status pics) |
| getready | Print prep | get_num (step number 1-7) |

## GCode Command Map (screen action → Klipper command)

See the extracted command table in the main repo docs. All commands flow through
Moonraker's printer.gcode.script endpoint.

## Dropped Functionality (vs stock voronFDM)

| Feature | Why Dropped |
|---------|-------------|
| UDS socket to phrozen_master | Cloud/Zigbee gateway removed |
| VirtualApp phone control | Used phrozen_master cloud relay |
| TFT OTA via UDS | Can flash TFT directly via SD |
| frpc remote tunnel | Security risk, use Tailscale/WireGuard instead |

## Dependencies

- Python 3.9+ (available on Armbian)
- pyserial-asyncio (Nextion UART)
- websockets (Moonraker client)
- No C extensions, pure Python
