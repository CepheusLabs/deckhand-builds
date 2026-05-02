# Sovol SV08 Max — MCU firmware

Three MCUs, all CAN-bus (1 Mbit), bridged to Linux via a `gs_usb` USB
adapter (`1d50:606f`). One MCU is the bridge itself; the other two
hang off the CAN bus by UUID.

## Inventory

| MCU | Chip | CAN UUID | Klipper section | Build config | Pre-built blob |
|-----|------|----------|-----------------|--------------|----------------|
| Main / CAN-bridge | STM32H750xx @ 400 MHz | `0d1445047cdd` | `[mcu]` | `main-mcu-h750.config` | **`mcu_klipper.bin`** (vendored from Sovol's MKSDEB, 28,996 bytes) |
| Toolhead / extruder | STM32F103xe @ 72 MHz | `61755fe321ac` | `[mcu extra_mcu]` | `toolhead-chamber-mcu-f103.config` | not published — built from source |
| Chamber | STM32F103xe @ 72 MHz | `58a72bb93aa4` | `[mcu hot_mcu]` | `toolhead-chamber-mcu-f103.config` | not published — built from source |

The two F103 MCUs use the SAME build config — they're distinguished
only by their CAN UUIDs at runtime, so the resulting `.bin` artifact
is interchangeable. Build once, flash twice.

The H750 main MCU's build config differs (uses the
`CONFIG_USBCANBUS=y` mode so the same chip serves as both Klipper MCU
**and** USB-CAN bridge to Linux).

## Source vs. binary distribution

Sovol's public repo ([Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX))
ships:

- All four `.config*` files in `home/sovol/klipper/` — the H750 one,
  two F103 variants, plus `.config.old`.
- One pre-built blob: `home/sovol/zhongchuang/MKSDEB/root/klipper.bin`
  (28,996 bytes, the H750 main-MCU firmware). This is what gets
  installed to `/root/klipper.bin` when Sovol's deb package is
  applied. **It is vendored here verbatim as `mcu_klipper.bin`.**

Sovol does NOT publish pre-built blobs for the toolhead or chamber
MCUs. Both must be built from source against
`toolhead-chamber-mcu-f103.config` using the Klipper tree at
`home/sovol/klipper/`.

## Files in this directory

| File | Purpose |
|------|---------|
| `mcu_klipper.bin` | Pre-built H750 main-MCU firmware. Vendored from Sovol's MKSDEB. |
| `flash_can.py` | Eric Callahan's Katapult/CanBoot uploader. Vendored from Sovol's `home/sovol/printer_data/build/`. |
| `mcu_update_fw.sh` | Sovol's flasher script for the main MCU. Detects Katapult bootloader USB device, then `flash_can.py -u 0d1445047cdd`. |
| `extruder_mcu_update_fw.sh` | Sovol's flasher script for the toolhead MCU. CAN-only flash via `-u 61755fe321ac`. |
| `extra_mcu_update_fw.sh` | Sovol's flasher script for the chamber MCU. CAN-only flash via `-u 58a72bb93aa4`. |
| `main-mcu-h750.config` | Klipper build config for the H750 main MCU (USBCANBUS bridge mode). |
| `main-mcu.config` | Backup copy — Sovol's currently-staged `.config` (sometimes the F103 variant, depending on which config they last built). Kept as a reference. |
| `toolhead-chamber-mcu-f103.config` | Klipper build config for both F103 MCUs. CANSERIAL+CANBUS mode, PB8/PB9 CAN, no USB. |
| `build-mcu-firmware.sh` | Deckhand-invoked builder. Stages a `.config`, runs `make`, copies the resulting `.bin` to a target path. Used by `flows.fresh_flash` and the optional rebuild paths in `flows.stock_keep`. |

## Flash mechanics

All three MCUs are flashed via Katapult/CanBoot — the open-source
serial bootloader Klipper uses on CAN-attached boards. The flow:

1. Klipper sends `RESTART_MCU` over CAN, which (with `bootloader_request=1`
   compiled in) drops the MCU into Katapult bootloader mode.
2. The bootloader announces itself with the same CAN UUID, but now
   accepts Katapult-protocol flash commands.
3. `flash_can.py -i can0 -f <blob> -u <uuid>` writes the new firmware.
4. The bootloader exits and the new firmware boots.

For the H750 main MCU specifically there's a USB-side fallback: when
the chip is in Katapult mode it ALSO appears as a USB device with
serial-by-id pattern `usb-katapult_stm32h750xx*`, so `mcu_update_fw.sh`
can use the USB transport if the CAN side isn't reachable.

The two F103 MCUs are CAN-only — no USB transport, no DFU mode.

## Building from source

Run on the printer (or in any Klipper-tree-equipped environment):

```bash
# Set up env (paths are profile-relative for Deckhand; absolute on the printer)
export KLIPPER_TREE=/home/sovol/klipper
export CONFIG_FILE=/path/to/firmware/toolhead-chamber-mcu-f103.config
export OUTPUT_PATH=/home/sovol/printer_data/build/extruder_mcu_klipper.bin

# Build
./build-mcu-firmware.sh
```

The script handles `apt install` of `gcc-arm-none-eabi` etc. if
they're missing, copies the config into `${KLIPPER_TREE}/.config`,
runs `make clean && make`, and copies `out/klipper.bin` to the
target.

For the chamber MCU, repeat with
`OUTPUT_PATH=/home/sovol/printer_data/build/extra_mcu_klipper.bin`.

For the main MCU on `flows.fresh_flash`, the build is the same shape
with `CONFIG_FILE=main-mcu-h750.config`. The `flows.stock_keep` path
skips the build entirely and uses the pre-vendored
`mcu_klipper.bin` directly.

## Notes on the H750 main MCU's USBCANBUS mode

The H750's `.config750` enables both `CONFIG_MACH_STM32H750=y` and
`CONFIG_USBCANBUS=y` — this is the mode where the chip:

- Acts as a Klipper MCU on its own CAN UUID (`0d1445047cdd`).
- Simultaneously bridges its CAN bus over USB to the Linux host
  (announces itself as a `gs_usb` adapter, USB ID `1d50:614e` per
  the build config; the running unit shows `1d50:606f` because the
  device firmware-side ID was further customized).

This is uncommon but valid — Klipper supports the dual role on H7-class
chips. The implication for flashing is that the main MCU is reachable
both over CAN (via the bridge it itself is providing) AND over USB
(via the Katapult bootloader's USB-CDC mode), so `mcu_update_fw.sh`
can use either path.
