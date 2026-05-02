#!/bin/bash
# build-mcu-firmware.sh — Deckhand-invoked Klipper-firmware builder
# for the Sovol SV08 Max MCUs.
#
# Inputs (env):
#   CONFIG_FILE   - path to a Klipper .config (e.g.
#                   ./firmware/main-mcu-h750.config or
#                   ./firmware/toolhead-chamber-mcu-f103.config).
#                   Resolved relative to the profile directory.
#   OUTPUT_PATH   - absolute path on the printer where the resulting
#                   .bin should land (e.g.
#                   /home/sovol/printer_data/build/extruder_mcu_klipper.bin).
#   KLIPPER_TREE  - absolute path to the Klipper source tree on the
#                   printer (Sovol's fork lives at /home/sovol/klipper).
#
# Behavior:
#   1. Stage the build config into <KLIPPER_TREE>/.config.
#   2. `make clean && make` against that config.
#   3. Verify the resulting out/klipper.bin exists and is non-empty.
#   4. Copy out/klipper.bin to OUTPUT_PATH (creating the parent dir if
#      needed).
#
# Exit non-zero on any failure. Idempotent: a re-run reproduces the
# same blob (assuming the source tree hasn't changed).

set -euo pipefail

: "${CONFIG_FILE:?CONFIG_FILE is required}"
: "${OUTPUT_PATH:?OUTPUT_PATH is required}"
: "${KLIPPER_TREE:?KLIPPER_TREE is required}"

if [ ! -f "${CONFIG_FILE}" ]; then
    echo "ERROR: CONFIG_FILE does not exist: ${CONFIG_FILE}" >&2
    exit 1
fi

if [ ! -d "${KLIPPER_TREE}" ]; then
    echo "ERROR: KLIPPER_TREE does not exist: ${KLIPPER_TREE}" >&2
    exit 1
fi

if [ ! -f "${KLIPPER_TREE}/Makefile" ]; then
    echo "ERROR: ${KLIPPER_TREE}/Makefile not found — is this a Klipper checkout?" >&2
    exit 1
fi

# Make sure host build deps are available. These are present on the
# stock SPI-XI image; this guards the fresh_flash path where the user
# may have a clean Armbian build.
need_pkgs=(build-essential gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi python3)
missing=()
for p in "${need_pkgs[@]}"; do
    if ! dpkg-query -W -f='${Status}' "${p}" 2>/dev/null | grep -q 'install ok installed'; then
        missing+=("${p}")
    fi
done
if [ ${#missing[@]} -gt 0 ]; then
    echo "Installing build deps: ${missing[*]}"
    sudo apt-get update -qq
    sudo apt-get install -y "${missing[@]}"
fi

echo "Building Klipper MCU firmware..."
echo "  CONFIG_FILE  = ${CONFIG_FILE}"
echo "  OUTPUT_PATH  = ${OUTPUT_PATH}"
echo "  KLIPPER_TREE = ${KLIPPER_TREE}"

cp "${CONFIG_FILE}" "${KLIPPER_TREE}/.config"

cd "${KLIPPER_TREE}"
make clean
make -j"$(nproc)"

if [ ! -s out/klipper.bin ]; then
    echo "ERROR: build did not produce out/klipper.bin" >&2
    exit 1
fi

mkdir -p "$(dirname "${OUTPUT_PATH}")"
cp out/klipper.bin "${OUTPUT_PATH}"

size=$(stat -c '%s' "${OUTPUT_PATH}")
echo "OK: wrote ${OUTPUT_PATH} (${size} bytes)"
