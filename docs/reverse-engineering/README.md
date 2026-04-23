# Reverse-engineering artefacts

This directory holds decompiled / reverse-engineered files we captured
while figuring out how stock vendor firmware is structured. They are
reference-only: nothing here is executed, bundled, or uploaded to a
printer by Deckhand.

## Layout

- `phrozen-arco/klipper-extras/phrozen_dev/` - decompiled
  `*_dead.py` Python modules recovered from the stock Arco eMMC image.
  Originally lived under
  `printers/phrozen-arco/klipper-extras/phrozen_dev/` before we
  realised they were not shipped as part of the Deckhand build and
  should not be packaged alongside the printer profile.

## Why keep them

Future debugging of stock behaviour (e.g. the Phrozen HDL gateway, the
FRP reverse-tunnel, or the custom KlipperScreen fork) is much easier
with the original source side-by-side. They inform what the profile
detectors flag as stock-OS bloat in `profile.yaml`.

## Rules

- Do not reference any file in this tree from a `profile.yaml`.
- Do not link-extras / upload from here.
- Treat the contents as documentation, not runtime code.
