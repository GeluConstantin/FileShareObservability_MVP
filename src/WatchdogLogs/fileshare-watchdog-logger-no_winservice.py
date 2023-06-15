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

if __name__ == '__main__':

    user = getpass.getuser()

    # filemode='a' to append to a log

    logging.basicConfig(filename='FileshareActivity.log', filemode='a', level=logging.INFO,
                        format='%(asctime)s | %(process)d | %(message)s' + f' | userid: {user}',
                        datefmt='%Y-%m-%d %H:%M:%S')


    #UNC path to be observed is defined by the path variable
    # path = sys.argv[1] if len(sys.argv) > 1 else '.' # if no path variabled passed at the start of the execution then the execution folder will be monitored

    path = r"\\domoff.local\dml\Software\Test_GeluLiuta"

    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()