#!/bin/bash
# Flash ChromaKit (MMU) firmware
# Usage: ./flash-chromakit.sh <firmware.bin>
#
# The ChromaKit uses a proprietary STM32 serial bootloader protocol.
# Flashing requires temporarily running phrozen_master (serial relay)
# and phrozen_slave_ota (flash tool). These are only started for the
# duration of the flash and killed afterward.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIRMWARE="$1"

if [ -z "$FIRMWARE" ]; then
    echo "ChromaKit Firmware Flash Tool"
    echo "============================="
    echo ""
    echo "Usage: $0 <firmware.bin>"
    echo ""
    echo "Available ChromaKit firmware versions:"
    ls -1 "$SCRIPT_DIR/chromakit/" 2>/dev/null | sed 's/^/  /' || echo "  (none found)"
    echo ""
    echo "Example:"
    echo "  $0 $SCRIPT_DIR/chromakit/FW_Arco-AMS_H1I1_V25328.bin"
    exit 1
fi

# Resolve relative path
if [ ! -f "$FIRMWARE" ]; then
    # Try relative to chromakit dir
    if [ -f "$SCRIPT_DIR/chromakit/$FIRMWARE" ]; then
        FIRMWARE="$SCRIPT_DIR/chromakit/$FIRMWARE"
    else
        echo "Error: firmware file not found: $FIRMWARE"
        exit 1
    fi
fi

# Check tools exist
MASTER="$SCRIPT_DIR/tools/phrozen_master"
SLAVE_OTA="$SCRIPT_DIR/tools/phrozen_slave_ota"

if [ ! -x "$MASTER" ]; then
    echo "Error: phrozen_master not found at $MASTER"
    exit 1
fi
if [ ! -x "$SLAVE_OTA" ]; then
    echo "Error: phrozen_slave_ota not found at $SLAVE_OTA"
    exit 1
fi

echo "ChromaKit Firmware Flash"
echo "========================"
echo "Firmware: $(basename "$FIRMWARE")"
echo "Size:     $(stat -c%s "$FIRMWARE" 2>/dev/null || stat -f%z "$FIRMWARE") bytes"
echo ""
echo "This will temporarily stop Klipper and run the Phrozen flash tools."
echo "No network connections will be made - the tools only access local serial ports."
echo ""
read -p "Continue? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

# Ensure cleanup on exit
cleanup() {
    echo ""
    echo "Cleaning up..."
    killall phrozen_slave_ota 2>/dev/null || true
    killall phrozen_master 2>/dev/null || true
    sleep 1
    echo "Restarting Klipper..."
    sudo systemctl start klipper
}
trap cleanup EXIT

# Stop Klipper to release serial ports
echo ""
echo "[1/5] Stopping Klipper..."
sudo systemctl stop klipper
sleep 2

# Copy firmware to where the OTA tool expects it
# The slave_ota reads from the phrozen_dev directory alongside DriveCodeFile.dat
echo "[2/5] Staging firmware..."
PHROZEN_DEV_DIR="$(find /home -path "*/klippy/extras/phrozen_dev" -type d 2>/dev/null | head -1)"
if [ -z "$PHROZEN_DEV_DIR" ]; then
    PHROZEN_DEV_DIR="/home/mks/kalico/klippy/extras/phrozen_dev"
fi
cp "$FIRMWARE" "$PHROZEN_DEV_DIR/" 2>/dev/null || true

# Start phrozen_master (serial port relay - local only)
echo "[3/5] Starting serial relay..."
# Block network access for phrozen_master using iptables
sudo iptables -A OUTPUT -m owner --uid-owner $(id -u) -d 42.193.239.84 -j DROP 2>/dev/null || true
sudo iptables -A OUTPUT -m owner --uid-owner $(id -u) -p tcp --dport 7000 -j DROP 2>/dev/null || true

chmod +x "$MASTER" "$SLAVE_OTA"
"$MASTER" >/dev/null 2>&1 &
MASTER_PID=$!
sleep 3

# Start flash process
echo "[4/5] Flashing ChromaKit firmware..."
echo "      This may take 1-2 minutes..."
"$SLAVE_OTA" 2>&1 &
SLAVE_PID=$!

# Wait for flash to complete (timeout 120s)
TIMEOUT=120
ELAPSED=0
while kill -0 $SLAVE_PID 2>/dev/null && [ $ELAPSED -lt $TIMEOUT ]; do
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo "      ... $ELAPSED seconds"
done

if kill -0 $SLAVE_PID 2>/dev/null; then
    echo "Warning: flash process timed out after ${TIMEOUT}s"
    kill $SLAVE_PID 2>/dev/null
fi

echo "[5/5] Flash process complete."

# Remove iptables rules
sudo iptables -D OUTPUT -m owner --uid-owner $(id -u) -d 42.193.239.84 -j DROP 2>/dev/null || true
sudo iptables -D OUTPUT -m owner --uid-owner $(id -u) -p tcp --dport 7000 -j DROP 2>/dev/null || true

# cleanup() runs via trap, restarts Klipper
echo ""
echo "Done. Check ChromaKit connection after Klipper restarts."
echo "Run 'P28' in the console to reconnect, then 'PRZ_VERSION' to verify."
