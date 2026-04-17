#!/bin/bash
# Wake UART1 on RK3328 (MKS-PI) by toggling the dw-apb-uart driver.
#
# The kernel's runtime PM can leave UART1 suspended with clocks gated.
# Unbinding and rebinding the platform driver forces a full re-init
# with pclk_uart1 and sclk_uart1 enabled.
#
# This script is called by systemd ExecStartPre with root privileges
# (via the '+' prefix).  It is idempotent.

set -e

DEV="ff120000.serial"
DRIVER="/sys/bus/platform/drivers/dw-apb-uart"
POWER="/sys/devices/platform/${DEV}/power"

# Check if already active
STATUS=$(cat "${POWER}/runtime_status" 2>/dev/null || echo "unknown")
if [ "$STATUS" = "active" ]; then
    exit 0
fi

echo "UART1 runtime_status=$STATUS, forcing driver rebind..." >&2

# Unbind (releases /dev/ttyS1)
echo "$DEV" > "${DRIVER}/unbind" 2>/dev/null || true
sleep 0.5

# Rebind (re-creates /dev/ttyS1 with clocks enabled)
echo "$DEV" > "${DRIVER}/bind" 2>/dev/null || true
sleep 0.5

# Pin power control to 'on' to prevent re-suspension
echo "on" > "${POWER}/control" 2>/dev/null || true

echo "UART1 rebind complete" >&2
