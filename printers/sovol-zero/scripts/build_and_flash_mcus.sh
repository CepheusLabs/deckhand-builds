#!/bin/bash
# Build the three MCU firmwares from the chosen klipper tree and
# katapult-flash them over CAN.
#
# The Sovol Zero ships with three MCUs all on can0 at 1 Mbit:
#   main      stm32h750xx   canbus_uuid 0d1445047cdd  (CAN-bridge to USB)
#   extruder  stm32f103xe   canbus_uuid 61755fe321ac
#   hot       stm32f103xe   canbus_uuid 58a72bb93aa4
#
# Build configs are embedded with this profile under firmware/:
#   firmware/main-mcu-h750.config            (h750 main)
#   firmware/extruder-and-hot-mcu-f103.config (f103, used for both
#                                              extruder and hot)
# These were extracted byte-for-byte from a stock Sovol Zero
# (live audit 2026-05-01, fingerprint sha256 captured in the file
# header below) so the built bins exactly reproduce Sovol's stock
# MCU firmwares modulo the upstream klipper code lineage of the
# chosen FIRMWARE_PATH.
#
# Inputs (env):
#   FIRMWARE_PATH    — chosen klipper install path. Required.
#                      Used as the build tree (make + .config dance).
#   MCU_CONFIG_DIR   — where the *.config files live. Set by the
#                      controller when it stages the profile assets
#                      onto the printer. Defaults to <profile>/firmware.

set -e

FIRMWARE_PATH=${FIRMWARE_PATH:-~/klipper}
MCU_CONFIG_DIR=${MCU_CONFIG_DIR:-$(dirname "$0")/../firmware}
BUILD_HELPER=~/printer_data/build

if [ ! -d "$FIRMWARE_PATH" ]; then
    echo "FIRMWARE_PATH=$FIRMWARE_PATH not found" >&2
    exit 1
fi
if [ ! -f "$MCU_CONFIG_DIR/main-mcu-h750.config" ]; then
    echo "Missing $MCU_CONFIG_DIR/main-mcu-h750.config — embedded MCU config not staged" >&2
    exit 1
fi
if [ ! -f "$MCU_CONFIG_DIR/extruder-and-hot-mcu-f103.config" ]; then
    echo "Missing $MCU_CONFIG_DIR/extruder-and-hot-mcu-f103.config" >&2
    exit 1
fi

mkdir -p "$BUILD_HELPER"

# flash_can.py from Sovol's klipper publishes it under lib/canboot/.
# A fresh klipper / kalico clone won't have it. Klipper upstream
# ships a script at scripts/flash-canbus.py with a similar role; we
# look for both. Failing both, we curl the canonical Katapult one.
locate_flasher() {
    for cand in \
        "$BUILD_HELPER/flash_can.py" \
        "$FIRMWARE_PATH/lib/canboot/flash_can.py" \
        "$FIRMWARE_PATH/scripts/flash-canbus.py"; do
        if [ -f "$cand" ]; then
            echo "$cand"
            return 0
        fi
    done
    # Fallback: fetch katapult's flash_can.py (canonical source).
    curl -fsSL --max-time 30 \
        "https://raw.githubusercontent.com/Arksine/katapult/master/scripts/flash_can.py" \
        -o "$BUILD_HELPER/flash_can.py"
    chmod +x "$BUILD_HELPER/flash_can.py"
    echo "$BUILD_HELPER/flash_can.py"
}

FLASHER=$(locate_flasher)
echo "Using flasher: $FLASHER"

build_mcu() {
    local label=$1 cfg=$2 outpath=$3
    echo "===> Building $label using $cfg"
    cd "$FIRMWARE_PATH"
    cp "$cfg" .config
    make olddefconfig
    make clean
    make -j2
    cp out/klipper.bin "$outpath"
    echo "===> $label firmware at $outpath ($(stat -c%s "$outpath") bytes)"
}

build_mcu "main (stm32h750)"     "$MCU_CONFIG_DIR/main-mcu-h750.config"            "$BUILD_HELPER/mcu_klipper.bin"
build_mcu "extruder (stm32f103)" "$MCU_CONFIG_DIR/extruder-and-hot-mcu-f103.config" "$BUILD_HELPER/extruder_mcu_klipper.bin"

# The hot/chamber MCU shares the f103 build with the extruder. Sovol
# uses the same firmware blob for both — they're identified by CAN
# UUID, not by content.
cp "$BUILD_HELPER/extruder_mcu_klipper.bin" "$BUILD_HELPER/extra_mcu_klipper.bin"

# Make sure can0 is up.
sudo ip link set can0 up 2>/dev/null || true
ip -d link show can0 || { echo "can0 not up; cannot flash"; exit 1; }

flash_one() {
    local label=$1 uuid=$2 blob=$3
    echo "===> Flashing $label (uuid=$uuid)"
    # Wake the chip into katapult bootloader by sending a flash
    # request and immediately killing it (matches Sovol's own
    # *_update_fw.sh pattern).
    python3 "$FLASHER" -i can0 -f "$blob" -u "$uuid" &
    local pid=$!
    sleep 5
    kill "$pid" 2>/dev/null || true
    sleep 1
    python3 "$FLASHER" -i can0 -f "$blob" -u "$uuid"
    echo "===> $label flashed"
}

flash_one "main"     "0d1445047cdd" "$BUILD_HELPER/mcu_klipper.bin"
flash_one "extruder" "61755fe321ac" "$BUILD_HELPER/extruder_mcu_klipper.bin"
flash_one "hot"      "58a72bb93aa4" "$BUILD_HELPER/extra_mcu_klipper.bin"

echo "All three MCUs flashed."
