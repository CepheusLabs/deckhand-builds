# SV08 Max ↔ Sovol Zero alignment notes

Cross-reference between the live audit of the Sovol SV08 Max
(`192.168.0.121`, performed 2026-05-01) and the parallel Sovol Zero
audit at `printers/sovol-zero/docs/STOCK-INVENTORY.md`. Written so the
Zero-side session can integrate SV08 Max findings without re-running
the audit.

Raw probe dumps for the SV08 Max are in
`installer/.audits/sovol-sv08-max-20260501/` (out-of-repo by default to
keep raw data — including any captured wifi PSKs — off the published
deckhand-builds repo). Three rounds: `probe_clean.txt`, `probe2.txt`,
`probe3.txt`, plus the working `FINDINGS.md` synthesizing them.

## SV08 Max identity (summary)

| Field | Value |
|-------|-------|
| Hostname | `SPI-XI` |
| Distro | Debian 11 Bullseye, rebranded `SPI-XI 2.3.3 Bullseye` |
| Kernel | `5.16.17-sun50iw9 #2.3.3` |
| SBC | BigTreeTech CB1 (`/proc/device-tree/model`) |
| SoC | Allwinner H616 |
| `board_model` (per `moonraker-obico.cfg [meta]`) | `H616_JC_6Z_5160_V1.2` (vs Zero `H616_JC_3Z_5160_V1.2`) |
| `printer_model` (per `[meta]`) | `SOVOL SV08 MAX` |
| eMMC | `mmcblk2`, ~32 GB |
| Build volume | ~500 × 505 × 505 mm (CoreXY, **4-Z quad-gantry**) |
| X/Y drivers | TMC5160 SPI @ **3.0 A** (Zero: 3.5 A) |
| Z motors | 4 × TMC2209 UART, gear ratio 80:12 |
| Probe | `probe_eddy_current` via LDC1612 on `extra_mcu` (same as Zero) |
| Accelerometer | LIS2DW on `extra_mcu` |
| Web UIs installed | **Mainsail AND Fluidd** (Zero: Mainsail only). Mainsail is active. |

## Stack converges (lift directly from Zero's STOCK-INVENTORY)

Verified identical on the SV08 Max:

- BTT CB1 / Allwinner H616 / sun50iw9 kernel / `SPI-XI 2.3.3 Bullseye`
  image / hostname `SPI-XI`.
- Default `sovol`/`sovol`. `%sovol ALL=(ALL) NOPASSWD: ALL` in
  `/etc/sudoers`.
- All 3 SSH host keys factory-baked from `chris-virtual-machine`:
  - ed25519 `SHA256:r29wTDuG7tzLvsyF4P06NSatzmc6dKh3dHWw3uGXs5w`
  - rsa     `SHA256:mWrPlIsu+ciWZH3iYUw1l3hEt8zQ5B3bpcBiqoIgoHo`
  - ecdsa   `SHA256:HF6v3Z3Ef9E4MDRyJTouFmV3JDnQdpbc7PPVpwN4VXs`
  Cross-printer impersonation is real and lives across the entire
  SPI-XI image lineage. Profile must regenerate host keys before any
  fingerprint-trust prompt on `stock_keep`.
- `/etc/rc.local` runs `chmod +x /boot/scripts/*; /boot/scripts/btt_init.sh`.
  Same `/boot/scripts/` set: `btt_init.sh`, `connect_wifi.sh`,
  `file_change_save.sh`, `system_cfg.sh`, `ota_service.sh`,
  `auto_setmcu_id.sh`, `extend_fs.sh`, `sync.sh`, `auto_brightness`,
  `set_rgb`, `mp3/`, `sound.sh`, `vibration.sh`, `vibrationsound.sh`,
  `wifi.log`. Same `/boot/system.cfg` template
  (`WIFI_SSID="ZYIPTest"`/`WIFI_PASSWD="12345678"` defaults plus the
  `BTT_PAD7`/`TOUCH_VIBRATION`/`TOUCH_SOUND`/`AUTO_BRIGHTNESS` toggles).
- `wifi_server.service` running as **root on 0.0.0.0:5000** with the
  same trivially-escapable `/command` endpoint
  (`subprocess.run(cmd, shell=True)` after a weak `startswith` filter,
  plus `/connect_wifi` doing `f"nmcli device wifi connect '{ssid}' password '{password}'"`).
  Same security finding, same severity.
- `moonraker-obico.service` enabled by default, talks to `app.obico.io`
  continuously. Same opt-out story.
- All MCUs on can0, 1 Mbit, `gs_usb` USB bridge `1d50:606f` (NOT the
  `614e` ID seen in the build configs — those are aspirational).
- **All 3 MCU CAN UUIDs are byte-identical to the Zero's**:
  - `[mcu]` main = `0d1445047cdd`
  - `[mcu extra_mcu]` toolhead = `61755fe321ac` (Zero calls this
    `extruder_mcu`)
  - `[mcu hot_mcu]` chamber (in `chamber_hot.cfg`) = `58a72bb93aa4`
  Sovol uses **deterministic CAN UUIDs by chip role across the entire
  SPI-XI line**. Two of these printers on the same CAN bus would
  collide. Profile detection has to allow for this — UUIDs are NOT
  per-unit identifiers.
- `~/printer_data/build/` flash tooling: `flash_can.py` (Eric
  Callahan's Katapult/CanBoot uploader), `mcu_update_fw.sh`,
  `extruder_mcu_update_fw.sh`, `extra_mcu_update_fw.sh`. The four
  scripts converge. **The .bin-blob situation does NOT converge** —
  see divergence list below.
- Sovol Klipper fork. Origin `http://192.168.1.233/root/klipper.git`.
  Same custom extras (`z_offset_calibration.py` Sovol-original;
  modified `probe_eddy_current.py` / `probe_pressure.py` /
  `ldc1612.py` / `lis2dw.py` / `bed_mesh.py` / `fan.py` /
  `homing.py` / `shaper_calibrate.py`).
- Moonraker is upstream (no Sovol modifications). KIAUH installed.
- iptables / ip6tables empty (default ACCEPT). `/etc/hosts` clean.
- apt sources are `deb.debian.org` only (no aliyun mirrors). udev
  quirks identical (`60-gpiod.rules` references nonexistent `biqu`
  group, `70-ttyusb.rules` makes `ttyS*` mode 0666). The exact set of
  enabled bullseye components differs — see divergence list.
- chamber_hot.cfg layout: `[mcu hot_mcu]` + a watermark-controlled
  `[heater_generic <NAME>]` on `hot_mcu:PA0` heater + `hot_mcu:PA5`
  thermistor, plus `M141`/`M191` macros and `[delayed_gcode check_chamber]`
  poller. **The heater section name differs** — see divergence list.
- Comgrow OTA endpoint `https://www.comgrow.com/files/printer/ver.json`
  with MD5-only verification (when invoked). Note that on the Max the
  daemon isn't actually started at boot — see divergence list.

## SV08 Max diverges from the Zero

These need SV08-Max-specific entries; do NOT lift from the Zero:

> **Corrections from the Zero session (2026-05-01)**: items 11–15
> below were originally in the convergence list but the Zero session
> caught the mismatch on cross-reference. Folded in here.

1. **`btt_init.sh` has `ota_service.sh` COMMENTED OUT** on the Max:
   ```
   #sudo -u sovol ./ota_service.sh &
   ```
   The Max does **not** run the OTA daemon at boot. The `_OTA` macro
   (which sends `SIGUSR1`) has no target — Comgrow OTA flow is
   non-functional out of the box on the Max. Sovol deliberately
   disabled it for this SKU.

2. **No Sovol vendor dpkg package** on the Max.
   `dpkg -l | grep -E 'sovol|sv08|update.{0,3}packge'` returns nothing.
   The Zero ships `sv08mini-update-packge`; the Max has no equivalent.
   Factory provisioning happened via shell scripts and direct file
   copies (per `/root/.bash_history`), not via dpkg. The typo'd file
   `01-dbbian-defaults.conf` exists on disk but isn't owned by any
   package on the Max.

3. **`/root/` is NOT empty** on the Max (Zero's was bare):
   - `/root/klipper.bin` (28.9 KB, sovol-owned) — **plausibly the main
     MCU firmware blob the Zero session noted as missing**. Same size
     as Klipper application firmware on F103xe. Hasn't been confirmed
     with `file` yet.
   - `/root/mcu_update.sh` (1.2 KB, sovol-owned) — flash helper.
   - `/root/.bash_history` shows the factory build trail:
     `cd zhongchuang/build/; make; ./builddeb.sh; cd ../patch/; ./patch.sh; pip install flask; systemctl enable wifi_server.service; vi ../printer_data/build/.version.cfg`

4. **`zhongchuang_klipper` daemon — ACTIVE on the Max, ABSENT on the Zero**:
   - The Max has the SV08 Max's serial-TFT screen client, with full
     C++ source at `/home/sovol/zhongchuang/` and an 8.6 MB built ELF
     at `/home/sovol/zhongchuang/build/zhongchuang_klipper`.
     Internal git origin: `http://192.168.1.233/root/zhongchuang.git`.
     README explicitly identifies it as "SV08max serial screen client".
     Launched by `makerbase-client.service` →
     `/home/sovol/zhongchuang/build/start.sh` →
     `./zhongchuang_klipper localhost`.
   - On the Zero this directory does not run a daemon — the Zero uses
     the small UC1701 LCD with a knob, driven by Klipper's own
     `[display]` extras (with the `~/patch/menu.py`/`menu.cfg`/`display.cfg`
     overlay). No mksclient-derived daemon needed.
   - Mksclient family DNA: links against `boost_system`, `wpa_client`,
     `curl`. Sources cover `MoonrakerAPI.cpp`, `KlippyGcodes.cpp`,
     `KlippyRest.cpp`, `process_messages.cpp`, `refresh_ui.cpp`,
     `ui.cpp`, `MakerbasePanel.cpp`, `MakerbaseShell.cpp`,
     `MakerbaseSerial.cpp`, plus Sovol's own `sovol_http.cpp`
     (handles OTA progress UI on the TFT).

5. **Screen topology — clarified by the user**:
   - The SV08 Max ships with a **serial TFT touchscreen** (driven by
     `zhongchuang_klipper`) as the default/primary screen.
   - The CB1's HDMI port supports an optional KlipperScreen-style
     display — `KlipperScreen.service` is enabled and rendering to
     fbdev whether or not a monitor is plugged in.
   - On the audited unit, no HDMI display is connected; the TFT is the
     only active UI.
   - Profile `screens:` block needs two entries: the TFT (recommended,
     `bundled+vendor_blob` source kind, requires the closed `.tft`
     firmware) and the optional HDMI KlipperScreen
     (`stock_in_place`, no-op if no display is plugged in).

6. **NM connections** on the Max do NOT include the build-site PSKs
   the Zero had. Zero shipped with `SPIXINETGEAR26 / Spixi2023`,
   `Spixi / ZCSW$888`, `ZYIPTest / 12345678`. Max audit shows only
   `ZYIPTest` plus the user's own networks. Either Sovol cleaned up
   before shipping the Max or the user removed them. **Profile
   detection of factory PSKs needs to be tolerant of "0 to 3 present".**

7. **Chamber heater max_temp**: 65 °C on Max vs 70 °C on Zero (small
   spec delta, same MCU pinout).

8. **Extra apt source**:
   `/etc/apt/sources.list.d/nodesource.list` for Node 22 on the Max,
   not on the Zero. Likely a zhongchuang build dep.

9. **Web UIs**: SV08 Max ships with **both Mainsail AND Fluidd**
   installed (Mainsail is the active default per
   `[include mainsail.cfg]` and the nginx site).

10. **`mksclient`-naming collision**: on the Zero the Sovol stack does
    NOT include the `makerbase-client.service`/zhongchuang daemon; on
    the Max it DOES. The Phrozen Arco profile also has a
    `makerbase-client.service` entry (the MKS-Pi alternative screen
    daemon, kept disabled there). The three printers all encounter
    the "MKS makerbase-client lineage" but resolve it differently.
    Make sure cross-references in service-id space don't collide.

11. **`众创klipper.tft.bak`** (9.7 MB ZhongChuang TFT firmware blob)
    is **Max-only**. Zero has no serial-TFT touchscreen and no reason
    to ship the vendor blob. Tied to the zhongchuang_klipper daemon
    (item 4); same scope.

12. **`~/printer_data/build/` .bin-blob population differs**
    (originally claimed convergence — wrong):
    - **Zero**: `extruder_mcu_klipper.bin` (~31 KB, dated 2025-03-10)
      is **present**. `mcu_klipper.bin` and `extra_mcu_klipper.bin`
      are absent.
    - **Max**: NO .bin blobs at all in `~/printer_data/build/`. But
      `/root/klipper.bin` (~28.9 KB, sovol-owned) exists — see item 3.
    - Net: each unit ships exactly one MCU firmware blob on disk, but
      they target different MCUs (extruder on Zero, presumed-main on
      Max) and live in different locations. Profile flow that wants
      to flash any specific MCU has to be aware that the blob may not
      be on disk and may need to be sourced (via OTA on Zero, via
      whatever-the-vendor-does on Max).

13. **`~/printer_data/build/` factory markers** (originally claimed
    convergence — wrong):
    - **Max** has `.version.cfg` (14 B) and an empty `finishedGuide`
      sentinel.
    - **Zero** has neither.
    These are factory-build trail artifacts. Surface them on the Max
    profile as cleanup-tier or as identification hooks; not present
    on the Zero.

14. **Chamber heater section name in `chamber_hot.cfg`** (originally
    claimed convergence — wrong):
    - **Max**: `[heater_generic chamber_temp]` (gcode_id: C). M141 /
      M191 macros in chamber_hot.cfg target `chamber_temp`. Verified
      in probe3.txt:1371.
    - **Zero**: `[heater_generic chamber_heater]`. M141 / M191 target
      `chamber_heater`. Verified by Zero session in
      audit-followup.txt:766.
    The macro definitions in each printer's `Macro.cfg` /
    `chamber_hot.cfg` are wired to its local section name, so this is
    not just cosmetic — any cross-printer macro library has to know
    the right name per profile. **Profile field that surfaces the
    chamber heater name must be parameterized, not hardcoded.**

15. **apt sources `bullseye-backports`** (originally claimed
    convergence — wrong):
    - **Max**: `bullseye-backports` is **commented out** in
      `/etc/apt/sources.list`. So `apt install -t bullseye-backports
      ...` won't work without uncommenting first.
    - **Zero**: `bullseye-backports` is **enabled**.
    Matters if any Deckhand step relies on a backports package being
    installable without first editing sources.list.

## Things the Max session actually got right that the Zero session
   didn't initially surface (acknowledged from the Zero session's
   review, recorded so they don't get lost)

- All three SSH host keys (ed25519, rsa, ecdsa) are pre-shared from
  `chris-virtual-machine`, not just the ed25519. Three impersonation
  vectors per shipped unit, not one. Already reflected above.
- Deterministic CAN UUIDs across SKUs is a **CAN-bus collision
  vector** for users running two SPI-XI printers on the same bench.
  Already reflected above.
- `extruder_mcu` (Zero) vs `extra_mcu` (Max) for the same UUID
  `61755fe321ac` is a naming-only pivot (Sovol renamed the second
  MCU between SKUs), not a hardware divergence. Profile field for
  this MCU should resolve through the UUID, not the section name.

## Resolved decisions (2026-05-01)

**Raw audit dumps live OUT of `deckhand-builds/`.** Both sessions
agreed. Action: Zero session moves
`deckhand-builds/printers/sovol-zero/audit/{audit-raw.txt,audit-followup.txt,audit-followup-2.txt,audit-sovol-zero.sh}`
to `installer/.audits/sovol-zero-20260501/`. Max session's dumps
are already at `installer/.audits/sovol-sv08-max-20260501/`.
Curated docs (`docs/STOCK-INVENTORY.md`, `docs/ALIGNMENT-WITH-ZERO.md`),
`profile.yaml`, and `README.md` stay in-repo.

**SV08 Max profile.yaml drafting**: Max session takes it. Reasoning
from the Zero session: the Max session has direct access to the
probe dumps and read the actual file contents (Macro.cfg,
chamber_hot.cfg, makerbase-client.service unit, zhongchuang
sources), so it can produce verified field values rather than
working second-hand through the alignment doc. Zero session
reviews the resulting draft against `printers/sovol-zero/profile.yaml`
for structural and naming consistency.

## Background — the dump-location decision

**Where do raw audit dumps belong?**

Zero session put `audit/audit-raw.txt`, `audit/audit-followup.txt`,
`audit/audit-followup-2.txt`, `audit/audit-sovol-zero.sh` directly
under `printers/sovol-zero/audit/` (in-repo).

SV08 Max session put `probe.sh`, `probe.txt`, `probe2.sh`, `probe2.txt`,
`probe3.sh`, `probe3.txt`, `FINDINGS.md`, `ALIGNMENT-WITH-ZERO.md` at
`installer/.audits/sovol-sv08-max-20260501/` (out-of-repo).

The SV08 Max raw dumps contain the user's home wifi PSK in plaintext
(captured from `/etc/NetworkManager/system-connections/*` via
`sudo cat`). That alone is a strong argument for keeping raw dumps
out of `deckhand-builds/`. The Zero session's dumps may have similar
captures (factory PSKs at minimum, possibly the user's own networks
too if their unit had any saved).

Recommendation: **move raw probe dumps out of
`deckhand-builds/printers/sovol-zero/audit/`** into a sibling
out-of-repo location like `installer/.audits/sovol-zero-20260501/`
before the deckhand-builds repo gets pushed anywhere. The curated
`docs/STOCK-INVENTORY.md` and `profile.yaml` stay in-repo. If the
Zero session disagrees, please raise.

## Profile-drafting work split

Most of the SV08 Max's `profile.yaml` is going to be near-identical
to the Zero's, since the Sovol stack converges. The shared blocks are:

- `os` (distro, kernel, image_brand)
- `ssh` (default credentials, fingerprint_notes including the host-key
  pre-share warning)
- `identification.hostname_patterns` (`^SPI-XI(-\d+)?$`)
- `identification.config_file_contains` (the `printer_model:` regex —
  different value on the Max)
- `stock_os.detections` (most of them — adjust the
  `printer_model: SOVOL ZERO` regex to `SOVOL SV08 MAX`)
- `stock_os.services` for `wifi_server`, `moonraker_obico`,
  `connect_wifi`, `file_change_save`, `hostapd_vestigial`,
  `screen-cleanup` (all converged)
- `stock_os.files` for the factory wifi cleanups, `~/usbmount/`,
  `~/offline_lib/`, `~/patch/` cleanup-tier entries
- `mcus` (all 3 MCUs match exactly by UUID)

The SV08-Max-specific blocks are:

- `hardware.build_volume_mm`, `hardware.steppers` (X/Y current 3.0 A,
  4× Z), `hardware.features` additions for quad_gantry_level
- `compatible_with` (different SKU note, no `sv08mini-update-packge`)
- `screens` (the two-entry TFT + KlipperScreen-on-HDMI block)
- `addons` for `zhongchuang_klipper` if we surface it as a
  removable/replaceable component, plus the closed `.tft` firmware
  blob constraint
- `stock_os.services` with an extra entry for `makerbase-client`
  (zhongchuang launcher) and an absence/override for the
  `ota_service` entry (since Sovol commented it out in btt_init.sh,
  the wizard step shape is different — there's nothing to disable)
- `stock_os.files` with `/root/klipper.bin`, `/root/mcu_update.sh`,
  the `众创klipper.tft.bak` blob, and the `/etc/X11/xorg.conf.d/01-dbbian-defaults.conf`
  typo'd file as cleanup-tier
- `wizard.extra_steps` for the screen choice (TFT vs HDMI
  KlipperScreen), if we offer the user an explicit choice rather
  than auto-detecting from connected hardware

Either session can draft the SV08 Max profile.yaml — flag here who's
taking it.
