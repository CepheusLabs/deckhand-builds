import logging
import time
from .base import *


class FilamentMixin:
    """Mixin for filament manipulation and cutting operations."""

    def Cmds_P1EnForceForward(self, chan, gcmd):
        logging.info("[(cmds.python)Cmds_P1EnForceForward]send command: E%d" % chan)

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+E:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241030:
        if chan in range(1, 5):
            self.Cmds_AMSSerial1Send("E%d" % chan)
            logging.info("Serial port 1 send command:E%d" % chan)
        elif chan in range(5, 9):
            self.Cmds_AMSSerial2Send("E%d" % (chan-4))
            logging.info("Serial port 2 send command:E%d" % (chan-4))


        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+E:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # lancaigang240228:toolhead retract a section distance, need stm32first retract a section distance
    # P1 G[n]; n:1~32 (1~4 if no daisy-chain); Retract specified channel filament some distance; ====="G?";
    def Cmds_P1GnExtruderBack(self, chan, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1EnForceForward]send command: G%d" % chan)

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+G:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241030:
        if chan in range(1, 5):
            self.Cmds_AMSSerial1Send("G%d" % chan)
            logging.info("Serial port 1 send command:G%d" % chan)
        elif chan in range(5, 9):
            self.Cmds_AMSSerial2Send("G%d" % (chan-4))
            logging.info("Serial port 2 send command:G%d" % (chan-4))


        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+G:1,%d" % self.G_ChangeChannelTimeoutNewChan)
    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_P1HnSpecialInfila(self, chan, gcmd):
        logging.info("[(cmds.python)Cmds_P1HnSpecialInfila]send command: H%d" % chan)

         #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+H:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241030:
        if chan in range(1, 5):
            self.Cmds_AMSSerial1Send("H%d" % chan)
            logging.info("Serial port 1 send command:H%d" % chan)
        elif chan in range(5, 9):
            self.Cmds_AMSSerial2Send("H%d" % (chan-4))
            logging.info("Serial port 2 send command:H%d" % (chan-4))


        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+H:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_P1InExtrudeManualIn(self, value):
        command_string = """
                        M106 S0
                        M83
                        G92 E0
                        G1 E%f F300
                        """ % (
                        value,
                    )
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1InExtrudeManualIn]GCODEcommand: %s" % command_string)


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # =====P1 J[n];multi-color manual purge;refill when buffer not full;
    def Cmds_P1JnManualSpitFila(self,chan, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1JnManualSpitFila]send commandP1J?")
        self.G_PhrozenFluiddRespondInfo("chan=%d;" % chan)
        self.G_PhrozenFluiddRespondInfo("+J:0,%d" % self.G_ChangeChannelTimeoutNewChan)


        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
        #lancaigang241030:
        if chan in range(1, 5):
            self.Cmds_AMSSerial1Send("J%d" % chan)
            logging.info("Serial port 1 send command:J%d" % chan)
        elif chan in range(5, 9):
            self.Cmds_AMSSerial2Send("J%d" % (chan-4))
            logging.info("Serial port 2 send command:J%d" % (chan-4))




        self.G_PhrozenFluiddRespondInfo("+J:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # =====P1 I[n];manual extrude whenstm32need refill;====="I?";?-extrude how much or retract how much
    #I2indicates extrude, I3indicates retract, I0indicatesidle
    def Cmds_P1InExtruderBack(self, value, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1InExtruderBack]send commandI?")
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
         #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+I:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang0415:I2indicates extrude, I3indicates retract
        if value>0:
            self.G_PhrozenFluiddRespondInfo("send command: I2;extrude")

            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("I2")
                logging.info("Serial port 1 send command:I2")
            elif self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("I2")
                logging.info("Serial port 2 send command:I2")

            #lancaigang240516:preventtime too close
            #lancaigang240705:prevent multiple timesrapid hitspacket concatenation;ortime too close
            self.G_ProzenToolhead.dwell(0.5)

            #time.sleep(2)
            self.G_PhrozenFluiddRespondInfo("time.sleep(2)")
        elif value<0:
            self.G_PhrozenFluiddRespondInfo("send command: I3;retract")

            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("I3")
                logging.info("Serial port 1 send command:I3")
            elif self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("I3")
                logging.info("Serial port 2 send command:I3")

            #lancaigang240516:preventtime too close
            #lancaigang240705:prevent multiple timesrapid hitspacket concatenation;ortime too close
            self.G_ProzenToolhead.dwell(0.52)

            #time.sleep(2)
            self.G_PhrozenFluiddRespondInfo("time.sleep(2)")
        elif value==0:
            self.G_PhrozenFluiddRespondInfo("send command: AT+IDLE;IDLEstate")

            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("AT+IDLE")
                logging.info("Serial port 1 send command:AT+IDLE")
            elif self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AT+IDLE")
                logging.info("Serial port 2 send command:AT+IDLE")

            #lancaigang240516:preventtime too close
            #lancaigang240705:prevent multiple timesrapid hitspacket concatenation;ortime too close
            self.G_ProzenToolhead.dwell(0.5)

            #time.sleep(2)
            self.G_PhrozenFluiddRespondInfo("time.sleep(2)")
        else:
            self.G_PhrozenFluiddRespondInfo("Send command: none")


        self.Cmds_P1InExtrudeManualIn(value)


        #self.Cmds_AMSSerial1Send("AT+IDLE")
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1EnForceForward]send command: AT+IDLE;IDLEstate")
        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+I:1,%d" % self.G_ChangeChannelTimeoutNewChan)




    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #P1 B?;filament retract
    def Cmds_P1BnWholeRollbackAction(self, chan, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1BnWholeRollbackAction]send command: B%d" % chan)
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
         #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+B:0,%d" % self.G_ChangeChannelTimeoutNewChan)


        #lancaigang241030:
        if chan in range(1, 5):
            self.Cmds_AMSSerial1Send("B%d" % chan)
            logging.info("Serial port 1 send command:B%d" % chan)
        elif chan in range(5, 9):
            self.Cmds_AMSSerial2Send("B%d" % (chan-4))
            logging.info("Serial port 2 send command:B%d" % (chan-4))



        #lancaigang240115:if current channel is notPTFE tube inside channel, can not check toolhead cut filament retract
        if self.G_ChangeChannelTimeoutNewChan == chan:
            #lancaigang240113:toolhead has filament only then detect
            if self.G_ToolheadIfHaveFilaFlag == True:
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201:Check if retract after cut is normal, pause if abnormal
                self.Cmds_CutFilaIfNormalCheck()

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+B:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #P1 D?;filament to park position
    def Cmds_P1DnMoveToParkPositonAction(self, chan, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1DnMoveToParkPositonAction]send command: P%d" % chan)
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
         #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+D:0,%d" % self.G_ChangeChannelTimeoutNewChan)

         #lancaigang241030:
        if chan in range(1, 5):
            self.Cmds_AMSSerial1Send("P%d" % chan)
            logging.info("Serial port 1 send command:P%d" % chan)
        elif chan in range(5, 9):
            self.Cmds_AMSSerial2Send("P%d" % (chan-4))
            logging.info("Serial port 2 send command:P%d" % (chan-4))


        #lancaigang240115:if current channel is notPTFE tube inside channel, can not check toolhead cut filament retract
        if self.G_ChangeChannelTimeoutNewChan == chan:
            #lancaigang240113:toolhead has filament only then detect
            if self.G_ToolheadIfHaveFilaFlag == True:
                self.G_ProzenToolhead.dwell(6.0)
                #lancaigang231201:Check if retract after cut is normal, pause if abnormal
                self.Cmds_CutFilaIfNormalCheck()

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+D:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaPrepare(self):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaPrepare]preparation before filament cut")

        # self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]special refill state before cut: H%d" % self.G_ChangeChannelTimeoutNewChan)
        # time.sleep(1)

        # #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]external macro-PG102;cut filament before, first purge/spitresidual toolhead filament, preventcut into pellets")
        # self.PG102Flag=True
        # self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=True")
        # command_string = """
        # PG102
        # """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command_string='%s'" % command_string)

        # # for i in range(15):
        # #     self.G_PhrozenFluiddRespondInfo("[(dev.python)]purge in, wait")
        # #     #lancaigang20231013:change is4seconds delay
        # #     #lancaigang231115:change is1s
        # #     self.G_ProzenToolhead.dwell(1.0)
        # #     #lancaigang240125:cannot usesleep, willblock main thread
        # #     #time.sleep(1)
        # self.PG102Flag=False
        # self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=False")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #move to cut filament position
    def Cmds_MoveToCutFilaAction(self, gcmd):
        # // [(cmds.python)Cmds_MoveToCutFilaAction]cut filament;gcodecommand=
        # // G91
        # // G1 Z1.200000 F3000
        # // [(cmds.python)Cmds_MoveToCutFilaAction]cut filament;gcodecommand=
        # // G90
        # // G1 X301.500000 Y0.000000 F24000
        # // G1 X308.500000 F600
        # // G1 X301.500000 F7200
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;send command")

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        # #lancaigang231208:pause resume abnormal, first disabled
        # # # 0=cut filament beforedefaultby internalgcodeexecute
        # #lancaigang231208:zaxis+positive will toward on
        # #lancaigang231215:Zaxis on rise after mustremember down lower
        # #if self.G_ChangeChannelIfZLiftingUpByGcode == 0:
        # command_string = """
        #     G91
        #     G1 Z%f F500
        #     """ % (
        #     self.G_AMSFilaCutZPositionLiftingUp,
        # )
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # #lancaigang231216:if filament change during pointclick pause, justgood filament change during lift risezaxis, to execute pause when, zaxis height also save, causes overall height abnormal
        # self.G_IfZPositionLiftUpFlag = True
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;Zaxis on lift up height/high;gcodecommand=%s" % command_string)
        # self.G_ProzenToolhead.wait_moves()
        # self.G_ProzenToolhead.dwell(1.0)



        # self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]special refill state before cut: H%d" % self.G_ChangeChannelTimeoutNewChan)
        # time.sleep(1)



        #run/move to cut filamentX Yposition, fast cut filament, again return a some
        # // G91
        # // G1 Z5.000000 F5000
        # // G90
        # // G1 X302.000000 Y244.100000 F5000
        # // G1 X309.000000 F500
        # // G1 X302.000000 F5000
        # // G1 X290 F5000
        command_string = """
            G91
            G1 Z%f F8000
            G90
            G1 X%f Y%f F10000
            G1 X%f Y%f F500
            G4 P500
            G1 X%f Y%f F8000
            G1 X%f F5000
            G91
            G1 Z-%f F8000
            """ % (
            self.G_AMSFilaCutZPositionLiftingUp,
            self.G_AMSFilaCutXPosition-7,
            self.G_AMSFilaCutYPosition,#lancaigang240409:
            self.G_AMSFilaCutXPosition,
            self.G_AMSFilaCutYPosition,
            self.G_AMSFilaCutXPosition-7,
            self.G_AMSFilaCutYPosition,#lancaigang241217:
            self.G_AMSFilaCutXPosition-30,#lancaigang250807:
            self.G_AMSFilaCutZPositionLiftingUp,
        )
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("Zaxis on lift up height/high and cut filament;gcodecommand=%s" % command_string)
        self.G_ProzenToolhead.wait_moves()

        #self.G_IfZPositionLiftUpFlag = True


        # #lancaigang240110:wait area zone wait before, first execute external macro, move tospecial fixed/set position performexecute/row wait
        # command_string = """
        #     PG101
        #     """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]external macro-tospecified positionwait purge;command_string='%s'" % command_string)
        # self.IfDoPG102Flag=True

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:1,%d" % self.G_ChangeChannelTimeoutNewChan)

        # #lancaigang231207:prevent cut filament top/push hold cutter, toward downpress/extrude0.5;causes pause resume when speedspecial otherslow, disabled
        # command = """
        #     G92 E0
        #     G1 E0.5 F300
        #     G92 E0
        # """
        # self.G_PhrozenGCode.run_script_from_command(command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;gcodecommand=%s" % command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]prevent cut filament top/push hold cutter, toward downpress/extrude0.5")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaAbsolutePositionNotReset(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAbsolutePositionNotReset]not home/reset cut filament, absolute pair/to position;send command=%s" % (gcmd.get_commandline()))

        # #lancaigang231208:zaxis+positive will toward on
        # # command_string = """
        # #     G91
        # #     G1 Z10 F3000
        # #     """
        # # self.G_PhrozenGCode.run_script_from_command(command_string)
        # #lancaigang231215:Zaxis on rise after mustremember down lower
        # command_string = """
        #     G91
        #     G1 Z%f F500
        #     """ % (
        #     self.G_AMSFilaCutZPositionLiftingUp,
        # )
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # #lancaigang231216:if filament change during pointclick pause, justgood filament change during lift risezaxis, to execute pause when, zaxis height also save, causes overall height abnormal
        # self.G_IfZPositionLiftUpFlag = True
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAbsolutePositionNotReset]Zaxis on rise10mm=%s" % command_string)
        # self.G_ProzenToolhead.wait_moves()
        # self.G_ProzenToolhead.dwell(1.0)


        # self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]special refill state before cut: H%d" % self.G_ChangeChannelTimeoutNewChan)
        # time.sleep(1)

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #run/move to cut filamentX Yposition, fast cut filament, again return a some
        # // G91
        # // G1 Z5.000000 F5000
        # // G90
        # // G1 X302.000000 Y244.100000 F5000
        # // G1 X309.000000 F500
        # // G1 X302.000000 F5000
        # // G1 X290 F5000
        command_string = """
            G91
            G1 Z%f F8000
            G90
            G1 X%f Y%f F10000
            G1 X%f Y%f F500
            G4 P500
            G1 X%f Y%f F8000
            G1 X%f F5000
            G91
            G1 Z-%f F8000
            """ % (
            self.G_AMSFilaCutZPositionLiftingUp,
            self.G_AMSFilaCutXPosition-7,
            self.G_AMSFilaCutYPosition,#lancaigang240409:
            self.G_AMSFilaCutXPosition,
            self.G_AMSFilaCutYPosition,
            self.G_AMSFilaCutXPosition-7,
            self.G_AMSFilaCutYPosition,#lancaigang241217:
            self.G_AMSFilaCutXPosition-30,#lancaigang250807:
            self.G_AMSFilaCutZPositionLiftingUp,
        )
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("Zaxis on lift up height/high and cut filament;gcodecommand=%s" % command_string)
        self.G_ProzenToolhead.wait_moves()

        #self.G_IfZPositionLiftUpFlag = True

        # #lancaigang240110:wait area zone wait before, first execute external macro, wipe nozzle
        # command_string = """
        #     PG107
        #     """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("external macro-wipe nozzle;command_string='%s'" % command_string)
        # self.IfDoPG102Flag=True

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:1,%d" % self.G_ChangeChannelTimeoutNewChan)

        # #lancaigang231207:prevent cut filament top/push hold cutter, toward downpress/extrude0.5;causes pause resume when speedspecial otherslow, disabled
        # command = """
        #     G92 E0
        #     G1 E0.5 F300
        #     G92 E0
        # """
        # self.G_PhrozenGCode.run_script_from_command(command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;gcodecommand=%s" % command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]prevent cut filament top/push hold cutter, toward downpress/extrude0.5")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaAbsolutePositionNotResetAndRollback(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAbsolutePositionNotResetAndRollback]not home/reset cut filament, absolute pair/to position;send command=%s" % (gcmd.get_commandline()))
        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
        # #lancaigang231208:zaxis+positive will toward on
        # # command_string = """
        # #     G91
        # #     G1 Z10 F3000
        # #     """
        # # self.G_PhrozenGCode.run_script_from_command(command_string)
        # #lancaigang231215:Zaxis on rise after mustremember down lower
        # command_string = """
        #     G91
        #     G1 Z%f F500
        #     """ % (
        #     self.G_AMSFilaCutZPositionLiftingUp,
        # )
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # #lancaigang231216:if filament change during pointclick pause, justgood filament change during lift risezaxis, to execute pause when, zaxis height also save, causes overall height abnormal
        # self.G_IfZPositionLiftUpFlag = True
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAbsolutePositionNotReset]Zaxis on rise10mm=%s" % command_string)
        # self.G_ProzenToolhead.wait_moves()
        # self.G_ProzenToolhead.dwell(1.0)

        # self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]special refill state before cut: H%d" % self.G_ChangeChannelTimeoutNewChan)
        # time.sleep(1)

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:0,%d" % self.G_ChangeChannelTimeoutNewChan)

       #run/move to cut filamentX Yposition, fast cut filament, again return a some
        # // G91
        # // G1 Z5.000000 F5000
        # // G90
        # // G1 X302.000000 Y244.100000 F5000
        # // G1 X309.000000 F500
        # // G1 X302.000000 F5000
        # // G1 X290 F5000
        command_string = """
            G91
            G1 Z%f F8000
            G90
            G1 X%f Y%f F10000
            G1 X%f Y%f F500
            G4 P500
            G1 X%f Y%f F8000
            G1 X%f F5000
            G91
            G1 Z-%f F8000
            """ % (
            self.G_AMSFilaCutZPositionLiftingUp,
            self.G_AMSFilaCutXPosition-7,
            self.G_AMSFilaCutYPosition,#lancaigang240409:
            self.G_AMSFilaCutXPosition,
            self.G_AMSFilaCutYPosition,
            self.G_AMSFilaCutXPosition-7,
            self.G_AMSFilaCutYPosition,#lancaigang241217:
            self.G_AMSFilaCutXPosition-30,#lancaigang250807:
            self.G_AMSFilaCutZPositionLiftingUp,
        )
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("Zaxis on lift up height/high and cut filament;gcodecommand=%s" % command_string)
        self.G_ProzenToolhead.wait_moves()

        # #self.G_IfZPositionLiftUpFlag = True
        # #lancaigang240110:wait area zone wait before, first execute external macro, wipe nozzle
        # command_string = """
        #     PG107
        #     """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("external macro-wipe nozzle;command_string='%s'" % command_string)
        # self.IfDoPG102Flag=True


        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:1,%d" % self.G_ChangeChannelTimeoutNewChan)


        # #lancaigang231207:prevent cut filament top/push hold cutter, toward downpress/extrude0.5;causes pause resume when speedspecial otherslow, disabled
        # command = """
        #     G92 E0
        #     G1 E0.5 F300
        #     G92 E0
        # """
        # self.G_PhrozenGCode.run_script_from_command(command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;gcodecommand=%s" % command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]prevent cut filament top/push hold cutter, toward downpress/extrude0.5")


        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            logging.info("Serial port 1 send command: AP, all retract to park position")
            #// all retract to park position;//===== P2 A1 all filament to park position for print Yes;"AP";
            self.Cmds_AMSSerial1Send("AP")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            logging.info("Serial port 2 send command: AP, all retract to park position")
            #// all retract to park position;//===== P2 A1 all filament to park position for print Yes;"AP";
            self.Cmds_AMSSerial2Send("AP")

        #lancaigang240913:delay timeplace/put to outside side/face
        self.G_ProzenToolhead.dwell(6.0)
        #lancaigang231201:Check if retract after cut is normal, pause if abnormal
        self.Cmds_CutFilaIfNormalCheck()

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaAndNotRollback(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAndNotRollback]cut filament;send command=%s" % (gcmd.get_commandline()))
        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Zero:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang20231019:printmachine abnormal power loss, auto filament change if found1channel toolheadresidual on time(s)filament, needcut material andretract carriage return all filament
        #lancaigang20231020:first not detect toolhead hasmaterial
        #if self.G_ToolheadIfHaveFilaFlag:
        # 0=cut filament beforedefaultby internalgcodeexecute
        #lancaigang231128:G28change isPG28
        #if self.G_ChangeChannelIfZLiftingUpByGcode == 0:
        self.G_PhrozenFluiddRespondInfo("home all and cut filament")
        command_string = """
        G28
        """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("home/reset=%s" % command_string)
        #lancaigang20231020:press/extrude outhead retractgcode, retract before need heat up toolhead, when interval comparelong time, here not handle, auto filament change only then heat up and cut filament
        # G92 E0
        # G1 E0.0000 F600
        # G91
        # G1 E-0.385 F8000
        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Zero:1,%d" % self.G_ChangeChannelTimeoutNewChan)

        self.G_PhrozenFluiddRespondInfo("cut filament")


        #lancaigang20231013:cut filament
        self.Cmds_MoveToCutFilaAction(gcmd)

####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaAndHomingXY(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAndHomingXY]cut filament;XYhome/reset")
        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Zero:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        #lancaigang20231019:printmachine abnormal power loss, auto filament change if found1channel toolheadresidual on time(s)filament, needcut material andretract carriage return all filament
        #lancaigang20231020:first not detect toolhead hasmaterial
        #if self.G_ToolheadIfHaveFilaFlag:
        # 0=cut filament beforedefaultby internalgcodeexecute
        #lancaigang231128:G28change isPG28
        #if self.G_ChangeChannelIfZLiftingUpByGcode == 0:
        self.G_PhrozenFluiddRespondInfo("G28home/return position/bitYand cut filament")
        command_string = """
        G28 Y0
        """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("Y0home/reset=%s" % command_string)
        self.G_PhrozenFluiddRespondInfo("G28home/return position/bitXand cut filament")
        command_string = """
        G28 X0
        """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("X0home/reset=%s" % command_string)
        #lancaigang20231020:press/extrude outhead retractgcode, retract before need heat up toolhead, when interval comparelong time, here not handle, auto filament change only then heat up and cut filament
        # G92 E0
        # G1 E0.0000 F600
        # G91
        # G1 E-0.385 F8000
        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Zero:1,%d" % self.G_ChangeChannelTimeoutNewChan)

        self.G_PhrozenFluiddRespondInfo("cut filament")


        #lancaigang20231013:cut filament
        self.Cmds_MoveToCutFilaAction(gcmd)


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaAndRollback(self, gcmd):
        number=50;
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAndRollback]cut filament;send command")

        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()

        #lancaigang20231019:printmachine abnormal power loss, auto filament change if found1channel toolheadresidual on time(s)filament, needcut material andretract carriage return all filament
        #lancaigang20231020:first not detect toolhead hasmaterial
        #if self.G_ToolheadIfHaveFilaFlag:
        # # 0=cut filament beforedefaultby internalgcodeexecute
        #lancaigang231128:G28change isPG28
        #lancaigang240319:GCODEinside hasPG28, here no needPG28
        #lancaigang240323:a layerfall/drop residual, first disabled
        # if self.G_ChangeChannelIfZLiftingUpByGcode == 0:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAndRollback]home all and cut filament")
        #     command_string = """
        #     PG28
        #     """
        #     self.G_PhrozenGCode.run_script_from_command(command_string)
        #     #lancaigang20231020:press/extrude outhead retractgcode, retract before need heat up toolhead, when interval comparelong time, here not handle, auto filament change only then heat up and cut filament
        #     # G92 E0
        #     # G1 E0.0000 F600
        #     # G91
        #     # G1 E-0.385 F8000

        self.G_PhrozenFluiddRespondInfo("cut filament")
        #lancaigang20231013:cut filament
        self.Cmds_MoveToCutFilaAction(gcmd)


        self.G_ProzenToolhead.dwell(2.0)


        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            logging.info("Serial port 1 send command: AP, all retract to park position")
            #// all retract to park position;//===== P2 A1 all filament to park position for print Yes;"AP";
            self.Cmds_AMSSerial1Send("AP")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            logging.info("Serial port 2 send command: AP, all retract to park position")
            #// all retract to park position;//===== P2 A1 all filament to park position for print Yes;"AP";
            self.Cmds_AMSSerial2Send("AP")




        #lancaigang240913:delay timeplace/put to outside side/face
        self.G_ProzenToolhead.dwell(6.0)
        #lancaigang231201:Check if retract after cut is normal, pause if abnormal
        self.Cmds_CutFilaIfNormalCheck()



        # if self.G_ToolheadIfHaveFilaFlag:
        #     for i in range(number):
        #             time.sleep(1)
        #             i += 1
        #             self.G_PhrozenFluiddRespondInfo('Toolhead has filament, AP command retracting filament; i=%d' % i)

        #             if i >= number:
        #                 self.G_PhrozenFluiddRespondInfo('APcommand timeout;number=%d' % number)
        #                 break
