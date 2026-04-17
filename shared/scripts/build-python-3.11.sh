#!/bin/bash
# build-python-3.11.sh
#
# Build Python 3.11 from source on an SBC with only Python 3.7 available
# (stock Phrozen Arco on Armbian Buster). Invoked by Deckhand when a
# profile's firmware choice declares python_min > system python.
#
# Runs on the printer via SSH. Non-interactive; exit code communicates
# success.

set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.11.9}"
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
BUILD_DIR="${BUILD_DIR:-/tmp/python-build-$$}"
JOBS="${JOBS:-2}"

log()  { printf '[build-python] %s\n' "$*"; }
fail() { printf '[build-python] FAIL: %s\n' "$*" >&2; exit 1; }

if command -v python3.11 >/dev/null 2>&1; then
    log "python3.11 already installed at $(command -v python3.11); skipping."
    exit 0
fi

if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

log "Installing build dependencies..."
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq \
    build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev \
    libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev \
    liblzma-dev uuid-dev tk-dev wget

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

TARBALL="Python-$PYTHON_VERSION.tar.xz"
URL="https://www.python.org/ftp/python/$PYTHON_VERSION/$TARBALL"

log "Fetching $URL..."
wget -q "$URL" -O "$TARBALL"
tar -xf "$TARBALL"
cd "Python-$PYTHON_VERSION"

log "Configuring..."
# No --enable-optimizations / PGO: avoids OOM on 1GB boards. Users who want
# a PGO build can re-run this with PYTHON_OPTIMIZATIONS=1 set.
CONFIGURE_ARGS=("--prefix=$INSTALL_PREFIX" "--enable-shared" "LDFLAGS=-Wl,-rpath=$INSTALL_PREFIX/lib")
if [ "${PYTHON_OPTIMIZATIONS:-0}" = "1" ]; then
    CONFIGURE_ARGS+=("--enable-optimizations")
fi
./configure "${CONFIGURE_ARGS[@]}" >/dev/null

log "Compiling (this takes ~20 minutes on a 1GB RK3328)..."
make -j"$JOBS" 2>&1 | tail -n 5

log "Installing..."
$SUDO make altinstall 2>&1 | tail -n 5

# Double-check the binary is on PATH under the standard name we need.
if ! "$INSTALL_PREFIX/bin/python3.11" --version >/dev/null 2>&1; then
    fail "Python 3.11 did not install successfully at $INSTALL_PREFIX/bin/python3.11."
fi

log "Cleaning up build tree..."
cd /
rm -rf "$BUILD_DIR"

log "Done. python3.11 is at $INSTALL_PREFIX/bin/python3.11"
"$INSTALL_PREFIX/bin/python3.11" --version
