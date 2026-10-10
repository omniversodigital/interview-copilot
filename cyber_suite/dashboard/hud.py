# cyber_suite/dashboard/hud.py
"""Dashboard UI for the Cyber Suite.
Provides a stealth‑aware Tkinter window with three tabs:
1. Live Scan View – displays recent scan results from the persistence DB.
2. Session Manager – lists active Metasploit/Empire sessions.
3. Log Viewer – shows audit logs.
The window uses the same `SetWindowDisplayAffinity` flag as the main HUD so it
remains invisible to screen‑share tools.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import ctypes
from ctypes import wintypes
import json
import threading
import time

# Import persistence utilities
from .. import persistence

# Windows API constants for invisibility
WDA_EXCLUDEFROMCAPTURE = 0x00000011
user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

class CyberDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sovereign Cyber Suite Dashboard")
        self.root.geometry("900x500+200+150")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#0a0c12")
        # Make window borderless but keep close button via custom UI
        self.root.overrideredirect(False)
        self.apply_invisibility()
        self.build_ui()
        # Auto‑refresh thread
        self.refresh_interval = 5  # seconds
        self._stop = threading.Event()
        threading.Thread(target=self.auto_refresh, daemon=True).start()

    def apply_invisibility(self):
        self.root.update_idletasks()
        hwnd = user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
        res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        if not res:
            err = ctypes.get_last_error()
            print(f"[!] Dashboard invisibility error: {err}")

    def build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        # Scan tab
        self.scan_frame = ttk.Frame(notebook)
        notebook.add(self.scan_frame, text="Live Scans")
        self.scan_tree = ttk.Treeview(self.scan_frame, columns=("target", "tool", "time"), show="headings")
        self.scan_tree.heading("target", text="Target")
        self.scan_tree.heading("tool", text="Tool")
        self.scan_tree.heading("time", text="Timestamp")
        self.scan_tree.pack(fill="both", expand=True)

        # Sessions tab
        self.session_frame = ttk.Frame(notebook)
        notebook.add(self.session_frame, text="Sessions")
        self.session_tree = ttk.Treeview(self.session_frame, columns=("session", "tool", "time"), show="headings")
        self.session_tree.heading("session", text="Session ID")
        self.session_tree.heading("tool", text="Tool")
        self.session_tree.heading("time", text="Timestamp")
        self.session_tree.pack(fill="both", expand=True)

        # Logs tab
        self.log_frame = ttk.Frame(notebook)
        notebook.add(self.log_frame, text="Logs")
        self.log_text = tk.Text(self.log_frame, bg="#111317", fg="#cbd5e1", wrap="word")
        self.log_text.pack(fill="both", expand=True)

        # Refresh button
        refresh_btn = ttk.Button(self.root, text="Refresh Now", command=self.refresh_all)
        refresh_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    def refresh_all(self):
        self.refresh_scans()
        self.refresh_sessions()
        self.refresh_logs()

    def refresh_scans(self):
        for i in self.scan_tree.get_children():
            self.scan_tree.delete(i)
        scans = persistence.load_scans(limit=50)
        for s in scans:
            self.scan_tree.insert("", "end", values=(s["target"], s["tool"], s["timestamp"]))

    def refresh_sessions(self):
        for i in self.session_tree.get_children():
            self.session_tree.delete(i)
        sessions = persistence.load_sessions()
        for sess in sessions:
            self.session_tree.insert("", "end", values=(sess["session_id"], sess["tool"], sess["timestamp"]))

    def refresh_logs(self):
        self.log_text.delete("1.0", tk.END)
        conn = persistence._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT level, message, ts FROM logs ORDER BY ts DESC LIMIT 100")
        rows = cur.fetchall()
        conn.close()
        for level, msg, ts in rows:
            self.log_text.insert(tk.END, f"[{ts}] {level}: {msg}\n")
        self.log_text.see(tk.END)

    def auto_refresh(self):
        while not self._stop.is_set():
            self.refresh_all()
            time.sleep(self.refresh_interval)

    def start(self):
        self.root.mainloop()
        self._stop.set()

if __name__ == "__main__":
    dashboard = CyberDashboard()
    dashboard.start()
