# Sovol SV08 Max profile

Deckhand profile for the [Sovol SV08 Max][sv08max] — a large-format
500×505×505 mm CoreXY FDM with a quad-Z gantry, BigTreeTech CB1
(Allwinner H616) SBC, and three CAN-bus MCUs driven through a USB
gs_usb adapter. Ships with a serial TFT touchscreen (Sovol's
open-source `zhongchuang_klipper` daemon) and an HDMI port that
supports KlipperScreen as a secondary display.

**Status:** `alpha`. Profile is structurally complete and every
load-bearing artifact is vendored from Sovol's published source at
[Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX). Both
`flows.stock_keep` and `flows.fresh_flash` are declared with full
step lists, but neither has been validated end-to-end on real
hardware through Deckhand yet.

## What's here

| Path | What it is |
|------|-----------|
| `profile.yaml` | The manifest Deckhand reads. Drives detection, the wizard, and every install step. Mirrors the Sovol Zero's vocabulary so the two look like siblings. |
| `configs/` | `printer.cfg`, `chamber_hot.cfg`, `Macro.cfg`, `plr.cfg`, `get_ip.cfg`, `mainsail.cfg`, `moonraker.conf`, `crowsnest.conf`, `buffer_stepper.cfg`, `shell_command.cfg`, `saved_variables.cfg`, `timelapse.cfg`, `moonraker_obico_macros.cfg`, `moonraker-obico.cfg`, `moonraker-obico-update.cfg` — vendored from Sovol's `home/sovol/printer_data/config/`. |
| `firmware/` | `flash_can.py` (Eric Callahan's Katapult uploader), `mcu_update_fw.sh` / `extruder_mcu_update_fw.sh` / `extra_mcu_update_fw.sh` (Sovol's flasher wrappers), `mcu_klipper.bin` (28,996-byte H750 main-MCU firmware vendored from Sovol's MKSDEB), `main-mcu-h750.config` and `toolhead-chamber-mcu-f103.config` (Klipper build configs), `build-mcu-firmware.sh` (Deckhand-invoked builder for the MCUs Sovol doesn't pre-build). |
| `klipper-extras/` | Sovol-original / Sovol-modified `klippy/extras/` modules: `z_offset_calibration.py`, `probe_pressure.py`, `buffer_stepper.py`, plus modified `probe_eddy_current.py`, `ldc1612.py`, `lis2dw.py`. |
| `screen-daemon/` | Full source tree for `zhongchuang_klipper` — Sovol's open-source mksclient derivative that drives the serial TFT. CMake build, links against pthread/boost_system/wpa_client/curl. Includes the systemd unit (`makerbase-client.service`) and the `start.sh` launcher. |
| `scripts/btt_init.sh.tmpl` | Deckhand-rewritten boot orchestrator. Drops `file_change_save.sh` unconditionally, conditionally drops `connect_wifi.sh` based on the wizard choice. Replaces Sovol's `/boot/scripts/btt_init.sh`. |
| `scripts/home/` | Vendor-supplied home-dir scripts (`plr.sh`, `clear_plr.sh`, `factory_resets.sh`, `get_ip.sh`, `ota_client.sh`) wired into Klipper macros via `configs/get_ip.cfg` + `configs/Macro.cfg`. |
| `scripts/pyhelper/` | Small Python helpers (`send_ip.py`, `restart_firmware.py`, `ota_process.py`) the home scripts call out to. |
| `docs/` | `STOCK-INVENTORY.md` (full audit narrative), `ALIGNMENT-WITH-ZERO.md` (cross-printer reconciliation against the Sovol Zero), `ARCHITECTURE.md` (system topology overview). |

## What's deliberately NOT here

| Missing artifact | Reason / where to get it |
|------------------|--------------------------|
| `extruder_mcu_klipper.bin` and `extra_mcu_klipper.bin` (toolhead + chamber MCU firmware blobs) | Sovol does not publish pre-built blobs for the F103 MCUs. The flows build them from source on-device using `firmware/toolhead-chamber-mcu-f103.config` against the Sovol klipper tree at `/home/sovol/klipper`. |
| `众创klipper.tft.bak` (TFT panel firmware) | Closed-source ZhongChuang vendor firmware — not redistributed by Deckhand. Whatever ships on the panel is the baseline; `~/众创klipper.tft.bak` on the printer is the documented restore image. |
| `/boot/scripts/auto_brightness`, `set_rgb` (binaries for HDMI display feedback) | Not redistributed. Sovol leaves them in `/boot/scripts/` from the BTT CB1 base image; Deckhand preserves whatever's there. |

## Reference docs

The files in `docs/` are the result of a live audit (raw probe dumps
out-of-repo at `installer/.audits/sovol-sv08-max-20260501/`) plus
cross-reference against Sovol's published source. Worth reading
before contributing:

- [`docs/STOCK-INVENTORY.md`](docs/STOCK-INVENTORY.md) — full audit
  of every Sovol-shipped service, file, and network indicator on
  stock.
- [`docs/ALIGNMENT-WITH-ZERO.md`](docs/ALIGNMENT-WITH-ZERO.md) —
  cross-printer reconciliation between the Sovol SV08 Max and the
  Sovol Zero (which share the SPI-XI base image).
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — hardware +
  software topology.
- [`firmware/README.md`](firmware/README.md) — MCU inventory, flash
  mechanics, build-from-source path.
- [`screen-daemon/README.md`](screen-daemon/README.md) — zhongchuang
  daemon lineage, build, lifecycle.
- [`klipper-extras/README.md`](klipper-extras/README.md) — Sovol's
  custom Klipper modules and the trade-off if you ever replace the
  klipper fork.
- [`configs/README.md`](configs/README.md) — what each config file
  does and which ones are optional-toggle.

## Sibling profile

The Sovol SV08 Max shares the SPI-XI base image with the
[Sovol Zero](../sovol-zero/). Most of the stock-OS service / file
inventory is identical (default `sovol`/`sovol` creds, pre-shared
SSH host keys, `wifi_server.service` LAN RCE, deterministic CAN
UUIDs, identical Klipper extras tree). See
[`docs/ALIGNMENT-WITH-ZERO.md`](docs/ALIGNMENT-WITH-ZERO.md) for the
side-by-side. Hardware divergences (build volume, board revision,
4-Z quad-gantry, dual part-cooling fans, serial TFT touchscreen vs
small UC1701 LCD) are reflected in the divergent fields of each
profile.

## Promoting this profile to `beta`

1. Run `flows.stock_keep` end-to-end against a real SV08 Max,
   document any failures, resolve them. The flow has 21 steps; pay
   particular attention to the ones we haven't tested:
   - `regenerate_ssh_host_keys` (must run BEFORE any fingerprint
     trust prompt — this is THE security-critical step).
   - `disable_wifi_server` (must run before any other LAN-side
     state change — root LAN RCE on port 5000).
   - `rewrite_btt_init_sh` (template-based rewrite of the boot
     orchestrator).
   - `flash_main_mcu` (uses our vendored `mcu_klipper.bin`).
   - The optional `build_and_flash_toolhead_mcu` /
     `build_and_flash_chamber_mcu` paths (build-from-source flow).
2. Run `flows.fresh_flash` end-to-end against a freshly-flashed
   eMMC. The fresh-flash path has more moving pieces (Armbian
   image download + flash, Klipper build, zhongchuang build, all
   three MCU firmware builds, then flash all three MCUs).
3. Verify power-loss-recovery still works through `~/plr.sh` after
   `stock_keep`.
4. Verify `M141` / `M191` chamber-control macros work (heater
   section name `[heater_generic chamber_temp]` — diverges from
   the Zero's `chamber_heater`).
5. Bump `profile_version` and `status` in `profile.yaml`, open a PR
   with a validation-notes section.

[sv08max]: https://www.sovol3d.com/products/sovol-sv08-max
