import logging
import time
from .base import *


class OrcaMixin:
    """Mixin for Orca slicer T-command tool change operations."""

    def Cmds_CmdOrcaPre(self):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdOrcaPre]orcabeforeset action" )

        #lancaigang250912：testingmany/more toolhead；first tospecified coordinate top/push open/enableinsertpin，then triggersendGPIOimplementmany/more toolhead positivereverse rotate/switch，many/more toolhead positivereverse rotate/switch toposition/bit haslight electric and motorcontrol

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdOrcaPre]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            #self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)

            return
        
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdOrcaPre]single-color mode，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            #self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdOrcaPre]single-color refill mode，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            #self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")
        
            self.G_ProzenToolhead.dwell(2)



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT0(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT0 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT1]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT1]single-color mode，not handleT0")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT1]single-color refill mode，not handleT0")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)


        #lancaigang250912:
        #self.Cmds_CmdOrcaPre()

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T0:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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
        chan=0+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)

        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT0 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT0=%d" % self.G_ChromaKitAccessT0)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT0, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T0:1,%d" % self.G_ChangeChannelTimeoutNewChan)


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT1(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT1 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT1]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT1]single-color mode，not handleT1")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT1]single-color refill mode，not handleT1")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)
        
        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()



        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T1:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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
        chan=1+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)

        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT1 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT1=%d" % self.G_ChromaKitAccessT1)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT1, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T1:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT2(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT2 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT2]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT2]single-color mode，not handleT2")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT2]single-color refill mode，not handleT2")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T2:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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
        chan=2+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT2 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT2=%d" % self.G_ChromaKitAccessT2)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT2, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T2:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT3(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT3 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)


        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT3]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT3]single-color mode，not handleT3")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT3]single-color refill mode，not handleT3")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:
        #self.Cmds_CmdOrcaPre()

        
        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T3:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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
        chan=3+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT3 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT3=%d" % self.G_ChromaKitAccessT3)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT3, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T3:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT4(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT4 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT4]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT4]single-color mode，not handleT4")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT4]single-color refill mode，not handleT4")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        
        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T4:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：withouttwoAMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has2AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without2AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T4:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return

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
        chan=4+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT4 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT4=%d" % self.G_ChromaKitAccessT4)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT4, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T4:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT5(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT5 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT5]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT5]single-color mode，not handleT5")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT5]single-color refill mode，not handleT5")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T5:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：withouttwoAMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has2AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without2AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T5:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


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
        chan=5+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT5 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT5=%d" % self.G_ChromaKitAccessT5)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT5, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T5:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT6(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT6 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT6]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT6]single-color mode，not handleT6")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT6]single-color refill mode，not handleT6")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T6:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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


        #lancaigang241224：withouttwoAMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has2AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without2AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T6:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return



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
        chan=6+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT6 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT6=%d" % self.G_ChromaKitAccessT6)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT6, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T6:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT7(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT7 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT7]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT7]single-color mode，not handleT7")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT7]single-color refill mode，not handleT7")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return

        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T7:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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


        #lancaigang241224：withouttwoAMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has2AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without2AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T7:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return

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
        chan=7+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT7 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT7=%d" % self.G_ChromaKitAccessT7)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT7, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T7:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT8(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT8 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT8]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT8]single-color mode，not handleT8")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT8]single-color refill mode，not handleT8")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T8:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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


        #lancaigang241224：without3AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has3AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without3AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T8:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return

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
        chan=8+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT8 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT8=%d" % self.G_ChromaKitAccessT8)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT8, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T8:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT9(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT9 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT9]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT9]single-color mode，not handleT9")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT9]single-color refill mode，not handleT9")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)


        # #lancaigang250912:
        # self.Cmds_CmdOrcaPre()

        



        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T9:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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


        #lancaigang241224：without3AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has3AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without3AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T9:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


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
        chan=9+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT9 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT9=%d" % self.G_ChromaKitAccessT9)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT9, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T9:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT10(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT10 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT10]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT10]single-color mode，not handleT10")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT10]single-color refill mode，not handleT10")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T10:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：without3AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has3AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without3AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T10:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return

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
        chan=10+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT10 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT10=%d" % self.G_ChromaKitAccessT10)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT10, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T10:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT11(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT11 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT11]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT11]single-color mode，not handleT11")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT11]single-color refill mode，not handleT11")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T11:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：without3AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has3AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without3AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T11:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


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
        chan=11+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT11 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT11=%d" % self.G_ChromaKitAccessT11)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT11, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T11:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT12(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT12 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT12]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT12]single-color mode，not handleT12")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT12]single-color refill mode，not handleT12")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T12:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：without4AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has4AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without4AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T12:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


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
        chan=12+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT12 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT12=%d" % self.G_ChromaKitAccessT12)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT12, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T12:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT13(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT13 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT13]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT13]single-color mode，not handleT13")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT13]single-color refill mode，not handleT13")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T13:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：without4AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has4AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without4AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T13:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


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
        chan=13+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT13 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT13=%d" % self.G_ChromaKitAccessT13)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT13, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T13:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT14(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT14 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT14]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT14]single-color mode，not handleT14")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT14]single-color refill mode，not handleT14")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:causesreturnabnormal
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T14:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：without4AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has4AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without4AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T14:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


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
        chan=14+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT14 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT14=%d" % self.G_ChromaKitAccessT14)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT14, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T14:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CmdT15(self,gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdT15 +1]orcacutchip/piece multi-color filament change" )

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT15]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250429：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT15]single-color mode，not handleT15")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        #lancaigang250514：
        if self.G_AMSDeviceWorkMode==AMS_WORK_MODE_MA :
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdT15]single-color refill mode，not handleT15")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro；command_string='%s'" % command_string)
            return
        
        #lancaigang240527：unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("unknown mode，because need operation manual command，default letSTM32perform enterMCmulti-color mode")
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC
            #lancaigang241030:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("serial port1send command：MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("serial port2send command：MC")

            self.G_ProzenToolhead.dwell(2)

        #lancaigang250912:
        #self.Cmds_CmdOrcaPre()

        

        
        #self.G_PhrozenFluiddRespondInfo("command='%s'；auto filament change" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T15:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
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

        #lancaigang241224：without4AMS，not execute；
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.G_PhrozenFluiddRespondInfo("has4AMS，continue execute command")
        else:
            self.G_PhrozenFluiddRespondInfo("without4AMS，not execute command")
            self.G_PhrozenFluiddRespondInfo("+T15:1,%d" % self.G_ChangeChannelTimeoutNewChan)
            return

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
        chan=15+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        if self.G_ChromaKitAccessT15 > 0:
            self.G_PhrozenFluiddRespondInfo("self.G_ChromaKitAccessT15=%d" % self.G_ChromaKitAccessT15)
            self.Cmds_P1CnAutoChangeChannel(self.G_ChromaKitAccessT15, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+T15:1,%d" % self.G_ChangeChannelTimeoutNewChan)

