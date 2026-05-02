#!/bin/bash
# Install Sovol's published Sovol Zero stock configs + helper scripts
# from github.com/Sovol3d/SOVOL-ZERO at a pinned commit.
#
# Used by fresh_flash, where the user has just booted a clean BTT CB1
# image and ~/printer_data/config/ doesn't yet contain Sovol's
# printer.cfg / Macro.cfg / chamber_hot.cfg / plr.cfg / etc.
#
# Idempotent across re-runs and across whichever files already exist
# on the target — won't clobber user-customised configs in
# ~/printer_data/config/. This handles both fresh_flash on a clean
# BTT image AND the OS-upgrade path: restore_preserved_state.sh
# writes the user's printer_data first, so this script sees the
# files as present and no-ops on them.

set -e

# Pinned to "zero motherboard" (2025-04-18). Bumping this is a
# conscious action: confirm github.com/Sovol3d/SOVOL-ZERO at the new
# commit still has the same file layout (sovol/ subdir, printer_data/
# config/, pyhelper/, patch/, etc.) and update this constant.
SOVOL_REPO=https://github.com/Sovol3d/SOVOL-ZERO.git
SOVOL_REF=b214ea5c7719e133b5d7b5c73898e24d882d8906

STAGE=~/sovol-stock-stage
CONFIG=~/printer_data/config
HOMEDIR=~

mkdir -p "$CONFIG" "$HOMEDIR/pyhelper" "$HOMEDIR/patch"

# Refresh stage clone.
rm -rf "$STAGE"
git clone --depth 1 --quiet "$SOVOL_REPO" "$STAGE"
cd "$STAGE"
git fetch --depth 1 --quiet origin "$SOVOL_REF"
git checkout --quiet FETCH_HEAD
echo "Cloned $SOVOL_REPO at $(git rev-parse --short HEAD)"

SRC=$STAGE/sovol

# Stock printer.cfg + included configs. Don't clobber a printer.cfg
# the user already customised — only write if absent.
for f in "$SRC/printer_data/config"/*; do
    [ -e "$f" ] || continue
    name=$(basename "$f")
    if [ -e "$CONFIG/$name" ]; then
        echo "Keeping existing $CONFIG/$name"
    else
        cp -p "$f" "$CONFIG/$name"
        echo "Installed $CONFIG/$name"
    fi
done

# Sovol's helper scripts — referenced by Macro.cfg / get_ip.cfg /
# plr.cfg via [gcode_shell_command] entries, so missing them breaks
# the touchscreen menus. Always overwrite — they're small, well-defined,
# and don't carry user state.
for f in get_ip.sh plr.sh clear_plr.sh factory_resets.sh ota_client.sh; do
    cp -p "$SRC/$f" "$HOMEDIR/$f"
    chmod +x "$HOMEDIR/$f"
    echo "Installed $HOMEDIR/$f"
done

# pyhelper: small Moonraker-API wrappers used by the OTA daemon and
# the touchscreen "Show IP" macro.
cp -rp "$SRC/pyhelper/." "$HOMEDIR/pyhelper/"
echo "Installed $HOMEDIR/pyhelper/"

# patch/: factory-reset payload + display-overlay sources.
# install_sovol_klipper_extras.sh handles the klippy/extras/display/
# overlay separately from the embedded klipper-extras/sovol_dev/display/
# tree; staging patch/ here is needed because ~/factory_resets.sh
# expects ~/patch/config/*.cfg as the reset payload.
cp -rp "$SRC/patch/." "$HOMEDIR/patch/"
echo "Staged $HOMEDIR/patch/"

rm -rf "$STAGE"
echo "Done."
