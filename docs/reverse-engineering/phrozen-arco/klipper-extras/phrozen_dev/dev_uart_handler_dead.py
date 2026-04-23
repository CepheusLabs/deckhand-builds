import binascii
import logging
import json
import time
import struct
import re
from .base import *
from .cmds_structs import *
from ctypes import *


class UartHandlerMixin:
    """Mixin for UART receive data handler."""

    def Device_TimmerUartRecvHandler(self,AMSNum,SerialRxBytes, SerialRxASCIIStr):
        #lancaigang240603:Paused - no printing needed
        if "+PAUSE" in SerialRxASCIIStr:
            self.G_PhrozenFluiddRespondInfo("[(dev.py)Device_TimmerUartRecvHandler]Paused%s" % SerialRxASCIIStr)
        else:
            self.G_PhrozenFluiddRespondInfo("[(dev.py)Device_TimmerUartRecvHandler]%s" % SerialRxASCIIStr)

        # #cancelCancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
        #lancaigang250517：
        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        self.G_PhrozenFluiddRespondInfo("Current pause state-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        self.G_PhrozenFluiddRespondInfo("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// Current pause state-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            self.G_PhrozenFluiddRespondInfo("Already in paused state")
        else:
            self.G_PhrozenFluiddRespondInfo("Not paused state")

        #self.G_PhrozenFluiddRespondInfo("Serial receiveG_PauseToLCDString: %s" % self.G_PauseToLCDString)

        # # // AMSMainboard2Firmware-1 1
        # if "V-H1-I1-F?" in SerialRxASCIIStr:
        #     #=====DriveCodeFile.dat
        #     # 1 , 1 , 24053 , 1 , 0
        #     # 2 , 0 , 0 , 0 , 0
        #     # 3 , 0 , 0 , 0 , 0
        #     # 4 , 0 , 0 , 0 , 0
        #     # 5 , 5 , 24046 , 5 , 0
        #     # 6 , 0 , 0 , 0 , 0
        #     # 7 , 7 , 24051 , 7 , 0
        #     # 8 , 0 , 0 , 0 , 0
        #     # 9 , 0 , 0 , 0 , 0
        #     # 10 , 10 , 24054 , 10 , 0
        #     # 11 , 11 , 24047 , 11 , 0
        #     # 12 , 0 , 0 , 0 , 0
        #     # 13 , 0 , 0 , 0 , 0
        #     # 14 , 0 , 0 , 0 , 0
        #     # 15 , 0 , 0 , 0 , 0
        #     # 16 , 0 , 0 , 0 , 0
        #     #lancaigang240530Write version todatFileDriveCodeJson.dat
        #     filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
        #     self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
        #     Lo_AllLine=""
        #     #data = [{"DriveCode":16,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":15,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":14,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":13,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":12,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":11,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":10,"DriveImageType":10,"DriveHwVersion":10,"DriveFwVersion":24045,"DriveId":0},{"DriveCode":9,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":8,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":7,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":6,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":5,"DriveImageType":5,"DriveHwVersion":5,"DriveFwVersion":24046,"DriveId":0},{"DriveCode":4,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":3,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":2,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":1,"DriveImageType":1,"DriveHwVersion":1,"DriveFwVersion":24042,"DriveId":0}]
        #     #f = open(filename, 'a')
        #     #json.dump(data, f)  #Object serial number as byte stream
        #     #f.close()
        #     with open(filename,'r') as file:
        #         #for line in file:
        #         # # realine() Read the entire line including "\n" Character
        #         # self.G_PhrozenFluiddRespondInfo(file.readline().strip())
        #         # #time.sleep(1)
        #         Lo_FileDataList=file.readlines()
        #         for line in Lo_FileDataList:
        #             #split = [i[:-1].split(',') for i in file.readlines()]
        #             #self.G_PhrozenFluiddRespondInfo(type(split))
        #             #self.G_PhrozenFluiddRespondInfo(split[1])
        #             #self.G_PhrozenFluiddRespondInfo(split[2])
        #             #self.G_PhrozenFluiddRespondInfo(split[3])
        #             #line_strip=line.strip()
        #             #self.G_PhrozenFluiddRespondInfo(line)
        #             #self.G_PhrozenFluiddRespondInfo("line.count=%d" % line.count)
        #             split=line.split(',')
        #             #self.G_PhrozenFluiddRespondInfo(type(split))
        #             #self.G_PhrozenFluiddRespondInfo("".join(split))
        #             #self.G_PhrozenFluiddRespondInfo(split[0])
        #             split[0]=split[0].strip()#Driver number
        #             split[1]=split[1].strip()#Hardwareid
        #             split[2]=split[2].strip()#Firmware version
        #             split[3]=split[3].strip()#Firmware imageid
        #             split[4]=split[4].strip()#Online status
        #             #split[4]='0'#Online check - default to0
        #             if "SN1" in SerialRxASCIIStr:
        #                 if split[0] == "1":
        #                     self.G_PhrozenFluiddRespondInfo(split[0])
        #                     self.G_PhrozenFluiddRespondInfo(split[1])
        #                     self.G_PhrozenFluiddRespondInfo(split[2])
        #                     self.G_PhrozenFluiddRespondInfo(split[3])
        #                     self.G_PhrozenFluiddRespondInfo(split[4])
        #                     #line=("%d,%d,%d," % (HW_VERSION,,))
        #                     line_modify=split[0]+','+'1'+','+SerialRxASCIIStr[9:14]+','+'1'+','+'1'
        #                     self.G_PhrozenFluiddRespondInfo(line_modify)
        #                     Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
        #                 else:
        #                     Lo_AllLine=Lo_AllLine+line
        #             if "SN2" in SerialRxASCIIStr:
        #                 if split[0] == "2":
        #                     self.G_PhrozenFluiddRespondInfo(split[0])
        #                     self.G_PhrozenFluiddRespondInfo(split[1])
        #                     self.G_PhrozenFluiddRespondInfo(split[2])
        #                     self.G_PhrozenFluiddRespondInfo(split[3])
        #                     self.G_PhrozenFluiddRespondInfo(split[4])
        #                     #line=("%d,%d,%d," % (HW_VERSION,,))
        #                     line_modify=split[0]+','+'1'+','+SerialRxASCIIStr[9:14]+','+'1'+','+'1'
        #                     self.G_PhrozenFluiddRespondInfo(line_modify)
        #                     Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
        #                 else:
        #                     Lo_AllLine=Lo_AllLine+line
        #             if "SN3" in SerialRxASCIIStr:
        #                 if split[0] == "3":
        #                     self.G_PhrozenFluiddRespondInfo(split[0])
        #                     self.G_PhrozenFluiddRespondInfo(split[1])
        #                     self.G_PhrozenFluiddRespondInfo(split[2])
        #                     self.G_PhrozenFluiddRespondInfo(split[3])
        #                     self.G_PhrozenFluiddRespondInfo(split[4])
        #                     #line=("%d,%d,%d," % (HW_VERSION,,))
        #                     line_modify=split[0]+','+'1'+','+SerialRxASCIIStr[9:14]+','+'1'+','+'1'
        #                     self.G_PhrozenFluiddRespondInfo(line_modify)
        #                     Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
        #                 else:
        #                     Lo_AllLine=Lo_AllLine+line
        #             if "SN4" in SerialRxASCIIStr:
        #                 if split[0] == "4":
        #                     self.G_PhrozenFluiddRespondInfo(split[0])
        #                     self.G_PhrozenFluiddRespondInfo(split[1])
        #                     self.G_PhrozenFluiddRespondInfo(split[2])
        #                     self.G_PhrozenFluiddRespondInfo(split[3])
        #                     self.G_PhrozenFluiddRespondInfo(split[4])
        #                     #line=("%d,%d,%d," % (HW_VERSION,,))
        #                     line_modify=split[0]+','+'1'+','+SerialRxASCIIStr[9:14]+','+'1'+','+'1'
        #                     self.G_PhrozenFluiddRespondInfo(line_modify)
        #                     Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
        #                 else:
        #                     Lo_AllLine=Lo_AllLine+line
        #     #self.G_PhrozenFluiddRespondInfo(Lo_AllLine)
        #     with open(filename,"w+") as file_w:
        #         file_w.write(Lo_AllLine)


        # # 16-colorHUBBoard firmware-7 7
        # if "V-H7-I7-F" in SerialRxASCIIStr:
        #     #lancaigang240530Write version todatFileDriveCodeJson.dat
        #     filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
        #     self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
        #     Lo_AllLine=""
        #     #data = [{"DriveCode":16,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":15,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":14,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":13,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":12,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":11,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":10,"DriveImageType":10,"DriveHwVersion":10,"DriveFwVersion":24045,"DriveId":0},{"DriveCode":9,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":8,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":7,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":6,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":5,"DriveImageType":5,"DriveHwVersion":5,"DriveFwVersion":24046,"DriveId":0},{"DriveCode":4,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":3,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":2,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":1,"DriveImageType":1,"DriveHwVersion":1,"DriveFwVersion":24042,"DriveId":0}]
        #     #f = open(filename, 'a')
        #     #json.dump(data, f)  #Object serial number as byte stream
        #     #f.close()
        #     with open(filename,'r') as file:
        #         #for line in file:
        #         # # realine() Read the entire line including "\n" Character
        #         # self.G_PhrozenFluiddRespondInfo(file.readline().strip())
        #         # #time.sleep(1)
        #         Lo_FileDataList=file.readlines()
        #         for line in Lo_FileDataList:
        #             #split = [i[:-1].split(',') for i in file.readlines()]
        #             #self.G_PhrozenFluiddRespondInfo(type(split))
        #             #self.G_PhrozenFluiddRespondInfo(split[1])
        #             #self.G_PhrozenFluiddRespondInfo(split[2])
        #             #self.G_PhrozenFluiddRespondInfo(split[3])
        #             #line_strip=line.strip()
        #             #self.G_PhrozenFluiddRespondInfo(line)
        #             #self.G_PhrozenFluiddRespondInfo("line.count=%d" % line.count)
        #             split=line.split(',')
        #             #self.G_PhrozenFluiddRespondInfo(type(split))
        #             #self.G_PhrozenFluiddRespondInfo("".join(split))
        #             #self.G_PhrozenFluiddRespondInfo(split[0])
        #             split[0]=split[0].strip()#Driver number
        #             split[1]=split[1].strip()#Hardwareid
        #             split[2]=split[2].strip()#Firmware version
        #             split[3]=split[3].strip()#Firmware imageid
        #             split[4]=split[4].strip()#Online status
        #             if split[0]== "7":
        #                 self.G_PhrozenFluiddRespondInfo(split[0])
        #                 self.G_PhrozenFluiddRespondInfo(split[1])
        #                 self.G_PhrozenFluiddRespondInfo(split[2])
        #                 self.G_PhrozenFluiddRespondInfo(split[3])
        #                 self.G_PhrozenFluiddRespondInfo(split[4])
        #                 #line=("%d,%d,%d," % (HW_VERSION,,))
        #                 line_modify=split[0]+','+'7'+','+SerialRxASCIIStr[9:14]+','+'7'+','+'1'
        #                 self.G_PhrozenFluiddRespondInfo(line_modify)
        #                 Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
        #             else:
        #                 Lo_AllLine=Lo_AllLine+line
        #     #self.G_PhrozenFluiddRespondInfo(Lo_AllLine)
        #     with open(filename,"w+") as file_w:
        #         file_w.write(Lo_AllLine)


        #lancaigang240326:
        #self.G_PauseToLCDString=SerialRxASCIIStr
        #// ttyUSB0Serial receive: CS00N0M03T04C0
        self.Device_ReportModeIfChanged()


        #lancaigang240524Unknown mode - not aM1-MC M2-MA M3Mode active - skip subsequent pause operations
        #lancaigang240521Do not pause if not in print mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#M1
            self.G_PhrozenFluiddRespondInfo("Unknown mode - skip serial data processing")
            return
            #lancaigang240524Permanently exit the callback
            #return self.G_PhrozenReactor.NEVER




        #Old AMS
        # // lancaigang231202:+PAUSE:1,ch;1-filament depleted/jammed during feed, pause
        # // lancaigang231202:+PAUSE:2,ch;2-pause ACK
        # // lancaigang231204:+PAUSE:3,ch;3-new channel slow refill timeout 10s during printing, pause
        # // lancaigang231205:+PAUSE:4,ch;4-new channel filament feed timeout 50s, pause
        # // lancaigang231205:+PAUSE:5,ch;5-new channel fast refill timeout 10s during printing, pause
        # // lancaigang231205:+PAUSE:6,ch;6-entry to park position timeout 10s, pause
        # // lancaigang231205:+PAUSE:7,ch;7-buffer full state timeout 30s, pause
        # // lancaigang231205:+PAUSE:8,ch;8-toolhead cutter or sensor abnormal, pause
        # // lancaigang231205:+PAUSE:9,ch;9-filament change timeout 120s, pause
        # // lancaigang231202:+PAUSE:a,ch;a-park position to buffer entry timeout 10s, pause
        # // lancaigang231202:+PAUSE:b,ch;b-reserved
        # // lancaigang231202:+PAUSE:c,ch;c-reserved
        # // lancaigang231202:+PAUSE:d,ch;d-reserved
        # // lancaigang231202:+PAUSE:10,ch;10-touchscreen or fluidd web UI initiated pause

        #New AMS
        # // lancaigang231202:+PAUSE:1,oldchannel,newchannel;1-not used in new AMS
        # // lancaigang231202:+PAUSE:2,oldchannel,newchannel;2-pause ACK
        # // lancaigang231204:+PAUSE:3,oldchannel,newchannel;3-
        # // lancaigang231205:+PAUSE:4,oldchannel,newchannel;4-feed timeout, pause (1. filament jammed during feed timeout 60s; 2. during feed)
        # // lancaigang231205:+PAUSE:5,oldchannel,newchannel;5-
        # // lancaigang231205:+PAUSE:6,oldchannel,newchannel;6-entry to buffer timeout 20s, pause
        # // lancaigang231205:+PAUSE:7,oldchannel,newchannel;7-buffer full state timeout 60s, pause (possible causes: abnormal feed overfill, toolhead jam, or hotend clog)
        # // lancaigang231205:+PAUSE:8,oldchannel,newchannel;8-toolhead cutter or sensor abnormal, 6s timeout; pause (possible causes: old channel depleted cannot retract, spool too low to retract, or cutter abnormal)
        # // lancaigang231205:+PAUSE:9,oldchannel,newchannel;9-
        # // lancaigang231202:+PAUSE:a,oldchannel,newchannel;a-
        # // lancaigang231202:+PAUSE:b,oldchannel,newchannel;b-single-color filament runout detection; no filament detected for ~3s, pause
        # // lancaigang231202:+PAUSE:c,oldchannel,newchannel;c-toolhead clog during purge; timeout 20s
        # // lancaigang231202:+PAUSE:d,oldchannel,newchannel;d-AMS cannot feed during purge, filament has bite marks; timeout 20s
        # // lancaigang231202:+PAUSE:e,oldchannel,newchannel;e-at print start, AMS not in drying state but chamber temp over 45C, pause and block print
        # // lancaigang231202:+PAUSE:f,oldchannel,newchannel;f-at print start, AMS currently drying but chamber temp over 45C, pause, block print, and stop drying
        # // lancaigang231202:+PAUSE:g,oldchannel,newchannel;g-ChromaKit MMU USB cable error, printing timeout 10s, report pause
        # // lancaigang231202:+PAUSE:h,oldchannel,newchannel;h-
        # // lancaigang231202:+PAUSE:i,oldchannel,newchannel;i-
        # // lancaigang231202:+PAUSE:j,oldchannel,newchannel;j-
        # // lancaigang231202:+PAUSE:10,oldchannel,newchannel;10-touchscreen or fluidd web UI initiated pause

        #MSG messages
         # // lancaigang250516:+MSG:1,0/1,oldchannel,newchannel;0-Purge started 1-Purge finished


        #lancaigang241128：
        #lancaigang250712:If print is cancelled, only filterAMSPause command
        if self.G_CancelFlag==True:
            self.G_PhrozenFluiddRespondInfo("Print cancelled - filtering out pause commands")
            return




        if "+PAUSE:1" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode active - duplicate pauseif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Filament ran out and jammed during load")
            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #if self.G_IfChangeFilaOngoing== False:
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #Force a filament load first to clear any abnormal entry sensor state
                    self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    self.G_PhrozenFluiddRespondInfo("Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                else:
                    #Special refill state
                    #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)

                    #lancaigang231207During filament change, if the filament jams after running out, it must be extracted from the toolhead feed tube - cannot retract normally
                    self.G_IfInFilaBlockFlag=True
                    #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                    self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")

                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        #klipperActive pause
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")




                    self.G_KlipperIfPaused = True

                    self.STM32ReprotPauseFlag=1
                    #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                    self.G_ChangeChannelFirstFilaFlag=True
                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    if "+PAUSE:1,1" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("1")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,1")
                        self.G_PauseToLCDString="+PAUSE:1,1"
                        self.G_Pause1Channel=1
                    elif "+PAUSE:1,2" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("2")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,2")
                        self.G_PauseToLCDString="+PAUSE:1,2"
                        self.G_Pause1Channel=2
                    elif "+PAUSE:1,3" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("3")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,3")
                        self.G_PauseToLCDString="+PAUSE:1,3"
                        self.G_Pause1Channel=3
                    elif "+PAUSE:1,4" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("4")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,4")
                        self.G_PauseToLCDString="+PAUSE:1,3"
                        self.G_Pause1Channel=4
                    elif "+PAUSE:1,5" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("5")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,5")
                        self.G_PauseToLCDString="+PAUSE:1,5"
                        self.G_Pause1Channel=5
                    elif "+PAUSE:1,6" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("6")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,6")
                        self.G_PauseToLCDString="+PAUSE:1,6"
                        self.G_Pause1Channel=6
                    elif "+PAUSE:1,7" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("7")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,7")
                        self.G_PauseToLCDString="+PAUSE:1,7"
                        self.G_Pause1Channel=7
                    elif "+PAUSE:1,8" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("8")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,8")
                        self.G_PauseToLCDString="+PAUSE:1,8"
                        self.G_Pause1Channel=8
                    elif "+PAUSE:1,9" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("9")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,9")
                        self.G_PauseToLCDString="+PAUSE:1,9"
                        self.G_Pause1Channel=9
                    elif "+PAUSE:1,10" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("10")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,10")
                        self.G_PauseToLCDString="+PAUSE:1,10"
                        self.G_Pause1Channel=10
                    elif "+PAUSE:1,11" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("11")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,11")
                        self.G_PauseToLCDString="+PAUSE:1,11"
                        self.G_Pause1Channel=11
                    elif "+PAUSE:1,12" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("12")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,12")
                        self.G_PauseToLCDString="+PAUSE:1,12"
                        self.G_Pause1Channel=12
                    elif "+PAUSE:1,13" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("13")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,13")
                        self.G_PauseToLCDString="+PAUSE:1,13"
                        self.G_Pause1Channel=13
                    elif "+PAUSE:1,14" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("14")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,14")
                        self.G_PauseToLCDString="+PAUSE:1,14"
                        self.G_Pause1Channel=14
                    elif "+PAUSE:1,15" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("15")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,15")
                        self.G_PauseToLCDString="+PAUSE:1,15"
                        self.G_Pause1Channel=15
                    elif "+PAUSE:1,16" in SerialRxASCIIStr:
                        self.G_PhrozenFluiddRespondInfo("16")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,16")
                        self.G_PauseToLCDString="+PAUSE:1,16"
                        self.G_Pause1Channel=16
                    else:
                        self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PauseToLCDString=SerialRxASCIIStr
                self.G_PhrozenFluiddRespondInfo("+PAUSE:1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

            return


        if "+PAUSE:2" in SerialRxASCIIStr:
            self.G_PhrozenFluiddRespondInfo("PauseACK")
            #self.G_PhrozenFluiddRespondInfo("+PAUSE:2,%d" % self.G_ChangeChannelTimeoutNewChan)

            return


        if "+PAUSE:3" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode active - duplicate pauseif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return

            self.G_PhrozenFluiddRespondInfo("Slow refill timed out during new channel printing10sPausing")

            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return



            # #if self.G_IfChangeFilaOngoing== False:
            # #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            # if self.STM32ReprotPauseFlag==0:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
            #     self.STM32ReprotPauseFlag=1
            #     self.G_KlipperIfPaused = True
            #     self.G_ChangeChannelFirstFilaFlag=True
            #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:3,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
            #     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            # else:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #Force a filament load first to clear any abnormal entry sensor state
                    #lancaigang240323Tends to cause jams - disabled for now
                    #self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:3,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #Special refill state
                        #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)



                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:3,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:3,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:3,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:3,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:3,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)




            return


        if "+PAUSE:5" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAAlready in this mode - duplicate pauseif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Fast refill timed out during new channel printing10sPausing")

            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            # #if self.G_IfChangeFilaOngoing== False:
            # #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            # if self.STM32ReprotPauseFlag==0:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
            #     self.STM32ReprotPauseFlag=1
            #     self.G_KlipperIfPaused = True
            #     self.G_ChangeChannelFirstFilaFlag=True
            #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:5,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
            #     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            # else:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #Force a filament load first to clear any abnormal entry sensor state
                    #lancaigang240323Tends to cause jams - disabled for now
                    #self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:5,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #Special refill state
                        #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)

                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:5,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:5,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:5,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:5,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:5,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return


        if "+PAUSE:4" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: duplicate pause detectedif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("New channel load timed out50sPausing")

            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            # #if self.G_IfChangeFilaOngoing== False:
            # #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            # if self.STM32ReprotPauseFlag==0:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
            #     self.STM32ReprotPauseFlag=1
            #     self.G_KlipperIfPaused = True
            #     self.G_ChangeChannelFirstFilaFlag=True
            #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
            #     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            # else:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #lancaigang240323Tends to cause jams - disabled for now
                    #self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #Special refill state
                        #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)

                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return


        if "+PAUSE:6" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode active - duplicate pauseif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Timeout moving from entry position to park position10sPausing")

            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            # #if self.G_IfChangeFilaOngoing== False:
            # #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            # if self.STM32ReprotPauseFlag==0:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
            #     self.STM32ReprotPauseFlag=1
            #     self.G_KlipperIfPaused = True
            #     self.G_ChangeChannelFirstFilaFlag=True
            #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:6,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
            #     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            # else:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #Force a filament load first to clear any abnormal entry sensor state
                    #lancaigang240323Tends to cause jams - disabled for now
                    #self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:6,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #Special refill state
                        #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)

                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:6,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:6,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:6,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:6,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:6,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return


        if "+PAUSE:7" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode active - duplicate pauseif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return

            self.G_PhrozenFluiddRespondInfo("Buffer full state timed out30sPausing")

            #lancaigang231215:
            self.G_STM32PauseCount+=1
            if self.G_STM32PauseCount==5:
                self.G_PhrozenFluiddRespondInfo("if self.G_STM32PauseCount==5;G_STM32PauseCount=%d" % self.G_STM32PauseCount)
                self.G_STM32PauseCount=0
            else:
                self.G_PhrozenFluiddRespondInfo("else;G_STM32PauseCount=%d" % self.G_STM32PauseCount)

            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        #lancaigang240103After resume, send command tostm32Restore previous state machine state
                        #Resume stateRS=F,Immediately restore previous state
                        #Resume stateRS=0,Immediately restore previousIDLE_STANDBYState
                        #Resume stateRS=X,...
                        #Resume stateRS=Y,...
                        #Resume stateRS=Z,...
                        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                            self.Cmds_AMSSerial1Send("AT+MARS=F")
                            self.G_PhrozenFluiddRespondInfo("Duplicate pause detectedMA;AT+MARS=F；STM32Restore previous state")

                        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
                            self.Cmds_AMSSerial1Send("AT+MCRS=F")
                            self.G_PhrozenFluiddRespondInfo("Duplicate pause detectedMC;AT+MCRS=F；STM32Restore previous state")



                        # self.G_ProzenToolhead.dwell(1.0)
                        # self.Cmds_AMSSerial1Send("AT+MARS=F")
                        # self.G_PhrozenFluiddRespondInfo("AT+MARS=F")

                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            # #if self.G_IfChangeFilaOngoing== False:
            # #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            # if self.STM32ReprotPauseFlag==0:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
            #     self.STM32ReprotPauseFlag=1
            #     self.G_KlipperIfPaused = True
            #     self.G_ChangeChannelFirstFilaFlag=True
            #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:7,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
            #     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            # else:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #Force a filament load first to clear any abnormal entry sensor state
                    #self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True

                    #lancaigang250725:Hall sensor still detects filament during print - likely a nozzle clog
                    if self.G_ToolheadIfHaveFilaFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Hall sensor detects filament during purge - nozzle clog")
                        self.G_PauseToLCDString="+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_PhrozenFluiddRespondInfo("Buffer unexpectedly full during purge but Hall sensor has no filament detected - classified as load timeout")
                        self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #Special refill state
                    #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)


                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)


                        #lancaigang250725:Hall sensor still detects filament during print - likely a nozzle clog
                        if self.G_ToolheadIfHaveFilaFlag==True:
                            self.G_PhrozenFluiddRespondInfo("Hall sensor detects filament during print - nozzle clog detected")
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:7,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                            self.G_PauseToLCDString="+PAUSE:7,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_PhrozenFluiddRespondInfo("Buffer unexpectedly full during filament feed but Hall sensor has no filament detected - classified as load timeout")
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                            self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:7,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:7,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:7,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return



        if "+PAUSE:a" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: duplicate pause detectedif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Timeout moving from park position to buffer entry10sPausing")


            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            # #if self.G_IfChangeFilaOngoing== False:
            # #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            # if self.STM32ReprotPauseFlag==0:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
            #     self.STM32ReprotPauseFlag=1
            #     self.G_KlipperIfPaused = True
            #     self.G_ChangeChannelFirstFilaFlag=True
            #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
            #     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            # else:
            #     self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
            #lancaigang240325:Check for any pause reports from the MCU during the resume process
            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    #Force a filament load first to clear any abnormal entry sensor state
                    #lancaigang240323Tends to cause jams - disabled for now
                    #self.Cmds_AMSSerial1Send("E%d" % self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: E%d" % self.G_ChangeChannelTimeoutNewChan)

                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:a,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #Special refill state
                        #self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]Send command: H%d" % self.G_ChangeChannelTimeoutNewChan)

                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)

                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)a

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:a,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:a,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return

        #lancaigang250423:Nozzle clog detection during printing
        if "+PAUSE:c" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: duplicate pause detectedif self.G_KlipperIfPaused == True:")

                    #lancaigang251124：
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: toolhead detected filament, but during purgestm32Pause error - cannot directlyreturn；")
                    self.STM32ReprotPauseFlag=1
                    #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                    #self.G_ChangeChannelFirstFilaFlag=True
                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    self.G_PauseToLCDString="+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Nozzle clog detected - pausing")


            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True

                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)a

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return


        #lancaigang250506:Refill error during purge - filament has bite marks from gear
        if "+PAUSE:d" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: duplicate pause detectedif self.G_KlipperIfPaused == True:")


                    #lancaigang251124：
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: toolhead detected filament, but during refillstm32Pause error - cannot directlyreturn；")
                    self.STM32ReprotPauseFlag=1
                    #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                    #self.G_ChangeChannelFirstFilaFlag=True
                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:c,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    self.G_PauseToLCDString="+PAUSE:d,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Purge/refill error - filament has bite marks (gear damage), pausing")


            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:d,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)a

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:d,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:d,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:d,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:d,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return

        #//lancaigang250507:+PAUSE:e,oldchannel,newchannel;e-When dryer is not active,AMSChamber temperature too high - printing not allowed
        if "+PAUSE:e" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: duplicate pause detectedif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return

            #lancaigang250510Not in print mode - pause not allowedklipperBut must notify the serial touchscreen
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("Not in print mode - pause not allowedklipperBut must notify the serial touchscreen")
                self.G_PhrozenFluiddRespondInfo("+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                return

            self.G_PhrozenFluiddRespondInfo("When dryer is not active,AMSChamber temperature too high - printing not allowed, pausing")


            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)a

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:e,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:e,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return

        #//lancaigang250507:+PAUSE:f,oldchannel,newchannel;f-Dryer is active - printing not allowed
        if "+PAUSE:f" in SerialRxASCIIStr:
            #lancaigang240106In single-color auto-refill mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refillMAMode: duplicate pause detectedif self.G_KlipperIfPaused == True:")
                    return
            #lancaigang240413In single-color mode, do not allow another pause if already paused
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("Single-colorM3Mode, withAMSMulti-color mode - duplicate pause:")
                    return
            self.G_PhrozenFluiddRespondInfo("Dryer is active - printing not allowed, pausing")

            #lancaigang250510Not in print mode - pause not allowedklipperBut must notify the serial touchscreen
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("Not in print mode - pause not allowedklipperBut must notify the serial touchscreen")
                self.G_PhrozenFluiddRespondInfo("+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                return


            #lancaigang240103Ignore if the pause was initiated by the touchscreenstm32MCU active report of
            if self.G_ToolheadIfHaveFilaFlag == True:
                    if self.G_IfToolheadHaveFilaInitiativePauseFlag==True:
                        self.G_PhrozenFluiddRespondInfo("Touchscreen initiated pause - ignoringstm32Active report")
                        return
            #lancaigang240113Filter if this is a manual commandstm32Pause report of
            if self.ManualCmdFlag==True or self.G_CutCheckTest==True:
                #lancaigang240611Report manual commands to the serial touchscreen as well
                self.G_PhrozenFluiddRespondInfo(SerialRxASCIIStr)
                #self.ManualCmdFlag=False
                self.G_PhrozenFluiddRespondInfo("Manual test command - ignoringstm32MCU actively reported pause")
                return

            self.G_ResumeProcessCheckPauseStatus=True
            self.G_PauseToLCDString=SerialRxASCIIStr
            #lancaigang240124：stm32MCU-reported pause can only pause1 time(s)
            if self.STM32ReprotPauseFlag==0:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                if self.PG102Flag==True:
                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    self.PG102DelayPauseFlag=True
                    self.G_PauseToLCDString="+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        #lancaigang231209Processing logic inside timer callbacks causes errors - should use a dedicated thread for interrupt handling instead
                        self.G_PhrozenFluiddRespondInfo("stm32MCU reported active pause - pausing1 time(s)")
                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                        self.G_ChangeChannelFirstFilaFlag=True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)a

                        self.G_PhrozenFluiddRespondInfo("+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    else:
                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

            else:
                self.G_PauseTriggerWhileChangeChannelFlag=True
                self.G_PhrozenFluiddRespondInfo("stm32MCU reported an active pause - duplicate pause detected")
                #lancaigang240325Report duplicate pause to the serial touchscreen as well
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:a,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                self.G_PhrozenFluiddRespondInfo("+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:f,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            return












        if "+FORCEFORWARD:1" in SerialRxASCIIStr:
            self.G_PhrozenFluiddRespondInfo("Remove the toolhead feed tube and force-extract jammed filament")
            return



        #lancaigang231202If receivedstm32If pause response received, pauseklipper




        # // CSDeviceid   Operating mode PreviousmcState   CurrentmcState  Channel number
        # // CS00       N0      M09         T09         C5
        # // CS00       N0      M02         T03         C0
        # // CS00       N0      M08         T10         C1
        #    deviceid   mode    pre_state   state       chan
        #Parse serial data using regex
        #CS00N0M03T04C0
        message_obj = re.match(
            AMS_SERIALPORT_RECEIV_PARSE_PATTERN,#Regular expression
            SerialRxASCIIStr,
            re.M | re.I,
        )


        # Parsed serial data contains errors
        if not message_obj:
            return


        if int(message_obj.group("mode")) is AMS_MC_MODE:
            self.G_PhrozenFluiddRespondInfo("Modemode==Multi-color mode==%d" % AMS_MC_MODE)
        if int(message_obj.group("mode")) is AMS_MA_MODE:
            self.G_PhrozenFluiddRespondInfo("Modemode==Auto-refill mode==%d" % AMS_MA_MODE)

        if int(message_obj.group("state")) is MC_STANDBY:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Standby phase==%d" % MC_STANDBY)
        if int(message_obj.group("state")) is MC_PREPARTION:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Filament staging park phase==%d" % MC_STANDBY)
        if int(message_obj.group("state")) is MC_CHANGING_P1:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Filament change phase1==%d" % MC_CHANGING_P1)
        if int(message_obj.group("state")) is MC_CHANGING_P2:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Filament change phase2==%d" % MC_CHANGING_P2)
        if int(message_obj.group("state")) is MC_FORCE_FEED:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Force refill during filament change phase==%d" % MC_FORCE_FEED)
        if int(message_obj.group("state")) is MC_PRINTING:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Refill during print phase==%d" % MC_PRINTING)
        if int(message_obj.group("state")) is MC_ROLLBACK:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Full filament unload==%d" % MC_ROLLBACK)
        if int(message_obj.group("state")) is MC_PARKBACK:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Unload filament to park position==%d" % MC_PARKBACK)
        if int(message_obj.group("state")) is MC_PARKALL:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Unload all filaments to park position==%d" % MC_PARKALL)
        if int(message_obj.group("state")) is MC_CLEANING:
            self.G_PhrozenFluiddRespondInfo("Current statestate==All filaments cleared==%d" % MC_CLEANING)
        if int(message_obj.group("state")) is MC_ERR_TIMEOUT:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Timeout error state==%d" % MC_ERR_TIMEOUT)
        if int(message_obj.group("state")) is MC_ERR_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Filament runout error state==%d" % MC_ERR_RUNOUT)
        if int(message_obj.group("state")) is MC_ERR_BLOCKUP:
            self.G_PhrozenFluiddRespondInfo("Current statestate==Filament jam error state==%d" % MC_ERR_BLOCKUP)
            #raise self.error("Motor filament jam error")
            #self.Cmds_PhrozenKlipperPause(None)

        self.G_PhrozenFluiddRespondInfo("Channel motor numberchan==%d" % int(message_obj.group("chan")))
        #raise self.error("Test: channel motor number")

        # lancaigang20231013Filament change phase handling: re-load after jam
        if int(message_obj.group("mode")) is AMS_MC_MODE:
            #lancaigang20231114Sometimes load retries loop endlessly - disabling for now
            cur_chan = int(message_obj.group("chan")) + 1
            # #lancaigang20231013Filament change phase2-->Force refill
            # if (int(message_obj.group("pre_state")) is MC_CHANGING_P2) and (int(message_obj.group("state")) is MC_FORCE_FEED):
            #     #lancaigang20231013No filament at the toolhead, But buffer is in full state, Indicates filament jam, Re-run unload and load sequence
            #     if not self.G_ToolheadIfHaveFilaFlag:
            #         self.AMSErrorRetryTimes += 1
            #         if self.AMSErrorRetryTimes < 5:
            #             #// =====T1~TnCommandPRZ_T[n] P1 T[n]n:1 ~32(device not on network, use1 ~4)Manually switch to the specified channel,Filament swap only(For testing)
            #             self.Cmds_AMSSerial1Send("T%d" % cur_chan)
            #             self.G_PhrozenFluiddRespondInfo("Toolhead did not detect filament during filament change, commandT?Retryingcmd T%s at %d times" % (cur_chan, self.AMSErrorRetryTimes))
            #         else:
            #             self.G_PhrozenFluiddRespondInfo("Toolhead did not detect filament during filament change, commandT?Retried5 time(s), CommandP?Retract to park position")
            #             #// Retract to park position// =====P1 D[n]；n:1~32(device not on network, use1~4)Retract filament in the specified channel back to the park position and stand by Yes；====="P?"；
            #             self.Cmds_AMSSerial1Send("P%d" % cur_chan)
            #             self.Cmds_PhrozenKlipperPause(None)
            #             self.AMSErrorRetryTimes = 0
            #     #lancaigang20231013Filament detected at the toolhead
            #     else:
            #         # After state returns to normal, Reset error retry counter
            #         self.AMSErrorRetryTimes = 0

            #     return self.G_PhrozenReactor.NOW + AMS_SERIALPORT_RECV_TIMER

            #lancaigang231103Disable firststm32Timeout status handling on return is unnecessary and causes execution order issues
            #lancaigang20231013：stm32Timeout state handling
            # if int(message_obj.group("state")) is MC_ERR_TIMEOUT:
            #     # typedef enum Enum_MCStateMachine {
            #     #     // 00； IdleStandby phase
            #     #     MCSTATEMACHINE_IDLE_STANDBY,
            #     #     // 01； Parked and waiting to load filament into printer phase// =====P1 S0 All channels parked and ready to load filament into the printer, Can load filament to park position or retract to park position====="RD";
            #     #     MCSTATEMACHINE_PARKPOSITION_ISREADY_INFILA_TO_PRINTER,
            #     #     // 02； Filament change phase1；// =====P1 T[n]n:1 ~32(device not on network, use1 ~4)Manually switch to the specified channel,Filament swap only(For testing)；====="T?"；
            #     #     MCSTATEMACHINE_CHANGING_FILA_STAGE_P1,
            #     #     // 03； Filament change phase2；// =====P1 T[n]n:1 ~32(device not on network, use1 ~4)Manually switch to the specified channel,Filament swap only(For testing)；====="T?"；
            #     #     MCSTATEMACHINE_CHANGING_FILA_STAGE_P2,
            #     #     // 04； Force-feed filament to the toolhead, corresponding toP1 T?
            #     #     MCSTATEMACHINE_FORCE_FEED_INFILA_TO_PRINTER,
            #     #     // 05； Phase during printing(Refill)
            #     #     MCSTATEMACHINE_PRINTING_INPROCESS_FEED,
            #     #     // 06； Full filament unload// =====B1~BnCommandPRZ_B[n] P1 B[n]n:1 ~32(device not on network, use1 ~4)Fully retract filament from the specified channel Yes
            #     #     MCSTATEMACHINE_FULLY_ROLLBACK,
            #     #     // 07； Retract to park position//"P"；P1 D[n]；n:1~32(device not on network, use1~4)Retract filament in the specified channel to park position and stand by Yes
            #     #     MCSTATEMACHINE_ROLLBACK_TO_PARKPOSITION,
            #     #     // 08； Retract all to park position// "AP"；P2 A1 All filaments retracted to park position, ready to print Yes
            #     #     MCSTATEMACHINE_ROLLBACK_ALL_TO_PARKPOSITION,
            #     #     // 09； Clear all filaments//====="CL"； P2 A2Retract all filaments Yes
            #     #     MCSTATEMACHINE_CLEAN_ALL_CHANNEL,
            #     #     // 10； Timeout error state
            #     #     MCSTATEMACHINE_ERROR_TIMEOUT,
            #     #     // 11； Filament runout error state
            #     #     MCSTATEMACHINE_ERROR_RUNOUT,
            #     # } Enum_MCStateMachine;
            #     self.AMSErrorRetryTimes += 1
            #     if self.AMSErrorRetryTimes < 5:
            #         #// =====T1~TnCommandPRZ_T[n] P1 T[n]n:1 ~32(device not on network, use1 ~4)Manually switch to the specified channel,Filament swap only(For testing)
            #         self.G_PhrozenFluiddRespondInfo("stm32Error state - commandT?Retryingcmd T%s at %d times" % (message_obj.group("chan"), self.AMSErrorRetryTimes))
            #         self.Cmds_AMSSerial1Send("T%d" % cur_chan)
            #     else:
            #         self.G_PhrozenFluiddRespondInfo("stm32Error state - commandT?Retried5 time(s), CommandP?Retract to park position")
            #         #// Retract to park position// =====P1 D[n]；n:1~32(device not on network, use1~4)Retract filament in the specified channel back to the park position and stand by Yes；====="P?"；
            #         self.Cmds_AMSSerial1Send("P%d" % cur_chan)
            #         self.Cmds_PhrozenKlipperPause(None)
            #         self.AMSErrorRetryTimes = 0

            #     return self.G_PhrozenReactor.NOW + AMS_SERIALPORT_RECV_TIMER



        #lancaigang20231013Auto-refill mode
        if int(message_obj.group("mode")) is AMS_MA_MODE:
            pass
