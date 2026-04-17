# ChromaKit Firmware Reverse Engineering

Deep analysis of the ChromaKit MMU firmware (`FW_Arco-AMS_H1I1_V25328.bin`) for the purpose of creating open-source replacement firmware.

## MCU Identification

The ChromaKit board runs on an **STM32F103CBT6** (ARM Cortex-M3):

- **Flash**: 128 KB at `0x08000000` (firmware is 145 KB — may use an STM32F103RCT6 with 256 KB, or an external section)
- **RAM**: Base `0x20000000`, initial SP at `0x200044D8` (~17.4 KB stack)
- **Peripherals confirmed via base addresses**:
  - RCC at `0x40021000` (STM32F1 family)
  - FLASH registers at `0x40022000` (STM32F1 family)
  - AFIO at `0x40010000`
  - GPIO A-E at `0x40010800`–`0x40011800`
- **Clock**: Likely 72 MHz HSE (standard for F103)
- **No STM32F4 peripheral addresses found** (rules out F4 family)

### Vector Table (76 entries, 60 IRQs)

| Vector | Address | Handler |
|--------|---------|---------|
| Initial SP | — | `0x200044D8` |
| Reset | 0x04 | `0x08006239` |
| NMI | 0x08 | `0x0801F1EF` |
| HardFault | 0x0C | `0x0801DDA3` |
| MemManage | 0x10 | `0x0801F1ED` |
| BusFault | 0x14 | `0x0801906D` |
| UsageFault | 0x18 | `0x0802272F` |
| Default handler | — | `0x08006253` (used for most unused IRQs) |

12 unique non-default interrupt handlers are registered.

## Original Source Files

The firmware preserves debug strings with source file annotations:

| File | Purpose |
|------|---------|
| `App.c` | Main application logic — motor control, command handling, state machines |
| `App.cpp` | Heartbeat/connection management |
| `App_Heater.c` | Heater (drying chamber) control |
| `FM175XX.c` | NFC chip driver (FM175XX — NFC filament tag reader) |
| `Global.c` | System info printing, global state, sensor status reporting |
| `Hw.c` | Hardware abstraction — segment LCD init, system timer init |
| `HwIRQ.c` | Interrupt/peripheral initialization — ADC, SPI, TIM, UART, GPIO |
| `main.c` | Entry point |
| `type_a.c` | NFC Type-A card protocol (ISO 14443A for filament NFC tags) |

## Peripheral Map

### Timers

| Timer | Function | Init Function |
|-------|----------|---------------|
| TIM1 | AMS motor PWM (channels 1-4?) | `HwIRQ_TIM1AndTIM4PWMAMSMotorInit` |
| TIM2 | AMS motor PWM (additional) | `HwIRQ_TIM1AndTIM4PWMAMSMotorInit` |
| TIM3 | System tick / timing (1ms?) | `HwIRQTIM3Init` |
| TIM4 | AMS motor PWM | `HwIRQ_TIM1AndTIM4PWMAMSMotorInit` |
| TIM5 | Heater PWM | `HwIRQ_TIM5PWMHeaterInit` |
| TIM8 | Fan PWM (3 fans) | `HwIRQ_TIM8PWMFanInit` |

### Communication

| Interface | Function | Details |
|-----------|----------|---------|
| USB CDC VCP | Communication with Klipper host | AT command protocol, receives commands from `phrozen_dev` module |
| UART2 (PA2/PA3) | Secondary communication / key input | `PA2` = TX output, `PA3` = key input (entry detect?) |
| I2C1 | AHT20 temperature/humidity sensor #1 | `App_AHT20Reset` with i2cx parameter |
| I2C2 | AHT20 temperature/humidity sensor #2 | Second intracavity sensor |
| SPI | FM175XX NFC reader | `HwIRQ_SPIInit`, `FM175XX_IO_Init` |
| ADC1 | NTC temperature sensors, filament sensors | `HwIRQ_ADC1SingleConvInit` |

### GPIO Functions (from init strings)

| Pin | Function |
|-----|----------|
| PA2 | UART2 TX (reconfigurable as GPIO output) |
| PA3 | UART2 RX / Key input (`AMS_ARCO_UART2_PA3_KEY_IN`) |
| PB1 | Motor related (referenced near motor direction code) |
| Various | `USBHUBRST` — USB hub reset control (ON/OFF) |
| Various | Segment LCD pins |
| Various | System LED |
| Various | Conveyor control |
| Various | Entry sensors (4 channels) — `AMS_ARCO_ENTRY[1-4]_GREEN_H/L` |

### Actuator Control Functions

| Macro/Function | Parameters | Purpose |
|----------------|------------|---------|
| `HEATER_DUTY_CTRL(duty, max)` | duty 0-100, max 100 | Heater element PWM via TIM5 |
| `FAN0_DUTY_CTRL(duty, max)` | duty 0-100, max 100 | Fan 0 PWM via TIM8 |
| `FAN1_DUTY_CTRL(duty, max)` | duty 0-100, max 100 | Fan 1 PWM via TIM8 |
| `FAN2_DUTY_CTRL(duty, max)` | duty 0-100, max 100 | Fan 2 PWM via TIM8 |

## AT Command Protocol (USB VCP)

Commands received from Klipper host via USB CDC:

| Command | Handler | Description |
|---------|---------|-------------|
| `AT+IDLE` | `App_IdleCmdHandle` | Set device to idle mode |
| `AT+PAUSE` | `App_PauseCmdHandle` | Pause current operation |
| `AT+RESTORE` | `App_RestoreCmdHandle` | Restore/resume from pause |
| `AT+RSTUSBHUB` | `App_RstUSBHubCmdHandle` | Reset USB hub (toggle USBHUBRST pin) |
| `AT+EBLOCKCHECK` | `App_EBLOCKCHECKTimingCmdHandle` | Start extruder block check timing |
| `AT+EBLOCKEND` | `App_EBLOCKEndTimingCmdHandle` | End extruder block check |
| `AT+CH` | (channel handler) | Channel/filament selection |
| `AT+SB=0..3` | `App_P114SBGetSystemSimpleStatusHandle` | Query simple status per slot (returns binary) |

The USB VCP receive handler is `HwIRQ_UsbCDCVCPRecvHandler`, which buffers into `G_SystemInfoSt.Uart1RecvStArray[]`. The main loop processes these in `App_While1TaskTUart1RXProcess`.

## Global State Structure: `G_SystemInfoSt`

This is the central state object. Reconstructed layout from debug strings:

```c
typedef enum {
    MOTOR_STOP = 0,
    MOTOR_FORWARD,
    MOTOR_BACK,
    MOTOR_FULL_WAIT,
} MotorDirEnum_t;

typedef struct {
    MotorDirEnum_t MotorDirEnum;
    uint32_t Runtime;
} MotorState_t;

typedef struct {
    float NTC1Temp;              // NTC thermistor 1 (tuyere/nozzle area)
    float NTC2Temp;              // NTC thermistor 2
    float IntracavityTempAverage;     // Averaged chamber temperature
    float IntracavityVirtualTempAverage; // Virtual/calculated temp
    float IntracavityHumiAverage;     // Averaged chamber humidity
    float TuyereTempAverage;          // Tuyere (duct) temperature
    uint8_t Entry1IfTrigger;     // Entry sensor 1 triggered
    uint8_t Entry2IfTrigger;     // Entry sensor 2 triggered
    uint8_t Entry3IfTrigger;     // Entry sensor 3 triggered
    uint8_t Entry4IfTrigger;     // Entry sensor 4 triggered
    uint8_t CacheFullIfTrigger;  // Buffer cache full
    uint8_t AMSSpittingFilaCheckEnable;
    uint32_t AMSSpittingFilaCheckCount;
    uint8_t ExtruderBlockCheckEnable;
    uint32_t ExtruderBlockCheckCount;
} EssentialSensorStatus_t;

typedef struct {
    uint8_t FilaType;       // Filament type (PLA, ABS, etc.)
    uint8_t FilaMode;       // Filament mode
    uint8_t Mode;           // Operating mode (temperature/humidity/timer)
    uint16_t Temperature;   // Target temperature
    uint16_t Timer;         // Drying timer value
    uint16_t Humidity;      // Target humidity
    uint32_t FlashRead;     // Flash read value
    uint32_t FlashWrite;    // Flash write value
} SetModeValueSt_t;

typedef struct {
    uint32_t BeepCnt;
    uint8_t HeaterSlowFlag;       // 0=normal, 1=slow, 2=special
    uint32_t HeaterSlowCount;
    uint8_t HeaterSpecialSlowFlag;
    uint32_t HeaterSpecialSlowCount;
    uint8_t HeaterSpecialSlowCountFlag;
} TimerCountSt_t;

typedef struct {
    uint16_t Count;
    // ... receive buffer data
} Uart1RecvSt_t;

typedef struct {
    // Motor states (4 filament channels)
    MotorState_t Motor1;
    MotorState_t Motor2;
    MotorState_t Motor3;
    MotorState_t Motor4;

    // Sensor status
    EssentialSensorStatus_t EssentialSensorStatus;

    // Drying/thermostat settings
    SetModeValueSt_t SetModeValueSt;

    // Timer/counter state
    TimerCountSt_t TimerCountSt;

    // Operating mode
    uint8_t Mode;  // IDLE_MODE, MCTR_MODE, MCTS_MODE, MATR_MODE, MATS_MODE, TIR_MODE, TIS_MODE

    // State machines (current + last for each mode)
    uint8_t IDLEModeStateMachine;
    uint8_t LastIDLEModeStateMachine;
    uint8_t MCTRModeStateMachine;
    uint8_t LastMCTRModeStateMachine;
    uint8_t MCTSModeStateMachine;
    uint8_t LastMCTSModeStateMachine;
    uint8_t MATRModeStateMachine;
    uint8_t LastMATRModeStateMachine;
    uint8_t MATSModeStateMachine;
    uint8_t LastMATSModeStateMachine;
    uint8_t TIRModeStateMachine;
    uint8_t LastTIRModeStateMachine;
    uint8_t TISModeStateMachine;
    uint8_t LastTISModeStateMachine;

    // Print status
    uint8_t PrintStatus;

    // Klipper command state
    uint8_t KlipperCmdMotorNum;

    // Connection management
    uint8_t AMSConnectFlag;
    uint8_t AMSRstUSBHubCount;

    // UART receive buffers
    Uart1RecvSt_t Uart1RecvStArray[/* N */];
    Uart1RecvSt_t Uart1RecvStTmp;

    // UI state
    uint8_t BeepVolume;
    uint8_t UpPressLongFlag;
    uint8_t DownPressLongFlag;
    uint8_t SetIndex;
    uint8_t ThermostatStatuseEnum;
} G_SystemInfoSt_t;
```

## Operating Modes

The ChromaKit has a dual-purpose design — it's both an MMU (multi-material unit) and a filament dryer.

| Mode Enum | Name | Description |
|-----------|------|-------------|
| `IDLE_MODE` | Idle | No active operation |
| `MCTR_MODE` | Multi-Color Tool Receive | Receiving filament for multi-color print |
| `MCTS_MODE` | Multi-Color Tool Send | Sending filament for multi-color print |
| `MATR_MODE` | Multi-Material Tool Receive | Receiving filament for multi-material print |
| `MATS_MODE` | Multi-Material Tool Send | Sending filament for multi-material print |
| `TIR_MODE` | Thermostat/IR mode | Temperature drying mode |
| `TIS_MODE` | Thermostat/IS mode | Humidity drying mode |

## State Machine States

Each mode has its own state machine. Common states across MC/MA modes:

| State | Meaning |
|-------|---------|
| `IDLE` | Waiting for command |
| `SLEEP` | Low-power standby |
| `START` | Operation beginning |
| `STOP` | Operation ending |
| `PAUSE` | Paused mid-operation |
| `BACK` | Retracting filament |
| `SET` | Configuration/setup |
| `P1S0RD` | Park position ready |
| `P1TN` | Tool N filament transfer (main filament change sequence) |
| `P1BN` | Tool N filament back/retract |
| `P1GN` | Tool N filament park to standby |
| `P1HN` | Tool N special refill |
| `P1IN` | Tool N manual insert |
| `P1DNPN` | Tool N direction/park |
| `P2A1AP` | All park to position |
| `P2A2CL` | All clean/clear |
| `P8FA` | Fast auto-change |

## Motor Control

4 independent filament drive motors, each with:
- **Direction control**: Forward / Back / Stop / FullWait
- **Runtime tracking**: Encoder or timer-based position
- **PWM speed control**: Via TIM1/TIM4

### Motor Operations

| Function | Description |
|----------|-------------|
| `App_AMSMotor[1-4]FullWait` | Drive motor until filament reaches entry sensor (GREEN_H) |
| `App_AMSMotor[1-4]Stop` | Stop individual motor |
| `App_AMSMotorAllBack` | Retract all 4 filaments simultaneously |
| `App_AMSMotorBackById` | Retract specific motor by ID |
| `App_AMSMotorForwardById` | Feed specific motor by ID |
| `App_AMSMotorDirInit` | Initialize motor direction pins |
| `App_AMSMotorStopAll` | Emergency stop all motors |
| `App_AMSMotorInit` | Full motor subsystem initialization |

### Entry Sensors

Each filament channel has an optical sensor at the entry point:
- `AMS_ARCO_ENTRY[1-4]_GREEN_H` — Filament present (sensor triggered high)
- `AMS_ARCO_ENTRY[1-4]_GREEN_L` — Filament absent (sensor triggered low)

These are used for filament detection, load confirmation, and runout detection.

## Filament Drying (Thermostat) System

The ChromaKit doubles as a filament dryer with a heated chamber.

### Supported Filament Types (with flash-stored presets)

PLA, ABS, PETG, PC, TPU, PA, PP, ASA, PET — each with stored Mode, Temperature, and Timer settings.

### Drying Modes

1. **Temperature Mode** (`Mode==1`): Maintains target temperature
   - If target ≤ 35°C: All fans + heater off (ambient drying)
   - If target > 35°C and ≤ 40°C: Gradual heating with slow ramp
   - If target > 40°C: Full heating with PID-like slow control
   - Safety cutoff: NTC1/NTC2 ≥ 80°C triggers immediate heater shutdown
   - Tuyere temp ≥ 52°C triggers protective mode

2. **Humidity Mode** (`Mode==2`): Maintains target humidity
   - Uses AHT20 I2C sensors for humidity feedback
   - Heater + fan control based on humidity differential

### Temperature Control Algorithm

The heater uses a multi-stage approach:
- `HeaterSlowFlag`: 0 = normal heating, 1 = slow approach, 2 = special slow
- `HeaterSpecialSlowFlag`: Additional derating for fine temperature control
- Virtual temperature calculation: `IntracavityTemp + (TargetTemp - 36) / 2`
- Hysteresis and slow-down prevent overshoot

## NFC Filament Tags (FM175XX)

The board includes an **FM175XX** NFC reader (likely FM17520 or FM17550), which is a Chinese clone/compatible of the NXP RC522 (MFRC522). This reads ISO 14443A Type-A NFC tags embedded in filament spools.

Source files: `FM175XX.c`, `type_a.c`

Functions found: `FM175XX_IO_Init`, `FM175XX_0HardReset`, `FM175XX_1HardReset` (suggesting two NFC readers or antenna positions).

## USB Hub Management

The ChromaKit manages a USB hub (`USBHUBRST` pin):
- `USBHUBRST_ON` / `USBHUBRST_OFF` — Hardware reset of USB hub
- Auto-reset logic: If `AMSConnectFlag == 0` for extended period, increments `AMSRstUSBHubCount`; at count ≥ 50, triggers USB hub reset
- Provides reconnection resilience for the USB VCP link to Klipper

## Flash Storage

User settings are persisted to internal flash (STM32 flash write):
- `STM32FlashWrite` function handles flash programming
- Per-filament-type storage at dedicated addresses (`FLASH_SAVE_ADDR_[TYPE]_[PARAM]`)
- Default/erased value: `0xFFFFFFFF`
- Stores: Mode, Temperature, Timer for each of the 10 filament types
- Also stores: Beep volume, last mode, image version

## Version / OTA

- `FW_VERSION` and `IMAGE_VERSION` are tracked separately
- Image version mismatch triggers reboot (`error ImageVersion; reboot`)
- Version string format: `V-H%d-I%d-F%d` (Hardware, Image, Firmware versions)
- OTA tool: `phrozen_slave_ota` (in `firmware/tools/`)

## Key Application Functions

| Function | Description |
|----------|-------------|
| `App_While1TaskTUart1RXProcess` | Main loop UART receive processing |
| `App_While1TaskTimeFlagSegmentLCDProcess` | LCD display update task |
| `App_While1TaskTimeFlagUart1RXProcess` | Timed UART processing |
| `App_Uart1ATCmdToKlipper` | Forward AT command responses to Klipper |
| `App_P1TnChangingFilaStageHandle` | Main filament change state machine |
| `App_P1TNStateHandle` | Per-channel filament transfer handler |
| `App_P1GnExtruderForceBackCmdHandle` | Force retract from extruder |
| `App_P1HnCutBackCmdHandle` | Cut and retract handler |
| `App_P1InManualExtrudedFilaCmdHandle` | Manual extrude handler |
| `App_P1JnManualSpitFilaCmdHandle` | Manual spit/purge handler |
| `App_P2A1RollbackAllToParkPositionCmdHandle` | Park all filaments |
| `App_GetKlipperCmdMotorNum` | Parse motor number from Klipper command |
| `App_M0ModeCmdHandle` | M0 (idle reset) mode handler |
| `App_MAModeCmdHandle` | MA (multi-material) mode handler |
| `App_MCModeCmdHandle` | MC (multi-color) mode handler |
| `App_ConnectAMSHeartbeat` | Heartbeat/keepalive handler |
| `App_RecordLastCmd` | Records last AT command for debug |
| `App_RebootChckEntryIfTrigger` | Check entry sensors after reboot |
| `App_CleanAllChannelCmdHandle` | Clear all channel states |
| `App_HeaterStop` | Emergency heater shutdown |
| `App_DigitNixieTubeShowThermostatStartMenu` | LCD menu display |
| `App_SegmentLCDShowDryingHumidityModeTimer` | LCD drying status |
| `App_SegmentLCDShowNormalTimer` | LCD normal timer display |
| `App_SystimInit` | System timer initialization |
| `App_SegmentLCDInit` | Segment LCD initialization |
| `Global_PrintSystemInfoModeStateMachine` | Debug: print all state machines |
| `Global_SensorStatusReport` | Debug: print all sensor values |
| `App_EBLOCKCHECKTimingCmdHandle` | Extruder block detection start |
| `App_EBLOCKEndTimingCmdHandle` | Extruder block detection end |

## Ghidra Tips for This Binary

### Memory Map Setup

```
Region      Start        End          Type
Flash       0x08000000   0x08024000   Code (r-x)
RAM         0x20000000   0x20005000   Data (rwx)
Peripherals 0x40000000   0x40030000   Volatile (rw-)
SCS/NVIC    0xE0000000   0xE0100000   Volatile (rw-)
```

### Recommended Ghidra Actions

1. **Apply SVD file**: Use `STM32F103xx.svd` from the CMSIS SVD repository to auto-label all peripheral registers. In Ghidra: `File → Load SVD` (requires SVD-Loader extension)

2. **Define `G_SystemInfoSt`**: Create the struct in Ghidra's Data Type Manager using the layout above. Find the global instance (likely in RAM around `0x20003xxx`) and apply the type.

3. **Rename functions**: Use the debug strings to rename all `FUN_*` functions. The strings contain explicit function names like `[(App.c)App_AMSMotor1FullWait]`.

4. **Label GPIO macros**: The `AMS_ARCO_ENTRY[1-4]_GREEN_H/L` are GPIO read/write macros — trace them to identify exact pin assignments.

5. **Trace the main loop**: Starting from `Reset_Handler` → `main` → look for the `while(1)` loop that calls the `App_While1Task*` functions.

6. **Label flash storage addresses**: Search for `0xFFFFFFFF` comparisons near flash read/write code to find the settings storage region (likely at the end of flash).

### Key Data Addresses to Find

- `G_SystemInfoSt` global instance (RAM)
- Flash settings base address
- USB VCP receive buffer
- AT command dispatch table (likely a string→function-pointer lookup)

## Recommendations for Open-Source Replacement

### Architecture

The replacement firmware should maintain the same USB VCP AT command interface so the existing `phrozen_dev` Klipper module works without modification.

### Minimum Viable Implementation

1. **USB CDC VCP**: AT command parser compatible with existing protocol
2. **Motor control**: 4-channel PWM motor drive with direction control
3. **Entry sensors**: 4x GPIO input for filament detection
4. **State machine**: Simplified IDLE/FORWARD/BACK/STOP per motor
5. **Status reporting**: Binary status response (16-byte format matching existing parser)

### Nice-to-Have Features

- NFC filament tag reading
- Filament drying/thermostat control
- Segment LCD display
- Flash settings persistence
- USB hub reset management

### Recommended Toolchain

- **Framework**: STM32 HAL or libopencm3
- **Build**: CMake + arm-none-eabi-gcc
- **Flash**: ST-Link or DFU via USB (if bootloader present)
- **Debug**: OpenOCD + GDB, or SWD via ST-Link
