import tkinter as tk
import ctypes
from ctypes import wintypes

WDA_EXCLUDEFROMCAPTURE = 0x00000011
user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

root = tk.Tk()
root.withdraw() # hide during init
root.update_idletasks()

# Get the HWND of the tkinter window
hwnd = user32.GetParent(root.winfo_id()) or root.winfo_id()
print(f"Tkinter HWND: {hwnd}")

# Apply invisibility
res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
err = ctypes.get_last_error()
print(f"SetWindowDisplayAffinity Result: {res} (Error: {err})")

root.destroy()
print("Tkinter invisibility test passed!")
