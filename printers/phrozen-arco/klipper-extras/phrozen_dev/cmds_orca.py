import logging
import time
from .base import *


class OrcaMixin:
    """Mixin for Orca slicer T-command tool change operations."""

    def Cmds_CmdOrcaPre(self):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_CmdOrcaPre]orcabeforeset action" )

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CmdOrcaPre]standalone mode with multi-color enabled，not handleT?")
            #lancaigang250828:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_PAUSE_WAITINGAREA")
            command_string = """
                PRZ_PAUSE_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)

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


    def _Cmds_CmdTn(self, n, gcmd):
        """Common handler for T0-T15 tool change commands.
        n: tool index (0-15), maps to channel n+1.
        """
        tn_label = "T%d" % n
        access_attr = "G_ChromaKitAccessT%d" % n

        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_Cmd%s +1]orcacutchip/piece multi-color filament change" % tn_label)

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250515：standalone mode with multi-color enabled，not handleT?
        if self.G_P0M1MCNoneAMS == 1:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_Cmd%s]standalone mode with multi-color enabled，not handleT?" % tn_label)
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
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_Cmd%s]single-color mode，not handle%s" % (tn_label, tn_label))
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
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_Cmd%s]single-color refill mode，not handle%s" % (tn_label, tn_label))
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


        self.G_PhrozenFluiddRespondInfo("auto filament change")
        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+%s:0,%d" % (tn_label, self.G_ChangeChannelTimeoutNewChan))

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

        #lancaigang241224：T4-T15 require second AMS unit
        if n >= 4:
            if self.G_SerialPort2OpenFlag == True:
                self.G_PhrozenFluiddRespondInfo("has2AMS，continue execute command")
            else:
                self.G_PhrozenFluiddRespondInfo("without2AMS，not execute command")
                self.G_PhrozenFluiddRespondInfo("+%s:1,%d" % (tn_label, self.G_ChangeChannelTimeoutNewChan))
                return

        #auto filament change
        chan=n+1
        self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)

        #lancaigang250515:judge serial portscreen config colormatch pair/to channel
        access_val = getattr(self, access_attr, 0)
        if access_val > 0:
            self.G_PhrozenFluiddRespondInfo("self.%s=%d" % (access_attr, access_val))
            self.Cmds_P1CnAutoChangeChannel(access_val, gcmd)
        else:
            self.G_PhrozenFluiddRespondInfo("chan=%d" % chan)
            self.Cmds_P1CnAutoChangeChannel(chan, gcmd)

        #lancaigang240524：use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+%s:1,%d" % (tn_label, self.G_ChangeChannelTimeoutNewChan))


    def Cmds_CmdT0(self, gcmd):
        self._Cmds_CmdTn(0, gcmd)

    def Cmds_CmdT1(self, gcmd):
        self._Cmds_CmdTn(1, gcmd)

    def Cmds_CmdT2(self, gcmd):
        self._Cmds_CmdTn(2, gcmd)

    def Cmds_CmdT3(self, gcmd):
        self._Cmds_CmdTn(3, gcmd)

    def Cmds_CmdT4(self, gcmd):
        self._Cmds_CmdTn(4, gcmd)

    def Cmds_CmdT5(self, gcmd):
        self._Cmds_CmdTn(5, gcmd)

    def Cmds_CmdT6(self, gcmd):
        self._Cmds_CmdTn(6, gcmd)

    def Cmds_CmdT7(self, gcmd):
        self._Cmds_CmdTn(7, gcmd)

    def Cmds_CmdT8(self, gcmd):
        self._Cmds_CmdTn(8, gcmd)

    def Cmds_CmdT9(self, gcmd):
        self._Cmds_CmdTn(9, gcmd)

    def Cmds_CmdT10(self, gcmd):
        self._Cmds_CmdTn(10, gcmd)

    def Cmds_CmdT11(self, gcmd):
        self._Cmds_CmdTn(11, gcmd)

    def Cmds_CmdT12(self, gcmd):
        self._Cmds_CmdTn(12, gcmd)

    def Cmds_CmdT13(self, gcmd):
        self._Cmds_CmdTn(13, gcmd)

    def Cmds_CmdT14(self, gcmd):
        self._Cmds_CmdTn(14, gcmd)

    def Cmds_CmdT15(self, gcmd):
        self._Cmds_CmdTn(15, gcmd)
