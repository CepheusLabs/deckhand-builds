# Sovol SV08 Max — stock configs

Vendored verbatim from Sovol's published source at
[Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX/tree/main/home/sovol/printer_data/config)
on 2026-05-01. These are the canonical "factory baseline" configs — i.e.
what a freshly-flashed SPI-XI image would have under
`/home/sovol/printer_data/config/` before any user calibration.

## Files

| File | Source | Purpose |
|------|--------|---------|
| `printer.cfg` | `printer_data/config/printer.cfg` | Top-level Klipper config. Includes `mainsail.cfg`, `buffer_stepper.cfg`, `timelapse.cfg`, `plr.cfg`, `Macro.cfg`, `moonraker_obico_macros.cfg`. NOTE: the published version has `[include chamber_hot.cfg]` **commented out**; the live audited unit had it enabled. See "Optional include toggles" below. |
| `chamber_hot.cfg` | `printer_data/config/chamber_hot.cfg` | Heated-chamber MCU + macros (M141/M191) + watermark control. Section name is `[heater_generic chamber_temp]` (the Sovol Zero uses `[heater_generic chamber_heater]` — they are NOT interchangeable). |
| `Macro.cfg` | `printer_data/config/Macro.cfg` | Vendor macros (FACTORY_RESETS, _global_var, mainled_on/off, START_PRINT/END_PRINT, M9928 wrappers, etc.). |
| `plr.cfg` | `printer_data/config/plr.cfg` | Power-loss-recovery `[gcode_shell_command POWER_LOSS_RESUME]` wired to `~/plr.sh`. |
| `get_ip.cfg` | `printer_data/config/get_ip.cfg` | `[gcode_shell_command]` entries for `_GET_IP`, `_OTA`, `_OBICO_RESTART`, `_MCU_UP`, `_EXTRUDER_MCU_UP`, `_EXTRA_MCU_UP`. |
| `mainsail.cfg` | `mainsail-config/client.cfg` (symlink target) | Standard Mainsail client.cfg — pause/cancel/resume macros, park positions. |
| `moonraker.conf` | `printer_data/config/moonraker.conf` | Moonraker server config. `host: 0.0.0.0`, port 7125, trusted_clients = LAN ranges, octoprint_compat + history + timelapse blocks. |
| `moonraker-obico.cfg` | `printer_data/config/moonraker-obico.cfg` | Obico bridge config (`url = https://app.obico.io`, no API key). The `[meta]` block is what we match on for printer identification (`printer_model: SOVOL SV08 MAX`, `board_model: H616_JC_6Z_5160_V1.2`). |
| `moonraker-obico-update.cfg` | `printer_data/config/moonraker-obico-update.cfg` | `[update_manager moonraker-obico]` entry (managed_services + git origin). |
| `moonraker_obico_macros.cfg` | `moonraker-obico/include_cfgs/moonraker_obico_macros.cfg` (symlink target) | Obico-side gcode macros. |
| `crowsnest.conf` | `printer_data/config/crowsnest.conf` | Crowsnest webcam config — single camera on /dev/video0. |
| `buffer_stepper.cfg` | `printer_data/config/buffer_stepper.cfg` | Optional aux-feeder buffer stepper config. Enabled by default in Sovol's published printer.cfg. |
| `shell_command.cfg` | `printer_data/config/shell_command.cfg` | Empty/skeleton — Sovol's placeholder for additional `[gcode_shell_command]` entries. |
| `saved_variables.cfg` | `printer_data/config/saved_variables.cfg` | Klipper SAVE_VARIABLE state (filepath, last_file, power_resume_z, etc.). |
| `timelapse.cfg` | `moonraker-timelapse/klipper_macro/timelapse.cfg` (symlink target) | moonraker-timelapse plugin macros. |

## Optional include toggles

The factory-published `printer.cfg` has these include-state defaults:

```
[include mainsail.cfg]
#[include chamber_hot.cfg]      <-- commented out by default
[include buffer_stepper.cfg]    <-- enabled by default
[include timelapse.cfg]
[include plr.cfg]
[include Macro.cfg]
[include moonraker_obico_macros.cfg]
```

Whether `chamber_hot.cfg` and `buffer_stepper.cfg` should be active
depends on whether the user has the heated-chamber and buffer-feeder
hardware installed on their unit. The audited live unit had the
opposite of the published defaults — chamber on, buffer off — so
Sovol clearly toggles these per-SKU at factory provisioning time.

The `flows.stock_keep` flow preserves whatever the user already has;
`flows.fresh_flash` lays down the published defaults and prompts the
user to toggle the includes if they have the optional hardware.

## What's NOT included

These configs are present in `/home/sovol/printer_data/config/` on a
running printer but NOT in the published-default set, because they're
generated at runtime by Klipper or Moonraker:

- `printer-backup.cfg` — Klipper SAVE_CONFIG output.
- `config-<timestamp>.zip` — Moonraker-managed config snapshots.
- `.moonraker.conf.bkp` and `moonraker.conf.backup` — auto-generated.
- Per-tool / per-extruder calibration overrides.

These accumulate on a printer over time and are not part of the
"factory baseline" we vendor here.
