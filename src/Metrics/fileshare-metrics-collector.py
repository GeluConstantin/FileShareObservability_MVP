"""
###############################################################
#
# Author: Gelu Liuta
# Creation date: 01.06.2023
# Version: 1.0.0
#
# The code is MVP (minimal viable product) for Windows file share observability and should be used accordingly
# Core components: python libraries (os, heapq, time) and the prometheus instrumentation library prometheus_client
###############################################################
"""

import heapq
import os
import sys
import time

import socket

import win32serviceutil

import servicemanager
import win32event
import win32service

from prometheus_client import start_http_server, Gauge

# Prometheus client for instrumentation
# the start_ttp_server is the metrics endpoint which will be scraped by Prometheus server to collect the metrics

# define the metrics which should be transfered to Prometheus
NUMBER_FILES_IN_SHARE= Gauge('number_of_file', 'Number of files in the target file share')
NUMBER_DIRECTORIES_IN_SHARE= Gauge('number_of_directories', 'Number of files in the target file share')
FILESHARE_SIZE = Gauge('fileshare_size', 'The size of the fileshare')

# Decorate function with metric.
@NUMBER_FILES_IN_SHARE.time()
@NUMBER_DIRECTORIES_IN_SHARE.time()
@FILESHARE_SIZE.time()
def collect_metrics(fileSharePath):

    kpis = count_files_and_directories(fileSharePath)
    fileshareSize = folder_size(fileSharePath)

    NUMBER_FILES_IN_SHARE.set(kpis[1])
    NUMBER_DIRECTORIES_IN_SHARE.set(kpis[0])
    FILESHARE_SIZE.set(fileshareSize)

    time.sleep(30)


def count_files_and_directories(fileSharePath):
    """a python function to collect the metrics for total number of files and directories in a file share path
        total_number_kpis[] = an array to collect the total number of files and directories in the target file shared defined by the
        function parameter fileSharePath
        index 0 = total number of directories
        index 1 = total number of files
        index 2 = total number of files and directories
    """

    total_number_kpis = [0,0,0]

    for base, dirs, files in os.walk(fileSharePath):
        # print('Searching in : ',base)
        for directories in dirs:
            total_number_kpis[0] += 1
        for Files in files:
            total_number_kpis[1] += 1

    total_number_kpis[2]=total_number_kpis[0]+total_number_kpis[1]

    return total_number_kpis


def folder_size(fileSharePath):
    """ a python function to collect the metrics for file share path in Bytes
    """

    fileShare_size = 0

    # calculate the file share size in Bytes

    for path, dirs, files in os.walk(fileSharePath):
        for f in files:
            fp = os.path.join(path, f)
            fileShare_size += os.stat(fp).st_size

    # display file share size in Bytes
    # print("Folder size: " + str(fileShare_size))

    return fileShare_size


def oldest_file_in_tree(fileSharePath, count=1, extension=""):
    """" a python function to identify the oldest file in the file share
        a file filter can be defined with the function parameter extension: for example extension=".sql"
        if no file filter is wanted, use the parameter extension="""

    return heapq.nsmallest(count,
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(fileSharePath)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)


def newest_file_in_tree(fileSharePath, count=1, extension=""):
    """ a python function to identify the oldest file in the file share
        a file filter can be defined with the function parameter extension: for example extension=".sql"
        if no file filter is wanted, use the parameter extension="""

    return heapq.nlargest(count,
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(fileSharePath)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime)

class FileShareObserverService:
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
            collect_metrics(r"\\domoff.local\dml\Software\Test_GeluLiuta")

class GenericWindowsService(win32serviceutil.ServiceFramework):
    """
    this class is responsible to run the Python module as a Windows Service
    """

    _svc_name_ = "FileShareObserver"
    _svc_display_name_ = "FileShare Observer"
    _svc_description_ = "FieShare Observer is a service written in Python which monitors fileshares"

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
        self.service_impl = FileShareObserverService()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.service_impl.run()


if __name__ == '__main__':

    # A console print for test purposes, the section can be commented out, it has no impact on the python module
    # print ("Die überwachte FileShare ist: "+ r"\\domoff.local\dml\Software\Test_GeluLiuta")
    #
    # kpis= count_files_and_directories(r"\\domoff.local\dml\Software\Test_GeluLiuta")
    #
    # print("Anzahl Ordner: " + str(kpis[0]))
    # print("Anzahl Dateien: " + str(kpis[1]))
    # print("Anzahl Ordner + Dateien: " + str(kpis[2]))
    #
    # print ("FileShare Grösse in Bytes: " + str(folder_size(r"\\domoff.local\dml\Software\Test_GeluLiuta")) + " Bytes")
    #
    # print("Die älteste Datei in dem FileShare ist: " + str(oldest_file_in_tree(r"\\domoff.local\dml\Software\Test_GeluLiuta")))
    # print("Die neueste Datei in dem FileShare ist: " + str(newest_file_in_tree(r"\\domoff.local\dml\Software\Test_GeluLiuta")))
    #
    # # Prometheus agent
    #
    # start_http_server(8000)
    # while True:
    #     collect_metrics(r"\\domoff.local\dml\Software\Test_GeluLiuta")

    '''
    
    start the python module as a Windows service
    this is a standard code to initialize the service
    before initializing the service the http server for prometheus must be started, using a custom port
    
    '''
    if len(sys.argv) == 1:
        start_http_server(8001)
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GenericWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GenericWindowsService)