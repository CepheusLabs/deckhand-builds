import logging
import time
from .base import *


class ChannelChangeMixin:
    """Mixin for filament channel change operations."""

    #filament change channel
    def Cmds_P1TnManualChangeChannel(self, chan, gcmd):
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_P1TnManualChangeChannel]")

        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("gcmd is None")
            #self.G_PhrozenFluiddRespondInfo("return")
            #return
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("gcmd is not None:")
            self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_P1TnManualChangeChannel]cmd='%s'" % (gcmd.get_commandline()))

        # #lancaigang20231101:first judge toolhead is not has filament, has then first unload filament
        # if self.G_ToolheadIfHaveFilaFlag:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]toolhead has filament, retract first to prevent clog;cmd='%s'" % (gcmd.get_commandline()))
        #     #// all retract to park position;//===== P2 A1 all filament to park position for print Yes;"AP";
        #     self.Cmds_AMSSerial1Send("AP")
        #     self.G_PhrozenFluiddRespondInfo("send command: AP, all retract to park position")


        #lancaigang231216:manual filament change also recordgcodechannel and command
        #get channelnumber andgcmdobject
        #self.G_ChangeChannelTimeoutOldChan=chan
        #self.G_ChangeChannelTimeoutOldGcmd=gcmd


        self.G_IfChangeFilaOngoing= True

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))



        #lancaigang240229:prevent send command packet concatenation
        #time.sleep(1)
        self.G_ProzenToolhead.dwell(0.5)

        #lancaigang250619:Check if AMS reconnected successfully
        self.Cmds_USBConnectErrorCheck()

        #lancaigang240223:if cut filament failure, onfunction alreadyZaxis down lower
        if self.ToolheadCutFlag==True:
            self.ToolheadCutFlag=False
            self.G_PhrozenFluiddRespondInfo("before cut filament abnormal, filament change failure")
            self.G_ChangeChannelFirstFilaFlag=True
            self.G_IfChangeFilaOngoing= False

            #stm32on report pause only can pause1time(s), cannot repeat pause
            self.STM32ReprotPauseFlag=1
            #lancaigang231202:P1 C?auto filament change when, if1time(s)channel then load filament abnormal pause, if need resume, also continue from1time(s)channel start
            self.G_ChangeChannelFirstFilaFlag=True

            # #lancaigang250308:resume itself already cut filament abnormal, here also report cut filament abnormal
            # #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d" % self.G_ChangeChannelTimeoutNewChan)
            # #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
            # if len(self.G_PauseToLCDString)==0:
            #     self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
            # else:
            #     self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

            self.G_PauseToLCDString="+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)

            #lancaigang240416:
            if self.G_SerialPort1OpenFlag == True:
                #lancaigang240603:preventAMSalwaysstop not
                self.Cmds_AMSSerial1Send("AT+PAUSE")
                logging.info("serial port1-AT+PAUSEpausestm32motor")
            #lancaigang241030:
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AT+PAUSE")
                logging.info("serial port2-AT+PAUSEpausestm32motor")

            if self.G_KlipperInPausing == False:
                self.G_PhrozenFluiddRespondInfo("not pausing, allow new pause")
                #lancaigang250607:
                self.G_PhrozenFluiddRespondInfo("enable quick pause")
                self.G_KlipperQuickPause = True
                #klipperactive/manual pause
                self.Cmds_PhrozenKlipperPause(None)
            else:
                self.G_PhrozenFluiddRespondInfo("pausing, not allow new pause")

            self.G_KlipperIfPaused = True

            #lancaigang240325:change failed, cannot execute resume
            self.G_MCModeCanResumeFlag = False

            #lancaigang240524:use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+T:1,%d" % self.G_ChangeChannelTimeoutNewChan)

            #lancaigang250529:
            if len(self.G_PauseToLCDString)==0:
                self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
            else:
                self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

            self.G_PhrozenFluiddRespondInfo("return")
            return

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

        #lancaigang241030:
        if self.G_ChangeChannelTimeoutNewChan in range(1, 5):
            #lancaigang240911:new AMSsectioncodescreen, T?command purely load filament
            #send manual change command
            self.Cmds_AMSSerial1Send("T%d" % self.G_ChangeChannelTimeoutNewChan)
            logging.info("serial port1change send command: T%d" % self.G_ChangeChannelTimeoutNewChan)
            #lancaigang240524:use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+T:0,%d" % self.G_ChangeChannelTimeoutNewChan)
        elif self.G_ChangeChannelTimeoutNewChan in range(5, 9):
            self.Cmds_AMSSerial2Send("T%d" % self.G_ChangeChannelTimeoutNewChan-4)
            logging.info("serial port2change send command: T%d" % self.G_ChangeChannelTimeoutNewChan-4)
            self.G_PhrozenFluiddRespondInfo("+T:0,%d" % self.G_ChangeChannelTimeoutNewChan-4)

        #lancaigang250322:
        if self.ManualCmdFlag==True:
            self.G_PhrozenFluiddRespondInfo("external macro-PG105;manual command, not execute purge function")
            self.IfDoPG102Flag=True
        #lancaigang250805:cutter test
        elif self.G_CutCheckTest == True:
            #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
            self.G_PhrozenFluiddRespondInfo("external macro-PG105;cut filament after, toolhead heat up simultaneouslyAMSperform filament")
            self.PG102Flag=True
            self.IfDoPG102Flag=True
            logging.info("self.Flag=True")
            command_string = """
            PG105
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
            self.PG102Flag=False
            logging.info("self.Flag=False")
        else:
            #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
            self.G_PhrozenFluiddRespondInfo("external macro-PG105;cut filament after, toolhead heat up simultaneouslyAMSperform filament")
            self.PG102Flag=True
            self.IfDoPG102Flag=True
            logging.info("self.Flag=True")
            command_string = """
            PG105
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
            self.PG102Flag=False
            logging.info("self.Flag=False")

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

        #lancaigang240328:manual command skip purge
        if self.ManualCmdFlag==True:
            self.G_PhrozenFluiddRespondInfo("external macro-PG110;manual command, not execute")
            self.IfDoPG102Flag=True
        #lancaigang250805:cutter test
        elif self.G_CutCheckTest == True:
            #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
            self.G_PhrozenFluiddRespondInfo("external macro-PG110;STM32 load filament after, klipper start purgecatch/connect hold load filament")
            self.PG102Flag=True
            self.IfDoPG102Flag=True
            logging.info("self.Flag=True")
            command_string = """
            PG110
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
            self.PG102Flag=False
            logging.info("self.Flag=False")
        else:
            #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
            self.G_PhrozenFluiddRespondInfo("external macro-PG110;STM32 load filament after, klipper start purgecatch/connect hold load filament")
            self.PG102Flag=True
            self.IfDoPG102Flag=True
            logging.info("self.Flag=True")
            command_string = """
            PG110
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
            self.PG102Flag=False
            logging.info("self.Flag=False")

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))
        # #lancaigang240328:manual command skip purge
        # if self.ManualCmdFlag==True:
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)]external macro-PG110;manual command, not execute")
        # else:
        #     #lancaigang240319:cutcomplete after, first purge/spitresidual toolhead filament, preventcut into pellets
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)]external macro-PG110;STM32 load filament after, klipperimmediately start purge")
        #     self.PG102Flag=True
        #     self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=True")
        #     command_string = """
        #     PG110
        #     """
        #     self.G_PhrozenGCode.run_script_from_command(command_string)
        #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command_string='%s'" % command_string)
        #     self.PG102Flag=False
        #     self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=False")



        # #lancaigang240226:cut filament afterAMS mainboard retract filament, delay after toolhead retract20mm
        # time.sleep(2)
        # #lancaigang231208:Ehead-negative retract, press/extrude outhead retract filament
        # command_string = """
        # G92 E0
        # G1 E0.0000 F600
        # G91
        # G1 E-50 F8000
        # """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]delay2s;Enegative toolhead retract filament50mm;GCODEcommand:command_string='%s'" % command_string)


        #lancaigang20231013:8
        #lancaigang231115:temporarily not useprinter.cfgconfig timeout, usepythoninternaldefaultfixed/setdefine timeout
        timeout = self.G_DictChangeChannelWaitAreaParam["T"] - 8

        # #lancaigang240125:wait filament change during, zaxis lift rise after again down lower
        # #lancaigang231208:zaxis+positive will toward on
        # command_string = """
        #     G91
        #     G1 Z%f F8000
        #     """ % (
        #     self.G_AMSFilaCutZPositionLiftingUp,
        # )
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]Zaxis on lift up height/high;gcodecommand=%s" % command_string)


        #lancaigang240619:
        # #lancaigang240306:moved to cut filament code
        # #lancaigang240110:wait area zone wait before, first execute external macro, move tospecial fixed/set position performexecute/row wait
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]external macro-PG101")
        # command_string = """
        #     PG101
        #     """
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]external macro;command_string='%s'" % command_string)
        # self.IfDoPG102Flag=True


        #lancaigang240223:because resume time, directly run/move toP9wait area, not lift rise may will causesscrape tomodel/mold type/model
        command_string = """
                        G90
                        G91
                        G1 Z%f F8000
                        """ % (
                        self.G_AMSFilaCutZPositionLiftingUp,
                    )
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.Lo_ThisIfZPositionLiftUpFlag = True
        self.G_PhrozenFluiddRespondInfo("Zaxistemporary when lift rise;command_string='%s'" % command_string)

        #lancaigang240325:
        #self.G_ResumeProcessCheckPauseStatus=False


        #lancaigang250519:
        self.G_PhrozenFluiddRespondInfo("external macro-PRZ_SPITTING_SCRAPE")
        command_string = """
            PRZ_SPITTING_SCRAPE
            """
        self.G_PhrozenGCode.run_script_from_command(command_string)
        self.G_PhrozenFluiddRespondInfo("external macro-scrape;command_string='%s'" % command_string)

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))
        #set flag
        Lo_ChangeChannelIfSuccess = False
        #lancaigang250607:print state;1-unload filament in;2-load filament in;3-print in;4-pause
        self.G_KlipperPrintStatus= 2
        #lancaigang20231013:timeout
        #lancaigang231114:Not changing filament change timeout in printer.cfg config file, changing timeout directly here
        #loop detect2time(s)load filament filament is not to toolhead
        for i in range(CHANGE_CHANNEL_WAIT_TIMEOUT):
            # self.G_XBasePosition+=2
            # self.G_YBasePosition+=2
            #lancaigang240325:if during resume state, can not judge on report pause state
            #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]self.G_ResumeProcessCheckPauseStatus='%d'" % self.G_ResumeProcessCheckPauseStatus)
            if self.G_ChangeChannelResumeFlag==True:
                if self.STM32ReprotPauseFlag==1:
                    self.G_PhrozenFluiddRespondInfo("during resume state during, detect to on time(s)pause")
                    if self.G_ResumeProcessCheckPauseStatus==True:
                        #lancaigang240430:move to after side/face failure handle
                        #self.G_ResumeProcessCheckPauseStatus=False
                        self.G_PhrozenFluiddRespondInfo("hasthis time(s)pause state on report, retract out resume process")
                        self.G_ChangeChannelFirstFilaFlag=True
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
                    #else:
                        #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]withoutthis time(s)pause state on report, continue resume process")

            else:
                #lancaigang231202:ifSTM32active/manual on report pause, need klipper topause
                if self.STM32ReprotPauseFlag==1:
                    self.G_ChangeChannelFirstFilaFlag=True
                    self.G_PhrozenFluiddRespondInfo("wait filament change during, stm32active/manual on reportpause")
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


            # #lancaigang231216:
            # if self.G_XBasePosition==0 and self.G_YBasePosition==0:
            #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]wait filament change during, base coordinateXYis0")
            #     command_string = """
            #         G90
            #         G1 X%.03f Y%.03f F5000
            #         """ % (
            #         150+(i%2),
            #         260+(i%2)
            #     )
            #     #lancaigang231129:slow back-and-forth movement
            #     self.G_PhrozenGCode.run_script_from_command(command_string)
            # else:
            #     #lancaigang231216:resume time, need back-and-forth movement prevent material leak generate apit
            #     #lancaigang231214:wait area zone base pointX YbyW Hrectangle step size back-and-forth move, implement purge function
            #     command_string = """
            #         G90
            #         G1 X%.03f Y%.03f F5000
            #         """ % (
            #         self.G_XBasePosition+(i%2),
            #         self.G_YBasePosition+(i%2)
            #     )
            #     #lancaigang231129:slow back-and-forth movement
            #     self.G_PhrozenGCode.run_script_from_command(command_string)
            #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]wait filament change during, base coordinateXYisP9config")
            #     #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]wait back-and-forth movement;command_string='%s'" % command_string)


            #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]wait filament change during, use external macro")


            #lancaigang240223:because resume time, directly run/move toP9wait area, not lift rise may will causesscrape tomodel/mold type/model, only lift rise a time(s)and down lower a time(s)
            if self.Lo_ThisIfZPositionLiftUpFlag == True:
                command_string = """
                                G90
                                G91
                                G1 Z-%f F8000
                                """ % (
                                self.G_AMSFilaCutZPositionLiftingUp,
                            )
                self.G_PhrozenGCode.run_script_from_command(command_string)
                self.Lo_ThisIfZPositionLiftUpFlag = False
                self.G_PhrozenFluiddRespondInfo("Zaxistemporary when down lower;command_string='%s'" % command_string)

            #lancaigang20231013:change is4seconds delay
            #lancaigang231115:change is1s
            self.G_ProzenToolhead.dwell(1)
            #lancaigang240125:cannot usesleep, willblock main thread
            #time.sleep(1)


            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            self.G_PhrozenFluiddRespondInfo("external macro-PG110;STM32 load filament after, klipper start purgecatch/connect hold load filament")
            command_string = """
            PG110
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)



            logging.info("current mode")
            self.Device_ReportModeIfChanged()


            Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
            logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
            logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
            #// current pause status-Lo_PauseStatus='{'is_paused': True}'
            if Lo_PauseStatus['is_paused'] == True:
                logging.info("already in paused state")
            else:
                logging.info("not in paused state")



            #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]i=%d;T=%d" % (i,self.G_ChangeChannelTimeoutNewChan))

            #detect new channel filament load filament, is not has filament to toolhead
            if self.G_ToolheadIfHaveFilaFlag:
                Lo_ChangeChannelIfSuccess = True
                break

        # #lancaigang240125:wait filament change during, zaxis lift rise after again down lower
        # command_string = """
        #     G91
        #     G1 -Z%f F8000
        #     """ % (
        #     self.G_AMSFilaCutZPositionLiftingUp,
        # )
        # self.G_PhrozenGCode.run_script_from_command(command_string)
        # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]Zaxis down lower;gcodecommand=%s" % command_string)




        #lancaigang240318:prevent Z rise without lower
        if self.Lo_ThisIfZPositionLiftUpFlag == True:
            command_string = """
                            G90
                            G91
                            G1 Z-%f F8000
                            """ % (
                            self.G_AMSFilaCutZPositionLiftingUp,
                        )
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.Lo_ThisIfZPositionLiftUpFlag = False
            self.G_PhrozenFluiddRespondInfo("Zaxistemporary when down lower;command_string='%s'" % command_string)


        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

        #normal filament change;change success
        if Lo_ChangeChannelIfSuccess:
            self.G_PhrozenFluiddRespondInfo("change success: T%d" % self.G_ChangeChannelTimeoutNewChan)
            self.G_IfChangeFilaOngoing= False

            #lancaigang250424:preventAMS buffer not yet full
            self.G_ProzenToolhead.dwell(0.5)

            #lancaigang250619:Check if AMS reconnected successfully
            self.Cmds_USBConnectErrorCheck()
            #lancaigang250423:load filament success, start purge, through/notify knowAMS start count when, if purgeexceed past/over5seconds buffer still/orslow state, indicates clogged nozzle
            #self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
            #self.G_PhrozenFluiddRespondInfo("AMS start count when buffer full when interval")
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                logging.info("serial port1-AMS start count when buffer full when interval")
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                logging.info("serial port2-AMS start count when buffer full when interval")
            self.G_ProzenToolhead.dwell(1)

            #lancaigang240229:
            if self.IfDoPG102Flag==True:
                self.IfDoPG102Flag=False

                self.G_PhrozenFluiddRespondInfo("purge start")
                self.G_PhrozenFluiddRespondInfo("+MSG:1,0,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                #lancaigang240328:manual command skip purge
                if self.ManualCmdFlag==True:
                    self.G_PhrozenFluiddRespondInfo("external macro-PG102;manual command, not execute purge function")
                    #lancaigang250409:hand/manual move entermaterial then readAMS state
                    self.Cmds_CmdP114(None)
                else:
                    # self.G_PhrozenFluiddRespondInfo("external macro-PG102")
                    # self.PG102Flag=True
                    # logging.info("self.Flag=True")
                    # command_string = """
                    # PG102
                    # """
                    # self.G_PhrozenGCode.run_script_from_command(command_string)
                    # self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)

                    #lancaigang241031:control purge count
                    if self.G_P10SpitNum==0:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG113")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG114
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==1:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG111")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG114
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==2:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG112")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG113
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==3:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG113")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG113
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==4:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG114")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG114
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==5:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG115")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG115
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    #lancaigang250528:
                    elif self.G_P10SpitNum==6:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG116")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG116
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==7:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG117")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG117
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==8:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG118")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG118
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==9:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG119")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG119
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material;command_string='%s'" % command_string)


                    self.PG102Flag=False
                    logging.info("self.Flag=False")

                self.G_PhrozenFluiddRespondInfo("purge end")
                self.G_PhrozenFluiddRespondInfo("+MSG:1,1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))


                #lancaigang240323:causesa layerfall/drop residual, first disabled
                # #lancaigang240321：purge complete after，move to bed/heatbed center，prevent resume time fromY305position directly to pause point，causes toolheadMCUheartbeat packet abnormalcrash
                # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]external macro-PG105；move to bed/heatbed center，prevent resume path past/overlong")
                # command_string = """
                # PG105
                # """
                # self.G_PhrozenGCode.run_script_from_command(command_string)
                # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]external macro-PG105；move to bed/heatbed center，prevent resume path past/overlong；command_string='%s'" % command_string)



                # for i in range(15):
                #     self.G_PhrozenFluiddRespondInfo("[(dev.python)]purge in，wait")
                #     #lancaigang20231013：change is4seconds delay
                #     #lancaigang231115：change is1s
                #     self.G_ProzenToolhead.dwell(1.0)
                #     #lancaigang240125：cannot usesleep，willblock main thread
                #     #time.sleep(1)
                if self.PG102DelayPauseFlag==True:
                    self.PG102DelayPauseFlag=False

                    #lancaigang250619:checkAMSisnot re-connect success
                    self.Cmds_USBConnectErrorCheck()
                    #lancaigang250427：
                    if self.G_SerialPort1OpenFlag == True:
                        self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                        logging.info("serial port1-AMSend count when buffer full when interval")
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                        logging.info("serial port2-AMSend count when buffer full when interval")

                    self.G_PhrozenFluiddRespondInfo("enable quick pause")
                    self.G_KlipperQuickPause = True
                    self.G_PhrozenFluiddRespondInfo("purge process in，STM32triggersendrunout pause")
                    #lancaigang231209：timer in handle business，will causes business abnormal，after side/face need use thread handle interrupt business
                    self.G_PhrozenFluiddRespondInfo("STM32 reported pause, pausing once")




                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        #lancaigang250607:
                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")




                    self.G_KlipperIfPaused = True
                    #stm32active/manual pause only can pause1time(s)，cannot repeat pause
                    self.STM32ReprotPauseFlag=1
                    #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
                    self.G_ChangeChannelFirstFilaFlag=True

                    self.G_ProzenToolhead.dwell(1.5)
                    self.G_PhrozenFluiddRespondInfo("+MSG:1,1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #lancaigang240524：use inUIUXdynamic interface
                    self.G_PhrozenFluiddRespondInfo("+C:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                    #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                    #lancaigang250529:
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)


                    #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                    self.G_KlipperPrintStatus= 3
                    self.G_PauseToLCDString=""

                    self.G_PhrozenFluiddRespondInfo("return")
                    return
                else:
                    #lancaigang240325:iscompatible pause，system a use pause1
                    if self.G_PauseTriggerWhileChangeChannelFlag==True:
                        #lancaigang231209：timer in handle business，will causes business abnormal，after side/face need use thread handle interrupt business
                        self.G_PhrozenFluiddRespondInfo("purge process in，STM32triggersendpause")
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                        #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                        #lancaigang250529:
                        if len(self.G_PauseToLCDString)==0:
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                        #lancaigang240325：change failed，cannot execute resume
                        self.G_MCModeCanResumeFlag = False
                        #lancaigang250527：quick pause execution
                        self.G_KlipperQuickPause = False
                    else:
                        #lancaigang240325：change success，can execute resume
                        self.G_MCModeCanResumeFlag = True
                        self.G_PhrozenFluiddRespondInfo("purge process normal，perform enter print")
                        #lancaigang250527：quick pause execution
                        self.G_KlipperQuickPause = True
            else:
                #lancaigang240325：change success，can execute resume
                self.G_MCModeCanResumeFlag = True
                #lancaigang250527：quick pause execution
                #self.G_KlipperQuickPause = True
            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()
            #lancaigang250427：
            if self.G_SerialPort1OpenFlag == True:
                self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                logging.info("serial port1-AMSend count when buffer full when interval")
            if self.G_SerialPort2OpenFlag == True:
                self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                logging.info("serial port2-AMSend count when buffer full when interval")
            self.G_ProzenToolhead.dwell(1.5)

            # #lancaigang240318：prevent Z rise without lower
            # if self.Lo_ThisIfZPositionLiftUpFlag == True:
            #     command_string = """
            #                     G90
            #                     G91
            #                     G1 Z-%f F8000
            #                     """ % (
            #                     self.G_AMSFilaCutZPositionLiftingUp,
            #                 )
            #     self.G_PhrozenGCode.run_script_from_command(command_string)
            #     self.Lo_ThisIfZPositionLiftUpFlag = False
            #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]Zaxistemporary when down lower；command_string='%s'" % command_string)

            self.G_ResumeProcessCheckPauseStatus=False
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+T:1,%d" % self.G_ChangeChannelTimeoutNewChan)

            #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
            self.G_KlipperPrintStatus= 3

            self.G_PauseToLCDString=""

            return


        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

        # change failed
        if self.G_DictChangeChannelWaitAreaParam["A"] == 0:
            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()

            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1TnManualChangeChannel]change failed；filament load filament to toolhead timeout；cmd='%s', all retract filament，klipperpause" % (gcmd.get_commandline()))
            # #// all retract to park position；//===== P2 A1 all filament to park position for print Yes；"AP"；
            # self.Cmds_AMSSerial1Send("AP")
            # self.G_PhrozenFluiddRespondInfo("send command: AP，all retract to park position")
            #lancaigang231209：stm32active/manual on report then not on report9
            if self.G_KlipperIfPaused==False:
                #lancaigang240328：if it is manual command，not pause
                if self.ManualCmdFlag==True:
                    self.G_PhrozenFluiddRespondInfo("manual command，klippernot execute pause")
                    #lancaigang250409：hand/manual move entermaterial then readAMSstate
                    self.Cmds_CmdP114(None)
                elif self.G_CutCheckTest==True:
                    self.G_PhrozenFluiddRespondInfo("cutter test command，klippernot execute pause")
                    #lancaigang250409：hand/manual move entermaterial then readAMSstate
                    self.Cmds_CmdP114(None)
                else:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
                        self.G_ChangeChannelFirstFilaFlag=True

                        self.G_PhrozenFluiddRespondInfo("change timeout60s，pause")
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                        #lancaigang240416:
                        if self.G_SerialPort1OpenFlag == True:
                            #lancaigang240603：preventAMSalwaysstop not
                            self.Cmds_AMSSerial1Send("AT+PAUSE")
                            logging.info("serial port1-AT+PAUSEpausestm32motor")
                        #lancaigang241030:
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+PAUSE")
                            logging.info("serial port2-AT+PAUSEpausestm32motor")

                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPause(None)
                        self.G_KlipperIfPaused = True

                        #lancaigang250529:
                        if len(self.G_PauseToLCDString)==0:
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                        #lancaigang240325：change failed，cannot execute resume
                        self.G_MCModeCanResumeFlag = False
                        #lancaigang250527：quick pause execution
                        self.G_KlipperQuickPause = False
                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")
            #lancaigang240124：cannot repeat pause
            else:
                self.G_PhrozenFluiddRespondInfo("already pause，no need repeat pause")
                #lancaigang240509：disabled
                # #lancaigang240326：on report pause
                # #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                # if len(self.G_PauseToLCDString)==0:
                #     self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240417：preventstm32not on report whenG_PauseToLCDStringis empty situation
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)
                #lancaigang240325：change failed，cannot execute resume
                self.G_MCModeCanResumeFlag = False
                #lancaigang250527：quick pause execution
                self.G_KlipperQuickPause = False

                #lancaigang240429：if resume process instm32and without on report pause state，here need on report pause
                if self.G_ResumeProcessCheckPauseStatus==False:
                    self.G_PhrozenFluiddRespondInfo("AMSwithout on report pause，klipperrepeat pause，need on report pause")
                    #lancaigang250529:
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                    #lancaigang240416:
                    if self.G_SerialPort1OpenFlag == True:
                        #lancaigang240603：preventAMSalwaysstop not
                        self.Cmds_AMSSerial1Send("AT+PAUSE")
                        logging.info("serial port1-AT+PAUSEpausestm32motor")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AT+PAUSE")
                        logging.info("serial port2-AT+PAUSEpausestm32motor")
                else:#True
                    self.G_PhrozenFluiddRespondInfo("AMShas on report pause，klippernot need need on report pause")
                    self.G_ResumeProcessCheckPauseStatus=False

                    #lancaigang250529:
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)


                # self.G_PhrozenFluiddRespondInfo("already pause，again pause1time(s)，prevent before pause abnormal")
                # #lancaigang250423：isprevent abnormal pause not hold，many/more pause1time(s)
                # #klipperactive/manual pause
                # self.Cmds_PhrozenKlipperPause(None)

            #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
            self.G_ChangeChannelFirstFilaFlag=True

            self.G_IfChangeFilaOngoing= False

            self.G_ResumeProcessCheckPauseStatus=False
            #lancaigang240524：use inUIUXdynamic interface
            self.G_PhrozenFluiddRespondInfo("+T:1,%d" % self.G_ChangeChannelTimeoutNewChan)

            #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
            self.G_KlipperPrintStatus= -1

            return

        #normal filament change；Actionnormal
        if self.G_DictChangeChannelWaitAreaParam["A"] == 1:
            pass


    ####################################
    #Function Name:
    #Input Parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
   # P1 C[n] n:1~32(device not on network, use1~4) autochange tospecified channel(many/more action command,includes cut filament, filament change, wait)
    def Cmds_P1CnAutoChangeChannel(self, chan, gcmd):
            #lancaigang241030：generally isP1 C1toP1 C32，range at1to32
            #1unit：1 2 3 4
            #2unit：5 6 7 8
            #3unit：9 10 11 12
            #4unit：13 14 15 16
            #5unit：17 18 19 20
            #6unit：21 22 23 24
            #7unit：25 26 27 28
            #8unit：29 30 31 32
        self.G_PhrozenFluiddRespondInfo("=====[(cmds.python)Cmds_P1CnAutoChangeChannel]")
        self.G_PhrozenFluiddRespondInfo("=====last filament changeself.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
        self.G_PhrozenFluiddRespondInfo("=====last filament changeself.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
        if gcmd is None:
            self.G_PhrozenFluiddRespondInfo("gcmd is None")
            #self.G_PhrozenFluiddRespondInfo("return")
            #return
            #pass
        if gcmd is not None:
            self.G_PhrozenFluiddRespondInfo("gcmd is not None:")
            self.G_PhrozenFluiddRespondInfo("=====last filament change'%s';self.G_ChangeChannelTimeoutOldChan=%d" % (gcmd.get_commandline(),self.G_ChangeChannelTimeoutOldChan))
            self.G_PhrozenFluiddRespondInfo("=====last filament change'%s';self.G_ChangeChannelTimeoutNewChan=%d" % (gcmd.get_commandline(),self.G_ChangeChannelTimeoutNewChan))

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))




        #lancaigang250824:
        logging.info("self.G_ProzenToolhead.wait_moves()")
        self.G_ProzenToolhead.wait_moves()





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

        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        #unlock
        self.Base_AMSSerialCmdUnlock()


        #lancaigang250605:
        if self.G_AMSDeviceWorkMode == AMS_WORK_MODE_UNKNOW:
            self.G_PhrozenFluiddRespondInfo("if receivedT?command，but mode is unknown mode，force rotate/switchchange isMCmulti-color mode")
            self.G_AMSDeviceWorkMode = AMS_WORK_MODE_MC

        logging.info("current mode")
        self.Device_ReportModeIfChanged()


        #lancaigang250526：pausing，not allow new gcodecommand，need wait pause complete
        if self.G_KlipperInPausing == True:
            self.G_PhrozenFluiddRespondInfo("pause process in，not allow new gcodecommand，need wait pause complete")
            for num in range(30):
                #lancaigang231115：change is1s
                self.G_PhrozenFluiddRespondInfo("self.G_ProzenToolhead.dwell(1)")
                self.G_ProzenToolhead.dwell(1)
                self.G_PhrozenFluiddRespondInfo("pause process in，not allow new gcodecommand，need wait pause complete")
                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])

                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    logging.info("not in paused state")

                if self.G_KlipperInPausing == False:
                    self.G_PhrozenFluiddRespondInfo("pause end")
                    Lo_ChangeChannelIfSuccess = True

                    Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                    logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                    logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                    #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                    if Lo_PauseStatus['is_paused'] == True:
                        logging.info("already in paused state")
                    else:
                        logging.info("not in paused state")
                        #klipperpause command；save current x y zcoordinate
                        #lancaigang240108：need consider multiple times pause save data isnot normal，aftercontinue need verify
                        self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                        logging.info("[(cmds.python)]PAUSE")
                        self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                        self.G_ProzenToolhead.wait_moves()
                        self.G_ProzenToolhead.dwell(1.0)

                    self.G_PhrozenFluiddRespondInfo("break")
                    break

            #lancaigang250725：ifloop end，still/or without executecomplete pausemacro，then immediately execute pause
            if self.G_KlipperInPausing == True:
                self.G_PhrozenFluiddRespondInfo("=====pause process in，receivednew color change command，but pause still not yet complete，here force pause")
                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    self.G_PhrozenFluiddRespondInfo("=====not in paused state，execute pause operation")
                    #klipperpause command；save current x y zcoordinate
                    #lancaigang240108：need consider multiple times pause save data isnot normal，aftercontinue need verify
                    self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                    logging.info("[(cmds.python)]PAUSE")
                    self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                    self.G_ProzenToolhead.wait_moves()
                    self.G_ProzenToolhead.dwell(1.0)

        else:
            self.G_PhrozenFluiddRespondInfo("not in pausing state")
            self.G_PhrozenFluiddRespondInfo("self.G_KlipperInPausing == False")

        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
        if Lo_PauseStatus['is_paused'] == True:
            logging.info("already in paused state")
        else:
            logging.info("not in paused state")

        #lancaigang250512：many/more pause1time(s)，prevent before without pause success situation
        if self.G_KlipperIfPaused == True:
            #not in resume state
            if self.G_ChangeChannelResumeFlag==False:
                self.G_PhrozenFluiddRespondInfo("not in resume state")
                self.G_PhrozenFluiddRespondInfo("klipperpause，but still received command")
                #lancaigang250508:prevent pause abnormal
                self.G_PhrozenFluiddRespondInfo("klipperpause，but still received command，again pause")
                self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                self.G_PauseToLCDString="+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan)
                #self.Cmds_PhrozenKlipperPause(None)

                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    logging.info("not in paused state")
                    #klipperpause command；save current x y zcoordinate
                    #lancaigang240108：need consider multiple times pause save data isnot normal，aftercontinue need verify
                    self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                    logging.info("[(cmds.python)]PAUSE")
                    self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                    self.G_ProzenToolhead.wait_moves()
                    self.G_ProzenToolhead.dwell(1.0)

                #lancaigang250524:
                self.G_PhrozenFluiddRespondInfo("pause process in，receivednew gcodecommand，also need record most new new old channel，prevent color mixing")
                self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
                self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
                self.G_ChangeChannelTimeoutNewChan=chan
                logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
                self.G_ChangeChannelTimeoutNewGcmd=gcmd
                self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)

                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    logging.info("not in paused state")

                self.G_PhrozenFluiddRespondInfo("return")
                return


       #lancaigang250619:checkAMSisnot re-connect success
        self.Cmds_USBConnectErrorCheck()
        if self.G_SerialPort1Obj is not None:
            if self.G_SerialPort1Obj.is_open:
                logging.info("serial port1is open")
                #self.G_SerialPort1Obj.flushInput()
                #self.G_PhrozenFluiddRespondInfo("G_SerialPort1Obj.flushInputserial port flushed")
        if self.G_SerialPort2Obj is not None:
            #lancaigang241030:
            if self.G_SerialPort2Obj.is_open:
                logging.info("serial port2is open")

        logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

        #lancaigang240226：cut filament afterAMSmainboard retract filament，delay after toolhead retract20mm
        #time.sleep(2)
        #self.G_ProzenToolhead.dwell(2.0)

        self.G_PauseTriggerWhileChangeChannelFlag=False
        self.G_PhrozenFluiddRespondInfo("+C:0,%d" % chan)

        self.G_ASM1DisconnectErrorCount=0



        # #lancaigang240322：pause and filament change simultaneously send，ifG?command already foundrunout pause，directly return
        # if self.STM32ReprotPauseFlag==1:
        #     self.G_PhrozenFluiddRespondInfo("self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
        #     self.G_PhrozenFluiddRespondInfo("self.G_Pause1Channel=%d" % self.G_Pause1Channel)
        #     if self.G_PauseTriggerWhileChangeChannelFlag==True:
        #         self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]G?command found pause on report，continue pause")
        #         #lancaigang240325：iscompatible runout without remove andreconnectclick screen，system a all use pause1indicates
        #         #self.G_PhrozenFluiddRespondInfo("+PAUSE:1,%d" % self.G_Pause1Channel)
        #         if "+PAUSE:1" in self.G_PauseToLCDString:
        #             self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
        #         #else:
        #             #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
        #         self.G_ChangeChannelFirstFilaFlag=True
        #         self.G_IfChangeFilaOngoing= False
        #         #lancaigang240524：use inUIUXdynamic interface
        #         self.G_PhrozenFluiddRespondInfo("+C:1,%d" % self.G_ChangeChannelTimeoutNewChan)
        #         return
        #     else:
        #         self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]G?command without found pause on report，need load filament resume")
        #         self.G_ChangeChannelFirstFilaFlag=True
        #         self.G_IfChangeFilaOngoing= False
        #         #lancaigang240325：without runout，can continue load filament
        #         #return


        self.G_IfChangeFilaOngoing= True



        #lancaigang250102:print filament change count
        self.G_PrintCountNum=self.G_PrintCountNum+1
        self.G_PhrozenFluiddRespondInfo("Filament change count=%d" % self.G_PrintCountNum)


        #filament changefirst time(s)1switch channel filament
        if self.G_ChangeChannelFirstFilaFlag:
            # #lancaigang240314：achannel first move tospecified position
            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]external macro-PG104")
            # command_string = """
            # PG104
            # """
            # self.G_PhrozenGCode.run_script_from_command(command_string)
            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]external macro-1channel move tospecified position；command_string='%s'" % command_string)


            #lancaigang240125：
            self.G_PhrozenFluiddRespondInfo("First filament change - switching to channel 1; pause/resume channel 1")

            # #lancaigang240124：stm32active/manual on report，enable can pause1time(s)
            # self.STM32ReprotPauseFlag=0
            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]self.STM32ReprotPauseFlag=0")




            #lancaigang231202：if1channel load filament afterklipperabnormal pause assignfalse，again resume after then no method/way perform enter1time(s)filament change
            self.G_ChangeChannelFirstFilaFlag = False

            #not in resume state，then need cut filament
            if self.G_ChangeChannelResumeFlag==False:
                self.G_PhrozenFluiddRespondInfo("first layer print，is not pause resume")
                self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                self.G_PhrozenFluiddRespondInfo("=====this filament changeself.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
                self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
                self.G_ChangeChannelTimeoutNewChan=chan
                self.G_PhrozenFluiddRespondInfo("=====this filament changeself.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
                self.G_ChangeChannelTimeoutNewGcmd=gcmd
                self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)




                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()
                #lancaigang241030:
                if self.G_ChangeChannelTimeoutOldChan in range(1, 5):# 1 2 3 4
                    # #lancaigang241011：filament change beforeAMSfirst execute retractsmall section distance，again executePG101；need consider pause resume repeat retract cut filament issue
                    self.G_PhrozenFluiddRespondInfo("+H:0,%d" % self.G_ChangeChannelTimeoutOldChan)
                    self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutOldChan)
                    logging.info("serial port1send command: H%d" % self.G_ChangeChannelTimeoutOldChan)
                    logging.info("serial port1filament change beforeAMSretract")
                    self.G_PhrozenFluiddRespondInfo("+H:1,%d" % self.G_ChangeChannelTimeoutOldChan)
                elif self.G_ChangeChannelTimeoutOldChan in range(5, 9):# 5 6 7 8
                    self.G_PhrozenFluiddRespondInfo("+H:0,%d" % self.G_ChangeChannelTimeoutOldChan-4)
                    self.Cmds_AMSSerial2Send("H%d" % self.G_ChangeChannelTimeoutOldChan-4)
                    logging.info("serial port2send command: H%d" % self.G_ChangeChannelTimeoutOldChan-4)
                    logging.info("serial port2filament change beforeAMSretract")
                    self.G_PhrozenFluiddRespondInfo("+H:1,%d" % self.G_ChangeChannelTimeoutOldChan-4)
                else:
                    self.G_PhrozenFluiddRespondInfo("retract abnormal channel，all channels retract some distance")
                    if self.G_SerialPort1OpenFlag == True:
                        #lancaigang240913：resume time，purpose is repeat perform filament，can all retract all filament a section distance，prevent old channel retract abnormal，new channel load filament abnormal
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command: AP；all channels retract some distance")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command: AP；all channels retract some distance")

                    #lancaigang240913：delay timeplace/put to outside side/face
                    self.G_ProzenToolhead.dwell(6)







                # #lancaigang241011：PG101before G?command performexecute/row retract，after executePG101toolhead retract operation，at then executeMChit/openbreakG?command
                # self.Cmds_AMSSerial1Send("MC")
                # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]send command：MC")
                # self.G_PhrozenFluiddRespondInfo("forcehit/openbreakAMSretract distance")


                logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

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

                #lancaigang250323：
                if self.G_ToolheadIfHaveFilaFlag==True:
                    self.G_PhrozenFluiddRespondInfo("toolhead has filament")



                    #lancaigang240909:cut filament actionplace/put atPG106before
                    # for i in range(15):
                    #     self.G_PhrozenFluiddRespondInfo("[(dev.python)]purge complete")
                    #     #lancaigang20231013：change is4seconds delay
                    #     #lancaigang231115：change is1s
                    #     self.G_ProzenToolhead.dwell(1.0)
                    #     #lancaigang240125：cannot usesleep，willblock main thread
                    #     #time.sleep(1)
                    #lancaigang240319：preparation before filament cut
                    #self.Cmds_MoveToCutFilaPrepare()
                    #lancaigang20231205：cutter cut filament
                    self.Cmds_MoveToCutFilaAction(gcmd)

                    #lancaigang250519:
                    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_CUT_WAITINGAREA")
                    command_string = """
                        PRZ_CUT_WAITINGAREA
                        """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position；command_string='%s'" % command_string)


                    #lancaigang240226：cut filament afterAMSmainboard retract filament，delay after toolhead retract20mm
                    #time.sleep(2)
                    self.G_ProzenToolhead.dwell(0.5)


                    #lancaigang250619:checkAMSisnot re-connect success
                    self.Cmds_USBConnectErrorCheck()
                    #lancaigang241030:
                    if self.G_ChangeChannelTimeoutOldChan in range(1, 5):
                        #lancaigang240906：new AMS，cut filament after，retract on a time(s)channel a section distance
                        #lancaigang20231013：stm32filament change
                        #lancaigang231129：stm32internal filament change withklipperfilament change separate，causesstm32internal force filament change，andklipperif toolhead cut filament abnormal and no method/way unload filament，causesklipperabnormal empty print
                        self.Cmds_AMSSerial1Send("G%d" % self.G_ChangeChannelTimeoutOldChan)
                        self.G_PhrozenFluiddRespondInfo("G%d" % self.G_ChangeChannelTimeoutOldChan)
                        self.G_PhrozenFluiddRespondInfo("serial port1-AMSold channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutOldChan)
                    elif self.G_ChangeChannelTimeoutOldChan in range(5, 9):
                        self.Cmds_AMSSerial2Send("G%d" % self.G_ChangeChannelTimeoutOldChan-4)
                        self.G_PhrozenFluiddRespondInfo("G%d" % self.G_ChangeChannelTimeoutOldChan-4)
                        self.G_PhrozenFluiddRespondInfo("serial port2-AMSold channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutOldChan-4)


                    logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))



                    #get channelnumber andgcmdobject
                    #self.G_ChangeChannelTimeoutOldChan=chan
                    #self.G_ChangeChannelTimeoutOldGcmd=gcmd

                    self.G_ProzenToolhead.dwell(0.5)




                    #lancaigang240913：delay timeplace/put to outside side/face
                    self.G_ProzenToolhead.dwell(6.5)
                    #lancaigang240911：Gcommand after delay6seconds check toolhead isnot has filament
                    #lancaigang231201：check cut filament after old channel filament isnot normal unload filament，not normal then pause
                    self.Cmds_CutFilaIfNormalCheck()
                    if self.G_KlipperIfPaused == True:
                        self.G_PhrozenFluiddRespondInfo("cut filament？secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                        #Lo_ChangeChannelIfSuccess = False
                        return
                # else:
                #     self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA-wait area")
                #     command_string = """
                #         PRZ_WAITINGAREA
                #         """
                #     self.G_PhrozenGCode.run_script_from_command(command_string)
                #     self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA；command_string='%s'" % command_string)



                logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

                #lancaigang240328：manual command skip purge
                if self.ManualCmdFlag==True:
                    self.G_PhrozenFluiddRespondInfo("external macro-PG106；manual command，not execute purge function")
                else:
                    #lancaigang240319：cutcomplete after，first purge/spitresidual toolhead filament，preventcut into pellets
                    self.G_PhrozenFluiddRespondInfo("external macro-PG106；cut filament after，toolhead heat up simultaneouslyAMSretract filament")
                    self.PG102Flag=True
                    logging.info("self.Flag=True")
                    command_string = """
                    PG106
                    """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                    self.PG102Flag=False
                    logging.info("self.Flag=False")


                #lancaigang231216：if filament change during pointclick pause，justgood filament change during lift risezaxis，to execute pause when，zaxis height also save，causes overall height abnormal
                #lancaigang231216：ifzaxis lift rise without by lower down，need lower down again pause
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
                    self.G_PhrozenFluiddRespondInfo("Zaxis down pull lower low；command_string='%s'" % command_string)


                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang20231013：manual filament change
                self.Cmds_P1TnManualChangeChannel(self.G_ChangeChannelTimeoutNewChan, self.G_ChangeChannelTimeoutNewGcmd)
            #lancaigang240912:pause resume process，use old record old channel and new channel
            else:
                self.G_PhrozenFluiddRespondInfo("is notfirst layer print，is pause resume")
                #lancaigang20231013：manual filament change
                self.Cmds_P1TnManualChangeChannel(self.G_ChangeChannelTimeoutNewChan, self.G_ChangeChannelTimeoutNewGcmd)









        #aftercontinuenswitch channel filament
        else:
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]filament change after side/facenchannelswitch；else")
            self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
            self.G_PhrozenFluiddRespondInfo("=====this filament changeself.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
            self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
            self.G_ChangeChannelTimeoutNewChan=chan
            self.G_PhrozenFluiddRespondInfo("=====this filament changeself.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
            self.G_ChangeChannelTimeoutNewGcmd=gcmd
            self.Cmds_PrintMode(self.G_AMSDeviceWorkMode)



            #lancaigang240124：stm32active/manual on report，enable can pause1time(s)
            self.STM32ReprotPauseFlag=0
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]self.STM32ReprotPauseFlag=0")
            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()
            #lancaigang241030:
            if self.G_ChangeChannelTimeoutOldChan in range(1, 5):
                # #lancaigang241011：filament change beforeAMSfirst execute retractsmall section distance，again executePG101；need consider pause resume repeat retract cut filament issue
                self.G_PhrozenFluiddRespondInfo("+H:0,%d" % self.G_ChangeChannelTimeoutOldChan)
                self.Cmds_AMSSerial1Send("H%d" % self.G_ChangeChannelTimeoutOldChan)
                logging.info("serial port1send command: H%d" % self.G_ChangeChannelTimeoutOldChan)
                logging.info("serial port1filament change beforeAMSretract")
                self.G_PhrozenFluiddRespondInfo("+H:1,%d" % self.G_ChangeChannelTimeoutOldChan)
            elif self.G_ChangeChannelTimeoutOldChan in range(5, 9):
                self.G_PhrozenFluiddRespondInfo("+H:0,%d" % self.G_ChangeChannelTimeoutOldChan-4)
                self.Cmds_AMSSerial2Send("H%d" % self.G_ChangeChannelTimeoutOldChan-4)
                logging.info("serial port2send command: H%d" % self.G_ChangeChannelTimeoutOldChan-4)
                logging.info("serial port2filament change beforeAMSretract")
                self.G_PhrozenFluiddRespondInfo("+H:1,%d" % self.G_ChangeChannelTimeoutOldChan-4)
            else:
                    self.G_PhrozenFluiddRespondInfo("retract abnormal channel，all channels retract some distance")
                    if self.G_SerialPort1OpenFlag == True:
                        #lancaigang240913：resume time，purpose is repeat perform filament，can all retract all filament a section distance，prevent old channel retract abnormal，new channel load filament abnormal
                        self.Cmds_AMSSerial1Send("AP")
                        logging.info("serial port1send command: AP；all channels retract some distance")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AP")
                        logging.info("serial port2send command: AP；all channels retract some distance")

                    #lancaigang240913：delay timeplace/put to outside side/face
                    self.G_ProzenToolhead.dwell(6)




            #lancaigang250824:
            logging.info("self.G_ProzenToolhead.wait_moves()")
            self.G_ProzenToolhead.wait_moves()


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
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]external macro-PG101-retract")
            command_string = """
                PG101
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]external macro-tospecified wait area position wait purge；command_string='%s'" % command_string)
            self.IfDoPG102Flag=True


            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))



            #lancaigang250824:
            logging.info("self.G_ProzenToolhead.wait_moves()")
            self.G_ProzenToolhead.wait_moves()


            #lancaigang250323：
            #if self.G_ToolheadIfHaveFilaFlag==True:
                #self.G_PhrozenFluiddRespondInfo("toolhead has filament")
                #lancaigang20231013：cutter cut filament，Zlift rise run/move toX Ycut filament position
            self.Cmds_MoveToCutFilaAction(gcmd)
            #else:
            #    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA-wait area")
            #    command_string = """
            #        PRZ_WAITINGAREA
            #        """
            #    self.G_PhrozenGCode.run_script_from_command(command_string)
            #    self.G_PhrozenFluiddRespondInfo("external macro-PRZ_WAITINGAREA；command_string='%s'" % command_string)


            #lancaigang250824:
            logging.info("self.G_ProzenToolhead.wait_moves()")
            self.G_ProzenToolhead.wait_moves()



            #lancaigang250519:
            self.G_PhrozenFluiddRespondInfo("external macro-PRZ_CUT_WAITINGAREA")
            command_string = """
                PRZ_CUT_WAITINGAREA
                """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("external macro-tospecified wait area position；command_string='%s'" % command_string)


            self.G_ProzenToolhead.dwell(0.5)


            #lancaigang250824:
            logging.info("self.G_ProzenToolhead.wait_moves()")
            self.G_ProzenToolhead.wait_moves()

            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()
            #lancaigang241030:
            if self.G_ChangeChannelTimeoutOldChan in range(1, 5):
                #lancaigang240906：cut filament after，retract on a time(s)channel a section distance
                #lancaigang20231013：stm32filament change
                #lancaigang231129：stm32internal filament change withklipperfilament change separate，causesstm32internal force filament change，andklipperif toolhead cut filament abnormal and no method/way unload filament，causesklipperabnormal empty print
                self.Cmds_AMSSerial1Send("G%d" % self.G_ChangeChannelTimeoutOldChan)
                self.G_PhrozenFluiddRespondInfo("G%d" % self.G_ChangeChannelTimeoutOldChan)
                self.G_PhrozenFluiddRespondInfo("serial port1-AMSold channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutOldChan)
            elif self.G_ChangeChannelTimeoutOldChan in range(5, 9):
                self.Cmds_AMSSerial2Send("G%d" % self.G_ChangeChannelTimeoutOldChan-4)
                self.G_PhrozenFluiddRespondInfo("G%d" % self.G_ChangeChannelTimeoutOldChan-4)
                self.G_PhrozenFluiddRespondInfo("serial port2-AMSold channel retract some distance first: G%d" % self.G_ChangeChannelTimeoutOldChan-4)


            #lancaigang250824:
            logging.info("self.G_ProzenToolhead.wait_moves()")
            self.G_ProzenToolhead.wait_moves()

            #lancaigang250322：PG106heat up need tenseveral seconds，here no need delay，but beforelift/mention isPG106must heat up
            #lancaigang240913：delay timeplace/put to outside side/face
            self.G_ProzenToolhead.dwell(6.5)
            #lancaigang250823：
            logging.info("self.G_ProzenToolhead.wait_moves()")
            self.G_ProzenToolhead.wait_moves()
            #lancaigang231201：check cut filament after isnot normal unload filament，not normal then pause
            #lancaigang231215：Zaxis on rise after mustremember down lower
            #lancaigang231216：wait6seconds check isnot cut filament success
            self.Cmds_CutFilaIfNormalCheck()
            if self.G_KlipperIfPaused == True:
                self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]cut filament？secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                #self.Cmds_PhrozenKlipperPause(None)

                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    logging.info("not in paused state")
                    #klipperpause command；save current x y zcoordinate
                    #lancaigang240108：need consider multiple times pause save data isnot normal，aftercontinue need verify
                    self.G_PhrozenGCode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE")
                    logging.info("[(cmds.python)]PAUSE")
                    self.G_PhrozenPrinterCancelPauseResume.send_pause_command()
                    self.G_ProzenToolhead.wait_moves()
                    self.G_ProzenToolhead.dwell(1.0)

                    self.G_PhrozenFluiddRespondInfo("toolhead cutter or sensor abnormality，pause")
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d" % self.G_ChangeChannelTimeoutOldChan)
                    #lancaigang250414:
                    #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                # #lancaigang250524:
                # self.G_PhrozenFluiddRespondInfo("pause process in，receivednew gcodecommand，also need record most new new old channel，prevent color mixing")
                # self.G_ChangeChannelTimeoutOldChan=self.G_ChangeChannelTimeoutNewChan
                # logging.info("=====self.G_ChangeChannelTimeoutOldChan=%d" % self.G_ChangeChannelTimeoutOldChan)
                # self.G_ChangeChannelTimeoutOldGcmd=self.G_ChangeChannelTimeoutNewGcmd
                # self.G_ChangeChannelTimeoutNewChan=chan
                # logging.info("=====self.G_ChangeChannelTimeoutNewChan=%d" % self.G_ChangeChannelTimeoutNewChan)
                # self.G_ChangeChannelTimeoutNewGcmd=gcmd

                Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                if Lo_PauseStatus['is_paused'] == True:
                    logging.info("already in paused state")
                else:
                    logging.info("not in paused state")

                self.G_PhrozenFluiddRespondInfo("return")
                return

            #lancaigang240229：prevent send command packet concatenation
            #time.sleep(1)
            self.G_ProzenToolhead.dwell(0.5)



            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            #lancaigang240319：cutcomplete after，first purge/spitresidual toolhead filament，preventcut into pellets
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)]external macro-PG106；cut filament after，toolhead heat up simultaneouslyAMSretract filament")
            self.PG102Flag=True
            self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=True")
            command_string = """
            PG106
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command_string='%s'" % command_string)
            self.PG102Flag=False
            self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=False")

            #lancaigang250619:checkAMSisnot re-connect success
            self.Cmds_USBConnectErrorCheck()
            #lancaigang241030:
            if self.G_ChangeChannelTimeoutNewChan in range(1, 5):
                #lancaigang240911：newAMS，Tcommand only responsible for load filament
                #lancaigang20231013：stm32filament change
                #lancaigang231129：stm32internal filament change withklipperfilament change separate，causesstm32internal force filament change，andklipperif toolhead cut filament abnormal and no method/way unload filament，causesklipperabnormal empty print
                self.Cmds_AMSSerial1Send("T%d" % self.G_ChangeChannelTimeoutNewChan)
                logging.info("serial port1change send command: T%d" % self.G_ChangeChannelTimeoutNewChan)
            elif self.G_ChangeChannelTimeoutNewChan in range(5, 9):
                self.Cmds_AMSSerial2Send("T%d" % self.G_ChangeChannelTimeoutNewChan-4)
                logging.info("serial port2change send command: T%d" % self.G_ChangeChannelTimeoutNewChan-4)






            #lancaigang240322：
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)]external macro-PG105；cut filament after，toolhead heat up simultaneouslyAMSperform filament")
            self.PG102Flag=True
            self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=True")
            command_string = """
            PG105
            """
            self.G_PhrozenGCode.run_script_from_command(command_string)
            self.G_PhrozenFluiddRespondInfo("[(cmds.python)]command_string='%s'" % command_string)
            self.PG102Flag=False
            self.G_PhrozenFluiddRespondInfo("[(dev.python)]self.Flag=False")

            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            #lancaigang240328：manual command skip purge
            if self.ManualCmdFlag==True:
                self.G_PhrozenFluiddRespondInfo("external macro-PG110；manual command，not execute")
            else:
                #lancaigang240319：cutcomplete after，first purge/spitresidual toolhead filament，preventcut into pellets
                self.G_PhrozenFluiddRespondInfo("external macro-PG110；STM32load filament after，klipperstart purgecatch/connect hold load filament")
                self.PG102Flag=True
                logging.info("self.Flag=True")
                command_string = """
                PG110
                """
                self.G_PhrozenGCode.run_script_from_command(command_string)
                self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)
                self.PG102Flag=False
                logging.info("self.Flag=False")


            #lancaigang240229：directlyzaxis down lower，no need to wait area
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
                self.G_PhrozenFluiddRespondInfo("Zaxis down pull lower low；command_string='%s'" % command_string)



            #lancaigang240223：if cut filament failure，onfunction alreadyZaxis down lower，already pause then not execute down side/face operation
            if self.ToolheadCutFlag==True:
                self.ToolheadCutFlag=False
                self.G_PhrozenFluiddRespondInfo("before cut filament abnormal，filament change failure")
                self.G_ChangeChannelFirstFilaFlag=True
                self.G_IfChangeFilaOngoing= False

                #stm32on report pause only can pause1time(s)，cannot repeat pause
                self.STM32ReprotPauseFlag=1
                #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
                self.G_ChangeChannelFirstFilaFlag=True

                #lancaigang250308：resume itself already cut filament abnormal，here also report cut filament abnormal
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d" % self.G_ChangeChannelTimeoutNewChan)
                #self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                #lancaigang240416:
                if self.G_SerialPort1OpenFlag == True:
                    #lancaigang240603：preventAMSalwaysstop not
                    self.Cmds_AMSSerial1Send("AT+PAUSE")
                    logging.info("serial port1-AT+PAUSEpausestm32motor")
                #lancaigang241030:
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AT+PAUSE")
                    logging.info("serial port2-AT+PAUSEpausestm32motor")



                if self.G_KlipperInPausing == False:
                    self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                    #lancaigang250607:
                    self.G_PhrozenFluiddRespondInfo("enable quick pause")
                    self.G_KlipperQuickPause = True
                    #klipperactive/manual pause
                    self.Cmds_PhrozenKlipperPause(None)
                else:
                    self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")



                self.G_KlipperIfPaused = True

                #lancaigang240325：change failed，cannot execute resume
                self.G_MCModeCanResumeFlag = False

                if len(self.G_PauseToLCDString)==0:
                    self.G_PhrozenFluiddRespondInfo("+PAUSE:8,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                else:
                    self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+C:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                self.G_PhrozenFluiddRespondInfo("return")
                return

            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            # #lancaigang231208：zaxis-negative will toward down
            # #lancaigang231213：F7200change is300
            # #lancaigang231215：Zaxis on rise after mustremember down lower
            # command_string = """
            #     G90
            #     G1 X%.3f Y%.3f F8000
            #     G91
            #     G1 Z-%f F8000
            #     """ % (
            #     self.G_DictChangeChannelWaitAreaParam["X"],
            #     self.G_DictChangeChannelWaitAreaParam["Y"],
            #     self.G_AMSFilaCutZPositionLiftingUp,
            # )
            # self.G_PhrozenGCode.run_script_from_command(command_string)
            # #lancaigang231216：if filament change during pointclick pause，justgood filament change during lift risezaxis，to execute pause when，zaxis height also save，causes overall height abnormal
            # self.G_IfZPositionLiftUpFlag = False
            # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]internalgcodeto wait areax y zaxis down pull lower low；command_string='%s'" % command_string)


            #set flag
            Lo_ChangeChannelIfSuccess = False
            self.G_PhrozenFluiddRespondInfo("Lo_ChangeChannelIfSuccess = False")


            #lancaigang231202：ifP9command movepatharray is empty，causeslenfunction abnormal causesklippercrash
            # is0then press/by path running
            #lancaigang231206：UIinterface if pause resume，is withoutP9set area zone ，back-and-forth movement array is empty，codedump
            if self.ChangeWaitMoveArea is None:
                self.G_PhrozenFluiddRespondInfo("wait area movement abnormal;klipperpause")
                Lo_ChangeChannelIfSuccess = False
                pass

            if self.ChangeWaitMoveArea is not None:
                #empty list
                if len(self.ChangeWaitMoveArea) == 0:
                    self.G_PhrozenFluiddRespondInfo("return;wait area movement abnormal，press/by path return;if len(self.ChangeWaitMoveArea) == 0")
                    #lancaigang231206：continue execution below
                    #return
                else:
                    self.G_PhrozenFluiddRespondInfo("for;wait area zone back-and-forth move normal，pathqueue repeatedly back-and-forth，wait filament change new filament toreach toolhead")


                # #lancaigang240306：moved to cut filament code
                # #lancaigang240110：wait area zone wait before，first execute external macro，move tospecial fixed/set position performexecute/row wait
                # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]external macro-PG101")
                # command_string = """
                #     PG101
                #     """
                # self.G_PhrozenGCode.run_script_from_command(command_string)
                # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]external macro-tospecified position wait purge；command_string='%s'" % command_string)
                # self.IfDoPG102Flag=True

                #lancaigang250519:
                self.G_PhrozenFluiddRespondInfo("external macro-PRZ_SPITTING_SCRAPE")
                command_string = """
                    PRZ_SPITTING_SCRAPE
                    """
                self.G_PhrozenGCode.run_script_from_command(command_string)
                self.G_PhrozenFluiddRespondInfo("external macro-scrape；command_string='%s'" % command_string)


                #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                self.G_KlipperPrintStatus= 2
                # Python enumerate() function
                # enumerate() combines a traversable data object (list, tuple, or string) into an index sequence, listing data and indices, typically used in for loops.
                # Available in Python 2.3+, start parameter added in 2.6.
                # for loop using enumerate
                # >>> seq = ['one', 'two', 'three']
                # >>> for i, element in enumerate(seq):
                # ...     print i, element
                # ...
                # 0 one
                # 1 two
                # 2 three
                #wait area zone back-and-forth movement，largeapproximately80seconds timeout；move by rectangle step size
                #for i in range(CHANGE_CHANNEL_WAIT_TIMEOUT):#largeapproximately120seconds
                #for num, point in enumerate(self.ChangeWaitMoveArea):
                for num in range(CHANGE_CHANNEL_WAIT_TIMEOUT):
                    #lancaigang231202：ifSTM32active/manual on report pause，needklipperpause
                    if self.STM32ReprotPauseFlag==1:
                        # Lo_ChangeChannelIfSuccess = False
                        # break
                        #lancaigang231205：if wait during hasstm32active/manual on report pause，this time directlyretract out，no need toward down pause
                        self.G_PhrozenFluiddRespondInfo("wait filament change during，stm32active/manual on reportpause")

                        Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                        logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                        logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                        #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                        if Lo_PauseStatus['is_paused'] == True:
                            logging.info("already in paused state")
                        else:
                            logging.info("not in paused state")
                        Lo_ChangeChannelIfSuccess = False
                        break


                    # #lancaigang231214：wait area zone base pointX Yby/withW Hrectangle step size back-and-forth move，implement purge function
                    # command_string = """
                    #     G90
                    #     G1 X%.03f Y%.03f F%d
                    #     """ % (
                    #     point[0]+(num%2),#Xbase coordinate；lancaigang231215：wait area zonexcoordinate offset right mm，prevent normal print toolheadcollide to material leak
                    #     point[1]+(num%2),#Ybase coordinate
                    #     int(self.G_WaitAreaEachStepDist / self.G_MovementSpeedFactor),#rate
                    #     #500
                    # )
                    # #lancaigang231129：slow back-and-forth movement
                    # self.G_PhrozenGCode.run_script_from_command(command_string)
                    # self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]wait filament change during，base coordinateXYisP9config")


                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]wait filament change during，use external macro")


                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]num='%d'" % num)
                    #lancaigang20231014：wait toolhead move tospecified position，willconsume a some when interval，1seconds left right
                    self.G_ProzenToolhead.wait_moves()
                    #self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]self.G_ProzenToolhead.wait_moves()")

                    #lancaigang231219：change isdwell
                    #lancaigang231209
                    #time.sleep(2)
                    #lancaigang231115：change is1s
                    self.G_ProzenToolhead.dwell(1)

                    logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

                    self.G_PhrozenFluiddRespondInfo("external macro-PG110；STM32load filament after，klipperstart purgecatch/connect hold load filament")
                    command_string = """
                    PG110
                    """
                    self.G_PhrozenGCode.run_script_from_command(command_string)
                    self.G_PhrozenFluiddRespondInfo("command_string='%s'" % command_string)



                    logging.info("current mode")
                    self.Device_ReportModeIfChanged()


                    Lo_PauseStatus=self.G_PhrozenPrinterCancelPauseResume.get_status(None)
                    logging.info("current pause status-Lo_PauseStatus='%s'" % Lo_PauseStatus)
                    logging.info("Lo_PauseStatus['is_paused']='%s'" % Lo_PauseStatus['is_paused'])
                    #// current pause status-Lo_PauseStatus='{'is_paused': True}'
                    if Lo_PauseStatus['is_paused'] == True:
                        logging.info("already in paused state")
                    else:
                        logging.info("not in paused state")



                    #lancaigang250111:forloop purgepress/extrude outmachine movement，prevent load filament jam atpress/extrude outwheel


                    #lancaigang240125：cannot usesleep，willblock main thread
                    #time.sleep(1)

                    # #lancaigang231129：if seconds after found toolhead still detect to filament，indicates toolhead cut filament abnormal，need pauseklipper
                    # if num == 3 and point[2] and self.G_ToolheadIfHaveFilaFlag:
                    #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]cut filament5secondstoolhead still detect to filament，cutter abnormal，please check cutter，pauseklipperprint")
                    #     Lo_ChangeChannelIfSuccess = False
                    #     break
                    # elif num > 3:
                    #     self.G_PhrozenFluiddRespondInfo("[(cmds.python)Cmds_P1CnAutoChangeChannel]cut filament success，continue wait new filamentchange enter")

                    # 10seconds afterand point allow detectand detect to filament
                    #lancaigang20231013：10change is8
                    #lancaigang231129：if cut filament not success，stm32will reserved on time(s)command and continue execute filament change action，butactual on filament alsoretract not carriage return go，and here past/overseveral seconds if detect to toolhead has filament，will continueklipperprint causes without filament also empty print
                    #lancaigang231129：change is seconds later detect toolhead isnot has filament，normal filament change time，5seconds inside cutter can cut filament，stm32motor and retract filament，this time toolhead is no method/way detect to filament ，30seconds after again detect isnot has new filamentchange enter
                    if num > 1 and self.G_ToolheadIfHaveFilaFlag:
                        self.G_PhrozenFluiddRespondInfo("detect has new filament，indicates change success，can print")
                        Lo_ChangeChannelIfSuccess = True
                        break



            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))

            #if istruesuccess，then return
            if Lo_ChangeChannelIfSuccess:
                self.G_PhrozenFluiddRespondInfo("change success；")
                self.G_PhrozenFluiddRespondInfo("change success")
                self.G_IfChangeFilaOngoing= False

                #lancaigang250424：preventAMSbuffer not yet full
                self.G_ProzenToolhead.dwell(0.5)

                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()
                #lancaigang250423：load filament success，start purge，through/notify knowAMSstart count when，if purgeexceed past/over5seconds buffer still/orslow state，indicates clogged nozzle
                #self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                #self.G_PhrozenFluiddRespondInfo("AMSstart count when buffer full when interval")
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AT+EBLOCKCHECK")
                    self.G_PhrozenFluiddRespondInfo("serial port1-AMSstart count when buffer full when interval")
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AT+EBLOCKCHECK")
                    self.G_PhrozenFluiddRespondInfo("serial port2-AMSstart count when buffer full when interval")
                self.G_ProzenToolhead.dwell(1)

                #lancaigang240229:
                if self.IfDoPG102Flag==True:
                    self.IfDoPG102Flag=False

                    self.G_PhrozenFluiddRespondInfo("purge start")
                    self.G_PhrozenFluiddRespondInfo("+MSG:1,0,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))


                    #lancaigang241031：control purge count
                    #lancaigang250324：default isPG113，purge3time(s)
                    if self.G_P10SpitNum==0:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG113")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG113
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==1:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG111")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG111
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==2:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG112")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG112
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==3:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG113")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG113
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==4:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG114")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG114
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    #lancaigang250528：
                    elif self.G_P10SpitNum==5:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG115")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG115
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    #lancaigang250528：
                    elif self.G_P10SpitNum==6:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG116")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG116
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==7:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG117")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG117
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==8:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG118")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG118
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)
                    elif self.G_P10SpitNum==9:
                        self.G_PhrozenFluiddRespondInfo("external macro-PG119")
                        self.PG102Flag=True
                        logging.info("self.Flag=True")
                        command_string = """
                        PG119
                        """
                        self.G_PhrozenGCode.run_script_from_command(command_string)
                        self.G_PhrozenFluiddRespondInfo("external macro-arrange waste material；command_string='%s'" % command_string)

                    self.PG102Flag=False
                    logging.info("self.Flag=False")

                    self.G_PhrozenFluiddRespondInfo("purge end")

                    # for i in range(15):
                    #     self.G_PhrozenFluiddRespondInfo("[(dev.python)]purge in，wait")
                    #     #lancaigang20231013：change is4seconds delay
                    #     #lancaigang231115：change is1s
                    #     self.G_ProzenToolhead.dwell(1.0)
                    #     #lancaigang240125：cannot usesleep，willblock main thread
                    #     #time.sleep(1)
                    if self.PG102DelayPauseFlag==True:
                        self.PG102DelayPauseFlag=False

                        #lancaigang250619:checkAMSisnot re-connect success
                        self.Cmds_USBConnectErrorCheck()
                        #lancaigang250427：
                        if self.G_SerialPort1OpenFlag == True:
                            self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                            logging.info("serial port1-AMSend count when buffer full when interval")
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                            logging.info("serial port2-AMSend count when buffer full when interval")

                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        self.G_PhrozenFluiddRespondInfo("purge process in，STM32triggersendrunout pause")
                        #lancaigang231209：timer in handle business，will causes business abnormal，after side/face need use thread handle interrupt business

                        if self.G_KlipperInPausing == False:
                            self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                            #lancaigang250607:
                            self.G_PhrozenFluiddRespondInfo("enable quick pause")
                            self.G_KlipperQuickPause = True
                            #klipperactive/manual pause
                            self.G_PhrozenFluiddRespondInfo("STM32 reported pause, pausing once")
                            self.Cmds_PhrozenKlipperPauseNoneCmdToSTM32(None)
                        else:
                            self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")

                        self.G_KlipperIfPaused = True
                        #stm32active/manual pause only can pause1time(s)，cannot repeat pause
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
                        self.G_ChangeChannelFirstFilaFlag=True

                        self.G_ProzenToolhead.dwell(1.5)
                        self.G_PhrozenFluiddRespondInfo("+MSG:1,1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        #lancaigang240524：use inUIUXdynamic interface
                        self.G_PhrozenFluiddRespondInfo("+C:1,%d" % self.G_ChangeChannelTimeoutNewChan)


                        #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                        #lancaigang250529:
                        if len(self.G_PauseToLCDString)==0:
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                        #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                        self.G_KlipperPrintStatus= 3
                        self.G_PauseToLCDString=""

                        self.G_PhrozenFluiddRespondInfo("return")
                        return

                        #lancaigang240326：purge during pause，system a use pause1indicates
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:1,%d" % self.G_ChangeChannelTimeoutNewChan)
                    else:
                        self.G_PhrozenFluiddRespondInfo("purge process normal，perform enter print")
                        #lancaigang250527：change success and perform entergocdetext piece/piece/piece/piece/piece print
                        #lancaigang250527：quick pause execution
                        self.G_KlipperQuickPause = True


                self.G_PhrozenFluiddRespondInfo("+MSG:1,1,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))

                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()
                #lancaigang250427：
                if self.G_SerialPort1OpenFlag == True:
                    self.Cmds_AMSSerial1Send("AT+EBLOCKEND")
                    logging.info("serial port1-AMSend count when buffer full when interval")
                if self.G_SerialPort2OpenFlag == True:
                    self.Cmds_AMSSerial2Send("AT+EBLOCKEND")
                    logging.info("serial port2-AMSend count when buffer full when interval")
                self.G_ProzenToolhead.dwell(1.5)



                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+C:1,%d" % self.G_ChangeChannelTimeoutNewChan)


                #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                self.G_KlipperPrintStatus= 3

                self.G_PauseToLCDString=""

                self.G_PhrozenFluiddRespondInfo("normal perform enter print")

                return





            self.G_PhrozenFluiddRespondInfo("change failed")
            logging.info("self.G_ToolheadIfHaveFilaFlag=%d" % (self.G_ToolheadIfHaveFilaFlag))
            # change failed
            if self.G_DictChangeChannelWaitAreaParam["A"] == 0:
                self.G_PhrozenFluiddRespondInfo("change failed；filament load filament timeout；cmd='%s', all retract filament，klipperpause")
                self.G_PhrozenFluiddRespondInfo("change failed；currentbuffer store command='%s';klipperpause" % (self.G_ChangeChannelTimeoutOldGcmd.get_commandline()))

                #lancaigang250527：quick pause execution
                self.G_KlipperQuickPause = False

                #lancaigang250619:checkAMSisnot re-connect success
                self.Cmds_USBConnectErrorCheck()

                # #lancaigang231129：klipperpause when，toolhead move toz=10；x=150；y=10
                # command_string = """
                # G91
                # G1 z10 F600
                # G90
                # G1 X150 F600
                # G1 Y10 F600
                # """
                # self.G_PhrozenGCode.run_script_from_command(command_string)

                #lancaigang231201：klipperpause whenstm32motor cannotmove/action
                # gcmd.respond_info("send command: AP，all retract to park position")
                # #// all retract to park position；//===== P2 A1 all filament to park position for print Yes；"AP"；
                # self.Cmds_AMSSerial1Send("AP")
                # logging.info("SendCmd: AP")
                if self.G_KlipperIfPaused==False:
                    #lancaigang250702：
                    if self.G_KlipperInPausing == False:
                        self.G_PhrozenFluiddRespondInfo("not pausing，allow new pause")
                        self.STM32ReprotPauseFlag=1
                        #lancaigang231202：P1 C?auto filament change when，if1time(s)channel then load filament abnormal pause，if need resume，also continue from1time(s)channel start
                        self.G_ChangeChannelFirstFilaFlag=True


                        #lancaigang240416:
                        if self.G_SerialPort1OpenFlag == True:
                            #lancaigang240603：preventAMSalwaysstop not
                            self.Cmds_AMSSerial1Send("AT+PAUSE")
                            logging.info("serial port1-AT+PAUSEpausestm32motor")
                        #lancaigang241030:
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+PAUSE")
                            logging.info("serial port2-AT+PAUSEpausestm32motor")

                        self.G_PhrozenFluiddRespondInfo("enable quick pause")
                        self.G_KlipperQuickPause = True
                        #klipperactive/manual pause
                        self.Cmds_PhrozenKlipperPause(None)
                        self.G_KlipperIfPaused = True
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)

                        self.G_PhrozenFluiddRespondInfo("change timeout60s，pause")
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        #lancaigang250529:
                        if len(self.G_PauseToLCDString)==0:
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                    else:
                        self.G_PhrozenFluiddRespondInfo("pausing，not allow new pause")
                #lancaigang240124：cannot repeat pause
                else:
                    self.G_PhrozenFluiddRespondInfo("already pause，no need repeat pause")
                    # #lancaigang250529:
                    # if len(self.G_PauseToLCDString)==0:
                    #     self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    # else:
                    #     self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                    #self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                    #lancaigang240417：preventstm32not on report whenG_PauseToLCDStringis empty situation
                    #if len(self.G_PauseToLCDString)==0:
                    #    self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    #lancaigang250529:
                    if len(self.G_PauseToLCDString)==0:
                        self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                    else:
                        self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)
                    #lancaigang240416:
                    if self.G_SerialPort1OpenFlag == True:
                        #lancaigang240603：preventAMSalwaysstop not
                        self.Cmds_AMSSerial1Send("AT+PAUSE")
                        logging.info("serial port1-AT+PAUSEpausestm32motor")
                    #lancaigang241030:
                    if self.G_SerialPort2OpenFlag == True:
                        self.Cmds_AMSSerial2Send("AT+PAUSE")
                        logging.info("serial port2-AT+PAUSEpausestm32motor")
                    #lancaigang240429：if resume process instm32and without on report pause state，here need on report pause
                    # if self.G_ResumeProcessCheckPauseStatus==False:
                    #     self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d" % self.G_ChangeChannelTimeoutNewChan)

                    if self.G_ResumeProcessCheckPauseStatus==False:
                        self.G_PhrozenFluiddRespondInfo("AMSwithout on report pause，klipperrepeat pause，need on report pause")
                        #self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        #lancaigang250529:
                        if len(self.G_PauseToLCDString)==0:
                            self.G_PhrozenFluiddRespondInfo("+PAUSE:4,%d,%d" % (self.G_ChangeChannelTimeoutOldChan,self.G_ChangeChannelTimeoutNewChan))
                        else:
                            self.G_PhrozenFluiddRespondInfo(self.G_PauseToLCDString)

                        #lancaigang240416:
                        if self.G_SerialPort1OpenFlag == True:
                            #lancaigang240603：preventAMSalwaysstop not
                            self.Cmds_AMSSerial1Send("AT+PAUSE")
                            logging.info("serial port1-AT+PAUSEpausestm32motor")
                        #lancaigang241030:
                        if self.G_SerialPort2OpenFlag == True:
                            self.Cmds_AMSSerial2Send("AT+PAUSE")
                            logging.info("serial port2-AT+PAUSEpausestm32motor")
                    else:
                        self.G_PhrozenFluiddRespondInfo("AMShas on report pause，klippernot need need on report pause")
                        self.G_ResumeProcessCheckPauseStatus=False

                    # self.G_PhrozenFluiddRespondInfo("already pause，again pause1time(s)，prevent before pause abnormal")
                    # #lancaigang250423：isprevent abnormal pause not hold，many/more pause1time(s)
                    # #klipperactive/manual pause
                    # self.Cmds_PhrozenKlipperPause(None)

                #lancaigang231207：P1 C?auto filament change when，if need resume，also continue from1time(s)channel start
                self.G_ChangeChannelFirstFilaFlag=True
                self.G_IfChangeFilaOngoing= False

                #lancaigang240524：use inUIUXdynamic interface
                self.G_PhrozenFluiddRespondInfo("+C:1,%d" % self.G_ChangeChannelTimeoutNewChan)

                #lancaigang250607：print state；1-unload filament in；2-load filament in；3-print in；4-pause
                self.G_KlipperPrintStatus= -1

                return

            #lancaigang20231013：Actionnormal filament change=1
            if self.G_DictChangeChannelWaitAreaParam["A"] == 1:
                pass
