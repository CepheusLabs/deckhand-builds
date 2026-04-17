# Upstream Tracking

How to stay current with both Kalico (base firmware) and Phrozen (AMS protocol).

## Kalico (Primary Upstream)

Kalico is actively maintained with weekly commits. It tracks mainline Klipper
and adds features on top.

### Setup (on the printer)

```bash
cd /home/mks/klipper
git remote add kalico https://github.com/KalicoCrew/kalico.git
git fetch kalico
```

### Checking for Updates

```bash
cd /home/mks/klipper
git fetch kalico
git log HEAD..kalico/main --oneline
```

### Applying Updates

The phrozen_dev extras module and CatchIP.py sit in `klippy/extras/` which
is outside the normal Klipper update path. A Kalico update should not
overwrite them.

```bash
cd /home/mks/klipper
git fetch kalico
git merge kalico/main
# Resolve any conflicts in the 2-3 patched files
# (virtual_sdcard.py, display_status.py)
# Then restart klipper
sudo systemctl restart klipper
```

If there are conflicts in the patched files, check if Kalico has added the
same functionality natively (e.g., SDCARD_SELECT_FILE, IP in status).

## Phrozen (AMS Protocol Updates)

Phrozen barely commits (2 commits in 16 months as of 2026-04). Their AMS
protocol updates are the only thing we care about.

### Setup (on your workstation)

```bash
cd /path/to/phrozen-arco-kalico
git clone https://github.com/phrozen3d/klipper.git /tmp/phrozen-klipper
```

### Checking for Updates

```bash
cd /tmp/phrozen-klipper
git fetch origin
# Check for new commits since the last known
git log cb087013..origin/phrozen-stable --oneline
```

If there are new commits, diff the phrozen_dev directory specifically:

```bash
git diff cb087013..origin/phrozen-stable -- klippy/extras/phrozen_dev/
```

### What to Look For

- **cmds.py changes**: New AMS commands, protocol changes, tool change logic
- **base.py changes**: New firmware version constants, new hardware IDs
- **dev.py changes**: New event handlers, timer changes, serial protocol updates
- **New files**: Additional peripherals, new screen protocol support

### Applying Phrozen Updates

Cherry-pick or manually port relevant changes into the phrozen_dev module
in this repo. Most Phrozen commits are bulk updates that include unrelated
changes (comment blocks, OTA code, FRP config) - only extract the AMS
protocol-relevant parts.

## Version Tracking

Keep track of which versions are deployed:

| Component | Current Base | Last Updated |
|-----------|-------------|--------------|
| Kalico | TBD (latest main at deploy time) | TBD |
| phrozen_dev | Based on `cb087013` (2026-01-13) | TBD |
| Moonraker | Stock upstream (latest at deploy time) | TBD |
| STM32F407 MCU firmware | Stock Phrozen (not reflashed) | N/A |
| STM32F103 Toolhead firmware | Stock Phrozen (not reflashed) | N/A |
| voronFDM | Stock Phrozen binary | N/A |
| TJC Screen firmware | Stock Phrozen (not reflashed) | N/A |
