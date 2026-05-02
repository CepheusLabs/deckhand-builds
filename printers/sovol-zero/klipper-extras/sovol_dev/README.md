# Sovol Zero — klippy/extras overlay

GPL-3.0-licensed Klipper-fork files extracted from a stock Sovol Zero
running Sovol's "1.3.7版本" firmware (commit cc8afd89 from
http://192.168.1.233/root/klipper.git on the live unit, audit date
2026-05-01). These files are referenced by the Sovol Zero stock
printer.cfg and chamber_hot.cfg and need to be present in
klippy/extras/ for the printer to boot.

Embedded here rather than fetched from `github.com/Sovol3d/klipper`
at install time because:

- `probe_eddy_current.py` and `ldc1612.py` are not present on
  Sovol's published klipper fork at master — the public mirror
  appears to be the SV08-Mini lineage which doesn't share those
  modules. Sovol's LAN-private fork on the printer does have them.
- The remaining files differ between Sovol's public master and the
  on-printer commit; the on-printer set is the one that pairs with
  the on-printer stock printer.cfg.

## Files

| File | Source | Purpose |
|------|--------|---------|
| `z_offset_calibration.py` | Sovol-original (header attributes Sovol3d 2024-2025) | Implements the `Z_OFFSET_CALIBRATION` g-code that printer.cfg's stock `START_PRINT` macro calls before each print. |
| `probe_pressure.py` | Sovol-derivative (Klipper-licensed header) | Strain-gauge / pressure-sensor probe support, referenced from probe_eddy_current's contact-detection path. |
| `probe_eddy_current.py` | Modified-from-upstream | Adds `vir_contact_speed`, `TYPE_VIR_TOUCH`, and rapid-scan support. printer.cfg's `[probe_eddy_current eddy]` block references `vir_contact_speed: 3.0`. |
| `ldc1612.py` | Modified-from-upstream | LDC1612 inductive-sensor i2c driver. Sovol added i2c-error retry handling (per git log: "增加i2c错误码分类处理"). |
| `lis2dw.py` | Modified-from-upstream | LIS2DW SPI accelerometer (Sovol uses LIS2DW instead of the more common ADXL345). |
| `bed_mesh.py` | Modified-from-upstream | Adds `rapid_scan` mesh-calibration mode that pairs with the eddy probe. |
| `probe.py` | Modified-from-upstream | Companion changes for probe_pressure / probe_eddy_current integration. |
| `homing.py` | Modified-from-upstream | Sovol's "tip code" prompts on homing failures (M117 Tip code: 102 etc.). |
| `shaper_calibrate.py` | Modified-from-upstream | Touched by `SHAPER_CALIBRATE` flow improvements. |
| `fan.py` / `heater_fan.py` | Modified-from-upstream | Sovol's chamber-fan / part-fan tuning. |
| `display/menu.py` / `menu.cfg` / `display.cfg` | Sovol-overlay | Replaces upstream Klipper's display menu definitions. Targets the EXP1/EXP2 UC1701 SPI LCD declared in `printer.cfg`. |

## How it's used

`scripts/install_sovol_klipper_extras.sh` copies these into
`<firmware-install-path>/klippy/extras/` whenever the chosen firmware
variant is `klipper` (upstream mainline) or `kalico` — i.e., whenever
the user picks a Klipper variant that does NOT already carry these
modules. For the default `sovol-fork` choice, the script no-ops since
Sovol's published fork is itself the source.
