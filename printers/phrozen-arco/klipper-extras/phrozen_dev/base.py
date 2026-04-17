####################################
#Project:
#Chip Type:
#Function:
#Developer: Lan Caigang
#Created: 20230830
####################################

import logging
import time

# prz version
#lancaigang240416:
#lancaigang240417:
#lancaigang240423:
#lancaigang240427: 24040
#lancaigang240428: 24040
#lancaigang240506: 24050
FW_VERSION = "25384"# e.g. 5x30+10=160 means 2025-May-10; if multiple versions released in one day, increment; normally no daily releases, roughly traceable to date
HW_VERSION = "16"
IMAGE_VERSION = "16"
# DRIVER_CODE // For Linux mainboard + multiple identical-firmware MCUs, protocol distinguishes by SN
#Format: V-H1-I1-F24045-SN1
#Format: V-H1-I1-F24045-SN2
#Format: V-H1-I1-F24045-SN3
#Format: V-H1-I1-F24045-SN4
#Format: V-H16-I16-F24045
#IMAGEID HWID FW version
# // ChromaKit mainboard 1 firmware-1 1 25164
# // ChromaKit mainboard 2 firmware-1 1 25164
# // ChromaKit mainboard 3 firmware-1 1 25164
# // ChromaKit mainboard 4 firmware-1 1 25164
# // Buffer board firmware-6 6 25164 reserved
# // 16-color HUB board firmware-7 7 25164
#  // Leveling board firmware-8 8 25164 reserved
# // DWIN serial screen foreground HMI firmware-11 11 25164
# // ARCO300-MKS-RK3328-DWIN serial screen virtual App-12 12  25164 reserved
# // ARCO300-MKS-RK3328-klipper-phrozen plugin-16 16 25164
# // ARCO300-MKS-RK3328-OTA sub-program-ChromaKit serial port OTA program-5 5 25164
# // ARCO300-MKS-RK3328-DWIN serial screen background program-10 10 25164 used as the image version of the entire phrozen_dev.zip for comparison with cloud version
# // ARCO300-MKS-RK3328-OTA main program-15 15 25164
# // DLP2K-YO2 submerged printer-STM32F401-Marlin-17 17 25164
# // ChromaKit segment-display new mainboard-STM32F103VET6-18 18 25164
# // 14K-13.5inch-SSD202-UI-LVGL-21 21 25164 #21 is the LVGL firmware on SSD202 of the 14K-13.5inch resin self-developed mainboard-SSD202-FPGA Gowin-STM32F407
# // 14K-13.5inch-Gowin FPGA-22 22 25164 #22 is the Gowin FPGA firmware on the 14K-13.5inch resin self-developed mainboard-SSD202-FPGA Gowin-STM32F407
# // 14K-13.5inch-STM32F4-MCU-23 23 25164#23 is the STM32F407 firmware on the 14K-13.5inch resin self-developed mainboard-SSD202-FPGA Gowin-STM32F407
# // 14K-17inch-SSD202-UI-LVGL-24 24 25164
# // 14K-17inch-Gowin FPGA-25 25 25164
# // 14K-17inch-STM32F4-MCU-26 26 25164
# // 16KMax-13.5inch-SSD202-UI-LVGL-27 27 25164   #27 is the LVGL firmware on SSD202 of the 16KMAX-13.5inch resin self-developed mainboard-SSD202-FPGA Gowin-STM32F407
# // 16KMax-13.5inch-Gowin FPGA-28 28 25164
# // 16KMax-13.5inch-STM32F4-MCU-28 29 25164
# // Fume purifier-30 30 25164
# // ARCO300-phrozen-RK3308-klipper-phrozen plugin-31 31 25164
# // ARCO300-phrozen-RK3308-OTA sub-program-ChromaKit serial port OTA program-32 32 25164
# // ARCO300-phrozen-RK3308-DWIN serial screen background program-33 33 25164 used as the image version of the entire phrozen_dev.zip for comparison with cloud version
# // ARCO300-phrozen-RK3308-OTA main program-34 34 25164
# // ARCO300-phrozen-RK3308-MCU STM32F407VET6-35 35 25164
# // ARCO300-phrozen-RK3308-toolhead board STM32F103CBT6-36 36 25164
# // ARCO300-MKS-RK3328-MCU STM32F407VET6-37 37 25164
# // ARCO300-MKS-RK3328-toolhead board STM32F103CBT6-38 38 25164
# // ARCO300-phrozen-RK3308-LVGL program-KLIPPER-39 39 25164 phrozen self-developed LVGL-UI controlling klipper


#=====DriveCodeFile.dat
#0, 95, version return info;
# 1 , 18 , 24053 , 18 , 0# // ChromaKit mainboard 1 firmware-18
# 2 , 18 , 24053 , 18 , 0# // ChromaKit mainboard 2 firmware-18
# 3 , 18 , 24053 , 18 , 0# // ChromaKit mainboard 3 firmware-18
# 4 , 18 , 24053 , 18 , 0# // ChromaKit mainboard 4 firmware-18
# 5 , 5 , 24046 , 5 , 0# // ARCO300-MKS-RK3328-STM32F407VET6-OTA sub-program-ChromaKit serial port OTA program-5 5
# 6 , 0 , 0 , 0 , 0# // Buffer board firmware-6 6 reserved
# 7 , 7 , 24051 , 7 , 0# // 16-color HUB board firmware-7 7 reserved
# 8 , 0 , 0 , 0 , 0 reserved
# 9 , 0 , 0 , 0 , 0 reserved
# 10 , 10 , 24054 , 10 , 0# // ARCO300-MKS-RK3328-STM32F407VET6-OTA sub-program-DWIN serial screen background program-10
# 11 , 11 , 24047 , 11 , 0# // DWIN serial screen foreground HMI firmware-11
# 12 , 0 , 0 , 0 , 0 reserved
# 13 , 0 , 0 , 0 , 0 reserved
# 14 , 0 , 0 , 0 , 0 reserved
# 15 , 15 , 25042 , 15 , 0 # // ARCO300-MKS-RK3328-STM32F407VET6-OTA main program-15 15 25164
# 16 , 16 , 25042 , 16 , 0 # // ARCO300-MKS-RK3328-STM32F407VET6-klipper-phrozen plugin-16 16 25164
# 17 , ? , 25042 , ? , 0 reserved
# 18 , ? , 25042 , ? , 0 reserved
# 19 , ? , 25042 , ? , 0 reserved
# 20 , ? , 25042 , ? , 0 reserved


#Downlink
# {"Cluster_ID":0,"Command":95,"Data":{}}
#Uplink
# {
#     "Data_ID": 95,
#     "Data": {
#         "GwId": "000000000000",
#         "GwMac": "000000000000",
#         "GwIP": "169.254.17.112",
#         "Mask": 0,
#         "GwName": "Gateway-000000000000",
#         "StartTime": 1700683341,
#         "JoinMode": 1,
#         "RouteESSID": "",
#         "DNSServer": "",
#         "DriveCodeList": [
#             {
#                 "DriveCode": 16,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 15,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 14,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 13,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 12,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 11,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 10,
#                 "DriveImageType": 10,
#                 "DriveHwVersion": 10,
#                 "DriveFwVersion": 24045,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 9,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 8,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 7,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 6,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 5,
#                 "DriveImageType": 5,
#                 "DriveHwVersion": 5,
#                 "DriveFwVersion": 24046,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 4,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 3,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 2,
#                 "DriveImageType": 0,
#                 "DriveHwVersion": 0,
#                 "DriveFwVersion": 0,
#                 "DriveId": 0
#             },
#             {
#                 "DriveCode": 1,
#                 "DriveImageType": 1,
#                 "DriveHwVersion": 1,
#                 "DriveFwVersion": 24042,
#                 "DriveId": 0
#             }
#         ],
#         "ProductId": "ARCO",
#         "MainImage": 3,
#         "MainHWVersion": 3,
#         "MainFWVersion": 24041,
#         "Gw_Ram": 334560,
#         "Gw_Rom": 346508
#     }
# }
#Gateway passthrough serial port bytes to node, node forwards to another MCU for control or OTA
# {"DeviceAddr":"0000000000000000","Epoint":8,"Cluster_ID":64513,"Command":0,"SendMode":2,
#"Data":{"PassData":"B5C305D51669B239C6A52397937A40D3FE8319ABC503004B1200"}}

# /*
#       STM32<->LinuxSOC data packet protocol
#       Baud rate: 115200bps; Start bit: 1; Data bits: 8; Parity: None; Stop bit: 1, Total bits: 11
#       No.     Notes           Bytes   Value   Description
#       1       Header          2       0xaaaa  Header marks the start of a data packet
#       2       Packet length   2       Datalen Frame length refers to the length of data after itself (including CRC16)
#       3       Sequence ID     1               Serial communication sequence number, used to prevent replay attacks
#                   Sender increments this sequence number when actively sending messages, keeps it the same as received sequence number when replying. Receiver checks this Byte before parsing data,
#                   if the sequence number hasn't changed for more than 10 consecutive times, it's considered a replay attack, the message will be discarded without processing or sending acknowledgment
#       4       Data type ID
#                 Distinguishes specific applications by ID number, specific data content can be compatible with different serial protocols
#                 0x01: STM32 OTA packet; 0xFE+byte_count+command_code+payload
#                 0x02: Zigbee protocol; opcode+byte_count+zigbee coordinator serial protocol
#                 0x03: Virtual App data protocol; opcode+byte_count+JSON data
#                 0x04: Modbus-RTU; opcode+byte_count+modbus(start_bit device_addr function_code data CRC_check end_char)
#                 0x05: extensible
#                 0x06: extensible
#                 0x07: extensible
#                 ...
#       5       Specific data content    Determined by data type; e.g. opcode+additional_data
#       6       CRC-16          2
#     */
#     */
#     /*
#   // f8 01 0400 09000100
#   // f8 00 1200 fe0f000000000000020100fc000100b40000
#   //=====Data format sent from gateway program to external program
#   //  Data structure:
#   //  Head    1   0xF8    Protocol header
#   //  DataId  1           Data packet identifier
#             // 0x00: Zigbee coordinator serial protocol data
#             // 0x01: Send drive code
#             // 0x02: Error feedback
#             // 0x03: Send heartbeat packet
#             // 0x04: Virtual client online notification reply
#             // 0x05: Virtual App data in JSON format
#             // 0x06: OTA data
#             // 0x07: Receive virtual drive info report feedback
#   //  Data_len    2       Data length
#   //  Data        Data_len
#   //=====Data format sent from external program to gateway program
#   //  Data structure:
#   //  Head    1   0xF9    Protocol header
#   //  DataId  1           Data packet identifier
#             //  0x00: Zigbee coordinator serial protocol data
#             //  0x01: Virtual drive online notification (notify gateway that driver has started; if it's a virtual Zigbee 3.0 device, the first data sent to gateway should be this, declaring the driver as a virtual Zigbee 3.0 device driver)
#             //  0x03: Heartbeat response
#             //  0x04: Virtual App online notification (if virtual app controls gateway client program via JSON format (e.g. magic mirror), declaring the driver as a virtual app client, communicating in JSON format)
#             //  0x05: Virtual App data in JSON format
#             //  0x06: OTA data
#             //  0x07: Virtual drive info report. Virtual drive reports driver info including hardware version, software version, ImageType, and driver identifier.
#   //  Data_len    2       Data length
#   //  Data        Data_len
#  */




#lancaigang240509: if 16-color HUB hot-plugged or ChromaKit MMU hot-plugged, /tty/USB0 may change to /tty/USB1
# Default serial ports
SERIAL_PORT1 = "/dev/ttyACM1"
SERIAL_PORT2 = "/dev/ttyACM2"
# Maximum number of color-change channels
AMS_MAX_CHANNEL = 32
# Loop event interval, serial port poll interval (seconds)
SERIAL_PORT_POLL_INTERVAL = 5.0
# USB-to-TTL serial port baud rate
SERIAL_PORT_BAUD = 19200




# Work mode
AMS_WORK_MODE_UNKNOW = 0  # Unknown mode; filament runout detection disabled
AMS_WORK_MODE_MC = 1  # Multi-color print mode
AMS_WORK_MODE_MA = 2  # Multi-color single-color auto-refill mode
AMS_WORK_MODE_FILA_RUNOUT = 3  # Single-color filament runout mode



#lancaigang240115: default no auto-connect
# Default: device does not auto-connect
AMS_AUTO_CONNECT = False
# Default X position for filament cut
AMS_FILA_CUT_X_POSITION = 313
#lancaigang240325: cut Y position
AMS_FILA_CUT_Y_POSITION = 307
# Default Z lift value for filament cut: 1.2
#lancaigang240603: new heated bed does not raise
AMS_FILA_CUT_Z_POSITION_LIFTING = 0.2
AMS_FILA_CUT_Z_POSITION_UP = 0.2
# Default ADC value when filament is inserted in toolhead
AMS_TOOLHEAD_FILA_EXIST_ADC_VALUE = 0.3
# Default ADC value when filament is removed from toolhead
AMS_TOOLHEAD_FILA_EMPTY_ADC_VALUE = 0.5



# Maximum toolhead movement speed while waiting (mm/min)
CHANGE_CHANNEL_WAIT_MAX_MOVEMENT_SPEED = 180
# Line width while waiting (mm)
CHANGE_CHANNEL_WAIT_LINE_WIDTH = 0.5
#lancaigang20231016: 120 seconds
 # Default timeout for filament change wait (seconds)
 #lancaigang240912: new ChromaKit MMU, changed to 100 seconds
 #lancaigang250111: changed to 90 seconds
  #lancaigang250113: changed to 50 seconds
CHANGE_CHANNEL_WAIT_TIMEOUT = 80


# Z-axis lift during color change controlled by gcode height
# 0=before cut, default uses internal gcode execution
CHANGE_CHANNEL_IF_Z_LIFTING_UP_BY_GCODE = 0



# ADC detection config
#Toolhead ADC active report interval: 15ms
#TOOLHEAD_ADC_REPORT_TIME = 0.015
#TOOLHEAD_ADC_DEBOUNCE_TIME = 0.025
#lancaigang250409: changed ADC report interval
TOOLHEAD_ADC_REPORT_TIME = 0.50
TOOLHEAD_ADC_DEBOUNCE_TIME = 0.70
#Toolhead ADC sample time
TOOLHEAD_ADC_SAMPLE_TIME = 0.100
#Toolhead ADC sample count
TOOLHEAD_ADC_SAMPLE_COUNT = 4



AMS_MC_MODE = 0  # Multi-color run mode
AMS_MA_MODE = 1  # Auto-refill run mode



MC_STANDBY = 0  # Standby phase
MC_PREPARTION = 1  # Preparation phase
MC_CHANGING_P1 = 2  # Filament change phase 1
MC_CHANGING_P2 = 3  # Filament change phase 2
MC_FORCE_FEED = 4  # Filament change forced feed phase
MC_PRINTING = 5  # Printing phase feed
MC_ROLLBACK = 6  # Full retract/unload
MC_PARKBACK = 7  # Retract to park position
MC_PARKALL = 8  # Retract all to park position
MC_CLEANING = 9  # Clear all filament
MC_ERR_TIMEOUT = 10  # Timeout error state
MC_ERR_RUNOUT = 11  # Filament runout error state
MC_ERR_BLOCKUP = 12  # Filament jam error state



MA_STANDBY = 0  # Standby phase
MA_FIND_WORK_CHAN = 1  # Find main feed channel
MA_FAST_FEED = 2  # Fast feed
MA_FORCE_FEED = 3  # Forced feed
MA_PRINTING_FEED = 4  # Printing phase
MA_MANUAL_ADD_FILA = 5  # Manual add filament
MA_AUTO_CHANGE_FILA = 6  # Auto change filament on runout
MA_ROLLBACK = 7  # Full retract/unload
MA_CLEANING = 8  # Clear all filament
MA_ERR_TIMEOUT = 9  # Timeout error state




#lancaigang231104: changed 1 to 3
# Filament runout detection cycle time (seconds)
#lancaigang230104: changed 3 to 6
AMS_FILA_RUNOUT_TIMER = 2.0
# Serial port receive cycle time (seconds)
#lancaigang240104: changed 0.2 to
#lancaigang240104: changed 0.2 to 0.1
AMS_SERIALPORT_RECV_TIMER = 0.1 #100ms
#lancaigang231104: changed 8 to 15
# Pause time count upper limit (seconds)
RUNOUT_MAX_PAUSE_TIME_COUNT = 15

#CS 00 N0 M03 T04 C0
# // Serial report to buffer board and printer
# // CS device_id   run_mode   prev_mc_state   current_mc_state   channel
# // CS00       N0      M09         T09         C5
# // CS00       N0      M02         T03         C0
# // CS00       N0      M08         T10         C1
#    deviceid   mode    pre_state   state       chan
# Serial receive string regex match pattern
AMS_SERIALPORT_RECEIV_PARSE_PATTERN = r"CS(?P<id>\d{2})N(?P<mode>\d{1})M(?P<pre_state>\d{2})T(?P<state>\d{2})C(?P<chan>\d{1})"




G_EmptyString = ""  # Empty string



# Query device standard status
G_DictPhrozenCmdP114 = {#python dict key-value
    "cmd": "P114",#websocket command
    "params": [G_EmptyString],#parameters
    "mcu_cmd": ["SD"],#ChromaKit MMU mainboard command SD
    "desc": "Query ChromaKit MMU mainboard sensor status",
}



# Query device basic status
G_DictPhrozenCmdP104 = {#python dict key-value
    "cmd": "P104",
    "params": [G_EmptyString],#python list
    "mcu_cmd": ["SB"],#python list
    "desc": "Query ChromaKit MMU mainboard basic status",
}



# Connect device
G_DictPhrozenCmdP28 = {#python dict key-value
    "cmd": "P28",
    "params": [G_EmptyString],#python list
    "mcu_cmd": [G_EmptyString],#python list
    "desc": "Connect ChromaKit MMU mainboard",
}



# Disconnect
G_DictPhrozenCmdP29 = {#python dict key-value
    "cmd": "P29",
    "params": [G_EmptyString],#python list
    "mcu_cmd": [G_EmptyString],#python list
    "desc": "Disconnect ChromaKit MMU mainboard",
}



# Auto-assign device IDs (for multi-device auto networking)
G_DictPhrozenCmdP30 = {#python dict key-value
    "cmd": "P30",
    "params": [G_EmptyString],#python list
    "mcu_cmd": ["I"],#list
    "desc": "Auto-assign device IDs for multiple ChromaKit MMU mainboards",
}



# Device work mode
G_DictPhrozenP0 = {#python dict key-value
    "cmd": "P0",
    "params": ["M","B"],#list
    "mcu_cmd": ["MC", "MA"],#python list
    "desc": "Set ChromaKit MMU mainboard work mode",
}



# Filament retract/unload handling
G_DictPhrozenCmdP2 = {#python dict key-value
    "cmd": "P2",
    "params": ["A","B"],#list
    "mcu_cmd": ["AP", "CL"],#python list
    "desc": "ChromaKit MMU mainboard retract commands",
}



# Emergency stop device
G_DictPhrozenCmdP4 = {#python dict key-value
    "cmd": "P4",
    "params": [G_EmptyString],#python list
    "mcu_cmd": ["SP"],#list
    "desc": "ChromaKit MMU mainboard emergency stop",
}


# P1 T[n]n:1~32(no networking, use 1~4) manually switch to specified channel, filament change only (for testing);====="T";
# P1 B[n]n:1~32(no networking, use 1~4) specified channel filament full retract Yes;====="B";
# P1 D[n];n:1~32(no networking, use 1~4); specified channel filament retract to park position standby Yes;====="P";
# P1 C[n] n:1~32(no networking, use 1~4) auto switch to specified channel (multi-action command, includes cut, change, wait);====="T";
#lancaigang231202:
# P1 E[n];n:1~32(no networking, use 1~4); specified channel filament force forward, note: remove the PTFE tube from toolhead Yes;====="E?";
# lancaigang240228: toolhead retract a distance, STM32 needs to retract a distance first
# P1 G[n];n:1~32(no networking, use 1~4); specified channel filament retract a distance Yes;====="G?";
# lancaigang240319: enter special feed phase, feed when buffer is not full
# =====P1 H[n];n:1~32(no networking, use 1~4); enter special feed phase, feed when buffer is not full Yes;====="H?";
#lancaigang240329: reserved
# =====P1 I[n]; STM32 needs to feed during manual extrusion;====="I?";
# =====P1 J[n]; multi-color manual purge; feed when buffer is not full;
# =====P1 K[n];
# =====P1 L[n];
# =====P1 M[n];
# =====P1 N[n];
# =====P1 O[n];
# =====P1 Q[n];
# =====P1 U[n];
# =====P1 V[n];
# =====P1 W[n];
# =====P1 X[n];
# =====P1 Y[n];
# =====P1 Z[n];
# Device multi-color mode filament change handling
G_DictPhrozenCmdP1 = {#python dict key-value
    "cmd": "P1",
    "params": ["S","C","T","B","D","E","G","I","J","K","L","M","N","O","Q","U","V","W","X","Y","Z"],#python list
    "mcu_cmd": ["RD","Tn","Bn","Pn","En","Gn","In","Jn","Kn","Ln","Mn","Nn","On","Qn","Un","Vn","Wn","Xn","Yn","Zn"],#python list
    "desc": "ChromaKit MMU mainboard channel commands",
}



# Filament change wait area handling
G_DictPhrozenCmdP9 = {#python dict key-value
    "cmd": "P9",
    "params": ["X", "Y", "W", "H", "D", "T", "A"],#python list
    "mcu_cmd": [G_EmptyString],#python list
    "desc": "Filament change toolhead wait area command",
}


# Purge count control
G_DictPhrozenCmdP10 = {#python dict key-value
    "cmd": "P10",
    "params": ["S"],#python list
    "mcu_cmd": [G_EmptyString],#python list
    "desc": "Purge count control",
}


# Execute auto-refill
G_DictPhrozenCmdP8 = {#python dict key-value
    "cmd": "P8",
    "params": [G_EmptyString],#python list
    "mcu_cmd": ["FA"],#python list
    "desc": "Auto-refill command",
}

G_DictPhrozenCmdTn = {#python dict key-value
    "cmd": "T",
    "params": [G_EmptyString],#python list
    "mcu_cmd": [G_EmptyString],#python list
    "desc": "Orca slicer color change",
}



# Query toolhead filament sensor ADC value
G_DictPhrozenCmdToolheadAdc = {#python dict key-value
    "cmd": "PRZ_ADC",
    "params": [G_EmptyString],#python list
    "mcu_cmd": [G_EmptyString],#python list
    "desc": "Get toolhead filament presence ADC value",
}

# 1. Python () represents a tuple, a tuple is an immutable sequence
#  1) Creation e.g.: tuple = (1,2,3) access: tuple[0]......  tuple[0,2].....tuple[1,2]......
# 2) Modify tuple: tuples are immutable
# 3) Delete tuple: del tuple
# 4) Built-in functions:
# cmp(tuple1, tuple2): compare two tuples
# len(tuple): calculate tuple length
# max(tuple): maximum value
# min(tuple): minimum value
# tuple(seq): convert list to tuple
# 2. Python [] represents a list, a list is a mutable sequence
# 1) Create list: l = [1,2,3,4] access: l[0]........
# 2) Lists are mutable
# 3) Built-in functions:
# cmp(list1, list2): compare two lists
# len(list): calculate list length
# max(list): maximum value
# min(list): minimum value
# list(seq): convert tuple to list
# list.append(obj): append object to end of list
# list.pop(): remove an element
# list.remove: remove first matching value in list
# list.sort(): sort
# list.reverse(): reverse list
# list.count(obj): count occurrences of object in list
# list.insert(index, obj): insert object at position
# 3. Python {} dict; dict is a mutable container, very flexible to use
# 1) Create dict: dict = {"a":1,"b":2}. Dict is key-value pairs. Access: dict['a']
# 2) Mutable
# 3) Delete: del dict["a"] delete a pair  del dict delete dict  dict.clear() clear all entries
# 4) Built-in functions:
# cmp(dict1, dict2): compare two dicts
# len(dict): calculate dict length
# dict.clear(): delete dict data
# dict.get(key, default=None): return specified value, or default if not found
# dict.has_key(key): check if value exists, returns true/false
# dict.item() returns traversable (key, value) tuples as a list
# dict.key() returns all keys of dict

# 1. Array definition and assignment
# Defining an array in Python is simple, just arr = []; arr is now defined as an empty array, but it has no values. Let's assign values to arr,
# arr = ['today', 'Singles Day', 'did you shop?']; now arr has three elements assigned. This step completes both definition and assignment. In development, definition and assignment are typically done in one step.
# 2. Get array elements
# After assigning values to an array, we usually need to get a specific element, e.g. get the first element of arr: arr[0]. Access elements by index,
# note index starts from 0, arr[2] means the third element, arr[len(arr)-1] means the last element, len(arr) is the total length, i.e. how many elements.
# 3. Traverse array
# In practice, we typically use a for loop to traverse array elements. If you don't know what a for loop is yet, you can skip this part for now, later articles will explain for loops in detail.
# See the code below for array traversal.
# 4. Array element append and delete
# After defining an array, we can continue to append and delete elements. There are mainly two ways to append: append and insert. append adds to the end of the array,
# insert can insert at a specified position, e.g. arr.insert(2, 'I am the third element inserted here'), arr becomes ['yesterday', 'today', 'I am the third element inserted here', 'did you shop?'].
# There are also three ways to delete array elements, here we introduce only one to avoid confusion: arr.pop(2) deletes the third element. Note 2 is the index.
# See the code below for details.
# 5. Check if element is in array
# We repeat "yesterday" "today" "tomorrow" every day, so arr = ['yesterday', 'today', 'tomorrow']. Now use Python to check if I remember what I did "yesterday", a simple "in" can do it.
# See the code below for details.
# 6. Array sorting
# I'll evaluate the value of these three days, price = [207,1400,50]; now I want Python to sort these three values from low to high and high to low, and tell me which is highest and lowest.
# See the code below for details.

####################################
#Class:
#Description: Lan Caigang-20230830
####################################
class error(Exception):
    pass

####################################
#Class:
#Description: Lan Caigang-20230830
####################################
class Base(object):
    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #Constructor initialization
    def __init__(self, config):
        if type(self) is Base:
            raise error("Base class cannot be instantiated")
        #Command lock token
        self.G_AMSSerialCmdLock = False
        #Default: toolhead has no filament
        self.G_ToolheadIfHaveFilaFlag = False

        # Filament runout handling timer
        self.G_FilaRunoutTimmer = None

        # Serial port 1 receive timer
        self.G_SerialPort1RecvTimmer = None
        # Serial port 2 receive timer
        self.G_SerialPort2RecvTimmer = None

        #printer.cfg config file
        self.G_PhrozenConfig = config
        self.G_PhrozenPrinter = config.get_printer()
        self.G_PhrozenReactor = self.G_PhrozenPrinter.get_reactor()
        #Pause/resume commands
        self.G_PhrozenPrinterCancelPauseResume = self.G_PhrozenPrinter.load_object(config, "pause_resume")
        #gcode commands
        self.G_PhrozenGCode = self.G_PhrozenPrinter.lookup_object("gcode")
        #Respond info to Fluidd
        self.G_PhrozenFluiddRespondInfo = self.G_PhrozenGCode.respond_info

        #lancaigang241105:
        self.G_AMS1DeviceState = {}
        self.G_AMS2DeviceState = {}


        #USB-to-TTL serial port
        self.G_Serialport1Define = self.G_PhrozenConfig.get("dev_port", SERIAL_PORT1)
        self.G_Serialport2Define = self.G_PhrozenConfig.get("dev_port2",SERIAL_PORT2)

        #printer.cfg; whether to auto-connect
        self.G_AMSIfAutoConnectFlag = self.G_PhrozenConfig.getboolean("auto_connect", AMS_AUTO_CONNECT)
        #printer.cfg; default X position for filament cut
        self.G_AMSFilaCutXPosition = self.G_PhrozenConfig.getfloat("fila_cut_x_pos", AMS_FILA_CUT_X_POSITION)
        #lancaigang240409: Y position
        self.G_AMSFilaCutYPosition = self.G_PhrozenConfig.getfloat("fila_cut_y_pos", AMS_FILA_CUT_Y_POSITION)
        #printer.cfg; default Z lift position for filament cut
        self.G_AMSFilaCutZPositionLiftingUp = self.G_PhrozenConfig.getfloat("fila_cut_x_pos_up", AMS_FILA_CUT_Z_POSITION_UP)




        #printer.cfg; default toolhead filament inserted ADC value
        self.G_ToolheadFilaExistAdcValueDefault = self.G_PhrozenConfig.getfloat("fila_exist_value", AMS_TOOLHEAD_FILA_EXIST_ADC_VALUE)
        #printer.cfg; default toolhead filament empty ADC value
        self.G_ToolheadFilaEmptyAdcValueDefault = self.G_PhrozenConfig.getfloat("fila_empty_value", AMS_TOOLHEAD_FILA_EMPTY_ADC_VALUE)
        #printer.cfg; toolhead filament ADC threshold; (exist+empty)/2
        self.G_ToolheadFilaAdcThresholdValue = (self.G_ToolheadFilaExistAdcValueDefault + self.G_ToolheadFilaEmptyAdcValueDefault) / 2.  # ADC voltage reference

        #Toolhead: fila_sensor_pin: _THR:PA2
        #printer.cfg; toolhead ADC detection pin
        self.G_ToolheadFilaSensorPin = self.G_PhrozenConfig.get("fila_sensor_pin", None)
        #Toolhead ADC value
        Lo_ToolheadAdcPins = self.G_PhrozenPrinter.lookup_object("pins")
        #Toolhead: fila_sensor_pin: _THR:PA2
        self.G_ToolheadAdc = Lo_ToolheadAdcPins.setup_pin("adc", self.G_ToolheadFilaSensorPin)
        self.G_ToolheadAdc.setup_minmax(TOOLHEAD_ADC_SAMPLE_TIME, TOOLHEAD_ADC_SAMPLE_COUNT)
        #Register callback function
        self.G_ToolheadAdc.setup_adc_callback(TOOLHEAD_ADC_REPORT_TIME, self.Base_ToolheadAdcCallback)
        Lo_ToolheadQueryAdc = self.G_PhrozenPrinter.lookup_object("query_adc")
        Lo_ToolheadQueryAdc.register_adc("prz_adc", self.G_ToolheadAdc)





        # printer.cfg; max toolhead movement speed during filament change wait
        self.G_ChangeChannelWaitMaxMovementSpeed = self.G_PhrozenConfig.getint("wait_max_velocity", CHANGE_CHANNEL_WAIT_MAX_MOVEMENT_SPEED)
        #printer.cfg; line width during filament change wait
        self.G_ChangeChannelWaitLineWidth = self.G_PhrozenConfig.getfloat("wait_line_width", CHANGE_CHANNEL_WAIT_LINE_WIDTH)
        #printer.cfg; filament change timeout, configurable via printer.cfg or default
        self.G_ChangeChannelTimeout = self.G_PhrozenConfig.getint("wait_timeout", CHANGE_CHANNEL_WAIT_TIMEOUT)
        #printer.cfg; whether Z-axis lift during filament change is controlled by gcode
        self.G_ChangeChannelIfZLiftingUpByGcode = self.G_PhrozenConfig.getint("switch_fila_zup_by_gcode", CHANGE_CHANNEL_IF_Z_LIFTING_UP_BY_GCODE)




        #lancaigang231207: during filament change, if feed jams, need to remove from toolhead PTFE tube, cannot retract filament
        self.G_IfInFilaBlockFlag = False

        #lancaigang231207: STM32 pause data
        self.G_SerialRxASCIIStr = None

        #lancaigang231207: whether filament change is in progress
        self.G_IfChangeFilaOngoing= False

        #lancaigang231215: STM32 pause active report, whether to pause immediately or count retries before pausing
        self.G_STM32PauseCount= 0


        #lancaigang231212: active pause flag, if paused during printing (i.e. toolhead has filament detected), no need to retract then feed after resume
        self.G_IfToolheadHaveFilaInitiativePauseFlag = False

        #lancaigang240108: single-color auto-refill resume flag, for resuming print after runout refill extrusion is complete
        self.G_M2MAModeResumeFlag = False

        #lancaigang240108:
        self.P0M3FilaRunoutSpittingFinished = True  # Single-color mode filament runout handling complete flag

        #lancaigang240113: manual feed T? filters STM32 reported timeout
        self.ManualCmdFlag = False

        #lancaigang240123: MA auto-refill timeout handling
        self.AMSRunoutPauseTimeCount = 0
        self.AMSRunoutPauseTimeoutFlag = 0

        #lancaigang240124: STM32 active report pause, can only pause once
        self.STM32ReprotPauseFlag = 0

        #lancaigang240223: toolhead cut failure flag
        self.ToolheadCutFlag = False

        #lancaigang240229: PG101
        self.IfDoPG102Flag = False

        #lancaigang240320: PG102
        self.PG102Flag = False

        #lancaigang240320: PG102
        self.PG102DelayPauseFlag = False

        #lancaigang240325: MC mode can resume flag
        self.G_MCModeCanResumeFlag = False

        #lancaigang240325: channel number for filament runout feed pause
        self.G_Pause1Channel = -1
        #lancaigang240325:
        self.G_PauseTriggerWhileChangeChannelFlag = False

        #lancaigang240325:
        self.G_ResumeProcessCheckPauseStatus = False

        #lancaigang240325:
        self.G_PauseToLCDString = ""

        #lancaigang240410:
        self.G_CancelFlag = False

        #lancaigang240411: if P0 M3 command not received, do not use filament runout detection
        self.G_P0M3Flag = False

        #lancaigang240412: ChromaKit MMU device 1 normal flag
        self.G_AMSDevice1IfNormal=False

        #lancaigang241029: ChromaKit MMU device 2 normal flag
        self.G_AMSDevice2IfNormal=False

        #lancaigang240415: toolhead has filament, no purge needed on first run
        self.G_P0M3ToolheadHaveFilaNotSpittingFlag = False

        #lancaigang240427: ChromaKit MMU abnormal restart, needs logging
        self.G_AMS1ErrorRestartFlag = False
        self.G_AMS1ErrorRestartCount = 0
        #lancaigang240521: on resume, if ChromaKit MMU abnormal restart detected, treat as hot-plug, execute full retract and change process
        self.G_ResumeCheckAMS1ErrorRestartFlag = False

        #lancaigang241030:
        self.G_AMS2ErrorRestartFlag = False
        self.G_AMS2ErrorRestartCount = 0
        self.G_ResumeCheckAMS2ErrorRestartFlag = False


        #lancaigang240528: P114 running flag
        self.G_P114RunFlag = 0


        #lancaigang241101: purge count control
        self.G_P10SpitNum = 0

        #lancaigang241106: single-color auto-refill MA enter printing flag
        self.G_P0M2MAStartPrintFlag = 0

        #lancaigang250102: print filament change count
        self.G_PrintCountNum = 0

        #lancaigang250104: P2A3 flag
        self.G_P2A3Flag = 0

        #lancaigang250514: parse serial screen config data
        self.G_P0M1MCNoneAMS = -1

        self.G_AutoReplaceState = -1
        self.G_ChromaKitNum = -1
        self.G_ChromaKitAccessT0 = -1
        self.G_ChromaKitAccessT1 = -1
        self.G_ChromaKitAccessT2 = -1
        self.G_ChromaKitAccessT3 = -1
        self.G_ChromaKitAccessT4 = -1
        self.G_ChromaKitAccessT5 = -1
        self.G_ChromaKitAccessT6 = -1
        self.G_ChromaKitAccessT7 = -1
        self.G_ChromaKitAccessT8 = -1
        self.G_ChromaKitAccessT9 = -1
        self.G_ChromaKitAccessT10 = -1
        self.G_ChromaKitAccessT11 = -1
        self.G_ChromaKitAccessT12 = -1
        self.G_ChromaKitAccessT13 = -1
        self.G_ChromaKitAccessT14 = -1
        self.G_ChromaKitAccessT15 = -1

        #lancaigang250526: while pausing, do not allow new gcode commands, wait for pause to complete
        self.G_KlipperInPausing = False

        #lancaigang250527: quick pause execution
        self.G_KlipperQuickPause = False

        #lancaigang250607: print status; 1-unloading; 2-loading; 3-printing; 4-paused
        self.G_KlipperPrintStatus= -1

        #lancaigang250619:
        self.G_PauseToUSBConnectString = ""

        #lancaigang250724: image ID
        self.G_ImageId= -1
        self.G_HwId= -1

        #lancaigang250805: cutter test
        self.G_CutCheckTest = False

        #lancaigang250812: single-color filament runout detection, retry return to pause area
        self.G_RetryToPauseAreaFlag = False
        self.G_RetryToPauseAreaCount = 0


        #lancaigang251120: PG108 execution flag
        self.G_PG108Ingoing=0


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # Acquire command lock
    def Base_AMSSerialCmdLock(self):
        logging.debug("ChromaKit: serial cmd lock")
        for _ in range(8):
            if self.G_AMSSerialCmdLock==False:
                #Acquire command lock token
                #Lock
                self.G_AMSSerialCmdLock = True
                return True
            #Delay 0.2s loop
            time.sleep(0.2)
        return False
    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # Release command lock
    def Base_AMSSerialCmdUnlock(self):
        logging.debug("ChromaKit: serial cmd unlock")
        #Unlock
        self.G_AMSSerialCmdLock = False
    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # Serial port receive periodic task, meant to be overridden
    def Device_TimmerUart1Recv(self, eventtime):
        self.G_PhrozenFluiddRespondInfo("[(base.python)Device_TimmerUart1Recv] serial port 1 receive thread")
        pass

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Device_TimmerUart2Recv(self, eventtime):
        self.G_PhrozenFluiddRespondInfo("[(base.python)Device_TimmerUart2Recv] serial port 2 receive thread")
        pass


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #Toolhead filament detection ADC; ms callback
    #250ms
    def Base_ToolheadAdcCallback(self, read_time, read_value):
        #self.G_PhrozenFluiddRespondInfo("[(base.python)Base_ToolheadAdcCallback]")
        _ = read_time
        #Whether toolhead has filament; ADC value below threshold means filament is present
        #lancaigang231213: (empty+exist)/2
        self.G_ToolheadIfHaveFilaFlag = read_value < self.G_ToolheadFilaAdcThresholdValue
        #self.G_PhrozenFluiddRespondInfo("[(base.python)Base_ToolheadAdcCallback]self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))
        #print(read_value)
        #print(self.G_ToolheadFilaAdcThresholdValue)
