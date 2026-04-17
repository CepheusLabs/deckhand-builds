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

    def _serial_reinit(self, port_num):
        """Re-initialize serial port 1 or 2. Returns True on success."""
        if port_num == 1:
            port_define = self.G_Serialport1Define
            recv_timer_fn = self.Device_TimmerUart1Recv
        else:
            port_define = self.G_Serialport2Define
            recv_timer_fn = self.Device_TimmerUart2Recv

        try:
            logging.info("re-initialize serial port%d" % port_num)
            obj = serial.Serial(port_define, SERIAL_PORT_BAUD, timeout=3)
            if obj is not None and obj.is_open:
                if port_num == 1:
                    self.G_SerialPort1Obj = obj
                    self.G_SerialPort1OpenFlag = True
                    self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(recv_timer_fn, self.G_PhrozenReactor.NOW)
                else:
                    self.G_SerialPort2Obj = obj
                    self.G_SerialPort2OpenFlag = True
                    self._tty2_open_failure_logged = False
                    self.G_SerialPort2RecvTimmer = self.G_PhrozenReactor.register_timer(recv_timer_fn, self.G_PhrozenReactor.NOW)
                logging.info("re-initialize serial port%dsuccess" % port_num)
                obj.flushInput()
                obj.flush()
                logging.info("serial port%dclear" % port_num)
                logging.info("re-register serial port%dcallback function" % port_num)
                return True
        except:
            self._log_port_failure(port_num)
        return False

    def _log_port_failure(self, port_num):
        """Log serial port open failure with dedup for port 2."""
        if port_num == 1:
            logging.info("Failed to open tty1 port - check USB connection or restart")
        else:
            if not self._tty2_open_failure_logged:
                self.G_PhrozenFluiddRespondInfo("Failed to open tty2 port - check USB connection or restart")
                self._tty2_open_failure_logged = True
            else:
                logging.debug("Failed to open tty2 port - check USB connection or restart")

    def _serial_send(self, port_num, cmd):
        """Send command on serial port 1 or 2 (fire-and-forget)."""
        if port_num == 1:
            port_define = self.G_Serialport1Define
            open_flag = self.G_SerialPort1OpenFlag
        else:
            port_define = self.G_Serialport2Define
            open_flag = self.G_SerialPort2OpenFlag

        if not open_flag:
            logging.info("[(cmds.py)Cmds_AMSSerial%dSend]tty%dserial port send failure;AMS%dmulti-color not yet connect, please first sendP28" % (port_num, port_num, port_num))
            self._serial_reinit(port_num)
            return

        logging.info("[(cmds.python)Cmds_AMSSerial%dSend]send command: cmd=%s" % (port_num, cmd))

        try:
            logging.info("send before, re-initialize serial port%d" % port_num)
            obj = serial.Serial(port_define, SERIAL_PORT_BAUD, timeout=3)
            if port_num == 1:
                self.G_SerialPort1Obj = obj
            else:
                self.G_SerialPort2Obj = obj
            if obj is not None and obj.is_open:
                #lock
                if self.Base_AMSSerialCmdLock():
                    obj.flush()
                    obj.write(cmd.encode())
                    logging.info("self.G_SerialPort%dObj.write" % port_num)
                    obj.flush()
                    #unlock
                    self.Base_AMSSerialCmdUnlock()
        except:
            self._log_port_failure(port_num)
            #unlock
            self.Base_AMSSerialCmdUnlock()

    def _serial_send_wait_rsp(self, port_num, cmd, res_len):
        """Send command on serial port and wait for response."""
        if port_num == 1:
            open_flag = self.G_SerialPort1OpenFlag
            obj = self.G_SerialPort1Obj
        else:
            open_flag = self.G_SerialPort2OpenFlag
            obj = self.G_SerialPort2Obj

        if not open_flag:
            logging.info("tty%dserial port send failure;AMS%dmulti-color not yet connect, please first sendP28" % (port_num, port_num))
            return

        logging.info("[(cmds.python)Cmds_AMSSerialPort%dSendWaitRsp]send command: cmd=%s" % (port_num, cmd))

        try:
            if obj is not None and obj.is_open:
                #lock
                if self.Base_AMSSerialCmdLock():
                    obj.write(cmd.encode())
                    logging.info("self.G_SerialPort%dObj.write" % port_num)
                    obj.flush()
                    resp = obj.read(res_len)
                    #unlock
                    self.Base_AMSSerialCmdUnlock()
                    return resp
        except:
            self._log_port_failure(port_num)
            #unlock
            self.Base_AMSSerialCmdUnlock()

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #serial send without waiting for response
    def Cmds_AMSSerial1Send(self, cmd):
        self._serial_send(1, cmd)

    def Cmds_AMSSerial2Send(self, cmd):
        self._serial_send(2, cmd)

    #serial send and wait for response
    def Cmds_AMSSerialPort1SendWaitRsp(self, cmd, res_len):
        return self._serial_send_wait_rsp(1, cmd, res_len)

    def Cmds_AMSSerialPort2SendWaitRsp(self, cmd, res_len):
        return self._serial_send_wait_rsp(2, cmd, res_len)


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
                        self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                        logging.info("len(self.G_PauseToLCDString)='%d'" % len(self.G_PauseToLCDString))

        except:
            logging.info("Failed to open tty1 port - check USB connection or restart")
            self.G_SerialPort1OpenFlag = False

            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW or self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                logging.info("single-colorM3or unknown mode, no need update pause info")
            else:
                logging.info("update pause info")
                logging.info("pause:+PAUSE:g")
                self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

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
        except:
            self._log_port_failure(2)
            self.G_SerialPort2OpenFlag = False

    def _report_pause8(self):
        """Report PAUSE:8 cutter/sensor abnormality to LCD."""
        pause_str = "+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan, self.G_ChangeChannelTimeoutNewChan)
        if len(self.G_PauseToLCDString) == 0:
            self.G_PhrozenFluiddRespondInfo(pause_str)
        else:
            self.G_PhrozenFluiddRespondInfo("update pause info")
            #lancaigang250721:ifAMScarriage return pull abnormal, all is abnormal pause8as is last pause
            self.G_PauseToLCDString = pause_str
            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

    def _send_at_pause_both_ports(self):
        """Send AT+PAUSE to both serial ports."""
        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("AT+PAUSE")
            logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AT+PAUSE")
            logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")

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

        #lancaigang240912:klipper delay must needlarge instm32old channel retract when interval
        self.G_PhrozenFluiddRespondInfo("seconds delay detect if filament present???")
        #retract filament8safter, toolhead is not has filament, normal is not will has filament
        if self.G_ToolheadIfHaveFilaFlag:
            self.G_PhrozenFluiddRespondInfo("toolhead retract past/over5seconds toolhead still detect to filament, please check cutter is not abnormal, manual change failed;klipperpause")
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

                #lancaigang250619:Check if AMS reconnected successfully
                self.Cmds_USBConnectErrorCheck()

                self._report_pause8()

            else:
                #lancaigang240328:if it is manual command, not pause
                if self.ManualCmdFlag==True:
                    self.G_PhrozenFluiddRespondInfo("manual command, klipper not execute pause")
                    self._send_at_pause_both_ports()
                    self._report_pause8()
                elif self.G_CutCheckTest==True:
                    self.G_PhrozenFluiddRespondInfo("cutter test, klipper not execute pause")
                    self._send_at_pause_both_ports()
                    self._report_pause8()
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

                    #lancaigang250619:Check if AMS reconnected successfully
                    self.Cmds_USBConnectErrorCheck()

                    self._report_pause8()
