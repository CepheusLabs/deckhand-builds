import logging
import json
import time
import serial
from .base import *


class RunoutMixin:
    """Mixin for filament runout detection timer."""

    def Device_TimmerRunoutCheck(self, eventtime):
        #lancaigang240528:If it isP114Do not process during status readsmt32Report data
        if self.G_P114RunFlag>=1:
            self.G_P114RunFlag=self.G_P114RunFlag+1
            if self.G_P114RunFlag>=3:
                self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]P114Failed")
                #self.G_PhrozenFluiddRespondInfo("+P114:2")
                #self.G_P114RunFlag=0
                #pythonEmpty dictionary
                Lo_AMSDetailState = {"dev_id": -1, "active_dev_id": -1, "dev_mode": -1, "cache_empty": -1, "cache_full": -1, "cache_exist": -1, "mc_state": -1, "ma_state": -1, "entry_state": -1, "park_state": -1}
                # Response datajsonConvert
                self.G_PhrozenFluiddRespondInfo(json.dumps(Lo_AMSDetailState))

                #lancaigang250708：
                self.G_PhrozenFluiddRespondInfo("P114Failed")
                self.G_PhrozenFluiddRespondInfo("+P114:2")
                self.G_P114RunFlag=0
            

            #self.G_PhrozenFluiddRespondInfo("+P114:1")
            #self.G_P114RunFlag=False
            #return eventtime + AMS_FILA_RUNOUT_TIMER

        #Default to unknown mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#M0
            return eventtime + AMS_FILA_RUNOUT_TIMER


        #lancaigang240410：
        if self.G_CancelFlag==True:
            return eventtime + AMS_FILA_RUNOUT_TIMER



            


        #lancaigang240105If the previous print was standalone single-color and the current print uses single-color auto-refill, the toolhead will repeatedly error and pause when filament runs outM3 M2Handle separately
        # =====M3Filament runout handling mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_FILA_RUNOUT:#M3 M2
            #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]Single-color mode timer")
            #lancaigang240411If not receivedP0 M3Command mode - filament runout detection disabled
            if self.G_P0M3Flag == False:
                #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]Not receivedP0M3Command or hasAMSMulti-color mode - skip single-color logicM3Mode detection mechanism, usingAMSMulti-color printing in single-color mode")
                return eventtime + AMS_FILA_RUNOUT_TIMER
            #else:
                #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]NoneAMSMulti-color mode and receivedP0M3Command - execute single-colorM3Mode detection mechanism")

            if self.G_ToolheadIfHaveFilaFlag==True:
                self.G_ToolheadFirstInputFila = True
            if self.G_ToolheadFirstInputFila==False:
                self.G_PhrozenFluiddRespondInfo("Filament not detected on attempt1Load attempt")
                return eventtime + AMS_FILA_RUNOUT_TIMER
            if self.G_ToolheadIfHaveFilaFlag==True:
                if self.P0M3FilaRunoutSpittingFinished==True:#Purge complete
                    #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]Purge complete")
                    return eventtime + AMS_FILA_RUNOUT_TIMER
                self.G_PhrozenFluiddRespondInfo("Filament detected - starting purge")
                self.G_PhrozenFluiddRespondInfo("Call external macro-PG108-Single-colorM3Mode started purge but purge is disabled - skipping")
                #lancaigang240407Called before purge to prevent rapid load/unload cycling on the toolhead, which causes repeated command errors
                self.P0M3FilaRunoutSpittingFinished = True#Purge complete - prevent duplicate command calls
                # command = """
                #     G90
                #     G1 X250 Y10 F10000
                #     G91
                #     G1 Z10 F500
                #     G92 E0
                #     G1 E100 F500
                #     G92 E0
                #     G0
                # """
                # self.G_PhrozenGCode.run_script_from_command(command)
                # self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]command=%s" % command)
                if self.G_P0M3ToolheadHaveFilaNotSpittingFlag==True:
                    self.G_PhrozenFluiddRespondInfo("P0M3Toolhead already has filament on print start - skip purge")
                    self.G_P0M3ToolheadHaveFilaNotSpittingFlag=False
                else:
                    self.G_PhrozenFluiddRespondInfo("Skip auto-purge - user must manually resume before purging")
                    # command_string = """
                    # PG108
                    # """
                    # self.G_PhrozenGCode.run_script_from_command(command_string)
                    # self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                    # self.G_PhrozenFluiddRespondInfo("Purge complete and toolhead detects filament - resuming print")

                self.STM32ReprotPauseFlag=0
                return self.G_PhrozenReactor.NOW + AMS_FILA_RUNOUT_TIMER
            
            #lancaigang240108Cannot pause again if already paused
            if self.G_KlipperIfPaused==True:
                #lancaigang251127Suspected to causemcuErrortimer too close；
                #self.G_PhrozenFluiddRespondInfo("P0M3Standalone mode - already paused")
                if self.G_RetryToPauseAreaFlag==False:
                    self.G_RetryToPauseAreaCount=self.G_RetryToPauseAreaCount+1
                    self.G_PhrozenFluiddRespondInfo("self.G_RetryToPauseAreaCount=%d" % self.G_RetryToPauseAreaCount)
                    #lancaigang251124:Send multiple pause commands after pausing to ensure the filament runout pause actually stops the printer
                    if self.G_RetryToPauseAreaCount >= 6:
                        self.G_RetryToPauseAreaCount=0
                        self.G_RetryToPauseAreaFlag=True
                    else:
                        #lancaigang251124:
                        if self.G_PG108Ingoing==1:
                            self.G_PhrozenFluiddRespondInfo("PG108Filament ran out (Hall sensor lost detection) mid-purge")
                            self.G_PhrozenFluiddRespondInfo("PG108Can't pause mid-purge - the pause position would be recorded inside the purge area, causing a collision with the purge bin on resume")
                        else:
                            self.G_PhrozenFluiddRespondInfo("PG108Not purging - filament runout can trigger a normal pause")

                            if self.G_KlipperInPausing == True:
                                self.G_PhrozenFluiddRespondInfo("Already paused - duplicate pause not allowed")
                            else:
                                self.G_PhrozenFluiddRespondInfo("Not currently paused - pause allowed")
                                #lancaigang250527Pause at staging area
                                self.G_PhrozenFluiddRespondInfo("Starting external macro command call-PRZ_PAUSE_WAITINGAREA")
                                command = """
                                PRZ_PAUSE_WAITINGAREA
                                """
                                self.G_PhrozenGCode.run_script_from_command(command)
                                self.G_PhrozenFluiddRespondInfo("Finished calling external macro command:command=%s" % (command))
                
                return eventtime + AMS_FILA_RUNOUT_TIMER
            
            #lancaigang240407Pause if the toolhead has no filament
            if self.G_ToolheadIfHaveFilaFlag==False:
                self.G_PhrozenFluiddRespondInfo("P0M3Standalone mode - no filament detected")
                self.G_PhrozenFluiddRespondInfo("self.G_IfChangeFilaOngoing=%d" % self.G_IfChangeFilaOngoing)
                #lancaigang250522Not inAMSFilament runout detection is only active during multi-color loading
                if self.G_IfChangeFilaOngoing==False:
                    self.AMSRunoutPauseTimeCount = 0
                    self.G_PhrozenFluiddRespondInfo("StandaloneM3Single-color filament runout handling;Pause")
                    
                    # #cancelCancel command
                    # self.G_PhrozenPrinterCancelPauseResume.cmd_CANCEL_PRINT(None)
                    #lancaigang250517：
                    Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                    self.G_PhrozenFluiddRespondInfo("Current pause state-Lo_PauseStatus='%s'" % Lo_PauseStatus)

                    self.G_PhrozenFluiddRespondInfo("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                    #// Current pause state-Lo_PauseStatus='{'is_paused': True}'
                    if Lo_PauseStatus['is_paused'] == True:
                        self.G_PhrozenFluiddRespondInfo("Already in paused state")
                    else:
                        self.G_PhrozenFluiddRespondInfo("Not paused state")

                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("Fast pause disabled")
                        self.G_KlipperQuickPause = False

                        if self.G_KlipperInPausing == True:
                            self.G_PhrozenFluiddRespondInfo("Already paused - duplicate pause not allowed")
                        else:
                            self.G_PhrozenFluiddRespondInfo("Not currently paused - pause allowed")
                            #lancaigang251124:
                            if self.G_PG108Ingoing==1:
                                self.G_PhrozenFluiddRespondInfo("PG108Filament ran out (Hall sensor lost detection) mid-purge")
                                self.G_PhrozenFluiddRespondInfo("PG108Can't pause mid-purge - the pause position would be recorded inside the purge area, causing a collision with the purge bin on resume")
                            else:
                                self.G_PhrozenFluiddRespondInfo("PG108Not purging - filament runout can trigger a normal pause")

                                self.Cmds_PhrozenKlipperPauseM2M3ToSTM32(None)
                                #lancaigang250812:Single-color filament runout detected - refill and return to pause area
                                self.G_RetryToPauseAreaFlag = False
                                self.G_RetryToPauseAreaCount = 0
                                #lancaigang250527Pause at staging area
                                self.G_PhrozenFluiddRespondInfo("Starting external macro command call-PRZ_PAUSE_WAITINGAREA")
                                command = """
                                PRZ_PAUSE_WAITINGAREA
                                """
                                self.G_PhrozenGCode.run_script_from_command(command)
                                self.G_PhrozenFluiddRespondInfo("Finished calling external macro command:command=%s" % (command))
                                #lancaigang250521: has AMSMulti-color
                                #if self.G_AMSDevice1IfNormal==True or self.G_AMSDevice2IfNormal==True:
                                #    self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                                #else:
                                self.G_PhrozenFluiddRespondInfo("+PAUSE:b,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                                #lancaigang250527Pause at staging area
                                self.G_PhrozenFluiddRespondInfo("Starting external macro command call-PRZ_PAUSE_WAITINGAREA")
                                command = """
                                PRZ_PAUSE_WAITINGAREA
                                """
                                self.G_PhrozenGCode.run_script_from_command(command)
                                self.G_PhrozenFluiddRespondInfo("Finished calling external macro command:command=%s" % (command))

            self.P0M3FilaRunoutSpittingFinished = False#Wait for next purge
            return self.G_PhrozenReactor.NOW + AMS_FILA_RUNOUT_TIMER


        # #=====MASingle-color auto-refill
        # if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:#M2
        #     #lancaigang241106：P8Only run filament runout detection and refill after a successful load
        #     if self.G_P0M2MAStartPrintFlag==1:
        #         #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]P8Load successful - running filament runout detection and refill")
        #         #if self.G_ToolheadIfHaveFilaFlag==True:
        #         #    self.G_PhrozenFluiddRespondInfo("P8Load successful - toolhead has filament")
        #         if self.G_ToolheadIfHaveFilaFlag==False:
        #             self.G_PhrozenFluiddRespondInfo("P8After finishing a channel with no filament in the toolhead, auto-refill triggered for new channel but timed out waiting at the staging area")
        #             #self.Cmds_CmdP8(None)

        #             #lancaigang240104Pause not allowed during filament change
        #             if self.G_IfChangeFilaOngoing==False:
        #                 self.G_PhrozenFluiddRespondInfo("Single-color auto-refill temporarily paused, waitingstm32Load new filament")
        #                 #Toolhead has no filament, causingklipperPause
        #                 self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
        #                 self.AMSRunoutPauseTimeCount = 0
        #                 self.AMSRunoutPauseTimeoutFlag=0

        #     self.P0M3FilaRunoutSpittingFinished = False
        #     #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]return;self.P0M3FilaRunoutSpittingFinished = False")
        #     return self.G_PhrozenReactor.NOW + AMS_FILA_RUNOUT_TIMER




        #=====M2MASingle-color auto-refill
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MA:#M2
            #lancaigang250607Print state1-Unloading filament2-Loading filament3-Printing in progress4-Pause
            if self.G_KlipperPrintStatus == 3:
                #lancaigang250619:Start counting if serial port errors are detected
                if self.G_SerialPort1OpenFlag==False:
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refill printingif self.G_KlipperPrintStatus == 3")
                    self.G_ASM1DisconnectErrorCount=self.G_ASM1DisconnectErrorCount+1
                    self.G_PhrozenFluiddRespondInfo("self.G_ASM1DisconnectErrorCount=%d" % self.G_ASM1DisconnectErrorCount)
                    if self.G_ASM1DisconnectErrorCount >= 2: #4s
                        try:
                            self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1")
                            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
                            #Serial port opened successfully
                            if self.G_SerialPort1Obj is not None:
                                if self.G_SerialPort1Obj.is_open:
                                    self.G_SerialPort1OpenFlag = True
                                    self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1Success")
                                    self.G_ASM1DisconnectErrorCount=0
                                    #self.G_PauseToLCDString=""
                                    #lancaigang231213Open serial port
                                    self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                                    self.G_SerialPort1Obj.flush()
                                    self.G_PhrozenFluiddRespondInfo("Serial port1Clear")
                                    self.G_PhrozenFluiddRespondInfo("Re-register serial port1Callback function")
                                    self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
                        except:
                            self.G_PhrozenFluiddRespondInfo("Failed to opentty1Port - please checkUSBPort or restart attempt")
                            self.G_SerialPort1OpenFlag=False
                            self.G_ASM1DisconnectErrorCount=self.G_ASM1DisconnectErrorCount+1
                            self.G_PhrozenFluiddRespondInfo("self.G_ASM1DisconnectErrorCount=%d" % self.G_ASM1DisconnectErrorCount)
                            if self.G_ASM1DisconnectErrorCount >= 5: #10s
                                self.G_ASM1DisconnectErrorCount=0
                                self.G_PhrozenFluiddRespondInfo("AMS1Connection lost filament exceeded10sPausing")
                                if self.G_KlipperIfPaused==False:
                                    self.G_KlipperIfPaused = True
                                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                                    if self.G_CancelFlag==False:
                                        self.G_PhrozenFluiddRespondInfo("AMS1Connection error - pausing")
                                        #lancaigang250604:
                                        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#M0
                                            self.G_PhrozenFluiddRespondInfo("Unknown mode - no pause needed")
                                        else:
                                            if self.STM32ReprotPauseFlag==0:
                                                self.G_PauseTriggerWhileChangeChannelFlag=True
                                                if self.PG102Flag==True:
                                                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                                                    self.PG102DelayPauseFlag=True
                                                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                                                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                                                else:
                                                    self.G_PhrozenFluiddRespondInfo("Not purging - can pause immediately")


                                                    if self.G_KlipperInPausing == False:
                                                        self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                                                        #lancaigang250607:
                                                        self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                                                        self.G_KlipperQuickPause = True
                                                        #klipperActive pause
                                                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                                                    else:
                                                        self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

                                                    
                                                    self.G_KlipperIfPaused = True
                                                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                                                    self.STM32ReprotPauseFlag=1
                                                    #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                                                    self.G_ChangeChannelFirstFilaFlag=True
                                                    self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                                                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                                            else:
                                                self.G_PauseTriggerWhileChangeChannelFlag=True
                                                self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


                                #if self.G_KlipperIfPaused==True:
                                else:
                                    self.G_PhrozenFluiddRespondInfo("USBError - already in paused state")
                                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


            #lancaigang241106：P8Only run filament runout detection and refill after a successful load
            if self.G_P0M2MAStartPrintFlag==1:
                #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]P8Load successful - running filament runout detection and refill")
                #if self.G_ToolheadIfHaveFilaFlag==True:
                #    self.G_PhrozenFluiddRespondInfo("P8Load successful - toolhead has filament")
                # if self.G_ToolheadIfHaveFilaFlag==False:
                #     self.G_PhrozenFluiddRespondInfo("P8After finishing a channel with no filament in the toolhead, auto-refill triggered for new channel but timed out waiting at the staging area")
                    #self.Cmds_CmdP8(None)
                ##1Filament entry detected - start tracking whether the toolhead has filament
                if self.G_ToolheadIfHaveFilaFlag==True:
                    #Toolhead attempt1Filament detected on attempt
                    self.G_ToolheadFirstInputFila = True
                # #1No filament manually inserted after N attempts - returning
                if self.G_ToolheadFirstInputFila==False:
                    #Filament runout handling;No initial filament feed has occurred yet;if not self.G_ToolheadFirstInputFila:")
                    return eventtime + AMS_FILA_RUNOUT_TIMER
                
                if self.G_ToolheadIfHaveFilaFlag==True:
                    #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]if self.G_ToolheadIfHaveFilaFlag==True:")
                    
                    if self.P0M3FilaRunoutSpittingFinished==True:
                        #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]return;if self.P0M3FilaRunoutSpittingFinished==True:")
                        #lancaigang241106Once the toolhead detects filament, if it remains detected continuously, do not proceed further
                        return eventtime + AMS_FILA_RUNOUT_TIMER
                    else:
                        self.P0M3FilaRunoutSpittingFinished = True

                    #lancaigang240123After final filament-empty timeout on reload, do not allow automatic resume
                    if self.AMSRunoutPauseTimeoutFlag==1:
                        #lancaigang240221After toolhead empty timeout, the user must manually press the resume button
                        #self.AMSRunoutPauseTimeoutFlag=0
                        self.G_PhrozenFluiddRespondInfo("Single-color auto-refill timed out - will not auto-resume, manual resume required")
                        return eventtime + AMS_FILA_RUNOUT_TIMER
                    
                    self.G_PhrozenFluiddRespondInfo("Single-color auto-refill: toolhead transitioned from no-filament to filament-detected, resuming print")

                    if self.AMSRunoutPauseTimeCount>0:
                        self.G_PhrozenFluiddRespondInfo("AMSRunoutPauseTimeCount=%d" % self.AMSRunoutPauseTimeCount)
                        self.AMSRunoutPauseTimeCount=0
                        self.G_M2MAModeResumeFlag=True
                    #lancaigang241106：count as 0Or timeout as0
                    else:
                        self.G_PhrozenFluiddRespondInfo("AMSRunoutPauseTimeCount=%d" % self.AMSRunoutPauseTimeCount)
                        if self.G_KlipperIfPaused == True:
                            self.G_PhrozenFluiddRespondInfo("Already paused - manual resume required")
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #lancaigang240108Single-color auto-refill load succeeded, load state normal - safe to restore data
                    if self.G_M2MAModeResumeFlag==True:
                        #self.Cmds_AMSSerial1Send("FA")
                        #self.G_PhrozenFluiddRespondInfo("Single-color auto-refill:FA；stm32Load new filament")
                        self.G_PhrozenFluiddRespondInfo("Single-color auto-refill: resuming print")
                        #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]if self.G_M2MAModeResumeFlag==True:")
                        #lancaigang250611：
                        # self.G_PhrozenFluiddRespondInfo("External macro command-PG108-Heat up, purge, and wipe nozzle")
                        # command_string = """
                        #     PG108
                        #     """
                        # self.G_PhrozenGCode.run_script_from_command(command_string)
                        #lancaigang250619:CheckAMSCheck if reconnection succeeded
                        self.Cmds_USBConnectErrorCheck()
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                            self.G_PhrozenFluiddRespondInfo("Serial port1-AMSStart buffer-full duration timer")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            self.G_PhrozenFluiddRespondInfo("Serial port2-AMSStart buffer-full duration timer")
                        #self.G_ProzenToolhead.dwell(1)
                        #lancaigang250522：
                        self.G_PhrozenFluiddRespondInfo("External macro command-PG109-Heat up")
                        command_string = """
                            PG109
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("External macro command-PG109-Heating upcommand_string='%s'" % command_string)
                        #lancaigang251120Set flag on purge entry to preventPG108Hall sensor lost filament during purge causing pause inside purge area - toolhead would collide with purge bin on resume
                        self.G_PG108Ingoing=1
                        #lancaigang250611：
                        self.G_PhrozenFluiddRespondInfo("External macro command-PG108-Heat up, purge, and wipe nozzle")
                        command_string = """
                            PG108
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        #lancaigang250427：
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            self.G_PhrozenFluiddRespondInfo("Serial port1-AMSStop buffer-full duration timer")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            self.G_PhrozenFluiddRespondInfo("Serial port2-AMSStop buffer-full duration timer")
                        
                        #lancaigang251124Ifstm32Pause error pending - cannot resume print
                        if self.STM32ReprotPauseFlag == 1:
                            self.G_PhrozenFluiddRespondInfo("Auto-refill mode detected filament present, but during purgeSTM32MCU reported a pause - cannot auto-resume")
                            #lancaigang240125Wrapper function
                            #self.Cmds_PhrozenKlipperResumeCommon()

                            if self.G_KlipperInPausing == False:
                                self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                                #lancaigang250607:
                                self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                                self.G_KlipperQuickPause = True
                                #klipperActive pause
                                self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                            else:
                                self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

                            
                            self.G_KlipperIfPaused = True
                            #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                            self.STM32ReprotPauseFlag=1
                            #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                            self.G_ChangeChannelFirstFilaFlag=True
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                            #lancaigang241106：
                            self.G_P0M2MAStartPrintFlag=0
                        else:
                            self.G_PhrozenFluiddRespondInfo("Toolhead has filament - resuming")
                            self.G_M2MAModeResumeFlag=False
                            #lancaigang240125Wrapper function
                            self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_KlipperIfPaused = False
                            #lancaigang240124：stm32MCU actively reported status - pause is now allowed1 time(s)
                            self.STM32ReprotPauseFlag=0

                        #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]self.G_KlipperIfPaused = False")
                        self.G_PhrozenFluiddRespondInfo("+RESUME:2,%d" % self.G_ChangeChannelTimeoutNewChan)

                    #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]return self.G_PhrozenReactor.NOW + AMS_FILA_RUNOUT_TIMER")
                    #lancaigang240109Changed toeventtime
                    return self.G_PhrozenReactor.NOW + AMS_FILA_RUNOUT_TIMER
                    #return eventtime + AMS_FILA_RUNOUT_TIMER
                


                #lancaigang240108Cannot pause again if already paused
                if self.G_KlipperIfPaused==True:
                    self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]Single-color auto-refill: temporarily paused, waitingstm32Load new filament again")
                    #lancaigang240224：
                    if self.AMSRunoutPauseTimeCount==0:
                        #lancaigang240122Immediately send command after pause tostm32Load new filament
                        #time.sleep(1)
                        #self.G_ProzenToolhead.dwell(0.5)

                        #self.Cmds_AMSSerial1Send("FA")
                        #lancaigang241106:
                        self.G_PhrozenFluiddRespondInfo("After single-color auto-refill temporary pause,P8Infila；stm32Load new filament")

                        #lancaigang240511Re-initialize the serial port on every resume to handle hot-plug scenariosAMSCaused serial communication error
                        try:
                            self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1")
                            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
                            #Serial port opened successfully
                            if self.G_SerialPort1Obj is not None:
                                if self.G_SerialPort1Obj.is_open:
                                    self.G_SerialPort1OpenFlag = True
                                    self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1Success")
                                    #lancaigang231213Open serial port
                                    self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                                    self.G_SerialPort1Obj.flush()
                                    self.G_PhrozenFluiddRespondInfo("Serial port1Clear")
                                    self.G_PhrozenFluiddRespondInfo("Re-register serial port1Callback function")
                                    self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
                        except:
                            self.G_PhrozenFluiddRespondInfo("Failed to opentty1Port - please checkUSBPort or restart attempt")
                        try:
                            self.G_PhrozenFluiddRespondInfo("[(cmds.py)Cmds_PhrozenKlipperResume]Re-initialize serial port2")
                            self.G_SerialPort2Obj = serial.Serial(self.G_Serialport2Define, SERIAL_PORT_BAUD, timeout=3)
                            #Serial port opened successfully
                            if self.G_SerialPort2Obj is not None:
                                if self.G_SerialPort2Obj.is_open:
                                    self.G_SerialPort2OpenFlag = True
                                    self.G_PhrozenFluiddRespondInfo("Re-initialize serial port2Success")
                                    self.G_SerialPort2Obj.flushInput()  # clean serial write cache
                                    self.G_SerialPort2Obj.flush()
                                    self.G_PhrozenFluiddRespondInfo("Serial port2Clear")
                                    self.G_PhrozenFluiddRespondInfo("Re-register serial port2Callback function")
                                    self.G_SerialPort2RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart2Recv, self.G_PhrozenReactor.NOW)
                        except:
                            self.G_PhrozenFluiddRespondInfo("Failed to opentty2Port - please checkUSBPort or restart attempt")
                        #lancaigang250515Re-load filament
                        self.Cmds_CmdP8Infila()

                    #lancaigang240122Pause durationsTimer waiting for new filament
                    self.AMSRunoutPauseTimeCount=self.AMSRunoutPauseTimeCount+1
                    self.G_PhrozenFluiddRespondInfo("AMSRunoutPauseTimeCount=%d" % self.AMSRunoutPauseTimeCount)

                    #Waitstm32During filament load, if the toolhead detects filament the new filament has arrived and printing can resume
                    if self.G_ToolheadIfHaveFilaFlag==True:
                        self.G_M2MAModeResumeFlag=True
                        self.AMSRunoutPauseTimeCount=0

                        #lancaigang250619:CheckAMSCheck if reconnection succeeded
                        self.Cmds_USBConnectErrorCheck()
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                            self.G_PhrozenFluiddRespondInfo("Serial port1-AMSStart buffer-full duration timer")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                            self.G_PhrozenFluiddRespondInfo("Serial port2-AMSStart buffer-full duration timer")

                        #lancaigang251120Set flag on purge entry to preventPG108Hall sensor lost filament during purge causing pause inside purge area - toolhead would collide with purge bin on resume
                        self.G_PG108Ingoing=1
                        #lancaigang250611：
                        self.G_PhrozenFluiddRespondInfo("External macro command-PG108-Heat up, purge, and wipe nozzle")
                        command_string = """
                            PG108
                            """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PG108Ingoing=0
                        #lancaigang250427：
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            self.G_PhrozenFluiddRespondInfo("Serial port1-AMSStop buffer-full duration timer")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            self.G_PhrozenFluiddRespondInfo("Serial port2-AMSStop buffer-full duration timer")


                        #lancaigang251124Ifstm32Pause error pending - cannot resume print
                        if self.STM32ReprotPauseFlag == 1:
                            self.G_PhrozenFluiddRespondInfo("Auto-refill mode detected filament present, but during purgeSTM32MCU reported a pause - cannot auto-resume")
                            #lancaigang240125Wrapper function
                            #self.Cmds_PhrozenKlipperResumeCommon()

                            if self.G_KlipperInPausing == False:
                                self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                                #lancaigang250607:
                                self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                                self.G_KlipperQuickPause = True
                                #klipperActive pause
                                self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                            else:
                                self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")
                            
                            self.G_KlipperIfPaused = True
                            #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                            self.STM32ReprotPauseFlag=1
                            #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                            self.G_ChangeChannelFirstFilaFlag=True
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                            #lancaigang241106：
                            self.G_P0M2MAStartPrintFlag=0
                        else:
                            # self.G_PhrozenFluiddRespondInfo("Toolhead has filament - resuming")
                            # self.G_M2MAModeResumeFlag=False
                            # #lancaigang240125Wrapper function
                            # self.Cmds_PhrozenKlipperResumeCommon()
                            # self.G_KlipperIfPaused = False
                            # #lancaigang240124：stm32MCU actively reported status - pause is now allowed1 time(s)
                            # self.STM32ReprotPauseFlag=0

                            #lancaigang240125Wrapper function
                            self.Cmds_PhrozenKlipperResumeCommon()
                            self.G_PhrozenFluiddRespondInfo("MASingle-color auto-refill: toolhead detected filament, auto-resuming print")
                            self.G_KlipperIfPaused = False
                            #lancaigang240124：stm32MCU actively reported status - pause is now allowed1 time(s)
                            self.STM32ReprotPauseFlag=0

                    if self.AMSRunoutPauseTimeCount>=50:
                        self.AMSRunoutPauseTimeCount=0
                        self.AMSRunoutPauseTimeoutFlag=1
                        #self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                        self.G_PhrozenFluiddRespondInfo("M2MASingle-color auto-refill:stm32New filament load timed out100s")
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        
                    return eventtime + AMS_FILA_RUNOUT_TIMER

                #lancaigang241106:
                if self.G_ToolheadIfHaveFilaFlag==False:
                    #lancaigang240104Pause not allowed during filament change
                    if self.G_IfChangeFilaOngoing==False:
                        self.G_PhrozenFluiddRespondInfo("M2MASingle-color auto-refill temporarily paused, waitingstm32Load new filament")

                        if self.G_KlipperInPausing == False:
                            self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                            #lancaigang250607:
                            #self.G_PhrozenFluiddRespondInfo("Fast pause enabled")
                            #self.G_KlipperQuickPause = True
                            #Toolhead has no filament, causingklipperPause
                            self.Cmds_PhrozenKlipperPauseMAToSTM32(None)
                        else:
                            self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")

                        


                        self.AMSRunoutPauseTimeCount = 0
                        self.AMSRunoutPauseTimeoutFlag=0

            self.P0M3FilaRunoutSpittingFinished = False


            



            return eventtime + AMS_FILA_RUNOUT_TIMER
            #return self.G_PhrozenReactor.NOW + AMS_FILA_RUNOUT_TIMER





        # =====M1MCMulti-color mode
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:#M1
            #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_MC:")
            #self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_TimmerRunoutCheck]Filament runout handling;Detection handling in multi-color mode")

            #lancaigang240407In multi-color mode, pause if the toolhead loses filament during printing
            #lancaigang240527Not emptynoneCan confirm that it was receivedP1CnCommand sent
            # if self.G_ChangeChannelTimeoutOldGcmd is not None:
            #     if self.G_ToolheadIfHaveFilaFlag==False:
            #         if self.G_ToolheadIfHaveFilaFlag==False:
            #             self.G_PhrozenFluiddRespondInfo("[(cmds.python)Device_TimmerRunoutCheck]MCToolhead lost filament during multi-color print")

            #lancaigang250607Print state1-Unloading filament2-Loading filament3-Printing in progress4-Pause
            if self.G_KlipperPrintStatus == 3:
                
                #lancaigang250619:Start counting if serial port errors are detected
                if self.G_SerialPort1OpenFlag==False:
                    self.G_PhrozenFluiddRespondInfo("Multi-color printing in progressif self.G_KlipperPrintStatus == 3")
                    self.G_ASM1DisconnectErrorCount=self.G_ASM1DisconnectErrorCount+1
                    self.G_PhrozenFluiddRespondInfo("Multi-color attempting to reconnectself.G_ASM1DisconnectErrorCount=%d" % self.G_ASM1DisconnectErrorCount)
                    #lancaigang250619:CheckAMSCheck if reconnection succeeded
                    self.Cmds_USBConnectErrorCheck()

                    if self.G_ASM1DisconnectErrorCount >= 5: #10s
                        try:
                            self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1")
                            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
                            #Serial port opened successfully
                            if self.G_SerialPort1Obj is not None:
                                if self.G_SerialPort1Obj.is_open:
                                    self.G_SerialPort1OpenFlag = True
                                    self.G_PhrozenFluiddRespondInfo("Re-initialize serial port1Success")
                                    self.G_ASM1DisconnectErrorCount=0
                                    #self.G_PauseToLCDString=""
                                    #lancaigang231213Open serial port
                                    self.G_SerialPort1Obj.flushInput()  # clean serial write cache
                                    self.G_SerialPort1Obj.flush()
                                    self.G_PhrozenFluiddRespondInfo("Serial port1Clear")
                                    self.G_PhrozenFluiddRespondInfo("Re-register serial port1Callback function")
                                    self.G_SerialPort1RecvTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerUart1Recv, self.G_PhrozenReactor.NOW)
                        except:
                            self.G_PhrozenFluiddRespondInfo("Failed to opentty1Port - please checkUSBPort or restart attempt")
                            self.G_SerialPort1OpenFlag=False
                            self.G_ASM1DisconnectErrorCount=self.G_ASM1DisconnectErrorCount+1
                            self.G_PhrozenFluiddRespondInfo("self.G_ASM1DisconnectErrorCount=%d" % self.G_ASM1DisconnectErrorCount)
                            if self.G_ASM1DisconnectErrorCount >= 20: #40s
                                self.G_ASM1DisconnectErrorCount=0
                                self.G_PhrozenFluiddRespondInfo("AMS1Connection lost filament exceeded40sPausing")
                                if self.G_KlipperIfPaused==False:
                                    self.G_KlipperIfPaused = True
                                    #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                                    if self.G_CancelFlag==False:
                                        self.G_PhrozenFluiddRespondInfo("AMS1Connection error - pausing")
                                        #lancaigang250604:
                                        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:#M0
                                            self.G_PhrozenFluiddRespondInfo("Unknown mode - no pause needed")
                                        else:
                                            if self.STM32ReprotPauseFlag==0:
                                                self.G_PauseTriggerWhileChangeChannelFlag=True
                                                if self.PG102Flag==True:
                                                    self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                                                    self.PG102DelayPauseFlag=True
                                                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                                                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                                                else:
                                                    self.G_PhrozenFluiddRespondInfo("Not purging - can pause immediately")
                                                    if self.PG102Flag==True:
                                                        self.G_PhrozenFluiddRespondInfo("Purge in progress - defer pause until purge completes")
                                                        self.PG102DelayPauseFlag=True
                                                        self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                                                    else:
                                                        if self.G_KlipperInPausing == False:
                                                            self.G_PhrozenFluiddRespondInfo("Not currently paused - new pause allowed")
                                                            self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                                                            self.G_KlipperIfPaused = True
                                                            #self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                                                            self.STM32ReprotPauseFlag=1
                                                            #lancaigang231202：P1 C?During auto filament change, if channel1Paused due to load failure on this channel - on resume, continue from channel1Starting channel attempt
                                                            self.G_ChangeChannelFirstFilaFlag=True
                                                            self.G_PhrozenFluiddRespondInfo("+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                                                            self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                                                        else:
                                                            self.G_PhrozenFluiddRespondInfo("Already paused - new pause not allowed")
                                            else:
                                                self.G_PauseTriggerWhileChangeChannelFlag=True
                                                self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


                                #if self.G_KlipperIfPaused==True:
                                else:
                                    self.G_PhrozenFluiddRespondInfo("USBError - already in paused state")
                                    self.G_PauseToLCDString="+PAUSE:g,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)


            return eventtime + AMS_FILA_RUNOUT_TIMER

        # Multiple safety checks, Safeguard against the above conditions failing,Timer stopped
        return eventtime + AMS_FILA_RUNOUT_TIMER
    
