# voronFDM Binary Analysis — Touch Dispatch & Screen Elements

Comprehensive reverse engineering notes from `bin/voronFDM` (ELF 64-bit aarch64, not stripped, 855 KB).

**Binary:** `bin/voronFDM`  
**Build ID:** `8082c2b1664f999f2c4201e866c82680ef903c14`  
**Tools used:** capstone (Python ARM64 disassembler), objdump, strings  
**Analysis date:** 2026-04-13

---

## 1. Architecture Overview

### Key Functions

| Function | Offset | Size | Purpose |
|----------|--------|------|---------|
| `Uart_pthread` | 0x1fba0 | 0x1b4 | UART read loop, calls Uart_pthread_cmd |
| `Uart_pthread_cmd` | 0x1fd54 | 0x18940 (100KB!) | Main touch/event dispatch — giant switch |
| `main_ScreenUpdate` | 0x5a04 | 0x558 | TFT firmware update handler |
| `Uart_pthread_cmddatasend` | 0x38694 | 0x60 | UART data send helper |
| `Utils_sendstring` | 0x10f80 | — | Send string command to TFT |
| `Popup_pthread` | 0x5e5c8 | 0x1284 | Popup/dialog handler |
| `Usb_pthread` | 0x3f0ac | — | USB file browser handler |
| `Usb_pthread_localSend` | 0x4371c | — | Local file list send |
| `Usb_pthread_hisSend` | 0x44a70 | — | History file list send |
| `WifiManage_pthread` | 0x396f8 | — | WiFi management |
| `WifiManage_pthread_wifiSend` | 0x3a054 | 0x1640 | WiFi list display |
| `Websocket_pthread` | 0x3cea4 | — | WebSocket for Moonraker |
| `Time_pthread` | 0x5f8b8 | — | Time/clock management |
| `Picture_pthread` | 0x5d8f8 | — | Thumbnail/picture handler |
| `utils_Global_Control` | 0x134ac | — | Global state controller |

### Frame Types

The UART protocol uses these frame markers (NOT standard Nextion):

| Byte | Type | Notes |
|------|------|-------|
| 0x88 | TFT firmware update | Triggers update page + progress display |
| 0x99 | Touch event (type A) | Packed into 32-bit: `(page<<8) \| cid` stored at sp+0x48c |
| 0x01 | Touch event (type B) | Packed into 16-bit: `(page<<8) \| cid` stored at sp+0x48a |

**Frame parsing at 0x20240:**
1. Read byte → if 0x99: read next 2 bytes, pack as `(byte1 << 8) | byte2`
2. Store packed value and dispatch via switch
3. If 0x01: same packing but stored in different location, separate switch

**IMPORTANT:** voronFDM does NOT process 0x65 touch events or 0x66 page reports. Our daemon adds those as the Nextion/TJC standard protocol. The TFT firmware sends 0x99/0x01 frames to voronFDM but sends standard 0x65/0x66 frames to us because we're using a different protocol init (bkcmd=0 + page commands).

---

## 2. Touch Dispatch Table

### Overview

45 unique (touch_page, component_id) entries found in Uart_pthread_cmd. The dispatch is **heavily context-dependent** — the same packed value triggers different actions based on global state variables (active page, printing state, calibration step, etc.).

### Critical Insight: Mega-Handlers

Several entries (especially cid=1 on pages 1-4, 9, 11, 14, 15) are "mega-handlers" containing 20-50 gcode commands and 10-20 navigation targets. These are NOT flat dispatches — they contain internal `if/else` chains that check:
- Current active page name
- Printing state (idle/printing/paused)
- Calibration step counter
- AMS/ChromaKit connection state
- First-time setup state

This means our `_binary_touch_map` in manager.py should only use the SIMPLE cases (dedicated per-page handlers) and leave the complex context-dependent cases to our page handler classes.

### Simple Direct-Action Entries (safe for binary touch map)

These entries have clear, single-purpose actions:

```
0x0301 (page=3, cid=1)  — Extruder: Extrude E1 F300
0x0302 (page=3, cid=2)  — Extruder: Extrude E10 F300
0x0303 (page=3, cid=3)  — Extruder: Extrude E20 F300
0x0304 (page=3, cid=4)  — Extruder: Extrude E50 F300
0x0401 (page=4, cid=1)  — Extruder: Retract E-1 F300
0x0402 (page=4, cid=2)  — Extruder: Retract E-10 F300
0x0403 (page=4, cid=3)  — Extruder: Retract E-20 F300
0x0404 (page=4, cid=4)  — Extruder: Retract E-50 F300
0x0C03 (page=12, cid=3) — Home: Calibration entry sequence
0x0C04 (page=12, cid=4) — Home: Nozzle wipe/cutter sequence
0x0C05 (page=12, cid=5) — Home: Nozzle wipe variant
0x0F02 (page=15, cid=2) — Calibration: Save config, cool, disable steppers
0x0F04 (page=15, cid=4) — Calibration: Cutting check start
```

### Context-Dependent Mega-Handlers (handle in page classes, NOT binary map)

These packed values dispatch to MANY different actions based on internal state:

```
0x0101 (page=1, cid=1)  — 18 navs, 43 gcodes — used across many pages
0x0201 (page=2, cid=1)  — 19 navs, 50 gcodes — used across many pages
0x0301 (page=3, cid=1)  — 14 navs, 49 gcodes — mixed extrude + nav
0x0401 (page=4, cid=1)  — 7 navs, 40 gcodes — mixed retract + nav
0x0901 (page=9, cid=1)  — 18 navs, 29 gcodes — settings + calibration
0x0A01 (page=10, cid=1) — 8 navs, 23 gcodes — filament + AMS
0x0B01 (page=11, cid=1) — 9 navs, 23 gcodes — wifi + setup
0x0E01 (page=14, cid=1) — 12 navs, 29 gcodes — tools + jog + temp
0x0F01 (page=15, cid=1) — 11 navs, 27 gcodes — calibration + print + jog
```

### Nav-Bar Entries (TFT-internal, cid=0 on various pages)

These are the nav bar buttons. The TFT often handles navigation internally, but voronFDM also has handlers for them:

```
0x0100 (page=1, cid=0)  — Navigate to homekey + set temp
0x0200 (page=2, cid=0)  — Navigate to homekey + set temp
0x0300 (page=3, cid=0)  — Screen update only (no nav)
0x0400 (page=4, cid=0)  — First-time setup + system
0x0500 (page=5, cid=0)  — File browser (USB/local/history)
0x0600 (page=6, cid=0)  — File browser + print start
0x0700 (page=7, cid=0)  — Preheat nozzle 220°C
0x0800 (page=8, cid=0)  — History browser + choose
0x0900 (page=9, cid=0)  — File browser + Chamber fan
0x0A00 (page=10, cid=0) — Manual/filament/setsp nav
0x0B00 (page=11, cid=0) — File browser pages
0x0C00 (page=12, cid=0) — Home page main area
0x0E00 (page=14, cid=0) — AMS/ChromaKit controls
0x0F00 (page=15, cid=0) — Print control + popups
```

---

## 3. All TFT Page Names

48 unique page names found via `page <name>` string commands:

```
auto            c_cail          Chamber_fan     check
choose          cutt_arco       cutt_cail       cutt_checking
extruder        filament        first           firstname
firstwifi       firstwificon    getready        herdware
history         home            homekey         if_reprint
info            language        lifting         local
manual          monochrome      NoButLoad       offdet
polychrome      popup1          popup2          print
print_tool      printerinfo     printfinish     printing
printplan       setsd           setsp           settem
settime         setwifi         social          standby
states          system          temperature     tool
update          update_check    usb             wait
wificon
```

---

## 4. Screen Elements Per Page

Complete list of TFT screen elements found in binary strings. Each entry shows `element.property` (txt=text, val=numeric, pic=picture ID).

### Home Page (`home`)
```
NAME.txt       — Machine name
pwifi.pic      — WiFi icon
t0.txt         — Bed temperature display
t1.txt         — Nozzle temperature display
```

### Printing Page (`printing`)
```
NAME.txt       — Machine name
PRINT_IP.txt   — IP address
b1.pic         — LED/pause button icon
b2.pic         — Second button icon
cname.txt      — Current filename
j0.val         — Progress bar (0-100)
mm.txt         — Layer height
num1.pic       — Digit display 1
num2.pic       — Digit display 2
pwifi.pic      — WiFi icon
t1.txt         — Nozzle temp
t2.txt         — Bed temp
t3.txt         — Fan speed %
t4.txt         — Print speed %
t5.txt         — Time remaining
t6.txt         — Time elapsed
t15.txt        — Z position
t16.txt        — Z position (secondary)
```

### Standby Page (`standby`)
```
NAME.txt       — Machine name
PRINT_IP.txt   — IP address display
b1.pic         — LED status icon
n0.pic         — Status icon 0
n1.pic         — Status icon 1
pwifi.pic      — WiFi icon
sname.txt      — Secondary name
```

### Temperature Page (`temperature`)
```
NAME.txt       — Machine name
he.txt         — Bed temp current
he1.txt        — Bed temp target
no.txt         — Nozzle temp current
no1.txt        — Nozzle temp target
nozz.val       — Nozzle numeric value
pwifi.pic      — WiFi icon
```

### Set Temperature Page (`settem`)
```
t0.txt         — Current temperature display
pic            — Background pic (141 for bed mode)
```

### Manual Page (`manual`)
```
NAME.txt       — Machine name
pwifi.pic      — WiFi icon
xy.pic         — XY plane indicator (pic=100)
z.pic          — Z axis indicator (pic=98)
```

### Extruder Page (`extruder`)
```
NAME.txt       — Machine name
bex.txt        — Target temp display
ex.val         — Current temp value
pwifi.pic      — WiFi icon
```

### Filament Page (`filament`)
```
NAME.txt       — Machine name
ams1.val       — AMS tray 1 state
ams2.val       — AMS tray 2 state
ams3.val       — AMS tray 3 state
ams4.val       — AMS tray 4 state
bex.txt        — Target temp
ex.val         — Current temp value
fil_num.val    — Active filament number
pwifi.pic      — WiFi icon
```

### Monochrome Page (`monochrome`)
```
NAME.txt       — Machine name
bex.txt        — Target temp
ex.val         — Current temp value
pwifi.pic      — WiFi icon
```

### Speed/Flow Pages (`setsp`, `flow`)
```
setsp:
  NAME.txt, pwifi.pic
  sp.val         — Speed slider value
  sp1.val        — Flow slider value
  spdata.txt     — Speed percentage text
  spdata1.txt    — Flow percentage text

flow:
  NAME.txt, pwifi.pic
  flowdata.txt   — Flow percentage text
  sp.val         — Flow slider value
```

### Z-Offset Page (`offdet`)
```
NAME.txt       — Machine name
pwifi.pic      — WiFi icon
z_offset.txt   — Z offset value (%.3f format)
```

### File Browser (`print`)
```
NAME.txt       — Machine name
j0.val         — Storage bar
pwifi.pic      — WiFi icon
t0.txt         — Storage text
usb.pic        — USB icon
```

### Print Plan Page (`printplan`)
```
au.pic         — Auto-start icon (168=off, 169=on)
but.pic        — Button icon
plan_judge.val — Plan state
t0.txt         — File name
t1.txt         — Estimated time
t2.txt         — Layer height
t3.txt         — Filament type
t4.txt         — Filament color
t7.txt         — File source
xz.pic         — Unknown icon (168/169)
```

### Print Finish Page (`printfinish`)
```
NAME.txt       — Machine name
fname.txt      — Filename
pwifi.pic      — WiFi icon
t1.txt         — Total duration
t2.txt         — Filament used
```

### Get Ready Page (`getready`)
```
get_num.val    — Stage number (1-7)
```

### Wait Page (`wait`)
```
update_j.val   — Progress value
wait_data.val  — Wait state data
```

### System Page (`system`)
```
NAME.txt       — Machine name
pwifi.pic      — WiFi icon
sys_data.val   — System data flag (0 or 1)
temname.txt    — Machine name edit
time.txt       — Standby timeout text
```

### Set Time Page (`settime`)
```
NAME.txt       — Machine name
min.txt        — Minutes display
min_num.val    — Minutes numeric
pwifi.pic      — WiFi icon
setime.val     — Slider value
```

### WiFi Page (`setwifi`)
```
NAME.txt       — Machine name
ip.txt         — IP address
pwifi.pic      — WiFi icon
wifi1.pic      — WiFi network 1 signal icon
wifi1pic.pic   — WiFi network 1 type icon
wifi1st.pic    — WiFi network 1 state icon
(also wifi2*, wifi3* for networks 2-3)
```

### Chamber Fan Page (`Chamber_fan`)
```
CFAN_NUM.val   — Fan speed percentage
NAME.txt       — Machine name
pwifi.pic      — WiFi icon
```

### Update Page (`update`)
```
L_update.txt   — Update progress text ("%d / %d")
dev.val        — Device type
j0.val         — Progress bar
n0.val         — Counter
```

### Calibration Pages
```
auto:
  NAME.txt, pwifi.pic
  t0.txt         — Bed temp
  t1.txt         — Nozzle temp
  temp_data.txt  — Nozzle temp (secondary)

c_cail:
  NAME.txt, pwifi.pic
  c_cail_num.val — Step counter
  setorfirst.val — First/subsequent flag

cutt_arco:
  NAME.txt, pwifi.pic
  cutt_arco_num.val — Step counter

cutt_cail:
  NAME.txt, pwifi.pic
  ams_num_cail.val  — AMS present flag
  cutt_cail_num.val — Step counter

check:
  NAME.txt, pwifi.pic
  p0.pic, p1.pic, p2.pic — Check state icons
```

### Popup/Dialog Pages
```
popup1:
  pop_num.val    — Dialog type (see Popup Types below)

popup2:
  ch.txt         — Channel text
  pop2_num.val   — Notification type
  pop_txt.txt    — Message text
```

### Info Pages
```
printerinfo:
  NAME.txt, pwifi.pic
  ams_sum.txt    — AMS count
  t0.txt         — Firmware version
  vv_1..vv_5.txt — AMS unit serial numbers
  vv_sum.txt     — AMS summary

states:
  STA.txt        — Status text
  edata.txt      — Error data
```

### USB Page (`usb`)
```
NAME.txt       — Machine name
path.txt       — Current path
pwifi.pic      — WiFi icon
usbno.pic      — USB device icon (151=present)
```

### Setup Pages
```
firstname:
  NAME.txt, pwifi.pic, t0.txt

firstwificon / wificon:
  t1.txt         — IP address

homekey:
  t0.txt         — Key/name display

lifting:
  firstnum.val   — Stage number (3)
```

---

## 5. Popup Types

### popup1 (pop_num values)
| Value | Likely Purpose |
|-------|---------------|
| 1 | Generic info |
| 2 | Confirmation |
| 4 | First-time setup prompt |
| 5 | WiFi connection prompt |
| 6 | Print confirmation / fan control |
| 7 | Heater timeout warning |
| 8 | Heater warning (extruder) |
| 10 | Error/warning |
| 12 | Filament error |
| 13 | Config error |
| 15 | Cancel print confirmation |
| 16 | Motor/stepper warning |
| 17 | Auto-level warning |
| 18 | Network error |
| 20 | Calibration result |
| 21 | Calibration result |
| 22 | Print start confirmation |
| 24 | Calibration save prompt |
| 25 | System action confirmation |
| 27 | Firmware check |
| 28 | Update notification |
| 29 | Update notification |
| 30 | Print recovery |
| 31 | Print recovery |
| 32 | Print recovery |

### popup2 (pop2_num values)
| Value | Likely Purpose |
|-------|---------------|
| 1 | General notification |
| 2 | Info notification |
| 3 | Print status update |
| 4 | Calibration prompt |
| 5 | Calibration prompt (variant) |
| 6 | Home/calibration popup |
| 8 | Error notification |
| 9 | Warning notification |
| 10 | Warning notification (variant) |
| 11 | File browser: no USB |
| 12 | File browser: no files |
| 13 | File browser: loading |
| 14 | File browser: error |
| 15 | Print info |
| 16 | System info (settime) |
| 17 | File operation |
| 18 | Cloud/network status |
| 19 | AMS notification |
| 20 | AMS notification (variant) |
| 21 | AMS notification (variant) |
| 22 | AMS notification (variant) |
| 24 | Print plan info |
| 25 | Cutting calibration |

---

## 6. PRZ Gcode Macros

Custom Klipper macros used by voronFDM:

| Macro | Purpose |
|-------|---------|
| `PRZ_ADC` | A/D converter calibration |
| `PRZ_BM0` | Bed mesh profile 0 |
| `PRZ_BM1` | Bed mesh profile 1 |
| `PRZ_CANCEL` | Cancel print |
| `PRZ_MANUAL_WAITING` | Manual filament change wait |
| `PRZ_PAUSE` | Pause print |
| `PRZ_PRINTING_START` | Start print |
| `PRZ_RESTORE` | Restore from power loss |
| `PRZ_RESUME` | Resume print |
| `PRZ_SPITTING` | Nozzle purge |
| `PRZ_WIPEMOUTH` | Nozzle wipe sequence |
| `PGZ` | Unknown (Z-related) |
| `TP_OUT` | Temperature output? |
| `p114` | AMS/ChromaKit command |
| `P1 B%d` | AMS tray select |
| `P1 T%d` | AMS tray activate |
| `P1 J%d` | AMS feed control |
| `P2 A2` | AMS mode switch |
| `P2 A3` | Cutting check |
| `P2 A6` | ChromaKit control |
| `prz_version` | Query firmware version |

---

## 7. Visibility (vis) Commands

Key visibility toggles used for dynamic UI:

| Command | Purpose |
|---------|---------|
| `vis exp0,1` | Show experience/progress bar |
| `vis c_fan,1` | Show chamber fan controls |
| `vis usbno,1/0` | Show/hide USB device icon |
| `vis lol1..3,1/0` | Show/hide file list items 1-3 |
| `vis XZ,0` | Hide XZ display |
| `vis banx,1` | Show banner |
| `vis www,1` | Show web status |
| `vis model,1` | Show 3D model preview |
| `vis A1..4,1/0` | Show/hide AMS trays |
| `vis BA,BA1..4` | AMS base visibility |
| `vis CA1..4` | AMS color visibility |
| `vis auto_pic,1` | Show auto-level icon |
| `vis bed_pic,1` | Show bed icon |
| `vis ex_pic,1` | Show extruder icon |
| `vis res_pic,1` | Show resonance icon |
| `vis tem_pic,1` | Show temperature icon |
| `vis cut1_pic,1` | Show cutter icon |
| `vis cut2_pic,1` | Show cutter icon (variant) |
| `vis sw0,1` | Show switch |
| `vis wifi1..3,*` | WiFi network visibility |
| `vis wifi1pic,*` | WiFi icon visibility |
| `vis wifi1st,*` | WiFi state visibility |
| `vis h1..3,*` | History items visibility |
| `vis p0..2,*` | Print items visibility |
| `vis s1..3,*` | Settings items visibility |
| `vis usb1..3,*` | USB items visibility |
| `vis x1..3,*` | Extra items visibility |
| `vis zx1..2,*` | Z-axis extra visibility |

---

## 8. LED/Button Picture IDs

| Element | PIC ID | Meaning |
|---------|--------|---------|
| `led.pic=69` | 69 | LED ON |
| `led.pic=70` | 70 | LED OFF |
| `led.pic2=69` | 69 | LED ON (secondary) |
| `led.pic2=70` | 70 | LED OFF (secondary) |
| `printing.b1.pic=52` | 52 | Printing LED ON |
| `printing.b1.pic=53` | 53 | Printing LED OFF |
| `standby.b1.pic=52` | 52 | Standby LED ON |
| `standby.b1.pic=53` | 53 | Standby LED OFF |
| `manual.xy.pic=100` | 100 | XY plane icon |
| `manual.z.pic=98` | 98 | Z axis icon |
| `usb.usbno.pic=151` | 151 | USB device present |
| `EX.pic=240` | 240 | Extruder icon (idle) |
| `EX.pic=241` | 241 | Extruder icon (active) |
| `RE.pic=235` | 235 | Retract icon |
| `printplan.au.pic=168` | 168 | Auto-start OFF |
| `printplan.au.pic=169` | 169 | Auto-start ON |
| `printplan.xz.pic=168` | 168 | XZ OFF |
| `printplan.xz.pic=169` | 169 | XZ ON |

---

## 9. File Browser String Patterns

The file browser uses format strings for displaying up to 3 items per page:

```
%s.name1.txt    — File 1 name
%s.name1_c.txt  — File 1 name (copy/alternative)
%s.name2.txt    — File 2 name
%s.name2_c.txt  — File 2 name (copy)
%s.name3.txt    — File 3 name
%s.name3_c.txt  — File 3 name (copy)
%s.data1.txt    — File 1 date
%s.data2.txt    — File 2 date
%s.data3.txt    — File 3 date
%s.datatime1.txt — File 1 time
%s.datatime2.txt — File 2 time
%s.datatime3.txt — File 3 time
%s.lt1..3.txt   — File 1-3 layer/time info
%s.xt1..3.txt   — File 1-3 extra info
%s.ut1..3.txt   — File 1-3 update time
%s.tx1..3.txt   — File 1-3 text info
%s.wifi1..3.txt — WiFi network names (setwifi context)
```

Where `%s` is the current page name (e.g., `print`, `usb`, `history`, `local`).

---

## 10. Speed Preset Values

voronFDM uses fixed speed presets (not arbitrary values):

```
M220 S50   — 50% speed
M220 S80   — 80% speed
M220 S100  — 100% speed (default)
M220 S120  — 120% speed
M220 S150  — 150% speed
```

---

## 11. Jog Movement Commands

### XY Jog (F6000-F7800)
```
G91; G1 x-0.1 F6000; G90    — X -0.1mm (fine)
G91; G1 x0.1 F6000; G90     — X +0.1mm (fine)
G91; G1 x-%d F6000; G90     — X -Nmm (variable)
G91; G1 x%d F6000; G90      — X +Nmm (variable)
G91; G1 x-0.5 F6000; G90    — X -0.5mm (cutter)
G91; G1 x0.5 F6000; G90     — X +0.5mm (cutter)
G91; G1 X-1 F600; G90       — X -1mm (slow)
G91; G1 X1 F600; G90        — X +1mm (slow)
G91; G1 X-25 F7800; G90     — X -25mm (fast)
G91; G1 X25 F7800; G90      — X +25mm (fast)
G91; G1 X-50 F600; G90      — X -50mm (bed mesh)
G91; G1 y-0.1 F6000; G90    — Y -0.1mm
G91; G1 y0.1 F6000; G90     — Y +0.1mm
G91; G1 y-%d F6000; G90     — Y -Nmm
G91; G1 y%d F6000; G90      — Y +Nmm
G91; G1 Y-25 F7800; G90     — Y -25mm (fast)
G91; G1 Y25 F7800; G90      — Y +25mm (fast)
```

### Z Jog (F600)
```
G91; G1 z-0.1 F600; G90     — Z -0.1mm
G91; G1 z0.1 F600; G90      — Z +0.1mm
G91; G1 z-%d F600; G90      — Z -Nmm
G91; G1 z%d F600; G90       — Z +Nmm
G91; G1 z10 F600; G90       — Z +10mm (lift)
G91; G1 z180 F600; G90      — Z +180mm (full lift)
```

### Park Positions
```
G1 X149 Y290 F4000          — Wipe start position
G1 X149 Y321 F4000          — Wipe mid position
G1 X124 Y321 F4000          — Wipe end position
G1 X149 Y321 F8000          — Fast wipe position
G1 X310 Y290 F8000          — Service position
G1 X310 Y260 F6000          — Calibration park
```

---

## 12. Calibration Sequences

### Auto-Level Entry
1. `G91; G1 Z10; G90` — Lift Z 10mm
2. `G28 Y` — Home Y
3. `G28 X` — Home X
4. Navigate to `c_cail` page
5. Set `c_cail.c_cail_num.val=1`

### Nozzle Wipe
1. `M83; G1 E-10 F300` — Retract 10mm
2. `M106 S255` — Fan full
3. `G1 X149 Y321 F8000` — Move to wipe position
4. `M106 S0` — Fan off
5. `G28` — Home all
6. `M84` — Disable steppers

### Bed Mesh Calibration
1. `G90; M140 S60; M104 S140; G28; G90`
2. `M106 S255` — Fan full
3. `BED_MESH_CLEAR`
4. `BED_MESH_CALIBRATE PROFILE=phrozen`

### Cutting Check
1. `G28 Y; G28 X`
2. `P2 A3` — ChromaKit cutting mode
3. `SET_HEATER_TEMPERATURE HEATER=extruder TARGET=220`
4. Navigate to `cutt_checking`

---

## 13. Known Limitations of This Analysis

1. **Context-dependent dispatch:** The binary uses global state to determine which action to take for the same (page, cid) value. Our static analysis captures ALL possible actions per entry but cannot determine the exact runtime conditions.

2. **AMS/ChromaKit commands:** `P1`, `P2`, `p114` commands are for the ChromaKit multi-material unit and only apply when AMS is connected.

3. **Format strings:** Many gcode commands use `%d` or `%0.3f` format specifiers — the actual values come from runtime state (temperature settings, position values, etc.).

4. **Additional dispatch threads:** `Popup_pthread`, `Usb_pthread`, `WifiManage_pthread` handle their own UART events outside of `Uart_pthread_cmd`. These haven't been fully analyzed here.

5. **0x66 page reports:** voronFDM doesn't use standard 0x66 page reports. Our daemon adds this capability via the standard TJC protocol. Page IDs in our `screen_map.json` come from live testing with `sendme` queries, not from the binary.
