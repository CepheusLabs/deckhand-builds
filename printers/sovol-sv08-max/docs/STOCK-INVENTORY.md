# Stock Sovol SV08 Max — Full Inventory

Complete inventory of everything Sovol ships on a stock Sovol SV08 Max
that our replacement process needs to be aware of. Derived from a
**live audit over SSH** (`sovol@192.168.0.121`, ed25519 audit key,
read-only with sudo for a small set of root-only file reads). Audit
date: 2026-05-01. Raw probes (out-of-repo to keep PSK-bearing dumps
out of `deckhand-builds/`):
`installer/.audits/sovol-sv08-max-20260501/probe_clean.txt`,
`probe2.txt`, `probe3.txt`, plus `FINDINGS.md` synthesizing them.

The Sovol SV08 Max shares its base OS image (the **SPI-XI 2.3.3
Bullseye** image) with the Sovol Zero. Most of the audit findings
converge with `printers/sovol-zero/docs/STOCK-INVENTORY.md`; the
material differences are flagged inline below. For the side-by-side
cross-check, see `docs/ALIGNMENT-WITH-ZERO.md`.

> **Note on this unit**: an audit SSH key
> (`deckhand-audit-20260501`) is appended to `~/.ssh/authorized_keys`.
> A prior `cowork-session` ed25519 key is also present from earlier
> work. Otherwise nothing has been modified — everything else in
> this document is factory Sovol.

## Identity

- **Hostname**: `SPI-XI` (also the OS image's `PRETTY_NAME` —
  `SPI-XI 2.3.3 Bullseye`).
- **Distro**: Debian 11 (Bullseye), Sovol-rebadged. Same Armbian-derived
  base as the Zero — many `armbian-*` services and the standard armbian
  motd scripts are present, but `/etc/armbian-release` has been stripped.
- **Kernel**: `5.16.17-sun50iw9 #2.3.3 SMP Tue Jan 21 10:22:53 CST 2025`
  — note the build date is **2025-01-21**, three months newer than the
  Zero's audited build of 2024-10-29 from the same kernel version
  string. Same kernel source, different build host run.
- **Architecture**: `aarch64`.
- **SBC**: device-tree model `BigTreeTech CB1`, device-tree compatible
  string `allwinner,sun50i-h616`. Same as the Zero — a BTT CB1 module
  socketed onto Sovol's mainboard.
- **Stock board** (per `moonraker-obico.cfg` `[meta]`):
  `H616_JC_6Z_5160_V1.2`. Sovol-internal designation; the `5160` aligns
  with the TMC5160 X/Y drivers and `6Z` aligns with the four Z-axis
  steppers on a quad-gantry plus two related connections (vs the
  Zero's `3Z` for its single-Z platform).
- **eMMC**: `mmcblk2`, **31,289,507,840 bytes (~32 GB)** — four times
  the Zero's eMMC. MBR (msdos) partition table.
  - `mmcblk2p1` — 256 MB FAT16 `/boot` (`LABEL=BOOT`)
  - `mmcblk2p2` — 30.7 GB ext4 `/`
  - `mmcblk2boot0`, `mmcblk2boot1` — 4 MB eMMC boot partitions
  - `zram0` (517 MB swap) and `zram1` (52 MB ext2 log2ram)
- **Time / NTP**: `ntpd` (classic NTP daemon). No `chrony`, no
  `aliyun` NTP override.
- **Timezone**: `Etc/UTC` (default). `/boot/system.cfg` exposes
  `TimeZone="Asia/Shanghai"` as a commented-out override.

### eMMC layout summary

| Mount | Device | Size | FS | Notes |
|-------|--------|------|----|-------|
| `/boot` | `mmcblk2p1` | 256 MB | vfat | `/boot/scripts/`, `/boot/system.cfg`, `/boot/gcode/` (USB-injected gcode pickup), kernel images. User-editable from a card reader. |
| `/` | `mmcblk2p2` | 30.7 GB | ext4 | 50% used at audit time. |

Boot mode is **MBR / msdos** (same as the Zero, same as the Arco).

## Boot sequence on stock

Two parallel boot tracks, identical structure to the Zero.

### 1. `/etc/rc.local` → `/boot/scripts/btt_init.sh` (vendor track)

`/etc/rc.local` runs:

```
chmod +x /boot/scripts/*
/boot/scripts/btt_init.sh
```

`btt_init.sh` chowns `/home/sovol/` recursively, sweeps any `*.gcode`
from `/boot/gcode/` into `~/printer_data/gcodes`, then backgrounds
the vendor daemons:

```bash
#./extend_fs.sh &
./system_cfg.sh &
./connect_wifi.sh &
#./auto_setmcu_id.sh &
./file_change_save.sh &
#sudo -u sovol ./ota_service.sh &
#./sync.sh &
```

**Divergence from the Zero**: the OTA service launch line is
**commented out** on the SV08 Max (`#sudo -u sovol ./ota_service.sh &`),
while it's active on the Zero. The OTA scripts are still present at
`/boot/scripts/ota_service.sh` and the `_OTA` Klipper macro is still
wired up via `~/ota_client.sh`, but the SIGUSR1 trigger has no
running target — the daemon doesn't start at boot. So the Max is
**not on Sovol's Comgrow OTA channel** out of the box.

`auto_setmcu_id.sh`, `extend_fs.sh`, `sync.sh` are present but
commented out — same as the Zero. `auto_setmcu_id.sh` is no longer
needed because Sovol now hardcodes CAN UUIDs in `printer.cfg` rather
than discovering them at boot.

### 2. systemd-enabled units (standard track)

38 enabled unit files. The non-default ones beyond stock
Armbian/Debian, with divergences from the Zero called out:

- `klipper.service` — runs `klippy.py` as `sovol`. Description string
  is `Klipper 3D Printer Firmware SV1` (same as Zero — "SV1" is the
  image-level label, not per-unit).
- `KlipperScreen.service` — runs upstream KlipperScreen unmodified
  (same as Zero). Status `running` on the Max (the Zero session saw
  `auto-restart` on theirs because Xorg was exiting).
- `moonraker.service` — Moonraker upstream.
  `SupplementaryGroups=moonraker-admin` (custom gid 1001 created at
  factory by kiauh).
- `moonraker-obico.service` — **enabled and running**. Talks to
  `app.obico.io` continuously (no API key shipped, but the heartbeat
  fires regardless). Same default-on as the Zero.
- `crowsnest.service` — webcam stream (ustreamer on `127.0.0.1:8080`,
  single camera at `/dev/video0`).
- `nginx.service` — serves Mainsail on port 80. Site config at
  `/etc/nginx/sites-available/mainsail`.
- `wifi_server.service` — see § Vendor binaries / `/usr/local/bin/wifi_server.py`.
  **CRITICAL**.
- `makerbase-client.service` — **Max-only**. Launches
  `/home/sovol/zhongchuang/build/start.sh` which runs the
  `zhongchuang_klipper` serial-TFT screen daemon. Not present on the
  Zero. See § Display / screen daemon.
- `hostapd.service` — enabled but in `auto-restart` (no AP config
  exists). Vestigial from the BTT CB1 base image.
- `bluetooth.service` — enabled but inactive.
- `hdmi-audio.service` — Sovol/Allwinner specific oneshot.
- `ssh.service` — OpenSSH 8.x (Debian-Bullseye build).
- `ntp.service` — classic ntpd.
- `NetworkManager.service` + `wpa_supplicant.service` +
  `networking.service` — net stack (NM-managed, with
  `/etc/network/interfaces.d/can0` for the CAN interface).
- `armbian-hardware-monitor`, `armbian-hardware-optimize`,
  `armbian-zram-config`, `bootsplash-hide-when-booted`,
  `fake-hwclock`, `e2scrub_reap`, `resolvconf*`, `rsync.service`,
  `systemd-pstore` — Armbian/Debian standard.

Notably **missing** (vs the Phrozen Arco): `frpc`, `phrozen_master`,
`voronFDM`, `mksclient` (the makerbase-client on the Max runs
zhongchuang_klipper, not the Phrozen-side mksclient), `makerbase-udp.service`,
`makerbase-net-mods.service`, `makerbase-byid.service`, `openvpn`,
`chrony*`. The Sovol image is dramatically cleaner than the Phrozen
one in this respect.

### Multi-user.target wants

Same set as the enabled list; nothing custom under
`default.target.wants`, `basic.target.wants`, or
`network-online.target.wants`.

## Vendor binaries and scripts

### `/boot/scripts/` (BigTreeTech CB1 base image scripts, retained by Sovol)

Same script set as the Zero — Sovol forked from BTT's CB1 reference
image and reworked the contents for their flow.

| Path | Role | Keep strategy |
|------|------|---------------|
| `/boot/scripts/btt_init.sh` | Boot orchestrator (called from `/etc/rc.local`). | Replace with a Deckhand-rewritten version on `stock_keep` (drop the daemons we don't want, keep the `/boot/gcode/` sweep and the `chown`). |
| `/boot/scripts/connect_wifi.sh` | Wifi connect helper. Reads `WIFI_SSID/WIFI_PASSWD` from `/boot/system.cfg`. The `connectUSBWifi()` USB-stick branch (reads `wifi.cfg` from `~/printer_data/gcodes/USB/`) is defined in the script but the call to it is **commented out** on the Max; on the Zero the call is live. | Stop launching from `btt_init.sh` after first wifi. NetworkManager remembers the connection. |
| `/boot/scripts/file_change_save.sh` | inotify watcher on `~/printer_data/config`, calls `sync` on writes. The PLR script `~/plr.sh` also appends to the same file — two writers. | Drop. Klipper/Moonraker handle config persistence. |
| `/boot/scripts/ota_service.sh` | OTA daemon (Comgrow). On the Max, **not started at boot** (commented out in `btt_init.sh`). | Leave on disk; don't re-enable. |
| `/boot/scripts/system_cfg.sh` | Applies `/boot/system.cfg` (timezone, hostname, KS rotation, BTT_PAD7 toggle, sound/vibration toggles). Writes Xorg fragment for HDMI-1 rotation when `BTT_PAD7=ON`. | Keep — useful first-run config knobs from the boot partition. |
| `/boot/scripts/auto_setmcu_id.sh` | Would set MCU UUID at boot. | Already disabled. |
| `/boot/scripts/extend_fs.sh` | One-shot rootfs expansion. | Already disabled. |
| `/boot/scripts/sync.sh` | Periodic `sync` loop. | Already disabled. |
| `/boot/scripts/auto_brightness` (binary, 14 KB) | Touchscreen brightness controller. Gated on `BTT_PAD7=ON` in system.cfg. | Keep if user attaches an HDMI display; cleanup tier otherwise. |
| `/boot/scripts/set_rgb` (binary, 9.6 KB) | RGB indicator LED on the screen module. | Same gating. |
| `/boot/scripts/sound.sh`, `vibration.sh`, `vibrationsound.sh` | Touch feedback hooks via `/sys/class/gpio/gpio79`. Gated on `TOUCH_VIBRATION/TOUCH_SOUND`. | Same gating. |
| `/boot/scripts/mp3/` | Sound files (click.mp3 etc). | Same gating. |
| `/boot/scripts/wifi.log` | Append-only log written by `connect_wifi.sh`. 12 MB on the audited unit (mostly retry noise from the never-reached `ZYIPTest` factory wifi). | Cleanup tier. |

### `/usr/local/bin/`

| Path | Role | Notes |
|------|------|-------|
| `/usr/local/bin/wifi_server.py` (sovol:sovol, world-readable) | Flask app. **Loaded by `/etc/systemd/system/wifi_server.service` and runs as ROOT on `0.0.0.0:5000` with NO authentication.** | **CRITICAL security finding (same on Zero).** Exposes `/scan_wifi`, `/connect_wifi`, `/disconnect_wifi`, `/networkInterface`, `/interfaceStatus`, `/activeConnections`, `/linkStatus`, `/get_ip`, `/ping`, and **`/command`**. The `/command` endpoint runs `subprocess.run(cmd, shell=True, …)` after a weak prefix check (`nmcli`, `ip`, `iw`, `ifconfig`, `ping`, `iwconfig`). Trivially escapable: `cmd="ip ; rm -rf /"` passes the `startswith` test. Also, `/connect_wifi` does `cmd = f"nmcli device wifi connect '{ssid}' password '{password}'"` then `subprocess.getoutput(cmd)` — SSID/password command injection. **Any device on the LAN can run shell commands as root.** |
| `/usr/local/bin/flask` | 208-byte Python entrypoint script (Flask CLI). | Standard. |
| `/usr/local/bin/watchdog_test` | 13.8 KB binary. | Not invoked at boot; provenance unclear. Cleanup tier. |
| `/usr/local/bin/crowsnest` (symlink → `/home/sovol/crowsnest/crowsnest`) | Standard Crowsnest entrypoint. | Keep. |

### `/home/sovol/` vendor scripts

| Path | Role | Notes |
|------|------|-------|
| `~/ota_client.sh` (mode 0777) | Sends `SIGUSR1` to `/boot/scripts/ota_service.sh`. Wired into Klipper macro `_OTA` (via `get_ip.cfg`). | **No-op on the Max** — the OTA daemon isn't running, so the SIGUSR1 has no target. |
| `~/factory_resets.sh` | `cp -p ~/patch/config/*.cfg ~/printer_data/config/ && python3 ~/pyhelper/restart_firmware.py`. Wired into Klipper macro `FACTORY_RESETS`. | `~/patch/config/` is empty on the audited unit; factory-reset is a no-op as configured. Same as Zero. |
| `~/get_ip.sh` | Calls `python3 ~/pyhelper/send_ip.py` which posts an `M117 <IP>` to Moonraker. | Wired into `_GET_IP` macro. Harmless. |
| `~/clear_plr.sh`, `~/plr.sh`, `~/sovol_plr_height` | Power-loss-recovery scripts. Wired into `plr.cfg`. | Keep. |
| `~/ttyS3.py` | 366 B. Opens `/dev/ttyS3` at 9600 baud, writes "Hello!", reads, closes. | A leftover developer probe — `/dev/ttyS3` IS used at runtime on the Max (zhongchuang_klipper drives the serial TFT through it, even if not currently held open at audit time). Cleanup tier. |
| `~/uart` (35 KB ELF aarch64) | Vendor serial helper binary. Unstripped. No URLs / cloud strings. | Cleanup tier — provenance unclear. |
| `~/pyhelper/send_ip.py` | Posts current IP as `M117` via Moonraker REST. | Keep. |
| `~/pyhelper/restart_firmware.py` | Posts `firmware_restart` via Moonraker. | Keep. |
| `~/pyhelper/ota_process.py` | Posts `M117 <progress>` during OTA download. | Keep, even though OTA isn't active. |
| `~/patch/patch.sh` | Build-time overlay. Already applied at factory. | Document as factory-build artifact. |
| `~/patch/menu.py`, `~/patch/menu.cfg`, `~/patch/display.cfg` | Sovol's overlay of `klippy/extras/display/`. Already overlaid onto klippy. | Same as Zero. |
| `~/patch/config/` | Empty directory. | factory-reset payload location; currently empty. |
| `~/usbmount/` | Sources for `makerbase-automount@.service`. Already `make install`-ed. | Cleanup tier. |
| `~/众创klipper.tft.bak` (9.7 MB) | **Max-only.** Closed-source ZhongChuang TFT panel firmware (Nextion-style serial firmware). Backup of whatever shipped on the panel. | Keep — needed if a user re-flashes the TFT panel. |
| `~/zhongchuang/` | **Max-only.** Full source tree for the `zhongchuang_klipper` serial-TFT screen daemon. See § Display below. | Keep — required at runtime. |
| `~/cache_cleaned`, `~/.kiauh.ini`, `~/clear_plr.sh`, `~/demon_vars.cfg`, `~/plr_parameter.txt`, `~/sovol_plr_height` | Various Sovol state/config files. | Various — see profile.yaml `stock_os.files`. |

### `/root/` — **Max-only artifacts**

Major divergence from the Zero, whose `/root/` is essentially empty.

| Path | Size | Notes |
|------|------|-------|
| `/root/klipper.bin` | 28.9 KB | sovol-owned, dated 2024-12-25. **Plausibly the main MCU firmware blob** — same size as a Klipper application binary on STM32H750 (chip identity inferred from the `.config750` build config under `~/klipper/`). `file(1)` not yet run to confirm; verify before relying on it for re-flashing. |
| `/root/mcu_update.sh` | 1.2 KB | Pairs with `klipper.bin`. Sovol-owned, dated 2024-12-25. Not invoked at runtime. |
| `/root/klipper.bin` + flasher pair | — | Together these document the path the factory build used to flash the main MCU. Note that the Sovol-shipped flash scripts at `~/printer_data/build/*_update_fw.sh` look in **that** directory for blobs, not in `/root/`. The Max's flasher won't find the blob without an explicit path override. |

`/root/.bash_history` documents the factory build trail:
`cd zhongchuang/build/; make; ./builddeb.sh; cd ../patch/; ./patch.sh; pip install flask; systemctl enable wifi_server.service; vi ../printer_data/build/.version.cfg`.
Confirms the zhongchuang daemon, Flask wifi_server, and patch overlay
were all set up by hand during factory provisioning.

`/root/.ssh/` does not exist — no root-level SSH keys.

### `~/printer_data/build/` (firmware-flash tooling)

Same script set as the Zero, **but no .bin blobs in this directory**:

| Path | Role |
|------|------|
| `flash_can.py` (26 KB) | Eric Callahan's Katapult/CanBoot CAN flasher. |
| `mcu_update_fw.sh` | Flashes main MCU at CAN UUID `0d1445047cdd`. |
| `extruder_mcu_update_fw.sh` | Flashes extruder/toolhead MCU at CAN UUID `61755fe321ac`. |
| `extra_mcu_update_fw.sh` | Flashes chamber MCU at CAN UUID `58a72bb93aa4`. |
| `.version.cfg` (14 B) | Factory version stamp. **Max-only** — not on Zero. |
| `finishedGuide` (0 B) | Factory-build sentinel. **Max-only** — not on Zero. |

**No .bin blobs are in this directory.** The Zero ships
`extruder_mcu_klipper.bin` (~31 KB) here; the Max ships none. The
candidate main-MCU blob is at `/root/klipper.bin` instead.

`get_ip.cfg` registers `[gcode_shell_command]` entries for each of
the three MCU updaters and exposes them as `_MCU_UP`,
`_EXTRUDER_MCU_UP`, `_EXTRA_MCU_UP` macros — so the user can trigger
MCU reflashes from the web UI / touchscreen, but only if a blob is
present at the script's expected path.

## OTA / phone-home

The OTA daemon (`/boot/scripts/ota_service.sh`) is **not running at
boot** on the Max. The script is the same as on the Zero — reads a
local version stamp from `~/klipper/klippy/extras/display/menu.cfg`,
fetches `https://www.comgrow.com/files/printer/ver.json`, loops
`sleep 1` waiting for `SIGUSR1`, downloads + MD5-verifies + `dpkg
-i`s + reboots on signal — but the launch line in `btt_init.sh` is
commented out, so nothing receives the SIGUSR1 from the `_OTA`
macro.

| Host / endpoint | Direction | Active on Max | Notes |
|-----------------|-----------|---------------|-------|
| `https://www.comgrow.com/files/printer/ver.json` | OTA → outbound HTTPS | **No** (daemon not running) | Comgrow is Sovol's primary EU/US reseller. The OTA channel is hosted on the partner's website. MD5-only integrity. |
| `https://app.obico.io` | Obico → outbound HTTPS | **Yes — always** while `moonraker-obico.service` is up. Resolves to GCP (34.95.90.112 observed). | Stock config has no API key — Obico won't actually function until the user registers — but the long-poll heartbeat hits Obico's servers continuously. Disable the service to stop. |
| `192.168.1.233/root/klipper.git` | git origin (decorative) | Never — internal Sovol LAN, not reachable post-ship. | |
| `192.168.1.233/root/zhongchuang.git` | git origin (decorative) | Never. | The zhongchuang screen daemon's internal Sovol Gitea. |
| Aliyun / Tencent / Gitee / HDL endpoints | — | **Not present** | Major divergence from the Phrozen Arco. |

`iptables -L` and `ip6tables -L` are empty. `/etc/cron.d/`,
`/etc/cron.daily/`, `/etc/crontab`, and per-user crontabs are stock
Armbian/Debian — **no Sovol cron entries**.

### Listening sockets (LAN-reachable)

| Port | Process | Auth | Severity |
|------|---------|------|----------|
| 22 | sshd | publickey/password | OK (PermitRootLogin no, factory user `sovol`/`sovol`). |
| 80 | nginx (mainsail) | none | Standard. |
| 5000 | `wifi_server.py` (root) | **none** | **CRITICAL** — see `/usr/local/bin/wifi_server.py` above. |
| 7125 | moonraker | trusted_clients (192.168/10/172.16/127/169.254) | Standard. |
| 8080 | `main` (ustreamer.bin, crowsnest) | bound to 127.0.0.1 only | LAN-unreachable. The "main" name in `ss -tnlp` is just ustreamer's renamed argv[0]. |
| 46793 (ephemeral) | moonraker-obico | n/a | Outbound-only IPC port. |

`avahi-daemon` advertises mDNS as `SPI-XI-2.local` (the `-2` suffix
is the per-host duplicate-name disambiguator NM applies on first
boot when another `SPI-XI` is already on the LAN).

## Vendor klipper extras

Klipper repo at `/home/sovol/klipper/`:

- **Tracked URL**: `http://192.168.1.233/root/klipper.git` — Sovol's
  internal Gitea (private LAN address, plain HTTP). Same origin as
  the Zero's. Won't reach anything once shipped; the git remote is
  decorative.
- **HEAD**: `d4031b3 zoffset校准增加前置电流校准动作` ("z offset
  calibration adds pre-current calibration action"). **Newer than
  the Zero's HEAD** (`cc8afd8 / 1.3.7版本`) — implies the Max ships
  with a slightly later Sovol klipper build. Same set of Sovol-
  modified extras files; the diff between them is concentrated in
  the eddy probe / z_offset_calibration code.
- **Base**: derived from upstream Klipper 0.12.0 (same as Zero).
- **MCU firmware build stamps**: Not captured during this audit. The
  Zero session captured stamps from `klippy.log` (main MCU
  `14d7b18-dirty-20250210_015142-SPI-XI`, extruder
  `cc8afd8-dirty-20250310_015728-SPI-XI`, hot
  `cc8afd8-dirty-20250310_015837-SPI-XI`, all built on a host
  named `SPI-XI`). The Max's stamps may differ; verify in a
  follow-up probe if firmware re-flashing is in scope.

### `klippy/extras/` Sovol modifications

Same set as the Zero — see
`printers/sovol-zero/docs/STOCK-INVENTORY.md` § "klippy/extras Sovol
modifications" for the full table. The headline pieces:

- `z_offset_calibration.py` — **Sovol-original**, copyright header
  `Sovol3d <info@sovol3d.com>`. Implements the `Z_OFFSET_CALIBRATION`
  g-code used in `START_PRINT`.
- `probe_eddy_current.py` — modified beyond upstream
  (Sovol-added `vir_contact_speed`, `TYPE_VIR_TOUCH`).
- `probe_pressure.py` — Sovol-original, started as a derivative of
  upstream `probe.py`.
- `lis2dw.py` (replaces ADXL345 in the Sovol toolchain).
- `bed_mesh.py` heavily extended for `rapid_scan` + eddy-current
  `BED_MESH_CALIBRATE`.
- Plus modified `fan.py`, `heater_fan.py`, `homing.py`,
  `ldc1612.py`, `probe.py`, `shaper_calibrate.py`,
  `display/menu.py`, `display/menu.cfg`, `display/display.cfg`.

### `/home/sovol/klipper/.config*` (USB-CAN bridge build configs)

Three saved build configs for the **USB-to-CAN bridge chip**, NOT
the downstream stepper/toolhead MCUs (those firmwares were flashed
at factory):

| File | Chip | Mode |
|------|------|------|
| `.config` (current) | STM32F103xe @ 72 MHz | CANSERIAL+CANBUS bridge, PB8/PB9, USB ID 1d50:614e |
| `.config103` | STM32F103xe @ 72 MHz | Same as `.config` |
| `.config750` | **STM32H750xx @ 400 MHz** | USBCANBUS mode, PA11/PA12 USB + PB8/PB9 CAN |

`.config750` is the highest-performance variant — the chip identity
implied by the running `klipper.bin` candidate at `/root/klipper.bin`
(28.9 KB matches an H750 application size). The two F103 configs
are presumed leftovers from earlier hardware revisions or the
Sovol Zero's bridge.

## Stock printer.cfg (live, runtime)

Single `~/printer_data/config/printer.cfg` (~48 KB), with includes
for `mainsail.cfg`, `chamber_hot.cfg`, `timelapse.cfg`, `plr.cfg`,
`Macro.cfg`, `moonraker_obico_macros.cfg`. (`buffer_stepper.cfg`
included is commented out.) Highlights:

- **Kinematics**: `corexy`. **Build volume from position_max /
  mesh_max**: X 502 / Y 505 / Z 505 mm; usable bed mesh region is
  `13,15 → 476,490` mm (~4 cm of edge unreachable to the bed-mesh
  probe, reachable to the toolhead). Large-format CoreXY consistent
  with the SV08 Max product description.
- **Three MCUs, all on CAN bus** (1 Mbps), same UUIDs as the Zero:
  - `[mcu]` (main) — `canbus_uuid: 0d1445047cdd` — STM32H750xx
    inferred. 400 MHz. Bridges USB host ↔ CAN bus.
  - `[mcu extra_mcu]` — `canbus_uuid: 61755fe321ac` — STM32F103xe
    @ 72 MHz. Carries the toolhead: extruder stepper, hotend
    heater + thermistor, hotend fan + tach, dual part-cooling fans
    (fan0/fan1), LDC1612 i2c eddy probe, LIS2DW SPI accelerometer.
    (Sovol calls this `extra_mcu` on the Max but `extruder_mcu` on
    the Zero — same chip role, same UUID, just renamed.)
  - `[mcu hot_mcu]` (in `chamber_hot.cfg`) — `canbus_uuid:
    58a72bb93aa4` — STM32F103xe @ 72 MHz. Carries the chamber
    heater (PA0), chamber thermistor (PA5), chamber fan, hot_led.
- **CAN bus dongle**: `lsusb` shows `1d50:606f OpenMoko, Inc.
  Geschwister Schneider CAN adapter` — gs_usb. The H750 main MCU
  exposes itself as gs_usb, providing the host-side `can0`
  interface. **`/dev/serial/by-id/` is empty** at runtime — no
  USB-serial Klipper MCU.
- **Steppers**:
  - X, Y: TMC5160 SPI (`run_current: 3.0`, `sense_resistor: 0.05`)
    — note **3.0 A** vs the Zero's **3.5 A**.
  - Z (×4 motors, quad-gantry): TMC2209 UART (`run_current: 1.2`,
    `sense_resistor: 0.150`, `gear_ratio: 80:12`).
  - Extruder: TMC2209 UART (`run_current: 0.8`, `hold_current: 0.3`).
- **Probe**: `probe_eddy_current eddy` using `ldc1612` on
  `extra_mcu i2c2`. `z_offset: 3.5`, `x_offset: -19.8`,
  `y_offset: -0.75`. Bed mesh is `60×60`, `algorithm: bicubic`,
  fade end 10 mm, scan_overshoot 4.
- **Accelerometer**: `lis2dw` on `extra_mcu` SPI (PB12-15),
  `axes_map: x,z,y`. Used for `resonance_tester` at probe point
  `250,250,30`.
- **Heaters**: hotend `max_temp: 310` with custom thermistor table
  `extruder_thermistor` (resistance values look like a PT1000-shaped
  curve, not a stock NTC); bed `max_temp: 120` with custom
  `bed_thermistor` table; chamber `max_temp: 65` watermark control
  (vs the Zero's 70 °C).
- **Fans**: `fan0` (front part-cooling, on toolhead), `fan1` (back
  part-cooling, on toolhead), `fan2` (auxiliary, on main),
  `fan3` (exhaust, on main), `heater_fan hotend_fan` (on toolhead
  PA6 with tach on PA1), `heater_fan bed_fan` (on main PE14).
  More fans than the Zero ships.
- **Filament sensors**: `filament_switch_sensor switch_sensor` on
  PB2 (microswitch) AND `filament_motion_sensor encoder_sensor` on
  PE7. Two sensors (the Zero has only the switch).
- **Power-loss recovery**: via `plr.cfg` — `[gcode_shell_command
  POWER_LOSS_RESUME]` runs `~/plr.sh`.
- **Vendor M-codes**: `M9928 X/Y/Z` (Sovol-custom homing — replaces
  G28's per-axis pieces in the homing_override block),
  `plr_temperature_wait` (Sovol PLR macro), `M141`/`M191` for
  chamber control. **The chamber heater section is named
  `[heater_generic chamber_temp]` on the Max** (the Zero uses
  `[heater_generic chamber_heater]`); `M141`/`M191` macros
  reference the local name and are NOT cross-printer interchangeable.

### Macro inventory (Macro.cfg + plr.cfg + chamber_hot.cfg)

- `_global_var` — global state holder. `variable_pause_park`,
  `variable_cancel_park` (parks at `y=501`, confirming the ~500 mm
  Y bed), `variable_z_maximum_lifting_distance: 502`,
  `variable_load_filament_extruder_temp: 250`,
  `variable_bed_mesh_calibrate_target_temp: 65`,
  `variable_disable_filament_jam_detection: False`,
  `variable_is_push_buffer: True` (commented — buffer feeder is
  optional hardware), etc.
- `[gcode_shell_command FACTORY_RESETS]` → `~/factory_resets.sh`.
- `[force_move]` — enable_force_move: True.
- `mainled_on` / `mainled_off` — `SET_PIN PIN=main_led VALUE=1/0`.
- `_GET_IP`, `_OTA`, `_OBICO_RESTART`, `_OBICO_CODE_GET` (in
  `get_ip.cfg`).
- `_MCU_UP`, `_EXTRUDER_MCU_UP`, `_EXTRA_MCU_UP` (the firmware
  reflasher entry points).
- `M141` / `M191` chamber control macros (in `chamber_hot.cfg`).

## Display / screen daemon

**Two-screen support, with the serial TFT as the default.** Major
divergence from the Sovol Zero, which has only a small UC1701 LCD
driven by Klipper's `[display]` extras (no separate daemon).

### Primary: serial TFT touchscreen

Driven by `zhongchuang_klipper`, a Sovol-built C++ daemon. Source
tree at `/home/sovol/zhongchuang/`. Built binary at
`/home/sovol/zhongchuang/build/zhongchuang_klipper` (8.6 MB ELF
aarch64). Launched by `makerbase-client.service` →
`/home/sovol/zhongchuang/build/start.sh` →
`./zhongchuang_klipper localhost`. Connects to Moonraker via
WebSocket on `localhost:7125`; talks to the TFT panel over
`/dev/ttyS3` (9600 baud, Nextion-style serial protocol).

The daemon is a **Makerbase mksclient derivative** with Sovol's
`sovol_http.cpp` addition for OTA progress UI. Source files under
`~/zhongchuang/src/`:

- Mksclient lineage: `MoonrakerAPI.cpp`, `KlippyGcodes.cpp`,
  `KlippyRest.cpp`, `process_messages.cpp`, `refresh_ui.cpp`,
  `ui.cpp`, `MakerbasePanel.cpp`, `MakerbaseShell.cpp`,
  `MakerbaseSerial.cpp`, `MakerbaseParseIni.cpp`, `event.cpp`,
  `file_list.cpp`, `wifi_list.cpp`, `mks_*.cpp`, plus headers and
  `wpa_test.c` / `wpa_wifi.c` companion utilities.
- Sovol-original: `sovol_http.cpp` (handles OTA progress
  notifications to the TFT during `_OTA` runs — note that on the
  Max, the OTA daemon isn't running so this code path is dormant).
- Build system: CMake. Links against `pthread`, `boost_system`,
  `wpa_client`, `curl`. Internal git origin
  `http://192.168.1.233/root/zhongchuang.git`.
- The systemd unit launches the daemon as **root** with
  `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libSegFault.so` and
  `LimitCORE=infinity` — Sovol expects the daemon may segfault and
  wants core dumps. Smell, but not Deckhand's problem.

The TFT panel firmware itself (the `.tft` blob loaded by the
Nextion-class display) is **closed-source ZhongChuang vendor
firmware**, separate from the open-source daemon. A 9.7 MB backup
sits at `/home/sovol/众创klipper.tft.bak`. Whatever ships on the
panel is the baseline; if a user re-flashes the panel, the `.bak`
is the documented restore image.

`/dev/ttyS3` was not held open by any process during the audit. The
zhongchuang daemon may open the port on demand, the TFT may have
been disconnected during this session, or the connection may use a
different transport intermittently. Worth confirming `lsof
/dev/ttyS3` while the screen is in active use.

### Secondary: KlipperScreen on HDMI (optional)

The CB1's HDMI port supports an optional touchscreen. KlipperScreen
runs upstream-unmodified on `/dev/tty7` via `xinit` + Xorg fbdev,
with the Xorg config at `/etc/X11/xorg.conf.d/01-dbbian-defaults.conf`
(typo: "dbbian" for "debian"). Default Xorg rotation is `UD`
(180-degree). Touchscreen calibration matrix is set up via
libinput.

`KlipperScreen.service` is enabled by default and renders to fbdev
whether or not an HDMI display is attached. Harmless when nothing
is plugged in. If a user attaches an HDMI display + USB touch:

- They flip `BTT_PAD7=ON` in `/boot/system.cfg` to enable the BTT
  PAD7 helper code paths in `system_cfg.sh`.
- `system_cfg.sh` writes
  `/usr/share/X11/xorg.conf.d/90-monitor.conf` with the
  user-configured rotation and CalibrationMatrix, then restarts
  KlipperScreen.

The `auto_brightness` and `set_rgb` binaries under `/boot/scripts/`
are PAD7-specific helpers also gated on `BTT_PAD7=ON`.

`/etc/X11/xorg.conf.d/01-dbbian-defaults.conf` is **not owned by
any dpkg package** on the Max (Sovol copied it directly during
factory build, not via `dpkg -i`).

## Network indicators

| Host / IP | Who reaches it | Port | Active? | Notes |
|-----------|----------------|------|---------|-------|
| `app.obico.io` (e.g. 34.95.90.112) | `moonraker-obico` | 443 | **Yes — always** | Disable `moonraker-obico.service` to stop. |
| `www.comgrow.com/files/printer/ver.json` | `ota_service.sh` | 443 | **No** (daemon not started at boot on Max) | Comgrow-hosted OTA. Differs from Zero. |
| `192.168.1.233/root/klipper.git` | git origin (decorative) | 80 | Never | Internal Sovol LAN, not reachable post-ship. |
| `192.168.1.233/root/zhongchuang.git` | git origin (decorative) | 80 | Never | Same. |
| Aliyun / Tencent / Gitee / HDL endpoints | — | — | **Not present** | Major divergence from Phrozen Arco. |

## Users, auth, SSH host keys

- `/etc/passwd`: `root` (bash, /root), `sovol` (uid 1000,
  /home/sovol, bash). Plus standard service accounts. **No
  additional vendor accounts.** Same as Zero.
- **`sovol` has passwordless sudo** via a line appended directly to
  `/etc/sudoers` (`%sovol ALL=(ALL) NOPASSWD: ALL`), bypassing
  `/etc/sudoers.d/`. Stock convention violation but functionally
  fine. Same as Zero.
- **Default password**: `sovol:sovol` — published in this repo. The
  wizard should force a change on first run.
- `/etc/sudoers.d/`: only `README` (Debian-shipped, not readable by
  sovol).
- `/etc/group`: `moonraker-admin` group (gid 1001, member: sovol)
  added by kiauh during factory build.

### Pre-shared SSH host keys (security finding — same as Zero)

The SV08 Max ships with **all three** factory-baked SSH host keys
generated on a build VM named `chris-virtual-machine`. Identical
fingerprints to the Sovol Zero, confirming the SPI-XI image lineage
shares the same baked key set across multiple Sovol SKUs:

```
ed25519  SHA256:r29wTDuG7tzLvsyF4P06NSatzmc6dKh3dHWw3uGXs5w
rsa      SHA256:mWrPlIsu+ciWZH3iYUw1l3hEt8zQ5B3bpcBiqoIgoHo
ecdsa    SHA256:HF6v3Z3Ef9E4MDRyJTouFmV3JDnQdpbc7PPVpwN4VXs
```

Any party that obtains the private half of any one key from any
shipped Sovol unit can transparently impersonate every other shipped
unit. **Mitigation**: `flows.stock_keep` MUST run `sudo
dpkg-reconfigure openssh-server` (or equivalent) early — before the
user is asked to trust the fingerprint, and BEFORE any user
credential prompt happens over the SSH channel. Regenerating only
the ed25519 key is insufficient; the RSA and ECDSA fingerprints
remain identical across units and are equally usable for
impersonation.

## Network credentials on disk

`/etc/NetworkManager/system-connections/` on the audited Max held
**only the user's own networks plus `ZYIPTest`** — not the full set
of three factory-build PSKs the Zero ships with. Either Sovol's
factory-build process for the Max was cleaner (only `ZYIPTest` left
in place), or the user removed the others before the audit.
Detection / cleanup must tolerate **0 to 3** factory profiles.

| SSID | Notes |
|------|-------|
| `ZYIPTest` | Default placeholder PSK `12345678`. Same as the Zero's, written into `/boot/system.cfg` as `WIFI_SSID/WIFI_PASSWD`. Should be deleted on `stock_keep`. |
| `SPIXINETGEAR26` (PSK `Spixi2023`) | Possibly absent on Max. Was present on Zero (factory NetGear router). |
| `Spixi` (PSK `ZCSW$888`) | Possibly absent on Max. Was present on Zero (zhongchuang/Sovol contract-manufacturer test wifi). |

`/boot/system.cfg`'s `WIFI_SSID="ZYIPTest"` / `WIFI_PASSWD="12345678"`
should be cleared on `stock_keep` so `connect_wifi.sh` doesn't try
to reconnect to the factory test network on the next boot.

## udev rules

- `10-wifi-disable-powermanagement.rules` — Armbian standard.
- `50-usb-realtek-net.rules` — Armbian standard.
- `60-gpiod.rules` — `SUBSYSTEM=="gpio", KERNEL=="gpiochip[0-4]",
  GROUP="biqu", MODE="0660"`. **Bug**: the `biqu` group does not
  exist on this image. Same as Zero. Rule fails silently.
- `70-ttyusb.rules` — sets all `ttyUSB*`, `ttyACM*`, `ttySTM*`,
  `ttyS*` to mode `0666`. **Wide-open serial devices on the LAN**.
  Tighten to `dialout` group.
- `/lib/udev/rules.d/60-usbmount.rules` — vendor automount rule
  (kernel `sd[a-z]*` → `systemctl restart
  makerbase-automount@%k.service`).

## apt sources

`/etc/apt/sources.list` is `deb.debian.org` for Bullseye main +
updates + security, but **`bullseye-backports` is commented out**
on the Max (the Zero has it enabled). If any Deckhand step relies
on a backports package being installable without first editing
sources.list, it'll fail on the Max.

`/etc/apt/sources.list.d/nodesource.list` adds Node 22 from the
NodeSource APT repo — **Max-only**, likely a build dep for
`zhongchuang_klipper`.

`dpkg -l | grep -iE 'sovol|sv08|update.{0,3}packge'` returns
**nothing on the Max**. The Sovol Zero ships an
`sv08mini-update-packge` debian package that owns key system files
(`/etc/network/interfaces.d/can0`,
`/etc/systemd/system/wifi_server.service`, etc.); on the Max those
files exist on disk but are not owned by any package (Sovol copied
them directly during factory build, not via `dpkg -i`).

## Files of concern (security / privacy)

| Item | Severity | Action |
|------|----------|--------|
| `wifi_server.py` exposing `/command` to the LAN as root | **Critical** | Disable `wifi_server.service` and remove or sandbox the script. |
| Pre-shared SSH host keys (all three) shared across all units | High | Regenerate all three before any user-visible action. |
| `connect_wifi.sh` still has `connectUSBWifi()` defined (commented call) | Medium (physical access) | Either disable `connect_wifi.sh` entirely after first wifi or guard the function. |
| `WIFI_SSID/WIFI_PASSWD` in `/boot/system.cfg` (cleartext) | Medium (privacy) | Clear on `stock_keep`. |
| Factory wifi PSKs still in `/etc/NetworkManager/system-connections/` (count varies on Max — only `ZYIPTest` confirmed) | High (privacy) | Delete the factory profiles on `stock_keep`. |
| `iptables` empty (no firewall) | Low–Medium | Optional — surface a wizard step. |
| `70-ttyusb.rules` makes `ttyS*` world-writable | Low | Tighten to `dialout` group. |
| `60-gpiod.rules` references non-existent `biqu` group | Low | Cleanup tier. |
| OTA does MD5-only verification (when invoked) | Low | OTA daemon isn't running at boot on Max anyway; non-issue unless re-enabled. |
| `~/ttyS3.py` developer-leftover | Low | Cleanup tier. |
| `~/众创klipper.tft.bak` closed TFT firmware | Vendor blob | Keep — required for re-flashing the TFT panel. |
| `/root/klipper.bin` outside the flasher's expected search path | Low (operational) | Document the path; do not relocate without testing. |

## Summary of what's new vs the Sovol Zero

The SV08 Max shares the Sovol Zero's base SPI-XI image, default
credentials, pre-shared SSH host keys, `wifi_server.py` LAN RCE,
moonraker-obico phone-home, `/boot/scripts/` orchestrator skeleton,
deterministic CAN UUIDs, and Klipper fork. The genuine differences:

1. **Hardware scale**: ~500×505×505 build volume (vs Zero's
   ~155×152×155), 4-Z quad-gantry (vs 1-Z), TMC5160 X/Y at 3.0 A
   (vs 3.5 A), dual part-cooling fans (vs single), filament
   switch + motion encoder (vs switch only).
2. **Mainboard revision**: `H616_JC_6Z_5160_V1.2` (vs `_3Z_`).
3. **Serial TFT touchscreen** driven by the open-source
   `zhongchuang_klipper` C++ daemon — Sovol's mksclient
   derivative with `sovol_http.cpp` for OTA progress UI. Closed
   `众创klipper.tft.bak` panel firmware blob accompanies it.
   The Zero has no equivalent; it uses a small UC1701 LCD driven
   directly by Klipper.
4. **Optional HDMI screen**: KlipperScreen renders to fbdev on
   tty7 with the typo'd `01-dbbian-defaults.conf` Xorg fragment.
   Functional whether a display is attached or not.
5. **OTA disabled at boot**: `btt_init.sh` has the `ota_service.sh`
   launch line commented out on the Max. `_OTA` macro is wired
   but inert. Zero runs the daemon by default.
6. **Factory build artifacts at `/root/`**: `/root/klipper.bin`
   (presumed main MCU firmware, sized like an STM32H750 application)
   and `/root/mcu_update.sh`. The Zero's `/root/` is essentially
   empty.
7. **No Sovol vendor dpkg package** on the Max. Factory provisioning
   was done by hand (per `/root/.bash_history`). The Zero ships
   `sv08mini-update-packge` that owns key system files.
8. **`bullseye-backports` is commented out** in `/etc/apt/sources.list`
   on the Max (enabled on Zero). NodeSource Node 22 repo is added
   on the Max (not on Zero).
9. **Heater section name**: chamber_hot.cfg uses `[heater_generic
   chamber_temp]` on the Max, `[heater_generic chamber_heater]` on
   the Zero. M141/M191 macros wire to the local name; cross-printer
   macro libraries must parameterize.
10. **Chamber max_temp**: 65 °C on Max vs 70 °C on Zero (small spec
    delta).
11. **Web UIs**: Mainsail AND Fluidd both present on the Max
    (Mainsail active); Mainsail-only on the Zero.
12. **Factory wifi PSK count**: only `ZYIPTest` confirmed on Max;
    Zero ships `SPIXINETGEAR26` + `Spixi` + `ZYIPTest`. Detection
    must tolerate 0–3.
