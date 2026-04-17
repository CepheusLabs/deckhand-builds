####################################
#Project:
#Chip Type:
#Function:
#Developer: Lan Caigang
#Created: 20230830
####################################

import os
import numpy as np

import logging
import json
import time
import serial
from .base import *

from ctypes import *

from .cmds_structs import *
from .cmds_serial import SerialMixin
from .cmds_filament import FilamentMixin
from .cmds_pause import PauseMixin
from .cmds_channel import ChannelChangeMixin
from .cmds_orca import OrcaMixin
from .cmds_system import SystemMixin
from .cmds_pcmds import PCommandsMixin


class Commands(
    PCommandsMixin,
    OrcaMixin,
    ChannelChangeMixin,
    PauseMixin,
    FilamentMixin,
    SystemMixin,
    SerialMixin,
    Base,
):
    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #constructor initialization
    def __init__(self, config):
        super(Commands, self).__init__(config)

        #tty serial port connected flag
        self.G_SerialPort1OpenFlag = False

        #tty serial port connected flag
        self.G_SerialPort2OpenFlag = False

        #tty2 port failure already logged flag (dedup console spam)
        self._tty2_open_failure_logged = False


        #MC filament change first switch
        self.G_ChangeChannelFirstFilaFlag = True
        #Toolhead first filament load
        self.G_ToolheadFirstInputFila = False  # First filament supply
        #klipper paused flag
        self.G_KlipperIfPaused = False
        #Movement speed factor
        self.G_MovementSpeedFactor = 1.0 / 60
        #Toolhead last position
        self.G_ToolheadLastPosition = None
        #AMS work mode
        self.G_AMSDeviceWorkMode = AMS_WORK_MODE_UNKNOW  # default work mode unknown

        #pythondict
        #P9 X190.290 Y238.700 W2.010 H11.200 D1
        # Toolhead waiting parameters during filament change
        self.G_DictChangeChannelWaitAreaParam = {#python {} dict key-valuekey-value pair/to
            "T": self.G_ChangeChannelTimeout,     #change timeout when interval(seconds), default120seconds
            "A": 0,         # actionAction
            "D": 0,         # default directionXdirection orYdirection
            "X": 0.0,       # wait area base pointXcoordinate
            #lancaigang20231020:
            "Y": 20.0,      # wait area base pointYcoordinate
            "W": 0.0,       # wait area base pointXdirection width
            "H": 0.0,       # wait area base pointYdirection height
        }



        # Following parameters are assigned in connect
        #toolhead
        self.G_ProzenToolhead = None
        #toolhead manual move
        self.G_ToolheadManualMovement = None
        #wait toolhead move end
        self.G_ToolheadWaitMovementEnd = None


        #lancaigang231115:print filament change timeout, add resume print function
        #lancaigang231216:default use channel0, not yetknow channel
        self.G_ChangeChannelTimeoutOldChan=-1
        self.G_ChangeChannelTimeoutOldGcmd=None
        #lancaigang240912:newAMS, use new old channel record
        self.G_ChangeChannelTimeoutNewChan=-1
        self.G_ChangeChannelTimeoutNewGcmd=None


        #lancaigang231206:pause not allowed during resume
        self.G_ChangeChannelResumeFlag = False

        # prepare generate path
        self.ChangeWaitMoveArea = []  # pathqueue


        #lancaigang231216:filament change wait area zoneXYbase coordinate
        self.G_XBasePosition=0
        self.G_YBasePosition=0

        #lancaigang231216:if filament change during pointclick pause, justgood filament change during lift risezaxis, to execute pause when, zaxis height also save, causes overall height abnormal
        self.G_IfZPositionLiftUpFlag = False

        #lancaigang231219:
        self.G_SerialPort1Obj=None

        #lancaigang241029:
        self.G_SerialPort2Obj=None

        #lancaigang241030:
        self.G_SerialPortHaveOpenedCount=0
        self.G_SerialPortIsOpenCount=0




    def Cmds_RegisterCmds(self):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_RegisterCmds]registerphrozenself fixed/setdefinegcodecommand")
        # P114 S；simple state；"SB"；
        # P114；all state ；"SD"；
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP114["cmd"],self.Cmds_CmdP114,desc=G_DictPhrozenCmdP114["desc"])
        # P28 connect device
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP28["cmd"],self.Cmds_CmdP28,desc=G_DictPhrozenCmdP28["desc"])
        # P29 disconnect connect
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP29["cmd"],self.Cmds_CmdP29,desc=G_DictPhrozenCmdP29["desc"])
        # P30 auto arrange deviceID(use inmany/more device auto network)；"I";handle auto arrange deviceIDcommand
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP30["cmd"],self.Cmds_CmdP30,desc=G_DictPhrozenCmdP30["desc"])
        # P0 M1；multi-color mode mode(need connect external device) Yes；"MC";
        # P0 M2；multi-color single-color refill mode(need connect external device)；"MA";
        # P0 M3; single-color runout mode
        #lancaigang240801:
        # P0 B?; self fixed/setdefine；
        self.G_PhrozenGCode.register_command(G_DictPhrozenP0["cmd"],self.Cmds_CmdP0,desc=G_DictPhrozenP0["desc"])
        # P2 A1 all filamentmaterial afterretract to park position printwait position Yes；====="AP";
        # P2 A2；retract out all filament Yes；"CL";
        # P2 A3 cut runoutmaterial
        # P2 A4 cut runoutmaterial and retract filament
        # P2 A5 print completecut runoutmaterial and retract filament，cannotcollide tomodel/mold type/model
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP2["cmd"],self.Cmds_CmdP2,desc=G_DictPhrozenCmdP2["desc"])
        # P1 S0 all channel at park position preparegood load filament to printmachine state, can load filament to park position or afterretract to park position；====="RD";
        # P1 T[n]n:1 ~32(device not on network, use1 ~4)manualchange tospecified channel,only filament change(use intesting)；====="T"；
        # P1 B[n]n:1 ~32(device not on network, use1 ~4)specified channel filamentmaterialcompletecomplete retract out Yes；====="B"；
        # P1 D[n]；n:1~32(device not on network, use1~4)；specified channel filamentmaterial afterretract stoppark at park positionstandby state Yes；====="P"；
        # P1 C[n] n:1~32(device not on network, use1~4) autochange tospecified channel(many/more action command,includes cut filament, filament change, wait)；====="T"；
        #lancaigang231202:
        # P1 E[n]；n:1~32(device not on network, use1~4)；specified channel filamentmaterial force before rotate/switch，neednote remove toolhead on material tube Yes；====="E?"；
        # lancaigang240228：toolhead retract a section distance，needstm32first retract a section distance
        # P1 G[n]；n:1~32(device not on network, use1~4)；retract channel filament some distance Yes；====="G?"；
        # lancaigang240319：perform enter special refillstep section，buffer not full then refill
        # =====P1 H[n]；n:1~32(device not on network, use1~4)；perform enter special refillstep section，buffer not full then refill Yes；====="H?"；
        #lancaigang240329：prepare use
        # =====P1 I[n]；manual extrude whenstm32need refill；====="I?"；
        # =====P1 J[n]；multi-color manual purge；refill when buffer not full；
        # =====P1 K[n]；
        # =====P1 L[n]；
        # =====P1 M[n]；
        # =====P1 N[n]；
        # =====P1 O[n]；
        # =====P1 Q[n]；
        # =====P1 U[n]；
        #lancaigang240418：
        # =====P1 V[n]；use in versionnumber
        # =====P1 W[n]；
        # =====P1 X[n]；
        # =====P1 Y[n]；
        # =====P1 Z[n]；
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP1["cmd"],self.Cmds_CmdP1,desc=G_DictPhrozenCmdP1["desc"])
        # P9 X[x_pos]Y[y_pos]W[width]H[height]D[0/1];x_pos:wait area base pointXcoordinatey_pos:wait area base pointYcoordinatewidth:wait area width
        # height:wait area heightD0:by/withXdirectionas slow moveYdirection count number(default)D1:by/withYdirectionas slow moveXdirection count numberset wait area zone
        # P9 T[expire]A[0/1];expire:timeout,unit seconds(default60)A0:ignore timeout,continue print(default)A1:timeout afterend stop printset wait timeout and handle
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP9["cmd"],self.Cmds_CmdP9,desc=G_DictPhrozenCmdP9["desc"])

        #lancaigang241101：
        # P10 S?    parameterS[1,5]:purge time(s)numbercontrol，S1-purge1time(s)，S2-purge2time(s)...，mostmany/moresupport hold purge5time(s)
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP10["cmd"],self.Cmds_CmdP10,desc=G_DictPhrozenCmdP10["desc"])

        #lancaigang250805：
        # P11 multi-color cutter test
        self.G_PhrozenGCode.register_command("P11",self.Cmds_CmdP11,desc="P11")
        #lancaigang250805：
        # P12 multi-color cutterlooptesting
        self.G_PhrozenGCode.register_command("P12",self.Cmds_CmdP12,desc="P12")

        # P8 execute auto refill Yes；"FA"；
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP8["cmd"],self.Cmds_CmdP8,desc=G_DictPhrozenCmdP8["desc"])
        # PRZ_ADC
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdToolheadAdc["cmd"],self.Cmds_PhrozenAdc,desc=G_DictPhrozenCmdToolheadAdc["desc"])
        # PRZ_PAUSEpause
        self.G_PhrozenGCode.register_command("PRZ_PAUSE",self.Cmds_PhrozenKlipperPauseScreen,desc="PHROZEN_PAUSE")
        # PRZ_RESUME resume
        self.G_PhrozenGCode.register_command("PRZ_RESUME",self.Cmds_PhrozenKlipperResume,desc="PHROZEN_RESUME")
        # PRZ_CANCEL cancel print
        self.G_PhrozenGCode.register_command("PRZ_CANCEL",self.Cmds_PhrozenKlipperCancel,desc="PHROZEN_CANCEL")
        # PRZ_VERSION query version
        self.G_PhrozenGCode.register_command("PRZ_VERSION",self.Cmds_PhrozenVersion,desc="PHROZEN_VERSION")
        # P4 emergency stop device；emergency stopStopcommand(time(s)excellent firstlevel)："SP"；
        self.G_PhrozenGCode.register_command(G_DictPhrozenCmdP4["cmd"],self.Cmds_CmdP4,desc=G_DictPhrozenCmdP4["desc"])

        self.G_PhrozenGCode.register_command("PRZ_BM1",self.Cmds_PhrozenBM1,desc="PRZ_BM1")
        self.G_PhrozenGCode.register_command("PRZ_BM0",self.Cmds_PhrozenBM0,desc="PRZ_BM0")

        self.G_PhrozenGCode.register_command("PRZ_PRINT_START",self.Cmds_PrzPrintStart,desc="PRZ_PRINT_START")

        #self.G_PhrozenGCode.register_command("PRINT_END",self.Cmds_PrzPrintEnd,desc="PRINT_END")
        #lancaigang250514:
        self.G_PhrozenGCode.register_command("HOMING_OVERRIDE_END",self.Cmds_HomingOverrideEnd,desc="HOMING_OVERRIDE_END")

        #lancaigang250115：
        self.G_PhrozenGCode.register_command("PRZ_RESTORE",self.Cmds_PrzATRestore,desc="PRZ_RESTORE")
        self.G_PhrozenGCode.register_command("PRZ_IDLE",self.Cmds_PrzATIdle,desc="PRZ_IDLE")


        #lancaigang250324：compatibleorcacutchip/piece soft piece/piece/piece/piece/piece T0 T1 T2 T3color change command
        self.G_PhrozenGCode.register_command("T0",self.Cmds_CmdT0,desc="T0")
        self.G_PhrozenGCode.register_command("T1",self.Cmds_CmdT1,desc="T1")
        self.G_PhrozenGCode.register_command("T2",self.Cmds_CmdT2,desc="T2")
        self.G_PhrozenGCode.register_command("T3",self.Cmds_CmdT3,desc="T3")
        self.G_PhrozenGCode.register_command("T4",self.Cmds_CmdT4,desc="T4")
        self.G_PhrozenGCode.register_command("T5",self.Cmds_CmdT5,desc="T5")
        self.G_PhrozenGCode.register_command("T6",self.Cmds_CmdT6,desc="T6")
        self.G_PhrozenGCode.register_command("T7",self.Cmds_CmdT7,desc="T7")
        self.G_PhrozenGCode.register_command("T8",self.Cmds_CmdT8,desc="T8")
        self.G_PhrozenGCode.register_command("T9",self.Cmds_CmdT9,desc="T9")
        self.G_PhrozenGCode.register_command("T10",self.Cmds_CmdT10,desc="T10")
        self.G_PhrozenGCode.register_command("T11",self.Cmds_CmdT11,desc="T11")
        self.G_PhrozenGCode.register_command("T12",self.Cmds_CmdT12,desc="T12")
        self.G_PhrozenGCode.register_command("T13",self.Cmds_CmdT13,desc="T13")
        self.G_PhrozenGCode.register_command("T14",self.Cmds_CmdT14,desc="T14")
        self.G_PhrozenGCode.register_command("T15",self.Cmds_CmdT15,desc="T15")
