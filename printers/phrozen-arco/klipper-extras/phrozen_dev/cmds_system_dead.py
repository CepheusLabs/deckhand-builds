import os
import logging
import json
import time
from .base import *


class SystemMixin:
    """Mixin for system diagnostics, print lifecycle, and state persistence."""

    def Cmds_PhrozenVersion(self, gcmd):
        # ASCIIcharset has a total of128character(see ontable)，code pointencoded number(i.e.characterencoded number)from0to127(two performcontrol is from0000 0000to0111 1111，
        #ten six performcontrol is from0x00to0x7F)，two performcontrol most height/highposition/bit all is0。where：
        # 0~31：cannot display cannot print control characters or special communication characters, like0x07(BELresponsebell)will let calculatemachine send outbeep asound、0x00(NULempty，note is not emptyspace)
        #typically use inspecifydisplay character string/serial end、0x0D(CRcarriage return)and0x0A(LFchangeexecute/row)use inspecifyshow printmachine printneedle head retract toexecute/row first(i.e.carriage return)andmove to down aexecute/row(i.e.changeexecute/row)Etc.
        # note： will this some use incontrol orcommunication controlcharacter orcommunicationspecial usecharacter called"character"，sense feel onlike almost has pointstrange，actual on this some allcalled "character"indicates itsactual is akind action orexecute/row is，
        #because this only thenalready cannot display also cannot print。
        # 32：can display but cannot print space character；
        # 33~126：can display can printcharacter，where48~57is0-9 Arabicuncle numbercharacter，65~90is26uppercase English letters，97~122is26smallwriteEnglish charactermother，
        #itsremaining is a somemark pointsymbol number、transportcalculate symbol numberEtc.
        # 127：cannot display cannot print controlcharacterDEL。


        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenVersion]command='%s'" % (gcmd.get_commandline(),))


        logging.info("current mode")
        self.Device_ReportModeIfChanged()



        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))
        # #lancaigang240224：testing
        # command = """
        # PAUSE
        # """
        # self.G_PhrozenGCode.run_script_from_command(command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.Cmds_PhrozenVersion)]calling macro:command=%s" % (command))
        # self.G_PhrozenFluiddRespondInfo("[(cmds.Cmds_PhrozenVersion)]prevent pause not hold，many/more add command；send_pause_command")
        # self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
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


        #emb_filename = "/home/prz/hdlDat/DriveCodeJson.dat"
        #json_data = json.load(emb_filename)
        # self.G_PhrozenFluiddRespondInfo("json_data=%s" % json_data)
        # DriveCode = json_data['DriveCode']
        # DriveImageType = json_data['DriveImageType']
        # DriveHwVersion = json_data['DriveHwVersion']
        # DriveFwVersion = json_data['DriveFwVersion']
        # DriveId = json_data['DriveId']
        # self.G_PhrozenFluiddRespondInfo("DriveCode=%s" % DriveCode)
        # self.G_PhrozenFluiddRespondInfo("DriveImageType=%s" % DriveImageType)
        # self.G_PhrozenFluiddRespondInfo("DriveHwVersion=%s" % DriveHwVersion)
        # self.G_PhrozenFluiddRespondInfo("DriveFwVersion=%s" % DriveFwVersion)
        # self.G_PhrozenFluiddRespondInfo("DriveId=%s" % DriveId)



        #self.G_ProzenToolhead.dwell(1.5)


        #=====DriveCodeFile.dat
        # 1 , 18 , 24053 , 18 , 0# // AMSmainboard1firmware-18
        # 2 , 18 , 24053 , 18 , 0# // AMSmainboard2firmware-18
        # 3 , 18 , 24053 , 18 , 0# // AMSmainboard3firmware-18
        # 4 , 18 , 24053 , 18 , 0# // AMSmainboard4firmware-18
        # 5 , 5 , 24046 , 5 , 0# // OTAsub-program-AMSserial port riselevel processorder/sequence-5 5
        # 6 , 0 , 0 , 0 , 0# // bufferboard firmware-6 6 reserved
        # 7 , 7 , 24051 , 7 , 0# // 16colorHUBboard firmware-7 7
        # 8 , 0 , 0 , 0 , 0
        # 9 , 0 , 0 , 0 , 0
        # 10 , 10 , 24054 , 10 , 0# // OTAsub-program-ceramic crystal pool serial portscreen backgroundprocessorder/sequence-10
        # 11 , 11 , 24047 , 11 , 0# // ceramic crystal pool serial portscreen foregroundHMIfirmware-11
        # 12 , 0 , 0 , 0 , 0
        # 13 , 0 , 0 , 0 , 0
        # 14 , 0 , 0 , 0 , 0
        # 15 , 15 , 25042 , 15 , 0
        # 16 , 16 , 25042 , 16 , 0
        # 17 , ? , 25042 , ? , 0
        # 18 , ? , 25042 , ? , 0
        # 19 , ? , 25042 , ? , 0
        # 20 , ? , 25042 , ? , 0
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
        #data = [{"DriveCode":16,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":15,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":14,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":13,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":12,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":11,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":10,"DriveImageType":10,"DriveHwVersion":10,"DriveFwVersion":24045,"DriveId":0},{"DriveCode":9,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":8,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":7,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":6,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":5,"DriveImageType":5,"DriveHwVersion":5,"DriveFwVersion":24046,"DriveId":0},{"DriveCode":4,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":3,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":2,"DriveImageType":0,"DriveHwVersion":0,"DriveFwVersion":0,"DriveId":0},{"DriveCode":1,"DriveImageType":1,"DriveHwVersion":1,"DriveFwVersion":24042,"DriveId":0}]
        #f = open(filename, 'a')
        #json.dump(data, f)  #objectsequence number is byte stream
        #f.close()
        with open(filename,'r') as file:
            #for line in file:
            # # realine() readwhole execute/row insidecontain，package include "\n" character
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
                    #line=("%d,%d,%d," % (HW_VERSION,,))
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
                    #line=("%d,%d,%d," % (HW_VERSION,,))
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="18":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    #line=("%d,%d,%d," % (HW_VERSION,,))
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="19":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    #line=("%d,%d,%d," % (HW_VERSION,,))
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A
                elif split[0]=="20":
                    self.G_PhrozenFluiddRespondInfo(split[0])
                    self.G_PhrozenFluiddRespondInfo(split[1])
                    self.G_PhrozenFluiddRespondInfo(split[2])
                    self.G_PhrozenFluiddRespondInfo(split[3])
                    self.G_PhrozenFluiddRespondInfo(split[4])
                    #line=("%d,%d,%d," % (HW_VERSION,,))
                    line_modify=split[0]+','+'18'+','+"00000"+','+'18'+','+'0'
                    self.G_PhrozenFluiddRespondInfo(line_modify)
                    Lo_AllLine=Lo_AllLine+line_modify+"\r\n"#0x0D 0x0A


                else:
                    Lo_AllLine=Lo_AllLine+line
        #self.G_PhrozenFluiddRespondInfo(Lo_AllLine)
        with open(filename,"w+") as file_w:
	        file_w.write(Lo_AllLine)




        #self.G_PhrozenFluiddRespondInfo("PRZ_DEV_VER: %s" % FW_VERSION)
        #self.G_PhrozenFluiddRespondInfo("V-H'%s'-I'%s'-F'%s'" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))




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

        #time.sleep(1)

        #self.Cmds_AMSSerial1Send("AT+SB=1")
        #self.G_PhrozenFluiddRespondInfo("send command: AT+SB=1；getAMSmainboard state")



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

        #  #lancaigang250514：Reading JSON config file，get single-color refill config and channel filament colormatch/config pair/to
        # #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json
        # self.Cmds_GetUartScreenCfg()

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

        #  #lancaigang250514：Reading JSON config file，get single-color refill config and channel filament colormatch/config pair/to
        # #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json
        # self.Cmds_GetUartScreenCfg()
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

        # #lancaigang250514：Reading JSON config file，get single-color refill config and channel filament colormatch/config pair/to
        # #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json
        # self.Cmds_GetUartScreenCfg()

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_HomingOverrideEnd(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_HomingOverrideEnd]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))

        # #lancaigang250514：Reading JSON config file，get single-color refill config and channel filament colormatch/config pair/to
        # #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json
        # self.Cmds_GetUartScreenCfg()


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

        #self.G_PhrozenFluiddRespondInfo("%s" % (gcmd.get_commandline(),))

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
                #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                #self.G_KlipperPrintStatus = 3
                if self.G_SerialPort1OpenFlag == False and self.G_SerialPort2OpenFlag == False:
                    self.G_PhrozenFluiddRespondInfo("no method/way connectAMS，pause")
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        self.G_KlipperIfPaused = True
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
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
                #self.G_ToolheadFirstInputFila=False
                #self.P0M3FilaRunoutSpittingFinished=True
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
                    # #lancaigang250427：
                    # if self.G_SerialPort1OpenFlag == True:
                    #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                    #     logging.info("serial port1-AMSend count when buffer full when interval")
                    # if self.G_SerialPort2OpenFlag == True:
                    #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                    #     logging.info("serial port2-AMSend count when buffer full when interval")
                    # #self.G_ProzenToolhead.dwell(1.5)
                else:
                    self.G_PhrozenFluiddRespondInfo("no filament，need pause wait")
                    # self.G_PhrozenFluiddRespondInfo("external macro-RESUME")
                    # command = """
                    # RESUME
                    # """
                    # self.G_PhrozenGCode.run_script_from_command(command)
                    # self.G_PhrozenFluiddRespondInfo("calling macro:command=%s" % (command))
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
                        #lancaigang250607:
                        #self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        #self.G_KlipperQuickPause = True
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")




                    self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                    # if self.G_SerialPort1OpenFlag==True or self.G_SerialPort2OpenFlag==True:
                    #     self.G_PhrozenFluiddRespondInfo("toolhead no filament，hasAMSmulti-color，executeP8complete load filament process")
                    #     #lancaigang241106：
                    #     self.G_P0M2MAStartPrintFlag=0

                    #     #lancaigang250522：not allowM3runout detection
                    #     self.G_IfChangeFilaOngoing = True

                    #     #lancaigang241106：
                    #     self.Cmds_CmdP8(gcmd)
                    #     #lancaigang241106:toolhead success load filament
                    #     if self.G_P0M2MAStartPrintFlag==1:
                    #         #lancaigang250607:
                    #         self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                    #         self.G_KlipperQuickPause = True
                    #         self.G_PhrozenFluiddRespondInfo("toolhead has filament，resume")
                    #         #lancaigang240125：encapsulated function
                    #         self.Cmds_PhrozenKlipperResumeCommon()
                    #     else:
                    #         self.G_KlipperQuickPause = False
                    #         self.G_PhrozenFluiddRespondInfo("toolhead no filament，refill continue pause")
                    #         if self.G_KlipperIfPaused == False:
                    #             self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    #             self.G_KlipperIfPaused=True
                    #             #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                    #             self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #         else:
                    #             self.G_PhrozenFluiddRespondInfo("already pause，no need repeat pause")
                    # else:
                    #     self.G_KlipperQuickPause = False
                    #     self.G_PhrozenFluiddRespondInfo("toolhead no filament，withoutAMSmulti-color，continue pause")
                    #     self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    #     #no filament continue pause
                    #     self.G_KlipperIfPaused=True
                    #     #lancaigang250521:hasAMSmulti-color
                    #     #if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    #     self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #     #else:
                    #     #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))




            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                self.G_PhrozenFluiddRespondInfo("+Mode:3,RUNOUT")
                self.G_P0M3Flag = True
                #self.G_ToolheadFirstInputFila = True
                #lancaigang240415：toolhead has filament，a time(s)no need purge
                #self.G_P0M3ToolheadHaveFilaNotSpittingFlag = True
                #self.P0M3FilaRunoutSpittingFinished==True:#purge complete

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
                    #self.G_KlipperQuickPause = True
                    # #lancaigang250427：
                    # if self.G_SerialPort1OpenFlag == True:
                    #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                    #     logging.info("serial port1-AMSend count when buffer full when interval")
                    # if self.G_SerialPort2OpenFlag == True:
                    #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                    #     logging.info("serial port2-AMSend count when buffer full when interval")
                    # #self.G_ProzenToolhead.dwell(1.5)
                else:
                    self.G_PhrozenFluiddRespondInfo("no filament，need pause wait")
                    # self.G_PhrozenFluiddRespondInfo("external macro-RESUME")
                    # command = """
                    # RESUME
                    # """
                    # self.G_PhrozenGCode.run_script_from_command(command)
                    # self.G_PhrozenFluiddRespondInfo("calling macro:command=%s" % (command))
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
                        #lancaigang250607:
                        #self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        #self.G_KlipperQuickPause = True
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")




                    self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                    # if self.G_SerialPort1OpenFlag==True or self.G_SerialPort2OpenFlag==True:
                    #     self.G_PhrozenFluiddRespondInfo("toolhead no filament，hasAMSmulti-color，executeP8complete load filament process")
                    #     #lancaigang241106：
                    #     self.G_P0M2MAStartPrintFlag=0

                    #     #lancaigang250522：not allowM3runout detection
                    #     self.G_IfChangeFilaOngoing = True

                    #     #lancaigang241106：
                    #     self.Cmds_CmdP8(gcmd)
                    #     #lancaigang241106:toolhead success load filament
                    #     if self.G_P0M2MAStartPrintFlag==1:
                    #         #lancaigang250607:
                    #         self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                    #         self.G_KlipperQuickPause = True
                    #         self.G_PhrozenFluiddRespondInfo("toolhead has filament，resume")
                    #         #lancaigang240125：encapsulated function
                    #         self.Cmds_PhrozenKlipperResumeCommon()
                    #     else:
                    #         self.G_KlipperQuickPause = False
                    #         self.G_PhrozenFluiddRespondInfo("toolhead no filament，refill continue pause")
                    #         if self.G_KlipperIfPaused == False:
                    #             self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    #             self.G_KlipperIfPaused=True
                    #             #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                    #             self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #         else:
                    #             self.G_PhrozenFluiddRespondInfo("already pause，no need repeat pause")
                    # else:
                    #     self.G_KlipperQuickPause = False
                    #     self.G_PhrozenFluiddRespondInfo("toolhead no filament，withoutAMSmulti-color，continue pause")
                    #     self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                    #     #no filament continue pause
                    #     self.G_KlipperIfPaused=True
                    #     #lancaigang250521:hasAMSmulti-color
                    #     #if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    #     self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #     #else:
                    #     #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

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
            # self.G_XBasePosition+=2
            # self.G_YBasePosition+=2
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
            #lancaigang240222：cannot usetime.sleep，will causes abnormalcodedump
            #time.sleep(1)



            # self.G_PhrozenFluiddRespondInfo("external macro-PG110；STM32load filament after，klipperstart purgecatch/connect hold load filament")
            # command_string = """
            # PG110
            # """
            # self.G_PhrozenGCode.run_script_from_command(command_string)
            # self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)




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


            # #lancaigang250611：
            # self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
            # command_string = """
            #     PG108
            #     """
            # self.G_PhrozenGCode.run_script_from_command(command_string)

            #lancaigang250607:
            self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
            self.G_KlipperQuickPause = True
            # #lancaigang250427：
            # if self.G_SerialPort1OpenFlag == True:
            #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
            #     logging.info("serial port1-AMSend count when buffer full when interval")
            # if self.G_SerialPort2OpenFlag == True:
            #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
            #     logging.info("serial port2-AMSend count when buffer full when interval")
            # #self.G_ProzenToolhead.dwell(1.5)


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

                    #lancaigang240104：no need sendstm32pause
                    #klipperactive/manual pause
                    self.Cmds_PhrozenKlipperPauseM2M3ToSTM32(None)

                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
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
