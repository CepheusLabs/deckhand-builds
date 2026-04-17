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

            self.G_PhrozenFluiddRespondInfo("time.sleep(2)")
        else:
            self.G_PhrozenFluiddRespondInfo("Send command: none")


        self.Cmds_P1InExtrudeManualIn(value)

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

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #move to cut filament position
    def Cmds_MoveToCutFilaAction(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;send command")

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #run/move to cut filamentX Yposition, fast cut filament, again return a some
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

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:1,%d" % self.G_ChangeChannelTimeoutNewChan)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_MoveToCutFilaAbsolutePositionNotReset(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAbsolutePositionNotReset]not home/reset cut filament, absolute pair/to position;send command=%s" % (gcmd.get_commandline()))

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:0,%d" % self.G_ChangeChannelTimeoutNewChan)

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

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:1,%d" % self.G_ChangeChannelTimeoutNewChan)

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

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:0,%d" % self.G_ChangeChannelTimeoutNewChan)

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

        #lancaigang240524:use inUIUXdynamic interface
        self.G_PhrozenFluiddRespondInfo("+Cut:1,%d" % self.G_ChangeChannelTimeoutNewChan)

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
        self.G_PhrozenFluiddRespondInfo("home all and cut filament")
        command_string = """
        G28
        """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("home/reset=%s" % command_string)
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
