####################################
#Project name:
#Chip type:
#Feature:
#Developer: Lan Caigang
#Development date: 20230830
####################################

import binascii
import logging
import time
import struct
import serial
import re

from .cwebsocketapis import *
from .dev_runout import RunoutMixin
from .dev_uart_handler import UartHandlerMixin
from .dev_uart_recv import UartRecvMixin




####################################
#Class name:
#Description: Lan Caigang-20230830
####################################
class PhrozenDev(UartRecvMixin, UartHandlerMixin, RunoutMixin, Apis):
    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #Constructor initialization
    def __init__(self, config):
        super(PhrozenDev, self).__init__(config)
        #Initialize event connectionklipper
        self.G_PhrozenPrinter.register_event_handler("klippy:connect", self.Device_KlipperConnectHandle)
        #Initialize event to cancel connectionklipper
        self.G_PhrozenPrinter.register_event_handler("klippy:disconnect", self.Device_KlipperDisconnectHandle)

        # dev.pyResetAMSRuntime parameters
        self.Device_ResetParams()

        # cmds.py；phrozenCustomGCODECommand
        self.Cmds_RegisterCmds()

        # cwebsocketapis.pyWeb pagewebsocket api
        self.WebsocketAPIs_RegisterAPIs()

        # dev.pyTest commandPRZ_TEST
        self.G_PhrozenGCode.register_command("PRZ_TEST", self.Device_CmdPhrozenTest, desc="PhrozenChromaKit MMU test command")
    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #AMSReset parameters
    # Report current mode to console (voronFDM parses these)
    def Device_ReportModeIfChanged(self):
        mode = self.G_AMSDeviceWorkMode
        mode_names = {
            AMS_WORK_MODE_UNKNOW: "+Mode:0,unkown",
            AMS_WORK_MODE_MC: "+Mode:1,MC",
            AMS_WORK_MODE_MA: "+Mode:2,MA",
            AMS_WORK_MODE_FILA_RUNOUT: "+Mode:3,RUNOUT",
        }
        self.G_PhrozenFluiddRespondInfo(mode_names.get(mode, "+Mode:-1,error"))

    def Device_ResetParams(self):
        logging.info("ChromaKit: resetting runtime parameters")
        self.G_FilaRunoutTimmer = None  # Filament runout handling timer
        self.G_LastP114State = None  # Track last ChromaKit state for change detection
        self.G_LastReportedMode = None  # Track last mode to suppress repeat console output
        self.G_SerialPort1RecvTimmer = None  # Serial receive timer
        #lancaigang241030：
        self.G_SerialPort2RecvTimmer = None  # Serial receive timer

        self.AMSRunoutPauseTimeCount = 0  # Wait time counter in the watchdog thread
        self.G_ToolheadFirstInputFila = False  # Initial filament feed
        self.P0M3FilaRunoutSpittingFinished = False
        self.AMSErrorRetryTimes = 0  # Error retry count
        #AMSChromaKit MMU status
        self.G_AMS1DeviceState = {}
        #lancaigang241105:
        self.G_AMS2DeviceState = {}

    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #Register filament runout detection periodic timer thread
    def Device_RegisterRunoutErrorThread(self):
        logging.info("ChromaKit: registering filament runout check timer")
        # Register filament runout handling periodic thread
        self.G_FilaRunoutTimmer = self.G_PhrozenReactor.register_timer(self.Device_TimmerRunoutCheck, self.G_PhrozenReactor.NOW + 0.5)
    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Device_UnregisterDaemonThread(self):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_UnregisterDaemonThread]")
        #Unregister
        self.G_PhrozenReactor.unregister_timer(self.G_FilaRunoutTimmer)
    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Device_ConnectAMSDevice(self):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_ConnectAMSDevice]phrozenExtensionpythonModule connectedAMSMulti-color")
        #Whether to auto-connectAMSChromaKit MMU
        #lancaigang240116Do not auto-connectAMS


    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Device_DisconnectAMSDevice(self):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_DisconnectAMSDevice]phrozenExtensionpythonModule disconnectedAMSMulti-color")
        self.Cmds_CmdP29(None)

    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    def Device_CmdPhrozenTest(self, gcmd):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_CmdPhrozenTest]gcmd.prz_testTest='%s'" % (gcmd.get_commandline(),))
        self.G_PhrozenFluiddRespondInfo("self.prz_testTest='%s'" % (gcmd.get_commandline(),))
        #klipperPause
        self.Cmds_PhrozenKlipperPause(None)



    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #Initial event registrationphrozenPlugin connectedklipper
    def Device_KlipperConnectHandle(self):
        logging.info("ChromaKit: phrozen_dev module connecting to Klipper")

        #lancaigang250724: Read system image ID to identify hardware variant
        self.Cmds_GetImageId()
        logging.info("ChromaKit: Image ID=%d", self.G_ImageId)

        # Get toolhead action
        self.G_ProzenToolhead = self.G_PhrozenPrinter.lookup_object("toolhead")
        #Manual toolhead move
        self.G_ToolheadManualMovement = self.G_ProzenToolhead.manual_move
        #Toolhead waiting for move to complete
        self.G_ToolheadWaitMovementEnd = self.G_ProzenToolhead.wait_moves
        #Toolhead last position
        self.G_ToolheadLastPosition = self.G_ProzenToolhead.get_position()
        # Register periodic filament runout detection thread
        self.Device_RegisterRunoutErrorThread()

        #lancaigang240430Because of power-loss recovery, ifAMSState has been saved - must not be overwritten after a power-loss restart
        #lancaigang240428IfklipperIf connection restarts, notifyAMSEnteridleState
        try:
            #Open serial port1Baud rate19200
            self.G_SerialPort1Obj = serial.Serial(self.G_Serialport1Define, SERIAL_PORT_BAUD, timeout=3)
            if self.G_SerialPort1Obj.is_open:
                #lancaigang231213Open serial port
                self.G_SerialPort1Obj.flushInput()
                self.G_SerialPort1Obj.flush()
                #lancaigang250115:Multi-color power-loss recovery
                logging.info("ChromaKit: serial port 1 - sending M0 reset")
                self.G_SerialPort1Obj.write("M0".encode())
                self.G_SerialPort1Obj.flush()
                self.G_SerialPort1Obj.close()
        except:
            logging.info("ChromaKit: serial port 1 not available at startup")

        #lancaigang241108：
        try:
            self.G_SerialPort2Obj = serial.Serial(self.G_Serialport2Define, SERIAL_PORT_BAUD, timeout=3)
            if self.G_SerialPort2Obj.is_open:
                self.G_SerialPort2Obj.flushInput()
                self.G_SerialPort2Obj.flush()
                logging.info("ChromaKit: serial port 2 - sending M0 reset")
                self.G_SerialPort2Obj.write("M0".encode())
                self.G_SerialPort2Obj.flush()
                self.G_SerialPort2Obj.close()
        except:
            logging.info("ChromaKit: serial port 2 not available at startup")


        #lancaigang240427：AMSUnexpected restart - must log this event
        self.G_AMS1ErrorRestartFlag = False
        self.G_AMS1ErrorRestartCount = 0

        #lancaigang241030:
        self.G_AMS2ErrorRestartFlag = False
        self.G_AMS2ErrorRestartCount = 0


        #lancaigang250514ReadjsonFile used to read single-color auto-refill config and channel-to-filament color mapping
        #/home/prz/klipper/klippy/extras/phrozen_dev/serial-screen/test.json




    ####################################
    #Function name:
    #Input parameters:
    #Return Value:
    #Description: Lan Caigang-20230830
    ####################################
    #Initial event registrationphrozenPlugin cancelled connectionklipper
    def Device_KlipperDisconnectHandle(self):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)Device_KlipperDisconnectHandle]phrozenExtensionpythonModule disconnectedklipper")
        #Cancel connectionAMSChromaKit MMU
        self.Device_DisconnectAMSDevice()
        self.Device_UnregisterDaemonThread()
        #ResetAMSRuntime parameters
        self.Device_ResetParams()


####################################
#Function name:
#Input parameters:
#Return Value:
#Description: Lan Caigang-20230830
####################################
#lancaigang0914Cannot move position; callingPhrozenDev class
def load_config(config):
    return PhrozenDev(config)
