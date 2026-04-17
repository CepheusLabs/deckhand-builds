import os
import logging
import json
import time
from .base import *


class SystemMixin:
    """Mixin for system diagnostics, print lifecycle, and state persistence."""

    def Cmds_PhrozenVersion(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenVersion]command='%s'" % (gcmd.get_commandline(),))


        logging.info("current mode")
        self.Device_ReportModeIfChanged()



        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))
        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            #lancaigang240524：readAMSmainboard version、16HUBmainboard version
            self.Cmds_AMSSerial1Send("AT+SB=0")
            logging.info("serial port1send command: AT+SB=0；getAMSmainboard version、16colorHUBmainboard version")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AT+SB=0")
            logging.info("serial port2send command: AT+SB=0；getAMSmainboard version、16colorHUBmainboard version")

        #lancaigang240529：phrozeninsert piece/piece/piece/piece/piece version
        self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))


        #lancaigang240530：versionwrite todattext piece/piece/piece/piece/piece；DriveCodeJson.dat
               #lancaigang250724：readsystem/relation systemmirror likeid，areadivide differentproduceproduct different mainboard different firmware
        #lancaigang250724:readmirror likeid
        self.Cmds_GetImageId()
        if self.G_ImageId==16:
            self.G_PhrozenFluiddRespondInfo("Image ID==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
            filename='/home/mks/hdlDat/DriveCodeFile.dat'
            self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
        elif self.G_ImageId==31:
            self.G_PhrozenFluiddRespondInfo("Image ID==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
            filename='/home/prz/hdlDat/DriveCodeFile.dat'
            self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
        elif self.G_ImageId==-1:
            self.G_PhrozenFluiddRespondInfo("Image ID==-1，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
            filename='/home/mks/hdlDat/DriveCodeFile.dat'
            self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)
        else:
            self.G_PhrozenFluiddRespondInfo("Image IDread not to，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
            filename='/home/mks/hdlDat/DriveCodeFile.dat'
            self.G_PhrozenFluiddRespondInfo("filename=%s" % filename)

        Lo_AllLine=""
        with open(filename,'r') as file:
            Lo_FileDataList=file.readlines()
            for line in Lo_FileDataList:
                split=line.split(',')
                split[0]=split[0].strip()#drive move/actionnumber
                split[1]=split[1].strip()#hard piece/piece/piece/piece/pieceid
                split[2]=split[2].strip()#firmware version
                split[3]=split[3].strip()#mirror likeid
                split[4]=split[4].strip()#isnot at filament

                #lancaigang240617：firstmirror likeid=1and7 at filament stateset position/bit0filament absent，ifAMShasresponse should，againset position/bit1at filament

                if split[0]=="16":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'16'+','+str(FW_VERSION)+','+'16'+','+'1'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="1":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'1'+','+"00000"+','+'1'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="2":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'1'+','+"00000"+','+'1'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="3":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'1'+','+"00000"+','+'1'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="4":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'1'+','+"00000"+','+'1'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="5":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+split[1]+','+split[2]+','+split[3]+','+'1'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="10":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+split[1]+','+split[2]+','+split[3]+','+'1'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="7":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'7'+','+"00000"+','+'7'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A

                elif split[0]=="17":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="18":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="19":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="20":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A


                else:
                    Lo_AllLine=Lo_AllLine+line
        with open(filename,"w+") as file_w:
	        file_w.write(Lo_AllLine)






    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #functiondescription：# PRZ_ADC query toolhead filament sensorvalue(use intesting)
    ####################################
    #lancaigang251020：
    def Cmds_PhrozenAdc(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenAdc]command=PRZ_ADC")

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        # read toolhead most after ADCvalue
        value, timestamp = self.G_ToolheadAdc.get_last_value()

        self.G_PhrozenFluiddRespondInfo("PRZ_ADC:readADCvalue %.6f (timestamp %.3f)  fila_exist:%r" % (value, timestamp, self.G_ToolheadIfHaveFilaFlag))
        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_AMS1ErrorRestartCount=%d" % (self.G_AMS1ErrorRestartCount))

        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        self.G_PhrozenFluiddRespondInfo("self.G_P0M3Flag=%d" % (self.G_P0M3Flag))
        self.G_PhrozenFluiddRespondInfo("self.G_KlipperIfPaused=%d" % (self.G_KlipperIfPaused))
        logging.info("self.G_CancelFlag=%d" % (self.G_CancelFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_IfChangeFilaOngoing=%d" % (self.G_IfChangeFilaOngoing))
        self.G_PhrozenFluiddRespondInfo("self.G_SerialPort1OpenFlag=%d" % (self.G_SerialPort1OpenFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_P0M2MAStartPrintFlag=%d" % (self.G_P0M2MAStartPrintFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_M2MAModeResumeFlag=%d" % (self.G_M2MAModeResumeFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_KlipperPrintStatus=%d" % (self.G_KlipperPrintStatus))
        self.G_PhrozenFluiddRespondInfo("self.G_SerialPort1OpenFlag=%d" % (self.G_SerialPort1OpenFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_SerialPort2OpenFlag=%d" % (self.G_SerialPort2OpenFlag))
        self.G_PhrozenFluiddRespondInfo("self.ManualCmdFlag=%d" % (self.ManualCmdFlag))
        self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=%d" % (self.STM32ReprotPauseFlag))
        self.G_PhrozenFluiddRespondInfo("self.PG102Flag=%d" % (self.PG102Flag))
        self.G_PhrozenFluiddRespondInfo("self.G_IfInFilaBlockFlag=%d" % (self.G_IfInFilaBlockFlag))
        self.G_PhrozenFluiddRespondInfo("self.PG102DelayPauseFlag=%d" % (self.PG102DelayPauseFlag))
        self.G_PhrozenFluiddRespondInfo("self.G_KlipperQuickPause=%d" % (self.G_KlipperQuickPause))
        self.G_PhrozenFluiddRespondInfo("self.G_PauseToLCDString=%s" % (self.G_PauseToLCDString))






        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)

        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")


        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            #lancaigang240524：readAMSmainboard version、16HUBmainboard version
            self.Cmds_AMSSerial1Send("AT+SB=0")
            logging.info("serial port1send command: AT+SB=0；getAMSmainboard version、16colorHUBmainboard version")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            #lancaigang240524：readAMSmainboard version、16HUBmainboard version
            self.Cmds_AMSSerial2Send("AT+SB=0")
            logging.info("serial port2send command: AT+SB=0；getAMSmainboard version、16colorHUBmainboard version")


        #lancaigang240529：phrozeninsert piece/piece/piece/piece/piece version
        self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s-SN1" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))

        #PRZ_PwrDownResumePrint
        try:
            logging.info("try")
            #lancaigang240530：versionwrite todattext piece/piece/piece/piece/piece；DriveCodeJson.dat

            #lancaigang250724：readsystem/relation systemmirror likeid，areadivide differentproduceproduct different mainboard different firmware
            #lancaigang250724:readmirror likeid
            self.Cmds_GetImageId()
            if self.G_ImageId==16:
                self.G_PhrozenFluiddRespondInfo("Image ID==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
            elif self.G_ImageId==31:
                self.G_PhrozenFluiddRespondInfo("Image ID==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
                with open('/home/prz/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
            elif self.G_ImageId==-1:
                self.G_PhrozenFluiddRespondInfo("Image ID==-1，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
            else:
                self.G_PhrozenFluiddRespondInfo("Image IDread not to，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
        except:
            self.G_PhrozenFluiddRespondInfo("except")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenBM1(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenBM1]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))

        #lancaigang250327：perform enter multi-color filament change before，not allowAMSmulti-color pause
        self.ManualCmdFlag=True
        self.G_PhrozenFluiddRespondInfo("self.ManualCmdFlag=True")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenBM0(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenBM0]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))
        #lancaigang250327：perform enter multi-color filament change before，not allowAMSmulti-color pause
        self.ManualCmdFlag=True
        self.G_PhrozenFluiddRespondInfo("self.ManualCmdFlag=True")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #PRZ_PRINT_START
    def Cmds_PrzPrintStart(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)CmdsPrzPrintStart]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_HomingOverrideEnd(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_HomingOverrideEnd]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PrzPrintEnd(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PrzPrintEnd]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))

####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PrintMode(self,mode):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PrintMode]send command: self.G_AMSDeviceWorkMode=%d" % self.G_AMSDeviceWorkMode)
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PrintMode]send command: mode=%d" % mode)

        try:
            logging.info("try")
            Phrozen_Dev = {"mode": self.G_AMSDeviceWorkMode, "nc1": self.G_ChangeChannelTimeoutOldChan, "nc2": self.G_ChangeChannelTimeoutNewChan,"nc3":0,"nc4":0,"nc5":0,"nc6":0}

            #lancaigang250724：readsystem/relation systemmirror likeid，areadivide differentproduceproduct different mainboard different firmware
            #lancaigang250724:readmirror likeid
            self.Cmds_GetImageId()
            if self.G_ImageId==16:
                self.G_PhrozenFluiddRespondInfo("Image ID==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'w') as file:
                    json.dump(Phrozen_Dev, file)
                    self.G_PhrozenFluiddRespondInfo("Writing JSON config file")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
            elif self.G_ImageId==31:
                self.G_PhrozenFluiddRespondInfo("Image ID==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
                with open('/home/prz/hdlDat/Phrozen_Dev.json', 'w') as file:
                    json.dump(Phrozen_Dev, file)
                    self.G_PhrozenFluiddRespondInfo("Writing JSON config file")
                with open('/home/prz/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
            elif self.G_ImageId==-1:
                self.G_PhrozenFluiddRespondInfo("Image ID==-1，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'w') as file:
                    json.dump(Phrozen_Dev, file)
                    self.G_PhrozenFluiddRespondInfo("Writing JSON config file")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
            else:
                self.G_PhrozenFluiddRespondInfo("Image IDread not to，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'w') as file:
                    json.dump(Phrozen_Dev, file)
                    self.G_PhrozenFluiddRespondInfo("Writing JSON config file")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
        except:
            self.G_PhrozenFluiddRespondInfo("except")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #PRZ_RESTORE
    def Cmds_PrzATRestore(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PrzATRestore]")

        logging.info("current mode")
        self.Device_ReportModeIfChanged()




        #PRZ_PwrDownResumePrint
        try:
            logging.info("try")

            #lancaigang250724：readsystem/relation systemmirror likeid，areadivide differentproduceproduct different mainboard different firmware
            #lancaigang250724:readmirror likeid
            self.Cmds_GetImageId()
            if self.G_ImageId==16:
                self.G_PhrozenFluiddRespondInfo("Image ID==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_AMSDeviceWorkMode = json_data['mode']
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode=%d" % (self.G_AMSDeviceWorkMode))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_ChangeChannelTimeoutOldChan=json_data['nc1']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutOldChan=%d" % (self.G_ChangeChannelTimeoutOldChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_ChangeChannelTimeoutNewChan=json_data['nc2']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=%d" % (self.G_ChangeChannelTimeoutNewChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
            elif self.G_ImageId==31:
                self.G_PhrozenFluiddRespondInfo("Image ID==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
                with open('/home/prz/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_AMSDeviceWorkMode = json_data['mode']
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode=%d" % (self.G_AMSDeviceWorkMode))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_ChangeChannelTimeoutOldChan=json_data['nc1']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutOldChan=%d" % (self.G_ChangeChannelTimeoutOldChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_ChangeChannelTimeoutNewChan=json_data['nc2']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=%d" % (self.G_ChangeChannelTimeoutNewChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
            elif self.G_ImageId==-1:
                self.G_PhrozenFluiddRespondInfo("Image ID==-1，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_AMSDeviceWorkMode = json_data['mode']
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode=%d" % (self.G_AMSDeviceWorkMode))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_ChangeChannelTimeoutOldChan=json_data['nc1']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutOldChan=%d" % (self.G_ChangeChannelTimeoutOldChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_ChangeChannelTimeoutNewChan=json_data['nc2']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=%d" % (self.G_ChangeChannelTimeoutNewChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))
            else:
                self.G_PhrozenFluiddRespondInfo("Image IDread not to，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                with open('/home/mks/hdlDat/Phrozen_Dev.json', 'r', encoding='utf-8') as file:
                    FileRead = file.read()
                    self.G_PhrozenFluiddRespondInfo("Reading JSON config file")
                    # parseJSONdata
                    json_data = json.loads(FileRead)
                    self.G_PhrozenFluiddRespondInfo("json_data['mode']=%d" % (json_data['mode']))
                    self.G_AMSDeviceWorkMode = json_data['mode']
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode=%d" % (self.G_AMSDeviceWorkMode))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc1']=%d" % (json_data['nc1']))
                    self.G_ChangeChannelTimeoutOldChan=json_data['nc1']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutOldChan=%d" % (self.G_ChangeChannelTimeoutOldChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc2']=%d" % (json_data['nc2']))
                    self.G_ChangeChannelTimeoutNewChan=json_data['nc2']
                    self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=%d" % (self.G_ChangeChannelTimeoutNewChan))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc3']=%d" % (json_data['nc3']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc4']=%d" % (json_data['nc4']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc5']=%d" % (json_data['nc5']))
                    self.G_PhrozenFluiddRespondInfo("json_data['nc6']=%d" % (json_data['nc6']))




            try:
                logging.info("[(cmds.py)Cmds_PrzATRestore]re-initialize serial port1")
                self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
                #serial port opened successfully
                if self.G_SerialPort1Obj is not None:
                    if self.G_SerialPort1Obj.is_open:
                        self.G_SerialPort1OpenFlag = True
                        logging.info("re-initialize serial port1success")
                        #lancaigang231213：open serial port
                        self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                        self.G_SerialPort1Obj.flush()
                        logging.info("serial port1clear")
                        logging.info("re-register serial port1callback function")
                        self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
            except:
                logging.info("not yet canhit/open open/enabletty1port，please checkUSBport or restarttry")
                self.G_SerialPort1OpenFlag = False

            try:
                logging.info("[(cmds.py)Cmds_PrzATRestore]re-initialize serial port2")
                self.G_SerialPort2Obj = serial.Serial(self.G_Serialport2Define, SERIAL_PORT_BAUD, timeout=3)
                #serial port opened successfully
                if self.G_SerialPort2Obj is not None:
                    if self.G_SerialPort2Obj.is_open:
                        self.G_SerialPort2OpenFlag = True
                        self._tty2_open_failure_logged = False
                        logging.info("re-initialize serial port2success")
                        self.G_SerialPort2Obj.flushInput()  # clean serial write cache
                        self.G_SerialPort2Obj.flush()
                        logging.info("serial port2clear")
                        logging.info("re-register serial port2callback function")
                        self.G_SerialPort2RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart2Recv, self.G_PhrozenReactor.NOW)
            except:
                if not self._tty2_open_failure_logged:
                    self.G_PhrozenFluiddRespondInfo("Failed to open tty2 port - check USB connection or restart")
                    self._tty2_open_failure_logged = True
                else:
                    logging.debug("Failed to open tty2 port - check USB connection or restart")
                self.G_SerialPort2OpenFlag = False


            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()
            #lancaigang240416:
            if self.G_SerialPort1OpenFlag == True:
                logging.info("serial port1send command：AT+RESTORE")
                self.Cmds_AMSSerial1Send("AT+RESTORE")

            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                logging.info("serial port2send command：AT+RESTORE")
                self.Cmds_AMSSerial2Send("AT+RESTORE")


            self.G_ProzenToolhead.dwell(2)




            logging.info("current mode")
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("+Mode:0,unkown")



            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
                self.G_PhrozenFluiddRespondInfo("+Mode:1,MC")
                if self.G_SerialPort1OpenFlag == False and self.G_SerialPort2OpenFlag == False:
                    self.G_PhrozenFluiddRespondInfo("no method/way connectAMS，pause")
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
                        self.G_ChangeChannelFirstFilaFlag=True
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")


            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                self.G_PhrozenFluiddRespondInfo("+Mode:2,MA")
                self.G_P0M2MAStartPrintFlag=1
                if self.G_ToolheadIfHaveFilaFlag:
                    self.G_PhrozenFluiddRespondInfo("has filament，can continue print")
                    #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                    self.G_KlipperPrintStatus= 3
                    #lancaigang250522：
                    self.G_PhrozenFluiddRespondInfo("external macro-PG108")
                    #lancaigang251120：perform enter purge，add flag，preventPG108purge process in toolheadHall without filament pause，causes pause position at purge area，resume would crash into the purge bin;
                    self.G_PG108Ingoing=1
                    command_string = """
                        PG108
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PG108Ingoing=0
                    self.G_PhrozenFluiddRespondInfo("external macro-PG108；command_string='%s'" % command_string)

                    #lancaigang250607:
                    self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                    self.G_KlipperQuickPause = True
                else:
                    self.G_PhrozenFluiddRespondInfo("no filament，need pause wait")
                    #lancaigang240125：encapsulated function
                    self.Cmds_PhrozenKlipperResumeCommon()

                    #lancaigang250522：
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                    command_string = """
                        PG109
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up；command_string='%s'" % command_string)





                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")


                    self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))




            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                self.G_PhrozenFluiddRespondInfo("+Mode:3,RUNOUT")
                self.G_P0M3Flag = True

                if self.G_ToolheadIfHaveFilaFlag:
                    self.G_PhrozenFluiddRespondInfo("has filament，can continue print")
                    self.G_PhrozenFluiddRespondInfo("external macro-PG108")
                    #lancaigang251120：perform enter purge，add flag，preventPG108purge process in toolheadHall without filament pause，causes pause position at purge area，resume would crash into the purge bin;
                    self.G_PG108Ingoing=1
                    command_string = """
                        PG108
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PG108Ingoing=0
                    self.G_PhrozenFluiddRespondInfo("external macro-PG108；command_string='%s'" % command_string)

                    #lancaigang250607:
                    self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                else:
                    self.G_PhrozenFluiddRespondInfo("no filament，need pause wait")
                    #lancaigang240125：encapsulated function
                    self.Cmds_PhrozenKlipperResumeCommon()

                    #lancaigang250522：
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                    command_string = """
                        PG109
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up；command_string='%s'" % command_string)


                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")


                    self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

            else:
                self.G_PhrozenFluiddRespondInfo("+Mode:-1,error")

        except:
            self.G_PhrozenFluiddRespondInfo("except")





    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PrzATIdle(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PrzATIdle]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))
        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        #lancaigang240416:
        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("AT+IDLE")
            logging.info("serial port1send command：AT+IDLE")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AT+IDLE")
            logging.info("serial port2send command：AT+IDLE")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MARetryInFila(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MARetryInFila]")


        self.G_IfChangeFilaOngoing= True


        #lancaigang250522：
        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
        command_string = """
            PG109
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up；command_string='%s'" % command_string)
        self.IfDoPG102Flag=True


        #lancaigang231228：need waitstm32executeFAafter，toolhead detect to filament only then start print
        #set flag
        Lo_ChangeChannelIfSuccess = False
        #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
        self.G_KlipperPrintStatus= 2
        #lancaigang20231013：timeout
        #lancaigang231114：Not changing filament change timeout in printer.cfg config file, changing timeout directly here
        #loop detect2time(s)load filament filament isnot to toolhead
        for i in range(CHANGE_CHANNEL_WAIT_TIMEOUT+50):#largeapproximately130seconds
            #lancaigang231202：ifSTM32active/manual on report pause，needklipperpause
            if self.STM32ReprotPauseFlag==1:
                self.G_ChangeChannelFirstFilaFlag=True
                self.G_PhrozenFluiddRespondInfo("wait filament change during，stm32active/manual on reportpause")
                Lo_ChangeChannelIfSuccess = False


                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    logging.info("not in paused state")

                break

            #lancaigang231216：
            if self.G_XBasePosition==0 and self.G_YBasePosition==0:
                self.G_PhrozenFluiddRespondInfo("wait filament change during，base coordinateXYis0")
            else:
                #lancaigang231216：resume time，need back-and-forth movement prevent material leak generate apit
                #lancaigang231214：wait area zone base pointX Yby/withW Hrectangle step size back-and-forth move，implement purge function
                command_string = """
                    G90
                    G1 X%.03f Y%.03f F1000
                    """ % (
                    self.G_XBasePosition+(i%2),
                    self.G_YBasePosition+(i%2)
                )
                #lancaigang231129：slow back-and-forth movement
                self.G_PhrozenGCode.run_script_from_command(command_string)
                self.G_PhrozenFluiddRespondInfo("wait filament change during，base coordinateXYisP9config")


            #lancaigang20231013：change is4seconds delay
            #lancaigang231115：change is1s
            self.G_ProzenToolhead.dwell(1)
            #detect new channel filament load filament，isnot has filament to toolhead
            if self.G_ToolheadIfHaveFilaFlag:
                Lo_ChangeChannelIfSuccess = True
                break



        #normal filament change
        if Lo_ChangeChannelIfSuccess==True:
            self.G_PhrozenFluiddRespondInfo("change success")
            self.G_IfChangeFilaOngoing= False

            #lancaigang240108：toolhead has filament，can resume
            self.G_M2MAModeResumeFlag=True

            #lancaigang241106：success load filament
            self.G_P0M2MAStartPrintFlag=1

            #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
            self.G_KlipperPrintStatus= 3

            self.G_PauseToLCDString=""


            #lancaigang250607:
            self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
            self.G_KlipperQuickPause = True

            return

        self.G_PhrozenFluiddRespondInfo("change failed")
        # expire:timeout,
        # unit seconds(default60)
        # A0:ignore timeout,continue print(default)
        # A1:timeout afterend stop print
        #change timeout
        # lancaigang20231013：A0:ignore timeout
        if self.G_DictChangeChannelWaitAreaParam["A"] == 0:
            #lancaigang231209：stm32active/manual on report then not on report9
            if self.G_KlipperIfPaused==False:
                self.G_PhrozenFluiddRespondInfo("change timeout100s，pause")

                #lancaigang250702：
                if self.G_KlipperInPausing == False:
                    self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")

                    #klipperactive/manual pause
                    self.Cmds_PhrozenKlipperPauseM2M3ToSTM32(None)

                    self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                else:
                    self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")

            #lancaigang240123：if already is pause state，not allow again pause
            else:
                self.G_PhrozenFluiddRespondInfo("already pause，not allow repeat pause")

            #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
            self.G_ChangeChannelFirstFilaFlag=True
            self.G_IfChangeFilaOngoing= False

            #lancaigang241106：load filament failure
            self.G_P0M2MAStartPrintFlag=0

            #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
            self.G_KlipperPrintStatus= -1

            return

        #normal filament change；Actionnormal
        if self.G_DictChangeChannelWaitAreaParam["A"] == 1:
            pass

        self.G_IfChangeFilaOngoing= False
