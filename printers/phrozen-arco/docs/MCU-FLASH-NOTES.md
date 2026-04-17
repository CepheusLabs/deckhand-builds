# MCU Flashing Notes

## What Happened

During the Kalico migration, the MCU firmware needed updating because
Kalico's protocol changed the `query_adxl345` command signature.

### Main MCU (STM32F407VET6) - FLASHED SUCCESSFULLY

- Connected via USB
- Entered DFU mode automatically when Klipper sent bootloader request
- Flashed with: `make flash FLASH_DEVICE=0483:df11`
- Now running Kalico firmware version 1257292

### Toolhead MCU (STM32F103CBT6) - NOT YET FLASHED

Connected via UART `/dev/ttyS0` at 250000 baud. Multiple approaches tried:

1. **`make flash`** - Fails because it expects a USB device, not UART
2. **`make serialflash`** - Uses stm32flash which needs STM32 system bootloader
   (BOOT0 pin high during reset). Can't be done remotely.
3. **`flash_can.py`** - Speaks Klipper/Katapult bootloader protocol, but the MCU
   doesn't enter the bootloader after FIRMWARE_RESTART
4. **Manual serial reset** - Tried sending raw Klipper protocol bytes to trigger
   `request_bootloader` command. MCU doesn't stay in bootloader long enough.
5. **Old Klipper + FIRMWARE_RESTART** - Started stock Klipper v0.11.0 (which can
   connect to the old toolhead firmware), sent FIRMWARE_RESTART via Moonraker API.
   MCU resets but boots back into application, not bootloader.

### The Issue

The toolhead MCU's `restart_method: command` does a normal reset. The Klipper
bootloader (if present at 0x8000000-0x8006FFF) only pauses for ~100ms to check
for a flash request before jumping to the application. The `flash_can.py` tool
can't connect fast enough over UART.

It's also possible this MCU was originally flashed via SWD/JTAG or with BOOT0
jumpered, and doesn't have a Klipper bootloader installed at all.

### Options to Flash the Toolhead MCU

1. **Physical access**: Hold BOOT0 high (jumper or button) during reset, then use
   `stm32flash -w klipper.bin -v -g 0x8007000 -b 57600 /dev/ttyS0`
2. **SWD/JTAG**: Connect an ST-Link or similar programmer
3. **Install Katapult first**: Flash a Katapult bootloader via method 1 or 2, then
   future updates can be done over serial without physical access
4. **Accept the limitation**: Comment out ADXL345 config. Everything else works.
   The accelerometer is only needed for input shaper calibration.

### Current Workaround

ADXL345 and resonance_tester sections commented out in printer.cfg.
Input shaper values from previous calibration are preserved in the
SAVE_CONFIG section (shaper_freq_x=56.8, shaper_freq_y=42.8).

### Build Configs Used

Main MCU (STM32F407):
- STM32F407, 168MHz, 8MHz crystal
- USB on PA11/PA12
- 32KiB bootloader offset (0x8008000)

Toolhead MCU (STM32F103) - BUILT BUT NOT FLASHED:
- STM32F103, 72MHz, 8MHz crystal
- Serial USART1 on PA9/PA10, 250000 baud
- 28KiB bootloader offset (0x8007000)
