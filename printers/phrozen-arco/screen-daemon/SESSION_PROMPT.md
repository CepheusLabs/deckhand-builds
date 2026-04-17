# arco_screen Session Continuation Prompt

Copy everything below the line into a new session.

---

## Project Overview

I'm building `arco_screen`, an open-source Python daemon to replace the closed-source `voronFDM` binary on my Phrozen Arco 3D printer. The printer runs a RK3328 SoC (MKS-PI board) with a TJC8048X250_011C touchscreen connected via UART1 (`/dev/ttyS1` at 115200 baud). The code lives in the `screen-daemon/` directory of the repo.

The repo is at: `/home/mks/phrozen-arco-kalico` on both machines, and mounted locally. The screen-daemon Python package is `arco_screen`.

## Infrastructure

**Two machines:**
- **192.168.0.40** — production printer (was .13, network changed). Has Klipper MCU connected. No `--dry-run`.
- **192.168.0.235** — test machine at my desk. MCU disconnected, runs with `--debug --dry-run`. Use this for all interactive testing.

**SSH access:** `mks@192.168.0.40` and `mks@192.168.0.235`, password `makerbase`. Use `SSH_ASKPASS` trick:
```bash
cat > /tmp/ssh_pass.sh << 'EOF'
#!/bin/bash
echo "makerbase"
EOF
chmod +x /tmp/ssh_pass.sh
export SSH_ASKPASS_REQUIRE=force SSH_ASKPASS=/tmp/ssh_pass.sh
```

**Service management:**
```bash
ssh mks@192.168.0.235 'echo makerbase | sudo -S systemctl restart arco-screen'
ssh mks@192.168.0.235 'echo makerbase | sudo -S journalctl -u arco-screen --no-pager -n 40'
```

**Deploying code:** Git push from local, then `git pull` on the machine. Or SCP individual files for quick iteration. **IMPORTANT:** After git pull, clear `.pyc` caches before restarting:
```bash
find /home/mks/phrozen-arco-kalico/screen-daemon -name "*.pyc" -delete
find /home/mks/phrozen-arco-kalico/screen-daemon -name "__pycache__" -type d -exec rm -rf {} +
```
We hit a bug where stale `.pyc` bytecode caused the old dispatch logic to keep running despite updated `.py` files.

**voronFDM:** Must be killed and chmod -x'd on any machine running our daemon, or it fights for /dev/ttyS1. Verify with `pgrep -a voronFDM` and `lsof /dev/ttyS1`.

## TJC/Nextion Serial Protocol — What We Learned

### Basics
- All commands terminated with `0xFF 0xFF 0xFF`
- Init sequence: flush (3x terminator) → `connect` → wait for `comok` → `bkcmd=0` → `page home`
- Do NOT send the DRAKJH reset string — that's TFT firmware upload, not normal startup
- `bkcmd=0` suppresses success return codes (reduces noise)

### UART1 Runtime PM (RK3328)
The `dw-apb-uart` driver can leave UART1 suspended with clocks gated. Fixed via:
1. `wake-uart.sh` as `ExecStartPre=+` (runs as root before daemon)
2. Python `_wake_uart()` fallback in `nextion.py`
Both unbind/rebind the driver and pin `power/control=on`.

### Frame Types
| Code | Type | Format |
|------|------|--------|
| `0x65` | Touch event | `65 PAGE CID EVENT` (EVENT: 0=RELEASE, 1=PRESS, 2=unknown→treat as PRESS) |
| `0x66` | Page report | `66 PAGE_ID` — TFT reports its own page changes |
| `0x70` | String data | `70 <string bytes>` |
| `0x71` | Numeric data | `71 <4 bytes little-endian>` |

### Two Page ID Systems (CRITICAL)
Touch events (`0x65`) carry **TFT-internal page IDs** that are DIFFERENT from the `0x66` page report IDs. The binary touch map uses the touch page IDs. The `screen_map.json` page_ids section maps 0x66 report IDs to page names.

Example: Home page is `0x66 page_id=12`, but touch events from home carry `touch_page_id=12` (happens to match here). Settem is `0x66 page_id=32`, touch events carry `touch_page_id=32` (also matches). But other pages may differ.

### Numpad Frame Format (CRITICAL DISCOVERY)
The TFT numpad does NOT send values as `0x70` string data frames. Instead, it embeds raw ASCII digit bytes BEFORE the touch event in the SAME frame:

```
"250\x65\x20\xAA\x02" = numpad value "250" + touch event (page=32, cid=170, event=2)
```

Pattern: `[ASCII digits][0x65][page][cid][event][0xFF 0xFF 0xFF]`

The numpad parser in `nextion.py` `_on_frame()` handles this by scanning for `0x65` marker and extracting the ASCII digit prefix. The numpad value is stored in `self.last_string_data`.

### Buttons That Send No UART Events
Some TFT buttons handle navigation internally without sending any UART event:
- **Nav bar buttons** (most of them) — TFT navigates internally
- **Back button on settem** — TFT navigates home internally, sends `0x66` page report

For these, we detect the navigation via `0x66` page report in `handle_page_report()`.

### Enter Button on settem
The enter button (cid=18) DOES send a UART event (as RELEASE, event=0), embedded after numpad digits. However, after processing it we must wait **800ms** before sending `page home` — the TFT's button press animation blocks serial commands during that window. Without the delay, `page home` is silently ignored.

## Touch Dispatch Architecture

**Two-tier dispatch in `handle_touch()`:**
1. **Primary:** `screen_map.json` — name-based, keyed by page name + component_id. Real-world tested mappings.
2. **Fallback:** Binary touch map — keyed by packed `(touch_page_id << 8 | component_id)`, extracted from voronFDM disassembly. Has 35 handlers.

This order matters. Earlier we had it reversed and the binary map was overriding correct screen_map entries (e.g., home cid=3 for nozzle was dispatching to a calibration sequence).

## Temperature Entry Flow

1. User taps nozzle (home cid=3) or bed (home cid=4) → `_execute_action` sets `_temp_target_heater` to `"extruder"` or `"heater_bed"` → navigates to settem
2. User types on numpad → TFT sends cid=170 with embedded numpad value → `temp_numpad_update` handler stores value in `_pending_temp`
3. User taps enter (cid=18) → `temp_confirm` handler → `_apply_temp_value()` → sends gcode → 800ms delay → `navigate("home")`
4. **OR** user taps back → TFT navigates away internally → `handle_page_report()` detects leaving settem → `_apply_temp_value_no_nav()` applies pending temp
5. **Safety net:** 3s debounce timer auto-applies pending temp if still on settem (in case neither cid=18 nor page report fires)

## Key Files

- **`nextion.py`** — Serial protocol, frame parsing, numpad parser, UART wake, comok handshake
- **`pages/manager.py`** — Page lifecycle, two-tier touch dispatch, temp entry flow, page report handling, binary touch map, standby timer
- **`screen_map.json`** — Primary touch mappings and 0x66 page ID → name map
- **`daemon.py`** — CLI args including `--dry-run`, mock state setup
- **`moonraker.py`** — Klipper gcode bridge, dry-run mode with mock state updates
- **`wake-uart.sh`** — UART1 runtime PM fix (ExecStartPre)
- **`arco-screen.service`** — systemd unit file

## Current State (as of commit 02458cf)

**Working:**
- Screen init and comok handshake (first attempt usually)
- Home page with live temps from Klipper
- Nozzle and bed temperature entry (full flow: navigate → numpad → enter/back → apply → home)
- LED toggle on home page
- **All 53 TFT pages mapped** with correct 0x66 page report IDs
- Navigation between all mapped pages via 0x66 page report detection
- Page handlers registered for all 53 TFT pages (most are stubs)
- Printing page with full live status (progress, temps, time, filename)
- Temperature page with nozzle/bed current + target temps
- Filament page with AMS unit status
- Standby timeout and wake-on-touch
- Dry-run mode for testing on .235

**Known Issues / TODO:**
- **Button CID discovery needed:** Most button CIDs are unknown. The improved unmapped touch logging (`Unmapped touch: page_name=X page_id=Y cid=Z event=W`) will capture CIDs as buttons are pressed on .40. Add discovered CIDs to `screen_map.json` `touch_map` section.
- **Binary touch map disabled:** voronFDM's 0x99 frame page IDs (1-15) don't match standard TJC 0x65/0x66 IDs (1-61). The binary_touch_map entries never matched real touches. Actions preserved in BINARY_ANALYSIS.md.
- Manual page jog buttons — need CIDs, then wire to: `G91 G1 X{±val} F6000`, `G91 G1 Y{±val} F6000`, `G91 G1 Z{±val} F600`
- Extruder extrude/retract buttons — need CIDs, then wire to: `M83 G1 E{±val} F300`
- Printing page pause/resume/cancel — need CIDs, then wire to: `PRZ_PAUSE`, `PRZ_RESUME`, `PRZ_CANCEL`
- File browser navigation — needs moonraker file API integration
- Print start flow — needs file selection → printplan → PRZ_PRINTING_START
- Speed preset buttons on setsp — need CIDs, then wire to `M220 S{val}`
- Z-offset buttons on offdet — need CIDs, then wire to `SET_GCODE_OFFSET Z_ADJUST=±{val} MOVE=1`
- `SetFlowPage` uses PAGE_NAME="flow" but no "flow" page exists in TFT (flow might be part of setsp)
- .235 test machine offline at last check

## Live Scan Results (2026-04-13)

### All 53 TFT Page IDs (from sendme scan on .40)
```
 1=first       2=firstname    4=firstwifi    5=firstwificon   6=popup1
 7=popup2      8=check        9=NoButLoad   10=choose        11=history
12=home       13=print       14=tool        16=info          17=getready
18=setwifi    19=wait        20=homekey     21=wificon       22=usb
23=printplan  24=printing    25=printfinish 26=manual        27=herdware
28=printerinfo 29=social     30=temperature 31=print_tool    32=settem
33=setsp      34=extruder    35=local       36=standby       37=auto
38=setsd      39=filament    40=cutt_checking 41=monochrome  42=system
43=settime    44=offdet      46=if_reprint  47=update        48=language
50=lifting    53=polychrome  55=Chamber_fan 56=c_cail        57=cutt_cail
58=cutt_arco  59=states      61=update_check
```
Note: Pages 3, 15, 45, 49, 51-52, 54, 56, 60 don't exist. No "settings" page — tool (14) handles both tools and settings.

### Page Name Corrections (from old screen_map)
- page 1 was "print_file_browser_legacy" → actually "first" (setup page)
- page 10 was "print_file_browser_inner" → actually "choose" (file source selector)
- page 15 was "settings" → doesn't exist (merged into "tool" page 14)
- page 27 was "calibration" → actually "herdware" (calibration menu)
- Touch map key "tools" → "tool", "wifi" → "setwifi", "calibration" → "herdware"

### voronFDM Page IDs vs Standard TJC IDs (CRITICAL)
voronFDM uses custom 0x99/0x01 frame types with its OWN page numbering (pages 1-15 in dispatch table), which is DIFFERENT from standard TJC 0x65/0x66 page IDs (1-61). Only two accidental matches: page 12 (home) and page 14 (tool). The binary_touch_map was disabled because all other entries used wrong page IDs and never matched real 0x65 touch events.

## Binary Analysis Results (2026-04-13)

Full documentation in `screen-daemon/BINARY_ANALYSIS.md`. Key findings:

### voronFDM Uses Different Frame Types Than Standard TJC
- voronFDM processes 0x88 (TFT update), 0x99 (touch type A), 0x01 (touch type B)
- It does NOT use standard 0x65/0x66 frames — our daemon adds those via standard TJC protocol init
- The packed value `(page_id << 8 | cid)` is the same concept but from different frame types

### Context-Dependent Mega-Handlers
- The binary's Uart_pthread_cmd (100KB function!) has 45 unique dispatch entries
- Most entries are "mega-handlers" that branch on global state
- Simple direct-action entries exist for: extruder extrude/retract, calibration entry, nozzle wipe, save config, cutting check
- Complex context-dependent behavior belongs in our page handler classes

### Key Actions From Binary (reference for when CIDs are discovered)
```
Extruder extrude:  M83\nG1 E{1,10,20,50} F300
Extruder retract:  M83\nG1 E-{1,10,20,50} F300
Manual jog X:      G91\nG1 X{±1,±10,±50} F6000-F7800\nG90
Manual jog Y:      G91\nG1 Y{±1,±10,±50} F6000-F7800\nG90
Manual jog Z:      G91\nG1 Z{±0.05,±0.1,±1,±10} F600\nG90
Speed presets:     M220 S{50,80,100,120,150}
Print pause:       PRZ_PAUSE
Print resume:      PRZ_RESUME
Print cancel:      PRZ_CANCEL
Nozzle wipe:       PRZ_WIPEMOUTH
Purge:             PRZ_SPITTING
Calibration entry: G91\nG1 Z10\nG90 → G28 Y → G28 X → page c_cail
Save + cool:       SET_HEATER_TEMPERATURE HEATER=extruder TARGET=0 → M84 → SAVE_CONFIG
```

### All 53 TFT Page Names
auto, c_cail, Chamber_fan, check, choose, cutt_arco, cutt_cail, cutt_checking, extruder, filament, first, firstname, firstwifi, firstwificon, getready, herdware, history, home, homekey, if_reprint, info, language, lifting, local, manual, monochrome, NoButLoad, offdet, polychrome, popup1, popup2, print, print_tool, printerinfo, printfinish, printing, printplan, setsd, setsp, settem, settime, setwifi, social, standby, states, system, temperature, tool, update, update_check, usb, wait, wificon

### PRZ Custom Klipper Macros
PRZ_ADC, PRZ_BM0, PRZ_BM1, PRZ_CANCEL, PRZ_MANUAL_WAITING, PRZ_PAUSE, PRZ_PRINTING_START, PRZ_RESTORE, PRZ_RESUME, PRZ_SPITTING, PRZ_WIPEMOUTH, PGZ, TP_OUT, prz_version, p114, P1 B/T/J (AMS), P2 A2/A3/A6 (ChromaKit)

### Complete Screen Elements Per Page
See BINARY_ANALYSIS.md Section 4 for full listing of every element.property on every page (txt=text, val=numeric, pic=image). This is the definitive reference for what our page handlers should be updating.

## Debugging Tips

- `journalctl -u arco-screen --no-pager -n 50` — recent logs
- RAW frame hex is logged at DEBUG level: `RAW frame [N bytes]: HEXSTRING`
- **Unmapped touches** now log at INFO with actionable info: `Unmapped touch: page_name=X page_id=Y cid=Z event=W (add to screen_map.json touch_map.X.Z)`
- To discover button CIDs: tap buttons on .40, then `grep "Unmapped touch" journalctl output`
- Always clear `__pycache__` after deploying new code before restarting
- Scanner scripts in repo `/tmp/` on .40: `scan_page_ids.py`, `scan_components_fast.py`, `scan_cids.py`
