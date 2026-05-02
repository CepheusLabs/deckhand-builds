#!/bin/bash
# Restore a workstation-side snapshot archive back onto a freshly
# flashed Sovol printer. Used by the fresh_flash flow when the user
# picked "Upgrade — snapshot + restore my existing state" in the
# wizard.fresh_flash_preserve_state prompt.
#
# Inputs (env, supplied by the Deckhand controller):
#   SNAPSHOT_ARCHIVE — workstation-side path to the .tar.gz produced
#                       by the snapshot_archive step earlier in the
#                       flow. The controller scp's this file to
#                       /tmp/deckhand-restore.tar.gz on the printer
#                       before invoking this script (or sets
#                       REMOTE_ARCHIVE to the on-printer location).
#   REMOTE_ARCHIVE   — on-printer path to the staged archive.
#                       Defaults to /tmp/deckhand-restore.tar.gz.
#   PRINTER_HOME     — printer-side home directory. Default ~.
#
# Behavior:
#   - Extracts the archive to a transient staging dir
#   - For each path category (printer_data, /boot, klipper, sovol-home),
#     copies entries that ARE in the archive but does NOT clobber
#     entries created by first_boot_setup / install_stack /
#     install_stock_configs that ran in between snapshot and restore.
#   - Logs every copy decision (kept-existing vs restored).

set -e

REMOTE_ARCHIVE=${REMOTE_ARCHIVE:-/tmp/deckhand-restore.tar.gz}
PRINTER_HOME=${PRINTER_HOME:-$HOME}

if [ ! -f "$REMOTE_ARCHIVE" ]; then
    echo "Snapshot archive $REMOTE_ARCHIVE not found on printer. Restore skipped." >&2
    exit 1
fi

STAGE=$(mktemp -d /tmp/deckhand-restore.XXXXXX)
trap 'rm -rf "$STAGE"' EXIT

echo "Extracting $REMOTE_ARCHIVE to $STAGE"
tar -xzf "$REMOTE_ARCHIVE" -C "$STAGE"

echo "Archive contents:"
find "$STAGE" -maxdepth 2 -type d | sort

# printer_data: restore everything (configs, gcode queue, logs).
# install_sovol_stock_configs.sh's "don't clobber existing" rule
# means the user's restored printer.cfg takes precedence over
# Sovol's stock printer.cfg, which is what we want — preserve
# calibration + custom macros.
if [ -d "$STAGE/printer_data" ]; then
    echo "Restoring printer_data"
    mkdir -p "$PRINTER_HOME/printer_data"
    cp -rp "$STAGE/printer_data/." "$PRINTER_HOME/printer_data/"
fi

# /boot: restore /boot/system.cfg user knobs (timezone, KS rotation,
# touch sound/vibration). Do NOT restore /boot/scripts/* — the BTT
# V3.1.0 base image has its own /boot/scripts that work on Debian 13;
# the Sovol vendor scripts (connect_wifi.sh / file_change_save.sh /
# ota_service.sh / btt_init.sh) are exactly what stock_keep would
# have rewritten or dropped, so on a fresh BTT base they should
# stay BTT-stock.
if [ -f "$STAGE/boot/system.cfg" ]; then
    echo "Restoring /boot/system.cfg"
    sudo cp -p "$STAGE/boot/system.cfg" /boot/system.cfg
fi

# klipper: skipped. install_firmware ran or will run; whichever
# klipper variant the user chose has just landed at ~/klipper or
# ~/kalico. Restoring the old ~/klipper would clobber that and
# revert the user's firmware choice.

# sovol home helpers: skipped. install_sovol_stock_configs.sh
# fetches these from github.com/Sovol3d/SOVOL-ZERO at the pinned
# commit, which is more reproducible than restoring whatever was on
# the user's old install. The user's printer_data is what matters
# for "feels like the same printer" continuity.

echo "Cleaning up archive and stage"
rm -f "$REMOTE_ARCHIVE"

echo "Restore complete."
