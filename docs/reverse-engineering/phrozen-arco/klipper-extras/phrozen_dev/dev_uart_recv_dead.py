import json
import os
import serial
from .base import *


class UartRecvMixin:
    """Mixin for UART serial port receive timer callbacks."""

    def Device_TimmerUart1Recv(self, eventtime):
        #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerUart1Recv]")
        #lancaigang240427：try catch
        try:
            # if self.G_SerialPort1OpenFlag==False:
            #     self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerUart1Recv]Serial port1Already closed")
            # if self.G_SerialPort2OpenFlag==False:
            #     self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerUart1Recv]Serial port2Already closed")

            #tty1Connection failed
            if self.G_SerialPort1OpenFlag==False:
                self.G_ASM1DisconnectErrorCount=0
                #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerUart1Recv]Serial port1Connection error - permanently exit the callback")
                #self.G_PhrozenFluiddRespondInfo("self.G_AMS1ErrorRestartCount=%d" % self.G_AMS1ErrorRestartCount)
                try:
                    if self.G_SerialPort1Obj is not None:
                        if self.G_SerialPort1Obj.is_open:
                            #tty1Close
                            self.G_SerialPort1Obj.close()
                            self.G_PhrozenFluiddRespondInfo("Close serial port1Success")
                            self.G_PhrozenFluiddRespondInfo("AMS1Connection failed")
                            #self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                            self.G_PhrozenFluiddRespondInfo("Cache the pause command+PAUSE:g")
                except:
                    self.G_PhrozenFluiddRespondInfo("Close serial port1Error")

                self.G_AMS1ErrorRestartCount=self.G_AMS1ErrorRestartCount+1

                #lancaigang241108:Delay a few seconds before pausing to preventAMSRestart takes some time
                if self.G_AMS1ErrorRestartCount>=5:
                    #self.G_PhrozenFluiddRespondInfo("if self.G_AMS1ErrorRestartCount>=5:")

                    self.G_AMS1ErrorRestartCount=0
                    #lancaigang250619:IfUSBOnly report error when the color-change itself fails
                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #self.G_PhrozenFluiddRespondInfo("Cache the pause command+PAUSE:g")

                    # if self.G_KlipperIfPaused==False:
                    #     self.G_KlipperIfPaused = True
                    #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #     if self.G_CancelFlag==False:
                    #         # self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #         # self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #         self.G_PhrozenFluiddRespondInfo("AMS1Connection error - pausing")

                    #         #lancaigang250604:
                    #         if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#M0
                    #             self.G_PhrozenFluiddRespondInfo("Unknown mode - no pause needed")
                    #         else:
                    #             if self.STM32ReprotPauseFlag==0:
                    #                 self.G_PauseTriggerWhileChangeChannelFlag=True
                    #                 if self.PG102Flag==True:
                    #                     self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    #                     self.PG102DelayPauseFlag=True
                    #                     #self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #                     self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #                 else:
                    #                     self.G_PhrozenFluiddRespondInfo("Not purging - can pause immediately")
                    #                     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #                     self.G_KlipperIfPaused = True
                    #                     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #                     self.STM32ReprotPauseFlag=1
                    #                     #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                    #                     self.G_ChangeChannelFirstFilaFlag=True
                    #                     self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #                     self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #             else:
                    #                 self.G_PauseTriggerWhileChangeChannelFlag=True
                    #                 self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    #         #     self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #         #lancaigang20231013Disconnect
                    #         self.Device_DisconnectAMSDevice()

                    # #if self.G_KlipperIfPaused==True:
                    # else:
                    #     self.G_PhrozenFluiddRespondInfo("USBError - already in paused state")
                    #     self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


                    #lancaigang240524Permanently exit the callback
                    return self.G_PhrozenReactor.NEVER


                return eventtime + AMS_SERIALPORT_RECV_TIMER

            #lancaigang250619:USBIf connection is normal, clear
            #self.G_PauseToLCDString=""
            self.G_AMS1ErrorRestartCount=0






            # #lancaigang240427：AMSUnexpected restart - must log this event
            # if self.G_AMS1ErrorRestartFlag == True:
            #     self.G_PhrozenFluiddRespondInfo("AMS1Error or restart;self.G_AMSErrorRestartCount=%d" % self.G_AMSErrorRestartCount)
            #     self.G_PhrozenFluiddRespondInfo("+AMSReboot:%d" % self.G_AMSErrorRestartCount)
            #     self.G_AMS1ErrorRestartFlag = False
                
            #     try:
            #         self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1")
            #         self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
            #         #Serial port1Opened successfully
            #         if self.G_SerialPort1Obj.is_open:
            #             self.G_SerialPort1OpenFlag = True
            #             self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1Success")
            #             #lancaigang231213Open serial port1
            #             self.G_SerialPort1Obj.flushInput()  # clean serial write cache
            #             self.G_SerialPort1Obj.flush()
            #             self.G_PhrozenFluiddRespondInfo("Serial port1Clear")
            #             self.G_PhrozenFluiddRespondInfo("Re-register serial port1Callback function")
            #             self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
            #     except:
            #         self.G_PhrozenFluiddRespondInfo("Failed to opentty1Port - please checkUSBPort or restart attempt")

            #     return eventtime + AMS_SERIALPORT_RECV_TIMER



            # #lancaigang240410：
            # if self.G_CancelFlag==True:
            #     #self.G_PhrozenFluiddRespondInfo("Print cancelled")
            #     return eventtime + AMS_SERIALPORT_RECV_TIMER



            #lancaigang231103:tty1Serial port has data
            if self.G_SerialPort1Obj.inWaiting() > 0:
                self.Device_ReportModeIfChanged()

                Lo_SerialRxLen=self.G_SerialPort1Obj.inWaiting()
                Lo_SerialRxBytes=self.G_SerialPort1Obj.read(Lo_SerialRxLen)
                #self.G_PhrozenFluiddRespondInfo("Lo_SerialRxBytes[1]-16Hex bytes0x%2x" % Lo_SerialRxBytes[1])
                #self.G_PhrozenFluiddRespondInfo("Lo_SerialRxBytes[1]-ASCIICode character%c" % Lo_SerialRxBytes[1])



                #lancaigang240705ExistsAMSMulti-color
                self.G_AMSDevice1IfNormal=True


                try:
                    #lancaigang250411：AMSStatus report
                    #if "R" in self.G_SerialRxASCIIStr:
                    if Lo_SerialRxBytes[0]==0x52 and Lo_SerialRxLen==16:

                        #self.G_PhrozenFluiddRespondInfo("%s" % SerialRxASCIIStr)
                        Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                        Lo_AMSDeviceStateInfo.whole[:] = Lo_SerialRxBytes
                        #pythonEmpty dictionary
                        Lo_AMSDetailState = {}
                        self.G_AMS1DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                        self.G_AMS1DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                        self.G_AMS1DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                        self.G_AMS1DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor reports empty(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_empty)
                        self.G_AMS1DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor reports full(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                        self.G_AMS1DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor filament status(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_exist)
                        self.G_AMS1DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                        self.G_AMS1DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                        self.G_AMS1DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Entry position sensor status(bit bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                        self.G_AMS1DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                        # Only log when state changes
                        Lo_StateStr = json.dumps(Lo_AMSDetailState)
                        if Lo_StateStr != self.G_LastP114State:
                            self.G_LastP114State = Lo_StateStr
                            self.G_PhrozenFluiddRespondInfo(Lo_StateStr)
                        self.G_PhrozenFluiddRespondInfo("+P114:1")
                        self.G_P114RunFlag=0

                    else:
                        self.G_PhrozenFluiddRespondInfo("AMSFirmware version")
                        #lancaigang20231013ReadttyUSB0Convert serial byte stream toASCII
                        #lancaigang240530：16Convert hex bytes toASCIICode character
                        self.G_SerialRxASCIIStr = Lo_SerialRxBytes.decode("ascii")
                        self.G_PhrozenFluiddRespondInfo("ASCIICode stringself.G_SerialRxASCIIStr=%s" % self.G_SerialRxASCIIStr)


                        #lancaigang250411：AMSFirmware version

                        # // AMSMainboard2Firmware-1 1
                        if "V-H18-I18-F" in self.G_SerialRxASCIIStr:
                            self.G_PhrozenFluiddRespondInfo("AMSSegment display dryer step1Board firmware version")
                            #=====DriveCodeFile.dat
                            # 1 , 18 , 24053 , 18 , 0# // AMSMainboard1Firmware-18
                            # 2 , 18 , 24053 , 18 , 0# // AMSMainboard2Firmware-18
                            # 3 , 18 , 24053 , 18 , 0# // AMSMainboard3Firmware-18
                            # 4 , 18 , 24053 , 18 , 0# // AMSMainboard4Firmware-18
                            # 5 , 5 , 24046 , 5 , 0# // OTASubroutine-AMSSerial port firmware upgrade utility-5 5
                            # 6 , 0 , 0 , 0 , 0# // Buffer board firmware-6 6 Retain
                            # 7 , 7 , 24051 , 7 , 0# // 16-colorHUBBoard firmware-7 7
                            # 8 , 0 , 0 , 0 , 0
                            # 9 , 0 , 0 , 0 , 0
                            # 10 , 10 , 24054 , 10 , 0# // OTASubroutine-TJC serial touchscreen background service-10
                            # 11 , 11 , 24047 , 11 , 0# // TJC serial touchscreen foregroundHMIFirmware-11
                            # 12 , 0 , 0 , 0 , 0
                            # 13 , 0 , 0 , 0 , 0
                            # 14 , 0 , 0 , 0 , 0
                            # 15 , 15 , 25042 , 15 , 0
                            # 16 , 16 , 25042 , 16 , 0
                            # 17 , ? , 25042 , ? , 0
                            # 18 , ? , 25042 , ? , 0
                            # 19 , ? , 25042 , ? , 0
                            # 20 , ? , 25042 , ? , 0
                            # Theme:c0f535790a90/GetZbGwInfo_Respon
                            # {
                            #     "Data_ID": 95,
                            #     "Data": {
                            #         "GwId": "c0f535790a90",
                            #         "HomeId": "",
                            #         "GWSN": "0000000000000000000",
                            #         "AccountId": "",
                            #         "GwMac": "c0f535790a90",
                            #         "GwIP": "192.168.3.53",
                            #         "GwName": "Name-c0f535790a90",
                            #         "ProductId": "ARCO",
                            #         "MainImage": 15,
                            #         "MainHWVersion": 15,
                            #         "MainFWVersion": 24064,
                            #         "Gw_Ram": 248584,
                            #         "Gw_Rom": 826536,
                            #         "JoinMode": 1,
                            #         "ESSID": "",
                            #         "MqttClientEMQfd": 31,
                            #         "MqttClientId": "c0f535790a90",
                            #         "MqttBrokerUserName": "",
                            #         "MqttBrokerPwd": "",
                            #         "DriveCodeList": [
                            #             {
                            #                 "DriveCode": 1,
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
                            #                 "DriveCode": 3,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
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
                            #                 "DriveCode": 5,
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
                            #                 "DriveCode": 7,
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
                            #                 "DriveCode": 9,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 10,
                            #                 "DriveImageType": 10,
                            #                 "DriveHwVersion": 10,
                            #                 "DriveFwVersion": 25033,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 11,
                            #                 "DriveImageType": 11,
                            #                 "DriveHwVersion": 11,
                            #                 "DriveFwVersion": 25022,
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
                            #                 "DriveCode": 13,
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
                            #                 "DriveCode": 15,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 16,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 17,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 18,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 19,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 20,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             }
                            #         ]
                            #     }
                            # }
                            #lancaigang250724Read system firmware imageidDifferentiate by product, mainboard, and firmware version
                            #lancaigang250724:Read firmware imageid
                            self.Cmds_GetImageId()
                            if self.G_ImageId==16:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageId==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                            elif self.G_ImageId==31:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageId==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                            elif self.G_ImageId==-1:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageId==-1Default:ARCO300-MKS-RK3328-STM32F407VET6-I16")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                            else:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageIdCannot read - defaulting to:ARCO300-MKS-RK3328-STM32F407VET6-I16")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')

                            self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
                            Lo_AllLine=""
                            #data = [{"DriveCode":16,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":15,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":14,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":13,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":12,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":11,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":10,"DriveImageType":10,"DriveHwVersion":10,"DriveFwVersion":24045,"DriveId":0},{"DriveCode":9,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":8,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":7,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":6,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":5,"DriveImageType":5,"DriveHwVersion":5,"DriveFwVersion":24046,"DriveId":0},{"DriveCode":4,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":3,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":2,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":1,"DriveImageType":1,"DriveHwVersion":1,"DriveFwVersion":24042,"DriveId":0}]
                            #f = open(filename, 'a')
                            #json.dump(data, f)  #Object serial number as byte stream
                            #f.close()
                            with open(filename,'r') as file:
                                #for line in file:
                                # # realine() Read the entire line including "\n" Character
                                # self.G_PhrozenFluiddRespondInfo(file.readline().strip())
                                # #time.sleep(1)
                                Lo_FileDataList=file.readlines()
                                for line in Lo_FileDataList:
                                    #split = [i[:-1].split(',') for i in file.readlines()]
                                    #self.G_PhrozenFluiddRespondInfo(type(split))
                                    #self.G_PhrozenFluiddRespondInfo(split[1])
                                    #self.G_PhrozenFluiddRespondInfo(split[2])
                                    #self.G_PhrozenFluiddRespondInfo(split[3])
                                    #line_strip=line.strip()
                                    #self.G_PhrozenFluiddRespondInfo(line)
                                    #self.G_PhrozenFluiddRespondInfo("line.count=%d" % line.count)
                                    split=line.split(',')
                                    #self.G_PhrozenFluiddRespondInfo(type(split))
                                    #self.G_PhrozenFluiddRespondInfo("".join(split))
                                    #self.G_PhrozenFluiddRespondInfo(split[0])
                                    # 1 , 18 , 24053 , 18 , 0
                                    split[0]=split[0].strip()#Driver number
                                    split[1]=split[1].strip()#Hardwareid
                                    split[2]=split[2].strip()#Firmware version
                                    split[3]=split[3].strip()#Firmware imageid
                                    split[4]=split[4].strip()#Online status
                                    #split[4]='0'#Online check - default to0
                                    #if "SN1" in self.G_SerialRxASCIIStr:
                                    if split[0] == "1":
                                        self.G_PhrozenFluiddRespondInfo("AMSSegment display dryer step1Board firmware version")
                                        self.G_PhrozenFluiddRespondInfo(split[0])
                                        self.G_PhrozenFluiddRespondInfo(split[1])
                                        self.G_PhrozenFluiddRespondInfo(split[2])
                                        self.G_PhrozenFluiddRespondInfo(split[3])
                                        self.G_PhrozenFluiddRespondInfo(split[4])
                                        #line=("%d,%d,%d," % (HW_VERSION,,))
                                        line_modify=split[0]+','+'18'+','+self.G_SerialRxASCIIStr[11:16]+','+'18'+','+'1'
                                        self.G_PhrozenFluiddRespondInfo(line_modify)
                                        Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    else:
                                        Lo_AllLine=Lo_AllLine+line
                                    # if "SN2" in self.G_SerialRxASCIIStr:
                                    #     if split[0] == "2":
                                    #         self.G_PhrozenFluiddRespondInfo(split[0])
                                    #         self.G_PhrozenFluiddRespondInfo(split[1])
                                    #         self.G_PhrozenFluiddRespondInfo(split[2])
                                    #         self.G_PhrozenFluiddRespondInfo(split[3])
                                    #         self.G_PhrozenFluiddRespondInfo(split[4])
                                    #         #line=("%d,%d,%d," % (HW_VERSION,,))
                                    #         line_modify=split[0]+','+'1'+','+self.G_SerialRxASCIIStr[9:14]+','+'1'+','+'1'
                                    #         self.G_PhrozenFluiddRespondInfo(line_modify)
                                    #         Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    #     else:
                                    #         Lo_AllLine=Lo_AllLine+line
                                    # if "SN3" in self.G_SerialRxASCIIStr:
                                    #     if split[0] == "3":
                                    #         self.G_PhrozenFluiddRespondInfo(split[0])
                                    #         self.G_PhrozenFluiddRespondInfo(split[1])
                                    #         self.G_PhrozenFluiddRespondInfo(split[2])
                                    #         self.G_PhrozenFluiddRespondInfo(split[3])
                                    #         self.G_PhrozenFluiddRespondInfo(split[4])
                                    #         #line=("%d,%d,%d," % (HW_VERSION,,))
                                    #         line_modify=split[0]+','+'1'+','+self.G_SerialRxASCIIStr[9:14]+','+'1'+','+'1'
                                    #         self.G_PhrozenFluiddRespondInfo(line_modify)
                                    #         Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    #     else:
                                    #         Lo_AllLine=Lo_AllLine+line
                                    # if "SN4" in self.G_SerialRxASCIIStr:
                                    #     if split[0] == "4":
                                    #         self.G_PhrozenFluiddRespondInfo(split[0])
                                    #         self.G_PhrozenFluiddRespondInfo(split[1])
                                    #         self.G_PhrozenFluiddRespondInfo(split[2])
                                    #         self.G_PhrozenFluiddRespondInfo(split[3])
                                    #         self.G_PhrozenFluiddRespondInfo(split[4])
                                    #         #line=("%d,%d,%d," % (HW_VERSION,,))
                                    #         line_modify=split[0]+','+'1'+','+self.G_SerialRxASCIIStr[9:14]+','+'1'+','+'1'
                                    #         self.G_PhrozenFluiddRespondInfo(line_modify)
                                    #         Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    #     else:
                                    #         Lo_AllLine=Lo_AllLine+line
                            #self.G_PhrozenFluiddRespondInfo(Lo_AllLine)
                            with open(filename,"w+") as file_w:
                                file_w.write(Lo_AllLine)


                        self.Device_TimmerUartRecvHandler(1,Lo_SerialRxBytes,self.G_SerialRxASCIIStr)

                except:
                    self.G_PhrozenFluiddRespondInfo("Serial data malformed - cannot parseAMSState")


            return eventtime + AMS_SERIALPORT_RECV_TIMER

        except Exception as e:
            self.G_PhrozenFluiddRespondInfo("Serial port1Read error,AMS1Error or restart detected - please checkAMS1Check if normal")
            self.Device_ReportModeIfChanged()
            #lancaigang0427IfAMSUnexpected restart detected - log the event and send a command after successful restart tostm32Entering slow refill phase
            #lancaigang240427：AMSUnexpected restart - must log this event
            self.G_AMS1ErrorRestartFlag = True
            self.G_AMS1ErrorRestartCount=self.G_AMS1ErrorRestartCount+1

            #lancaigang241011Serial port error - data transmission not allowed
            self.G_SerialPort1OpenFlag=False
            
            #lancaigang240521On resume, if detectedAMSUnexpected restart - treat as hot-plug eventAMSExecute the full unload and filament change sequence
            self.G_ResumeCheckAMS1ErrorRestartFlag = True

            
            return eventtime + AMS_SERIALPORT_RECV_TIMER


    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #100ms
    def Device_TimmerUart2Recv(self, eventtime):
        try:
            #tty2Connection failed
            if self.G_SerialPort2OpenFlag==False:
                self.G_ASM1DisconnectErrorCount=0
                #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerUart2Recv]Serial port2Connection error - permanently exit the callback")
                #self.G_PhrozenFluiddRespondInfo("self.G_AMS2ErrorRestartCount=%d" % self.G_AMS2ErrorRestartCount)

                self.G_AMS2ErrorRestartCount=self.G_AMS2ErrorRestartCount+1

                try:
                    if self.G_SerialPort2Obj is not None:
                        if self.G_SerialPort2Obj.is_open:
                            #tty2Close
                            self.G_SerialPort2Obj.close()
                            self.G_PhrozenFluiddRespondInfo("Close serial port2Success")
                            self.G_PhrozenFluiddRespondInfo("AMS2Connection failed")
                            self.G_PhrozenFluiddRespondInfo("Cache the pause command+PAUSE:g")
                except:
                    self.G_PhrozenFluiddRespondInfo("Close serial port2Error")

                #lancaigang241108:Delay a few seconds before pausing to preventAMSRestart takes some time
                if self.G_AMS2ErrorRestartCount>=5:
                    #self.G_PhrozenFluiddRespondInfo("if self.G_AMS2ErrorRestartCount>=5:")

                    self.G_AMS2ErrorRestartCount=0
                    #lancaigang250619:IfUSBOnly report error when the color-change itself fails
                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    

                    # if self.G_KlipperIfPaused==False:
                    #     self.G_KlipperIfPaused = True
                    #     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #     if self.G_CancelFlag==False:
                    #         # self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #         # self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #         self.G_PhrozenFluiddRespondInfo("AMS2Connection error - pausing")

                    #         #lancaigang250604:
                    #         if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#M0
                    #             self.G_PhrozenFluiddRespondInfo("Unknown mode - no pause needed")
                    #         else:
                    #             if self.STM32ReprotPauseFlag==0:
                    #                 self.G_PauseTriggerWhileChangeChannelFlag=True
                    #                 if self.PG102Flag==True:
                    #                     self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                    #                     self.PG102DelayPauseFlag=True
                    #                     #self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #                     self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #                 else:
                    #                     self.G_PhrozenFluiddRespondInfo("Not purging - can pause immediately")
                    #                     self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #                     self.G_KlipperIfPaused = True
                    #                     #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    #                     self.STM32ReprotPauseFlag=1
                    #                     #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                    #                     self.G_ChangeChannelFirstFilaFlag=True
                    #                     self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #                     self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    #             else:
                    #                 self.G_PauseTriggerWhileChangeChannelFlag=True
                    #                 self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

                    #         #     self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #         #lancaigang20231013Disconnect
                    #         self.Device_DisconnectAMSDevice()

                    # #if self.G_KlipperIfPaused==True:
                    # else:
                    #     self.G_PhrozenFluiddRespondInfo("USBError - already in paused state")
                    #     self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


                    #lancaigang240524Permanently exit the callback
                    return self.G_PhrozenReactor.NEVER

                return eventtime + AMS_SERIALPORT_RECV_TIMER

            #lancaigang250619:USBIf connection is normal, clear
            #self.G_PauseToLCDString=""
            self.G_AMS2ErrorRestartCount=0


            #lancaigang241128：
            if self.G_CancelFlag==True:
                #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]Print cancelled")
                return eventtime + AMS_SERIALPORT_RECV_TIMER
        


            # #lancaigang240427：AMSUnexpected restart - must log this event
            # if self.G_AMS1ErrorRestartFlag == True:
            #     self.G_PhrozenFluiddRespondInfo("AMS1Error or restart;self.G_AMSErrorRestartCount=%d" % self.G_AMSErrorRestartCount)
            #     self.G_PhrozenFluiddRespondInfo("+AMSReboot:%d" % self.G_AMSErrorRestartCount)
            #     self.G_AMS1ErrorRestartFlag = False
                
            #     try:
            #         self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1")
            #         self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
            #         #Serial port1Opened successfully
            #         if self.G_SerialPort1Obj.is_open:
            #             self.G_SerialPort1OpenFlag = True
            #             self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1Success")
            #             #lancaigang231213Open serial port1
            #             self.G_SerialPort1Obj.flushInput()  # clean serial write cache
            #             self.G_SerialPort1Obj.flush()
            #             self.G_PhrozenFluiddRespondInfo("Serial port1Clear")
            #             self.G_PhrozenFluiddRespondInfo("Re-register serial port1Callback function")
            #             self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
            #     except:
            #         self.G_PhrozenFluiddRespondInfo("Failed to opentty1Port - please checkUSBPort or restart attempt")

            #     return eventtime + AMS_SERIALPORT_RECV_TIMER



            # #lancaigang240410：
            # if self.G_CancelFlag==True:
            #     #self.G_PhrozenFluiddRespondInfo("Print cancelled")
            #     return eventtime + AMS_SERIALPORT_RECV_TIMER



            #lancaigang231103:tty2Serial port has data
            if self.G_SerialPort2Obj.inWaiting() > 0:
                self.Device_ReportModeIfChanged()

                Lo_SerialRxLen=self.G_SerialPort2Obj.inWaiting()
                Lo_SerialRxBytes=self.G_SerialPort2Obj.read(Lo_SerialRxLen)
                #self.G_PhrozenFluiddRespondInfo("Lo_SerialRxBytes[1]-16Hex bytes0x%2x" % Lo_SerialRxBytes[1])
                #self.G_PhrozenFluiddRespondInfo("Lo_SerialRxBytes[1]-ASCIICode character%c" % Lo_SerialRxBytes[1])


                #lancaigang20231013ReadttyUSB0Convert serial byte stream toASCII
                #lancaigang240530：16Convert hex bytes toASCIICode character
                self.G_SerialRxASCIIStr = Lo_SerialRxBytes.decode("ascii")
                #self.G_PhrozenFluiddRespondInfo("ASCIICode stringself.G_SerialRxASCIIStr=%s" % self.G_SerialRxASCIIStr)



                #lancaigang240705ExistsAMSMulti-color
                self.G_AMSDevice2IfNormal=True


                try:
                    # #if "R" in self.G_SerialRxASCIIStr:
                    # if Lo_SerialRxBytes[0]==0x52:
                    #     self.G_PhrozenFluiddRespondInfo("AMS#2Board async return")

                    #     #self.G_PhrozenFluiddRespondInfo("%s" % SerialRxASCIIStr)
                    #     Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                    #     Lo_AMSDeviceStateInfo.whole[:] = Lo_SerialRxBytes
                    #     #pythonEmpty dictionary
                    #     Lo_AMSDetailState = {}
                    #     self.G_AMS2DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                    #     self.G_AMS2DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                    #     self.G_AMS2DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                    #     self.G_AMS2DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                    #     #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor reports empty(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_empty)
                    #     self.G_AMS2DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                    #     #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor reports full(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                    #     self.G_AMS2DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                    #     #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor filament status(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_exist)
                    #     self.G_AMS2DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                    #     self.G_AMS2DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                    #     self.G_AMS2DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                    #     #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Entry position sensor status(bit bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                    #     self.G_AMS2DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                    #     #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Park position sensor status(bit bit)==%d" % Lo_AMSDeviceStateInfo.field.park_state)
                        
                    #     # Response datajsonConvert
                    #     self.G_PhrozenFluiddRespondInfo(json.dumps(Lo_AMSDetailState))


                    #if "R" in self.G_SerialRxASCIIStr:
                    if Lo_SerialRxBytes[0]==0x52 and Lo_SerialRxLen==16:
                        self.G_PhrozenFluiddRespondInfo("AMS#2Board async return")

                        #self.G_PhrozenFluiddRespondInfo("%s" % SerialRxASCIIStr)
                        Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                        Lo_AMSDeviceStateInfo.whole[:] = Lo_SerialRxBytes
                        #pythonEmpty dictionary
                        Lo_AMSDetailState = {}
                        self.G_AMS1DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                        self.G_AMS1DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                        self.G_AMS1DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                        self.G_AMS1DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor reports empty(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_empty)
                        self.G_AMS1DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor reports full(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                        self.G_AMS1DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Buffer sensor filament status(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_exist)
                        self.G_AMS1DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                        self.G_AMS1DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                        self.G_AMS1DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP114]Entry position sensor status(bit bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                        self.G_AMS1DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                        # Only log when state changes
                        Lo_StateStr = json.dumps(Lo_AMSDetailState)
                        if Lo_StateStr != self.G_LastP114State:
                            self.G_LastP114State = Lo_StateStr
                            self.G_PhrozenFluiddRespondInfo(Lo_StateStr)
                        self.G_PhrozenFluiddRespondInfo("+P114:1")
                        self.G_P114RunFlag=0

                    else:
                        self.G_PhrozenFluiddRespondInfo("AMSFirmware version")
                        #lancaigang20231013ReadttyUSB0Convert serial byte stream toASCII
                        #lancaigang240530：16Convert hex bytes toASCIICode character
                        self.G_SerialRxASCIIStr = Lo_SerialRxBytes.decode("ascii")
                        self.G_PhrozenFluiddRespondInfo("ASCIICode stringself.G_SerialRxASCIIStr=%s" % self.G_SerialRxASCIIStr)


                        #lancaigang250411：AMSFirmware version

                        # // AMSMainboard2Firmware-1 1
                        if "V-H18-I18-F" in self.G_SerialRxASCIIStr:
                            self.G_PhrozenFluiddRespondInfo("AMSSegment display dryer step2Board firmware version")
                            #=====DriveCodeFile.dat
                            # 1 , 18 , 24053 , 18 , 0# // AMSMainboard1Firmware-18
                            # 2 , 18 , 24053 , 18 , 0# // AMSMainboard2Firmware-18
                            # 3 , 18 , 24053 , 18 , 0# // AMSMainboard3Firmware-18
                            # 4 , 18 , 24053 , 18 , 0# // AMSMainboard4Firmware-18
                            # 5 , 5 , 24046 , 5 , 0# // OTASubroutine-AMSSerial port firmware upgrade utility-5 5
                            # 6 , 0 , 0 , 0 , 0# // Buffer board firmware-6 6 Retain
                            # 7 , 7 , 24051 , 7 , 0# // 16-colorHUBBoard firmware-7 7
                            # 8 , 0 , 0 , 0 , 0
                            # 9 , 0 , 0 , 0 , 0
                            # 10 , 10 , 24054 , 10 , 0# // OTASubroutine-TJC serial touchscreen background service-10
                            # 11 , 11 , 24047 , 11 , 0# // TJC serial touchscreen foregroundHMIFirmware-11
                            # 12 , 0 , 0 , 0 , 0
                            # 13 , 0 , 0 , 0 , 0
                            # 14 , 0 , 0 , 0 , 0
                            # 15 , 15 , 25042 , 15 , 0
                            # 16 , 16 , 25042 , 16 , 0
                            # 17 , ? , 25042 , ? , 0
                            # 18 , ? , 25042 , ? , 0
                            # 19 , ? , 25042 , ? , 0
                            # 20 , ? , 25042 , ? , 0
                            # Theme:c0f535790a90/GetZbGwInfo_Respon
                            # {
                            #     "Data_ID": 95,
                            #     "Data": {
                            #         "GwId": "c0f535790a90",
                            #         "HomeId": "",
                            #         "GWSN": "0000000000000000000",
                            #         "AccountId": "",
                            #         "GwMac": "c0f535790a90",
                            #         "GwIP": "192.168.3.53",
                            #         "GwName": "Name-c0f535790a90",
                            #         "ProductId": "ARCO",
                            #         "MainImage": 15,
                            #         "MainHWVersion": 15,
                            #         "MainFWVersion": 24064,
                            #         "Gw_Ram": 248584,
                            #         "Gw_Rom": 826536,
                            #         "JoinMode": 1,
                            #         "ESSID": "",
                            #         "MqttClientEMQfd": 31,
                            #         "MqttClientId": "c0f535790a90",
                            #         "MqttBrokerUserName": "",
                            #         "MqttBrokerPwd": "",
                            #         "DriveCodeList": [
                            #             {
                            #                 "DriveCode": 1,
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
                            #                 "DriveCode": 3,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
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
                            #                 "DriveCode": 5,
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
                            #                 "DriveCode": 7,
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
                            #                 "DriveCode": 9,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 10,
                            #                 "DriveImageType": 10,
                            #                 "DriveHwVersion": 10,
                            #                 "DriveFwVersion": 25033,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 11,
                            #                 "DriveImageType": 11,
                            #                 "DriveHwVersion": 11,
                            #                 "DriveFwVersion": 25022,
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
                            #                 "DriveCode": 13,
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
                            #                 "DriveCode": 15,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 16,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 17,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 18,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 19,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             },
                            #             {
                            #                 "DriveCode": 20,
                            #                 "DriveImageType": 0,
                            #                 "DriveHwVersion": 0,
                            #                 "DriveFwVersion": 0,
                            #                 "DriveId": 0
                            #             }
                            #         ]
                            #     }
                            # }
                            #lancaigang250724Read system firmware imageidDifferentiate by product, mainboard, and firmware version
                            #lancaigang250724:Read firmware imageid
                            self.Cmds_GetImageId()
                            if self.G_ImageId==16:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageId==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                            elif self.G_ImageId==31:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageId==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                            elif self.G_ImageId==-1:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageId==-1Default:ARCO300-MKS-RK3328-STM32F407VET6-I16")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                            else:
                                self.G_PhrozenFluiddRespondInfo("Firmware imageIdCannot read - defaulting to:ARCO300-MKS-RK3328-STM32F407VET6-I16")
                                #lancaigang240530Write version todatFileDriveCodeJson.dat
                                filename=os.path.join(os.path.dirname(__file__), 'DriveCodeFile.dat')
                                
                            self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
                            Lo_AllLine=""
                            #data = [{"DriveCode":16,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":15,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":14,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":13,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":12,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":11,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":10,"DriveImageType":10,"DriveHwVersion":10,"DriveFwVersion":24045,"DriveId":0},{"DriveCode":9,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":8,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":7,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":6,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":5,"DriveImageType":5,"DriveHwVersion":5,"DriveFwVersion":24046,"DriveId":0},{"DriveCode":4,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":3,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":2,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":1,"DriveImageType":1,"DriveHwVersion":1,"DriveFwVersion":24042,"DriveId":0}]
                            #f = open(filename, 'a')
                            #json.dump(data, f)  #Object serial number as byte stream
                            #f.close()
                            with open(filename,'r') as file:
                                #for line in file:
                                # # realine() Read the entire line including "\n" Character
                                # self.G_PhrozenFluiddRespondInfo(file.readline().strip())
                                # #time.sleep(1)
                                Lo_FileDataList=file.readlines()
                                for line in Lo_FileDataList:
                                    #split = [i[:-1].split(',') for i in file.readlines()]
                                    #self.G_PhrozenFluiddRespondInfo(type(split))
                                    #self.G_PhrozenFluiddRespondInfo(split[1])
                                    #self.G_PhrozenFluiddRespondInfo(split[2])
                                    #self.G_PhrozenFluiddRespondInfo(split[3])
                                    #line_strip=line.strip()
                                    #self.G_PhrozenFluiddRespondInfo(line)
                                    #self.G_PhrozenFluiddRespondInfo("line.count=%d" % line.count)
                                    split=line.split(',')
                                    #self.G_PhrozenFluiddRespondInfo(type(split))
                                    #self.G_PhrozenFluiddRespondInfo("".join(split))
                                    #self.G_PhrozenFluiddRespondInfo(split[0])
                                    # 2 , 18 , 24053 , 18 , 0
                                    split[0]=split[0].strip()#Driver number
                                    split[1]=split[1].strip()#Hardwareid
                                    split[2]=split[2].strip()#Firmware version
                                    split[3]=split[3].strip()#Firmware imageid
                                    split[4]=split[4].strip()#Online status
                                    #split[4]='0'#Online check - default to0
                                    # #if "SN1" in self.G_SerialRxASCIIStr:
                                    # if split[0] == "1":
                                    #     self.G_PhrozenFluiddRespondInfo(split[0])
                                    #     self.G_PhrozenFluiddRespondInfo(split[1])
                                    #     self.G_PhrozenFluiddRespondInfo(split[2])
                                    #     self.G_PhrozenFluiddRespondInfo(split[3])
                                    #     self.G_PhrozenFluiddRespondInfo(split[4])
                                    #     #line=("%d,%d,%d," % (HW_VERSION,,))
                                    #     line_modify=split[0]+','+'1'+','+self.G_SerialRxASCIIStr[9:14]+','+'1'+','+'1'
                                    #     self.G_PhrozenFluiddRespondInfo(line_modify)
                                    #     Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    # else:
                                    #     Lo_AllLine=Lo_AllLine+line

                                    #if "SN2" in self.G_SerialRxASCIIStr:
                                    if split[0] == "2":
                                        self.G_PhrozenFluiddRespondInfo("AMS#2Board firmware version")
                                        self.G_PhrozenFluiddRespondInfo(split[0])
                                        self.G_PhrozenFluiddRespondInfo(split[1])
                                        self.G_PhrozenFluiddRespondInfo(split[2])
                                        self.G_PhrozenFluiddRespondInfo(split[3])
                                        self.G_PhrozenFluiddRespondInfo(split[4])
                                        #line=("%d,%d,%d," % (HW_VERSION,,))
                                        line_modify=split[0]+','+'18'+','+self.G_SerialRxASCIIStr[11:16]+','+'18'+','+'1'
                                        self.G_PhrozenFluiddRespondInfo(line_modify)
                                        Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    else:
                                        Lo_AllLine=Lo_AllLine+line

                                    # if "SN3" in self.G_SerialRxASCIIStr:
                                    #     if split[0] == "3":
                                    #         self.G_PhrozenFluiddRespondInfo(split[0])
                                    #         self.G_PhrozenFluiddRespondInfo(split[1])
                                    #         self.G_PhrozenFluiddRespondInfo(split[2])
                                    #         self.G_PhrozenFluiddRespondInfo(split[3])
                                    #         self.G_PhrozenFluiddRespondInfo(split[4])
                                    #         #line=("%d,%d,%d," % (HW_VERSION,,))
                                    #         line_modify=split[0]+','+'1'+','+self.G_SerialRxASCIIStr[9:14]+','+'1'+','+'1'
                                    #         self.G_PhrozenFluiddRespondInfo(line_modify)
                                    #         Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    #     else:
                                    #         Lo_AllLine=Lo_AllLine+line
                                    # if "SN4" in self.G_SerialRxASCIIStr:
                                    #     if split[0] == "4":
                                    #         self.G_PhrozenFluiddRespondInfo(split[0])
                                    #         self.G_PhrozenFluiddRespondInfo(split[1])
                                    #         self.G_PhrozenFluiddRespondInfo(split[2])
                                    #         self.G_PhrozenFluiddRespondInfo(split[3])
                                    #         self.G_PhrozenFluiddRespondInfo(split[4])
                                    #         #line=("%d,%d,%d," % (HW_VERSION,,))
                                    #         line_modify=split[0]+','+'1'+','+self.G_SerialRxASCIIStr[9:14]+','+'1'+','+'1'
                                    #         self.G_PhrozenFluiddRespondInfo(line_modify)
                                    #         Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                                    #     else:
                                    #         Lo_AllLine=Lo_AllLine+line
                            #self.G_PhrozenFluiddRespondInfo(Lo_AllLine)
                            with open(filename,"w+") as file_w:
                                file_w.write(Lo_AllLine)


                        self.Device_TimmerUartRecvHandler(2,Lo_SerialRxBytes,self.G_SerialRxASCIIStr)

                except:
                    self.G_PhrozenFluiddRespondInfo("Serial data malformed - cannot parseAMSState")

            return eventtime + AMS_SERIALPORT_RECV_TIMER

        except Exception as e:
            self.G_PhrozenFluiddRespondInfo("Serial port2Read error,AMS2Error or restart detected - please checkAMS2Check if normal")
            self.Device_ReportModeIfChanged()
            #lancaigang0427IfAMSUnexpected restart detected - log the event and send a command after successful restart tostm32Entering slow refill phase
            #lancaigang240427：AMSUnexpected restart - must log this event
            self.G_AMS2ErrorRestartFlag = True
            self.G_AMS2ErrorRestartCount=self.G_AMS2ErrorRestartCount+1

            #lancaigang241011Serial port2Error - data transmission not allowed
            self.G_SerialPort2OpenFlag=False
            
            #lancaigang240521On resume, if detectedAMSUnexpected restart - treat as hot-plug eventAMSExecute the full unload and filament change sequence
            self.G_ResumeCheckAMS2ErrorRestartFlag = True

            
            return eventtime + AMS_SERIALPORT_RECV_TIMER


    

