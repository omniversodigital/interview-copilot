"""
Ghost Cloak Utility (Windows DWM Compositor Stealth)
Applies WDA_EXCLUDEFROMCAPTURE (0x00000011) to hide windows from:
- Zoom Screen Sharing
- Google Meet Screen Sharing
- Microsoft Teams Screen Sharing
- Discord / OBS / Snipping Tool / PrintScreen

The window remains 100% visible on your physical screen, but completely transparent / invisible to screen shares.
"""

import ctypes
from ctypes import wintypes
import time

# Windows Constants
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011

user32 = ctypes.WinDLL("user32", use_last_error=True)

# SetWindowDisplayAffinity(HWND hWnd, DWORD dwAffinity)
user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

# GetWindowTextW
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int

# EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL

def find_windows_by_title_substring(substring: str):
    matches = []
    def enum_cb(hwnd, lparam):
        length = 512
        buffer = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buffer, length)
        title = buffer.value
        if substring.lower() in title.lower():
            matches.append((hwnd, title))
        return True
    user32.EnumWindows(EnumWindowsProc(enum_cb), 0)
    return matches

def cloak_window(hwnd: int) -> bool:
    res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
    if not res:
        err = ctypes.get_last_error()
        print(f"[-] Failed to cloak HWND {hwnd}: WinError {err}")
        return False
    print(f"[+] SUCCESS: HWND {hwnd} is now 100% INVISIBLE to Zoom, Meet & Teams screen sharing!")
    return True

def uncloak_window(hwnd: int) -> bool:
    res = user32.SetWindowDisplayAffinity(hwnd, WDA_NONE)
    return bool(res)

if __name__ == "__main__":
    import sys
    search_term = sys.argv[1] if len(sys.argv) > 1 else "Sovereign"
    print(f"Searching for windows containing: '{search_term}'...")
    windows = find_windows_by_title_substring(search_term)
    if not windows:
        print(f"No windows found matching '{search_term}'.")
    else:
        for hwnd, title in windows:
            print(f"Found Window: [HWND: {hwnd}] '{title}'")
            cloak_window(hwnd)
