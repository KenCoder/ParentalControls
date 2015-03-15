
"""
Usage : python Watcher.py [install start stop remove test]

C:\>python Watcher.py  --username <username> --password <PASSWORD> --startup auto install
"""

import subprocess
import time
import sys
import os
import datetime
import urllib
import win32service
import win32api
import win32event
import logging
import win32security

import wmi
import yaml
import win32serviceutil

from WatcherLib import games_allowed

mydir = os.path.dirname(os.path.realpath(__file__))


def AdjustPrivilege( priv ):
    flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    htoken =  win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    id = win32security.LookupPrivilegeValue(None, priv)
    newPrivileges = [(id, win32security.SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

schedule = r'https://www.dropbox.com/s/j5g11lhkb8gvlyv/Duncan.txt?dl=1'
log_frequency = 60
last_full = 0
wmi_api = None
warned = set()
initialized = False
running = set()

def execute_loop():
    global last_full, wmi_api, initialized, running
    if not initialized:
        logging.basicConfig(filename=os.path.join(mydir, 'watcher.log'), level=logging.INFO,
                            format='%(asctime)s %(message)s')
        AdjustPrivilege("seDebugPrivilege")
        logging.info("Initialized")
        initialized = True

    f = urllib.urlopen(schedule)
    config = yaml.safe_load(f)
    f.close()
    had_block = False
    full_log = time.time() - last_full > log_frequency

    if wmi_api is None:
        wmi_api = wmi.WMI()

    procs = wmi_api.Win32_Process()

    sched = config['Schedule']

    now = datetime.datetime.now()
    allowed = games_allowed(sched, now)
    if full_log:
        logging.info("Running %s allowed %s" % (str(config), allowed))
    
    if allowed:
        for how_much in [1, 2]:
            if not how_much in warned and not games_allowed(sched, now + datetime.timedelta(minutes=how_much)):
                warned.add(how_much)
                subprocess.call(os.path.join(mydir, 'warn%s.wma' % how_much), shell=True)
                break
    else:
        warned.clear()
    current = set()

    for process in procs:
        block = len([x for x in config['Block']['Programs'] if x.lower() == process.Name.lower()]) > 0
        current.add(process.Name)
        if process.ExecutablePath:
            root = os.path.dirname(process.ExecutablePath)
            block = block or len([x for x in config['Block']['Folders'] if os.path.isdir(os.path.join(root, x))]) > 0
            if not allowed and block:
                try:
                    process.Terminate()
                    had_block = True
                    logging.warning("Terminated program %s" % process.Name)
                except:
                    logging.exception("Unexpected error terminating %s" % process.name)

        if had_block:
            subprocess.call(os.path.join(mydir, 'blocked.wma'), shell=True)
        if full_log:
            last_full = time.time()
    if current != running:
        started = current - running
        if len(started) > 0:
            logging.info("Started %s" % started)
        stopped = running - current
        if len(stopped) > 0:
            logging.info("Stopped %s" % stopped)
        running = current

class Watcher(win32serviceutil.ServiceFramework):
    _svc_name_ = "Game Watcher"
    _svc_display_name_ = "GameWatcher"
    _svc_description_ = "Ken's Service for restricting kids game access"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        import servicemanager

        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))

        self.timeout = 10000
        while True:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                servicemanager.LogInfoMsg("Service - STOPPED")
                break
            try:
                execute_loop()
            except:
                logging.exception("Exception in service")

def ctrlHandler(ctrlType):
    return True

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        while True:
            execute_loop()
            time.sleep(10)
    else:
        win32api.SetConsoleCtrlHandler(ctrlHandler, True)
        win32serviceutil.HandleCommandLine(Watcher)


