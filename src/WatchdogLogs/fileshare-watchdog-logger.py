###############################################################
#
# Author: Gelu Liuta
# Creation date: 01.06.2023
# Version: 1.0.0
#
# The code is MVP (minimal viable product) for Windows file share observability and should be used accordingly
# The app tracks the fileshare activity and save it as a log
# Core components: python libraries (watchdog, sys, logging, getapass, time) and the prometheus instrumentation library prometheus_client
###############################################################

import sys

import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import logging
import getpass

import socket
import win32serviceutil
import servicemanager
import win32event
import win32service

def log_Fileshare_Activity(path):

    filesharepath = path
    user = getpass.getuser()

    # filemode='a' to append to a log

    logging.basicConfig(filename='D:/ProgramFiles/CAP/fileshareObserver/log/FileshareActivity.log', filemode='a', level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(message)s' + f' | userid: {user}',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # UNC path to be observed is defined by the path variable
    # path = sys.argv[1] if len(sys.argv) > 1 else '.' # if no path variabled passed at the start of the execution then the execution folder will be monitored

    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, filesharepath, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


class FileShareWatchdogLoggerService:
    """the class where the business logic is implemented"""
    def stop(self):
        """Stop the service"""
        self.running = False

    def run(self):
        """Main service loop. This is where work is done!"""
        self.running = True
        while self.running:
            # time.sleep(10)  # Important work
            servicemanager.LogInfoMsg("Service running...")

            # business logic must be implemented in this section
            log_Fileshare_Activity(r"\\domoff.local\dml\Software\Test_GeluLiuta")


class GenericWindowsService(win32serviceutil.ServiceFramework):
    """
    this class is responsible to run the Python module as a Windows Service
    """

    _svc_name_ = "FileShareActivity Logger"
    _svc_display_name_ = "FileShareActivity Logger"
    _svc_description_ = "FileShareActivity Logger is a service written in Python which logs the activity on a target fileshare"

    def __init__(self, args):
        '''
        Constructor of the Windows service
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)


    def SvcStop(self):
        '''
        Called when the Windows service is asked to stop
        '''


        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_impl.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)


    def SvcDoRun(self):

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.service_impl = FileShareWatchdogLoggerService()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.service_impl.run()

if __name__ == '__main__':

    '''

    start the python module as a Windows service
    this is a standard code to initialize the service
    before initializing the service the http server for prometheus must be started, using a custom port

    '''
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GenericWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GenericWindowsService)



    # user = getpass.getuser()
    #
    # # filemode='a' to append to a log
    #
    # logging.basicConfig(filename='.\log\FileshareActivity.log', filemode='a', level=logging.INFO,
    #                     format='%(asctime)s | %(process)d | %(message)s' + f' | userid: {user}',
    #                     datefmt='%Y-%m-%d %H:%M:%S')
    #
    #
    # #UNC path to be observed is defined by the path variable
    # # path = sys.argv[1] if len(sys.argv) > 1 else '.' # if no path variabled passed at the start of the execution then the execution folder will be monitored
    #
    # path = r"\\domoff.local\dml\Software\Test_GeluLiuta"
    #
    # event_handler = LoggingEventHandler()
    # observer = Observer()
    # observer.schedule(event_handler, path, recursive=True)
    # observer.start()
    #
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    #     observer.join()