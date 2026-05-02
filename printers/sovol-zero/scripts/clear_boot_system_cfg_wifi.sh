#!/bin/bash
# Clear the WIFI_SSID and WIFI_PASSWD fields in /boot/system.cfg.
#
# Stock Sovols ship that file with WIFI_SSID="ZYIPTest" /
# WIFI_PASSWD="12345678" — the factory test wifi credentials in
# cleartext on a FAT partition any user with a card reader can mount.
# /boot/scripts/connect_wifi.sh sources this file at every boot and
# tries to (re)connect to that SSID, which means a stock unit on a
# network where "ZYIPTest" exists as an attacker SSID with the same
# password will silently associate to the attacker.
#
# Other fields in /boot/system.cfg (TimeZone, ks_angle, BTT_PAD7,
# TOUCH_VIBRATION, TOUCH_SOUND, AUTO_BRIGHTNESS) stay — they are the
# user-facing knobs the file exists for. Only the wifi pair is wiped.
#
# A timestamped backup of the original is kept alongside the file so
# the user can recover their cleartext PSK in the rare case they
# wanted it.

set -e

CFG=/boot/system.cfg
TS=$(date -u +%Y%m%dT%H%M%SZ)
BAK="${CFG}.deckhand-pre-${TS}.bak"

if [ ! -f "$CFG" ]; then
    echo "$CFG does not exist; nothing to clear"
    exit 0
fi

echo "Backing up $CFG to $BAK"
sudo cp -p "$CFG" "$BAK"

echo "Clearing WIFI_SSID / WIFI_PASSWD"
sudo sed -i -E 's/^WIFI_SSID=.*/WIFI_SSID=""/' "$CFG"
sudo sed -i -E 's/^WIFI_PASSWD=.*/WIFI_PASSWD=""/' "$CFG"

echo "After:"
sudo grep -E '^(WIFI_SSID|WIFI_PASSWD)=' "$CFG"
