#!/bin/bash
# Overlay Sovol's klippy/extras/ modifications on top of an
# already-installed Klipper or Kalico tree, using the embedded
# overlay copies under printers/sovol-zero/klipper-extras/sovol_dev/.
#
# Used when firmware.choice is `klipper` (upstream mainline) or
# `kalico`. Skipped when firmware.choice is `sovol-fork` — that
# variant clones github.com/Sovol3d/klipper which is itself the
# upstream of these files (modulo the two — probe_eddy_current.py
# and ldc1612.py — that aren't on Sovol's public fork; see
# klipper-extras/sovol_dev/README.md).
#
# Inputs (env):
#   FIRMWARE_PATH   — install path of the chosen firmware
#                     (e.g. ~/klipper, ~/kalico). Required.
#   OVERLAY_DIR     — path to the embedded overlay tree on the
#                     printer side. Set by the controller when it
#                     stages the profile assets onto the printer.
#                     Defaults to a sibling of FIRMWARE_PATH if
#                     unset, which lets the script also be run
#                     standalone for testing.

set -e

FIRMWARE_PATH=${FIRMWARE_PATH:-~/klipper}
OVERLAY_DIR=${OVERLAY_DIR:-$(dirname "$0")/../klipper-extras/sovol_dev}

if [ ! -d "$FIRMWARE_PATH/klippy/extras" ]; then
    echo "FIRMWARE_PATH=$FIRMWARE_PATH does not look like a Klipper install (no klippy/extras/)" >&2
    exit 1
fi

if [ ! -d "$OVERLAY_DIR" ]; then
    echo "OVERLAY_DIR=$OVERLAY_DIR not found — embedded overlay missing" >&2
    exit 1
fi

EXTRAS=$FIRMWARE_PATH/klippy/extras
TS=$(date -u +%Y%m%dT%H%M%SZ)

# Sovol-original modules — not in upstream Klipper, must be copied
# in or printer.cfg fails to load.
SOVOL_ORIGINAL=(
    z_offset_calibration.py
    probe_pressure.py
)

# Modified-from-upstream modules. Sovol's versions add features the
# stock printer.cfg references. Existing upstream copies are
# snapshotted to .deckhand-pre-<ts> siblings before overwrite.
SOVOL_MODIFIED=(
    probe_eddy_current.py
    ldc1612.py
    lis2dw.py
    bed_mesh.py
    probe.py
    homing.py
    shaper_calibrate.py
    fan.py
    heater_fan.py
)

for f in "${SOVOL_ORIGINAL[@]}"; do
    if [ ! -f "$OVERLAY_DIR/$f" ]; then
        echo "Missing from overlay: $OVERLAY_DIR/$f" >&2
        exit 1
    fi
    cp -p "$OVERLAY_DIR/$f" "$EXTRAS/$f"
    echo "Added (sovol-original): $EXTRAS/$f"
done

for f in "${SOVOL_MODIFIED[@]}"; do
    if [ ! -f "$OVERLAY_DIR/$f" ]; then
        echo "Missing from overlay: $OVERLAY_DIR/$f" >&2
        exit 1
    fi
    if [ -f "$EXTRAS/$f" ]; then
        cp -p "$EXTRAS/$f" "$EXTRAS/$f.deckhand-pre-${TS}"
    fi
    cp -p "$OVERLAY_DIR/$f" "$EXTRAS/$f"
    echo "Overlaid (sovol-modified): $EXTRAS/$f"
done

# klippy/extras/display/ overlay (Sovol's menu/display rework).
mkdir -p "$EXTRAS/display"
for f in menu.py menu.cfg display.cfg; do
    if [ ! -f "$OVERLAY_DIR/display/$f" ]; then
        echo "Missing from overlay: $OVERLAY_DIR/display/$f" >&2
        exit 1
    fi
    if [ -f "$EXTRAS/display/$f" ]; then
        cp -p "$EXTRAS/display/$f" "$EXTRAS/display/$f.deckhand-pre-${TS}"
    fi
    cp -p "$OVERLAY_DIR/display/$f" "$EXTRAS/display/$f"
    echo "Overlaid (sovol-display): $EXTRAS/display/$f"
done

# Drop pyc cache so the new .py files are picked up next klipper start.
find "$EXTRAS" -name '*.pyc' -delete 2>/dev/null || true
find "$EXTRAS" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

echo "Sovol klippy/extras overlay applied to $FIRMWARE_PATH"
