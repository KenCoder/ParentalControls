import ctypes
import ctypes.wintypes as wintypes
user32 = ctypes.windll.User32
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

import wmi
import yaml
import win32serviceutil

from WatcherLib import games_allowed


def enum_desktops():
    GetProcessWindowStation = user32.GetProcessWindowStation

    EnumDesktops = user32.EnumDesktopsW
    EnumDesktopsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.LPWSTR, wintypes.LPARAM)
    hwinsta = GetProcessWindowStation()

    def foreach_desktop(desk_name, lparam):
        print("Desktop %s"%desk_name)
        return True
    EnumDesktops(hwinsta, EnumDesktopsProc(foreach_desktop), 0)

def get_first(name):
    wmi_api = wmi.WMI()
    procs = wmi_api.Win32_Process()
    res = [process for process in procs if process.Name.lower() == name.lower()]
    if len(res) == 0:
        return None
    else:
        return res[0]