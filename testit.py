import ctypes
import ctypes.wintypes as wintypes
user32 = ctypes.windll.User32


def enum_desktops():
    GetProcessWindowStation = user32.GetProcessWindowStation

    EnumDesktops = user32.EnumDesktopsW
    EnumDesktopsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.LPWSTR, wintypes.LPARAM)
    hwinsta = GetProcessWindowStation()

    def foreach_desktop(desk_name, lparam):
        print("Desktop %s"%desk_name)
        return True
    EnumDesktops(hwinsta, EnumDesktopsProc(foreach_desktop), 0)


enum_desktops()