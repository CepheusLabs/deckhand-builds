import os
import numpy as np
import logging
import json
import time
import serial
from .base import *
from .cmds_structs import *
from ctypes import *


class PCommandsMixin:
    """Mixin for P-command G-code handlers."""

    def Cmds_CmdP114(self, gcmd):
        _ = gcmd

        if gcmd is None:
            logging.info("[(cmds.python)Cmds_CmdP114]commandP114-None")
        if gcmd is not None:
            logging.info("[(cmds.python)Cmds_CmdP114]command='%s'" % (gcmd.get_commandline(),))

            #getP114command parameter
            params = gcmd.get_command_parameters()

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang240510：
        self.G_PhrozenFluiddRespondInfo("+P114:0")

        self.Device_ReportModeIfChanged()


        #unlock
        self.Base_AMSSerialCmdUnlock()



        logging.info("self.G_CancelFlag='%s'" % self.G_CancelFlag)
        #lancaigang250712:


        #lancaigang240511：resume time，all initialize a down serial port，prevent hot-plugAMScauses serial portcommunication abnormal
        try:
            logging.info("[(cmds.py)Cmds_CmdP114]re-initialize serial port1")
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

        try:
            logging.info("[(cmds.py)Cmds_CmdP114]re-initialize serial port2")
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


        #lancaigang240524：serial flush handles packet separation, no delay needed

        if self.G_SerialPort1OpenFlag==True:
            if self.G_SerialPort1Obj.is_open:
                logging.info("serial port1is open")

        if self.G_SerialPort2OpenFlag==True:
            if self.G_SerialPort2Obj.is_open:
                logging.info("serial port2is open")



        #lancaigang250619:checkAMSisnot re-connect success

        #get ChromaKit MMU detailed status
        #lancaigang240430：stm32will delay on report，here usewithrsp，will causestime too close；so during printing not allow sendP114
         #lancaigang240524：change is send afterasynccatch/connect receive
        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("SD")
            logging.info("serial port1send command：SD")

        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("SD")
            logging.info("serial port2send command：SD")


        
        #lancaigang240123：preventcutchip/piece soft piece/piece/piece/piece/piece read toofast causesstm32packet concatenation
        #lancaigang240229：cannot usetime.sleep，will causestime to close
        #lancaigang240510：

        self.G_P114RunFlag=1

        return


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P30 auto arrange deviceID(use inmany/more device auto network)；"I";handle auto arrange deviceIDcommand
    def Cmds_CmdP30(self, gcmd):
        if not self.G_SerialPort1OpenFlag:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP30]AMSmulti-color not yet connect，please first sendP28")
            return
        
        self.G_PhrozenFluiddRespondInfo("command='%s'" % (gcmd.get_commandline(),))

        mcu_cmd = G_DictPhrozenCmdP30["mcu_cmd"][0] + "0"
        self.Cmds_AMSSerial1Send(mcu_cmd)
        self.G_PhrozenFluiddRespondInfo("send command: %s" % mcu_cmd)

        logging.info("SendCmd: %s" % mcu_cmd)

    

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P29 disconnect connect
    def Cmds_CmdP29(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP29]command")

        try:
            if self.G_SerialPort1Obj is not None:
                if self.G_SerialPort1Obj.is_open:
                    #tty1close
                    self.G_SerialPort1Obj.close()
        except:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP29]AMS1multi-color not yet connect")
        self.G_SerialPort1OpenFlag = False
        self.G_PhrozenFluiddRespondInfo("AMS1clear")
        self.G_SerialPort1Obj=None

        try:
            if self.G_SerialPort2Obj is not None:
                if self.G_SerialPort2Obj.is_open:
                    self.G_SerialPort2Obj.close()
        except:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP29]AMS2multi-color not yet connect")
        self.G_SerialPort2OpenFlag = False
        self.G_PhrozenFluiddRespondInfo("AMS2clear")
        self.G_SerialPort2Obj=None


        if self.G_SerialPort1RecvTimmer:
            #unregister
            self.G_PhrozenReactor.unregister_timer(self.G_SerialPort1RecvTimmer)
            #clear timer
            self.G_SerialPort1RecvTimmer = None

        #lancaigang241030
        if self.G_SerialPort2RecvTimmer:
            #unregister
            self.G_PhrozenReactor.unregister_timer(self.G_SerialPort2RecvTimmer)
            #clear timer
            self.G_SerialPort2RecvTimmer = None

        #lancaigang250515：
        self.G_P0M1MCNoneAMS=0
        logging.info("self.G_P0M1MCNoneAMS=0")



        #lancaigang231122：usettyafter，need enable backgroundIAPriselevel processorder/sequencehdl_zigbee_gateway



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_GetImageId(self):
        logging.info("[(dev.python)Cmds_GetImageId]")

        current_directory = os.getcwd()
        logging.info("current_directory=%s" % (current_directory))

        #lancaigang250514：read configtable
        try:
            logging.info("try")
            
            # hit/open open/enableJSONtext piece/piece/piece/piece/piece and read insidecontain
            logging.info("/etc/ImageId.json")
            with open('/etc/ImageId.json', 'r', encoding='utf-8') as file:
                ImageData = file.read()
            logging.info("with open")
            # parseJSONdata
            json_data = json.loads(ImageData)
            self.G_PhrozenFluiddRespondInfo("json_data['ImageId']=%d" % (json_data['ImageId']))
            self.G_ImageId= json_data['ImageId']
            self.G_PhrozenFluiddRespondInfo("self.G_ImageId=%d" % (self.G_ImageId))
            self.G_PhrozenFluiddRespondInfo("json_data['HwId']=%d" % (json_data['HwId']))
            self.HwId= json_data['HwId']
            self.G_PhrozenFluiddRespondInfo("self.HwId=%d" % (self.HwId))
            self.G_PhrozenFluiddRespondInfo("json_data['FwId']=%d" % (json_data['FwId']))
            self.G_PhrozenFluiddRespondInfo("json_data['NC0']=%d" % (json_data['NC0']))
            self.G_PhrozenFluiddRespondInfo("json_data['NC1']=%d" % (json_data['NC1']))
            self.G_PhrozenFluiddRespondInfo("json_data['NC2']=%d" % (json_data['NC2']))
            self.G_PhrozenFluiddRespondInfo("json_data['NC3']=%d" % (json_data['NC3']))
            self.G_PhrozenFluiddRespondInfo("json_data['NC4']=%d" % (json_data['NC4']))

            if self.G_ImageId==16:
                self.G_PhrozenFluiddRespondInfo("Image ID==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
            elif self.G_ImageId==31:
                self.G_PhrozenFluiddRespondInfo("Image ID==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
            elif self.G_ImageId==-1:
                self.G_PhrozenFluiddRespondInfo("Image ID==-1，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
            else:
                self.G_PhrozenFluiddRespondInfo("Image IDread not to，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
        except Exception as e:
            self.G_PhrozenFluiddRespondInfo("Failed to read config file")
            self.G_PhrozenFluiddRespondInfo("self.G_ImageId=%d" % (self.G_ImageId))


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_GetUartScreenCfg(self):
        logging.info("[(cmds.python)Cmds_GetUartScreenCfg]")


        #lancaigang250514：read configtable
        try:
            logging.info("try")

            #lancaigang250724：readsystem/relation systemmirror likeid，areadivide differentproduceproduct different mainboard different firmware
            #lancaigang250724:readmirror likeid
            self.Cmds_GetImageId()
            if self.G_ImageId==16:
                self.G_PhrozenFluiddRespondInfo("Image ID==16：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                # hit/open open/enableJSONtext piece/piece/piece/piece/piece and read insidecontain
                with open('/home/mks/klipper/klippy/extras/phrozen_dev/serial-screen/plr_print_precfg.json', 'r', encoding='utf-8') as file:
                    UartScreenCfgData = file.read()
            elif self.G_ImageId==31:
                self.G_PhrozenFluiddRespondInfo("Image ID==31：ARCO300-phrozen-RK3308-STM32F407VET6-I31")
                # hit/open open/enableJSONtext piece/piece/piece/piece/piece and read insidecontain
                with open('/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/plr_print_precfg.json', 'r', encoding='utf-8') as file:
                    UartScreenCfgData = file.read()
            elif self.G_ImageId==-1:
                self.G_PhrozenFluiddRespondInfo("Image ID==-1，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                # hit/open open/enableJSONtext piece/piece/piece/piece/piece and read insidecontain
                with open('/home/mks/klipper/klippy/extras/phrozen_dev/serial-screen/plr_print_precfg.json', 'r', encoding='utf-8') as file:
                    UartScreenCfgData = file.read()
            else:
                self.G_PhrozenFluiddRespondInfo("Image IDread not to，default：ARCO300-MKS-RK3328-STM32F407VET6-I16")
                # hit/open open/enableJSONtext piece/piece/piece/piece/piece and read insidecontain
                with open('/home/mks/klipper/klippy/extras/phrozen_dev/serial-screen/plr_print_precfg.json', 'r', encoding='utf-8') as file:
                    UartScreenCfgData = file.read()

            logging.info("with open")
            # parseJSONdata
            json_data = json.loads(UartScreenCfgData)
            self.G_PhrozenFluiddRespondInfo("json_data['Auto_Replace_state']=%d" % (json_data['Auto_Replace_state']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_num']=%d" % (json_data['Chroma_Kit_num']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T0']=%d" % (json_data['Chroma_Kit_access']['T0']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T1']=%d" % (json_data['Chroma_Kit_access']['T1']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T2']=%d" % (json_data['Chroma_Kit_access']['T2']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T3']=%d" % (json_data['Chroma_Kit_access']['T3']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T4']=%d" % (json_data['Chroma_Kit_access']['T4']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T5']=%d" % (json_data['Chroma_Kit_access']['T5']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T6']=%d" % (json_data['Chroma_Kit_access']['T6']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T7']=%d" % (json_data['Chroma_Kit_access']['T7']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T8']=%d" % (json_data['Chroma_Kit_access']['T8']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T9']=%d" % (json_data['Chroma_Kit_access']['T9']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T10']=%d" % (json_data['Chroma_Kit_access']['T10']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T11']=%d" % (json_data['Chroma_Kit_access']['T11']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T12']=%d" % (json_data['Chroma_Kit_access']['T12']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T13']=%d" % (json_data['Chroma_Kit_access']['T13']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T14']=%d" % (json_data['Chroma_Kit_access']['T14']))
            self.G_PhrozenFluiddRespondInfo("json_data['Chroma_Kit_access']['T15']=%d" % (json_data['Chroma_Kit_access']['T15']))


            self.G_AutoReplaceState = json_data['Auto_Replace_state']
            self.G_ChromaKitNum = json_data['Chroma_Kit_num']
            self.G_ChromaKitAccessT0 = json_data['Chroma_Kit_access']['T0']
            self.G_ChromaKitAccessT1 = json_data['Chroma_Kit_access']['T1']
            self.G_ChromaKitAccessT2 = json_data['Chroma_Kit_access']['T2']
            self.G_ChromaKitAccessT3 = json_data['Chroma_Kit_access']['T3']
            self.G_ChromaKitAccessT4 = json_data['Chroma_Kit_access']['T4']
            self.G_ChromaKitAccessT5 = json_data['Chroma_Kit_access']['T5']
            self.G_ChromaKitAccessT6 = json_data['Chroma_Kit_access']['T6']
            self.G_ChromaKitAccessT7 = json_data['Chroma_Kit_access']['T7']
            self.G_ChromaKitAccessT8 = json_data['Chroma_Kit_access']['T8']
            self.G_ChromaKitAccessT9 = json_data['Chroma_Kit_access']['T9']
            self.G_ChromaKitAccessT10 = json_data['Chroma_Kit_access']['T10']
            self.G_ChromaKitAccessT11 = json_data['Chroma_Kit_access']['T11']
            self.G_ChromaKitAccessT12 = json_data['Chroma_Kit_access']['T12']
            self.G_ChromaKitAccessT13 = json_data['Chroma_Kit_access']['T13']
            self.G_ChromaKitAccessT14 = json_data['Chroma_Kit_access']['T14']
            self.G_ChromaKitAccessT15 = json_data['Chroma_Kit_access']['T15']

            self.G_PhrozenFluiddRespondInfo("self.G_AutoReplaceState=%d" % (self.G_AutoReplaceState))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitNum=%d" % (self.G_ChromaKitNum))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT0=%d" % (self.G_ChromaKitAccessT0))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT1=%d" % (self.G_ChromaKitAccessT1))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT2=%d" % (self.G_ChromaKitAccessT2))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT3=%d" % (self.G_ChromaKitAccessT3))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT4=%d" % (self.G_ChromaKitAccessT4))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT5=%d" % (self.G_ChromaKitAccessT5))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT6=%d" % (self.G_ChromaKitAccessT6))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT7=%d" % (self.G_ChromaKitAccessT7))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT8=%d" % (self.G_ChromaKitAccessT8))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT9=%d" % (self.G_ChromaKitAccessT9))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT10=%d" % (self.G_ChromaKitAccessT10))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT11=%d" % (self.G_ChromaKitAccessT11))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT12=%d" % (self.G_ChromaKitAccessT12))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT13=%d" % (self.G_ChromaKitAccessT13))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT14=%d" % (self.G_ChromaKitAccessT14))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT15=%d" % (self.G_ChromaKitAccessT15))
            
        except:
            self.G_PhrozenFluiddRespondInfo("parse data abnormal，but notaffect data get")

####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_GetUartScreenCfgClear(self):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_GetUartScreenCfgClear]")


        #lancaigang250514：read configtable
        try:
            logging.info("try")
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

            self.G_PhrozenFluiddRespondInfo("self.G_AutoReplaceState=%d" % (self.G_AutoReplaceState))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitNum=%d" % (self.G_ChromaKitNum))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT0=%d" % (self.G_ChromaKitAccessT0))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT1=%d" % (self.G_ChromaKitAccessT1))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT2=%d" % (self.G_ChromaKitAccessT2))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT3=%d" % (self.G_ChromaKitAccessT3))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT4=%d" % (self.G_ChromaKitAccessT4))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT5=%d" % (self.G_ChromaKitAccessT5))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT6=%d" % (self.G_ChromaKitAccessT6))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT7=%d" % (self.G_ChromaKitAccessT7))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT8=%d" % (self.G_ChromaKitAccessT8))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT9=%d" % (self.G_ChromaKitAccessT9))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT10=%d" % (self.G_ChromaKitAccessT10))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT11=%d" % (self.G_ChromaKitAccessT11))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT12=%d" % (self.G_ChromaKitAccessT12))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT13=%d" % (self.G_ChromaKitAccessT13))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT14=%d" % (self.G_ChromaKitAccessT14))
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT15=%d" % (self.G_ChromaKitAccessT15))
            
        except:
            self.G_PhrozenFluiddRespondInfo("situation serial portscreen config data abnormal")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P0 M1；multi-color mode mode(need connect external device) Yes；"MC";P0 M1;P28;P2 A1;
    # P0 M2；multi-color in single-color refill mode(need connect external device)；"MA";P0 M2;P28;P8;
    # P0 M3; single-color runout mode;P0 M3;
    # P28 connect device
    def Cmds_CmdP28(self, gcmd):
        logging.info("[(cmds.python)Cmds_CmdP28]command='%s'" % (gcmd.get_commandline(),))

        logging.info("self.G_CancelFlag='%s'" % self.G_CancelFlag)


        #lancaigang250517：
        #lancaigang250517：
        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)


        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")

        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        #unlock
        self.Base_AMSSerialCmdUnlock()

        #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
        if self.G_KlipperPrintStatus == 3:
            self.G_PhrozenFluiddRespondInfo("print in，not handleP28!!!")
            return

        #lancaigang250724:readmirror likeid
        self.Cmds_GetImageId()

        #lancaigang250514：Reading JSON config file，get single-color refill config and channel filament colormatch/config pair/to
        #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json
        self.Cmds_GetUartScreenCfg()
        


        #lancaigang231220：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP28]single-color mode，not handleP28")
            self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))
            return

        #lancaigang250610：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP28]single-color refill mode，not handleP28")
            self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))
            return



        #lancaigang231205：
        self.G_KlipperIfPaused = False
        #lancaigang250526：pausing，not allow new gcodecommand，need wait pause complete
        self.G_KlipperInPausing = False
        #lancaigang250526：
        self.G_IfToolheadHaveFilaInitiativePauseFlag=False
        #lancaigang240223：toolhead cut failure flag
        self.ToolheadCutFlag = False



        if self.G_SerialPort1Obj is not None:
            #lancaigang231219：if serial port alreadyhit/open open/enable，cannot again toward down
            if self.G_SerialPort1Obj.is_open:
                self.G_PhrozenFluiddRespondInfo("Duplicate P28 - serial port 1 already open")

                #lancaigang240524：not tube is is notNone，all performexecute/row serial port timer register
                #timercycle period thread
                logging.info("re-register serial port1callback function")
                self.G_Serial1PortRecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)

                #lancaigang240511：may causes before afterpacket concatenation abnormal，likeMA M0 MAEtc.,causesAMSrestart


                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()
                if self.G_SerialPort1OpenFlag == True:
                    

                    self.Cmds_AMSSerial1Send("SD")
                    logging.info("SD")

                self.G_ProzenToolhead.dwell(2)


                self.G_SerialPortHaveOpenedCount=self.G_SerialPortHaveOpenedCount+1



        if self.G_SerialPort2Obj is not None:
            if self.G_SerialPort2Obj.is_open:
                self.G_PhrozenFluiddRespondInfo("Duplicate P28 - serial port 2 already open")
                logging.info("re-register serial port2callback function")
                self.G_SerialPort2RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart2Recv, self.G_PhrozenReactor.NOW)
                

                self.G_ProzenToolhead.dwell(0.5)

                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("SD")
                    logging.info("SD")

                self.G_ProzenToolhead.dwell(2)

                self.G_SerialPortHaveOpenedCount=self.G_SerialPortHaveOpenedCount+1



        #lancaigang241030:
        if self.G_SerialPortHaveOpenedCount>0:
            self.G_PhrozenFluiddRespondInfo("ChromaKit connected, open serial ports='%d'" % (self.G_SerialPortHaveOpenedCount,))
            self.G_SerialPortHaveOpenedCount=0
            self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))
            self.G_PhrozenFluiddRespondInfo("+AMSCONNECT:0")

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

            self.G_PhrozenFluiddRespondInfo("return")
            return


        #lancaigang240511：change is0.5，preventklipperstart move/actiontime too close
        time.sleep(0.5)
        
        #lancaigang231128：G28change isPG28



        #lancaigang241030:serial port1
        try:
            #hit/open open/enablettyserial port，baud rate19200
            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
            #serial port opened successfully
            if self.G_SerialPort1Obj.is_open:
                self.G_PhrozenFluiddRespondInfo("serial port11time(s)hit/open open/enable success")
                #lancaigang231213：open serial port
                self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                self.G_SerialPort1Obj.flush()
                self.G_SerialPort1OpenFlag = True
                #lancaigang240524：not tube is is notNone，all performexecute/row serial port timer register
                #timercycle period thread
                self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)

                #lancaigang240306：if mode isM1-MC，then sendMCtostm32
                if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
                    self.G_PhrozenFluiddRespondInfo("AMS_WORK_MODE_MC；send command: M1-MC，MCmode")
                    self.Cmds_AMSSerial1Send("MC")

                #lancaigang241031：unknown mode，thendefaultMC
                if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                    self.G_PhrozenFluiddRespondInfo("AMS_WORK_MODE_UNKNOW；send command: M1-MC，MCmode")
                    self.Cmds_AMSSerial1Send("MC")


                if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                    self.G_PhrozenFluiddRespondInfo("AMS_WORK_MODE_MA；send command: M2-MA，MAmode")
                    self.Cmds_AMSSerial1Send("MA")

                if self.G_ToolheadIfHaveFilaFlag:
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament")
                    #lancaigang240113：MCmode or unknown moderetract filament AMS_WORK_MODE_UNKNOW, 
                    if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
                        #lancaigang240319：preparation before filament cut
                        self.G_PhrozenFluiddRespondInfo("PG107；heat before wipe nozzle")
                        command_string = """
                        PG107
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                        #lancaigang240323：cut filament before first wipe nozzle
                        #lancaigang231202：home/reset cut filament and retract
                        self.Cmds_MoveToCutFilaAndRollback(gcmd)
                    #lancaigang240104：single-colorM2MArefill mode cannot cut filament

                    #delay20s，preventp28after side/facetight with other command and no method/way handle
                
                self.G_ProzenToolhead.dwell(2)

                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("SD")
                    logging.info("SD")

                self.G_ProzenToolhead.dwell(2)


                self.G_SerialPortIsOpenCount=self.G_SerialPortIsOpenCount+1


            else:
                self.G_PhrozenFluiddRespondInfo("serial port11time(s)hit/open open/enable failure")
                self.G_SerialPort1OpenFlag = False
                #lancaigang231207：1-AMSmulti-color connect failure
                #lancaigang231207：2-AMSmulti-color serial portttyhit/open open/enable failure
                self.G_PhrozenFluiddRespondInfo("+AMSERROR:1")
                self.G_PhrozenFluiddRespondInfo("AMS1multi-color connect failure")
        except:
            self.G_PhrozenFluiddRespondInfo("serial port11time(s)hit/open open/enable failure")
            #lancaigang231207：1-AMSmulti-color connect failure
            #lancaigang231207：2-AMSmulti-color serial portttyhit/open open/enable failure
            self.G_PhrozenFluiddRespondInfo("+AMSERROR:2")
            self.G_PhrozenFluiddRespondInfo("not yet canhit/open open/enabletty1port，please checkUSBport or restarttry")
        


        #lancaigang241030:serial port2
        try:
            #hit/open open/enablettyserial port，baud rate19200
            self.G_SerialPort2Obj = serial.Serial(self.G_Serialport2Define, SERIAL_PORT_BAUD, timeout=3)
            #serial port opened successfully
            if self.G_SerialPort2Obj.is_open:
                self.G_PhrozenFluiddRespondInfo("serial port21time(s)hit/open open/enable success")
                self.G_SerialPort2Obj.flushInput()  # clean serial write cache
                self.G_SerialPort2Obj.flush()
                self.G_SerialPort2OpenFlag = True
                self.G_SerialPort2RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart2Recv, self.G_PhrozenReactor.NOW)

                self.G_ProzenToolhead.dwell(0.5)

                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("SD")
                    logging.info("SD")

                self.G_ProzenToolhead.dwell(2)

                self.G_SerialPortIsOpenCount=self.G_SerialPortIsOpenCount+1



            else:
                self.G_PhrozenFluiddRespondInfo("serial port21time(s)hit/open open/enable failure")
                self.G_SerialPort2OpenFlag = False
                self.G_PhrozenFluiddRespondInfo("+AMSERROR:1")
                self.G_PhrozenFluiddRespondInfo("AMS2multi-color connect failure")
        except:
            self.G_PhrozenFluiddRespondInfo("serial port21time(s)hit/open open/enable failure")
            self.G_PhrozenFluiddRespondInfo("+AMSERROR:2")
            if not self._tty2_open_failure_logged:
                self.G_PhrozenFluiddRespondInfo("Failed to open tty2 port - check USB connection or restart")
                self._tty2_open_failure_logged = True
            else:
                logging.debug("Failed to open tty2 port - check USB connection or restart")



        #lancaigang241030:only need successhit/open open/enableaserial port，indicates can use multi-color
        if self.G_SerialPortIsOpenCount>0:
            self.G_PhrozenFluiddRespondInfo("successhit/open open/enableAMSmulti-color hasseveral unit=%d" % self.G_SerialPortIsOpenCount)
            self.G_SerialPortIsOpenCount=0
            
            self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))
            self.G_PhrozenFluiddRespondInfo("+AMSCONNECT:0")

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

        #if is0，indicates without successhit/open open/enableany what/how aserial port
        else:
            self.G_PhrozenFluiddRespondInfo("+AMSERROR:2")
            self.G_PhrozenFluiddRespondInfo("not yet canhit/open open/enableany what/howttyport，please checkUSBport or restarttry")

            raise gcmd.error("without connectany what/howAMSmulti-color，connectAMSfailure")



    ####################################
    #Function Name:python
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20241101
    ####################################
    #lancaigang241101：
    # P10 S?    parameterS[1,5]:purge time(s)numbercontrol，S1-purge1time(s)，S2-purge2time(s)...，mostmany/moresupport hold purge5time(s)
    def Cmds_CmdP10(self, gcmd):
        #get command parameter
        params = gcmd.get_command_parameters()

        if self.G_KlipperIfPaused == True:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP10]klipperpause，but still received command")

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP10]command='%s'" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("command：'%s'" % (gcmd.get_commandline(),))

        if "S" in params:
            Lo_SpitNum = int(params["S"])
            if not Lo_SpitNum in [1, 2, 3,4,5,6,7,8,9]:
                raise gcmd.error("noeffect parameter command;cmd '%s', parameterSneed at[1/2/3/4/5/6/7/8/9]" % (gcmd.get_commandline(),))

            self.G_P10SpitNum=Lo_SpitNum



        #lancaigang250519:
        self.G_PhrozenFluiddRespondInfo("external macro-PRZ_CUT_WAITINGAREA")
        command_string = """
            PRZ_CUT_WAITINGAREA
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position；command_string='%s'" % command_string)



        self.G_PhrozenFluiddRespondInfo("purge time(s)number：'%d'" % (self.G_P10SpitNum,))

    ####################################
    #Function Name:python
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20241101
    ####################################
    # P11 T?;multi-color cutter test
    def Cmds_CmdP11(self, gcmd):
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP11]gcmd-None")
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP11]return")
            return
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP11]command='%s'" % (gcmd.get_commandline(),))
        
        #get command parameter
        params = gcmd.get_command_parameters()

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP11]command='%s'；multi-color cutter test" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("command：'%s'" % (gcmd.get_commandline(),))

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+P11:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang231209：manualadjust can no need tube pause
        self.G_KlipperIfPaused=False
        #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
        self.STM32ReprotPauseFlag=0
        self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")

        #lancaigang250805:cutter test
        self.G_CutCheckTest=True
        self.ManualCmdFlag=False


        self.G_PhrozenFluiddRespondInfo("force home/reset，cut filament；allAMSfirst retract")
        #lancaigang231205：home/reset cut filament retract
        self.Cmds_MoveToCutFilaAndHomingXY(gcmd)



        self.G_PhrozenFluiddRespondInfo("external macro-PG104-get pre-change global variables")
        command_string = """
            PG104
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-PG104-get pre-change global variables；command_string='%s'" % command_string)
        self.IfDoPG102Flag=True


        #lancaigang240510：filament change before，first run/move to wait area
        #lancaigang240306：moved to cut filament code
        #lancaigang240110：wait area zone wait before，first execute external macro，move tospecial fixed/set position performexecute/row wait
        #lancaigang240515：filament change before，first first need to wait area
        self.G_PhrozenFluiddRespondInfo("external macro-PG101-retract")
        command_string = """
            PG101
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position wait purge；command_string='%s'" % command_string)
        self.IfDoPG102Flag=True



        #lancaigang240319：cutcomplete after，first purge/spitresidual toolhead filament，preventcut into pellets
        self.G_PhrozenFluiddRespondInfo("external macro-PG106；cut filament before，first purge/spitresidual toolhead filament，preventcut into pellets")
        self.PG102Flag=True
        logging.info("self.Flag=True")
        command_string = """
        PG106
        """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
        self.PG102Flag=False
        logging.info("self.Flag=False")



        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()


        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("AP")
            logging.info("serial port1send command：AP")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AP")
            logging.info("serial port2send command：AP")

        self.G_ProzenToolhead.dwell(0.5)


        #lancaigang240913：delay timeplace/put to outside side/face
        self.G_ProzenToolhead.dwell(6.0)
        #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
        self.Cmds_CutFilaIfNormalCheck()
        if self.G_KlipperIfPaused == True:
            self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P11:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            #lancaigang250805:cutter test
            self.G_CutCheckTest=False
            return


        #lancaigang231207：
        if self.G_IfInFilaBlockFlag:
            self.G_PhrozenFluiddRespondInfo("load filament jammed filament，first manualP1 E?from toolhead onmaterial tube remove and manualprz_resumeresume")
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P11:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            #lancaigang250805:cutter test
            self.G_CutCheckTest=False
            return


        if "T" in params:
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P11 Tn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=int(params["T"])
            self.G_ChangeChannelTimeoutNewGcmd=gcmd


            self.G_P10SpitNum=1

            #lancaigang241030：generally isP1 C1toP1 C32，range at1to32
            #1unit：1 2 3 4
            #2unit：5 6 7 8
            #3unit：9 10 11 12
            #4unit：13 14 15 16
            #5unit：17 18 19 20
            #6unit：21 22 23 24
            #7unit：25 26 27 28
            #8unit：29 30 31 32
            #manual filament change
            self.Cmds_P1TnManualChangeChannel(int(params["T"]), gcmd)
            #lancaigang240524：use inUIUXdynamic interface


            self.Cmds_MoveToCutFilaAction(gcmd)

            #lancaigang250519:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_CUT_WAITINGAREA")
            command_string = """
                PRZ_CUT_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position；command_string='%s'" % command_string)


            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("AP")
                logging.info("serial port1send command：AP")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AP")
                logging.info("serial port2send command：AP")

            self.G_ProzenToolhead.dwell(0.5)



            #lancaigang240913：delay timeplace/put to outside side/face
            self.G_ProzenToolhead.dwell(6.0)
            #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
            self.Cmds_CutFilaIfNormalCheck()
            if self.G_KlipperIfPaused == True:
                self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P11:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang250805:cutter test
                self.G_CutCheckTest=False
                return



        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+P11:1,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang250805:cutter test
        self.G_CutCheckTest=False

    ####################################
    #Function Name:python
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20241101
    ####################################
    # P12 T?;multi-color cutterlooptesting
    def Cmds_CmdP12(self, gcmd):
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP12]gcmd-None")
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP12]return")
            return
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP12]command='%s'" % (gcmd.get_commandline(),))
        
        #get command parameter
        params = gcmd.get_command_parameters()

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP12]command='%s'；multi-color cutterlooptesting" % (gcmd.get_commandline(),))

        self.G_PhrozenFluiddRespondInfo("command：'%s'" % (gcmd.get_commandline(),))

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+P12:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang231209：manualadjust can no need tube pause
        self.G_KlipperIfPaused=False
        #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
        self.STM32ReprotPauseFlag=0
        self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")

        #lancaigang250805:cutter test
        self.G_CutCheckTest=True
        self.ManualCmdFlag=False



        self.G_PhrozenFluiddRespondInfo("external macro-PG104-get pre-change global variables")
        command_string = """
            PG104
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-PG104-get pre-change global variables；command_string='%s'" % command_string)
        self.IfDoPG102Flag=True


        #lancaigang240510：filament change before，first run/move to wait area
        #lancaigang240306：moved to cut filament code
        #lancaigang240110：wait area zone wait before，first execute external macro，move tospecial fixed/set position performexecute/row wait
        #lancaigang240515：filament change before，first first need to wait area
        self.G_PhrozenFluiddRespondInfo("external macro-PG101-retract")
        command_string = """
            PG101
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position wait purge；command_string='%s'" % command_string)
        self.IfDoPG102Flag=True



        #lancaigang240319：cutcomplete after，first purge/spitresidual toolhead filament，preventcut into pellets
        self.G_PhrozenFluiddRespondInfo("external macro-PG106；cut filament before，first purge/spitresidual toolhead filament，preventcut into pellets")
        self.PG102Flag=True
        logging.info("self.Flag=True")
        command_string = """
        PG106
        """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
        self.PG102Flag=False
        logging.info("self.Flag=False")



        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()


        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("AP")
            logging.info("serial port1send command：AP")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AP")
            logging.info("serial port2send command：AP")

        self.G_ProzenToolhead.dwell(0.5)


        #lancaigang240913：delay timeplace/put to outside side/face
        self.G_ProzenToolhead.dwell(6.0)
        #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
        self.Cmds_CutFilaIfNormalCheck()
        if self.G_KlipperIfPaused == True:
            self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P12:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            #lancaigang250805:cutter test
            self.G_CutCheckTest=False
            return


        #lancaigang231207：
        if self.G_IfInFilaBlockFlag:
            self.G_PhrozenFluiddRespondInfo("load filament jammed filament，first manualP1 E?from toolhead onmaterial tube remove and manualprz_resumeresume")
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P12:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            #lancaigang250805:cutter test
            self.G_CutCheckTest=False
            return


        if "T" in params:
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P12 Tn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=int(params["T"])
            self.G_ChangeChannelTimeoutNewGcmd=gcmd


            self.G_P10SpitNum=1

            #lancaigang241030：generally isP1 C1toP1 C32，range at1to32
            #1unit：1 2 3 4
            #2unit：5 6 7 8
            #3unit：9 10 11 12
            #4unit：13 14 15 16
            #5unit：17 18 19 20
            #6unit：21 22 23 24
            #7unit：25 26 27 28
            #8unit：29 30 31 32
            #manual filament change
            self.Cmds_P1TnManualChangeChannel(int(params["T"]), gcmd)
            #lancaigang240524：use inUIUXdynamic interface


            self.Cmds_MoveToCutFilaAction(gcmd)

            #lancaigang250519:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_CUT_WAITINGAREA")
            command_string = """
                PRZ_CUT_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position；command_string='%s'" % command_string)


            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("AP")
                logging.info("serial port1send command：AP")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AP")
                logging.info("serial port2send command：AP")

            self.G_ProzenToolhead.dwell(0.5)



            #lancaigang240913：delay timeplace/put to outside side/face
            self.G_ProzenToolhead.dwell(6.0)
            #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
            self.Cmds_CutFilaIfNormalCheck()
            if self.G_KlipperIfPaused == True:
                self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P12:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang250805:cutter test
                self.G_CutCheckTest=False
                return



        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+P12:1,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang250805:cutter test
        self.G_CutCheckTest=False



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #'P9 X195.940 Y242.500 W3.010 H41.450 D?'
    #filament change wait area zone handle
    # P9 

    # P9 
    # expire:timeout,unit seconds(default60) 
    # A0:ignore timeout,continue print(default)   A1:timeout afterend stop printset wait timeout and handle
    def Cmds_CmdP9(self, gcmd):
        #get command parameter
        params = gcmd.get_command_parameters()

        if self.G_KlipperIfPaused == True:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP9]klipperpause，but still received command")

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP9]command='%s'" % (gcmd.get_commandline(),))

        #lancaigang20231016：P9aftercontinue parameterXYWH；Xcoordinate；Ycoordinate；Wwait area width；Hwait area height
        #'P9 X195.940 Y242.500 W3.010 H41.450 D0'
        for flag in "XYWH":
            if flag in params:
                self.G_DictChangeChannelWaitAreaParam[flag] = float(params[flag])

        self.G_PhrozenFluiddRespondInfo("command：'%s'" % (gcmd.get_commandline(),))

        #parameterD # D0:by/withXdirectionas slow moveYdirection count number(default) D1:by/withYdirectionas slow moveXdirection count numberset wait area zone
        #'P9 X195.940 Y242.500 W3.010 H41.450 D0'
        if "D" in params:
            direction = int(params["D"])
            self.G_DictChangeChannelWaitAreaParam["D"] = direction

        #lancaigang241031：
        self.G_PhrozenFluiddRespondInfo("P9parameter;self.G_DictChangeChannelWaitAreaParam[D]='%d'" % (self.G_DictChangeChannelWaitAreaParam["D"],))


        #parameterT # expire:timeout,unit seconds(default60) 
        #'P9 X195.940 Y242.500 W3.010 H41.450 D0'
        if "T" in params:
            expire = int(params["T"])
            #lancaigang20231016：change is60seconds
            if expire < 60:
                self.G_PhrozenFluiddRespondInfo("noeffect timeout，must is60seconds inside '%s'" % (gcmd.get_commandline(),))
            self.G_DictChangeChannelWaitAreaParam["T"] = expire
            self.G_PhrozenFluiddRespondInfo("change send command: expire=%d" % expire)

        #parameter A# A0:ignore timeout,continue print(default)   A1:timeout afterend stop printset wait timeout and handle
        #'P9 X195.940 Y242.500 W3.010 H41.450 D0'
        if "A" in params:
            action = int(params["A"])
            if not action in [0, 1]:
                self.G_PhrozenFluiddRespondInfo("noeffect timeout handle，Aparameter must is[0/1] '%s'" % (gcmd.get_commandline(),))
            self.G_DictChangeChannelWaitAreaParam["A"] = action

        # list dataitem not needtool hasmutual same type
        # create alist，only needcommadivide separated dataitem usebracketsinclude together i.e.can。like down allshow：
        # andcharacter string/serial index a appearance，listindex from0start。list can performslice、group combineEtc.
        self.ChangeWaitMoveArea = []
        # default filamentwidthmm；cfgconfig filamentwidth or internaldefault filamentwidth
        Lo_LineWidth = self.G_ChangeChannelWaitLineWidth  
        #wait area zonewidth height/high
        Lo_WaitAreaWidth, Lo_WaitAreaHeight = abs(self.G_DictChangeChannelWaitAreaParam["W"]), abs(self.G_DictChangeChannelWaitAreaParam["H"])
        #wait area zoneXbase point coordinate Ybase point coordinate
        Lo_XBasePosition, Lo_YBasePosition = self.G_DictChangeChannelWaitAreaParam["X"], self.G_DictChangeChannelWaitAreaParam["Y"]
        #lancaigang231216
        self.G_XBasePosition=Lo_XBasePosition
        self.G_YBasePosition=Lo_YBasePosition

        #total move distance
        Lo_TotalMovingDist = (Lo_WaitAreaWidth * Lo_WaitAreaHeight / Lo_LineWidth)
        #each astep size;# step performmm/s
        self.G_WaitAreaEachStepDist = min(Lo_TotalMovingDist / self.G_DictChangeChannelWaitAreaParam["T"], self.G_ChangeChannelWaitMaxMovementSpeed* self.G_MovementSpeedFactor) 

        # D0:by/withXdirectionas slow moveYdirection count number(default) D1:by/withYdirectionas slow moveXdirection count numberset wait area zone
        if self.G_DictChangeChannelWaitAreaParam["D"] == 1:
            Lo_WaitAreaWidth, Lo_WaitAreaHeight = Lo_WaitAreaHeight, Lo_WaitAreaWidth

        if self.G_WaitAreaEachStepDist > Lo_WaitAreaWidth:
             #lancaigang231129：widthexceed out also continue wait filament change continue print
             self.G_PhrozenFluiddRespondInfo("noeffect parameter;cmd='%s', that less than minstep: %.03f"% (gcmd.get_commandline(), self.G_WaitAreaEachStepDist))

        #generate wait area zonerectangle each a step data
        for index, y in enumerate(np.arange(0.0, Lo_WaitAreaHeight, Lo_LineWidth)):
            #
            if len(self.ChangeWaitMoveArea) >= self.G_DictChangeChannelWaitAreaParam["T"]:
                break
            if index % 2 == 0:
                for x in np.arange(0, Lo_WaitAreaWidth, self.G_WaitAreaEachStepDist):
                    if x < Lo_WaitAreaWidth - self.G_WaitAreaEachStepDist / 2:
                        self.ChangeWaitMoveArea.append([x, y, True])
                    else:
                        self.ChangeWaitMoveArea.append([Lo_WaitAreaWidth, y, True])
                        if y + Lo_LineWidth < Lo_WaitAreaHeight:
                            self.ChangeWaitMoveArea.append((Lo_WaitAreaWidth, y + Lo_LineWidth, False))
                        break
            else:
                for x in np.arange(Lo_WaitAreaWidth - self.G_WaitAreaEachStepDist, 0.0, -self.G_WaitAreaEachStepDist):
                    if x > self.G_WaitAreaEachStepDist / 2:
                        self.ChangeWaitMoveArea.append([x, y, True])
                    else:
                        self.ChangeWaitMoveArea.append([0, y, False])
                        break

        # D0:by/withXdirectionas slow moveYdirection count number(default) D1:by/withYdirectionas slow moveXdirection count numberset wait area zone
        if self.G_DictChangeChannelWaitAreaParam["D"] == 1:
            self.ChangeWaitMoveArea = [[y, x, b] for [x, y, b] in self.ChangeWaitMoveArea]

        # Wwidth
        if self.G_DictChangeChannelWaitAreaParam["W"] < 0:
            self.ChangeWaitMoveArea = [[-x, y, b] for [x, y, b] in self.ChangeWaitMoveArea]

        # Hheight/high
        if self.G_DictChangeChannelWaitAreaParam["H"] < 0:
            self.ChangeWaitMoveArea = [[x, -y, b] for [x, y, b] in self.ChangeWaitMoveArea]

        self.ChangeWaitMoveArea = [[x + Lo_XBasePosition, y + Lo_YBasePosition, b] for [x, y, b] in self.ChangeWaitMoveArea]


####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdP0M3P8FA(self, AMSNum,gcmd):
        
        self.G_ProzenToolhead.dwell(2.0)

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP0M3P8FA]command=P8FA" )

        Lo_MCUSTM32Cmd = G_DictPhrozenCmdP8["mcu_cmd"][0]
        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241030:
        if AMSNum==1:
            self.Cmds_AMSSerial1Send("MA")
            self.G_PhrozenFluiddRespondInfo("serial port1sendMA")
        elif AMSNum==2:
            self.Cmds_AMSSerial2Send("MA")
            self.G_PhrozenFluiddRespondInfo("serial port2sendMA")

        #lancaigang240124：stm32active/manual on report，enable can pause1time(s)
        self.STM32ReprotPauseFlag=0


        #lancaigang240123：if toolhead has filament，no need sendFAtostm32，wait toolhead print complete after pause again sendFA，and auto resume
        if self.G_ToolheadIfHaveFilaFlag==False:
            self.G_PhrozenFluiddRespondInfo("toolhead no filament，FA")
            #lancaigang240115:delay2seconds，prevent packet concatenation
            self.G_ProzenToolhead.dwell(2.0)

            #lancaigang241030:
            if AMSNum==1:
                self.Cmds_AMSSerial1Send("FA")
                self.G_PhrozenFluiddRespondInfo("serial port1sendFA")
            elif AMSNum==2:
                self.Cmds_AMSSerial2Send("FA")
                self.G_PhrozenFluiddRespondInfo("serial port2sendFA")

            #lancaigang231229:encapsulated function，wait load filament
            self.Cmds_MARetryInFila(gcmd)
            #lancaigang240108：P8command no need handle resume command
            self.G_M2MAModeResumeFlag=False



        else:#toolhead has filament
            self.G_PhrozenFluiddRespondInfo("toolhead has filament，FB")
            self.G_ProzenToolhead.dwell(2.0)

            #lancaigang241030:
            if AMSNum==1:
                self.Cmds_AMSSerial1Send("FB")
                self.G_PhrozenFluiddRespondInfo("serial port1sendFB")
            elif AMSNum==2:
                self.Cmds_AMSSerial2Send("FB")
                self.G_PhrozenFluiddRespondInfo("serial port2sendFB")

            self.G_M2MAModeResumeFlag=False

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_P8AMS1AutoSelectChannel(self):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P8AMS1AutoSelectChannel]")

        bitmask1=0b0001
        bitmask2=0b0010
        bitmask4=0b0100
        bitmask8=0b1000
        if self.G_AMS1DeviceState["entry_state"] == 0:
            if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                self.Cmds_AMSSerial1Send("T1")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=1
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=1
                self.G_PhrozenFluiddRespondInfo("+T:0,1")
            elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                self.Cmds_AMSSerial1Send("T2")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=2
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=2
                self.G_PhrozenFluiddRespondInfo("+T:0,2")
            elif self.G_AMS1DeviceState["park_state"] & bitmask4 == 4:#0100
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                self.Cmds_AMSSerial1Send("T3")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=3
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=3
                self.G_PhrozenFluiddRespondInfo("+T:0,3")
            elif self.G_AMS1DeviceState["park_state"] & bitmask8 == 8:#1000
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T4")
                self.Cmds_AMSSerial1Send("T4")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=4
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=4
                self.G_PhrozenFluiddRespondInfo("+T:0,4")
            else:
                self.G_PhrozenFluiddRespondInfo("no filament")
        elif self.G_AMS1DeviceState["entry_state"] & bitmask1 == 1:#0001
            self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
            self.Cmds_AMSSerial1Send("T1")
            if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=1
            else:
                self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutNewChan=1
            self.G_PhrozenFluiddRespondInfo("+T:0,1")
        elif self.G_AMS1DeviceState["entry_state"] & bitmask2 == 2:#0010
            if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                self.Cmds_AMSSerial1Send("T1")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=1
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=1
                self.G_PhrozenFluiddRespondInfo("+T:0,1")
            elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                self.Cmds_AMSSerial1Send("T2")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=2
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=2
                self.G_PhrozenFluiddRespondInfo("+T:0,2")
            else:
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                self.Cmds_AMSSerial1Send("T2")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=2
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=2
                self.G_PhrozenFluiddRespondInfo("+T:0,2")
        elif self.G_AMS1DeviceState["entry_state"] & bitmask4 == 4:#0100
            if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                self.Cmds_AMSSerial1Send("T1")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=1
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=1
                self.G_PhrozenFluiddRespondInfo("+T:0,1")
            elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                self.Cmds_AMSSerial1Send("T2")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=2
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=2
                self.G_PhrozenFluiddRespondInfo("+T:0,2")
            elif self.G_AMS1DeviceState["park_state"] & bitmask4 == 4:#0100
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                self.Cmds_AMSSerial1Send("T3")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=3
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=3
                self.G_PhrozenFluiddRespondInfo("+T:0,3")
            else:
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                self.Cmds_AMSSerial1Send("T3")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=3
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=3
                self.G_PhrozenFluiddRespondInfo("+T:0,3")
        elif self.G_AMS1DeviceState["entry_state"] & bitmask8 ==8:#1000
            if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                self.Cmds_AMSSerial1Send("T1")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=1
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=1
                self.G_PhrozenFluiddRespondInfo("+T:0,1")
            elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                self.Cmds_AMSSerial1Send("T2")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=2
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=2
                self.G_PhrozenFluiddRespondInfo("+T:0,2")
            elif self.G_AMS1DeviceState["park_state"] & bitmask4 == 4:#0100
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                self.Cmds_AMSSerial1Send("T3")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=3
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=3
                self.G_PhrozenFluiddRespondInfo("+T:0,3")
            elif self.G_AMS1DeviceState["park_state"] & bitmask8 == 8:#1000
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T4")
                self.Cmds_AMSSerial1Send("T4")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=4
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=4
                self.G_PhrozenFluiddRespondInfo("+T:0,4")
            else:
                self.G_PhrozenFluiddRespondInfo("serial port1change send command: T4")
                self.Cmds_AMSSerial1Send("T4")
                if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                    self.G_ChangeChannelTimeoutOldChan=4
                else:
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_ChangeChannelTimeoutNewChan=4
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+T:0,4")



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P8 execute auto refill Yes；"FA"；
    def Cmds_CmdP8(self,gcmd):
        #lancaigang250522：not allowM3runout detection
        self.G_IfChangeFilaOngoing = True

        self.G_ProzenToolhead.dwell(2.0)

        logging.info("[(cmds.python)Cmds_CmdP8]command=P8" )


        logging.info("current mode")
        self.Device_ReportModeIfChanged()



        Lo_MCUSTM32Cmd = G_DictPhrozenCmdP8["mcu_cmd"][0]


        #lancaigang240511：resume time，all initialize a down serial port，prevent hot-plugAMScauses serial portcommunication abnormal
        try:
            logging.info("[(cmds.python)Cmds_CmdP8]re-initialize serial port1")
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

        try:
            logging.info("[(cmds.py)Cmds_PhrozenKlipperResume]re-initialize serial port2")
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



        #lancaigang241030:
        if self.G_SerialPort1OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("serial port1sendMA")
            self.Cmds_AMSSerial1Send("MA")

        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("serial port2sendMA")
            self.Cmds_AMSSerial2Send("MA")


        #lancaigang240124：stm32active/manual on report，enable can pause1time(s)
        self.STM32ReprotPauseFlag=0



        # lancaigang241105：if power loss restart after，root this not know current toolhead inside filament is whichAMSwhich channel ，so first retract all channel
        #lancaigang231205：not home/reset cut filament retract
        self.Cmds_MoveToCutFilaAndRollback(gcmd)



        if self.G_KlipperIfPaused == True:
            self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
            self.G_PauseToLCDString="+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
            self.G_IfChangeFilaOngoing= False
            return


        #if cut filament normal，thenexcellent firstselectaAMSachannel load filament
        if self.G_KlipperIfPaused == False:
            self.G_ProzenToolhead.dwell(2.0)

            if self.G_SerialPort1OpenFlag == True:
                try:
                    self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                    #get ChromaKit MMU detailed status
                    Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort1SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                    self.G_PhrozenFluiddRespondInfo("ttyserial port1catch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                    if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                        self.G_PhrozenFluiddRespondInfo("AMS1not yetresponse should，please checkAMS")
                        #lancaigang240412:AMSmulti-color flag
                        self.G_AMSDevice1IfNormal=False
                    else:
                        self.G_PhrozenFluiddRespondInfo("AMS1connect success")
                        self.G_PhrozenFluiddRespondInfo("self.G_AMSDevice1IfNormal=True")
                        #lancaigang240412:AMSmulti-color flag
                        self.G_AMSDevice1IfNormal=True

                        Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                        Lo_AMSDeviceStateInfo.whole[:] = bytearray(Lo_AMSDeviceStateRspInfo)
                        #pythonempty dict
                        Lo_AMSDetailState = {}
                        self.G_AMS1DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                        self.G_AMS1DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                        self.G_AMS1DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                        self.G_AMS1DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                        self.G_AMS1DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                        self.G_PhrozenFluiddRespondInfo("buffer sensor full state(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                        self.G_AMS1DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                        self.G_AMS1DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                        self.G_AMS1DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                        self.G_AMS1DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                        self.G_PhrozenFluiddRespondInfo("entry position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                        self.G_AMS1DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                        self.G_PhrozenFluiddRespondInfo("park position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.park_state)
                except:
                    self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")
                


            if self.G_SerialPort2OpenFlag == True:
                try:
                    self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                    Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort2SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                    self.G_PhrozenFluiddRespondInfo("ttyserial port2catch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                    if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                        self.G_PhrozenFluiddRespondInfo("AMS2not yetresponse should，please checkAMS")
                        #lancaigang240412:AMSmulti-color flag
                        self.G_AMSDevice2IfNormal=False
                    else:
                        self.G_PhrozenFluiddRespondInfo("AMS2connect success")
                        self.G_PhrozenFluiddRespondInfo("self.G_AMSDevice2IfNormal=True")
                        #lancaigang240412:AMSmulti-color flag
                        self.G_AMSDevice2IfNormal=True

                        Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                        Lo_AMSDeviceStateInfo.whole[:] = bytearray(Lo_AMSDeviceStateRspInfo)
                        #pythonempty dict
                        Lo_AMSDetailState = {}
                        self.G_AMS2DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                        self.G_AMS2DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                        self.G_AMS2DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                        self.G_AMS2DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                        self.G_AMS2DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                        self.G_PhrozenFluiddRespondInfo("buffer sensor full state(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                        self.G_AMS2DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                        self.G_AMS2DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                        self.G_AMS2DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                        self.G_AMS2DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                        self.G_PhrozenFluiddRespondInfo("entry position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                        self.G_AMS2DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                        self.G_PhrozenFluiddRespondInfo("park position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.park_state)

                except:
                    self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")



        self.G_ProzenToolhead.dwell(2.0)


        if self.G_AMSDevice1IfNormal==True:

            #lancaigang241106:excellent firstaAMSachannel
            if self.G_AMS1DeviceState["entry_state"] > 0 or self.G_AMS1DeviceState["park_state"] > 0:
                self.G_PhrozenFluiddRespondInfo("1AMShas filament")
                #lancaigang250711：ifscreen selectcolor channel，by/with useuser select channelexcellent first；
                # =====M3mode
                if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:#M3 M2
                    self.G_PhrozenFluiddRespondInfo("M3mode single-colormodel/mold type/model，useuser selectmulti-colorsinglechannel print single-colormodel/mold type/model；")
                    if self.G_ChromaKitAccessT0>0:
                        self.Cmds_AMSSerial1Send("T%d" % self.G_ChromaKitAccessT0)
                        logging.info("serial port1send command: T%d" % self.G_ChromaKitAccessT0)
                        if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChromaKitAccessT0
                        else:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=self.G_ChromaKitAccessT0
                    elif self.G_ChromaKitAccessT1>0:
                        self.Cmds_AMSSerial1Send("T%d" % self.G_ChromaKitAccessT1)
                        logging.info("serial port1send command: T%d" % self.G_ChromaKitAccessT1)
                        if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChromaKitAccessT1
                        else:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=self.G_ChromaKitAccessT1
                    elif self.G_ChromaKitAccessT2>0:
                        self.Cmds_AMSSerial1Send("T%d" % self.G_ChromaKitAccessT2)
                        logging.info("serial port1send command: T%d" % self.G_ChromaKitAccessT2)
                        if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChromaKitAccessT2
                        else:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=self.G_ChromaKitAccessT2
                    elif self.G_ChromaKitAccessT3>0:
                        self.Cmds_AMSSerial1Send("T%d" % self.G_ChromaKitAccessT3)
                        logging.info("serial port1send command: T%d" % self.G_ChromaKitAccessT3)
                        if self.G_ChangeChannelTimeoutOldChan<0 or self.G_ChangeChannelTimeoutNewChan<0:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChromaKitAccessT3
                        else:
                            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=self.G_ChromaKitAccessT3
                    else:
                        self.G_PhrozenFluiddRespondInfo("M3mode single-colormodel/mold type/model，useuser withoutselect multi-colorsinglechannel print single-colormodel/mold type/model；autoselect channel print single-colormodel/mold type/model")
                        self.Cmds_P8AMS1AutoSelectChannel()
                else:
                    self.G_PhrozenFluiddRespondInfo("other mode single-colormodel/mold type/model，useuser withoutselect multi-colorsinglechannel print single-colormodel/mold type/model；autoselect channel print single-colormodel/mold type/model")
                    self.Cmds_P8AMS1AutoSelectChannel()
            else:
                self.G_PhrozenFluiddRespondInfo("1AMSno filament")


        if self.G_AMSDevice2IfNormal==True:
            if self.G_AMS2DeviceState["entry_state"]>0:
                self.G_PhrozenFluiddRespondInfo("2AMShas filament")

        self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)

         #lancaigang231229:encapsulated function，wait load filament
        self.Cmds_MARetryInFila(gcmd)

        #lancaigang240108：P8command no need handle resume command
        self.G_M2MAModeResumeFlag=False

####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdP8Infila(self):

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP8Infila]" )

        logging.info("current mode")
        self.Device_ReportModeIfChanged()

        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241030:
        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("MB")
            self.G_PhrozenFluiddRespondInfo("serial port1sendMB")
        elif self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("MB")
            self.G_PhrozenFluiddRespondInfo("serial port2sendMB")

        #lancaigang240124：stm32active/manual on report，enable can pause1time(s)
        self.STM32ReprotPauseFlag=0

        self.G_ProzenToolhead.dwell(2.5)

        if self.G_SerialPort1OpenFlag == True:
            try:
                self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                #get ChromaKit MMU detailed status
                Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort1SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                self.G_PhrozenFluiddRespondInfo("ttyserial port1catch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                    self.G_PhrozenFluiddRespondInfo("AMS1not yetresponse should，please checkAMS")
                    #lancaigang240412:AMSmulti-color flag
                    self.G_AMSDevice1IfNormal=False
                else:
                    self.G_PhrozenFluiddRespondInfo("AMS1connect success")
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDevice1IfNormal=True")
                    #lancaigang240412:AMSmulti-color flag
                    self.G_AMSDevice1IfNormal=True

                    Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                    Lo_AMSDeviceStateInfo.whole[:] = bytearray(Lo_AMSDeviceStateRspInfo)
                    #pythonempty dict
                    Lo_AMSDetailState = {}
                    self.G_AMS1DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                    self.G_AMS1DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                    self.G_AMS1DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                    self.G_AMS1DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                    self.G_AMS1DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                    self.G_PhrozenFluiddRespondInfo("buffer sensor full state(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                    self.G_AMS1DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                    self.G_AMS1DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                    self.G_AMS1DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                    self.G_AMS1DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                    self.G_PhrozenFluiddRespondInfo("entry position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                    self.G_AMS1DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                    self.G_PhrozenFluiddRespondInfo("park position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.park_state)
            except:
                self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")



        if self.G_SerialPort2OpenFlag == True:
            try:
                self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort2SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                self.G_PhrozenFluiddRespondInfo("ttyserial port2catch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                    self.G_PhrozenFluiddRespondInfo("AMS2not yetresponse should，please checkAMS")
                    #lancaigang240412:AMSmulti-color flag
                    self.G_AMSDevice2IfNormal=False
                else:
                    self.G_PhrozenFluiddRespondInfo("AMS2connect success")
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDevice2IfNormal=True")
                    #lancaigang240412:AMSmulti-color flag
                    self.G_AMSDevice2IfNormal=True

                    Lo_AMSDeviceStateInfo = AMSDetailInfoBytes()
                    Lo_AMSDeviceStateInfo.whole[:] = bytearray(Lo_AMSDeviceStateRspInfo)
                    #pythonempty dict
                    Lo_AMSDetailState = {}
                    self.G_AMS2DeviceState["dev_id"] = Lo_AMSDetailState["dev_id"] = Lo_AMSDeviceStateInfo.field.dev_id
                    self.G_AMS2DeviceState["active_dev_id"] = Lo_AMSDetailState["active_dev_id"] = Lo_AMSDeviceStateInfo.field.active_dev_id
                    self.G_AMS2DeviceState["dev_mode"] = Lo_AMSDetailState["dev_mode"] = Lo_AMSDeviceStateInfo.field.dev_mode
                    self.G_AMS2DeviceState["cache_empty"] = Lo_AMSDetailState["cache_empty"] = Lo_AMSDeviceStateInfo.field.cache_empty
                    self.G_AMS2DeviceState["cache_full"] = Lo_AMSDetailState["cache_full"] = Lo_AMSDeviceStateInfo.field.cache_full
                    self.G_PhrozenFluiddRespondInfo("buffer sensor full state(bool)==%d" % Lo_AMSDeviceStateInfo.field.cache_full)
                    self.G_AMS2DeviceState["cache_exist"] = Lo_AMSDetailState["cache_exist"] = Lo_AMSDeviceStateInfo.field.cache_exist
                    self.G_AMS2DeviceState["mc_state"] = Lo_AMSDetailState["mc_state"] = Lo_AMSDeviceStateInfo.field.mc_state
                    self.G_AMS2DeviceState["ma_state"] = Lo_AMSDetailState["ma_state"] = Lo_AMSDeviceStateInfo.field.ma_state
                    self.G_AMS2DeviceState["entry_state"] = Lo_AMSDetailState["entry_state"] = Lo_AMSDeviceStateInfo.field.entry_state
                    self.G_PhrozenFluiddRespondInfo("entry position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.entry_state)
                    self.G_AMS2DeviceState["park_state"] = Lo_AMSDetailState["park_state"] = Lo_AMSDeviceStateInfo.field.park_state
                    self.G_PhrozenFluiddRespondInfo("park position sensor state(bitposition/bit)==%d" % Lo_AMSDeviceStateInfo.field.park_state)
            except:
                self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")
                
        if self.G_AMSDevice1IfNormal==True:
            bitmask1=0b0001
            bitmask2=0b0010
            bitmask4=0b0100
            bitmask8=0b1000
            #lancaigang241106:excellent firstaAMSachannel
            if self.G_AMS1DeviceState["entry_state"] > 0 or self.G_AMS1DeviceState["park_state"] > 0:
                self.G_PhrozenFluiddRespondInfo("1AMShas filament")
                if self.G_AMS1DeviceState["entry_state"] == 0:
                    if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                        self.Cmds_AMSSerial1Send("T1")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=1
                        self.G_PhrozenFluiddRespondInfo("+T:0,1")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                        self.Cmds_AMSSerial1Send("T2")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=2
                        self.G_PhrozenFluiddRespondInfo("+T:0,2")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask4 == 4:#0100
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                        self.Cmds_AMSSerial1Send("T3")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=3
                        self.G_PhrozenFluiddRespondInfo("+T:0,3")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask8 == 8:#1000
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T4")
                        self.Cmds_AMSSerial1Send("T4")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=4
                        self.G_PhrozenFluiddRespondInfo("+T:0,4")
                    else:
                        self.G_PhrozenFluiddRespondInfo("no filament")
                elif self.G_AMS1DeviceState["entry_state"] & bitmask1 == 1:#0001
                    self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                    self.Cmds_AMSSerial1Send("T1")
                    self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                    self.G_ChangeChannelTimeoutNewChan=1
                    self.G_PhrozenFluiddRespondInfo("+T:0,1")
                elif self.G_AMS1DeviceState["entry_state"] & bitmask2 == 2:#0010
                    if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                        self.Cmds_AMSSerial1Send("T1")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=1
                        self.G_PhrozenFluiddRespondInfo("+T:0,1")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                        self.Cmds_AMSSerial1Send("T2")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=2
                        self.G_PhrozenFluiddRespondInfo("+T:0,2")
                    else:
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                        self.Cmds_AMSSerial1Send("T2")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=2
                        self.G_PhrozenFluiddRespondInfo("+T:0,2")
                elif self.G_AMS1DeviceState["entry_state"] & bitmask4 == 4:#0100
                    if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                        self.Cmds_AMSSerial1Send("T1")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=1
                        self.G_PhrozenFluiddRespondInfo("+T:0,1")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                        self.Cmds_AMSSerial1Send("T2")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=2
                        self.G_PhrozenFluiddRespondInfo("+T:0,2")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask4 == 4:#0100
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                        self.Cmds_AMSSerial1Send("T3")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=3
                        self.G_PhrozenFluiddRespondInfo("+T:0,3")
                    else:
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                        self.Cmds_AMSSerial1Send("T3")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=3
                        self.G_PhrozenFluiddRespondInfo("+T:0,3")
                elif self.G_AMS1DeviceState["entry_state"] & bitmask8 ==8:#1000
                    if self.G_AMS1DeviceState["park_state"] & bitmask1 == 1:#0001
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T1")
                        self.Cmds_AMSSerial1Send("T1")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=1
                        self.G_PhrozenFluiddRespondInfo("+T:0,1")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask2 == 2:#0010
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T2")
                        self.Cmds_AMSSerial1Send("T2")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=2
                        self.G_PhrozenFluiddRespondInfo("+T:0,2")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask4 == 4:#0100
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T3")
                        self.Cmds_AMSSerial1Send("T3")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=3
                        self.G_PhrozenFluiddRespondInfo("+T:0,3")
                    elif self.G_AMS1DeviceState["park_state"] & bitmask8 == 8:#1000
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T4")
                        self.Cmds_AMSSerial1Send("T4")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=4
                        self.G_PhrozenFluiddRespondInfo("+T:0,4")
                    else:
                        self.G_PhrozenFluiddRespondInfo("serial port1change send command: T4")
                        self.Cmds_AMSSerial1Send("T4")
                        self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                        self.G_ChangeChannelTimeoutNewChan=4
                        #lancaigang240524：use inUIUXdynamic interface
                        self.G_PhrozenFluiddRespondInfo("+T:0,4")
            else:
                self.G_PhrozenFluiddRespondInfo("1AMSno filament")

        self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)

        if self.G_AMSDevice2IfNormal==True:
            if self.G_AMS2DeviceState["entry_state"]>0:
                self.G_PhrozenFluiddRespondInfo("2AMShas filament")

        #lancaigang240108：P8command no need handle resume command
        self.G_M2MAModeResumeFlag=False


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P4 emergency stop device；emergency stopStopcommand(time(s)excellent firstlevel)："SP"；
    def Cmds_CmdP4(self, gcmd):
        
        self.G_PhrozenFluiddRespondInfo("[(cmds.py)Cmds_CmdP4]command:emergency stop")

        mcu_cmd = G_DictPhrozenCmdP4["mcu_cmd"][0]
        self.G_PhrozenFluiddRespondInfo("mcucommand")



        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            #lancaigang231207：stm32pause
            self.Cmds_AMSSerial1Send(mcu_cmd)
            logging.info("serial port1send command")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send(mcu_cmd)
            logging.info("serial port2send command")

        #lancaigang240125：
        #lancaigang231207：klipperpause+stm32pause
        #klipperactive/manual pause
        

        if self.G_KlipperInPausing == False:
            self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
            #lancaigang250607:
            self.G_PhrozenFluiddRespondInfo("enable quick pause")
            self.G_KlipperQuickPause = True
            #klipperactive/manual pause
            self.Cmds_PhrozenKlipperPause(None)
        else:
            self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P2 A1 all filamentmaterial afterretract to park position printwait position Yes；====="AP";
    # P2 A2；retract out all filament Yes；"CL";
    # P2 A3 cut runoutmaterial
    # P2 A4 cut runoutmaterial and retract filament
    # P2 A7 cut runoutmaterial and retract filament，not detect pause，only use in print completeAMSretract all filament
    def Cmds_CmdP2(self, gcmd):
        
        self.G_PhrozenFluiddRespondInfo("[(cmds.py)Cmds_CmdP2]command='%s'" % (gcmd.get_commandline(),))


        #get command parameter
        params = gcmd.get_command_parameters()


        logging.info("current mode")
        self.Device_ReportModeIfChanged()



        self.G_PhrozenFluiddRespondInfo("delay0.5")
        self.G_ProzenToolhead.dwell(0.5)



        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()



        if "A" in params:
            action = int(params["A"])
            if not action in [1, 2, 3,4,5,6,7]:
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is A[1/2/3/4/5/6/7]" % (gcmd.get_commandline(),))
            # P2 A1 all filamentmaterial afterretract to park position printwait position Yes；====="AP";
            if action == 1:
                #lancaigang250515：standalone mode with multi-color enabled，not handleP2A?
                if self.G_P0M1MCNoneAMS == 1:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]standalone mode with multi-color enabled，not handleP2A?")
                    return
                #lancaigang250427：
                if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]P0M3single-color mode，not handleP2 A1")
                    return
                if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]P0M2MAsingle-color refill mode，not handleP2 A1")
                    return


                self.G_PhrozenFluiddRespondInfo("command='%s'；all filament retract to park position" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A1:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang231201：print complete after，if home/reset，may willcollide to printgood model/mold type/model，cannot home/reset but again need cut filament retract filament
                
                #lancaigang250323：
                if self.G_ToolheadIfHaveFilaFlag==True:
                    #lancaigang231205：home/reset cut filament retract
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament")
                    #lancaigang20231024home/reset cut filament；cannotcollide tomodel/mold type/model
                    #lancaigang240109：toolhead has filament only then allow cut filament
                    #lancaigang240319：preparation before filament cut
                    self.Cmds_MoveToCutFilaAbsolutePositionNotReset(gcmd)
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command: AP；all channel filament retract to park position")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command: AP；all channel filament retract to park position")

                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA-wait area")
                    command_string = """
                        PRZ_WAITINGAREA
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA；command_string='%s'" % command_string)

                    #lancaigang240913：delay timeplace/put to outside side/face
                    self.G_ProzenToolhead.dwell(6.0)

                    #lancaigang231201：check cut filament after isnot normal unload filament，not normal then pause
                    #lancaigang231225：inside delay may causesklipperprint completehominghome/return position/bit abnormal，first disabled
                    #lancaigang240224：need check isnot cut filament success
                    self.Cmds_CutFilaIfNormalCheck()
                else:
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command: AP；all channel filament retract to park position")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command: AP；all channel filament retract to park position")

                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA-wait area")
                    command_string = """
                        PRZ_WAITINGAREA
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA；command_string='%s'" % command_string)



                #lancaigang240113：clear manual commandflag/mark
                self.ManualCmdFlag=False


                # PG28

                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A1:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang250409：hand/manual move entermaterial then readAMSstate
                self.Cmds_CmdP114(None)

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                return



            # P2 A2；retract out all filament Yes；"CL";
            if action == 2:
                #lancaigang250515：standalone mode with multi-color enabled，not handleP2A?
                if self.G_P0M1MCNoneAMS == 1:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]standalone mode with multi-color enabled，not handleP2A?")
                    return
                #lancaigang250427：
                if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]single-color mode，not handleP2 A2")
                    return
                self.G_PhrozenFluiddRespondInfo("command='%s'；all filamentcompletecomplete retract out" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A2:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240319：preparation before filament cut


                if self.G_ToolheadIfHaveFilaFlag:
                    #lancaigang231205：home/reset cut filament retract
                    self.Cmds_MoveToCutFilaAndNotRollback(gcmd)
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament，allAMSfirst retract")
                    #lancaigang241030:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command：AP")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command：AP")

                    self.G_ProzenToolhead.dwell(0.5)

                    #     PG101

                    #lancaigang240913：delay timeplace/put to outside side/face
                    self.G_ProzenToolhead.dwell(6.0)
                    #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                    self.Cmds_CutFilaIfNormalCheck()
                    if self.G_KlipperIfPaused == True:
                            self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                            return



                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()
                #lancaigang241031:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("CL")
                    self.G_PhrozenFluiddRespondInfo("serial port1send command: CL")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("CL")
                    self.G_PhrozenFluiddRespondInfo("serial port2send command: CL")



                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A2:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                return



            # P2 A3 cut runoutmaterial
            if action == 3:
                self.G_PhrozenFluiddRespondInfo("command='%s'；cut filament" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A3:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240319：preparation before filament cut

                self.Cmds_MoveToCutFilaAbsolutePositionNotReset(gcmd)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A3:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                #lancaigang250104：P2A3flag
                self.G_P2A3Flag = 1
                #lancaigang240516：prevent packet concatenation
                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)


            # P2 A4 cut runoutmaterial and retract filament
            if action == 4:
                #lancaigang250515：standalone mode with multi-color enabled，not handleP2A?
                if self.G_P0M1MCNoneAMS == 1:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]standalone mode with multi-color enabled，not handleP2A?")
                    return
                self.G_PhrozenFluiddRespondInfo("command='%s'；cut filament and retract filament to park position" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A4:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240319：preparation before filament cut

                self.Cmds_MoveToCutFilaAbsolutePositionNotReset(gcmd)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A4:1,%d" % self.G_ChangeChannelTimeoutNewChan)



            # P2 A5 print completecut runoutmaterial and retract filament，cannotcollide tomodel/mold type/model
            if action == 5:
                #lancaigang250515：standalone mode with multi-color enabled，not handleP2A?
                if self.G_P0M1MCNoneAMS == 1:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]standalone mode with multi-color enabled，not handleP2A?")
                    return
                self.G_PhrozenFluiddRespondInfo("command='%s'print completecut runoutmaterial and retract filament，cannotcollide tomodel/mold type/model" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A5:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240319：preparation before filament cut

                self.Cmds_MoveToCutFilaAbsolutePositionNotReset(gcmd)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A5:0,%d" % self.G_ChangeChannelTimeoutNewChan)


            # P2 A6 home/reset and cut filament retract
            if action == 6:
                #lancaigang250515：standalone mode with multi-color enabled，not handleP2A?
                if self.G_P0M1MCNoneAMS == 1:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]standalone mode with multi-color enabled，not handleP2A?")
                    return
                self.G_PhrozenFluiddRespondInfo("command='%s'；home/reset and cut filament retract" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A6:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang231201：print complete after，if home/reset，may willcollide to printgood model/mold type/model，cannot home/reset but again need cut filament retract filament
                
                #lancaigang250323：
                if self.G_ToolheadIfHaveFilaFlag==True:
                    #lancaigang231205：home/reset cut filament retract
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament，home/resetXYcut filament and retract")
                    self.Cmds_MoveToCutFilaAndHomingXY(gcmd)
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command: AP；all channel filament retract to park position")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command: AP；all channel filament retract to park position")


                    #lancaigang240913：delay timeplace/put to outside side/face
                    self.G_ProzenToolhead.dwell(6.0)

                    #lancaigang231201：check cut filament after isnot normal unload filament，not normal then pause
                    #lancaigang231225：inside delay may causesklipperprint completehominghome/return position/bit abnormal，first disabled
                    #lancaigang240224：need check isnot cut filament success
                    self.Cmds_CutFilaIfNormalCheck()
                else:
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command: AP；all channel filament retract to park position")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command: AP；all channel filament retract to park position")



                #lancaigang240113：
                self.ManualCmdFlag=True


                # PG28

                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A6:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang250409：hand/manual move entermaterial then readAMSstate

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                return

            # P2 A7 cut runoutmaterial and retract filament，not detect pause，only use in print completeAMSretract all filament
            if action == 7:
                #lancaigang251014：print complete；clear flag；
                self.G_P0M1MCNoneAMS = 0
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A7:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                
                #lancaigang250427：
                if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_UNKNOW:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]P0 M0unknown mode")
                
                #lancaigang250618:single-color and single-color refill runout detectionretract out
                self.G_P0M3Flag = False
                self.G_P0M2MAStartPrintFlag=0

                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()

                #lancaigang250427：
                if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
                    self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP2]P0 M3;single-color mode")

                    
                #lancaigang2521:
                if self.G_SerialPort1OpenFlag == True:
                    try:
                        self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                        #get ChromaKit MMU detailed status
                        Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort1SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                        self.G_PhrozenFluiddRespondInfo("tty1serial portcatch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                        if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                            self.G_PhrozenFluiddRespondInfo("AMS1not yetresponse should，please checkAMS1='%s'" % (gcmd.get_commandline(),))
                            #lancaigang240412:AMSmulti-color flag
                            self.G_AMSDevice1IfNormal=False
                        else:
                            #lancaigang240412:AMSmulti-color flag
                            self.G_AMSDevice1IfNormal=True
                    except:
                        self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")

                if self.G_SerialPort2OpenFlag == True:
                    try:
                        self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                        #get ChromaKit MMU detailed status
                        Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort2SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                        self.G_PhrozenFluiddRespondInfo("tty2serial portcatch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                        if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                            self.G_PhrozenFluiddRespondInfo("AMS2not yetresponse should，please checkAMS2='%s'" % (gcmd.get_commandline(),))
                            self.G_AMSDevice2IfNormal=False
                        else:
                            self.G_AMSDevice2IfNormal=True
                    except:
                        self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")

                #lancaigang241107:
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    self.G_PhrozenFluiddRespondInfo("hasAMSmulti-color，handleP2 A7")
                else:
                    self.G_PhrozenFluiddRespondInfo("withoutAMSmulti-color，not handleP2 A7")
                    #lancaigang250619:checkAMSisnot re-connect success
                    self.Cmds_USBConnectErrorCheck()
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port1send command: M0")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port2send command: M0")
                    
                    #lancaigang240524：use inUIUXdynamic interface
                    self.G_PhrozenFluiddRespondInfo("+P2A7:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                    self.G_PhrozenFluiddRespondInfo("return")
                    return

                self.G_PhrozenFluiddRespondInfo("command='%s'；all filament retract to park position" % (gcmd.get_commandline(),))
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A7:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang231201：print complete after，if home/reset，may willcollide to printgood model/mold type/model，cannot home/reset but again need cut filament retract filament
                
                #lancaigang250323：
                if self.G_ToolheadIfHaveFilaFlag==True:
                    #lancaigang231205：home/reset cut filament retract
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament")
                    #lancaigang20231024home/reset cut filament；cannotcollide tomodel/mold type/model
                    #lancaigang240109：toolhead has filament only then allow cut filament
                    #lancaigang240319：preparation before filament cut
                    self.Cmds_MoveToCutFilaAbsolutePositionNotReset(gcmd)
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("RD")
                        self.G_PhrozenFluiddRespondInfo("serial port1send command: RD；all channel filament retract to park position")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("RD")
                        self.G_PhrozenFluiddRespondInfo("serial port2send command: RD；all channel filament retract to park position")

                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA-wait area")
                    command_string = """
                        PRZ_WAITINGAREA
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA；command_string='%s'" % command_string)

                    self.G_PhrozenFluiddRespondInfo("delay16seconds")
                    self.G_ProzenToolhead.dwell(16)
                    self.G_PhrozenFluiddRespondInfo("delay16seconds")

                    #lancaigang250619:checkAMSisnot re-connect success
                    self.Cmds_USBConnectErrorCheck()
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port1send command: M0")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port2send command: M0")
                else:
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("RD")
                        self.G_PhrozenFluiddRespondInfo("serial port1send command: RD；all channel filament retract to park position")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("RD")
                        self.G_PhrozenFluiddRespondInfo("serial port2send command: RD；all channel filament retract to park position")

                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA-wait area")
                    command_string = """
                        PRZ_WAITINGAREA
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA；command_string='%s'" % command_string)

                    self.G_PhrozenFluiddRespondInfo("delay12seconds")
                    self.G_ProzenToolhead.dwell(12)
                    self.G_PhrozenFluiddRespondInfo("delay12seconds")

                    #lancaigang250619:checkAMSisnot re-connect success
                    self.Cmds_USBConnectErrorCheck()
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port1send command: M0")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port2send command: M0")



                #lancaigang240113：clear manual commandflag/mark
                self.ManualCmdFlag=False


                # PG28

                

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang250409：hand/manual move entermaterial then readAMSstate
                self.Cmds_CmdP114(None)

                self.G_PhrozenFluiddRespondInfo("delay0.5")
                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P2A7:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                return



        #lancaigang240801：P2 B?
        if "B" in params:
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo(gcmd.get_commandline())


        #lancaigang240516：prevent packet concatenation
        self.G_PhrozenFluiddRespondInfo("delay0.5")
        self.G_ProzenToolhead.dwell(0.5)



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P1 S0 all filament load filament to park position；====="RD";
    # P1 T[n]n:1 ~32(device not on network, use1 ~4)manualchange tospecified channel,only filament change(use intesting)；====="T"；
    # P1 B[n]n:1 ~32(device not on network, use1 ~4)specified channel filamentmaterialcompletecomplete retract out Yes；====="B"；
    # P1 D[n]；n:1~32(device not on network, use1~4)；specified channel filamentmaterial afterretract stoppark at park positionstandby state Yes；====="P"；
    # P1 C[n] n:1~32(device not on network, use1~4) autochange tospecified channel(many/more action command,includes cut filament, filament change, wait)；====="T"；
    #lancaigang231202:
    # P1 E[n]；n:1~32(device not on network, use1~4)；specified channel filamentmaterial force before rotate/switch，neednote remove toolhead on material tube Yes；====="E?"；
    # lancaigang240228：toolhead retract a section distance，needstm32first retract a section distance
    # P1 G[n]；n:1~32(device not on network, use1~4)；retract channel filament some distance Yes；====="G?"；
    # lancaigang240319：
    # =====P1 H[n]；n:1~32(device not on network, use1~4)；filament change before retract Yes；====="H?"；
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
    def Cmds_CmdP1(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdP1]command='%s'" % (gcmd.get_commandline(),))

        if self.G_AMSDevice1IfNormal==False and self.G_AMSDevice2IfNormal==False:
            self.G_PhrozenFluiddRespondInfo("withoutAMSmulti-color，allAMSmulti-color not yet connect，not handleP1 ??command")



            #get command parameter
            params = gcmd.get_command_parameters()

            # =====P1 I[n]；manual extrude whenstm32need refill；====="I?"；
            if "I" in params:
                self.G_PhrozenFluiddRespondInfo("AMSmulti-colorP28not yet connect，manual extrude use single-colorM3mode")
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P1In:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                if not int(params["I"]) in range(-1000, 1000):
                    raise gcmd.error("noeffect parameter command;cmd '%s', manual extrude past/overlong" % (gcmd.get_commandline()))

                #lancaigang240705：notthroughAMS，directly usegcodecommand，speedfast
                self.Cmds_P1InExtrudeManualIn(int(params["I"]))


                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P1In:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return
        


        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        #lancaigang240529：phrozeninsert piece/piece/piece/piece/piece version
        self.G_PhrozenFluiddRespondInfo("V-H%s-I%s-F%s-SN1" % (HW_VERSION,IMAGE_VERSION,FW_VERSION))


        #lancaigang231228：preventrandom commands causingstm32 ATcommandpacket concatenation
        #lancaigang240516：preventtime too close


        #lancaigang240105：add a entryATcommand
        self.G_PhrozenFluiddRespondInfo("+P1START:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang20231019：if found toolhead on detect to filament，firstcut runoutmaterial againretract out all thread to park position

        #get command parameter
        params = gcmd.get_command_parameters()


        #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()



        # P1 S0；all filament load filament to park position
        # P1 S1；retract asmall section distance
        if "S" in params:
            self.G_PhrozenFluiddRespondInfo("Cmds_CmdP1]P1 S?")



            #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    logging.info("serial port1send command：MC")
                    self.Cmds_AMSSerial1Send("MC")
                    
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    logging.info("serial port2send command：MC")
                    self.Cmds_AMSSerial2Send("MC")
                    

                self.G_ProzenToolhead.dwell(2)

                

            if self.G_ToolheadIfHaveFilaFlag:
                #lancaigang231205：home/reset cut filament retract
                self.Cmds_MoveToCutFilaAndNotRollback(gcmd)
                self.G_PhrozenFluiddRespondInfo("toolhead has filament，allAMSfirst retract")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AP")
                    logging.info("serial port1send command：AP")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AP")
                    logging.info("serial port2send command：AP")

                self.G_ProzenToolhead.dwell(0.5)

                #     PG101

                #lancaigang240913：delay timeplace/put to outside side/face
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                self.Cmds_CutFilaIfNormalCheck()
                if self.G_KlipperIfPaused == True:
                        self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                        return

                
            self.G_PhrozenFluiddRespondInfo("command='%s'；asmall section distance" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1S:0,%d" % self.G_ChangeChannelTimeoutNewChan)

            #lancaigang231207：
            if self.G_IfInFilaBlockFlag:
                self.G_PhrozenFluiddRespondInfo("load filament jammed filament，first manualP1 E?from toolhead onmaterial tube remove and manualprz_resumeresume")
                self.G_PhrozenFluiddRespondInfo("+P1END:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P1S:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                return

            if int(params["S"])==0:
                #load filament to park position
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("RD")
                    self.G_PhrozenFluiddRespondInfo("serial port1send command：RD")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("RD")
                    self.G_PhrozenFluiddRespondInfo("serial port2send command：RD")

                self.G_PhrozenFluiddRespondInfo("send command=RD；all channel filament load filament to park position")
            if int(params["S"])==1:
                #load filament to park position
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("RB")
                    self.G_PhrozenFluiddRespondInfo("serial port1send command：RB")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("RB")
                    self.G_PhrozenFluiddRespondInfo("serial port2send command：RB")
                self.G_PhrozenFluiddRespondInfo("send command=RB；retract asmall section distance")



            #lancaigang240113：manual commandflag/mark
            self.ManualCmdFlag=True


            #lancaigang231201：check cut filament after isnot normal unload filament，not normal then pause
            #lancaigang240528：disabled not detect cut filament

            self.G_PhrozenFluiddRespondInfo("+P1END:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1S:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return



        #lancaigang20231013：auto filament change
        # P1 C[n] auto filament change
        if "C" in params:
            self.G_PhrozenFluiddRespondInfo("P1 C?")
            logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
            logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

            #lancaigang250515：standalone mode with multi-color enabled，not handleT?
            if self.G_P0M1MCNoneAMS == 1:
                self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT0]standalone mode with multi-color enabled，not handleT?")
                return
            #lancaigang250429：
            if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
                self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT0]single-color mode，not handleT?")
                return
            #lancaigang250514：
            if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
                self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT0]single-color refill mode，not handleT?")
                return

            #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
                self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
                self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    logging.info("serial port1send command：MC")
                    self.Cmds_AMSSerial1Send("MC")
                    
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    logging.info("serial port2send command：MC")
                    self.Cmds_AMSSerial2Send("MC")
                    
            
                self.G_ProzenToolhead.dwell(2)

            #lancaigang250913:causesreturnabnormal
            
            self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
            self.G_PhrozenFluiddRespondInfo("auto filament change")
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Cn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["C"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is C?" % (gcmd.get_commandline()))
            
            #lancaigang240113：clear manual commandflag/mark
            self.ManualCmdFlag=False
            #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0
            self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")
            #lancaigang250517：
            Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
            logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
            logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
            #// current pause status-Lo_PauseStatus='{'is_paused': True}'
            if Lo_PauseStatus['is_paused'] == True:
                logging.info("already in paused state")
            else:
                logging.info("not in paused state")
            #lancaigang240113：clear manual commandflag/mark
            self.ManualCmdFlag=False
            #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0
            self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")

            #lancaigang241030：generally isP1 C1toP1 C32，range at1to32
            #1unit：1 2 3 4
            #2unit：5 6 7 8
            #3unit：9 10 11 12
            #4unit：13 14 15 16
            #5unit：17 18 19 20
            #6unit：21 22 23 24
            #7unit：25 26 27 28
            #8unit：29 30 31 32
            #auto filament change
            chan=int(params["C"])

            if chan==1:
                #lancaigang250515:judge serial portscreen config colormatch pair/to channel
                if self.G_ChromaKitAccessT0 > 0:
                    self.G_PhrozenFluiddRespondInfo("useuser selectmatch match/config channel；self.G_ChromaKitAccessT0=%d" % self.G_ChromaKitAccessT0)
                    self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT0, gcmd)
                else:
                    self.G_PhrozenFluiddRespondInfo("useuser not yetselectmatch match/config channel，default channel；chan=%d" % chan)
                    self.Cmds_P1CnAutoChangeChannel(chan, gcmd)
            elif chan==2:
                #lancaigang250515:judge serial portscreen config colormatch pair/to channel
                if self.G_ChromaKitAccessT1 > 0:
                    self.G_PhrozenFluiddRespondInfo("useuser selectmatch match/config channel；self.G_ChromaKitAccessT1=%d" % self.G_ChromaKitAccessT1)
                    self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT1, gcmd)
                else:
                    self.G_PhrozenFluiddRespondInfo("useuser not yetselectmatch match/config channel，default channel；chan=%d" % chan)
                    self.Cmds_P1CnAutoChangeChannel(chan, gcmd)
            elif chan==3:
                #lancaigang250515:judge serial portscreen config colormatch pair/to channel
                if self.G_ChromaKitAccessT2 > 0:
                    self.G_PhrozenFluiddRespondInfo("useuser selectmatch match/config channel；self.G_ChromaKitAccessT2=%d" % self.G_ChromaKitAccessT2)
                    self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT2, gcmd)
                else:
                    self.G_PhrozenFluiddRespondInfo("useuser not yetselectmatch match/config channel，default channel；chan=%d" % chan)
                    self.Cmds_P1CnAutoChangeChannel(chan, gcmd)
            elif chan==4:
                #lancaigang250515:judge serial portscreen config colormatch pair/to channel
                if self.G_ChromaKitAccessT3 > 0:
                    self.G_PhrozenFluiddRespondInfo("useuser selectmatch match/config channel；self.G_ChromaKitAccessT3=%d" % self.G_ChromaKitAccessT3)
                    self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT3, gcmd)
                else:
                    self.G_PhrozenFluiddRespondInfo("useuser not yetselectmatch match/config channel，default channel；chan=%d" % chan)
                    self.Cmds_P1CnAutoChangeChannel(chan, gcmd)


            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Cn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        #lancaigang20231013：manual filament change
        # P1 T[n] manual filament change
        if "T" in params:
            self.G_PhrozenFluiddRespondInfo("P1 T?")
            #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("MC")
                    logging.info("serial port1send command：MC")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("MC")
                    logging.info("serial port2send command：MC")

                self.G_ProzenToolhead.dwell(2)
            
            self.G_PhrozenFluiddRespondInfo("command='%s'；manual filament change" % (gcmd.get_commandline(),))
            self.G_PhrozenFluiddRespondInfo("manual filament change")
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Tn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["T"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is T?" % (gcmd.get_commandline()))
            
            #lancaigang231209：manualadjust can no need tube pause
            self.G_KlipperIfPaused=False
            #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0
            self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")

            #lancaigang240113：manual commandflag/mark
            self.ManualCmdFlag=True

            #lancaigang231207：
            if self.G_IfInFilaBlockFlag:
                self.G_PhrozenFluiddRespondInfo("load filament jammed filament，first manualP1 E?from toolhead onmaterial tube remove and manualprz_resumeresume")
                self.G_PhrozenFluiddRespondInfo("+P1END:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P1Tn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                return

            #lancaigang231202：not home/reset cut filament not retract
            #lancaigang240319：preparation before filament cut


            if self.G_ToolheadIfHaveFilaFlag:
                #lancaigang231205：home/reset cut filament retract
                self.Cmds_MoveToCutFilaAndNotRollback(gcmd)
                self.G_PhrozenFluiddRespondInfo("toolhead has filament，allAMSfirst retract")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AP")
                    logging.info("serial port1send command：AP")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AP")
                    logging.info("serial port2send command：AP")

                self.G_ProzenToolhead.dwell(0.5)

                #     PG101

                #lancaigang240913：delay timeplace/put to outside side/face
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                self.Cmds_CutFilaIfNormalCheck()
                if self.G_KlipperIfPaused == True:
                    self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                    return



            # PG109



            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=int(params["T"])
            self.G_ChangeChannelTimeoutNewGcmd=gcmd

            #lancaigang241030：generally isP1 C1toP1 C32，range at1to32
            #1unit：1 2 3 4
            #2unit：5 6 7 8
            #3unit：9 10 11 12
            #4unit：13 14 15 16
            #5unit：17 18 19 20
            #6unit：21 22 23 24
            #7unit：25 26 27 28
            #8unit：29 30 31 32
            #manual filament change
            self.Cmds_P1TnManualChangeChannel(int(params["T"]), gcmd)



            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Tn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        # P1 B[n] manualcompletecomplete retractmaterial
        if "B" in params:
            self.G_PhrozenFluiddRespondInfo("P1 B?")
            #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("MC")
                    logging.info("serial port1send command：MC")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("MC")
                    logging.info("serial port2send command：MC")

                self.G_ProzenToolhead.dwell(2)
            
            self.G_PhrozenFluiddRespondInfo("command='%s'；filamentcompletecomplete retract out" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Bn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["B"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is B?" % (gcmd.get_commandline()))
            
            #lancaigang231209：manualadjust can no need tube pause
            self.G_KlipperIfPaused=False
            #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0
            self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")

            #lancaigang240113：manual commandflag/mark
            self.ManualCmdFlag=True

            #lancaigang240319：preparation before filament cut



            if self.G_ToolheadIfHaveFilaFlag==True:
                #lancaigang231205：home/reset cut filament retract
                self.Cmds_MoveToCutFilaAndNotRollback(gcmd)
                self.G_PhrozenFluiddRespondInfo("toolhead has filament，allAMSfirst retract")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AP")
                    logging.info("serial port1send command：AP")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AP")
                    logging.info("serial port2send command：AP")

                self.G_ProzenToolhead.dwell(0.5)

                #     PG101

                #lancaigang240913：delay timeplace/put to outside side/face
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                self.Cmds_CutFilaIfNormalCheck()
                if self.G_KlipperIfPaused == True:
                        self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                        return


            # PG109



            #lancaigang231207：
            if self.G_IfInFilaBlockFlag:
                self.G_PhrozenFluiddRespondInfo("load filament jammed filament，first manualP1 E?from toolhead onmaterial tube remove and manualprz_resumeresume")
                self.G_PhrozenFluiddRespondInfo("+P1END:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P1Bn:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                return

            
            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=int(params["B"])
            self.G_ChangeChannelTimeoutNewGcmd=gcmd


            #manualcompletecomplete retractmaterial
            self.Cmds_P1BnWholeRollbackAction(int(params["B"]), gcmd)

            #lancaigang240115:delay1seconds
            time.sleep(1)
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Bn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        # P1 D[n] manual to park position
        if "D" in params:
            self.G_PhrozenFluiddRespondInfo("P1 D?")
            #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
                self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("MC")
                    logging.info("serial port1send command：MC")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("MC")
                    logging.info("serial port2send command：MC")
                
                self.G_ProzenToolhead.dwell(2)
            
            self.G_PhrozenFluiddRespondInfo("command='%s'；manual to park position" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Dn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["D"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is D?" % (gcmd.get_commandline()))
            
            #lancaigang231209：manualadjust can no need tube pause
            self.G_KlipperIfPaused=False
            #lancaigang240221：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0
            self.G_PhrozenFluiddRespondInfo("self.STM32ReprotPauseFlag=0")

            #lancaigang240113：manual commandflag/mark
            self.ManualCmdFlag=True

            #lancaigang240319：preparation before filament cut



            if self.G_ToolheadIfHaveFilaFlag:
                #lancaigang231205：home/reset cut filament retract
                self.Cmds_MoveToCutFilaAndNotRollback(gcmd)
                self.G_PhrozenFluiddRespondInfo("toolhead has filament，allAMSfirst retract")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AP")
                    logging.info("serial port1send command：AP")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AP")
                    logging.info("serial port2send command：AP")

                self.G_ProzenToolhead.dwell(0.5)

                #     PG101

                #lancaigang240913：delay timeplace/put to outside side/face
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                self.Cmds_CutFilaIfNormalCheck()
                if self.G_KlipperIfPaused == True:
                        self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                        return


            # PG109

            #lancaigang231207：
            if self.G_IfInFilaBlockFlag:
                self.G_PhrozenFluiddRespondInfo("load filament jammed filament，first manualP1 E?from toolhead onmaterial tube remove and manualprz_resumeresume")
                self.G_PhrozenFluiddRespondInfo("+P1END:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+P1Dn:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                return


            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=int(params["D"])
            self.G_ChangeChannelTimeoutNewGcmd=gcmd

            #manual to park position
            self.Cmds_P1DnMoveToParkPositonAction(int(params["D"]), gcmd)

            #lancaigang240115:delay1seconds
            time.sleep(1)

            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Dn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        #lancaigang231202：force before rotate/switch motor，remove toolheadmaterial tubetake out jammaterial
        # P1 E[n]
        if "E" in params:
            self.G_PhrozenFluiddRespondInfo("P1 E?")
            
            self.G_PhrozenFluiddRespondInfo("command='%s'；force before rotate/switch motor，remove toolheadmaterial tubetake out jammaterial" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1En:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["E"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is E?" % (gcmd.get_commandline()))
            
            #lancaigang231202：not home/reset cut filament not retract
            #lancaigang231214：toolhead force remove filament，no need auto cut filament，needhand/manual work cut filament

            #lancaigang240603：prevent packet concatenation

            #manual to park position
            self.Cmds_P1EnForceForward(int(params["E"]), gcmd)

            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1En:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        # lancaigang240228：toolhead retract a section distance，needstm32first retract a section distance
        # P1 G[n]；n:1~32(device not on network, use1~4)；retract channel filament some distance Yes；====="G?"；
        if "G" in params:
            self.G_PhrozenFluiddRespondInfo("P1 G?")
            
            self.G_PhrozenFluiddRespondInfo("command='%s'AMSforce first retract a section distance" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Gn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["G"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is G?" % (gcmd.get_commandline()))
            

            if self.G_ToolheadIfHaveFilaFlag:
                #lancaigang231205：home/reset cut filament retract
                self.Cmds_MoveToCutFilaAndNotRollback(gcmd)
                self.G_PhrozenFluiddRespondInfo("toolhead has filament，allAMSfirst retract")
                #lancaigang241030:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AP")
                    logging.info("serial port1send command：AP")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AP")
                    logging.info("serial port2send command：AP")

                self.G_ProzenToolhead.dwell(0.5)

                #     PG101

                #lancaigang240913：delay timeplace/put to outside side/face
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                self.Cmds_CutFilaIfNormalCheck()
                if self.G_KlipperIfPaused == True:
                        self.G_PhrozenFluiddRespondInfo("cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                        return

            

            # PG109



            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=int(params["G"])
            self.G_ChangeChannelTimeoutNewGcmd=gcmd

            self.Cmds_P1GnExtruderBack(int(params["G"]), gcmd)

            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Gn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        if "H" in params:
            self.G_PhrozenFluiddRespondInfo("P1 H?")
            
            self.G_PhrozenFluiddRespondInfo("command='%s'special refill" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Hn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["H"]) in range(1, AMS_MAX_CHANNEL + 1):
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is H?" % (gcmd.get_commandline()))
            
            

            self.Cmds_P1HnSpecialInfila(int(params["H"]), gcmd)


            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Hn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        # =====P1 I[n]；manual extrude whenstm32need refill；====="I?"；
        if "I" in params:
            self.G_PhrozenFluiddRespondInfo("P1 I?")
            
            self.G_PhrozenFluiddRespondInfo("command='%s'manual extrude whenstm32need refill" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1In:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["I"]) in range(-1000, 1000):
                raise gcmd.error("noeffect parameter command;cmd '%s', manual extrude past/overlong" % (gcmd.get_commandline()))
            
            

            self.Cmds_P1InExtruderBack(int(params["I"]), gcmd)


            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1In:1,%d" % self.G_ChangeChannelTimeoutNewChan)


        # =====P1 J[n]；multi-color manual purge；refill when buffer not full；
        if "J" in params:
            self.G_PhrozenFluiddRespondInfo("P1 J?")

            self.G_PhrozenFluiddRespondInfo("command='%s'manual extrude whenstm32need refill" % (gcmd.get_commandline(),))
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Jn:0,%d" % self.G_ChangeChannelTimeoutNewChan)
            if not int(params["J"]) in range(-1000, 1000):
                raise gcmd.error("noeffect parameter command;cmd '%s', manual extrude parameter abnormal" % (gcmd.get_commandline()))
            
            

            self.Cmds_P1JnManualSpitFila(int(params["J"]), gcmd)


            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+P1Jn:1,%d" % self.G_ChangeChannelTimeoutNewChan)



        #lancaigang240105：command after add a entry completeATcommand
        self.G_PhrozenFluiddRespondInfo("+P1END:0,%d" % self.G_ChangeChannelTimeoutNewChan)
    


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # P0 M1；multi-color mode mode(need connect external device) Yes；"MC";P0 M1;P28;P2 A1;
    # P0 M2；multi-color in single-color refill mode(need connect external device)；"MA";P0 M2;P28;P8;
    # P0 M3; single-color runout mode;P0 M3;
    #lancaigang240801:
    # P0 B?
    def Cmds_CmdP0(self, gcmd):
        params = gcmd.get_command_parameters()

        # LED queries from voronFDM are high-frequency - only log to file
        cmdline = gcmd.get_commandline()
        if "LED_" in cmdline:
            logging.debug("P0: %s", cmdline)
        else:
            logging.info("P0: %s", cmdline)

        #unlock
        self.Base_AMSSerialCmdUnlock()



        #lancaigang240801：P2 M?
        if "M" in params:
            #lancaigang250522：clearAMSconnect
            self.G_AMSDevice1IfNormal=False
            self.G_AMSDevice2IfNormal=False

            #lancaigang250526：
            self.G_IfToolheadHaveFilaInitiativePauseFlag=False
            #lancaigang250526：pausing，not allow new gcodecommand，need wait pause complete
            self.G_KlipperInPausing = False
            #lancaigang250527：quick pause execution
            self.G_KlipperQuickPause = False
            #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
            self.G_KlipperPrintStatus= -1
            self.G_ASM1DisconnectErrorCount=0
            #lancaigang250812:single-color runout detection，supplement carriage return to pause area
            self.G_RetryToPauseAreaFlag = False
            self.G_RetryToPauseAreaCount = 0
            self.G_P10SpitNum=0
            self.G_IfChangeFilaOngoing= False
            #lancaigang240223：toolhead cut failure flag
            self.ToolheadCutFlag = False



            #lancaigang250618：single-colorM3runout detection
            self.G_P0M3Flag = False
            #lancaigang250618：single-color refillM2runout detection
            self.G_P0M2MAStartPrintFlag = 0
            self.ManualCmdFlag=False
            #lancaigang250805:cutter test
            self.G_CutCheckTest=False


            #lancaigang250515:clear LCD screen config data
            self.Cmds_GetUartScreenCfgClear()

            #lancaigang250514：Reading JSON config file，get single-color refill config and channel filament colormatch/config pair/to
            #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json
            self.Cmds_GetUartScreenCfg()
            
            logging.info("current mode")
            self.Device_ReportModeIfChanged()


            self.G_PhrozenFluiddRespondInfo("delay1")
            self.G_ProzenToolhead.dwell(1)

            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()


            #lancaigang250517：
            #lancaigang250517：
            Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
            logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
            self.G_PhrozenPrinterCancelPauseResume.cmd_CLEAR_PAUSE(None)
            self.G_PhrozenFluiddRespondInfo("clear pause state")
            Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
            logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
            logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
            #// current pause status-Lo_PauseStatus='{'is_paused': True}'
            if Lo_PauseStatus['is_paused'] == True:
                logging.info("already in paused state")
            else:
                logging.info("not in paused state")
            #lancaigang240511：initialize a down serial port，prevent hot-plugAMScauses serial portcommunication abnormal
            try:
                logging.info("re-initialize serial port1")
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

            try:
                logging.info("re-initialize serial port2")
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



            #lancaigang250323：
            self.G_PhrozenFluiddRespondInfo("external macro-PG103-get toolheadhotend temperature；global")
            command_string = """
                PG103
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro-PG103；command_string='%s'" % command_string)



            #get command mode parameter
            Lo_AMSWorkMode = int(params["M"])

            if not Lo_AMSWorkMode in [
                AMS_WORK_MODE_UNKNOW,#unknown mode 0
                AMS_WORK_MODE_MC,#MCmode 1
                AMS_WORK_MODE_MA,#single-colorMAmode 2
                AMS_WORK_MODE_FILA_RUNOUT,#runout handle mode 3
            ]:
                raise gcmd.error("noeffect parameter command;cmd '%s', that must is M[0/1/2/3]" % (gcmd.get_commandline(),))
            


            self.G_AMSDeviceWorkMode = Lo_AMSWorkMode
            self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)


        
            logging.info("current mode")
            self.Device_ReportModeIfChanged()



            #lancaigang240410：
            self.G_CancelFlag=False
            #lancaigang240413：pause state
            self.G_KlipperIfPaused = False
            #lancaigang240413：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0

            #lancaigang250515：
            self.G_P0M1MCNoneAMS=0
            logging.info("self.G_P0M1MCNoneAMS=0")


            self.G_PhrozenFluiddRespondInfo("delay1")
            self.G_ProzenToolhead.dwell(1)


            #=====M0;unknown mode
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#0
                self.G_ToolheadFirstInputFila = False
                self.G_PhrozenFluiddRespondInfo("P0 M0unknown mode")

                #lancaigang240411：if without receivedP0 M3command，not use runout detection mechanism
                self.G_P0M3Flag = False
                
                self.G_P0M1MCNoneAMS=0
                logging.info("self.G_P0M1MCNoneAMS=0")


                #lancaigang250327：perform enter multi-color filament change before，not allowAMSmulti-color pause
                self.ManualCmdFlag=True
                self.G_PhrozenFluiddRespondInfo("self.ManualCmdFlag=True")

                #lancaigang250104：P2A3flag
                if self.G_P2A3Flag == 1:
                    self.G_P2A3Flag = 0
                    #lancaigang240416:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AT+IDLE")
                        logging.info("serial port1send command：AT+IDLE")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AT+IDLE")
                        logging.info("serial port2send command：AT+IDLE")
                
                else:
                    #lancaigang240416:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port1send command：M0")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("M0")
                        self.G_PhrozenFluiddRespondInfo("serial port2send command：M0")

                self.G_ProzenToolhead.dwell(0.5)

            #=====M1;multi-color mode
            #P0 M1
            #P28
            #P2 A1
            #T?
            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:  #1
                self.G_PhrozenFluiddRespondInfo("P0 M1multi-color mode: MC")

                #lancaigang250520：notallow allow hand/manual move
                self.ManualCmdFlag=False

                #lancaigang250304：each time(s)P0M1initialize multi-color channel，prevent record channelnumber causes retract abnormal
                self.G_ChangeChannelTimeoutOldChan=-1
                self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutOldChan=-1")
                self.G_ChangeChannelTimeoutOldGcmd=None
                self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutOldGcmd=None")
                self.G_ChangeChannelTimeoutNewChan=-1
                self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=-1")
                self.G_ChangeChannelTimeoutNewGcmd=None
                self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewGcmd=None")


                #lancaigang250102：print filament change count calculation
                self.G_PrintCountNum=0

                #lancaigang240125：no needP28connect also can first home/reset cut filament
                #lancaigang231219：home/reset cut filament not retract
                #lancaigang240319：PG28home/reset toomany/more will causes coordinate abnormal


                #lancaigang240416:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("MC")
                    logging.info("serial port1send command：MC")

                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("MC")
                    logging.info("serial port2send command：MC")



                self.G_ChangeChannelFirstFilaFlag = True


                self.G_ProzenToolhead.dwell(2.5)


                self.G_PhrozenFluiddRespondInfo("check isnot hasAMS")

                if self.G_SerialPort1OpenFlag == True:
                    try:
                        self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                        #get ChromaKit MMU detailed status
                        Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort1SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                        self.G_PhrozenFluiddRespondInfo("tty1serial portcatch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                        if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                            self.G_PhrozenFluiddRespondInfo("AMS1not yetresponse should，please checkAMS1='%s'" % (gcmd.get_commandline(),))
                            #lancaigang240412:AMSmulti-color flag
                            self.G_AMSDevice1IfNormal=False
                        else:
                            #lancaigang240412:AMSmulti-color flag
                            self.G_AMSDevice1IfNormal=True
                    except:
                        self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")

                if self.G_SerialPort2OpenFlag == True:
                    try:
                        self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                        #get ChromaKit MMU detailed status
                        Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort2SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                        self.G_PhrozenFluiddRespondInfo("tty2serial portcatch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                        if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                            self.G_PhrozenFluiddRespondInfo("AMS2not yetresponse should，please checkAMS2='%s'" % (gcmd.get_commandline(),))
                            self.G_AMSDevice2IfNormal=False
                        else:
                            self.G_AMSDevice2IfNormal=True
                    except:
                        self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")



                self.G_ProzenToolhead.dwell(1.0)



                #lancaigang250515:P0 M1multi-colormodel/mold type/model，need compatible not yetcatch/connectAMShandle
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open multi-colormodel/mold type/modelP0 M1，hasAMS")
                    self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open multi-colormodel/mold type/modelP0 M1，executeP2 A1")
                    self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open multi-colormodel/mold type/modelP0 M1，executeT?")
                    #lancaigang250722：multi-color auto refill；
                    if self.G_AutoReplaceState == 1:
                        self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open multi-colormodel/mold type/model auto refill;P0 M1auto rotate/switchchange isP0 M2，enable refill detect")
                        self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MA


                        self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)
                        self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MA")
                        self.G_PhrozenFluiddRespondInfo("P8")
                        #lancaigang241106：
                        self.Cmds_CmdP8(gcmd)

                        if self.G_ToolheadIfHaveFilaFlag:
                            #lancaigang250607:
                            self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                            self.G_KlipperQuickPause = True
                            #lancaigang251120：perform enter purge，add flag，preventPG108purge process in toolheadHall without filament pause，causes pause position at purge area，resume would crash into the purge bin;
                            self.G_PG108Ingoing=1
                            command_string = """
                            PG108
                            """
                            self.G_PhrozenGCode.run_script_from_command(command_string)
                            self.G_PG108Ingoing=0
                            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                            self.G_PhrozenFluiddRespondInfo("purge complete，toolhead detected filament，print")

                    else:
                        self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open multi-colormodel/mold type/model")
                else:
                    self.G_PhrozenFluiddRespondInfo("=====single-colorhit/open multi-colormodel/mold type/modelP0 M1，withoutAMS，executeP0 M3single-color print，disabledP2 A1andT?")
                    self.G_PhrozenFluiddRespondInfo("=====P0 M1rotate/switchchange isP0 M3")
                    self.G_AMSDeviceWorkMode = AMS_WORK_MODE_FILA_RUNOUT
                    self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)
                    self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode = AMS_WORK_MODE_FILA_RUNOUT")
                    self.G_P0M1MCNoneAMS=1
                    self.G_PhrozenFluiddRespondInfo("self.G_P0M1MCNoneAMS=1")
                    #lancaigang240411：use runout detection mechanism
                    self.G_P0M3Flag = True
                    self.G_PhrozenFluiddRespondInfo("self.G_P0M3Flag = True")
                    if self.G_AutoReplaceState == 1:
                        self.G_PhrozenFluiddRespondInfo("=====single-colorhit/open multi-colormodel/mold type/model auto refill;")
                    else:
                        self.G_PhrozenFluiddRespondInfo("=====single-colorhit/open multi-colormodel/mold type/model")

                    logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                    #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                    if Lo_PauseStatus['is_paused'] == True:
                        logging.info("already in paused state")
                    else:
                        logging.info("not in paused state")

                    if self.G_ToolheadIfHaveFilaFlag==True:
                        self.G_PhrozenFluiddRespondInfo("detect to filament，start print")
                        #lancaigang240412：if has multi-colorAMS，then executeMAsingle-color refill
                        #lancaigang241030:many/more unitAMS，press/by sequenceexcellent first from1unit start，only canselect1unit
                        if self.G_AMSDevice1IfNormal==True:
                            self.G_PhrozenFluiddRespondInfo("detect to filament，AMS1multi-color connect，pleaseexcellent first use multi-colorAMS1 filament")
                            self.G_ChangeChannelFirstFilaFlag = True
                        elif self.G_AMSDevice2IfNormal==True:
                            self.G_PhrozenFluiddRespondInfo("detect to filament，AMS2multi-color connect，pleaseexcellent first use multi-colorAMS2 filament")
                            self.G_ChangeChannelFirstFilaFlag = True
                        else:
                            self.G_PhrozenFluiddRespondInfo("detect to filament，AMSmulti-color not yet connect，please manualplace/put perform filament")
                            #lancaigang240411：use runout detection mechanism
                            self.G_P0M3Flag = True
                            #lancaigang240415：toolhead has filament，a time(s)no need purge
                            self.G_P0M3ToolheadHaveFilaNotSpittingFlag = True
                        #lancaigang251120：perform enter purge，add flag，preventPG108purge process in toolheadHall without filament pause，causes pause position at purge area，resume would crash into the purge bin;
                        self.G_PG108Ingoing=1
                        command_string = """
                        PG108
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                        self.G_PhrozenFluiddRespondInfo("purge complete，toolhead detected filament，print")

                    else:
                        self.G_PhrozenFluiddRespondInfo("not yet detect to filament，pause")
                        #lancaigang240407：calibrate before cannot pause
                        self.Cmds_PhrozenKlipperPauseM2M3NoneCmdToSTM32(None)
                        #lancaigang240411：use runout detection mechanism
                        self.G_P0M3Flag = True
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                self.G_ProzenToolhead.dwell(0.5)



            #=====M2;multi-color in single-color auto refill mode
            #P0 M2
            #P28
            #P8
            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:  #2
                self.G_PhrozenFluiddRespondInfo("=====P0 M2single-color refill mode: MA")

                #lancaigang250520：notallow allow hand/manual move
                self.ManualCmdFlag=False


                #lancaigang250102：print filament change count calculation
                self.G_PrintCountNum=0

                #lancaigang240416:
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("MA")
                    self.G_PhrozenFluiddRespondInfo("serial port1send command：MA")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("MA")
                    self.G_PhrozenFluiddRespondInfo("serial port2send command：MA")
    
                self.G_ChangeChannelFirstFilaFlag = True



                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang240104：single-colorM2MArefill mode cannot cut filament
                #lancaigang20231219：home/reset cut filament retract


            #=====M3;single-color runout detection mode
            #lancaigang250511：ifstore atAMSmulti-color，then autostart use auto refill mode；P0 M3rotate/switchchange isP0 M2
            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:#3
                self.G_PhrozenFluiddRespondInfo("P0 M3single-color wait filament")

                #lancaigang250520：notallow allow hand/manual move
                self.ManualCmdFlag=False

                #lancaigang250102：print filament change count calculation
                self.G_PrintCountNum=0

                if self.G_SerialPort1OpenFlag == True:
                    try:
                        self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                        #get ChromaKit MMU detailed status
                        Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort1SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                        self.G_PhrozenFluiddRespondInfo("tty1serial portcatch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                        if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                            self.G_PhrozenFluiddRespondInfo("AMS1not yetresponse should，please checkAMS1='%s'" % (gcmd.get_commandline(),))
                            #lancaigang240412:AMSmulti-color flag
                            self.G_AMSDevice1IfNormal=False
                        else:
                            #lancaigang240412:AMSmulti-color flag
                            self.G_AMSDevice1IfNormal=True
                    except:
                        self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")



                if self.G_SerialPort2OpenFlag == True:
                    try:
                        self.G_PhrozenFluiddRespondInfo("try;Lo_AMSDeviceStateRspInfo")
                        #get ChromaKit MMU detailed status
                        Lo_AMSDeviceStateRspInfo = self.Cmds_AMSSerialPort2SendWaitRsp("SD", sizeof(AMSDetailInfoBytes))
                        self.G_PhrozenFluiddRespondInfo("tty2serial portcatch/connect receive: %s" % Lo_AMSDeviceStateRspInfo)
                        if len(Lo_AMSDeviceStateRspInfo) != sizeof(AMSDetailInfoBytes):
                            self.G_PhrozenFluiddRespondInfo("AMS2not yetresponse should，please checkAMS2='%s'" % (gcmd.get_commandline(),))
                            self.G_AMSDevice2IfNormal=False
                        else:
                            self.G_AMSDevice2IfNormal=True
                    except:
                        self.G_PhrozenFluiddRespondInfo("except;Lo_AMSDeviceStateRspInfo")
                        


                #lancaigang241107:
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    #lancaigang241106：
                    self.G_P0M2MAStartPrintFlag=0

                    #lancaigang250104：prevent serial port abnormal


                    self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open single-colormodel/mold type/modelP0 M3")
                    self.G_PhrozenFluiddRespondInfo("self.G_AutoReplaceState=%d" % self.G_AutoReplaceState)



                    #lancaigang250514:if enable single-color auto refill，thenP0 M3rotate/switchchange isP0 M2
                    if self.G_AutoReplaceState == 1:
                        #lancaigang250511：if hasAMSmulti-color，rotate/switchchange is single-color auto refill mode
                        #P0 M2
                        #P8
                        self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open single-colormodel/mold type/model auto refill;P0 M3auto rotate/switchchange isP0 M2，enable refill detect")
                        self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MA
                        self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)
                        self.G_PhrozenFluiddRespondInfo("self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MA")
                        self.G_PhrozenFluiddRespondInfo("P8")
                        #lancaigang241106：
                        self.Cmds_CmdP8(gcmd)

                        if self.G_ToolheadIfHaveFilaFlag:
                            #lancaigang250607:
                            self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                            self.G_KlipperQuickPause = True

                    else:
                        self.G_PhrozenFluiddRespondInfo("=====multi-colorhit/open single-colorP0 M3，enable runout detection")
                        self.G_PhrozenFluiddRespondInfo("P8")
                        #lancaigang241106：
                        self.Cmds_CmdP8(gcmd)
                        if self.G_ToolheadIfHaveFilaFlag:
                            #lancaigang250607:
                            self.G_PhrozenFluiddRespondInfo("can resume，STM32print in fast error report")
                            self.G_KlipperQuickPause = True
                        #lancaigang240411：use runout detection mechanism
                        self.G_P0M3Flag = True
                        self.G_PhrozenFluiddRespondInfo("self.G_P0M3Flag = True")


                    #lancaigang241106:toolhead success load filament
                    if self.G_P0M2MAStartPrintFlag==1:
                        self.G_PhrozenFluiddRespondInfo("toolhead has filament")
                    else:
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament")
                else:
                    self.G_PhrozenFluiddRespondInfo("=====single-colorhit/open single-colormodel/mold type/modelP0 M3")
                    self.G_PhrozenFluiddRespondInfo("self.G_AutoReplaceState=%d" % self.G_AutoReplaceState)


                #lancaigang231220：has filament can only print
                for i in range(10):#
                    self.G_ProzenToolhead.dwell(1.0)
                    self.G_PhrozenFluiddRespondInfo("wait manualplace/put filament；i=%d" % (i))

                    if self.G_ToolheadIfHaveFilaFlag==True:
                        self.G_PhrozenFluiddRespondInfo("detect to filament，start print")

                        #lancaigang240412：if has multi-colorAMS，then executeMAsingle-color refill
                        #lancaigang241030:many/more unitAMS，press/by sequenceexcellent first from1unit start，only canselect1unit
                        if self.G_AMSDevice1IfNormal==True:
                            self.G_PhrozenFluiddRespondInfo("detect to filament，AMS1multi-color connect，pleaseexcellent first use multi-colorAMS1 filament")
                            self.G_ChangeChannelFirstFilaFlag = True
                        elif self.G_AMSDevice2IfNormal==True:
                            self.G_PhrozenFluiddRespondInfo("detect to filament，AMS2multi-color connect，pleaseexcellent first use multi-colorAMS2 filament")
                            self.G_ChangeChannelFirstFilaFlag = True
                        else:
                            self.G_PhrozenFluiddRespondInfo("detect to filament，AMSmulti-color not yet connect，please manualplace/put perform filament")
                            #lancaigang240411：use runout detection mechanism
                            self.G_P0M3Flag = True
                            #lancaigang240415：toolhead has filament，a time(s)no need purge
                            self.G_P0M3ToolheadHaveFilaNotSpittingFlag = True

                        #lancaigang251120：perform enter purge，add flag，preventPG108purge process in toolheadHall without filament pause，causes pause position at purge area，resume would crash into the purge bin;
                        self.G_PG108Ingoing=1
                        command_string = """
                        PG108
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                        self.G_PhrozenFluiddRespondInfo("purge complete，toolhead detected filament，print")
                        self.G_PG108Ingoing=0
                        break
                    if i>=9:
                        #lancaigang240412：if has multi-colorAMS，then executeMAsingle-color refill
                        if self.G_AMSDevice1IfNormal==True:
                            self.G_PhrozenFluiddRespondInfo("AMS1multi-color connect，pleaseexcellent first use multi-colorAMS1 filament")
                            self.G_ChangeChannelFirstFilaFlag = True
                        elif self.G_AMSDevice2IfNormal==True:
                            self.G_PhrozenFluiddRespondInfo("AMS2multi-color connect，pleaseexcellent first use multi-colorAMS2 filament")
                            self.G_ChangeChannelFirstFilaFlag = True
                        else:
                            self.G_PhrozenFluiddRespondInfo("AMSmulti-color not yet connect，please manualplace/put perform filament")
                            self.G_PhrozenFluiddRespondInfo("wait filament load filament timeout;pause")
                            

                            logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                            #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                            if Lo_PauseStatus['is_paused'] == True:
                                logging.info("already in paused state")
                            else:
                                logging.info("not in paused state")
                            
                                #lancaigang240407：calibrate before cannot pause
                                self.Cmds_PhrozenKlipperPauseM2M3NoneCmdToSTM32(None)
                                #lancaigang240411：use runout detection mechanism
                                self.G_P0M3Flag = True

                                self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                            return
                        
                self.G_ProzenToolhead.dwell(0.5)

            self.G_PhrozenFluiddRespondInfo("delay0.5")
            #lancaigang231228：preventrandom commands causingstm32 ATcommandpacket concatenation
            self.G_ProzenToolhead.dwell(0.5)


        #lancaigang240801：P0 B?
        if "B" in params:
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo(gcmd.get_commandline())



