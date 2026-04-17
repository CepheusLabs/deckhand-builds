####################################
# AMS ctypes structure definitions
# Developer: Lan Caigang
# Created: 20230830
####################################

from ctypes import *


# Simple info structure
# typedef struct St_SystemSimpleStatus {
#     uint8_t InfoFlag;
#     int CurrentDeviceId;
#     int EndDeviceId;
#     uint8_t DeviceMode;
#     uint8_t MCStateMachine : 4;
#     uint8_t MAStateMachine : 4;
# } St_SystemSimpleStatus;
####################################
#Class:
#Description: Lan Caigang-20230830
####################################
class AMSSimpleInfoSt(LittleEndianStructure):#little-endian
    _pack_ = 1
    _fields_ = [
        ("info_flag", c_uint8),#8bit; flag tag
        ("dev_id", c_uint8),#8bit; multi-color device id
        ("end_dev_id", c_uint8),#8bit; last multi-color device id
        ("dev_mode", c_uint8),#8bit; multi-color device mode
        ("mc_state", c_uint8, 4),#4bit; mc state
        ("ma_state", c_uint8, 4),#4bit; ma state
    ]

####################################
#Class:
#Description: Lan Caigang-20230830
####################################
class AMSSimpleInfoBytes(Union):#ChromaKit MMU simple status
    _fields_ = [
        ("field", AMSSimpleInfoSt),
        ("whole", c_uint8 * sizeof(AMSSimpleInfoSt)),
    ]

# Detailed info structure
# typedef struct St_SystemDetailStatus {
#     uint8_t InfoFlag;
#     int8_t CurrentDeviceId;
#     int8_t EndDeviceId;
#     int8_t ActiveDeviceId;
#     int8_t TargetDeviceId;
#     uint8_t Others;
#     uint8_t DeviceMode : 2;
#     uint8_t IfAnyMotorRuning : 1;
#     uint8_t CacheEmptyIfTrigger : 1;
#     uint8_t CacheFullIfTrigger : 1;
#     uint8_t CacheExistIfTrigger : 1;
#     uint8_t Reserve : 2;
#     uint8_t MCStateMachine : 4;
#     uint8_t MAStateMachine : 4;
#     uint32_t EntryPositionIfTriggerBitMask;
#     uint32_t ParkPositionIfTriggerBitMask;
# } St_SystemDetailStatus;
####################################
#Class:
#Description: Lan Caigang-20230830
####################################
class AMSDetailInfoSt(LittleEndianStructure):#little-endian
    _pack_ = 1
    _fields_ = [
        ("info_flag", c_uint8),#8bit; flag tag
        ("dev_id", c_uint8),#8bit;
        ("end_dev_id", c_int8),#8bit;
        ("active_dev_id", c_int8),#8bit;
        ("target_dev_id", c_int8),#8bit;
        ("others", c_uint8),#8bit;

        ("dev_mode", c_uint8, 2),#2bit; multi-color device mode
        ("any_motor_runing", c_uint8, 1),#1bit; whether any motor is running
        ("cache_empty", c_uint8, 1),#1bit; buffer empty state
        ("cache_full", c_uint8, 1),#1bit; buffer full state
        ("cache_exist", c_uint8, 1),#1bit; buffer filament present state
        ("reserve", c_uint8, 2),#2bit;

        ("mc_state", c_uint8, 4),#4bit; mc state
        ("ma_state", c_uint8, 4),#4bit; ma state

        ("entry_state", c_uint32),#32bit; feed entry position state
        ("park_state", c_uint32),#32bit; park position state
    ]

####################################
#Class:
#Description: Lan Caigang-20230830
####################################
class AMSDetailInfoBytes(Union):#ChromaKit MMU detailed status
    _fields_ = [
        ("field", AMSDetailInfoSt),
        ("whole", c_uint8 * sizeof(AMSDetailInfoSt)),
    ]
