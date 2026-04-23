import logging
import time
import serial
from .base import *


class SerialMixin:
    """Mixin for serial communication and hardware transport."""

    def Cmds_MoveTo(self, pos, velocity):
        #Cannot get toolhead object
        if self.G_ProzenToolhead is None:
            return

        #wait toolhead move
        self.G_ProzenToolhead.wait_moves()
        #get Toolhead last position
        self.G_ToolheadLastPosition = self.G_ProzenToolhead.get_position()

        for index, p in enumerate(pos):
            self.G_ToolheadLastPosition[index] = p

        #toolhead manual move
        self.G_ProzenToolhead.manual_move(self.G_ToolheadLastPosition, velocity * self.G_MovementSpeedFactor)
        #wait toolhead move
        self.G_ProzenToolhead.wait_moves()
    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #serial send without waiting for response
    def Cmds_AMSSerial1Send(self, cmd):
        if self.G_SerialPort1OpenFlag==False:
            logging.info("[(cmds.py)Cmds_AMSSerial1Send]tty1serial port send failure;AMS1multi-color not yet connect, please first sendP28")
            try:
                logging.info("[(cmds.py)Cmds_AMSSerial1Send]re-initialize serial port1")
                self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
                #serial port opened successfully
                if self.G_SerialPort1Obj is not None:
                    if self.G_SerialPort1Obj.is_open:
                        self.G_SerialPort1OpenFlag = True
                        logging.info("re-initialize serial port1success")
                        #lancaigang231213:open serial port
                        self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                        self.G_SerialPort1Obj.flush()
                        logging.info("serial port1clear")
                        logging.info("re-register serial port1callback function")
                        self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
            except:
                logging.info("Failed to open tty1 port - check USB connection or restart")
            return

        logging.info("[(cmds.python)Cmds_AMSSerial1Send]send command: cmd=%s" % cmd)

        try:
            logging.info("send before, re-initialize serial port1")
            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
            #serial port opened successfully
            if self.G_SerialPort1Obj is not None:
                if self.G_SerialPort1Obj.is_open:
                    #tty1serial send commandlock
                    #lock
                    if self.Base_AMSSerialCmdLock():
                        self.G_SerialPort1Obj.flush()
                        #tty1serial port send
                        self.G_SerialPort1Obj.write(cmd.encode())#.encode()
                        logging.info("self.G_SerialPort1Obj.write")
                        self.G_SerialPort1Obj.flush()
                        #unlock
                        self.Base_AMSSerialCmdUnlock()

        except:
            logging.info("Failed to open tty1 port - check USB connection or restart")
            #unlock
            self.Base_AMSSerialCmdUnlock()



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_AMSSerial2Send(self, cmd):
        if self.G_SerialPort2OpenFlag==False:
            logging.info("[(cmds.py)Cmds_AMSSerial2Send]tty2serial port send failure;AMS2multi-color not yet connect, please first sendP28")
            try:
                logging.info("[(cmds.py)Cmds_AMSSerial2Send]re-initialize serial port2")
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
            return

        logging.info("[(cmds.python)Cmds_AMSSerial2Send]send command: cmd=%s" % cmd)


        try:
            logging.info("send before, re-initialize serial port2")
            self.G_SerialPort2Obj = serial.Serial(self.G_Serialport2Define, SERIAL_PORT_BAUD, timeout=3)
            #serial port opened successfully
            if self.G_SerialPort2Obj is not None:
                if self.G_SerialPort2Obj.is_open:
                    #tty1serial send commandlock
                    #lock
                    if self.Base_AMSSerialCmdLock():
                        self.G_SerialPort2Obj.flush()
                        #tty1serial port send
                        self.G_SerialPort2Obj.write(cmd.encode())#.encode()
                        logging.info("self.G_SerialPort2Obj.write")
                        self.G_SerialPort2Obj.flush()
                        #unlock
                        self.Base_AMSSerialCmdUnlock()
                        logging.info("self.G_SerialPort2Obj.write")
        except:
            if not self._tty2_open_failure_logged:
                self.G_PhrozenFluiddRespondInfo("Failed to open tty2 port - check USB connection or restart")
                self._tty2_open_failure_logged = True
            else:
                logging.debug("Failed to open tty2 port - check USB connection or restart")
            #unlock
            self.Base_AMSSerialCmdUnlock()




    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #serial send and wait for response
    def Cmds_AMSSerialPort1SendWaitRsp(self, cmd, res_len):
        if self.G_SerialPort1OpenFlag==False:
                logging.info("tty1serial port send failure;AMS1multi-color not yet connect, please first sendP28")
                return

        logging.info("[(cmds.python)Cmds_AMSSerialPort1SendWaitRsp]send command: cmd=%s" % cmd)


        try:
            #serial port opened successfully
            if self.G_SerialPort1Obj is not None:
                if self.G_SerialPort1Obj.is_open:
                    #acquire command lock token
                    #lock
                    if self.Base_AMSSerialCmdLock():
                        #tty1serial port send byte stream
                        self.G_SerialPort1Obj.write(cmd.encode())
                        logging.info("self.G_SerialPort1Obj.write")
                        self.G_SerialPort1Obj.flush()
                        #tty1serial port read byte stream
                        resp = self.G_SerialPort1Obj.read(res_len)
                        #unlock
                        self.Base_AMSSerialCmdUnlock()
                        return resp
        except:
            logging.info("Failed to open tty1 port - check USB connection or restart")
            #unlock
            self.Base_AMSSerialCmdUnlock()


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #serial send and wait for response
    def Cmds_AMSSerialPort2SendWaitRsp(self, cmd, res_len):
        if self.G_SerialPort2OpenFlag==False:
                logging.info("tty2serial port send failure;AMS2multi-color not yet connect, please first sendP28")
                return

        logging.info("[(cmds.python)Cmds_AMSSerialPort2SendWaitRsp]send command: cmd=%s" % cmd)

        # #acquire command lock token
        # #lock
        # if self.Base_AMSSerialCmdLock():
        #     #tty2serial port send byte stream
        #     self.G_SerialPort2Obj.write(cmd.encode())
        #     self.G_SerialPort2Obj.flush()
        #     #tty2serial port read byte stream
        #     resp = self.G_SerialPort2Obj.read(res_len)
        #     #unlock
        #     self.Base_AMSSerialCmdUnlock()
        #     return resp
        try:
            #serial port opened successfully
            if self.G_SerialPort2Obj is not None:
                if self.G_SerialPort2Obj.is_open:
                    #acquire command lock token
                    #lock
                    if self.Base_AMSSerialCmdLock():
                        #tty2serial port send byte stream
                        self.G_SerialPort2Obj.write(cmd.encode())
                        logging.info("self.G_SerialPort2Obj.write")
                        self.G_SerialPort2Obj.flush()
                        #tty2serial port read byte stream
                        resp = self.G_SerialPort2Obj.read(res_len)
                        #unlock
                        self.Base_AMSSerialCmdUnlock()
                        return resp
        except:
            if not self._tty2_open_failure_logged:
                self.G_PhrozenFluiddRespondInfo("Failed to open tty2 port - check USB connection or restart")
                self._tty2_open_failure_logged = True
            else:
                logging.debug("Failed to open tty2 port - check USB connection or restart")
            #unlock
            self.Base_AMSSerialCmdUnlock()




    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_USBConnectErrorCheck(self):
        logging.info("[(cmds.python)Cmds_USBConnectErrorCheck]")


        logging.info("self.G_CancelFlag='%s'" % self.G_CancelFlag)
        logging.info("current mode")
        self.Device_ReportModeIfChanged()

        try:
            logging.info("[(cmds.py)Cmds_USBConnectErrorCheck]re-initialize serial port1")
            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
            #serial port opened successfully
            if self.G_SerialPort1Obj is not None:
                if self.G_SerialPort1Obj.is_open:
                    self.G_SerialPort1OpenFlag = True
                    logging.info("re-initialize serial port1success")
                    #lancaigang231213:open serial port
                    self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                    self.G_SerialPort1Obj.flush()
                    logging.info("serial port1clear")
                    logging.info("re-register serial port1callback function")
                    self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)

                    if "+PAUSE:g" in self.G_PauseToLCDString:
                        logging.info("if it isUSBrunout error, clear error report info")
                        #lancaigang250902:cannot is empty, prevent after side/face pause error report info is empty and no way to popup pause dialog box
                        #self.G_PauseToLCDString=""
                        self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                        logging.info("len(self.G_PauseToLCDString)='%d'" % len(self.G_PauseToLCDString))

        except:
            logging.info("Failed to open tty1 port - check USB connection or restart")
            self.G_SerialPort1OpenFlag = False

            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW or self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                logging.info("single-colorM3or unknown mode, no need update pause info")
            else:
                if len(self.G_PauseToLCDString)==0:
                    logging.info("update pause info")
                    logging.info("pause:+PAUSE:g")
                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                else:
                    #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                    logging.info("update pause info")
                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    logging.info("pause:+PAUSE:g")

        try:
            logging.info("[(cmds.py)Cmds_USBConnectErrorCheck]re-initialize serial port2")
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
                    # if "+PAUSE:g" in self.G_PauseToLCDString:
                    #     self.G_PauseToLCDString=""
        except:
            if not self._tty2_open_failure_logged:
                self.G_PhrozenFluiddRespondInfo("Failed to open tty2 port - check USB connection or restart")
                self._tty2_open_failure_logged = True
            else:
                logging.debug("Failed to open tty2 port - check USB connection or restart")
            self.G_SerialPort2OpenFlag = False

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_CutFilaIfNormalCheck(self):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_CutFilaIfNormalCheck]")

        #lancaigang241016:
        self.ToolheadCutFlag=False

        #lancaigang250527:quick pause execution
        self.G_KlipperQuickPause = False

        # send command8Safter check filament is notstopremain/stay during toolhead, normal retract8stoolhead not should has filament
        #lancaigang20231013:change is8sdelay
        #lancaigang231201:change is5seconds
        #lancaigang240912:klipper delay must needlarge instm32old channel retract when interval
        #self.G_ProzenToolhead.dwell(6.0)

        self.G_PhrozenFluiddRespondInfo("seconds delay detect if filament present???")
        #lancaigang240125:cannot usesleep, willblock main thread
        #time.sleep(5)
        #retract filament8safter, toolhead is not has filament, normal is not will has filament
        if self.G_ToolheadIfHaveFilaFlag:
            #raise self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]filament change check toolhead is not has filament, but retract past/overseveral seconds toolhead on still detect to filament;cmd='%s'" % (gcmd.get_commandline()))
            self.G_PhrozenFluiddRespondInfo("toolhead retract past/over5seconds toolhead still detect to filament, please check cutter is not abnormal, manual change failed;klipperpause")
            # // lancaigang231202:+PAUSE:1,ch;1-load filament exhausted / jammed filament, pause
            # // lancaigang231202:+PAUSE:2,ch;2-pauseACK
            # // lancaigang231204:+PAUSE:3,ch;3-new channel print slow refill timeout10s, pause
            # // lancaigang231205:+PAUSE:4,ch;4-new channel load filament timeout50s, pause
            # // lancaigang231205:+PAUSE:5,ch;5-new channel print fast refill timeout10s, pause
            # // lancaigang231205:+PAUSE:6,ch;6-entry position to park position timeout10s, pause
            # // lancaigang231205:+PAUSE:7,ch;7-buffer full state timeout30s, pause
            # // lancaigang231205:+PAUSE:8,ch;8-toolhead cutter or sensor abnormality, pause
            # // lancaigang231205:+PAUSE:9,ch;9-change timeout120s, pause
            # // lancaigang231202:+PAUSE:a,ch;a-park position to buffer entry port timeout10s, pause
            # // lancaigang231202:+PAUSE:b,ch;b-reserved
            # // lancaigang231202:+PAUSE:c,ch;c-reserved
            # // lancaigang231202:+PAUSE:d,ch;d-reserved
            # // lancaigang231202:+PAUSE:10,ch;10-touchscreen orfluiddweb page active/manual pause
            #lancaigang240223:beforeZlift rise cut filament already failure, pause before first needZdown lower
            if self.G_IfZPositionLiftUpFlag==True:
                command_string = """
                    G90
                    G91
                    G1 Z-%f F8000
                    """ % (
                    self.G_AMSFilaCutZPositionLiftingUp,
                )
                self.G_PhrozenGCode.run_script_from_command(command_string)
                self.G_IfZPositionLiftUpFlag = False
                self.G_PhrozenFluiddRespondInfo("Zaxis down pull lower low;command_string='%s'" % command_string)


            #lancaigang240223:
            self.ToolheadCutFlag=True

            #lancaigang240322:if before side/face already pause, no need again report abnormal
            if self.STM32ReprotPauseFlag==1:
                self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                self.G_PhrozenFluiddRespondInfo("toolhead cutter or sensor abnormality, pause")
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d" % self.G_ChangeChannelTimeoutOldChan)
                #lancaigang250414:
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                #lancaigang250619:Check if AMS reconnected successfully
                self.Cmds_USBConnectErrorCheck()


                #lancaigang250721:
                if len(self.G_PauseToLCDString)==0:
                    self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                else:
                    #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                    self.G_PhrozenFluiddRespondInfo("update pause info")
                    #lancaigang250721:ifAMScarriage return pull abnormal, all is abnormal pause8as is last pause
                    self.G_PauseToLCDString="+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                    self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)




            else:
                #lancaigang240328:if it is manual command, not pause
                if self.ManualCmdFlag==True:
                    self.G_PhrozenFluiddRespondInfo("manual command, klipper not execute pause")
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AT+PAUSE")
                        logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AT+PAUSE")
                        logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")

                    #lancaigang250805:
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                        self.G_PhrozenFluiddRespondInfo("update pause info")
                        #lancaigang250721:ifAMScarriage return pull abnormal, all is abnormal pause8as is last pause
                        self.G_PauseToLCDString="+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                elif self.G_CutCheckTest==True:
                    self.G_PhrozenFluiddRespondInfo("cutter test, klipper not execute pause")
                    #lancaigang241031:
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AT+PAUSE")
                        logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AT+PAUSE")
                        logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")

                    #lancaigang250805:
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                        self.G_PhrozenFluiddRespondInfo("update pause info")
                        #lancaigang250721:ifAMScarriage return pull abnormal, all is abnormal pause8as is last pause
                        self.G_PauseToLCDString="+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                else:
                    self.G_PhrozenFluiddRespondInfo("toolhead cutter or sensor abnormality, pause")


                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPause(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")

                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d" % self.G_ChangeChannelTimeoutOldChan)
                    #lancaigang250619:Check if AMS reconnected successfully
                    self.Cmds_USBConnectErrorCheck()

                    #lancaigang250414:
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                        self.G_PhrozenFluiddRespondInfo("update pause info")
                        #lancaigang250721:ifAMScarriage return pull abnormal, all is abnormal pause8as is last pause
                        self.G_PauseToLCDString="+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
