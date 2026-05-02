# Stock Sovol Zero — Full Inventory

Complete inventory of everything Sovol ships on a stock Sovol Zero
that our replacement process needs to be aware of. Derived from a **live
audit over SSH** (sovol@192.168.0.140, ed25519 audit key, read-only with
one harmless `sudo cat` on `/etc/NetworkManager/system-connections/*`).
Audit date: 2026-05-01. Raw probe dumps and the runner script live
out-of-repo at `installer/.audits/sovol-zero-20260501/`
(`audit-raw.txt`, `audit-followup.txt`, `audit-followup-2.txt`,
`audit-sovol-zero.sh`) — they contain factory wifi PSKs and all three
pre-shared SSH host-key fingerprints in plaintext, so they're kept off
the published deckhand-builds repo.

> **Note on this unit:** the surveyed printer has had a Deckhand audit
> SSH key appended to `~/.ssh/authorized_keys` (see the `deckhand-audit-20260501`
> comment). Nothing else has been modified. Everything else in this
> document is factory Sovol.

> **Klipper "1.3.7" vs OTA "1.4.7":** two different version trains.
> Klipper's git-tag commit message reads `1.3.7版本` (= "version 1.3.7"),
> while the OTA log shows the unit at OTA package version 1.4.7. The
> first is the firmware-side version Sovol stamps on klipper builds; the
> second is the OS-image OTA version delivered through Comgrow's
> `ver.json` endpoint (see § OTA / phone-home).

## Identity

- **Hostname**: `SPI-XI` (also the OS image's "PRETTY_NAME" — `SPI-XI 2.3.3 Bullseye`)
- **Distro**: Debian 11 (Bullseye), Sovol-rebadged. **Not** Armbian as a top-level distro (`/etc/armbian-release` is missing) but the systemd unit list contains many `armbian-*` services and `/etc/update-motd.d/30-system-sysinfo` is the standard Armbian script — the image is Armbian-derived with the Armbian release file stripped and Sovol branding swapped in.
- **Kernel**: `5.16.17-sun50iw9 #2.3.3 SMP Tue Oct 29 18:49:57 CST 2024` — built on a Chinese-locale build host, dated Oct 2024. `sun50iw9` denotes the Allwinner H6/H616 family.
- **Architecture**: `aarch64`
- **SBC**: device-tree model is `BigTreeTech CB1`, device-tree compatible string `allwinner,sun50i-h616`. So this is a BigTreeTech CB1 (Allwinner H616, 4× Cortex-A53, 1 GB) — Sovol uses BTT's CB1 module rather than custom SBC silicon.
- **Stock board** (per `moonraker-obico.cfg` `[meta]` section): `H616_JC_3Z_5160_V1.2`. Sovol-internal designation; the `5160` aligns with the TMC5160 X/Y drivers and `3Z` likely refers to three Z-axis screws.
- **eMMC**: `mmcblk2`, 7.81 GB (`7818182656` bytes), MBR (msdos) partition table.
  - `mmcblk2p1` — 256 MB FAT16 `/boot` (`LABEL=BOOT`, UUID `4F43-9E00`)
  - `mmcblk2p2` — 7.38 GB ext4 `/` (UUID `a161f893-e56e-4833-89bd-91d3a36e9904`)
  - `mmcblk2boot0`, `mmcblk2boot1` — 4 MB eMMC boot partitions (unused by Linux)
  - `zram0` (517 MB swap) and `zram1` (52 MB ext2 log2ram)
- **Time / NTP**: `ntpd` (classic NTP daemon), pool unconfigured beyond defaults. **No `chrony`. No aliyun NTP override.**
- **Timezone**: `Etc/UTC` (default). `/boot/system.cfg` exposes `TimeZone="Asia/Shanghai"` as a commented-out override; if a user edits the boot file to uncomment, `system_cfg.sh` will switch.

### eMMC layout summary

| Mount | Device | Size | FS | Notes |
|-------|--------|------|----|-------|
| `/boot` | `mmcblk2p1` | 256 MB | vfat | Holds `/boot/scripts/`, `/boot/system.cfg`, `/boot/gcode/` (USB-injected gcode pickup). User-editable from a card reader. |
| `/` | `mmcblk2p2` | 7.38 GB | ext4 | 67% used at audit time. |

Boot mode is **MBR / msdos** (not GPT) — same partition-table style as the Arco's MKS-Pi.

## Boot sequence on stock

There are two parallel boot tracks:

### 1. `/etc/rc.local` → `/boot/scripts/btt_init.sh` (vendor track)

`/etc/rc.local` runs:

```
chmod +x /boot/scripts/*
/boot/scripts/btt_init.sh
```

`btt_init.sh` is short — it chowns `/home/sovol/` recursively to `sovol:sovol`, copies any `*.gcode` from `/boot/gcode/` into `~/printer_data/gcodes` (a "drop a gcode on the boot partition over USB" feature), then backgrounds the four vendor daemons:

1. `./system_cfg.sh &` — applies user-overridable settings from `/boot/system.cfg` (timezone, hostname, KlipperScreen rotation, BTT_PAD7, touch vibration/sound toggles, `WIFI_SSID`/`WIFI_PASSWD`).
2. `./connect_wifi.sh &` — sources `/boot/system.cfg` for `WIFI_SSID/WIFI_PASSWD` and connects via `nmcli`. Has a `connectUSBWifi()` fallback that reads `/home/sovol/printer_data/gcodes/USB/wifi.cfg` from a connected USB stick — **physical-access wifi takeover vector** (similar to the Arco's `makerbase-net-mods.service`, but USB-stick driven instead of wpa_supplicant copy).
3. `./file_change_save.sh &` — runs `inotifywait -m -e close_write` on `/home/sovol/printer_data/config` and calls `sync` on each change. Logs to `/home/mount.log` (path looks like a typo for `/home/sovol/mount.log`).
4. `sudo -u sovol ./ota_service.sh &` — see § OTA below.

The four `&` lines never wait, so all four daemons run for the lifetime of the printer.

`auto_setmcu_id.sh`, `extend_fs.sh`, and `sync.sh` are present in `/boot/scripts/` but **commented out** in `btt_init.sh`. `auto_setmcu_id.sh` is no longer needed because Sovol now hardcodes CAN UUIDs in `printer.cfg` rather than discovering them at boot.

### 2. systemd-enabled units (standard track)

`systemctl list-unit-files --state=enabled` returns 36 enabled units. The non-default ones (i.e. anything beyond stock Armbian/Debian) are:

- `klipper.service` — runs `/home/sovol/klippy-env/bin/python /home/sovol/klipper/klippy/klippy.py …` as `sovol`. Description string is `Klipper 3D Printer Firmware SV1` — Sovol's internal model code for this printer is **SV1** (the firmware unit description), even though the user-facing model is "Sovol Zero".
- `KlipperScreen.service` — runs the upstream `KlipperScreen-start.sh` (which is **NOT** customized — it just `xinit`s `screen.py`; major divergence from Arco). Currently in `auto-restart` because Xorg is exiting; possibly the touchscreen driver path during early boot.
- `moonraker.service` — runs `/home/sovol/moonraker-env/bin/python … moonraker.py`. Service description: `API Server for Klipper SV1`.
- `moonraker-obico.service` — runs the standard Obico bridge. **Enabled and running by default**, unlike on the Arco where it's enabled but the boot script deletes the venv each cycle. The shipped `moonraker-obico.cfg` has no API key wired in — the user has to register on first launch — but the bridge dials `app.obico.io` (Google Cloud, observed at runtime) regardless.
- `crowsnest.service` — webcam stream (ustreamer on `127.0.0.1:8080`, single camera at `/dev/video0`, 720×540 @ 15 fps).
- `nginx.service` — serves Mainsail on port 80. Mainsail-only — no Fluidd installed.
- `wifi_server.service` — see § Vendor binaries.
- `hostapd.service` — present and `enabled`, but in `auto-restart` (no AP config exists). Looks vestigial from the BTT CB1 base image.
- `bluetooth.service` — enabled but inactive (no Bluetooth adapter in use).
- `hdmi-audio.service` — Sovol/Allwinner specific oneshot.
- `ssh.service` — OpenSSH 7.x (Debian-Bullseye build).
- `ntp.service` — classic ntpd.
- `NetworkManager.service` + `wpa_supplicant.service` + `networking.service` — net stack (NM-managed, with `/etc/network/interfaces.d/can0` for the CAN interface).
- `armbian-hardware-monitor`, `armbian-hardware-optimize`, `armbian-zram-config`, `bootsplash-hide-when-booted`, `fake-hwclock`, `e2scrub_reap`, `resolvconf*`, `rsync.service`, `systemd-pstore` — Armbian/Debian standard.

Notably **missing** (vs the Arco): `frpc`, `phrozen_master`, `voronFDM`, `mksclient`, `makerbase-client.service`, `makerbase-udp.service`, `makerbase-net-mods.service`, `makerbase-byid.service`, `makerbase-shutdown.service`, `makerbase-auto-fresh.service`, `openvpn.service`, `chrony*`. The `makerbase-automount@.service` template *is* still installed (the usbmount source is at `/home/sovol/usbmount/` and was `make install`-ed during factory build per `/home/sovol/.bash_history`), but no USB device is currently triggering it.

### Multi-user.target wants

Same set as the enabled list above, all symlinked into `/etc/systemd/system/multi-user.target.wants/`. Nothing custom under `default.target.wants`, `basic.target.wants`, or `network-online.target.wants`.

## Vendor binaries and scripts

### `/boot/scripts/` (BigTreeTech CB1 base image scripts, retained by Sovol)

Both Sovol and BigTreeTech started from the same CB1 image base; the script names match BTT's reference image but the contents have been reworked for Sovol's flow.

| Path | Role | Keep strategy |
|------|------|---------------|
| `/boot/scripts/btt_init.sh` | Boot orchestrator (called from `/etc/rc.local`). | Replace with a Deckhand-rewritten version on `stock_keep` (drop the four `&` daemons we don't want, keep the `/boot/gcode/` sweep and the `chown`). |
| `/boot/scripts/connect_wifi.sh` | Wifi connect helper (reads `/boot/system.cfg`, has `connectUSBWifi()` fallback that reads `/home/sovol/printer_data/gcodes/USB/wifi.cfg`). | Stop launching from `btt_init.sh` after first wifi. The `connectUSBWifi()` USB-stick branch is a physical-access wifi takeover vector. |
| `/boot/scripts/file_change_save.sh` | inotify watcher on `~/printer_data/config`, calls `sync` on writes. Logs to `/home/mount.log`. | Drop. Klipper/Moonraker handle config persistence; this is duplicate. |
| `/boot/scripts/ota_service.sh` | OTA daemon (see § OTA). | Drop on `stock_keep`; user can re-add if they want Sovol's update channel. |
| `/boot/scripts/system_cfg.sh` | Applies `/boot/system.cfg` (timezone, hostname, KS rotation, sound/vibration toggles). | Keep — useful first-run config knobs from the boot partition. |
| `/boot/scripts/auto_setmcu_id.sh` | Would set MCU UUID at boot. | Already disabled by Sovol (commented out of btt_init.sh) — printer.cfg has hardcoded `canbus_uuid`s now. Safe to delete. |
| `/boot/scripts/extend_fs.sh` | One-shot rootfs expansion. | Already disabled. |
| `/boot/scripts/sync.sh` | Periodic `sync` loop. | Already disabled. |
| `/boot/scripts/auto_brightness` (binary, 14 KB) | Touchscreen brightness controller. | Keep if user keeps stock screen; remove on full replacement. |
| `/boot/scripts/set_rgb` (binary, 9.6 KB) | RGB indicator LED on the screen module. | Same — bound to vendor screen UI. |
| `/boot/scripts/sound.sh`, `vibration.sh`, `vibrationsound.sh` | Touch feedback hooks. | Same. |
| `/boot/scripts/mp3/` | Sound files. | Same. |
| `/boot/scripts/wifi.log` | Append-only log written by `connect_wifi.sh`. | Cleanup tier. |

### `/usr/local/bin/`

| Path | Role | Notes |
|------|------|-------|
| `/usr/local/bin/wifi_server.py` (sovol:sovol, world-readable) | Flask app. **Loaded by `/etc/systemd/system/wifi_server.service` and runs as ROOT on `0.0.0.0:5000` with NO authentication.** | **CRITICAL security finding.** Exposes `/scan_wifi`, `/connect_wifi`, `/disconnect_wifi`, `/networkInterface`, `/interfaceStatus`, `/activeConnections`, `/linkStatus`, `/get_ip`, `/ping`, and **`/command`**. The `/command` endpoint runs `subprocess.run(cmd, shell=True, …)` after a weak prefix check (`nmcli`, `ip`, `iw`, `ifconfig`, `ping`, `iwconfig`). Trivially escapable: `cmd="ip ; rm -rf /"` passes the `startswith` test. Also, `/connect_wifi` does `cmd = f"nmcli device wifi connect '{ssid}' password '{password}'"` then `subprocess.getoutput(cmd)` — SSID/password command injection. **Any device on the LAN can run shell commands as root.** |
| `/usr/local/bin/flask` | 208-byte Python entrypoint script (Flask CLI). | Standard. |
| `/usr/local/bin/watchdog_test` | 13.8 KB binary. | Not invoked at boot; provenance unclear. Cleanup tier. |
| `/usr/local/bin/crowsnest` (symlink → `/home/sovol/crowsnest/crowsnest`) | Standard Crowsnest entrypoint. | Keep. |

### `/home/sovol/` vendor scripts

| Path | Role | Notes |
|------|------|-------|
| `~/ota_client.sh` (mode 0777) | Sends `SIGUSR1` to `/boot/scripts/ota_service.sh` — manual OTA-trigger. | Wired into Klipper macros via `~/printer_data/config/get_ip.cfg` `[gcode_macro _OTA]` so the touchscreen can request an OTA. |
| `~/factory_resets.sh` | `cp -p /home/sovol/patch/config/*.cfg ~/printer_data/config/; firmware_restart`. | Wired into Klipper macro `FACTORY_RESETS`. **Factory-reset destination is `/home/sovol/patch/config/` — currently empty on this unit; Sovol may populate it in a later OTA, or the fact that it's empty indicates this code path was never finished.** Keep behavior on `stock_keep`. |
| `~/get_ip.sh` | Calls `python3 ~/pyhelper/send_ip.py` which posts an `M117 <IP>` to Moonraker. | Wired into `_GET_IP` macro / `[menu __reset __showip]`. Harmless. |
| `~/clear_plr.sh`, `~/plr.sh`, `~/sovol_plr_height` | Power-loss-recovery scripts. Wired into `plr.cfg`. | Keep. |
| `~/ttyS3.py` | 366 B. Opens `/dev/ttyS3` at 9600 baud, writes `Hello!`, reads, closes. | A leftover developer probe. `/dev/ttyS3` is not used at runtime by anything else. Cleanup tier. |
| `~/ota.log` | OTA version-check log. | Cleanup tier (status info, not load-bearing). |
| `~/pyhelper/send_ip.py` | Posts current IP as `M117` via Moonraker REST. | Keep. |
| `~/pyhelper/restart_firmware.py` | Posts `firmware_restart` via Moonraker. | Keep. |
| `~/pyhelper/ota_process.py` | Posts `M117 <progress>` during OTA download. | Keep. |
| `~/patch/patch.sh` | Build-time overlay: `cp menu.py menu.cfg display.cfg ~/klipper/klippy/extras/display/` and `cp config/*.cfg ~/printer_data/config/`. | Already applied at factory; the modified files now live in the running klipper tree. The `patch.sh` script itself is not invoked at runtime. Document as factory-build artifact. |
| `~/patch/menu.py` (39.7 KB), `~/patch/menu.cfg` (18.6 KB), `~/patch/display.cfg` (9.8 KB) | Sovol's overlay of `klippy/extras/display/menu.py` etc. | These define the Klipper-extras-side menu (the one rendered on the small UC1701 LCD if connected — see § Display). Already overlaid onto klippy. Cleanup-tier on disk if user is on KlipperScreen. |
| `~/patch/config/` | Empty directory. | Where `factory_resets.sh` expects the canonical configs to live. Currently empty — factory-reset is a no-op on this unit. |
| `~/usbmount/` | Sources for `makerbase-automount@.service`. Already `make install`-ed at factory time per bash_history. | Cleanup tier. |
| `~/offline_lib/flask/` | Pre-bundled Flask 3.1.0 + dependencies as `.whl` files (used to install `wifi_server.py`'s deps offline at factory time). | Cleanup tier. |

### `~/printer_data/build/` (firmware-flash tooling, used by touchscreen flow)

| Path | Role |
|------|------|
| `flash_can.py` (26 KB) | Katapult/CanBoot CAN flasher. |
| `mcu_klipper.bin` | Main MCU firmware blob. **Not present** on this unit (only the flash script). |
| `extruder_mcu_klipper.bin` (31 KB) | Extruder MCU firmware. Present. |
| `extra_mcu_klipper.bin` | Hot/chamber MCU firmware. **Not present** on this unit. |
| `mcu_update_fw.sh` | Flashes main MCU at CAN UUID `0d1445047cdd` (or via katapult USB at `usb-katapult_stm32h750xx`). |
| `extruder_mcu_update_fw.sh` | Flashes extruder MCU at CAN UUID `61755fe321ac`. |
| `extra_mcu_update_fw.sh` | Flashes chamber MCU at CAN UUID `58a72bb93aa4`. |

`get_ip.cfg` registers `[gcode_shell_command]` entries for each of the three MCU updaters and exposes them as `_MCU_UP`, `_EXTRUDER_MCU_UP`, `_EXTRA_MCU_UP` macros — so the user can trigger MCU reflashes from the web UI / touchscreen.

### `/root/`

Essentially empty: only `.bashrc`, `.bash_history`, `.profile`, `.cache/`, `.viminfo`. **No `/root/.ssh/` directory, no SSH backdoor keys, no vendor binaries under `/root/`.** Massive contrast with the Arco where `/root/phrozen/` carried a full C++ project tree (mksclient sources + binary).

`/root/.bash_history` shows the factory build process — `cd /home/sovol/zhongchuangv0.12.0/`, `cmake ..`, `pip install -v "numpy<1.26"`, `make uninstall` of crowsnest, etc. The directory `zhongchuangv0.12.0/` no longer exists on disk; it was cleaned up before shipping. "Zhongchuang" (中创) is the contract-manufacturer brand visible elsewhere in the network-config PSKs (`ZCSW$888`).

## OTA / phone-home

The OTA daemon at `/boot/scripts/ota_service.sh` runs as user `sovol` (root spawns it via `sudo -u sovol`). It:

1. Reads `/home/sovol/klipper/klippy/extras/display/menu.cfg`, parses `[menu __main __info __version]` and pulls the `name:` field as the local version.
2. Curls `https://www.comgrow.com/files/printer/ver.json` for `versionCode` + `firmwareMD5` + `path`.
3. Loops `sleep 1` indefinitely, waiting for `SIGUSR1` (sent by `~/ota_client.sh`).
4. On signal: if local `name` ≠ remote `versionCode`, downloads the `path`, verifies MD5 (no GPG / signature, just MD5), runs `sudo dpkg -i --force-overwrite <file>`, then `reboot`.

| Host / endpoint | Direction | Active | Notes |
|-----------------|-----------|--------|-------|
| `https://www.comgrow.com/files/printer/ver.json` | OTA → outbound HTTPS | On user trigger (touchscreen `_OTA` macro). | Comgrow is Sovol's primary EU/US reseller — the OTA is hosted on the partner's website, not on a Sovol-owned cloud. |
| `https://app.obico.io` | Obico → outbound HTTPS | **Always** while `moonraker-obico.service` is up. Resolves to Google Cloud (34.95.90.112 observed). | Stock config has no API key — Obico won't actually function until the user registers — but the long-poll heartbeat still hits Obico's servers continuously. Disable the service to stop. |

There is **no `frpc` reverse tunnel**, no Aliyun NTP, no Tencent / Gitee endpoints, no HDL Zigbee gateway. The Sovol-vs-Phrozen difference here is significant: the Sovol Zero has only **one always-on phone-home (Obico)**, vs the Arco's stack of frpc + HDL + aliyun-ntp + dormant gitee.

`ota.log` history on this unit: `1.3.7` → `1.4.2` → `1.4.7` (current). Versions 1.4.x are OS-image releases, distinct from the `1.3.7版本` git-tag stamp in klipper's commit log.

## Vendor klipper extras

Klipper repo at `/home/sovol/klipper/`:

- **Tracked URL**: `http://192.168.1.233/root/klipper.git` — Sovol's internal Gitea (private LAN address, plain HTTP). Won't reach anything once shipped. The git remote is decorative — the printer's klipper never updates from this URL post-ship.
- **HEAD**: `cc8afd89abb4f137a51220ebda4844f1c8145f89` ("`1.3.7版本`", 2025-01-20), branch `main`.
- **Base**: derived from upstream Klipper 0.12.0.
- **MCU firmware build stamps** (from `klippy.log`): main MCU is `14d7b18-dirty-20250210_015142-SPI-XI` (STM32H750xx, 400 MHz, with `CANBUS_BRIDGE=1`); extruder_mcu is `cc8afd8-dirty-20250310_015728-SPI-XI` (STM32F103xe); hot_mcu is `cc8afd8-dirty-20250310_015837-SPI-XI` (STM32F103xe). All three were built on a host named `SPI-XI` (Sovol's build machine, also the same name as the SBC).

### `klippy/extras/` Sovol modifications

Files modified after Sovol's base import (Nov 8 2024):

| File | Date | Notes |
|------|------|-------|
| `bed_mesh.py` | 2025-05-08 | 77 KB — heavily extended for `rapid_scan` + eddy-current `BED_MESH_CALIBRATE`. |
| `fan.py` | 2025-05-08 | |
| `heater_fan.py` | 2025-04-29 | |
| `homing.py` | 2025-03-10 | |
| `ldc1612.py` | 2025-03-10 | LDC1612 driver for the eddy-current Z probe. |
| `lis2dw.py` | 2024-12-17 | LIS2DW accelerometer (replaces the more common ADXL345). |
| `probe.py` | 2025-03-10 | |
| `probe_eddy_current.py` | 2025-05-08 | Eddy-current Z probe. Modified beyond upstream (Sovol-added `vir_contact_speed`, `TYPE_VIR_TOUCH`). |
| `probe_pressure.py` | 2025-03-10 | **Not in upstream Klipper** — Sovol-original (header still credits Kevin O'Connor 2017–2021, suggesting it started as a derivative of `probe.py`). |
| `shaper_calibrate.py` | 2025-03-28 | |
| `z_offset_calibration.py` | 2025-03-29 | **Sovol-original** — header explicitly says `Copyright (C) 2024-2025 Sovol3d <info@sovol3d.com>`. Implements the `Z_OFFSET_CALIBRATION` g-code used in `START_PRINT`. Depends on `probe`, `probe_eddy_current`, `manual_probe`. |
| `display/menu.py`, `display/menu.cfg`, `display/display.cfg` | (varies) | Sovol's menu overlay — 39.7 KB / 18.6 KB / 9.8 KB. Replaces upstream menu definitions. |

### `/home/sovol/klipper/config/`

Holds Sovol example printer.cfgs for the older product line: `printer-sovol-sv01-2020.cfg`, `printer-sovol-sv05-2022.cfg`, `printer-sovol-sv06-2022.cfg`, `printer-sovol-sv06-plus-2023.cfg`. **No `printer-sovol-zero.cfg`** — the Zero hasn't been upstreamed into Sovol's klipper config dir. The actual stock printer.cfg lives in `~/printer_data/config/printer.cfg` only.

## Stock printer.cfg (live, runtime)

Single `~/printer_data/config/printer.cfg` (~14 KB), with includes for `mainsail.cfg`, `timelapse.cfg`, `get_ip.cfg`, `Macro.cfg`, `plr.cfg`, `moonraker_obico_macros.cfg`, `chamber_hot.cfg`. Highlights:

- **Kinematics**: `corexy`. **Build volume from position_max / mesh_max**: X 155 / Y 152.5 / Z 155 mm; usable bed mesh region is `12,12 → 132,140` (~120 × 128 mm). **Small printer**, consistent with the "Sovol Zero" product description.
- **Three MCUs, all on CAN bus** (1 Mbps):
  - `[mcu]` (main) — `canbus_uuid: 0d1445047cdd` — STM32H750xx with `CANBUS_BRIDGE=1` (so the H750 bridges USB host ↔ CAN bus). 400 MHz.
  - `[mcu extruder_mcu]` — `canbus_uuid: 61755fe321ac` — STM32F103xe @ 72 MHz. Carries the extruder stepper, hotend heater, hotend NTC, hotend fan, part fan, LDC1612 i2c, LIS2DW SPI.
  - `[mcu hot_mcu]` (in `chamber_hot.cfg`) — `canbus_uuid: 58a72bb93aa4` — STM32F103xe @ 72 MHz. Carries the chamber heater, chamber outlet temp NTC, chamber-fan tachometer, hot_led indicator.
- **CAN bus dongle**: `lsusb` shows `1d50:606f OpenMoko, Inc. Geschwister Schneider CAN adapter` — gs_usb / canable. The H750 main MCU exposes itself as gs_usb, providing the host-side `can0` interface.
- **`/dev/serial/by-id/` is empty** at runtime — there's no USB-serial Klipper MCU, only the gs_usb CAN bus. The Arco-style "match by serial path" will not find anything here.
- **Steppers**:
  - X, Y: TMC5160 SPI (`run_current: 3.5`, `sense_resistor: 0.05`)
  - Z: TMC2209 UART (`run_current: 1.5`, `sense_resistor: 0.150`)
  - Extruder: TMC2209 UART (`run_current: 0.8`, `sense_resistor: 0.150`)
- **Probe**: `probe_eddy_current eddy` using `ldc1612` on `extruder_mcu i2c2` (PB10/PB11). `z_offset: 3.5`, `x_offset: -19.8`, `y_offset: -0.75`. Bed mesh is `20×20`, `algorithm: bicubic`, calibrated and present in SAVE_CONFIG.
- **Accelerometer**: `lis2dw` on `extruder_mcu` SPI (PB12-15), `axes_map: x,z,y`. Used for `resonance_tester` at probe point `76,76,30`.
- **Heaters**: hotend `max_temp: 355` with custom thermistor table (`my_thermistor_e`); bed `max_temp: 125` with `my_thermistor` table; chamber heater (in `chamber_hot.cfg`) `max_temp: 70` watermark control.
- **Fans**: `fan0` (part), `fan2` (auxiliary), `fan3`, `temperature_fan exhaust_fan` (PB0 + tach PB1), `heater_fan hotend_fan` (extruder_mcu PA6).
- **Display**: A `[display] lcd_type: uc1701` block defines a small monochrome SPI LCD on EXP1/EXP2 headers with rotary encoder + click. **Whether this LCD is physically populated on the production unit is unclear from the audit alone** — Klipper accepts the section as long as the pins resolve, but the runtime presence isn't confirmable from config alone. The customer-facing UI is the touchscreen running KlipperScreen on `/dev/tty7` via xinit + Xorg.
- **Filament sensor**: `filament_switch_sensor filament_sensor` on PB2 (microswitch).
- **Power-loss recovery**: via `plr.cfg` — `[gcode_shell_command POWER_LOSS_RESUME]` runs `~/plr.sh`.

## Display / screen daemon

**KlipperScreen** is the only screen daemon on this unit. Critically different from the Arco:

- KlipperScreen launches under `xinit` on `/dev/tty7` via the **stock upstream `KlipperScreen-start.sh`**. Sovol did **not** modify the start script. There is no vendor TJC daemon (no `voronFDM`, no `mksclient`, no `serial-screen/*`).
- The status line of KlipperScreen.service is `activating auto-restart` because Xorg exits ("[Xorg] <defunct>") shortly after start — likely fixable by getting on the screen and waiting it out, or possibly always-restarting normal behavior; not investigated further in this pass.
- The `[display] lcd_type: uc1701` block in printer.cfg suggests a small monochrome rotary-encoder LCD wired to the EXP1/EXP2 headers, which Klipper would drive directly via its `klippy/extras/display/` menu system (this is what the `~/patch/menu.py` overlay configures). Production units may or may not have this LCD physically populated; cannot tell from this audit.

Replacement strategy options:

| Option | Notes |
|--------|-------|
| Keep KlipperScreen | Default. The stock start script is already clean upstream code. |
| Replace with arco_screen | Possible but requires the same display hardware research the Arco needed; not a priority. |
| Disable both | Headless operation via Mainsail only. |

## Network indicators

| Host / IP | Who reaches it | Port | Active? | Notes |
|-----------|----------------|------|---------|-------|
| `app.obico.io` (e.g. 34.95.90.112) | `moonraker-obico` | 443 | **Yes — always** (heartbeat even when not registered) | Disable `moonraker-obico.service` to stop. |
| `www.comgrow.com/files/printer/ver.json` | `ota_service.sh` | 443 | On user trigger only (SIGUSR1) | OTA channel hosted by Comgrow, Sovol's reseller. MD5-only integrity. |
| `192.168.1.233/root/klipper.git` | git origin (decorative) | 80 | Never — internal Sovol LAN, not reachable post-ship | |
| Aliyun / Tencent / Gitee / HDL endpoints | — | — | Not present | Major divergence from Arco. |

`iptables -L` and `ip6tables -L` are both empty (default ACCEPT all chains). `/etc/cron.d/`, `/etc/cron.daily/`, `/etc/crontab`, and per-user crontabs are stock Armbian/Debian (armbian-truncate-logs, armbian-updates, e2scrub_all, apt-compat, fake-hwclock) — **no Sovol cron entries**.

### Listening sockets (LAN-reachable)

| Port | Process | Auth | Severity |
|------|---------|------|----------|
| 22 | sshd | publickey/password | OK (PermitRootLogin no, factory user `sovol`/`sovol` is published). |
| 80 | nginx (mainsail) | none | Standard. |
| 5000 | `wifi_server.py` (root) | **none** | **CRITICAL** — see § Vendor binaries / `/usr/local/bin/wifi_server.py`. |
| 7125 | moonraker | trusted_clients (192.168/10/172.16/127/169.254) | Standard. |
| 46793 (ephemeral) | moonraker socket | n/a | Outbound-only. |

`avahi-daemon` advertises mDNS as `SPI-XI-2.local`. UDP listeners are avahi (5353) and ntpd (123). No vendor UDP services (no `udp_server`-equivalent).

## Users, auth, SSH host keys

- `/etc/passwd`: `root` (bash, /root), `sovol` (uid 1000, /home/sovol, bash). Plus standard service accounts. **No additional vendor accounts.**
- **`sovol` has passwordless sudo via a line appended directly to `/etc/sudoers`** (`%sovol ALL=(ALL) NOPASSWD: ALL`), bypassing `/etc/sudoers.d/`. Stock convention violation but functionally fine.
- **Default password**: `sovol:sovol` — published in this repo. The repo's wizard should force a change on first run.
- `/etc/sudoers.d/`: only `README` (Debian-shipped, not readable by sovol).
- `/etc/group`: contains a `moonraker-admin` group (gid 1001, member: sovol) and an empty `klipperscreen` group (gid 1002). Created by kiauh during factory build (visible in `~/.bash_history`).
- `/root/.ssh/`: does not exist — no root-level SSH keys.
- `~/.ssh/authorized_keys`: only the audit key we appended for this audit.

### Pre-shared SSH host key (security finding)

The Sovol Zero ships with a **factory-baked SSH host key** that survives imaging — every Sovol Zero on the same software release shares the same host fingerprint. Concrete evidence:

- The host key is `SHA256:r29wTDuG7tzLvsyF4P06NSatzmc6dKh3dHWw3uGXs5w` (ed25519). Comment in the public key file: `root@chris-virtual-machine`.
- `~/known_hosts` on the auditor's workstation already had this same fingerprint from `192.168.0.121`, `192.168.0.115`, `192.168.0.156` — i.e. four different printers on the same LAN, all the same key.
- Implication: a MITM that obtains the private key (e.g. by extracting it from another printer of the same SKU) can transparently impersonate every shipped Sovol Zero.

The mitigation is one of: regenerate host keys on first boot via `dpkg-reconfigure openssh-server` (the standard Debian fix); or have the wizard regenerate before any user interaction. A `flows.stock_keep` step that runs `sudo /usr/sbin/dpkg-reconfigure openssh-server` early (before the user has cached the host fingerprint) is the right move.

## Network credentials on disk

`/etc/NetworkManager/system-connections/` contains three NM profiles, each readable only by root but with **plaintext PSKs**. These are **factory-test wifi credentials baked into every shipped unit**:

| SSID | PSK | Notes |
|------|-----|-------|
| `SPIXINETGEAR26` | `Spixi2023` | Factory test wifi — NetGear router at the build site. |
| `Spixi` | `ZCSW$888` | "ZCSW" = "Zhongchuang Sovol Wireless" (or similar — Zhongchuang is the contract manufacturer per `~/.bash_history`'s `zhongchuangv0.12.0` reference). |
| `ZYIPTest` | `12345678` | Default placeholder — also referenced as `WIFI_SSID="ZYIPTest"` / `WIFI_PASSWD="12345678"` in `/boot/system.cfg`. |

All three should be **deleted on `stock_keep`** (privacy + minor security). `/boot/system.cfg`'s `WIFI_SSID/WIFI_PASSWD` should be cleared at the same time so `connect_wifi.sh` doesn't try to reconnect to the factory test network on the next boot.

## udev rules

`/etc/udev/rules.d/`:

- `10-wifi-disable-powermanagement.rules` — Armbian standard.
- `50-usb-realtek-net.rules` — Armbian standard for Realtek USB ethernet adapters.
- `60-gpiod.rules` — `SUBSYSTEM=="gpio", KERNEL=="gpiochip[0-4]", GROUP="biqu", MODE="0660"`. **Bug**: the `biqu` group does not exist on this image (it's a leftover from the BTT CB1 base image). Rule fails silently.
- `70-ttyusb.rules` — sets all `ttyUSB*`, `ttyACM*`, `ttySTM*`, `ttyS*` to mode `0666`. **Wide-open serial devices on the LAN**.

`/lib/udev/rules.d/60-usbmount.rules` — vendor automount rule (kernel `sd[a-z]*` → `systemctl restart makerbase-automount@%k.service`). Will fire if a USB mass-storage device is plugged in.

## apt sources

`/etc/apt/sources.list` is **clean**: stock `deb.debian.org` for Bullseye main + updates + backports + security. `/etc/apt/sources.list.d/` is empty.

This is a major divergence from the Arco, which ships `mirrors.aliyun.com` (Chinese) and required us to switch to `archive.debian.org` for the EOL Buster repos. The Sovol image ships ready-to-go Debian Bullseye repos; nothing to fix on this front.

`dpkg -l` highlights:

- `sv08mini-update-packge` — Sovol's update package (typo: "packge"). Owns `/etc/X11/xorg.conf.d/01-dbbian-defaults.conf` (typo: "dbbian"), `/etc/network/interfaces.d/can0`, `/etc/systemd/system/wifi_server.service`, `/home/sovol/8189fs.ko` (RTL8189FS wifi kernel module), and **klipper subset** (configs, klippy/__pycache__/*, chelper/). The package name "sv08mini" suggests Sovol bundles SV08-Mini and Zero into the same update channel.
- `linux-image-current-sun50iw9`, `linux-headers-current-sun50iw9` — the Allwinner H616 kernel.
- `network-manager`, `wpasupplicant`, `bluez`, `nginx`, `python3.9-minimal`, etc. — standard.

## Files of concern (security / privacy)

| Item | Severity | Action |
|------|----------|--------|
| `wifi_server.py` exposing `/command` to the LAN as root | **Critical** | Disable `wifi_server.service` and remove or sandbox the script. |
| Factory wifi PSKs in `/etc/NetworkManager/system-connections/` | High (privacy / weak network exposure) | Delete the three factory profiles on `stock_keep`. |
| Pre-shared SSH host key shared across all units | High | Regenerate host keys before first user-visible action. |
| `connect_wifi.sh` `connectUSBWifi()` reads `~/printer_data/gcodes/USB/wifi.cfg` | Medium (physical access) | Either disable `connect_wifi.sh` entirely after first wifi or guard the USB branch. |
| `WIFI_SSID/WIFI_PASSWD` in `/boot/system.cfg` (cleartext) | Medium (privacy) | Clear on `stock_keep`. |
| `iptables` empty (no firewall) | Low–Medium (LAN-wide attack surface) | Optional — surface a wizard step. |
| `70-ttyusb.rules` makes `ttyS*` world-writable | Low (any local user can MITM klipper-MCU traffic) | Tighten to `dialout` group. |
| `60-gpiod.rules` references non-existent `biqu` group | Low (no effect, just dead rule) | Cleanup tier. |
| OTA does MD5-only verification, no signature | Low (channel integrity assumed via TLS) | Note in docs; no action unless we own the OTA story. |
| `~/ttyS3.py` developer-leftover | Low | Cleanup tier. |
| `~/patch/` factory build scaffolding | Low | Cleanup tier. |
| `~/usbmount/`, `~/offline_lib/flask/` factory-build leftovers | Low | Cleanup tier. |

## Summary of what's new vs the Arco

1. **Different SBC family**: Sovol uses BigTreeTech CB1 (Allwinner H616, sun50i-h616, aarch64 with stock Bullseye) — not MKS Pi (Rockchip RK3328 with Armbian Buster). Same CoreXY-on-SBC topology, completely different hardware.
2. **Three MCUs all on CAN bus** (vs Arco's USB main + UART toolhead). Main MCU is STM32H750 acting as CAN-bridge; extruder + chamber MCUs are STM32F103. Flashing is via Katapult/CanBoot on `can0` rather than DFU/stm32flash. No `/dev/serial/by-id/` to match against — host-side identification is via CAN UUIDs hardcoded in printer.cfg.
3. **Phone-home minimalism**: only `moonraker-obico` runs by default (Google Cloud), and only because Sovol enables it. No frpc, no HDL, no Aliyun NTP, no Gitee dormant code, no openvpn vestigial config. The Sovol image is dramatically cleaner than the Phrozen one in this respect.
4. **One on-disk daemon is a critical security hole**: `wifi_server.py` runs as root on `0.0.0.0:5000` with an unauthenticated `/command` endpoint that escapes its weak prefix filter trivially. This is a much bigger lift than any single Arco service. Treat as **must-disable** by default.
5. **Pre-shared SSH host key**: the same ed25519 host key ships on every Sovol Zero (and likely every Sovol that uses the SPI-XI image) — factory-build VM `chris-virtual-machine`'s key. Confirmed across four IPs on the same LAN. Regenerate on first run.
6. **Factory wifi credentials baked in**: three NM profiles with plaintext PSKs (`SPIXINETGEAR26/Spixi2023`, `Spixi/ZCSW$888`, `ZYIPTest/12345678`). Plus `/boot/system.cfg` keeps a 4th cleartext copy. Delete all four.
7. **Clean apt sources**: stock `deb.debian.org`, no mirror swap needed (Arco needs `aliyun → archive.debian.org` on Buster).
8. **No vendor screen daemon**: KlipperScreen on `xinit/Xorg/tty7` with the stock upstream start script. The Arco's voronFDM/mksclient complexity isn't here.
9. **Sovol-specific Klipper extras**: `z_offset_calibration.py` (Sovol-original), modified `probe_eddy_current.py` (`vir_contact_speed`), `probe_pressure.py` (Sovol-derivative), `lis2dw.py` (replaces ADXL345). Plus `~/patch/menu.py` overlay onto `klippy/extras/display/menu.py`.
10. **No vendor proprietary binaries with cloud connectivity**. Compare with the Arco's `phrozen_master`, `phrozen_slave_ota`, `mksclient`, `frpc`/`frpc_script`, `voronFDM`, `ota_control`, `auto_refresh`, `udp_server`, `mks-id.sh`, `soft_shutdown.sh`. The Sovol-side equivalents are all open-source: shell + Python + standard kiauh-installed klipper/moonraker/crowsnest/mainsail/obico.
11. **Boot orchestration via `/etc/rc.local` → `/boot/scripts/btt_init.sh`** rather than via `KlipperScreen-start.sh`. Different rewrite target on `stock_keep`.

## Cross-check items for the SV08 Max session

The user has another Claude session auditing the Sovol SV08 Max in parallel. The audit was done independently against a different physical printer; here are the items where the Zero's findings should carry over to the SV08 Max if the two share the Sovol stack (they should), and the items where the two should differ for legitimate hardware reasons.

### Should converge (vendor stack — same on both)

- BigTreeTech CB1 SBC, Allwinner H616, sun50iw9 kernel `5.16.17`, aarch64.
- `SPI-XI 2.3.3 Bullseye` OS image.
- Hostname `SPI-XI`, mDNS as `SPI-XI-N.local` (suffix differs by unit).
- `/etc/passwd`: `sovol:sovol` user, no vendor accounts.
- `/etc/sudoers` line `%sovol ALL=(ALL) NOPASSWD: ALL`.
- Pre-shared ed25519 host key `SHA256:r29wTDuG7tzLvsyF4P06NSatzmc6dKh3dHWw3uGXs5w` (`root@chris-virtual-machine`).
- Three factory wifi profiles with PSKs `Spixi2023` / `ZCSW$888` / `12345678`.
- `/boot/scripts/` BTT-style boot scripts (btt_init.sh, connect_wifi.sh, ota_service.sh, file_change_save.sh, system_cfg.sh, plus `auto_brightness`, `set_rgb`, `mp3/`, `vibration*.sh`).
- `wifi_server.py` on port 5000 as root with `/command` injection.
- Comgrow OTA endpoint `https://www.comgrow.com/files/printer/ver.json` (the JSON content / `versionCode` will differ per SKU).
- `~/.bash_history` factory build trace ending at kiauh + moonraker-timelapse + usbmount.
- Same systemd-enabled services: klipper, KlipperScreen, moonraker, moonraker-obico, crowsnest, nginx, ssh, ntp, NetworkManager, wpa_supplicant, hostapd (auto-restart), wifi_server.
- `/etc/apt/sources.list` clean (deb.debian.org).
- moonraker-obico shipped enabled but unconfigured.
- Klipper repo origin `http://192.168.1.233/root/klipper.git` (Sovol internal Gitea).
- KlipperScreen-start.sh is the stock upstream script (no Sovol customization).

### Should differ (hardware-dependent)

- **Build volume**: Zero is ~155×152.5×155 mm; SV08 Max should be substantially larger — confirm position_max in printer.cfg.
- **Number of MCUs / CAN UUIDs**: Zero has three MCUs (`0d1445047cdd` main / `61755fe321ac` extruder / `58a72bb93aa4` hot/chamber). SV08 Max may have additional MCUs (e.g. tool-changer head, LED controller). UUIDs will be different per-unit anyway.
- **Stepper count and current**: Zero is X+Y TMC5160 SPI @ 3.5 A, single Z TMC2209 UART. SV08 Max likely has 4× Z-screws (or more) — driver layout will differ.
- **Probe**: Zero uses eddy-current via LDC1612. SV08 Max may use the same or a different probe (Sovol has shipped optical / Klicky / contact across SKUs).
- **`board_model` string in `moonraker-obico.cfg [meta]`**: Zero is `H616_JC_3Z_5160_V1.2`. SV08 Max should be a different board revision designation.
- **`printer_model` string**: Zero is `SOVOL ZERO`. SV08 Max should be `SOVOL SV08 MAX` or similar.
- **Klipper service description**: Zero says "SV1" (Sovol's internal name for the Zero). SV08 Max should differ — likely "SV08" or similar.
- **`sv08mini-update-packge` debian package**: present on Zero. The SV08 Max may have `sv08max-update-packge` or share `sv08mini-update-packge` (the typo `packge` is consistent — same authoring lineage). Worth recording either way.
- **`/etc/hostname` IP-suffix**: differs per unit; not a real divergence.
- **Some `klippy/extras/` modification dates**: depend on which firmware release each printer was last OTAed to.

If the SV08 Max session reports any of the "should converge" items differently (e.g. a different host key, an `aliyun` apt mirror, an active `frpc` daemon), that's a real divergence — and it means the Sovol vendor stack splits per-SKU more than expected. Flag it for the user; don't paper over.
