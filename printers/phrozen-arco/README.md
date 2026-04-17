# Phrozen Arco profile

Deckhand profile for the [Phrozen Arco][arco] — a CoreXY FDM with a
Rockchip RK3328 SBC, TJC serial touchscreen, and the ChromaKit AMS.

**Status:** `alpha`. Profile structure is complete, flows are declared but
not yet validated end-to-end on real hardware through Deckhand.

## What's here

| Path | What it is |
|------|-----------|
| `profile.yaml` | The manifest Deckhand reads. Drives detection, the wizard, and every install step. |
| `configs/` | `printer.cfg`, `printer_MCU.cfg`, `printer_gcode_macro.cfg`, `moonraker.conf`, `fluidd.cfg`, `KlipperScreen.conf`, `crowsnest.conf` — all pinned for the Arco's hardware. |
| `klipper-extras/phrozen_dev/` | ChromaKit AMS support module (self-contained Klipper extras). |
| `klipper-extras/CatchIP.py` | Small helper extra that surfaces the printer's LAN IP in klippy state. |
| `firmware/flash-chromakit.sh` | On-demand flash script for the ChromaKit MCU. Uses Phrozen proprietary helper binaries from the stock install (not bundled here — see note below). |
| `screen-daemon/arco_screen/` | Open-source replacement for voronFDM (TJC/Nextion touchscreen ↔ Moonraker bridge). |
| `moonraker/chromakit_proxy.py` | Moonraker component that proxies ChromaKit status to the web UI. |
| `kiauh-extension/` | Optional KIAUH extension that adds "Phrozen Arco" as a one-click preset. |
| `docs/` | Reference documentation — stock-OS audit, MCU flash notes, ChromaKit command protocol, firmware reverse-engineering notes, etc. |

## What's deliberately NOT here

Content that's either proprietary to Phrozen or too large / irrelevant to
ship with a profile:

| Missing artifact | Where to get it |
|------------------|-----------------|
| `voronFDM` binary | Copy from your own stock eMMC at `/home/mks/voronFDM` if you want the stock screen daemon (see profile's `screens.voronFDM.restore_paths`). |
| `phrozen_master`, `phrozen_slave_ota` ARM binaries | Kept in-place on the stock install; `flash-chromakit.sh` uses them transiently. Don't remove them from the stock `klippy/extras/phrozen_dev/frp-oms/` tree if you want ChromaKit firmware flashing to keep working. |
| TJC screen firmware (`.tft` blobs) | Phrozen proprietary. Ship on your unit already; no known OSS path. |
| ChromaKit MCU firmware (`.bin` blobs) | Phrozen proprietary. Whatever ships on your unit is the baseline. |

## Reference docs

The files in `docs/` are the result of reverse-engineering Phrozen's stock
install, decoding the ChromaKit serial protocol, and documenting the MCU
hardware. Worth reading before contributing to this profile:

- [`docs/STOCK-INVENTORY.md`](docs/STOCK-INVENTORY.md) — full audit of
  every Phrozen/MKS service, file, and network indicator on stock.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — hardware + software
  topology.
- [`docs/CHROMAKIT-COMMANDS.md`](docs/CHROMAKIT-COMMANDS.md) — gcode
  surface for the AMS.
- [`docs/CHROMAKIT-FIRMWARE-RE.md`](docs/CHROMAKIT-FIRMWARE-RE.md) —
  reverse-engineering notes on the ChromaKit firmware.
- [`docs/MCU-COMPATIBILITY.md`](docs/MCU-COMPATIBILITY.md) / `MCU-FLASH-NOTES.md`
  — STM32F407 + STM32F103 build configs and flash procedures.
- [`docs/REMOVED-SERVICES.md`](docs/REMOVED-SERVICES.md) — detailed
  rationale for every service Deckhand drops.

## Promoting this profile

Status lifecycle is `stub → alpha → beta → stable`. To promote:

1. Run the stock-keep flow end-to-end against a real Arco, document any
   issues, resolve them.
2. Run the fresh-flash flow end-to-end against a real Arco. Same.
3. Verify power-loss recovery still works through `arco_screen`.
4. Bump `profile_version` and `status` in `profile.yaml`, open a PR with
   a validation-notes section in the PR description.

[arco]: https://www.phrozen3d.com/products/arco-fdm-3d-printer
