#!/bin/bash
# First-time installation of arco_screen daemon (voronFDM replacement).
#
# What this does:
#   1. Installs Python dependencies into the Kalico venv
#   2. Creates the config directory at ~/printer_data/config/arco_screen/
#   3. Migrates any existing voronFDM config files (use_conf.txt, plr data)
#   4. Stops and disables voronFDM
#   5. Installs and enables the arco-screen systemd service
#   6. Adds the update_manager section to moonraker.conf (if not present)
#
# After running: sudo systemctl start arco-screen
#
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV="$HOME/kalico-env"
SERVICE_NAME="arco-screen"
PRINTER_DATA="$HOME/printer_data"
CONFIG_DIR="$PRINTER_DATA/config/arco_screen"
MOONRAKER_CONF="$PRINTER_DATA/config/moonraker.conf"

# Legacy voronFDM config locations (tried in order)
LEGACY_DIRS=(
    "$HOME/klipper/klippy/extras/phrozen_dev/serial-screen"
    "$HOME/kalico/klippy/extras/phrozen_dev/serial-screen"
)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "============================================"
echo "  arco_screen daemon installer"
echo "  (voronFDM replacement)"
echo "============================================"
echo ""

# --- 1. Python dependencies ---
if [ ! -d "$VENV" ]; then
    error "Python venv not found at $VENV"
    echo "       Install Kalico first (scripts/setup.sh)."
    exit 1
fi

info "[1/6] Installing Python dependencies..."
"$VENV/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
info "  Done"

# --- 2. Config directory ---
info "[2/6] Creating config directory..."
mkdir -p "$CONFIG_DIR"
info "  $CONFIG_DIR"

# --- 3. Migrate legacy config ---
info "[3/6] Checking for legacy voronFDM config..."
MIGRATED=false

for LEGACY_DIR in "${LEGACY_DIRS[@]}"; do
    if [ -d "$LEGACY_DIR" ]; then
        info "  Found legacy config at $LEGACY_DIR"

        # use_conf.txt - machine settings
        if [ -f "$LEGACY_DIR/use_conf.txt" ] && [ ! -f "$CONFIG_DIR/use_conf.txt" ]; then
            cp "$LEGACY_DIR/use_conf.txt" "$CONFIG_DIR/use_conf.txt"
            info "  Migrated use_conf.txt"
            MIGRATED=true
        fi

        # plr_print_precfg.json - AMS/ChromaKit config
        if [ -f "$LEGACY_DIR/plr_print_precfg.json" ] && [ ! -f "$CONFIG_DIR/plr_print_precfg.json" ]; then
            cp "$LEGACY_DIR/plr_print_precfg.json" "$CONFIG_DIR/plr_print_precfg.json"
            info "  Migrated plr_print_precfg.json"
            MIGRATED=true
        fi

        # plr_data.json - power loss recovery state
        if [ -f "$LEGACY_DIR/plr_data.json" ] && [ ! -f "$CONFIG_DIR/plr_data.json" ]; then
            cp "$LEGACY_DIR/plr_data.json" "$CONFIG_DIR/plr_data.json"
            info "  Migrated plr_data.json"
            MIGRATED=true
        fi

        break
    fi
done

if [ "$MIGRATED" = false ]; then
    info "  No legacy config found (fresh install)"
fi

# --- 4. Stop and disable voronFDM ---
info "[4/6] Disabling voronFDM..."

# Kill running voronFDM process
if pgrep -x voronFDM >/dev/null 2>&1; then
    sudo killall voronFDM 2>/dev/null || true
    info "  Stopped voronFDM process"
fi

# Disable the systemd service if it exists
if systemctl list-unit-files voronFDM.service >/dev/null 2>&1; then
    sudo systemctl stop voronFDM.service 2>/dev/null || true
    sudo systemctl disable voronFDM.service 2>/dev/null || true
    info "  Disabled voronFDM.service"
fi

# Prevent it from being started again by making the binary non-executable
# (we don't delete it — user might want to revert)
for BIN_PATH in /usr/local/bin/voronFDM /home/mks/voronFDM /home/mks/klipper/klippy/extras/phrozen_dev/voronFDM; do
    if [ -x "$BIN_PATH" ]; then
        sudo chmod -x "$BIN_PATH"
        info "  Disabled $BIN_PATH (chmod -x)"
    fi
done

info "  Done"

# --- 5. Install systemd service ---
info "[5/6] Installing arco-screen systemd service..."

sudo cp "$SCRIPT_DIR/arco-screen.service" /etc/systemd/system/arco-screen.service
sudo systemctl daemon-reload
sudo systemctl enable arco-screen.service
info "  Service installed and enabled"

# --- 6. Add update_manager section to moonraker.conf ---
info "[6/6] Configuring Moonraker update manager..."

if [ -f "$MOONRAKER_CONF" ]; then
    if ! grep -q '\[update_manager arco-screen\]' "$MOONRAKER_CONF" 2>/dev/null; then
        cat >> "$MOONRAKER_CONF" << 'MOONRAKER_EOF'

[update_manager arco-screen]
type: git_repo
path: ~/phrozen-arco-kalico
origin: https://github.com/CepheusLabs/phrozen-arco-kalico.git
primary_branch: main
managed_services: arco-screen
install_script: screen-daemon/install.sh
MOONRAKER_EOF
        info "  Added [update_manager arco-screen] to moonraker.conf"
    else
        info "  update_manager section already present"
    fi
else
    warn "  moonraker.conf not found at $MOONRAKER_CONF"
    warn "  You'll need to add the update_manager section manually."
fi

# --- Done ---
echo ""
echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo ""
echo "  Start:   sudo systemctl start arco-screen"
echo "  Status:  sudo systemctl status arco-screen"
echo "  Logs:    journalctl -u arco-screen -f"
echo ""
echo "  Config:  $CONFIG_DIR"
echo "  Service: /etc/systemd/system/arco-screen.service"
echo ""

# Start it if the user wants. Deckhand invokes this script over SSH
# without a pty, so `read -p` would hang indefinitely waiting for input
# that can never arrive (the installer's step timeout would then fire
# and abort the whole flow with a timeout error that masks what
# really happened). Gate the prompt on `[ -t 0 ]` so it only fires
# when the script is run interactively from a real terminal. In the
# automated path, default to Y (start the service) - that's the
# overwhelmingly common user intent.
if [ -t 0 ]; then
    read -p "Start arco-screen now? [Y/n]: " start_choice
else
    start_choice="Y"
fi

if [ "$start_choice" != "n" ] && [ "$start_choice" != "N" ]; then
    sudo systemctl start arco-screen
    sleep 2
    if systemctl is-active --quiet arco-screen; then
        info "arco-screen is running!"
        echo "  Logs: journalctl -u arco-screen -f"
    else
        error "arco-screen failed to start"
        echo "  Check: journalctl -u arco-screen --no-pager -n 30"
    fi
fi
