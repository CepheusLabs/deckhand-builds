# MCU Firmware Compatibility

## Current MCU Firmware

Both MCUs are running Klipper firmware built from the Phrozen fork (v0.11.0 era):

### Main MCU (STM32F407VET6)
- **Firmware**: `v0.11.0-122-ge6ef48cd-dirty`
- **Build date**: 2023-03-30
- **Connection**: USB (`/dev/serial/by-id/usb-Klipper_stm32f407xx_550027...`)
- **Commands**: 117 registered
- **Compiler**: arm-none-eabi-gcc 7.3.1

### Toolhead MCU (STM32F103CBT6, alias `MKS_THR`)
- **Firmware**: `v0.11.0-122-ge6ef48cd-dirty`
- **Build date**: 2023-09-06
- **Connection**: UART (`/dev/ttyS0`) at 250000 baud
- **Commands**: 105 registered
- **Compiler**: arm-none-eabi-gcc 7.3.1

## Kalico Compatibility

Kalico checks the MCU firmware app identifier on connect. When it sees "Klipper"
instead of "Kalico", it logs a runtime warning:

```
MCU 'mcu' currently has firmware compiled for Klipper (version v0.11.0-122-...).
It is recommended to re-flash for best compatibility with Kalico
```

**This is a warning only, not a hard error.** Kalico will connect and operate
normally with the existing Klipper MCU firmware. The protocol layer (`msgproto.py`)
is backwards-compatible.

## Benefits of Reflashing (Optional, Future Step)

Once Kalico is verified working with the old firmware:

| Benefit | Details |
|---------|---------|
| Bug fixes | 3+ years of fixes to STM32 drivers (clock, DMA, SPI, I2C) |
| ADC improvements | Better sampling for the filament sensor (`MKS_THR:PA2`) |
| Stepper timing | Improved step pulse timing and acceleration smoothing |
| TMC driver comms | Better TMC5160/TMC2209 UART/SPI communication stability |
| Homing reliability | Improved endstop debouncing and homing sequence |
| Clean startup | No compatibility warning in logs |

## How to Reflash (When Ready)

### Main MCU (STM32F407VET6)

```bash
# On the printer:
cd ~/kalico

# Configure for STM32F407
make menuconfig
# Select: STM32F407, 168MHz, USB (PA11/PA12), 32KiB bootloader offset

# Build
make clean
make

# Enter DFU mode: hold BOOT0 button, press RESET, release BOOT0
# Or use software reset if supported

# Flash
make flash FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_stm32f407xx_550027...
```

### Toolhead MCU (STM32F103CBT6)

```bash
cd ~/kalico

# Configure for STM32F103
make menuconfig
# Select: STM32F103, serial USART1 (PA9/PA10), 28KiB bootloader offset

# Build
make clean
make

# Flash via UART (Klipper can flash over its own serial connection)
make flash FLASH_DEVICE=/dev/ttyS0
```

### Rollback

If MCU flash fails or causes issues, re-flash with the stock firmware:
- The stock MCU firmware binary would need to be extracted from the backup
  tarball or rebuilt from the Phrozen Klipper fork at commit `e6ef48cd`

## Pin Mappings (Reference for menuconfig)

### Main MCU (STM32F407VET6)
- Clock: 168MHz (8MHz crystal, `RESERVE_PINS_crystal=PH0,PH1`)
- USB: PA11/PA12 (`RESERVE_PINS_USB=PA11,PA12`)
- SPI1: PA5/PA6/PA7 (TMC5160 X/Y steppers)
- I2C1: PB6/PB7
- SDIO: PC8-PC12, PD2

### Toolhead MCU (STM32F103CBT6)
- Clock: 72MHz
- Serial: USART1 PA9/PA10 (`RESERVE_PINS_serial=PA10,PA9`), 250000 baud
- SPI1: PA5/PA6/PA7 (ADXL345 accelerometer)
- ADC: PA1 (extruder thermistor), PA2 (filament sensor)
- PWM: PB3 (heater), PB4 (hotend fan), PB5 (part cooling), PB6 (assist fan)
- GPIO: PB8 (extruder step), PB9 (extruder dir), PC13 (extruder enable)
- Endstop: PB12 (X endstop on toolhead)
