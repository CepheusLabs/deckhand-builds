#!/bin/bash
# build-python-3.11.sh
#
# Build Python 3.11 from source on an SBC with only an older Python
# available (stock Phrozen Arco ships 3.7.3 on Armbian Buster).
# Invoked by Deckhand when a profile's firmware choice declares
# `python_min > os.stock.python`.
#
# Runs on the printer via SSH. Non-interactive; exit code communicates
# success. Deckhand's askpass helper handles the internal `sudo` calls
# without needing a pty.
#
# SECURITY:
#   - PYTHON_SHA256 is REQUIRED. Profiles MUST set it to the sha256 of
#     the tarball they expect to receive. This script refuses to run
#     without one and fails hard if the download does not match.
#   - PYTHON_VERSION is constrained to `<major>.<minor>.<patch>` so a
#     malicious profile cannot inject URL-altering metacharacters via
#     this variable.
#   - BUILD_DIR is sanity-checked to prevent `rm -rf ""` or `rm -rf /`
#     if the env var is accidentally unset or set to something bogus.

set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.11.9}"
PYTHON_SHA256="${PYTHON_SHA256:-}"
INSTALL_PREFIX="${INSTALL_PREFIX:-/usr/local}"
BUILD_DIR="${BUILD_DIR:-/tmp/python-build-$$}"
JOBS="${JOBS:-2}"

log()  { printf '[build-python] %s\n' "$*"; }
fail() { printf '[build-python] FAIL: %s\n' "$*" >&2; exit 1; }

# ------------------------------------------------------------------
# Input validation - refuse to proceed with unsafe arguments.

if ! [[ "$PYTHON_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    fail "PYTHON_VERSION must be <major>.<minor>.<patch>, got: $PYTHON_VERSION"
fi

if ! [[ "$PYTHON_SHA256" =~ ^[0-9a-f]{64}$ ]]; then
    fail "PYTHON_SHA256 must be a 64-character hex sha256. \
Profiles MUST pin this to the expected tarball hash. \
Look it up at https://www.python.org/downloads/release/python-${PYTHON_VERSION//./}/"
fi

# ~$$ alone is not guaranteed empty-safe under all shells when the var
# is unset by the caller, so check explicitly.
case "$BUILD_DIR" in
    ""|"/"|"//"|"/*")
        fail "BUILD_DIR is empty or root - refusing to proceed"
        ;;
esac

if command -v python3.11 >/dev/null 2>&1; then
    log "python3.11 already installed at $(command -v python3.11); skipping."
    exit 0
fi

if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# ------------------------------------------------------------------
# apt install - minimal deps for a Klippy-capable Python
#
# We only install the libraries Klippy actually uses when it imports
# standard-library modules. Tutorials list a much longer set (tk,
# ncurses, gdbm, readline, ...) because they're building a "full"
# Python for interactive use. Klippy doesn't need any of that.
#
# Why so short:
#   build-essential  - gcc/make to compile cpython itself
#   zlib1g-dev       - `zlib` (pip wheels + klippy's gzip usage)
#   libssl-dev       - `ssl` + `hashlib` (pip over HTTPS, requests)
#   libffi-dev       - `ctypes` (cryptography wheel, several pip deps)
#   libsqlite3-dev   - `sqlite3` (pip's wheel cache)
#   libbz2-dev       - `bz2` (some klippy extras)
#   liblzma-dev      - `lzma` (xz tarballs in upstream fetches)
#   wget + ca-certs  - fetching the cpython tarball itself
#
# Notably NOT installed:
#   libncurses5-dev  - pulls in a strict version of libtinfo6 that
#                      conflicts with whatever the stock printer image
#                      already has (Phrozen ships a newer patch level
#                      than archive.debian.org's EOL snapshot). Klippy
#                      doesn't import `curses`, so we skip it and the
#                      conflict disappears.
#   tk-dev           - `tkinter`, not used.
#   libgdbm-dev      - `gdbm`, not used.
#   libreadline-dev  - nicer interactive prompt, not used at runtime.
#   uuid-dev         - Python's `uuid` module works without the libuuid
#                      headers; it only uses them for faster gen if
#                      available.
#   libnss3-dev      - Mozilla NSS, a different crypto stack from
#                      OpenSSL; Python uses OpenSSL via libssl-dev.

export DEBIAN_FRONTEND=noninteractive

BUILD_DEPS=(
    build-essential
    zlib1g-dev
    libssl-dev
    libffi-dev
    libsqlite3-dev
    libbz2-dev
    liblzma-dev
    wget
    ca-certificates
    coreutils
)

log "apt-get update (retry once on transient failure)..."
if ! $SUDO apt-get update -qq; then
    log "first update failed, retrying after 5s..."
    sleep 5
    $SUDO apt-get update -qq || fail "apt-get update failed twice"
fi

log "Installing build dependencies..."
# --no-upgrade: don't touch packages that are already installed at a
# working version. Keeps us from churning system libs just because
# archive.debian.org has a slightly different patch level than what
# Phrozen originally shipped.
if ! $SUDO apt-get install -y -qq --no-upgrade "${BUILD_DEPS[@]}"; then
    fail "apt install failed; see output above for the broken package(s)"
fi

# ------------------------------------------------------------------
# Fetch, verify, configure, build, install

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

TARBALL="Python-$PYTHON_VERSION.tar.xz"
URL="https://www.python.org/ftp/python/$PYTHON_VERSION/$TARBALL"

log "Fetching $URL..."
# HTTPS only - python.org enforces TLS but belt-and-suspenders via the
# URL constant above. If an upstream mirror ever switches to a http://
# redirect we want the download to fail, not silently weaken.
wget --https-only -q "$URL" -O "$TARBALL" || fail "download failed"

log "Verifying sha256 ($PYTHON_SHA256)..."
# sha256sum -c reads `<expected>  <filename>` from stdin. `--status`
# suppresses the per-file output; the exit code is what we care about.
printf '%s  %s\n' "$PYTHON_SHA256" "$TARBALL" | sha256sum --check --status \
    || fail "sha256 mismatch on $TARBALL - refusing to build. Expected $PYTHON_SHA256"

tar -xf "$TARBALL"
cd "Python-$PYTHON_VERSION"

log "Configuring..."
# No --enable-optimizations / PGO: avoids OOM on 1GB boards. Users who
# want a PGO build can re-run with PYTHON_OPTIMIZATIONS=1 set.
CONFIGURE_ARGS=(
    "--prefix=$INSTALL_PREFIX"
    "--enable-shared"
    "LDFLAGS=-Wl,-rpath=$INSTALL_PREFIX/lib"
)
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
# Re-check BUILD_DIR just before the destructive call, in case something
# unset it mid-script (shouldn't happen under `set -u`, but cheap).
case "$BUILD_DIR" in
    ""|"/"|"//"|"/*")
        log "WARN: BUILD_DIR is empty or root at cleanup - leaving tree alone"
        ;;
    *)
        rm -rf -- "$BUILD_DIR"
        ;;
esac

log "Done. python3.11 is at $INSTALL_PREFIX/bin/python3.11"
"$INSTALL_PREFIX/bin/python3.11" --version
