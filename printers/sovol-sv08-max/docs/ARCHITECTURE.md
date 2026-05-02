# Sovol SV08 Max — Architecture

System topology + how the stock Sovol stack hangs together. For the
full stock-OS audit see `STOCK-INVENTORY.md`; for cross-printer
reconciliation against the Sovol Zero see `ALIGNMENT-WITH-ZERO.md`.

## Hardware

| Component | Details |
|-----------|---------|
| SBC | BigTreeTech CB1 module (Allwinner H616, 4× Cortex-A53, 1 GB RAM, ~32 GB eMMC) |
| Mainboard | Sovol-custom `H616_JC_6Z_5160_V1.2` — CB1 socketed on, plus the X/Y TMC5160 SPI drivers and the USB-CAN bridge silicon |
| Main MCU | STM32H750xx @ 400 MHz (inferred from `~/klipper/.config750`); functions as both the printer's main MCU **and** the host-side USB-to-CAN bridge (CONFIG_USBCANBUS=y). Exposed to Linux via USB as `1d50:606f` (Geschwister Schneider gs_usb adapter). Klipper-side CAN UUID `0d1445047cdd`. |
| Toolhead MCU | STM32F103xe @ 72 MHz, on the CAN bus. Klipper-side CAN UUID `61755fe321ac` (named `[mcu extra_mcu]` in printer.cfg). Carries: extruder stepper + driver, hotend heater + thermistor, hotend fan + tach, dual part-cooling fans, LDC1612 eddy probe, LIS2DW accelerometer. |
| Chamber MCU | STM32F103xe @ 72 MHz, on the CAN bus. Klipper-side CAN UUID `58a72bb93aa4` (named `[mcu hot_mcu]` in `chamber_hot.cfg`). Carries: chamber heater + thermistor, chamber outlet temp, chamber fan tachometer, hot_led indicator. |
| CAN bus | 1 Mbit, brought up by `/etc/network/interfaces.d/can0` (classic ifupdown) over the gs_usb USB device. No native CAN on the SBC. All three MCUs are on this bus. |
| Kinematics | CoreXY, ~500×505×505 mm, 4-Z quad-gantry with `gear_ratio: 80:12` |
| Steppers X/Y | TMC5160 (SPI, 3.0 A run current, sensorless capable but not configured) |
| Steppers Z×4 | TMC2209 (UART, 1.2 A) |
| Extruder | TMC2209 (UART, 0.8 A run / 0.3 A hold), `rotation_distance: 6.5` (geared) |
| Probe | `probe_eddy_current` via LDC1612 on `extra_mcu` i2c2 (eddy/scanner-style, contact + non-contact via Sovol's `vir_contact_speed` extension) |
| Accelerometer | LIS2DW on `extra_mcu` SPI (replaces the more common ADXL345) |
| Display (primary) | Serial TFT touchscreen, Nextion-class, on `/dev/ttyS3` at 9600 baud. Vendor-supplied `.tft` firmware blob (`众创klipper.tft.bak`, 9.7 MB, closed). |
| Display (secondary) | Optional: HDMI display attached to the CB1's HDMI port. Driven by KlipperScreen via Xorg fbdev on `/dev/tty7`. Disabled when nothing's plugged in. |
| Fans | fan0 (front part-cooling, toolhead) + fan1 (back part-cooling, toolhead) + fan2 (auxiliary, main MCU) + fan3 (exhaust, main MCU) + heater_fan hotend_fan (toolhead, with tach) + heater_fan bed_fan (main MCU) |
| Sensors | Extruder NTC (custom Sovol thermistor table — PT1000-shaped curve, max 310 °C), bed NTC (100K, max 120 °C), chamber NTC (max 65 °C, watermark control), filament switch (PB2), filament motion encoder (PE7) |

## Software stack

```
┌─────────────────────────────────────────────────────────────┐
│  Mainsail UI  (active, served by nginx :80)                 │
│  Fluidd UI    (installed, not served)                       │
├─────────────────────────────────────────────────────────────┤
│  Moonraker API (:7125)                                      │
├─────────────────────────────────────────────────────────────┤
│  Klipper (Sovol fork @ d4031b3, base 0.12.0)                │
│  ├── klippy/extras/z_offset_calibration.py  (Sovol-original)│
│  ├── klippy/extras/probe_pressure.py        (Sovol-derived) │
│  ├── klippy/extras/probe_eddy_current.py    (modified)      │
│  ├── klippy/extras/ldc1612.py / lis2dw.py   (modified)      │
│  ├── klippy/extras/bed_mesh.py              (rapid-scan ext)│
│  └── klippy/extras/display/menu.{py,cfg}    (~/patch/ overlay)│
├─────────────────────────────────────────────────────────────┤
│  zhongchuang_klipper                                        │
│  ├── connects to Moonraker WebSocket on localhost:7125      │
│  └── drives serial TFT on /dev/ttyS3                        │
│                                                             │
│  KlipperScreen (xinit/Xorg/fbdev on tty7)  [if HDMI plugged]│
│                                                             │
│  moonraker-obico  →  app.obico.io  (continuous heartbeat)   │
│  crowsnest        →  ustreamer on 127.0.0.1:8080            │
│  wifi_server.py   :5000  (root, Flask)  ← CRITICAL RCE      │
├─────────────────────────────────────────────────────────────┤
│  USB → gs_usb (1d50:606f) → can0 (1 Mbps)                   │
│  ├── main MCU (STM32H750xx) — UUID 0d1445047cdd            │
│  ├── extra_mcu / toolhead (F103xe) — UUID 61755fe321ac     │
│  └── hot_mcu / chamber  (F103xe) — UUID 58a72bb93aa4       │
└─────────────────────────────────────────────────────────────┘
```

## Boot sequence

Two parallel boot tracks. See `STOCK-INVENTORY.md` § "Boot sequence
on stock" for the full breakdown; the headline:

1. **systemd → multi-user.target.wants** brings up the standard
   stack: klipper, moonraker, KlipperScreen (rendering to whatever
   fbdev is available), crowsnest, nginx, ssh, ntp, NetworkManager,
   wpa_supplicant, hostapd (which auto-restarts because no AP
   config exists), wifi_server, makerbase-client (the
   zhongchuang_klipper TFT daemon), moonraker-obico.
2. **`/etc/rc.local` → `/boot/scripts/btt_init.sh`** runs the
   vendor track: chowns `~/sovol`, sweeps `/boot/gcode/` into the
   print spool, and backgrounds `system_cfg.sh` (timezone /
   hostname / KS rotation / BTT_PAD7 toggles), `connect_wifi.sh`,
   and `file_change_save.sh`. Sovol left the `ota_service.sh`
   launch line **commented out** in this file on the SV08 Max,
   so the OTA daemon never runs and the `_OTA` Klipper macro is
   inert.

## Sovol custom code — what it does

### `~/zhongchuang/` — TFT screen daemon

Open-source C++ daemon that drives the serial TFT touchscreen.
Source tree on disk; built into
`~/zhongchuang/build/zhongchuang_klipper` (8.6 MB ELF aarch64).
Internal git origin `http://192.168.1.233/root/zhongchuang.git`
(Sovol's LAN Gitea — decorative post-ship).

It's a Makerbase mksclient derivative. Mksclient lineage files
(`MoonrakerAPI.cpp`, `KlippyGcodes.cpp`, `KlippyRest.cpp`,
`process_messages.cpp`, `refresh_ui.cpp`, `ui.cpp`,
`MakerbasePanel.cpp`, `MakerbaseShell.cpp`, `MakerbaseSerial.cpp`,
`MakerbaseParseIni.cpp`, `event.cpp`, `file_list.cpp`,
`wifi_list.cpp`, `mks_*.cpp`) handle the Moonraker WebSocket
client, gcode dispatch, file browsing, the panel UI state machine,
and the serial protocol to the TFT.

Sovol's addition is `src/sovol_http.cpp` — wraps Comgrow OTA
progress notifications and exposes them on the TFT panel during
`_OTA` runs. (Note: the OTA daemon isn't running at boot on the
Max, so this code path is dormant.)

Build system: CMake. Links against `pthread`, `boost_system`,
`wpa_client`, `curl`. Built once at factory time per
`/root/.bash_history`; the `~/zhongchuang/build/` dir contains the
artifacts. Companion utilities (`wpa_test.c`, `wpa_wifi.c`,
`wpa.mk`) handle WPA-CLI interaction for wifi setup screens.

The systemd unit (`makerbase-client.service`) launches the daemon
as **root** with `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libSegFault.so`
and `LimitCORE=infinity` — Sovol expects segfaults and wants core
dumps. Auto-restarts every 5 seconds.

### `~/klipper/klippy/extras/` Sovol modifications

Sovol's klipper fork at `http://192.168.1.233/root/klipper.git`,
HEAD `d4031b3 zoffset校准增加前置电流校准动作`. Diff against
upstream Klipper 0.12.0 concentrates on the eddy-current Z probe
and the resulting bed-mesh / homing flow:

| File | Origin | Purpose |
|------|--------|---------|
| `z_offset_calibration.py` | Sovol-original | `Z_OFFSET_CALIBRATION` g-code used in `START_PRINT`. Depends on `probe`, `probe_eddy_current`, `manual_probe`. Header credits `Sovol3d <info@sovol3d.com>`. |
| `probe_eddy_current.py` | upstream + Sovol mods | Adds `vir_contact_speed`, `TYPE_VIR_TOUCH` — non-contact eddy probing with a "virtual contact" approach distinct from upstream Klipper's. |
| `probe_pressure.py` | Sovol-original (derived from `probe.py`) | Pressure-sensing probe path. |
| `ldc1612.py` | upstream + Sovol mods | LDC1612 driver with custom calibration hooks. |
| `lis2dw.py` | upstream + Sovol mods | LIS2DW accelerometer (replaces ADXL345 in the Sovol toolchain). |
| `bed_mesh.py` | upstream + Sovol mods (heavily extended) | `rapid_scan` and eddy-current `BED_MESH_CALIBRATE` — much faster bed mapping. |
| `fan.py`, `heater_fan.py` | upstream + minor mods | Toolhead-fan tach handling tweaks. |
| `homing.py`, `probe.py` | upstream + minor mods | Adjusted to the eddy-probe contact model. |
| `shaper_calibrate.py` | upstream + minor mods | |
| `display/menu.py`, `display/menu.cfg`, `display/display.cfg` | Sovol overlay (~/patch/) | Replaces upstream menu definitions for the small UC1701 LCD path. **Not used on the SV08 Max** (the Max uses the serial TFT, not a UC1701 LCD) — present because the patch tree is shared with the Sovol Zero. |

Replacing the Sovol klipper fork with vanilla upstream or Kalico
loses the eddy-probe contact behavior unless those modules are
ported forward.

### `~/printer_data/build/` — MCU flashing

Sovol-shipped Katapult/CanBoot CAN-flashing tooling:

| Script | MCU | Expected blob path |
|--------|-----|--------------------|
| `mcu_update_fw.sh` | main (UUID `0d1445047cdd`) | `~/printer_data/build/mcu_klipper.bin` |
| `extruder_mcu_update_fw.sh` | toolhead (UUID `61755fe321ac`) | `~/printer_data/build/extruder_mcu_klipper.bin` |
| `extra_mcu_update_fw.sh` | chamber (UUID `58a72bb93aa4`) | `~/printer_data/build/extra_mcu_klipper.bin` |

`flash_can.py` (26 KB) is Eric Callahan's Katapult uploader.

The blobs the scripts expect are **not present** in
`~/printer_data/build/` on the audited Max. The candidate main-MCU
blob is at `/root/klipper.bin` (28.9 KB, sized like an STM32H750
application) — but the Sovol-shipped scripts won't find it without
an explicit path override. The toolhead and chamber blobs are
absent entirely. Reflashing the Max's MCUs requires either
sourcing them from another unit or rebuilding from Sovol's klipper
fork (the build configs under `~/klipper/.config*` are for the
USB-CAN bridge chip, not the downstream Klipper MCUs — those build
configs are not on disk).

The flash scripts are exposed as Klipper macros via
`get_ip.cfg` `[gcode_shell_command]` entries: `_MCU_UP`,
`_EXTRUDER_MCU_UP`, `_EXTRA_MCU_UP`.

### `/boot/scripts/` — boot orchestrator

| Script | Active on Max | Purpose |
|--------|---------------|---------|
| `btt_init.sh` | yes (called from `/etc/rc.local`) | Top-level. chowns home dir, sweeps `/boot/gcode/`, backgrounds the daemons. |
| `system_cfg.sh` | yes | Applies `/boot/system.cfg` (timezone, hostname, KS rotation, BTT_PAD7, sound/vibration). |
| `connect_wifi.sh` | yes | Reads `WIFI_SSID/WIFI_PASSWD` from `/boot/system.cfg`. The `connectUSBWifi()` function is defined but the call to it is **commented out** on the Max. |
| `file_change_save.sh` | yes | inotify watch on `~/printer_data/config`, calls `sync` on every write. Duplicate work; logs noise to `/home/mount.log`. |
| `ota_service.sh` | **no** (launch commented out in `btt_init.sh`) | Comgrow OTA daemon (`https://www.comgrow.com/files/printer/ver.json`, MD5-only). Script present but inert. |
| `auto_setmcu_id.sh` | no (commented out) | Would set MCU UUID at boot — superseded by hardcoded UUIDs in printer.cfg. |
| `extend_fs.sh` | no (commented out) | One-shot rootfs expansion (already done). |
| `sync.sh` | no (commented out) | Periodic sync loop. |
| `auto_brightness` (binary) | gated on `BTT_PAD7=ON` | Touchscreen brightness controller for HDMI displays. |
| `set_rgb` (binary) | gated on `BTT_PAD7=ON` | RGB indicator LED on the screen module. |
| `sound.sh`, `vibration.sh`, `vibrationsound.sh` | gated on `TOUCH_SOUND/VIBRATION=ON` | Touch feedback hooks via `/sys/class/gpio/gpio79`. |

### `/usr/local/bin/wifi_server.py` — LAN-exposed root command server

A 200-line Flask app, owned by sovol but launched as **root** via
`wifi_server.service`. Listens on **0.0.0.0:5000** with no
authentication. Endpoints:

- `GET /scan_wifi` — `nmcli -t -f SSID,SIGNAL,SECURITY device wifi list`
- `POST /connect_wifi` — `subprocess.getoutput(f"nmcli device wifi connect '{ssid}' password '{password}'")` (SSID/password command injection)
- `POST /disconnect_wifi`
- `GET /networkInterface`, `GET /interfaceStatus`, `GET /activeConnections`, `GET /linkStatus`, `GET /get_ip`, `GET /ping`
- **`POST /command`** — `subprocess.run(cmd, shell=True, …)` after a `startswith` check against `nmcli`/`ip`/`iw`/`ifconfig`/`ping`/`iwconfig`. Trivially escapable: `cmd="ip ; rm -rf /"` passes the prefix test.

**Anyone on the LAN gets unauthenticated root.** Used by an older
Sovol mobile app for wifi setup; the current touchscreen does wifi
setup via NetworkManager directly. **Disabling the service breaks
nothing user-facing.** This is the load-bearing security finding
on the SV08 Max — has to be the first thing `flows.stock_keep`
addresses.

### `~/plr.sh` — power-loss recovery

Synthesizes a resume gcode under `~/printer_data/gcodes/plr/`
when the printer recovers from an unexpected power-loss:

1. Reads `~/printer_data/config/saved_variables.cfg` for the
   in-progress filepath, last_file, and `power_resume_z`.
2. Reads `~/sovol_plr_height` (JSON) for the last-known toolhead
   `Z` and `commandline`.
3. Strips thumbnails and DOS line endings from the source gcode,
   normalizes Z values.
4. Synthesizes a header that warms the bed, lifts Z, homes XY,
   re-extrudes a small amount, then jumps to the resume point.
5. Hands off to Klipper's `[virtual_sdcard]` for playback.

Wired into Klipper as `[gcode_shell_command POWER_LOSS_RESUME]`
in `plr.cfg`. Triggered by the touchscreen's "resume after power
loss" flow.

### `~/factory_resets.sh` — reset to factory configs

```bash
#!/bin/bash
cp -p /home/sovol/patch/config/*.cfg /home/sovol/printer_data/config/
python3 /home/sovol/pyhelper/restart_firmware.py
```

Wired into Klipper as `[gcode_macro FACTORY_RESETS]` in `Macro.cfg`.
Triggered from the touchscreen settings menu.

`/home/sovol/patch/config/` is **empty** on the audited unit, so
the factory-reset macro is a no-op as currently configured. Sovol
may populate this dir in a later firmware revision; right now it's
a load-bearing-by-name path that doesn't actually do anything.

## Phone-home and cloud surface

| Source | Destination | Active | Notes |
|--------|-------------|--------|-------|
| `moonraker-obico.service` | `app.obico.io` (GCP) | **Always** | Default-on, dials continuously even with no API key configured. |
| `ota_service.sh` | `www.comgrow.com/files/printer/ver.json` | No | Daemon not started at boot on Max. |
| `klipper.git` origin | `http://192.168.1.233/root/klipper.git` | Never | Sovol internal LAN; not reachable post-ship. |
| `zhongchuang.git` origin | `http://192.168.1.233/root/zhongchuang.git` | Never | Same — Sovol internal LAN. |
| Aliyun / Tencent / Gitee / HDL | — | Not present | Major divergence from the Phrozen Arco. |

`iptables` and `ip6tables` are empty; no firewall.

## Comparison anchors

The SV08 Max is closest to the **Sovol Zero** in stack — both
share the SPI-XI base image and the deterministic CAN UUIDs.
Differences are documented in `ALIGNMENT-WITH-ZERO.md`.

The SV08 Max is closer to the **Phrozen Arco** in product class
(both are large-format CoreXY printers running Klipper on an SBC
with serial-TFT touchscreens) but differs sharply at the network
layer: Sovol ships only one default phone-home (Obico), no
proprietary reverse tunnels, no aliyun NTP, no HDL Zigbee gateway.
The screen-daemon situation is also different — Phrozen ships a
closed-binary `voronFDM`, Sovol ships open C++ source with a
closed `.tft` panel firmware blob.
