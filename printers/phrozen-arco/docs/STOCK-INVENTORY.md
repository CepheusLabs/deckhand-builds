# Stock Phrozen Arco — Full Inventory

Complete inventory of everything Phrozen/MKS ships on a stock Arco that our
replacement process needs to be aware of. Derived from a **live eMMC survey**
(USB-attached, read-only mount via `wsl --mount` / `usbipd-win`) plus the
repo's prior artifacts and a `/home/mks/` capture. This is the audit we work
from when deciding what to keep, stub, replace, or remove.

> **Note on this unit:** the surveyed eMMC has already had our setup.sh run on
> it — so `arco-screen.service` is present, `/usr/local/bin/python3.11` is
> installed, `/etc/apt/sources.list` has been switched from `mirrors.aliyun.com`
> to `archive.debian.org`, and `klipper.env.stock` exists under
> `printer_data/systemd/`. These are **our additions**, not factory stock.
> Everything else in this document is factory Phrozen/MKS.

## Boot sequence on stock

There are **two independent boot hooks** that start Phrozen/MKS processes:

### 1. `makerbase-client.service` (systemd, `Restart=always`)

Runs `bash /root/phrozen/start.sh` on boot, which launches
`/root/phrozen/build/mksclient` — a **C++ application that IS an alternative
screen daemon** (not `voronFDM`). It opens `/dev/ttyS1` at 115200 baud to talk
to the TJC touchscreen and connects to `ws://localhost:7125/websocket` for
Moonraker. Full source at `/root/phrozen/` (websocket_client, process_messages,
mks_file, mks_serial, refreshui, etc.). **Purpose: MKS-branded SKUs use
`mksclient`; Phrozen-branded SKUs use `voronFDM`.** KlipperScreen-start.sh
stops `makerbase-client.service` so voronFDM can claim `/dev/ttyS1`.

### 2. `KlipperScreen.service` → `KlipperScreen-start.sh`

Standard KlipperScreen launcher, but Phrozen **replaces** the stock
`KlipperScreen-start.sh` with a heavily-modified version that:

1. Stops `makerbase-client.service` (disables mksclient so voronFDM can run)
2. `chmod -R 777` on `phrozen_dev/`, `hdlDat/`, `phrozen_dev/serial-screen/`
3. `rm -rf ~/moonraker-obico` + `~/moonraker-obico-env` (actively deletes Obico every boot)
4. Launches `phrozen_master` in background (HDL Zigbee gateway + UDS + flash relay)
5. Launches `voronFDM` in background (TJC screen daemon)
6. Launches `frpc_script &` (reverse tunnel — port-mapped from MAC address)
7. `ntpdate ntp1.aliyun.com &` (Chinese NTP, redundant with enabled chrony/ntp)
8. Infinite `sleep 1` loop (KlipperScreen service expects the script not to exit)

### Also enabled in multi-user.target.wants (beyond standard Armbian)

- `KlipperScreen.service`
- `makerbase-auto-fresh.service` (oneshot, `/root/auto_refresh` binary — no network indicators found)
- `makerbase-byid.service` (oneshot, `/root/mks-id.sh` — patches MKS_THR.cfg serial path dynamically)
- `makerbase-client.service` (mksclient, see above)
- `makerbase-net-mods.service` (oneshot — copies `wpa_supplicant-wlan0.conf` from a USB stick into `/etc/wpa_supplicant/` on boot, then unblocks rfkill wifi)
- `makerbase-shutdown.service` (oneshot — GPIO85/GPIO80 soft-shutdown button handler)
- `makerbase-udp.service` (oneshot — `/root/udp_server` binary, LAN discovery/file-upload)
- `makerbase-wlan0.service` (wpa_supplicant for wlan0)
- `moonraker-obico.service` (enabled but deleted each boot by KlipperScreen-start.sh — dead loop)
- `openvpn.service` (enabled but no configs in `/etc/openvpn/` — dormant)
- `nginx.service` (serves fluidd + mainsail)
- `chrony.service` + `chronyd.service` + `ntp.service` (**three conflicting time-sync services** enabled)
- `unattended-upgrades.service`
- `rsync.service`, `sysstat.service`, `smartd.service`, `vnstat.service`
- `klipper.service`, `klipper-mcu.service`, `moonraker.service`, `crowsnest.service` (standard stack)

## Phrozen / MKS binaries

### In `~/klipper/klippy/extras/phrozen_dev/` (AMS module tree)

| Binary | Roles | Keep strategy |
|--------|-------|--------------|
| `frp-oms/phrozen_master` | (a) HDL Zigbee cloud gateway (phones home), (b) UDS at `/tmp/UNIX.domain` for voronFDM, (c) serial relay during ChromaKit flashing | Kill daemon; retain binary in `firmware/tools/` for flash-time use; stub UDS when screen=voronFDM |
| `frp-oms/phrozen_master-arm-prz` | Variant build (Phrozen SKU) | Remove if unused |
| `frp-oms/phrozen_slave_ota` | (a) Receives OTA pushes from Phrozen cloud, (b) the actual flash tool used by `flash-chromakit.sh` | Kill; retain binary for flash-time use |
| `frp-oms/frp/frpc` | FRP reverse tunnel client | Remove |
| `frp-oms/frp/frpc_script` | Shell wrapper — derives tunnel ports from eth0/wlan0 MACs, generates `frpc.ini`, supervises frpc | Remove |
| `serial-screen/ota_control` | Coordinates OTA across screen/AMS/SBC | Remove |
| `serial-screen/voronFDM` | TJC touchscreen daemon (Nextion on `/dev/ttyS1`) — Phrozen SKU | Keep (with stub) OR replace with `arco_screen` (user choice) |
| `serial-screen/voronFDM-arm-mks` | MKS SKU variant | Remove if unused |
| `serial-screen/voronFDM-arm-prz` | Phrozen SKU variant | Remove if unused |

### In `/root/` (MKS system-root binaries — **NOT** in our prior docs)

| Binary | Launched by | Purpose |
|--------|-------------|---------|
| `/root/phrozen/build/mksclient` | `makerbase-client.service` → `/root/phrozen/start.sh` | **MKS SKU screen daemon** (C++ alternative to voronFDM). Source in `/root/phrozen/src/*.cpp` (20 files, ~300KB of C++). Talks to Moonraker at `ws://localhost:7125/websocket` and TJC screen on `/dev/ttyS1`. |
| `/root/auto_refresh` | `makerbase-auto-fresh.service` | 9KB ARM binary. `strings` scan shows no network indicators. Likely a Klipper restart/sanity probe. |
| `/root/udp_server` | `makerbase-udp.service` | 20KB binary, embeds a HTTP server (`wz simple httpd 1.0`). Handles `GET /printer/dev_name` and saves uploaded files to `~/printer_data/gcodes/USB/`. **LAN discovery + file-upload service for MKS slicer/phone app.** No auth. |
| `/usr/bin/makerbase-automount` | `makerbase-automount@.service` (template) | Auto-mounts USB sticks per fstype configs in `/etc/makerbase-automount.d/{auto,vfat,ntfs,hfsplus}` |
| `/root/mks-id.sh` | `makerbase-byid.service` | Rewrites `serial:` line in `~/printer_data/config/MKS_THR.cfg` to current `/dev/serial/by-id/*`. Also `rm -f printer-*.cfg`. |
| `/root/soft_shutdown.sh` | `makerbase-shutdown.service` | GPIO monitor: exports GPIO80 (input) + GPIO85 (output), polls 100Hz, triggers `shutdown -h now` when button pressed. Hardware feature, not phone-home. |
| `/root/auto_update.cpp` (source) | — (built binary path unclear) | USB-stick firmware update: waits for `~/printer_data/gcodes/USB/armbian-update.deb`, `dpkg -i`'s it, optionally reboots. Requires physical USB access. |

### Phone-home code in `mksclient` (dormant)

Source review of `/root/phrozen/src/mks_file.cpp` shows a `find_update_package()`
/ `get_lastest_version()` path that fetches
`https://gitee.com/kenneth_lin/kenpine-tv/raw/master/test.txt` (Gitee = Chinese
GitHub, `kenneth_lin` developer account, `kenpine-tv` project name is
unrelated — likely repurposed). These calls are **commented out in `main.cpp`**,
so they don't run in the current build. Flag as dormant phone-home capability
that could be re-enabled silently in a future MKS update.

The only other URL in the codebase is `http://makerbase.com/test` used as the
`url` metadata field in the Moonraker `server.connection.identify` handshake
(not an actual HTTP request target).

### `/root/phrozen/` project tree (ships the mksclient source)

```
/root/phrozen/
├── .git/                              # Full git history
├── main.cpp, src/*.cpp, include/*.h   # mksclient source
├── build/mksclient                    # Built binary (launched by start.sh)
├── libwpa_client.so, wpa_ctrl.h       # Bundled wpa_supplicant library
├── MKSDEB/                            # Debian packaging metadata
├── PHROZEN_APP.deb                    # Distributable package
├── start.sh, debug_intall.sh, etc.    # Lifecycle scripts
├── makerbase-client.service           # Unit file (installed to /lib/systemd)
├── rk3328-roc-cc.dts                  # Device tree source (matches /root/)
├── others/                            # Contains stock Klipper extruder.py + heater_bed.py (override reference)
└── udisk/                             # Empty directory
```

## Data / config files

### `~/hdlDat/` (29 files) and `/etc/hdlDat/` (27 files) — **replicated in two places**

Both contain HDL Zigbee gateway state including `rsa_priv.txt` (**plaintext
RSA private key**). `/etc/hdlDat/` additionally has `hdlDriverID.dat` that's
not in `~/hdlDat/`. Only needed if `phrozen_master` runs as the Zigbee
gateway. Safe to purge when Zigbee is dropped. `/etc/hdl/` exists as an
empty placeholder directory.

Notable files (superset of both locations):
- `rsa_priv.txt` — **plaintext RSA private key (security liability)**
- `NVImage.bin` — Zigbee coordinator firmware (148KB)
- `ZbGwId.dat` — gateway ID / device MAC
- `HttpsNewLoginUrl`, `HttpsNewLoginRspGatewayId` — HDL cloud login endpoints
- `Phrozen_Dev.json` — device registration
- `doorlockUserInfoFile.dat` — door-lock user table (irrelevant to 3D printer)
- `ZbCoordinatorDebug.log` — 80KB debug log
- `ZbGw*.dat` — Zigbee device/group/binding/scene/zone/logic tables
- `DriveCodeFile.dat`, `hdlDatSTM32SerialPortVirtualDriverDriverID.dat`, `hdlDriverID.dat`

### `~/phrozen_dir/`

- `phrozen_install.sh` — Phrozen's first-boot install script (copies files around, bootstraps phrozen_dev)

### Home-directory scripts and flag files

| File | Purpose |
|------|---------|
| `~/update.sh` | Installs `ELEGOO_APP.deb` from SD card (`gcode_files/sda1/ELEGOO_UPDATE_DIR/ELEGOO_APP.deb`) — **Elegoo branding suggests shared OEM lineage** |
| `~/update_moonraker.sh` | Moonraker update stub |
| `~/plr.sh` | Power-loss recovery gcode generator (reads saved_variables, writes resume.gcode) |
| `~/clear_plr.sh` | Clear PLR state |
| `~/cache_cleaned`, `~/fix_ready`, `~/moonraker_updated` | Install-once sentinel flags |
| `~/LinuxVersionInfo` | Empty marker |
| `~/udo systemctl restart crowsnest`, `~/ystemctl status chronyd` | **Accidental typo-files** — shell redirect mistakes saved as filenames. Harmless but messy. |

### Phrozen-adjacent home directories

- `~/printer_file/gcodes/` — non-standard gcode staging
- `~/hdl/` — empty placeholder
- `~/demo/` — empty
- `~/kiauh/`, `~/kiauh-backups/`, `~/.kiauh.ini` — KIAUH installed (possibly used during factory build)
- `~/printer_data/config/moonraker-obico.cfg`, `moonraker-obico-update.cfg` — Obico configs present but boot script deletes the venv each time
- `~/printer_data/systemd/klipper.env.stock` — **our** setup.sh wrote this (rollback file); not on factory stock

## System-level files and modifications

### `/etc/` findings

| Path | Status | Notes |
|------|--------|-------|
| `/etc/hostname` | `mkspi` | MKS branding |
| `/etc/hosts` | `127.0.1.1 mkspi` + `::1 ... mkspi` | Hostname-only, no cloud pinnings |
| `/etc/issue` | `Armbian 22.05.0-trunk Buster` | OS identity |
| `/etc/apt/sources.list` | currently `archive.debian.org` (Buster is EOL) — **was `mirrors.aliyun.com` per bash history, we switched it** | Factory-stock uses Chinese mirror |
| `/etc/apt/sources.list.d/` | `armbian.list` only | Standard |
| `/etc/chrony/chrony.conf` | `pool 2.debian.pool.ntp.org` (standard) | But `ntpdate ntp1.aliyun.com` also fires from KlipperScreen-start.sh |
| `/etc/ntp.conf` | standard pool | Coexists with chrony (conflict) |
| `/etc/openvpn/` | only the default `update-resolv-conf` script | Service enabled but no configs — dormant |
| `/etc/nginx/sites-enabled/` | `fluidd`, `mainsail` | Standard dual web UI |
| `/etc/wpa_supplicant/` | `wpa_supplicant-wlan0.conf` + `.bak` | Standard |
| `/etc/makerbase-automount.d/` | `auto`, `hfsplus`, `ntfs`, `vfat` configs | Per-fstype USB mount behavior |
| `/etc/hdl/` | empty directory | Placeholder |
| `/etc/hdlDat/` | **second copy of HDL Zigbee data** | Duplicate of `~/hdlDat/` + `hdlDriverID.dat` |
| `/etc/cron.d/` | `armbian-truncate-logs`, `armbian-updates`, `sysstat` | Standard — **no Phrozen cron entries** |
| `/etc/rc.local` | `exit 0` | Empty — unused |
| `/etc/profile.d/` | standard Armbian only | No Phrozen drop-ins |
| `/etc/sudoers.d/` | `README` (Armbian) + `arco-screen` (**our addition**) | No Phrozen sudo rules |

### `/usr/local/`

- `/usr/local/bin/`:
  - **`python3.11` + symlinks, `pip3`, `pydoc3`, `idle3`, `2to3`** — Python 3.11 install (**ours**, from setup.sh)
  - `klipper_mcu` — standard Klipper host MCU binary
  - `crowsnest`, `mjpg_streamer`, `input_*.so`, `output_*.so` — symlinks to `~/mks/mjpg-streamer/` (standard stack)
- `/usr/local/sbin/` — empty
- `/opt/` — empty

### `/root/` (root-owned directory, contains most load-bearing MKS code)

- Full `phrozen/` C++ project tree (see mksclient section above)
- Binaries: `auto_refresh`, `udp_server`
- Scripts: `mks-id.sh`, `soft_shutdown.sh`, `fix-service.sh` (empty)
- `core` — 34MB core dump from a past crash (leftover artifact)
- `rk3328-roc-cc.dts` + `.dtb` — device tree for RK3328 board
- No `.ssh/` directory — **no root-level backdoor keys**

### Users and access

- `/etc/passwd`: `root` (bash login), `mks` (uid 1000, bash login), plus `nm-openvpn` and `vnstat` service accounts. **No extra Phrozen accounts.**
- `/home/mks/.ssh/authorized_keys`: contains only the user's own key (this unit has already been SSH'd into with user key). Factory-stock state of this file unverified.
- `/etc/sudoers.d/`: no Phrozen rules.

## Network indicators (phone-home endpoints)

| Host / IP | Who uses it | Port | Active? |
|-----------|-------------|------|---------|
| `42.193.239.84` | frpc tunnel (Phrozen) | 7000 | Active |
| `global.hdlcontrol.com` | phrozen_master (HDL API) | 443 | Active when phrozen_master runs |
| `china-gateway.hdlcontrol.com` | phrozen_master (HDL China) | 443 | Active when phrozen_master runs |
| `42.193.239.84` | phrozen_master (HTTPS) | 8080 | Active when phrozen_master runs |
| HDL MQTT broker (dynamic) | phrozen_master | dynamic | Active when phrozen_master runs |
| `ntp1.aliyun.com` | KlipperScreen-start.sh `ntpdate` | 123 | Active on every boot |
| `mirrors.aliyun.com` | apt (factory sources.list) | 80/443 | Active on `apt update` until switched |
| `gitee.com/kenneth_lin/kenpine-tv` | mksclient `find_update_package` | 443 | **Dormant** — compiled in but commented out in main() |

## Local-LAN attack surface (non-phone-home but exposed)

- `udp_server` runs a `wz simple httpd 1.0` and accepts `GET /printer/dev_name` + file uploads into `~/printer_data/gcodes/USB/`. **No authentication.**
- Moonraker `trusted_clients` allows `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16` — any LAN client can print, flash, or modify config without auth.
- `voronFDM` expects the `/tmp/UNIX.domain` UDS — our stub handles this.
- `makerbase-net-mods.service` copies any `wpa_supplicant-wlan0.conf` from a USB stick at boot. **Physical USB insert = wifi takeover on reboot.**

## Action matrix (to be finalized with flag design)

| Item | Keep (no-op) | Stub / replace | Remove |
|------|---|---|---|
| `phrozen_master` daemon | — | stub when screen=voronFDM | when screen=arco_screen or mksclient |
| `phrozen_master` binary on disk | keep for flash use | — | cleanup tier |
| `phrozen_slave_ota` daemon | — | — | always (replace with OSS updater eventually) |
| `phrozen_slave_ota` binary | keep for flash use | — | cleanup tier |
| `ota_control` | — | — | always |
| `frpc` / `frpc_script` | — | — | **always (security)** |
| `voronFDM` | when screen=voronFDM | — | when screen=arco_screen or mksclient |
| `mksclient` (`makerbase-client.service`) | when screen=mksclient (new option!) | — | when screen=voronFDM or arco_screen |
| `makerbase-client.service` unit | keep | — | remove on OSS path |
| `makerbase-udp.service` (`udp_server`) | keep — local MKS slicer/app | replace with authenticated equivalent | if LAN attack surface matters |
| `makerbase-auto-fresh.service` | keep (low-risk oneshot) | — | cleanup tier |
| `makerbase-byid.service` (`mks-id.sh`) | keep | replace with symlink rule | cleanup tier |
| `makerbase-shutdown.service` | **keep (hardware power button)** | — | never — physical feature |
| `makerbase-net-mods.service` | **review** — USB-based wifi provisioning is a feature for some, risk for others | disable after initial provisioning | OSS path |
| `makerbase-automount@.service` | keep (USB mount for prints/updates) | — | OSS path optional |
| `makerbase-wlan0.service` | keep | — | — |
| `~/hdlDat/` | keep if Zigbee kept | — | default (rsa_priv.txt minimum) |
| `/etc/hdlDat/` (duplicate) | keep if Zigbee kept | — | default |
| `rsa_priv.txt` (both copies) | — | — | **always (security)** |
| `moonraker-obico.service` | — | — | always (dead loop with rm) |
| `openvpn.service` | — | — | always (dormant, no configs) |
| aliyun NTP call | — | switch to pool.ntp.org | remove entire line |
| `mirrors.aliyun.com` apt pinning | — | switch to archive.debian.org / deb.debian.org | always |
| Redundant `ntp` + `chronyd` | — | pick one (chrony), disable others | — |
| `~/update.sh` (Elegoo .deb installer) | — | — | always |
| `~/moonraker-obico*` rm loop in KS-start | — | — | remove from boot script |
| `~/phrozen_dir/` | — | — | cleanup tier |
| Typo-files (`udo systemctl...`, etc.) | — | — | cleanup tier |
| Dated `.txt` notes in phrozen_dev | — | — | cleanup tier |
| `cmds-240226.py` (old extras) | — | — | cleanup tier |
| `/root/core` (34MB crash dump) | — | — | cleanup tier |
| Default user password (`makerbase`) | — | **force change on first setup** | — |
| Moonraker `trusted_clients` LAN-open | — | tighten to user-specified CIDRs | — |

## Summary of what's new beyond the repo's prior docs

1. **`mksclient` screen daemon (C++)** is a third option alongside `voronFDM` and `arco_screen`. Source is on-disk, no phone-home in currently-built code path. Adds a documented "keep stock MKS screen" option.
2. **Nine `makerbase-*` systemd services** (we tracked only one). Most are local-only and legitimate (GPIO power button, USB auto-mount, MKS_THR serial fix). `makerbase-udp.service` and `makerbase-net-mods.service` are the two to think carefully about.
3. **Duplicated HDL Zigbee data at `/etc/hdlDat/`** — not just `~/hdlDat/`. Includes duplicated `rsa_priv.txt`.
4. **Dormant Gitee phone-home** in mksclient (compiled in but commented out of main()). Flag as a future risk.
5. **Three conflicting time-sync services** enabled: chrony + chronyd + ntp, plus manual `ntpdate aliyun` from KlipperScreen-start.sh. Chrony alone is correct.
6. **OpenVPN enabled but empty config** — dormant, harmless, but flagged.
7. **`makerbase-net-mods.service`** copies wifi creds from any USB stick at boot — physical-access wifi takeover vector.
8. **`udp_server`** is a LAN-only unauth HTTP+UDP service (MKS slicer/phone app bridge), not phone-home but an attack surface.
9. **No SSH backdoor keys** on this unit; `/root/.ssh` doesn't exist. No Phrozen accounts in `/etc/passwd`. No Phrozen `sudoers.d` rules. No `/opt/` contents.
10. **Elegoo rebrand lineage confirmed** — `~/update.sh` expects `ELEGOO_APP.deb`.
