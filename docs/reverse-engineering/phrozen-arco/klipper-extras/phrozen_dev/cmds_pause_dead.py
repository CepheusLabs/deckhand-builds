import logging
import time
import serial
from .base import *


class PauseMixin:
    """Mixin for print pause, resume, and cancel operations."""

    def Cmds_PhrozenKlipperPauseCommon(self):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_PhrozenKlipperPauseCommon]klipperpause")
        logging.info("=====PAUSE=====")
        logging.info("=====PAUSE=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====PAUSE=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
        #lancaigang250517:
        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)

        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")

        #lancaigang240229:
        if self.IfDoPG102Flag==True:
            logging.info("self.IfDoPG102Flag==True")
            self.IfDoPG102Flag=False

            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseCommon]external macro-PG104")
            # command_string = """
            # PG104
            # """
            # self.G_PhrozenGCode.run_script_from_command(command_string)
            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseCommon]external macro-arrange waste material;command_string='%s'" % command_string)
            # command = """
            #     G91
            #     G1 Z5 F5000
            #     G90
            #     G1 X240 Y280 F8000
            #     G91
            #     G1 Z-5 F5000
            #     G90
            # """
            # self.G_PhrozenGCode.run_script_from_command(command)
            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command=%s" % (command))


        #lancaigang241030:Can only pause while printing
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#0
            self.G_PhrozenFluiddRespondInfo("Not in print mode, skip PAUSE macro")
        else:
            Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
            logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
            logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
            #// current pause status-Lo_PauseStatus='{'is_paused': True}'
            if Lo_PauseStatus['is_paused'] == True:
                logging.info("already in paused state")
            else:
                logging.info("not in paused state")

                # #lancaigang250527:pause to wait area
                # self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
                # command = """
                # PRZ_PAUSE_WAITINGAREA
                # """
                # self.G_PhrozenGCode.run_script_from_command(command)
                # self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))

                #lancaigang250527:quick pause execution
                if self.G_KlipperQuickPause == True:
                    self.G_KlipperQuickPause = False


                    self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
                    command = """
                    PRZ_PAUSE_WAITINGAREA
                    """
                    self.G_PhrozenGCode.run_script_from_command(command)

                    #lancaigang240119:pause change usecfgconfigtable macro
                    self.G_PhrozenFluiddRespondInfo("start calling external macro-PAUSE_PRINTING")
                    command = """
                    PAUSE_PRINTING
                    """
                    self.G_PhrozenGCode.run_script_from_command(command)
                    logging.info("self.G_ProzenToolhead.wait_moves()")
                    self.G_ProzenToolhead.wait_moves()
                    self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))
                    #self.G_PhrozenFluiddRespondInfo("prevent pause not hold, many/more add command;send_pause_command")
                    #self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                else:
                    self.G_KlipperQuickPause = False

                    # #lancaigang250716:all need first to pause area
                    # self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
                    # command = """
                    # PRZ_PAUSE_WAITINGAREA
                    # """
                    # self.G_PhrozenGCode.run_script_from_command(command)

                    #lancaigang240119:pause change usecfgconfigtable macro
                    self.G_PhrozenFluiddRespondInfo("start calling external macro-PAUSE")
                    command = """
                    PAUSE
                    """
                    self.G_PhrozenGCode.run_script_from_command(command)
                    logging.info("self.G_ProzenToolhead.wait_moves()")
                    self.G_ProzenToolhead.wait_moves()
                    self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))
                    #self.G_PhrozenFluiddRespondInfo("prevent pause not hold, many/more add command;send_pause_command")
                    #self.G_PhrozenPrinterCancelPauseResume.send_pause_command()

                # #lancaigang250527:pause to wait area
                # self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
                # command = """
                # PRZ_PAUSE_WAITINGAREA
                # """
                # self.G_PhrozenGCode.run_script_from_command(command)
                # self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))

                #lancaigang240125:pause, then not allowstm23active/manual on report again pause
                self.STM32ReprotPauseFlag=1
                logging.info("self.STM32ReprotPauseFlag=1")

                self.G_KlipperIfPaused = True
                logging.info("self.G_KlipperIfPaused = True")
                logging.info("klipperpause;")




        #lancaigang240325:change failed, cannot execute resume
        self.G_MCModeCanResumeFlag = False

        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
        #lancaigang250517:
        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)

         #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")


        #lancaigang250607:print state;1-unload filament in;2-load filament in;3-print in;4-pause
        self.G_KlipperPrintStatus= 4

        # # #move to before side/face convenient user operation
        # # command = """
        # #     G90
        # #     G1 X150 Y10 F5400
        # # """
        # # self.G_PhrozenGCode.run_script_from_command(command)
        # # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command=%s" % (command))
        # # #eachgcodecommand after all need add a downwait_movesfunction
        # # #lancaigang231202:wait_moves may prevent klipper pause
        # # #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # # self.G_ProzenToolhead.wait_moves()
        # # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]move to before side/face convenient user operation")
        # #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_MoveToCutFilaAction]cut filament;gcodecommand=%s" % command)
        # #klipperpause command;save current x y zcoordinate
        # #lancaigang240108:Verify multi-pause saved data, to be validated
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]SAVE_GCODE_STATE")
        # self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
        # #self.G_ProzenToolhead.wait_moves()
        # self.G_ProzenToolhead.dwell(1.0)

        # #time.sleep(1)
        # #self.G_ProzenToolhead.wait_moves()
        # #self.G_PhrozenFluiddRespondInfo("[(cmds.python)]wait_moves")
        # #lancaigang231219:not determine is is not pause move causesklipper abnormalcrash
        # #lancaigang230103:pause sometimesstop not hold
        # #move to before side/face convenient user operation
        # # G91
        # # G1 Z10 F7000
        # # G90
        # command = """
        # G91
        # G1 X150 Y10 F6000
        # G90
        # """
        # self.G_PhrozenGCode.run_script_from_command(command)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command=%s" % (command))
        # self.G_ProzenToolhead.dwell(1.0)

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenKlipperPauseM2M3ToSTM32(self, gcmd):
        _ = gcmd

        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseM2M3ToSTM32]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseM2M3ToSTM32]command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseM2M3ToSTM32]command='%s'" % (gcmd.get_commandline(),))

        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()

        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")

        #lancaigang231129:pause when toolhead move tospecified position
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_KlipperIfPaused = True
        # #toolhead wait move
        #lancaigang231202:wait_moves may prevent klipper pause
        #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # self.G_ProzenToolhead.wait_moves()


        #time.sleep(1)
        #lancaigang231201:klipperpause when, pausestm32motor
        #// AT+PAUSE
        #// AT+PAUSE=8
        #// AT+PAUSE=9


        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("AT+PAUSE")
            logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AT+PAUSE")
            logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")


        #lancaigang240125:encapsulated function
        self.Cmds_PhrozenKlipperPauseCommon()


        self.G_KlipperIfPaused = True
        logging.info("self.G_KlipperIfPaused = True")
        logging.info("klipperpause;")

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenKlipperPauseMAToSTM32(self, gcmd):
        _ = gcmd

        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseMAToSTM32]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("command='%s'" % (gcmd.get_commandline(),))

        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")


        #time.sleep(1)

        # #lancaigang241031:
        # if self.G_SerialPort1OpenFlag == True:
        #     self.Cmds_AMSSerial1Send("AT+PAUSE")
        #     logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
        # #lancaigang241030:
        # if self.G_SerialPort2OpenFlag == True:
        #     self.Cmds_AMSSerial2Send("AT+PAUSE")
        #     logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")

        #lancaigang240229:
        if self.IfDoPG102Flag==True:
            logging.info("self.IfDoPG102Flag==True")
            self.IfDoPG102Flag=False

        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")

        #lancaigang241030:Can only pause while printing
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#0
            self.G_PhrozenFluiddRespondInfo("Not in print mode, skip PAUSE macro")
        else:

            #lancaigang240119:pause change usecfgconfigtable macro
            self.G_PhrozenFluiddRespondInfo("start calling external macro-PAUSEMA")
            command = """
            PAUSEMA
            """
            self.G_PhrozenGCode.run_script_from_command(command)
            self.G_PhrozenFluiddRespondInfo("calling macro:command=%s" % (command))
            #self.G_PhrozenFluiddRespondInfo("prevent pause not hold, many/more add command;send_pause_command")
            #self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
            self.G_PhrozenFluiddRespondInfo("finished calling external macro-PAUSEMA")

            #lancaigang240125:pause, then not allowstm23active/manual on report again pause
            self.STM32ReprotPauseFlag=1
            logging.info("self.STM32ReprotPauseFlag=1")
            self.G_KlipperIfPaused = True
            logging.info("self.G_KlipperIfPaused = True")
            logging.info("klipperpause;")


        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")


        #lancaigang240325:change failed, cannot execute resume
        self.G_MCModeCanResumeFlag = False

        logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenKlipperPauseM2M3NoneCmdToSTM32(self, gcmd):
        _ = gcmd

        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseM2M3NoneCmdToSTM32]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseM2M3NoneCmdToSTM32]command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseM2M3NoneCmdToSTM32]command='%s'" % (gcmd.get_commandline(),))


        #lancaigang231129:pause when toolhead move tospecified position
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_KlipperIfPaused = True
        # #toolhead wait move
        #lancaigang231202:wait_moves may prevent klipper pause
        #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # self.G_ProzenToolhead.wait_moves()

        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")


        #lancaigang240125:encapsulated function
        self.Cmds_PhrozenKlipperPauseCommon()


        self.G_KlipperIfPaused = True
        logging.info("self.G_KlipperIfPaused = True")
        logging.info("klipperpause;")

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")

    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # PRZ_PAUSE pause print (this pause is separate from the system built-in pause; used during filament change)
    # AT+PAUSE
    def Cmds_PhrozenKlipperPauseNoneCmdToSTM32(self, gcmd):
        _ = gcmd

        #lancaigang231130:disabled, each time(s)pause all execute below
        # if self.G_KlipperIfPaused == True:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseNoneCmdToSTM32]Already in klipper pause state")
        #     return


        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseNoneCmdToSTM32]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseNoneCmdToSTM32]command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseNoneCmdToSTM32]command='%s'" % (gcmd.get_commandline(),))


        #lancaigang231129:pause when toolhead move tospecified position
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_KlipperIfPaused = True
        # #toolhead wait move
        #lancaigang231202:wait_moves may prevent klipper pause
        #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # self.G_ProzenToolhead.wait_moves()

        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")


        #lancaigang240125:encapsulated function
        self.Cmds_PhrozenKlipperPauseCommon()


        self.G_KlipperIfPaused = True
        logging.info("self.G_KlipperIfPaused = True")
        logging.info("klipperpause;")

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenKlipperPauseToolheadCutFailsure(self, gcmd):
        _ = gcmd

        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseToolheadCutFailsure]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseToolheadCutFailsure]command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseToolheadCutFailsure]command='%s'" % (gcmd.get_commandline(),))


        #lancaigang231129:pause when toolhead move tospecified position
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_KlipperIfPaused = True
        # #toolhead wait move
        #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # self.G_ProzenToolhead.wait_moves()


        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")


        #lancaigang240125:encapsulated function
        self.Cmds_PhrozenKlipperPauseCommon()

        self.G_KlipperIfPaused = True
        logging.info("self.G_KlipperIfPaused = True")
        logging.info("klipperpause;")

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenKlipperPauseChangeChannelTimeout(self, gcmd):
        _ = gcmd


        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseChangeChannelTimeout]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseChangeChannelTimeout]command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseChangeChannelTimeout]command='%s'" % (gcmd.get_commandline(),))


        #lancaigang231129:pause when toolhead move tospecified position
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_KlipperIfPaused = True
        # #toolhead wait move
        #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # self.G_ProzenToolhead.wait_moves()


        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")


        #lancaigang240125:encapsulated function
        self.Cmds_PhrozenKlipperPauseCommon()

        self.G_KlipperIfPaused = True
        logging.info("self.G_KlipperIfPaused = True")
        logging.info("klipperpause;")

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # PRZ_PAUSE pause print (this pause is separate from the system built-in pause; used during filament change)
    # AT+PAUSE
    def Cmds_PhrozenKlipperPause(self, gcmd):
        _ = gcmd
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_PhrozenKlipperPause]klipperpause")
        #lancaigang231130:disabled, each time(s)pause all execute below
        # if self.G_KlipperIfPaused == True:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]Already in klipper pause state")
        #     return

        # if self.G_ChangeChannelResumeFlag:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]currently resume on time(s)action, not allow pause")
        #     return


        # #lancaigang231216:
        # eventtime = self.G_PhrozenReactor.monotonic()
        # # Determine "printing" status
        # idle_timeout = self.G_PhrozenPrinter.lookup_object("idle_timeout")
        # is_printing = idle_timeout.get_status(eventtime)["state"] == "Printing"
        # if is_printing:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]currently print in;command='%s'" % (gcmd.get_commandline(),))
        # else:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]not yet during print in;command='%s;return'" % (gcmd.get_commandline(),))
        #     return


        #lancaigang231115:Must check if gcmd is None first, otherwise klipper may crash
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]self.G_PhrozenFluiddRespondInfo;gcmdobject is empty")
            logging.info("self.G_PhrozenFluiddRespondInfo;klipperpause")
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]command='%s'" % (gcmd.get_commandline(),))
            logging.info("klipperpause")
            #pass
        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPause]command='%s'" % (gcmd.get_commandline(),))

        logging.info("current mode")
        self.Device_ReportModeIfChanged()

        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()

        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True
        logging.info("pausing, not allow new gcodecommand, need wait pause complete")



        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = True



        #time.sleep(1)

        #lancaigang231201:klipperpause when, pausestm32motor
        #// AT+PAUSE
        #// AT+PAUSE=8
        #// AT+PAUSE=9


        #lancaigang241031:
        if self.G_SerialPort1OpenFlag == True:
            self.Cmds_AMSSerial1Send("AT+PAUSE")
            logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AT+PAUSE")
            logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")

        #lancaigang231129:pause when toolhead move tospecified position
        # self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PRZ_PAUSE_STATE")
        # self.G_KlipperIfPaused = True
        # #toolhead wait move
        #lancaigang231207:cannot usewait_moves, not then causes save gcodecommand abnormal
        # self.G_ProzenToolhead.wait_moves()





        #lancaigang240125:encapsulated function
        self.Cmds_PhrozenKlipperPauseCommon()


        self.G_KlipperIfPaused = True
        logging.info("self.G_KlipperIfPaused = True")
        logging.info("klipperpause;")

        #lancaigang250526:
        self.G_KlipperInPausing = False
        logging.info("pause complete, allow new gcodecommand")


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # PRZ_RESUME resume print(andPRZ_PAUSEcorresponding to use)
    def Cmds_PhrozenKlipperResumeCommon(self):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_PhrozenKlipperResumeCommon]klipperresume")

        # #lancaigang240103:delay again resume
        # #self.G_ProzenToolhead.dwell(3.0)
        # velocity = 2400
        # self.G_PhrozenGCode.run_script_from_command(
        #     "RESTORE_GCODE_STATE NAME=PRZ_PAUSE_STATE MOVE=1 MOVE_SPEED=%.4f"
        #     % (velocity)
        # )
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResumeCommon]RESTORE_GCODE_STATE")
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResumeCommon]NAME=PRZ_PAUSE_STATE")
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResumeCommon]send_resume_command")
        # #klipperresume command
        # self.G_PhrozenPrinterCancelPauseResume.send_resume_command()
        # #self.G_ProzenToolhead.wait_moves()
        # self.G_ProzenToolhead.dwell(2.0)
        # # #lancaigang240103:Zaxis on rise after mustremember down lower, corresponding to pause when on rise height
        # # command_string = """
        # #     G90
        # #     G91
        # #     G1 Z-10 F3000
        # #     """
        # # self.G_PhrozenGCode.run_script_from_command(command_string)


        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            self.G_PhrozenFluiddRespondInfo("is pause state, need resume")
            #lancaigang240119:pause change usecfgconfigtable macro
            self.G_PhrozenFluiddRespondInfo("external macro-RESUME")
            command = """
            RESUME
            """
            self.G_PhrozenGCode.run_script_from_command(command)
            self.G_PhrozenFluiddRespondInfo("calling macro:command=%s" % (command))

            self.G_PauseToLCDString=""
        else:
            self.G_PhrozenFluiddRespondInfo("not in paused state, no need again resume")

        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])





        #lancaigang240325:resume data after, needinitial flag
        self.G_MCModeCanResumeFlag == False
        #lancaigang240108:pause state
        self.G_KlipperIfPaused = False
        #lancaigang240124:stm32active/manual on report, enable can pause1time(s)
        self.STM32ReprotPauseFlag=0

        #lancaigang250607:print state;1-unload filament in;2-load filament in;3-print in;4-pause
        self.G_KlipperPrintStatus= 3

        #lancaigang250619:ifusbconnectexceed past/over10s, then error report pause
        self.G_ASM1DisconnectErrorCount= 0




    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # PRZ_RESUME resume print(andPRZ_PAUSEcorresponding to use)
    def Cmds_PhrozenKlipperResume(self, gcmd):
        _ = gcmd
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.py)Cmds_PhrozenKlipperResume]")
        self.G_PhrozenFluiddRespondInfo("+RESUME:1,%d" % self.G_ChangeChannelTimeoutNewChan)
        logging.info("=====RESUME=====")
        logging.info("=====RESUME=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====RESUME=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
        #lancaigang250517:
        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")




        #lancaigang240511:resume time, all initialize a down serial port, prevent hot-plugAMScauses serial portcommunication abnormal
        try:
            logging.info("[(cmds.py)Cmds_PhrozenKlipperResume]re-initialize serial port1")
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




        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        #lancaigang241108:Can only pause while printing
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#0
            self.G_PhrozenFluiddRespondInfo("not during print mode, not execute resume,return")
            self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


        #lancaigang250510:
        if self.PG102Flag==True:
            self.G_PhrozenFluiddRespondInfo("currently purge in, not allow resume")
            self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
            return


        # #lancaigang231216:
        # eventtime = self.G_PhrozenReactor.monotonic()
        # # Determine "printing" status
        # idle_timeout = self.G_PhrozenPrinter.lookup_object("idle_timeout")
        # is_printing = idle_timeout.get_status(eventtime)["state"] == "Printing"
        # if is_printing:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]currently print in;command='%s'")
        # else:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]not yet during print in;command='%s;return'")
        #     return
        logging.info("klipperresume")

        #lancaigang240325:MCmode special handle, involves multiple times pause multiple times load/unload filament
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
            self.G_PhrozenFluiddRespondInfo("Multi-color special resume - first pause is standard, subsequent load/unload pauses skip resume")

            #lancaigang241011:first not handle resume during AMSactive/manual on report pause
            self.STM32ReprotPauseFlag=0

        else:
            self.G_PhrozenFluiddRespondInfo("single-color/single-color refill resume")
            #lancaigang240108:pause state
            self.G_KlipperIfPaused = False
            #lancaigang240124:stm32active/manual on report, enable can pause1time(s)
            self.STM32ReprotPauseFlag=0

            #lancaigang241106:
            #self.G_P0M2MAStartPrintFlag=0


        #lancaigang240325:
        #lancaigang240426:resume afterset position/bitfalse
        self.G_ResumeProcessCheckPauseStatus=False
        #lancaigang231207:+PAUSE:1load filament jammaterial flag
        self.G_IfInFilaBlockFlag=False
        #lancaigang240321:PG102process in pause flag
        self.PG102DelayPauseFlag=False
        #lancaigang240325:resume process state
        self.G_ChangeChannelResumeFlag=True
        #lancaigang231207:P1 C?auto filament change when, if need resume, also continue from1time(s)channel start
        self.G_ChangeChannelFirstFilaFlag=True
        #self.G_PhrozenFluiddRespondInfo("+RESUME:1,%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250812:single-color runout detection, supplement carriage return to pause area
        self.G_RetryToPauseAreaFlag = False
        self.G_RetryToPauseAreaCount = 0





        #=====lancaigang231212:LCD/web manual pause resume, if toolhead has detect to filament, then resume directly, no need stm32retract again load filament
        #lancaigang240108:active/manual pause also need consider toolhead is not has filament situation, aftercontinue need handle
        if self.G_IfToolheadHaveFilaInitiativePauseFlag  == True:
            self.G_IfToolheadHaveFilaInitiativePauseFlag=False

            #lancaigang240103:single-colorM2MArefill mode, need sendstm32resume state, preventstm32abnormal and no way to performexecute/row refill
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
                self.G_PhrozenFluiddRespondInfo("M2MAmode resume, manual pause resume")
                #lancaigang240122:
                self.AMSRunoutPauseTimeCount = 0
                #lancaigang240123:
                self.AMSRunoutPauseTimeoutFlag=0

                #has filament only then can resume print
                if self.G_ToolheadIfHaveFilaFlag:
                    self.G_M2MAModeResumeFlag=True
                    #lancaigang240412:single-color mode, if ChromaKit connected, need resume AMS
                    if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                        self.G_PhrozenFluiddRespondInfo("toolhead has filament, ChromaKit connected, no retract needed, send STM32 command to restore last state")
                        # #self.Cmds_CmdP8(gcmd)
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("FA")
                        #     self.G_PhrozenFluiddRespondInfo("Serial port 1 sendFA")
                        # elif self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("FA")
                        #     self.G_PhrozenFluiddRespondInfo("Serial port 2 sendFA")

                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                        self.G_KlipperQuickPause = True
                        # #lancaigang250427:
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        #     logging.info("serial port1-AMSend count when buffer full when interval")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        #     logging.info("serial port2-AMSend count when buffer full when interval")
                        # self.G_ProzenToolhead.dwell(1.5)

                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+RESTORE")
                            logging.info("serial port1-resume")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+RESTORE")
                            logging.info("serial port2-resume")
                        # #lancaigang250611:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        # command_string = """
                        #     PG108
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament, resume without retract and reload")
                        #lancaigang240125:encapsulated function
                        self.Cmds_PhrozenKlipperResumeCommon()
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead has filament, without ChromaKit connected, resume directly")
                        self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament, resume without retract and reload")

                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        # #lancaigang250611:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        # command_string = """
                        #     PG108
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        #lancaigang240125:encapsulated function
                        self.Cmds_PhrozenKlipperResumeCommon()
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                else:
                    if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, ChromaKit connected, executeP8complete load filament process")
                        #lancaigang241106:
                        self.G_P0M2MAStartPrintFlag=0

                        #lancaigang250522:not allowM3runout detection
                        self.G_IfChangeFilaOngoing = True

                        #lancaigang241106:
                        self.Cmds_CmdP8(gcmd)
                        #lancaigang250619:Check if AMS reconnected successfully
                        self.Cmds_USBConnectErrorCheck()
                        #lancaigang241106:toolhead success load filament
                        if self.G_P0M2MAStartPrintFlag==1:
                            #lancaigang250607:
                            self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                            self.G_KlipperQuickPause = True
                            # #lancaigang250427:
                            # if self.G_SerialPort1OpenFlag == True:
                            #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            #     logging.info("serial port1-AMSend count when buffer full when interval")
                            # if self.G_SerialPort2OpenFlag == True:
                            #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            #     logging.info("serial port2-AMSend count when buffer full when interval")
                            # self.G_ProzenToolhead.dwell(1.5)
                            #lancaigang250423:load filament success, start purge, through/notify knowAMS start count when, if purgeexceed past/over5seconds buffer still/orslow state, indicates clogged nozzle
                            #self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            #self.G_PhrozenFluiddRespondInfo("AMS start count when buffer full when interval")
                            if self.G_SerialPort1OpenFlag == True:
                                self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                                logging.info("serial port1-AMS start count when buffer full when interval")
                            if self.G_SerialPort2OpenFlag == True:
                                self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                                logging.info("serial port2-AMS start count when buffer full when interval")
                            #self.G_ProzenToolhead.dwell(1)
                            #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                            self.G_PG108Ingoing=1
                            #lancaigang250611:
                            self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                            command_string = """
                                PG108
                                """
                            self.G_PhrozenGCode.run_script_from_command(command_string)
                            self.G_PG108Ingoing=0
                            #lancaigang250427:
                            if self.G_SerialPort1OpenFlag == True:
                                self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                                logging.info("serial port1-AMSend count when buffer full when interval")
                            if self.G_SerialPort2OpenFlag == True:
                                self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                                logging.info("serial port2-AMSend count when buffer full when interval")

                            if self.STM32ReprotPauseFlag == 1:
                                self.G_PhrozenFluiddRespondInfo("STM32on report already pause, cannot resume")
                                #lancaigang240125:encapsulated function
                                #self.Cmds_PhrozenKlipperResumeCommon()
                                self.G_ChangeChannelResumeFlag=False
                                self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                            else:
                                self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                                #lancaigang240125:encapsulated function
                                self.Cmds_PhrozenKlipperResumeCommon()
                                self.G_ChangeChannelResumeFlag=False
                                self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_KlipperQuickPause = False
                            self.G_PhrozenFluiddRespondInfo("toolhead no filament, single-color refill continue pause")
                            if self.G_KlipperIfPaused == False:
                                self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                                logging.info("[(cmds.python)]PAUSE")
                                self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                                self.G_ProzenToolhead.wait_moves()
                                self.G_KlipperIfPaused=True
                                #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                                self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                            else:
                                self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, withoutAMS multi-color, single-color refill continue pause")
                        if self.G_KlipperIfPaused == False:
                            self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                            logging.info("[(cmds.python)]PAUSE")
                            self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                            self.G_ProzenToolhead.wait_moves()
                            self.G_KlipperIfPaused=True
                            #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)

                return


            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
                self.G_PhrozenFluiddRespondInfo("M3mode resume, manual pause resume")
                # #lancaigang241106:ChromaKit connected
                # if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                #     self.G_PhrozenFluiddRespondInfo("single-colorM3mode, ChromaKit connected, need sendstm32resume state")
                #     # #lancaigang240416:
                #     # if self.G_SerialPort1OpenFlag == True:
                #     #     self.Cmds_AMSSerial1Send("MA")
                #     #     self.G_PhrozenFluiddRespondInfo("serial port1-MA")
                #     # #lancaigang241030:
                #     # elif self.G_SerialPort2OpenFlag == True:
                #     #     self.Cmds_AMSSerial2Send("MA")
                #     #     self.G_PhrozenFluiddRespondInfo("serial port2-MA")

                #     # time.sleep(2)

                #     # #lancaigang240416:
                #     # if self.G_SerialPort1OpenFlag == True:
                #     #     self.Cmds_AMSSerial1Send("FA")
                #     #     self.G_PhrozenFluiddRespondInfo("serial port1-FA")
                #     # #lancaigang241030:
                #     # elif self.G_SerialPort2OpenFlag == True:
                #     #     self.Cmds_AMSSerial2Send("FA")
                #     #     self.G_PhrozenFluiddRespondInfo("serial port2-FA")

                #     #lancaigang241106:
                #     self.Cmds_CmdP8(gcmd)
                #     #lancaigang241106:toolhead success load filament
                #     if self.G_P0M2MAStartPrintFlag==1:
                #         self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament, resume without retract and reload")
                #         #lancaigang240125:encapsulated function
                #         self.Cmds_PhrozenKlipperResumeCommon()
                #     else:
                #         self.G_PhrozenFluiddRespondInfo("toolhead no filament, single-color refill continue pause")
                #         self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                #         self.G_PhrozenFluiddRespondInfo("send_pause_command")
                #         #no filament continue pause
                #         self.G_KlipperIfPaused=True
                #         self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                # else:
                #     if self.G_ToolheadIfHaveFilaFlag==True:
                #         self.G_PhrozenFluiddRespondInfo("single-colorM3mode, withoutAMS multi-color, klipperresume directly")
                #         self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament, resume without retract and reload")
                #         #lancaigang240125:encapsulated function
                #         self.Cmds_PhrozenKlipperResumeCommon()
                #     else:
                #         self.G_PhrozenFluiddRespondInfo("toolhead no filament, single-color refill continue pause")
                #         self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                #         self.G_PhrozenFluiddRespondInfo("send_pause_command")
                #         #no filament continue pause
                #         self.G_KlipperIfPaused=True
                #         self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)

                #has filament only then can resume print
                if self.G_ToolheadIfHaveFilaFlag:
                    #lancaigang240412:M3mode, if ChromaKit connected, need resume AMS
                    if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                        self.G_PhrozenFluiddRespondInfo("toolhead has filament, ChromaKit connected, no retract needed, send STM32 command to restore last state")
                        # #self.Cmds_CmdP8(gcmd)
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("FA")
                        #     self.G_PhrozenFluiddRespondInfo("Serial port 1 sendFA")
                        # elif self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("FA")
                        #     self.G_PhrozenFluiddRespondInfo("Serial port 2 sendFA")
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                        self.G_KlipperQuickPause = True
                        # #lancaigang250427:
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        #     logging.info("serial port1-AMSend count when buffer full when interval")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        #     logging.info("serial port2-AMSend count when buffer full when interval")
                        # self.G_ProzenToolhead.dwell(1.5)

                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+RESTORE")
                            logging.info("serial port1-resume")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+RESTORE")
                            logging.info("serial port2-resume")

                        # #lancaigang250611:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        # command_string = """
                        #     PG108
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament, resume without retract and reload")
                        #lancaigang240125:encapsulated function
                        self.Cmds_PhrozenKlipperResumeCommon()
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead has filament, without ChromaKit connected, resume directly")
                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        # self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament, resume without retract and reload")
                        # #lancaigang250409:purge again on resume
                        # command_string = """
                        # PG108
                        # """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                        # self.G_PhrozenFluiddRespondInfo("purge complete, toolhead detected filament resume print")
                        #lancaigang240125:encapsulated function
                        self.Cmds_PhrozenKlipperResumeCommon()
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                else:
                    if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, ChromaKit connected, executeP8complete load filament process")
                        #lancaigang241106:
                        self.G_P0M2MAStartPrintFlag=0

                        #lancaigang250522:not allowM3runout detection
                        self.G_IfChangeFilaOngoing = True

                        #lancaigang241106:
                        self.Cmds_CmdP8(gcmd)
                        #lancaigang250619:Check if AMS reconnected successfully
                        self.Cmds_USBConnectErrorCheck()
                        #lancaigang241106:toolhead success load filament
                        if self.G_P0M2MAStartPrintFlag==1:
                            #lancaigang250607:
                            self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                            self.G_KlipperQuickPause = True
                            # #lancaigang250427:
                            # if self.G_SerialPort1OpenFlag == True:
                            #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            #     logging.info("serial port1-AMSend count when buffer full when interval")
                            # if self.G_SerialPort2OpenFlag == True:
                            #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            #     logging.info("serial port2-AMSend count when buffer full when interval")
                            # self.G_ProzenToolhead.dwell(1.5)
                            if self.G_SerialPort1OpenFlag == True:
                                self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                                logging.info("serial port1-AMS start count when buffer full when interval")
                            if self.G_SerialPort2OpenFlag == True:
                                self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                                logging.info("serial port2-AMS start count when buffer full when interval")
                            #self.G_ProzenToolhead.dwell(1)
                            #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                            self.G_PG108Ingoing=1
                            #lancaigang250611:
                            self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                            command_string = """
                                PG108
                                """
                            self.G_PhrozenGCode.run_script_from_command(command_string)
                            self.G_PG108Ingoing=0
                            #lancaigang250427:
                            if self.G_SerialPort1OpenFlag == True:
                                self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                                logging.info("serial port1-AMSend count when buffer full when interval")
                            if self.G_SerialPort2OpenFlag == True:
                                self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                                logging.info("serial port2-AMSend count when buffer full when interval")
                            if self.STM32ReprotPauseFlag == 1:
                                self.G_PhrozenFluiddRespondInfo("STM32on report already pause, cannot resume")
                                #lancaigang240125:encapsulated function
                                #self.Cmds_PhrozenKlipperResumeCommon()
                                self.G_ChangeChannelResumeFlag=False
                                self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                            else:
                                self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                                #lancaigang240125:encapsulated function
                                self.Cmds_PhrozenKlipperResumeCommon()
                                self.G_ChangeChannelResumeFlag=False
                                self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_KlipperQuickPause = False
                            self.G_PhrozenFluiddRespondInfo("toolhead no filament, M3mode refill continue pause")
                            if self.G_KlipperIfPaused == False:
                                self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                                logging.info("[(cmds.python)]PAUSE")
                                self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                                self.G_ProzenToolhead.wait_moves()
                                self.G_KlipperIfPaused=True
                                #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                                self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                            else:
                                self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, withoutAMS multi-color, M3mode continue pause")
                        self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                        logging.info("[(cmds.python)]PAUSE")
                        self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                        self.G_ProzenToolhead.wait_moves()
                        #no filament continue pause
                        self.G_KlipperIfPaused=True
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)



                return


            #lancaigang240115:active/manual pause resume, resumestm32 state to slow print refill state
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
                self.G_PhrozenFluiddRespondInfo("M1MCmode resume")
                #lancaigang240521:resume time, if foundAMS abnormal restart, can consider is hot-plugAMS, execute complete unload filament filament change process
                if self.G_ResumeCheckAMS1ErrorRestartFlag == True:
                    self.G_ResumeCheckAMS1ErrorRestartFlag=False
                    self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume;multi-colorMCmode;foundAMS abnormal restart, execute resume filament change process")
                else:
                    self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume;multi-colorMCmode, stm32resume slow print refill state")
                    #self.Cmds_AMSSerial1Send("AT+MCRS=F")
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]AT+MCRS=F")
                    #lancaigang240115:if screen active/manual pause during, operationmanual command, stm32 state will change come change go, no way to know pause before state, only can re-executeP1 C?command
                    #if toolhead has filament, indicatesstm32can directly rotate/switchchange to slow refill state
                    if self.G_ToolheadIfHaveFilaFlag==True:
                        # #lancaigang241030:
                        # if self.G_ChangeChannelTimeoutNewChan in range(1, 4):
                        #     #lancaigang0427:not tube in interval is not hasmanual command, resumestm32 time, force change is slow refill state
                        #     self.Cmds_AMSSerial1Send("AT+MCRS=5,%d" % self.G_ChangeChannelTimeoutNewChan)#05=slow refill state
                        #     self.G_PhrozenFluiddRespondInfo("AT+MCRS=5,%d" % self.G_ChangeChannelTimeoutNewChan)
                        # elif self.G_ChangeChannelTimeoutNewChan in range(5, 8):
                        #     self.Cmds_AMSSerial2Send("AT+MCRS=5,%d" % self.G_ChangeChannelTimeoutNewChan-4)#05=slow refill state
                        #     self.G_PhrozenFluiddRespondInfo("AT+MCRS=5,%d" % self.G_ChangeChannelTimeoutNewChan-4)

                        self.G_PhrozenFluiddRespondInfo("multi-colorMCmode, sendstm32resume slow print refill state")
                        self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume, toolhead has filament")

                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+RESTORE")
                        #     logging.info("serial port1-resume")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+RESTORE")
                        #     logging.info("serial port2-resume")

                        # #lancaigang241012:active/manual pause also need re-load filament, preventAMS stateswitch abnormal

                        # #lancaigang240125:encapsulated function
                        # self.Cmds_PhrozenKlipperResumeCommon()
                        # self.G_ChangeChannelResumeFlag=False
                        # self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                        # return

                    else:
                        self.G_PhrozenFluiddRespondInfo("LCD/web manual pause resume;toolhead no filament, execute resume filament change process")




        #=====lancaigang231229:MAsingle-color refill independently handle, andsinglemachine single-color difference
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
            self.G_PhrozenFluiddRespondInfo("M2MAmode resume")
            #lancaigang240122:
            self.AMSRunoutPauseTimeCount = 0
            #lancaigang240123:
            self.AMSRunoutPauseTimeoutFlag=0

            # # #lancaigang240416:
            # # if self.G_SerialPort1OpenFlag == True:
            # #     self.Cmds_AMSSerial1Send("MA")
            # #     self.G_PhrozenFluiddRespondInfo("serial port1-MA")
            # # #lancaigang241030:
            # # elif self.G_SerialPort2OpenFlag == True:
            # #     self.Cmds_AMSSerial2Send("MA")
            # #     self.G_PhrozenFluiddRespondInfo("serial port2-MA")

            # # #lancaigang240115:delay1seconds, prevent packet concatenation
            # # time.sleep(2)

            # #has filament only then can resume print
            # if self.G_ToolheadIfHaveFilaFlag:
            #     # #lancaigang231228:resume after, send command tostm32resume on a time(s)statemachine state
            #     # #resume stateRS=F,i.e.resume on a time(s)state
            #     # #resume stateRS=0,i.e.resume onMASTATEMACHINE_IDLE_STANDBYstate
            #     # #resume stateRS=X,...
            #     # #resume stateRS=Y,...
            #     # #resume stateRS=Z,...
            #     # #lancaigang240108:do not send yet
            #     # #self.Cmds_AMSSerial1Send("AT+MARS=F")
            #     # #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]AT+MARS=F")
            #     # #lancaigang240108:re-select old work channel performexecute/row print, avoidPTFE tube inside filament is runout causes abnormal
            #     # #lancaigang240226:toolhead has filament, no need sendFA
            #     # #lancaigang240416:
            #     # if self.G_SerialPort1OpenFlag == True:
            #     #     self.Cmds_AMSSerial1Send("FA")
            #     #     self.G_PhrozenFluiddRespondInfo("serial port1-FA")
            #     # #lancaigang241030:
            #     # elif self.G_SerialPort2OpenFlag == True:
            #     #     self.Cmds_AMSSerial2Send("FA")
            #     #     self.G_PhrozenFluiddRespondInfo("serial port2-FA")

            #     # self.G_PhrozenFluiddRespondInfo("single-colorM2MArefill mode, toolhead has filament, resume directly")
            #     # #lancaigang240108:extrude complete again resume
            #     # #if self.P0M3FilaRunoutSpittingFinished == True:
            #     # #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]extrude complete, can resume")


            #     #lancaigang241106:
            #     self.Cmds_CmdP8(gcmd)
            #     #lancaigang241106:toolhead success load filament
            #     if self.G_P0M2MAStartPrintFlag==1:
            #         self.G_PhrozenFluiddRespondInfo("toolhead has filament, retract again load filament")
            #         #lancaigang240125:encapsulated function
            #         self.Cmds_PhrozenKlipperResumeCommon()
            #     else:
            #         self.G_PhrozenFluiddRespondInfo("toolhead no filament, single-color refill continue pause")
            #         self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
            #         self.G_PhrozenFluiddRespondInfo("send_pause_command")
            #         #no filament continue pause
            #         self.G_KlipperIfPaused=True
            #         self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)

            #     #lancaigang241106:
            #     #self.Cmds_CmdP8(gcmd)
            #     #self.Cmds_PhrozenKlipperResumeCommon()


            #     #lancaigang240108:toolhead has filament, can resume
            #     self.G_M2MAModeResumeFlag=True

            #     self.G_ChangeChannelResumeFlag=False
            #     self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)

            #     return
            # #no filament, need to reload
            # else:
            #     #lancaigang240108:resume time, allow runout extrude
            #     self.P0M3FilaRunoutSpittingFinished = False
            #     self.G_ToolheadFirstInputFila=False
            #     #lancaigang240108:toolhead has filament, can resume
            #     #lancaigang240109:not tube load filament is not timeout only need toolhead detect to filament, then can performexecute/row resume operation
            #     self.G_M2MAModeResumeFlag=True

            #     self.G_PhrozenFluiddRespondInfo("single-colorM2MArefill mode, toolhead no filament, need new filament")



            #     # #lancaigang240103:toolhead no filament, need re-load filament, re-arrange load filament sequence, execute single-color auto refillF8
            #     # #ttyUSB0serial port send:FA
            #     # #lancaigang240108:do not send yetFA
            #     # #lancaigang240416:
            #     # if self.G_SerialPort1OpenFlag == True:
            #     #     self.Cmds_AMSSerial1Send("FA")
            #     #     self.G_PhrozenFluiddRespondInfo("serial port1-FA")
            #     # #lancaigang241030:
            #     # elif self.G_SerialPort2OpenFlag == True:
            #     #     self.Cmds_AMSSerial2Send("FA")
            #     #     self.G_PhrozenFluiddRespondInfo("serial port2-FA")
            #     # #lancaigang231229:encapsulated function
            #     # self.Cmds_MARetryInFila(gcmd)

            #     #lancaigang241106:
            #     self.Cmds_CmdP8(gcmd)
            #     #lancaigang241106:toolhead success load filament
            #     if self.G_P0M2MAStartPrintFlag==1:
            #         self.G_PhrozenFluiddRespondInfo("toolhead has filament, retract again load filament")
            #         #lancaigang240125:encapsulated function
            #         self.Cmds_PhrozenKlipperResumeCommon()
            #     else:
            #         self.G_PhrozenFluiddRespondInfo("toolhead no filament, single-color refill continue pause")
            #         self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
            #         self.G_PhrozenFluiddRespondInfo("send_pause_command")
            #         #no filament continue pause
            #         self.G_KlipperIfPaused=True
            #         self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)

            #has filament only then can resume print
            if self.G_ToolheadIfHaveFilaFlag:
                self.G_M2MAModeResumeFlag=True
                #lancaigang240412:M2MAmode, if ChromaKit connected, need resume AMS
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, ChromaKit connected, but still is executeP8complete load filament process, prevent cut filament abnormal situation")
                    self.G_P0M2MAStartPrintFlag=0

                    #lancaigang250522:not allowM3runout detection
                    self.G_IfChangeFilaOngoing = True

                    self.Cmds_CmdP8(gcmd)
                    #lancaigang250619:Check if AMS reconnected successfully
                    self.Cmds_USBConnectErrorCheck()
                    # if self.G_SerialPort1OpenFlag == True:
                    #     self.Cmds_AMSSerial1Send("FA")
                    #     self.G_PhrozenFluiddRespondInfo("Serial port 1 sendFA")
                    # elif self.G_SerialPort2OpenFlag == True:
                    #     self.Cmds_AMSSerial2Send("FA")
                    #     self.G_PhrozenFluiddRespondInfo("Serial port 2 sendFA")
                    #lancaigang241106:toolhead success load filament
                    if self.G_P0M2MAStartPrintFlag==1:
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                        self.G_KlipperQuickPause = True
                        # #lancaigang250427:
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        #     logging.info("serial port1-AMSend count when buffer full when interval")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        #     logging.info("serial port2-AMSend count when buffer full when interval")
                        # self.G_ProzenToolhead.dwell(1.5)
                        #lancaigang250522:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        # command_string = """
                        #     PG109
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+RESTORE")
                        #     logging.info("serial port1-resume")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+RESTORE")
                        #     logging.info("serial port2-resume")
                        # self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                        # #lancaigang250611:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        # command_string = """
                        #     PG108
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # #lancaigang240125:encapsulated function
                        # self.Cmds_PhrozenKlipperResumeCommon()
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                            logging.info("serial port1-AMS start count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            logging.info("serial port2-AMS start count when buffer full when interval")
                        #self.G_ProzenToolhead.dwell(1)
                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                        self.G_PG108Ingoing=1
                        #lancaigang250611:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        command_string = """
                            PG108
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        #lancaigang250427:
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            logging.info("serial port1-AMSend count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            logging.info("serial port2-AMSend count when buffer full when interval")
                        if self.STM32ReprotPauseFlag == 1:
                            self.G_PhrozenFluiddRespondInfo("STM32on report already pause, cannot resume")
                            #lancaigang240125:encapsulated function
                            #self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                            #lancaigang240125:encapsulated function
                            self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, M2MAmode continue pause")
                        if self.G_KlipperIfPaused == False:
                            self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                            logging.info("[(cmds.python)]PAUSE")
                            self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                            self.G_ProzenToolhead.wait_moves()
                            #no filament continue pause
                            self.G_KlipperIfPaused=True
                            #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                else:
                    self.G_KlipperQuickPause = False
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, without ChromaKit connected, resume directly")
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume without retract and reload")

                    #lancaigang250522:
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                    command_string = """
                        PG109
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                    #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                    self.G_PG108Ingoing=1
                    #lancaigang250611:
                    self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                    command_string = """
                        PG108
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PG108Ingoing=0
                    #lancaigang240125:encapsulated function
                    self.Cmds_PhrozenKlipperResumeCommon()
                    self.G_ChangeChannelResumeFlag=False
                    self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
            else:
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    self.G_PhrozenFluiddRespondInfo("toolhead no filament, ChromaKit connected, executeP8complete load filament process")
                    #lancaigang241106:
                    self.G_P0M2MAStartPrintFlag=0

                    #lancaigang250522:not allowM3runout detection
                    self.G_IfChangeFilaOngoing = True

                    #lancaigang241106:
                    self.Cmds_CmdP8(gcmd)
                    #lancaigang250619:Check if AMS reconnected successfully
                    self.Cmds_USBConnectErrorCheck()
                    #lancaigang241106:toolhead success load filament
                    if self.G_P0M2MAStartPrintFlag==1:
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                        self.G_KlipperQuickPause = True
                        # #lancaigang250427:
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        #     logging.info("serial port1-AMSend count when buffer full when interval")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        #     logging.info("serial port2-AMSend count when buffer full when interval")
                        # self.G_ProzenToolhead.dwell(1.5)
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                            logging.info("serial port1-AMS start count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            logging.info("serial port2-AMS start count when buffer full when interval")
                        #self.G_ProzenToolhead.dwell(1)
                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                        self.G_PG108Ingoing=1
                        #lancaigang250611:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        command_string = """
                            PG108
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        #lancaigang250427:
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            logging.info("serial port1-AMSend count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            logging.info("serial port2-AMSend count when buffer full when interval")
                        if self.STM32ReprotPauseFlag == 1:
                            self.G_PhrozenFluiddRespondInfo("STM32on report already pause, cannot resume")
                            #lancaigang240125:encapsulated function
                            #self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                            #lancaigang240125:encapsulated function
                            self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, M2MAmode continue pause")
                        if self.G_KlipperIfPaused == False:
                            self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                            logging.info("[(cmds.python)]PAUSE")
                            self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                            self.G_ProzenToolhead.wait_moves()
                            self.G_KlipperIfPaused=True
                            #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                else:
                    self.G_KlipperQuickPause = False
                    self.G_PhrozenFluiddRespondInfo("toolhead no filament, withoutAMS multi-color, M2MAcontinue pause")
                    self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                    logging.info("[(cmds.python)]PAUSE")
                    self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                    self.G_ProzenToolhead.wait_moves()
                    self.G_KlipperIfPaused=True
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
                    self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    self.G_ChangeChannelResumeFlag=False
                    self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)







            return




        #=====lancaigang231220:M3single-color, need manual refill, only when toolhead detect to filament only then can resume print
        # singlemachineM3runout handle mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("M3mode resume")
            # #has filament only then can resume print
            # if self.G_ToolheadIfHaveFilaFlag:
            #     #lancaigang240412:single-color mode, if ChromaKit connected, need resume AMS
            #     if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
            #         # #lancaigang240416:
            #         # if self.G_SerialPort1OpenFlag == True:
            #         #     self.Cmds_AMSSerial1Send("MA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port1-MA")
            #         # #lancaigang241030:
            #         # elif self.G_SerialPort2OpenFlag == True:
            #         #     self.Cmds_AMSSerial2Send("MA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port2-MA")

            #         # #lancaigang240115:delay1seconds, prevent packet concatenation
            #         # time.sleep(2)

            #         # #lancaigang241030:FAuse in
            #         # if self.G_SerialPort1OpenFlag == True:
            #         #     self.Cmds_AMSSerial1Send("FA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port1-FA")
            #         # #lancaigang241030:
            #         # elif self.G_SerialPort2OpenFlag == True:
            #         #     self.Cmds_AMSSerial2Send("FA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port2-FA")

            #         #lancaigang241106:executeP8brand new load filament process, preventAMS abnormal power loss or other reason restart
            #         self.Cmds_CmdP8(gcmd)
            #         #lancaigang241106:toolhead success load filament
            #         if self.G_P0M2MAStartPrintFlag==1:
            #             self.G_PhrozenFluiddRespondInfo("single-colorM3mode, AMS multi-color toolhead has filament resume")
            #             #lancaigang240125:encapsulated function
            #             self.Cmds_PhrozenKlipperResumeCommon()
            #         else:
            #             self.G_PhrozenFluiddRespondInfo("singlemachineM3mode, ChromaKit connected toolhead no filament continue pause, please manually load filament")
            #             self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
            #             self.G_PhrozenFluiddRespondInfo("send_pause_command")
            #             #no filament continue pause
            #             self.G_KlipperIfPaused=True
            #             self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
            #     else:
            #         self.G_PhrozenFluiddRespondInfo("singlemachineM3mode, withoutAMS multi-color toolhead has filament resume")
            #         # #lancaigang240411:manual extrude again resume
            #         # command = """
            #         #     G90
            #         #     G1 X250 Y10 F10000
            #         #     G91
            #         #     G1 Z10 F500
            #         #     G92 E0
            #         #     G1 E100 F500
            #         #     G92 E0
            #         #     G0
            #         # """
            #         # self.G_PhrozenGCode.run_script_from_command(command)
            #         # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]command=%s" % command)
            #         self.G_PhrozenFluiddRespondInfo("call externalmacro-PG108-single-colorM3mode start purge")
            #         #lancaigang240407:callpurge function, place/put during purge before, prevent toolhead load filament again immediately outmaterial, causes execute multiple times command error report
            #         self.P0M3FilaRunoutSpittingFinished = True#purge complete, prevent multiple times call command
            #         # command = """
            #         #     G90
            #         #     G1 X250 Y10 F10000
            #         #     G91
            #         #     G1 Z10 F500
            #         #     G92 E0
            #         #     G1 E100 F500
            #         #     G92 E0
            #         #     G0
            #         # """
            #         # self.G_PhrozenGCode.run_script_from_command(command)
            #         # self.G_PhrozenFluiddRespondInfo("[(dev.python)Cmds_PhrozenKlipperResume]command=%s" % command)
            #         command_string = """
            #         PG108
            #         """
            #         self.G_PhrozenGCode.run_script_from_command(command_string)
            #         self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)


            #         #lancaigang240125:encapsulated function
            #         self.Cmds_PhrozenKlipperResumeCommon()

            #     # #lancaigang241106:
            #     # self.Cmds_CmdP8(gcmd)
            #     # self.Cmds_PhrozenKlipperResumeCommon()

            #     self.G_ChangeChannelResumeFlag=False
            #     self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)


            #     return


            # #without filament continue pause
            # else:
            #     #lancaigang240412:single-color mode, if ChromaKit connected, need resume AMS
            #     if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
            #         # #lancaigang240416:
            #         # if self.G_SerialPort1OpenFlag == True:
            #         #     self.Cmds_AMSSerial1Send("MA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port1-MA")
            #         # #lancaigang241030:
            #         # elif self.G_SerialPort2OpenFlag == True:
            #         #     self.Cmds_AMSSerial2Send("MA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port2-MA")

            #         # #lancaigang240115:delay1seconds, prevent packet concatenation
            #         # time.sleep(2)

            #         # self.G_PhrozenFluiddRespondInfo("single-colorM3mode, ChromaKit connected toolhead no filament, need new filament")
            #         # #lancaigang240103:toolhead no filament, need re-load filament, re-arrange load filament sequence, execute single-color auto refillF8
            #         # #ttyUSB0serial port send:FA
            #         # #lancaigang240108:do not send yetFA
            #         # #lancaigang240416:
            #         # if self.G_SerialPort1OpenFlag == True:
            #         #     self.Cmds_AMSSerial1Send("FA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port1-FA")
            #         # #lancaigang241030:
            #         # elif self.G_SerialPort2OpenFlag == True:
            #         #     self.Cmds_AMSSerial2Send("FA")
            #         #     self.G_PhrozenFluiddRespondInfo("serial port2-FA")

            #         # #lancaigang231229:encapsulated function
            #         # self.Cmds_MARetryInFila(gcmd)

            #         #lancaigang241106:executeP8brand new load filament process, preventAMS abnormal power loss or other reason restart
            #         self.Cmds_CmdP8(gcmd)
            #         #lancaigang241106:toolhead success load filament
            #         if self.G_P0M2MAStartPrintFlag==1:
            #             self.G_PhrozenFluiddRespondInfo("single-colorM3mode, AMS multi-color toolhead has filament resume")
            #             #lancaigang240125:encapsulated function
            #             self.Cmds_PhrozenKlipperResumeCommon()
            #         else:
            #             self.G_PhrozenFluiddRespondInfo("singlemachineM3mode, ChromaKit connected toolhead no filament continue pause, please manually load filament")
            #             self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
            #             self.G_PhrozenFluiddRespondInfo("send_pause_command")
            #             #no filament continue pause
            #             self.G_KlipperIfPaused=True
            #             self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)

            #     else:
            #         self.G_PhrozenFluiddRespondInfo("singlemachineM3mode, withoutAMS multi-color toolhead no filament continue pause, please manually load filament")
            #         self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
            #         self.G_PhrozenFluiddRespondInfo("send_pause_command")
            #         #no filament continue pause
            #         self.G_KlipperIfPaused=True
            #         self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)



            #has filament only then can resume print
            if self.G_ToolheadIfHaveFilaFlag:
                #lancaigang240412:M3mode, if ChromaKit connected, need resume AMS
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    # self.G_PhrozenFluiddRespondInfo("toolhead has filament, ChromaKit connected, no retract needed, send STM32 command to restore last state")
                    # #self.Cmds_CmdP8(gcmd)
                    # if self.G_SerialPort1OpenFlag == True:
                    #     self.Cmds_AMSSerial1Send("FA")
                    #     self.G_PhrozenFluiddRespondInfo("Serial port 1 sendFA")
                    # elif self.G_SerialPort2OpenFlag == True:
                    #     self.Cmds_AMSSerial2Send("FA")
                    #     self.G_PhrozenFluiddRespondInfo("Serial port 2 sendFA")
                    # self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume without retract and reload")
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, ChromaKit connected, but still is executeP8complete load filament process, prevent cut filament abnormal situation")
                    self.G_P0M2MAStartPrintFlag=0

                    #lancaigang250522:not allowM3runout detection
                    self.G_IfChangeFilaOngoing = True

                    self.Cmds_CmdP8(gcmd)
                    #lancaigang250619:Check if AMS reconnected successfully
                    self.Cmds_USBConnectErrorCheck()
                    # if self.G_SerialPort1OpenFlag == True:
                    #     self.Cmds_AMSSerial1Send("FA")
                    #     self.G_PhrozenFluiddRespondInfo("Serial port 1 sendFA")
                    # elif self.G_SerialPort2OpenFlag == True:
                    #     self.Cmds_AMSSerial2Send("FA")
                    #     self.G_PhrozenFluiddRespondInfo("Serial port 2 sendFA")
                    #lancaigang241106:toolhead success load filament
                    if self.G_P0M2MAStartPrintFlag==1:
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                        self.G_KlipperQuickPause = True
                        # #lancaigang250427:
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        #     logging.info("serial port1-AMSend count when buffer full when interval")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        #     logging.info("serial port2-AMSend count when buffer full when interval")
                        # self.G_ProzenToolhead.dwell(1.5)
                        #lancaigang250522:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        # command_string = """
                        #     PG109
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+RESTORE")
                        #     logging.info("serial port1-resume")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+RESTORE")
                        #     logging.info("serial port2-resume")
                        # self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                        # #lancaigang250611:
                        # self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        # command_string = """
                        #     PG108
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        # #lancaigang240125:encapsulated function
                        # self.Cmds_PhrozenKlipperResumeCommon()
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                            logging.info("serial port1-AMS start count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            logging.info("serial port2-AMS start count when buffer full when interval")
                        #self.G_ProzenToolhead.dwell(1)
                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                        self.G_PG108Ingoing=1
                        #lancaigang250611:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        command_string = """
                            PG108
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        #lancaigang250427:
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            logging.info("serial port1-AMSend count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            logging.info("serial port2-AMSend count when buffer full when interval")
                        if self.STM32ReprotPauseFlag == 1:
                            self.G_PhrozenFluiddRespondInfo("STM32on report already pause, cannot resume")
                            #lancaigang240125:encapsulated function
                            #self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                            #lancaigang240125:encapsulated function
                            self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, M3mode continue pause")
                        if self.G_KlipperIfPaused == False:
                            self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                            logging.info("[(cmds.python)]PAUSE")
                            self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                            self.G_ProzenToolhead.wait_moves()
                            self.G_KlipperIfPaused=True
                            #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                else:
                    self.G_KlipperQuickPause = False
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, without ChromaKit connected, resume directly")
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume without retract and reload")
                    #lancaigang250522:
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                    command_string = """
                        PG109
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                    #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                    self.G_PG108Ingoing=1
                    #lancaigang250409:purge again on resume
                    command_string = """
                    PG108
                    """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PG108Ingoing=0
                    self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                    self.G_PhrozenFluiddRespondInfo("purge complete, toolhead detected filament resume print")
                    #lancaigang240125:encapsulated function
                    self.Cmds_PhrozenKlipperResumeCommon()
                    self.G_ChangeChannelResumeFlag=False
                    self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
            else:
                if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                    self.G_PhrozenFluiddRespondInfo("toolhead no filament, ChromaKit connected, executeP8complete load filament process")
                    #lancaigang241106:
                    self.G_P0M2MAStartPrintFlag=0

                    #lancaigang250522:not allowM3runout detection
                    self.G_IfChangeFilaOngoing = True

                    #lancaigang241106:
                    self.Cmds_CmdP8(gcmd)
                    #lancaigang250619:Check if AMS reconnected successfully
                    self.Cmds_USBConnectErrorCheck()
                    #lancaigang241106:toolhead success load filament
                    if self.G_P0M2MAStartPrintFlag==1:
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("can resume, STM32print in fast error report")
                        self.G_KlipperQuickPause = True
                        # #lancaigang250427:
                        # if self.G_SerialPort1OpenFlag == True:
                        #     self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        #     logging.info("serial port1-AMSend count when buffer full when interval")
                        # if self.G_SerialPort2OpenFlag == True:
                        #     self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        #     logging.info("serial port2-AMSend count when buffer full when interval")
                        # self.G_ProzenToolhead.dwell(1.5)
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                            logging.info("serial port1-AMS start count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            logging.info("serial port2-AMS start count when buffer full when interval")
                        #self.G_ProzenToolhead.dwell(1)
                        #lancaigang250522:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-PG109-heat up;command_string='%s'" % command_string)
                        #lancaigang251120:perform enter purge, add flag, preventPG108purge process in toolheadHall without filament pause, causes pause position during purge area, resume would crash into the purge bin;
                        self.G_PG108Ingoing=1
                        #lancaigang250611:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG108-heat up purge wipe nozzle")
                        command_string = """
                            PG108
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        #lancaigang250427:
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            logging.info("serial port1-AMSend count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            logging.info("serial port2-AMSend count when buffer full when interval")
                        if self.STM32ReprotPauseFlag == 1:
                            self.G_PhrozenFluiddRespondInfo("STM32on report already pause, cannot resume")
                            #lancaigang240125:encapsulated function
                            #self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)
                        else:
                            self.G_PhrozenFluiddRespondInfo("toolhead has filament, resume")
                            #lancaigang240125:encapsulated function
                            self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_ChangeChannelResumeFlag=False
                            self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_KlipperQuickPause = False
                        self.G_PhrozenFluiddRespondInfo("toolhead no filament, M3mode continue pause")
                        if self.G_KlipperIfPaused == False:
                            self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                            logging.info("[(cmds.python)]PAUSE")
                            self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                            self.G_ProzenToolhead.wait_moves()
                            #no filament continue pause
                            self.G_KlipperIfPaused=True
                            #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo("already pause, no need repeat pause")
                        self.G_ChangeChannelResumeFlag=False
                        self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)

                else:
                    self.G_KlipperQuickPause = False
                    self.G_PhrozenFluiddRespondInfo("toolhead no filament, withoutAMS multi-color, M3continue pause")
                    self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                    logging.info("[(cmds.python)]PAUSE")
                    self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                    self.G_ProzenToolhead.wait_moves()
                    #no filament continue pause
                    self.G_KlipperIfPaused=True
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d" % self.G_ChangeChannelTimeoutNewChan)
                    self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    self.G_ChangeChannelResumeFlag=False
                    self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)




            # self.G_ChangeChannelResumeFlag=False
            # self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)


            return






        # #lancaigang240319:toolhead has filament, special refillH?
        # if self.G_ToolheadIfHaveFilaFlag:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]toolhead has filament")
        #     #lancaigang240319:preparation before filament cut
        #     #self.Cmds_MoveToCutFilaPrepare()
        #     self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutNewChan)
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]special refill state before cut: H%d" % self.G_ChangeChannelTimeoutNewChan)
        #     time.sleep(1)


        # #lancaigang240423:resume time, first retract filament
        # self.Cmds_AMSSerial1Send("G%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]G%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]AMSfirst retract a section distance, then toolhead again retractmm: G%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PauseTriggerWhileChangeChannelFlag=False




        self.G_PhrozenFluiddRespondInfo("external macro-PG104-get pre-change global variables")
        command_string = """
            PG104
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-PG104-get pre-change global variables;command_string='%s'" % command_string)
        self.IfDoPG102Flag=True


        self.G_PhrozenFluiddRespondInfo("external macro-PG101-retract")
        command_string = """
            PG101
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position wait purge;command_string='%s'" % command_string)
        self.IfDoPG102Flag=True





        #lancaigang240328:manual command skip purge
        if self.ManualCmdFlag==True:
            self.G_PhrozenFluiddRespondInfo("external macro-PG106;manual command, not execute purge function")
        else:
            #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
            self.G_PhrozenFluiddRespondInfo("external macro-PG106;cut filament before, first purge/spitresidual toolhead filament, preventcut into pellets")
            self.PG102Flag=True
            logging.info("self.Flag=True")
            command_string = """
            PG106
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
            self.PG102Flag=False
            logging.info("self.Flag=False")

        #lancaigang241012:execute after side/face PG102
        self.IfDoPG102Flag=True

        #lancaigang250717:first purge/spitresidual, buffer and inertia down press asmall small section down
        self.G_ProzenToolhead.dwell(8)

        #lancaigang250519:
        self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WIPEMOUTH")
        command_string = """
            PRZ_WIPEMOUTH
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position;command_string='%s'" % command_string)




        #lancaigang20231205:cutter cut filament
        #lancaigang231215:Zaxis on rise after mustremember down lower
        self.Cmds_MoveToCutFilaAction(gcmd)




        #lancaigang231216:ifzaxis lift rise without by lower down, need lower down again pause
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




        #lancaigang240226:cut filament afterAMS mainboard retract filament, delay after toolhead retract20mm
        #time.sleep(2)
        self.G_ProzenToolhead.dwell(0.5)



        # #lancaigang240328:manual command skip purge
        # if self.ManualCmdFlag==True:
        #     self.G_PhrozenFluiddRespondInfo("external macro-PG106;manual command, not execute purge function")
        # else:
        #     #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
        #     self.G_PhrozenFluiddRespondInfo("external macro-PG106;cut filament before, first purge/spitresidual toolhead filament, preventcut into pellets")
        #     self.PG102Flag=True
        #     logging.info("self.Flag=True")
        #     command_string = """
        #     PG106
        #     """
        #     self.G_PhrozenGCode.run_script_from_command(command_string)
        #     self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
        #     self.PG102Flag=False
        #     logging.info("self.Flag=False")

        # #lancaigang241012:execute after side/face PG102
        # self.IfDoPG102Flag=True

        # #lancaigang240906:new AMS, cut filament after, retract on a time(s)channel a section distance
        # #lancaigang20231013:stm32filament change
        # #lancaigang231129:stm32internal filament change withklipperfilament change separate, causesstm32internal force filament change, andklipperif toolhead cut filament abnormal and no way to unload filament, causesklipper abnormal empty print
        # self.Cmds_AMSSerial1Send("G%d" % self.G_ChangeChannelTimeoutOldChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]G%d" % self.G_ChangeChannelTimeoutOldChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]AMSold channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutOldChan)

        # # #lancaigang240906:during onposition/bitmachine delay wait, stm32only responsible for purely change channel and print refill
        # # for i in range(5):#
        # #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]wait old channel retract")
        # #     self.G_ProzenToolhead.dwell(1.0)
        # #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]i=%d;T=%d" % (i,chan))

        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()
        #lancaigang240416:
        if self.G_SerialPort1OpenFlag == True:
            #lancaigang240913:resume time, purpose is repeat perform filament, can all retract all filament a section distance, prevent old channel retract abnormal, new channel load filament abnormal
            self.Cmds_AMSSerial1Send("AP")
            logging.info("Serial port 1 send command: AP;all channels retract some distance")
        #lancaigang241030:
        if self.G_SerialPort2OpenFlag == True:
            self.Cmds_AMSSerial2Send("AP")
            logging.info("Serial port 2 send command: AP;all channels retract some distance")


        # self.Cmds_AMSSerial1Send("G%d" % self.G_ChangeChannelTimeoutOldChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]G%d" % self.G_ChangeChannelTimeoutOldChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]AMSold channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutOldChan)

        # self.G_ProzenToolhead.dwell(5)


        # self.Cmds_AMSSerial1Send("G%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]G%d" % self.G_ChangeChannelTimeoutNewChan)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]AMSnew channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutNewChan)

        # self.G_ProzenToolhead.dwell(5)


        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]external macro-PG101")
        # command_string = """
        #     PG101
        #     """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperResume]external macro-tospecified wait area position wait purge;command_string='%s'" % command_string)
        # self.IfDoPG102Flag=True



        #lancaigang231216:if filament change during pointclick pause, justgood filament change during lift risezaxis, to execute pause when, zaxis height also save, causes overall height abnormal
        #lancaigang231216:ifzaxis lift rise without by lower down, need lower down again pause
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

        #lancaigang240920:resume retract filament after, clear flag
        #self.ToolheadCutFlag=False

        #lancaigang250519:
        self.G_PhrozenFluiddRespondInfo("external macro-PRZ_CUT_WAITINGAREA")
        command_string = """
            PRZ_CUT_WAITINGAREA
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position;command_string='%s'" % command_string)


        #lancaigang240913:delay timeplace/put to outside side/face
        self.G_ProzenToolhead.dwell(6)
        #lancaigang240911:Gcommand after delay5seconds check toolhead is not has filament
        #lancaigang231201:check cut filament after old channel filament is not normal unload filament, not normal then pause
        self.Cmds_CutFilaIfNormalCheck()
        #lancaigang240912:itself is pause, resume time will detect to is pause, here will causes directly return
        #lancaigang250109:because multi-colorMCresume need re-load filament.so cannot pause return
        # if self.G_KlipperIfPaused == True:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)]cut filament6secondstoolhead still detect to filament, cutter abnormal, please check cutter, pauseklipperprint")
        #     #Lo_ChangeChannelIfSuccess = False
        #     return
        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")


        #lancaigang250712:
        if self.G_ChangeChannelTimeoutOldChan==-1 and self.G_ChangeChannelTimeoutNewChan==-1:
            self.G_PhrozenFluiddRespondInfo("multi-color print, prepare print time pause, not way to record new old channel, ifP2A1normal, then resume directly, wait down acolor change command")
            if self.G_ToolheadIfHaveFilaFlag == False:
                self.G_PhrozenFluiddRespondInfo("toolhead retract past/over5seconds toolhead not yet detect to filament, indicates filament already retract, special situation resume;")
                #lancaigang240125:encapsulated function
                self.Cmds_PhrozenKlipperResumeCommon()
                self.G_ChangeChannelResumeFlag=False
                self.G_ChangeChannelFirstFilaFlag=True
                self.G_IfChangeFilaOngoing= False

                self.G_PhrozenFluiddRespondInfo("return")
                return



        #lancaigang250102:resume time, enable fan, prevent fan not rotate/switch situation
        #self.G_ProzenToolhead.dwell(0.5)
        self.G_PrintCountNum=self.G_PrintCountNum-1


        #lancaigang231115:change business logic;resume and resume print before channel
        #toolhead has filament
        if self.G_ToolheadIfHaveFilaFlag:
            self.G_PhrozenFluiddRespondInfo("toolhead has filament, can resume print")
            #lancaigang240323:first filament change, again resumebecome1time(s)channel handle
            self.Cmds_P1CnAutoChangeChannel(self.G_ChangeChannelTimeoutNewChan, self.G_ChangeChannelTimeoutNewGcmd)
            #lancaigang240325:change success, can performexecute/row data resume
            if self.G_MCModeCanResumeFlag == True:
                self.G_PhrozenFluiddRespondInfo("change success, can resume data")
                #lancaigang240125:encapsulated function
                self.Cmds_PhrozenKlipperResumeCommon()

                self.G_ProzenToolhead.dwell(1)
                self.G_ChangeChannelResumeFlag=False
                self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)
            else:
                self.G_PhrozenFluiddRespondInfo("filament change not success, cannot resume data")

                #lancaigang250527:pause to wait area
                self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
                command = """
                PRZ_PAUSE_WAITINGAREA
                """
                self.G_PhrozenGCode.run_script_from_command(command)
                self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))

                self.G_ProzenToolhead.dwell(1)
                self.G_ChangeChannelResumeFlag=False
                self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        #toolhead no filament
        else:
            self.G_PhrozenFluiddRespondInfo("toolhead no filament, re-execute filament change operation")
            #lancaigang240323:first filament change, again resumebecome1time(s)channel handle
            self.Cmds_P1CnAutoChangeChannel(self.G_ChangeChannelTimeoutNewChan, self.G_ChangeChannelTimeoutNewGcmd)
            #lancaigang240325:change success, can performexecute/row data resume
            if self.G_MCModeCanResumeFlag == True:
                self.G_PhrozenFluiddRespondInfo("change success, can resume data")
                #lancaigang240125:encapsulated function
                self.Cmds_PhrozenKlipperResumeCommon()

                self.G_ProzenToolhead.dwell(1)
                self.G_ChangeChannelResumeFlag=False
                self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)

            else:
                self.G_PhrozenFluiddRespondInfo("filament change not success, cannot resume data")

                #lancaigang250527:pause to wait area
                self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
                command = """
                PRZ_PAUSE_WAITINGAREA
                """
                self.G_PhrozenGCode.run_script_from_command(command)
                self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))

                #lancaigang240509:disabled
                # #lancaigang240426:resume failure, need on report pause
                # if len(self.G_PauseToLCDString)==0:
                #     #lancaigang0429:prevent multiple times report pause
                #     #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                #     self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
                self.G_ProzenToolhead.dwell(1)
                self.G_ChangeChannelResumeFlag=False
                self.G_PhrozenFluiddRespondInfo("+RESUME:0,%d" % self.G_ChangeChannelTimeoutNewChan)




        #lancaigang250102:resume time, enable fan, prevent fan not rotate/switch situation
        #self.G_ProzenToolhead.dwell(0.5)
        self.G_PrintCountNum=self.G_PrintCountNum-1
        #lancaigang250102:print filament change count calculation;1time(s)filament change not open/enable fan
        if self.G_PrintCountNum<=0:
            self.G_PrintCountNum=0
            self.G_PhrozenFluiddRespondInfo("Resume complete, first filament change - fan not enabled")
        else:
            command_string = """
                M106 S255
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("resume end, enable fan;command_string='%s'" % command_string)
            self.G_PhrozenFluiddRespondInfo("self.G_PrintCountNum='%d'" % self.G_PrintCountNum)
        #self.G_ProzenToolhead.dwell(0.5)


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Cmds_PhrozenKlipperPauseScreen(self, gcmd):
        _ = gcmd

        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperPauseScreen]")
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
        #klipperactive/manual pause
        logging.info("=====PAUSE=====")
        logging.info("=====PAUSE=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        logging.info("=====PAUSE=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)

        #lancaigang250527:quick pause execution
        self.G_KlipperQuickPause = False

        #lancaigang250516:purge in do not allow pause
        if self.PG102Flag==True:
            self.G_PhrozenFluiddRespondInfo("purge in, do not allow pause")
            #self.G_PhrozenFluiddRespondInfo("+PAUSE:10,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
            return



        #lancaigang231228:only whenMCmode only then allowZaxis action
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
            #lancaigang231216:if filament change during pointclick pause, justgood filament change during lift risezaxis, to execute pause when, zaxis height also save, causes overall height abnormal
            #lancaigang231216:ifzaxis lift rise without by lower down, need lower down again pause
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


        if self.G_ToolheadIfHaveFilaFlag==True:
            self.G_PhrozenFluiddRespondInfo("toolhead has filament, set resume without retract and reload")
            #lancaigang240116:MAmode need pausestm32
            if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:#MA
                if self.G_KlipperInPausing == False:
                    self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                    #lancaigang250607:
                    self.G_PhrozenFluiddRespondInfo("enable quick pause")
                    self.G_KlipperQuickPause = True
                    #lancaigang241012:temporarily not pause AMS
                    self.Cmds_PhrozenKlipperPause(None)
                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                else:
                    self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")

            #lancaigang240412:single-color mode, if ChromaKit connected load filament, need pause AMS
            elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:#M3
                if self.G_AMSDevice1IfNormal==True:
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, single-colorM3mode ChromaKit connected, need stm32also pause")
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        #lancaigang241012:temporarily not pause AMS
                        self.Cmds_PhrozenKlipperPause(None)
                        #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")
                else:
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament, single-colorM3mode withoutAMS multi-color, not need stm32pause")
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")

            else:#MC
                #lancaigang240427:disabled
                #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                #lancaigang240427:screen active/manual pause, also need stm32pause
                self.G_PhrozenFluiddRespondInfo("toolhead has filament, MCmulti-color mode ChromaKit connected, need stm32pause")
                if self.G_KlipperInPausing == False:
                    self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                    #lancaigang250607:
                    self.G_PhrozenFluiddRespondInfo("enable quick pause")
                    self.G_KlipperQuickPause = True
                    #lancaigang241012:temporarily not pause AMS
                    self.Cmds_PhrozenKlipperPause(None)
                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                else:
                    self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")


            self.G_IfToolheadHaveFilaInitiativePauseFlag  = True
        else:
            #lancaigang231216:if currently filament change process in active/manual pause, because filament change process in already lift risezaxis, resume time no way to resume this part zaxis height
            self.G_PhrozenFluiddRespondInfo("toolhead no filament, set resume needSTM32retract again load filament")
            if self.G_KlipperInPausing == False:
                self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                #lancaigang250607:
                self.G_PhrozenFluiddRespondInfo("enable quick pause")
                self.G_KlipperQuickPause = True
                #lancaigang241012:temporarily not pause AMS
                self.Cmds_PhrozenKlipperPause(None)
                #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
            else:
                self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")



        #lancaigang250527:pause to wait area
        self.G_PhrozenFluiddRespondInfo("start calling external macro-PRZ_PAUSE_WAITINGAREA")
        command = """
        PRZ_PAUSE_WAITINGAREA
        """
        self.G_PhrozenGCode.run_script_from_command(command)
        self.G_PhrozenFluiddRespondInfo("finished calling external macro:command=%s" % (command))

        self.G_PhrozenFluiddRespondInfo("touchscreen orfluiddweb page active/manual pause, pause")
        #self.G_PhrozenFluiddRespondInfo("+PAUSE:10,%d" % self.G_ChangeChannelTimeoutNewChan)
        self.G_PhrozenFluiddRespondInfo("+PAUSE:10,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))



    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    # PRZ_CANCEL cancel print
    def Cmds_PhrozenKlipperCancel(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperCancel]klippercancel print;")

        self.G_PhrozenFluiddRespondInfo("+CANCEL:0,%d" % self.G_ChangeChannelTimeoutNewChan)

        self.G_PhrozenFluiddRespondInfo("=====CANCEL=====")
        self.G_PhrozenFluiddRespondInfo("=====CANCEL=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        self.G_PhrozenFluiddRespondInfo("=====CANCEL=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)




        self.G_PhrozenFluiddRespondInfo("external macro:CANCEL_PRINT")
        #lancaigang240120:pause change usecfgconfigtable macro
        command = """
        CANCEL_PRINT
        """
        self.G_PhrozenGCode.run_script_from_command(command)
        self.G_PhrozenFluiddRespondInfo("calling macro:command=%s" % (command))


        #unlock
        self.Base_AMSSerialCmdUnlock()


        # #lancaigang231216:
        # eventtime = self.G_PhrozenReactor.monotonic()
        # # Determine "printing" status
        # idle_timeout = self.G_PhrozenPrinter.lookup_object("idle_timeout")
        # is_printing = idle_timeout.get_status(eventtime)["state"] == "Printing"
        # if is_printing:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperCancel]currently print in;command='%s'")
        # else:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperCancel]not yet during print in;command='%s;return'")
        #     return


        #lancaigang231207:+PAUSE:1load filament jammaterial flag
        self.G_IfInFilaBlockFlag=False
        #lancaigang240321:PG102process in pause flag
        self.PG102DelayPauseFlag=False
        #lancaigang240426:resume afterset position/bitfalse
        self.G_ResumeProcessCheckPauseStatus=False
        #lancaigang240410:
        self.G_CancelFlag=True
        #lancaigang240411:if without receivedP0 M3command, not use runout detection mechanism
        self.G_P0M3Flag = False

        self.ManualCmdFlag=False
        #lancaigang250805:cutter test
        self.G_CutCheckTest=False

        #lancaigang240427:AMS abnormal restart, need record
        self.G_AMS1ErrorRestartFlag = False
        self.G_AMS1ErrorRestartCount = 0

        #lancaigang241030:
        self.G_AMS2ErrorRestartFlag = False
        self.G_AMS2ErrorRestartCount = 0

        #lancaigang240124:stm32active/manual on report, enable can pause1time(s)
        self.STM32ReprotPauseFlag=0

        #lancaigang250526:
        self.G_IfToolheadHaveFilaInitiativePauseFlag=False
        #lancaigang250526:pausing, not allow new gcodecommand, need wait pause complete
        self.G_KlipperInPausing = False
        #lancaigang250527:quick pause execution
        self.G_KlipperQuickPause = False
        #lancaigang250607:print state;1-unload filament in;2-load filament in;3-print in;4-pause
        self.G_KlipperPrintStatus= -1
        self.G_ASM1DisconnectErrorCount=0
        #lancaigang250812:single-color runout detection, supplement carriage return to pause area
        self.G_RetryToPauseAreaFlag = False
        self.G_RetryToPauseAreaCount = 0
        self.G_P10SpitNum=0
        self.G_IfChangeFilaOngoing= False
        #lancaigang240223:toolhead cut failure flag
        self.ToolheadCutFlag = False





        #lancaigang250515:
        self.G_P0M1MCNoneAMS=0
        logging.info("self.G_P0M1MCNoneAMS=0")

        #lancaigang250515:clear LCD screen config data
        self.Cmds_GetUartScreenCfgClear()


        #lancaigang250807:cancel then clear pause state
        self.G_PhrozenPrinterCancelPauseResume.cmd_CLEAR_PAUSE(None)
        self.G_PhrozenFluiddRespondInfo("clear pause state")





        #lancaigang241016:
        #self.ToolheadCutFlag=False

        # #AMS multi-color emergency stop
        # #self.Cmds_CmdP4(None)
        # #lancaigang240125:
        # #lancaigang240507:not send pause command, sendM0command
        # #lancaigang240516:cancel, not execute resume print function
        # self.Cmds_AMSSerial1Send("AT+PAUSE")
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperCancel]AT+PAUSEpausestm32motor")

        # #klipperactive/manual pause
        # self.Cmds_PhrozenKlipperPause(None)
        # #cancelcancel command
        # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)

        self.G_ProzenToolhead.dwell(1.0)

        #lancaigang240416:
        #lancaigang240516:cancel, not execute resume print function
        # if self.G_SerialPort1OpenFlag == True:
        #     self.Cmds_AMSSerial1Send("M0")
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperCancel]send command:M0")

        # #AMS multi-color emergency stop
        # #self.Cmds_CmdP4(None)
        # #lancaigang240125:
        # #lancaigang240507:not send pause command, sendM0command
        # #lancaigang240516:cancel, not execute resume print function
        # self.Cmds_AMSSerial1Send("AT+PAUSE")
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_PhrozenKlipperCancel]AT+PAUSEpausestm32motor")

        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()

        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:
            self.G_PhrozenFluiddRespondInfo("Send command: MC multi-color - set AMS to idlemulti-color mode-MC-AMS idle mode")
            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MC")
                logging.info("Serial port 1 send command:MC")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MC")
                logging.info("Serial port 2 send command:MC")
        elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:
            self.G_PhrozenFluiddRespondInfo("send command:M2single-color refill mode-MA-AMS idle mode")
            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MA")
                self.G_PhrozenFluiddRespondInfo("Serial port 1 Send command: MC multi-color - set AMS to idle")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MA")
                self.G_PhrozenFluiddRespondInfo("Serial port 2 Send command: MC multi-color - set AMS to idle")
        elif self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:
            self.G_PhrozenFluiddRespondInfo("send command:M3single-color mode-MA-AMS idle mode")
            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("MA")
                self.G_PhrozenFluiddRespondInfo("Serial port 1 Send command: MC multi-color - set AMS to idle")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("MA")
                self.G_PhrozenFluiddRespondInfo("Serial port 2 Send command: MC multi-color - set AMS to idle")
        else:
            self.G_PhrozenFluiddRespondInfo("Unknown mode - pause AMS")

            #lancaigang241031:
            if self.G_SerialPort1OpenFlag == True:
                #lancaigang240516:Unknown mode - pause AMS
                self.Cmds_AMSSerial1Send("AT+PAUSE")
                logging.info("Serial port 1 sendAT+PAUSEpausestm32motor")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AT+PAUSE")
                logging.info("Serial port 2 sendAT+PAUSEpausestm32motor")


        #lancaigang241106:
        self.G_P0M2MAStartPrintFlag=0
        #lancaigang250104:P2A3flag
        self.G_P2A3Flag = 0

        #lancaigang250102:print layer calculation
        self.G_PrintCountNum=0


        #lancaigang20231013:disconnect connect
        #self.Device_DisconnectAMSDevice()
        #lancaigang250712:disabled, no need disconnect connect
        #lancaigang250815:not disabled, prevent cancel after serial port abnormal
        self.Cmds_CmdP29(None)

        #lancaigang250815:set mode to unknown
        self.G_AMSDeviceWorkMode = AMS_WORK_MODE_UNKNOW



        self.G_PhrozenFluiddRespondInfo("+CANCEL:1,%d" % self.G_ChangeChannelTimeoutNewChan)
