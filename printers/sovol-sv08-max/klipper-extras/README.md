# Sovol SV08 Max — Klipper extras (Sovol-original / Sovol-modified)

Six Sovol-authored or Sovol-modified Python modules under
`klippy/extras/`. Vendored from
[Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX/tree/main/home/sovol/klipper/klippy/extras)
on 2026-05-01. Together with the unmodified upstream Klipper modules
in Sovol's tree, these implement the eddy-current Z probe + the
quad-gantry leveling + the auxiliary buffer feeder.

## Modules

| File | Origin | Why it's here |
|------|--------|---------------|
| `z_offset_calibration.py` | Sovol-original (header credits `Sovol3d <info@sovol3d.com>`, 2024-2025) | Implements the `Z_OFFSET_CALIBRATION` g-code used in `START_PRINT`. Depends on `probe`, `probe_eddy_current`, `manual_probe`. Not in upstream Klipper. |
| `probe_pressure.py` | Sovol-original (derived from upstream `probe.py`) | Pressure-sensing probe path used as fallback when the eddy probe doesn't return a clean reading. Header retains Kevin O'Connor's 2017–2021 copyright (the derivation source) but the implementation is Sovol's. |
| `buffer_stepper.py` | Sovol-original | Auxiliary filament-feeder buffer-stepper driver. Used by the SV08 Max's optional aux feeder; referenced from `configs/buffer_stepper.cfg`. |
| `probe_eddy_current.py` | upstream + Sovol mods | Adds `vir_contact_speed` and `TYPE_VIR_TOUCH` parameters — Sovol's "virtual contact" approach for non-contact eddy probing. Not in upstream's `probe_eddy_current.py`. |
| `ldc1612.py` | upstream + Sovol mods | LDC1612 eddy-coil chip driver with custom calibration hooks tied to `probe_eddy_current.py` above. |
| `lis2dw.py` | upstream + Sovol mods | LIS2DW accelerometer driver. The SV08 Max uses LIS2DW on the toolhead instead of the more common ADXL345; Sovol's modifications adapt the driver to the toolhead pin map (`extra_mcu:PB12-PB15`, `axes_map: x,z,y`). |

## Modules vendored for upstream Klipper / Kalico porting

These are vendored alongside the six core modules above so that
firmware-replacement choices (`firmware.choices: kalico` or
`firmware.choices: klipper-mainline` in `profile.yaml`) can lay
them down on top of an upstream tree:

| File | Origin | Why it's needed for Kalico/Klipper |
|------|--------|-------------------------------------|
| `bed_mesh.py` | upstream + Sovol mods (heavily extended) | Adds `rapid_scan` + eddy-driven `BED_MESH_CALIBRATE` paths used by `START_PRINT`. Vanilla upstream lacks the rapid-scan code. |
| `fan.py` | upstream + Sovol mods | Toolhead-fan tach handling adapted to the SV08 Max's `extra_mcu` pin map. |
| `heater_fan.py` | upstream + Sovol mods | Same — tach + kick_start tuning aligned with Sovol's stock printer.cfg. |
| `homing.py` | upstream + Sovol mods | Hooks into the eddy-probe contact behavior (the `vir_contact_speed` path). Without this, `M9928` homing macros won't reach the right code path. |
| `probe.py` | upstream + Sovol mods | Companion to the modified `probe_eddy_current.py` and `probe_pressure.py`. |
| `shaper_calibrate.py` | upstream + minor Sovol mods | Aligns input-shaper calibration with the LIS2DW (instead of upstream's ADXL345 default). |

That's twelve files total. If you replace Sovol's klipper fork
wholesale (e.g. with vanilla Klipper or Kalico), the profile's
`link_extras` step copies all twelve over the upstream files. **This
is fragile** — upstream's `probe_eddy_current.py` got a major rewrite
in Klipper 0.13.x, so Sovol's modifications may not apply cleanly to
recent Kalico/Klipper master. Test on a snapshot before promoting to
beta.

## Modules NOT vendored

- `display/menu.py`, `display/menu.cfg`, `display/display.cfg` —
  the `~/patch/` overlay that targets the small UC1701 LCD path. Not
  used on the SV08 Max (which uses the serial TFT, not a UC1701);
  vendored separately under `scripts/home/...`-style paths if needed
  for Sovol Zero parity, but the SV08 Max profile doesn't link them.

## How they get installed

`flows.stock_keep`: `link_extras` step copies them into
`/home/sovol/klipper/klippy/extras/` with backups, overwriting the
current stock copies. Idempotent — re-running the flow re-links the
same files.

`flows.fresh_flash`: same shape, but runs after `install_klipper`
(which `rsync`s Sovol's klipper tree out of the
`Sovol3d/SV08MAX` repo to `/home/sovol/klipper`). The link_extras
step is then a no-op for these files (they came in via the rsync)
unless we've patched any of them.

If a future iteration of this profile patches one of these modules
(e.g. forward-porting `z_offset_calibration.py` to Kalico), the
patched version replaces the Sovol-original here and the link_extras
step actually does work on a fresh install.
