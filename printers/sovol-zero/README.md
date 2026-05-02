# Sovol Zero profile (alpha)

Both flows are wired:

| Flow | What it does |
|------|--------------|
| `stock_keep` | Security cleanup against the stock SPI-XI image. Optional firmware refresh / replacement (Sovol fork / upstream Klipper / Kalico). Klipper / Moonraker / your printer.cfg / saved bed mesh / gcode queue stay intact unless the user explicitly opts into firmware change. |
| `fresh_flash` | Flash a clean BigTreeTech CB1 V3.1.0 image to the eMMC over a USB adapter, layer the chosen Klipper variant, clone the stock Sovol printer.cfg / Macro.cfg / chamber_hot.cfg / plr.cfg / etc. from `github.com/Sovol3d/SOVOL-ZERO` at a pinned commit, install the standard Moonraker + Mainsail/Fluidd + KIAUH + Crowsnest stack, and build + katapult-flash the three MCU firmwares (main STM32H750, extruder + chamber STM32F103) over CAN. |

## stock_keep — what gets cleaned up

Wizard-driven via `apply_services` / `apply_files` against the
`stock_os.services` and `stock_os.files` declarations in
`profile.yaml` — the user can override any default per-item.
Defaults below.

| Change | Why |
|--------|-----|
| Mask `wifi_server.service` | Stock unit runs a Flask app as root on `0.0.0.0:5000` with an unauthenticated `/command` endpoint that escapes its weak prefix filter — **trivial LAN-side root RCE**. Mask (rather than just disable) so a future Sovol OTA can't silently bring it back. |
| Regenerate SSH host keys | Every shipped Sovol Zero (and SV08-line printer using the SPI-XI image) ships the same ed25519 / rsa / ecdsa key triple from a factory build VM (`root@chris-virtual-machine`). A MITM that obtains the private key from any one printer can impersonate every shipped unit until this runs. |
| Delete factory wifi profiles | Three NM profiles (`SPIXINETGEAR26`/`Spixi2023`, `Spixi`/`ZCSW$888`, `ZYIPTest`/`12345678`) ship in `/etc/NetworkManager/system-connections/` with plaintext PSKs. |
| Clear `WIFI_SSID`/`WIFI_PASSWD` in `/boot/system.cfg` | Cleartext copy of `ZYIPTest`/`12345678` on the FAT boot partition any user with a card reader can mount. |
| Disable `moonraker-obico.service` | Stock cfg has no API key but still heartbeats `app.obico.io` continuously. User can re-enable if they actually pair with Obico. |
| Disable `hostapd.service` | Vestigial from the BTT CB1 base image; no AP config exists, so it auto-restarts forever. |
| Rewrite `/boot/scripts/btt_init.sh` | Drop `connect_wifi.sh` (NM already handles wifi; the stock branch reads `wifi.cfg` from any plugged-in USB stick — physical-access takeover vector), `file_change_save.sh` (duplicates Klipper/Moonraker persistence), and `ota_service.sh` (Comgrow OTA channel does MD5-only verification and `dpkg -i`'s arbitrary debs as root). Keep the `/boot/gcode/` USB-gcode-injection sweep and `system_cfg.sh` (timezone / KS rotation / sound / vibration / brightness knobs). |
| Cleanup-tier file deletes | `~/ttyS3.py` (developer leftover), `~/offline_lib/` (factory-build pip cache), `~/usbmount/` (already-make-installed source tree), `/home/mount.log` (vendor-script append log). |
| Install `deckhand.json` marker | So the connect screen recognises the printer next time. |
| `install_firmware` (with confirm prompt) | Default firmware choice is Sovol's published fork at `github.com/Sovol3d/klipper@master` — refresh in place. Klipper / Kalico choices also available; both layer the Sovol klippy/extras overlay (`scripts/install_sovol_klipper_extras.sh`) so the stock printer.cfg's `z_offset_calibration` / `probe_eddy_current vir_contact_speed` references resolve. User can decline at the confirm prompt to keep their existing Klipper untouched. |

A pre-flight `snapshot_paths` step lets the user select
`printer_data` and `boot_partition` (default-on) and
`klipper_install` and `home_helpers` (default-off) for snapshot to
`<path>.deckhand-stock-<ts>` before any destructive change runs.

## fresh_flash also handles in-place OS upgrades

`wizard.fresh_flash_preserve_state` (default: **preserve**) asks
whether this is a clean install of a brand-new printer or an
in-place upgrade of an existing one (e.g. moving from the stock
SPI-XI 2.3.3 Debian-11 image to BTT V3.1.0 Debian-13). On preserve:

- **Before flash** (printer still on its old image, SSH-reachable): a
  `snapshot_archive` step bundles the user-selected paths from
  `stock_os.snapshot_paths` (default-on: `printer_data` and
  `boot_partition`) into a workstation-side `.tar.gz`.
- **After flash + first_boot_setup** (printer rebooted into the new
  BTT image, SSH-reachable again): `restore_preserved_state.sh`
  extracts the archive back. Restores `~/printer_data/` (printer.cfg,
  Macro.cfg, chamber_hot.cfg, plr.cfg, the SAVE_CONFIG bed mesh + PID
  + input shaper, gcode queue, Klipper logs) and `/boot/system.cfg`
  (timezone / KS rotation / sound / vibration / brightness toggles).
  Skips `~/klipper` (about to be replaced by `install_firmware`) and
  the Sovol home helpers (about to be reinstalled by
  `install_sovol_stock_configs`). The user-restored printer.cfg
  takes precedence over the published Sovol stock printer.cfg
  because `install_sovol_stock_configs.sh` won't clobber an existing
  config file.

On clean: snapshot + restore are skipped; the printer comes up with
Sovol's published stock configs only.

## fresh_flash — what gets installed

1. **Pick a base image** from `os.fresh_install_options`:
   - `BigTreeTech CB1 V3.1.0 — Debian 13 minimal` (recommended, ~473 MB compressed)
   - `BigTreeTech CB1 V3.1.0 — Debian 13 with Klipper preinstalled` (~1.18 GB compressed)
   Both pinned by sha256.

2. **Pick a USB-attached eMMC adapter** (size ≥ 8 GB, removable).

3. Image is downloaded over HTTPS from `github.com/bigtreetech/CB1` releases, **sha256-verified** before any disk write, then flashed with read-back verify.

4. After the user reseats the eMMC and reboots, `wait_for_ssh` polls until the printer answers SSH (default creds on a fresh BTT image are `biqu`/`biqu`, NOT `sovol`/`sovol`).

5. `first_boot_setup` runs `apt update` and pulls build tools.

6. **`install_firmware`** clones the chosen Klipper variant. Default `sovol-fork` clones `github.com/Sovol3d/klipper`. Other choices clone `github.com/Klipper3d/klipper` (mainline) or `github.com/KalicoCrew/kalico`.

7. **`install_klipper_extras`** (only when the chosen variant isn't `sovol-fork`) layers Sovol's klippy/extras (`z_offset_calibration.py`, `probe_pressure.py`, modified `probe_eddy_current.py`/`ldc1612.py`/`lis2dw.py`/`bed_mesh.py`/`probe.py`/`homing.py`/`shaper_calibrate.py`/`fan.py`/`heater_fan.py`, plus the `display/menu.py` + `display/menu.cfg` + `display/display.cfg` overlay) onto the chosen firmware tree.

8. **`install_stack`** brings up Moonraker, Mainsail (or Fluidd), KIAUH, Crowsnest.

9. **`install_stock_configs`** (`scripts/install_sovol_stock_configs.sh`) clones `github.com/Sovol3d/SOVOL-ZERO` at the pinned commit `b214ea5c771932e2eddae3bf30c6a5b03bd5e6ed` and copies `printer.cfg`, `Macro.cfg`, `chamber_hot.cfg`, `plr.cfg`, `get_ip.cfg`, `shell_command.cfg`, `moonraker.conf`, `crowsnest.conf` into `~/printer_data/config/` (only writing files that don't already exist), plus `~/get_ip.sh`, `~/plr.sh`, `~/clear_plr.sh`, `~/factory_resets.sh`, `~/ota_client.sh`, `~/pyhelper/`, and `~/patch/`.

10. **`configure_can0`** writes `/etc/network/interfaces.d/can0` (BTT base doesn't have it; without it the `gs_usb` CAN bridge stays down and the three MCUs are unreachable). `bring_up_can0` runs `ifup can0`.

11. **`build_and_flash_mcus`** (`scripts/build_and_flash_mcus.sh`) builds the three MCU firmwares from the chosen klipper tree's `.config` (STM32H750) and `.config103` (STM32F103) build configs and katapult-flashes each over CAN at the deterministic UUIDs:
    - main `0d1445047cdd` (STM32H750 — CAN-USB bridge)
    - extruder `61755fe321ac` (STM32F103)
    - hot/chamber `58a72bb93aa4` (STM32F103)

12. `apply_files`, `install_marker`, `install_screen`, `start_services`, `run_verifiers`.

## What `stock_keep` does NOT do

- Does not touch user-side calibration data (SAVE_CONFIG block in `printer.cfg`, saved bed mesh, PID, input shaper) — `printer_data/` is preserved verbatim.
- Does not modify `Macro.cfg`, `chamber_hot.cfg`, `plr.cfg`, `get_ip.cfg`, `shell_command.cfg`, or any other config the user might have customised.
- Does not delete the user's own NetworkManager wifi profile — only the three known factory entries.
- Does not replace KlipperScreen — the stock `KlipperScreen-start.sh` is upstream-unmodified and stays.

## Layout

```
profile.yaml                          status: alpha, both flows enabled
README.md                             this file
docs/STOCK-INVENTORY.md               live audit findings

klipper-extras/sovol_dev/             GPL-3.0 Sovol-fork klippy/extras (byte-pinned)
  z_offset_calibration.py               Sovol-original
  probe_pressure.py                     Sovol-derivative
  probe_eddy_current.py + ldc1612.py    required, NOT on Sovol's public master
  lis2dw.py / bed_mesh.py / probe.py / homing.py /
  shaper_calibrate.py / fan.py / heater_fan.py
  display/{menu.py, menu.cfg, display.cfg}
  README.md                             per-file provenance

firmware/                             MCU build configs (byte-pinned from live unit)
  main-mcu-h750.config                  STM32H750 main MCU
  extruder-and-hot-mcu-f103.config      STM32F103 (used for both extruder + hot)

scripts/
  btt_init.sh.tmpl                    new /boot/scripts/btt_init.sh (rewrite step)
  clear_boot_system_cfg_wifi.sh       sed-in-place for /boot/system.cfg wifi fields
  regen_ssh_host_keys.sh              rm + ssh-keygen -A + reload sshd
  install_sovol_stock_configs.sh      clone Sovol3d/SOVOL-ZERO at pinned SHA, copy stock configs
  install_sovol_klipper_extras.sh     overlay embedded Sovol klippy/extras
  build_and_flash_mcus.sh             build + katapult-flash all three MCUs over CAN
  restore_preserved_state.sh          extract a workstation-staged snapshot back onto the printer
```

Raw audit dumps live out-of-repo at `installer/.audits/sovol-zero-20260501/` (factory wifi PSKs and the SSH host-key triple in plaintext).

## Pinned upstream sources

| Source | Pin | Why pinned |
|--------|-----|-----------|
| `github.com/bigtreetech/CB1` V3.1.0 | sha256 per asset (in `profile.yaml`) | OS image — sha256 enforced before any disk write. |
| `github.com/Sovol3d/SOVOL-ZERO` | commit `b214ea5c7719e133b5d7b5c73898e24d882d8906` | Stock Sovol configs + helper scripts. Pinned in `scripts/install_sovol_stock_configs.sh`. |
| `github.com/Sovol3d/klipper` (sovol-fork firmware choice) | branch `master` | Tracks Sovol's published fork. Note: master is missing `probe_eddy_current.py` and `ldc1612.py` — the embedded overlay below carries those, so even sovol-fork installs run the overlay. |
| `klipper-extras/sovol_dev/` (embedded overlay) | byte-pinned at audit-time SHAs | Sovol klippy/extras files extracted from the live unit at audit time. sha256 of each file is in this profile's commit history. |
| `firmware/main-mcu-h750.config` | sha256 `6c630795bddfd93a00ff599b1954b6616bdde147c3cbf6ee491bb0294728b244` | STM32H750 main-MCU build config, byte-pinned from live unit. |
| `firmware/extruder-and-hot-mcu-f103.config` | sha256 `a66226e7ecd9a6277ca81d4bf822b84f3c8308c3105d6954327f95b1f565e650` | STM32F103 build config (used for both extruder + hot MCUs), byte-pinned from live unit. |
| `github.com/Klipper3d/klipper` (klipper firmware choice) | branch `master` | Tracks upstream Klipper. |
| `github.com/KalicoCrew/kalico` (kalico firmware choice) | branch `main` | Tracks Kalico community fork. |

Bumping any pin is a conscious action: refetch the relevant URL, paste the new sha or commit, run the validator. Do not use floating tags or `*_current` redirects in production — they defeat reproducibility.

## What's next (toward `beta`)

The profile is structurally complete — both flows wired, schema-validated, all referenced scripts and assets present and byte-pinned. What's left is real-hardware validation:

1. **Run `stock_keep` against the live unit.** Reversible aside from the SSH host-key regen (which is exactly what we want anyway). The `confirm_before_run` prompts on `rewrite_btt_init_sh` and `regen_ssh_host_keys` give a manual escape hatch mid-flow. `wizard.extra_steps.stock_keep_firmware_refresh` defaults to "skip" so existing Klipper stays untouched unless the user explicitly opts in.
2. **Run `fresh_flash` against a spare eMMC.** Needs a USB eMMC adapter; the sourced eMMC can be the printer's own (after a `stock_keep` snapshot of `printer_data` for restore) or a spare ≥ 8 GB. Whole flow takes ~30 minutes; the long pole is the three MCU builds (~5 minutes each on the CB1) plus the katapult flash (~30 seconds each).
3. **Address the `sv08mini-update-packge` dpkg situation.** `apt remove` is risky (its files include the can0 ifupdown config and the RTL8189FS wifi kernel module, both of which we want to keep); the conservative answer is to leave it installed — the only service it ships is `wifi_server.service` which is already masked, and the package's other contents are inert. Decision made; documented here rather than coded as a flow step.

Neither flow has been run end-to-end against real hardware in this session. Until that happens this profile is `alpha` not `beta` — even though every line is in place.

## Contributing

1. Run a flow on real hardware. File issues against `printers/sovol-zero:` for anything that breaks.
2. PR title prefix: `sovol-zero:`.