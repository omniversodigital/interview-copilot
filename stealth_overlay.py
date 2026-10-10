"""
Sovereign Invisible Ghost Overlay
Native Tkinter Heads-Up Display with WDA_EXCLUDEFROMCAPTURE.
100% physically invisible to Zoom, Google Meet, Microsoft Teams, Slack, and Discord screen sharing.
"""

import tkinter as tk
from tkinter import ttk
import ctypes
from ctypes import wintypes
import json
import threading
import time
import subprocess
import sys
import os
import websockets
import asyncio

# Windows API Constants
WDA_EXCLUDEFROMCAPTURE = 0x00000011
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

class StealthOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sovereign Ghost HUD")
        
        # Window setup: 850x320 at top of screen
        screen_w = self.root.winfo_screenwidth()
        win_w = 880
        win_h = 320
        pos_x = (screen_w - win_w) // 2
        pos_y = 25

        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.93)
        self.root.configure(bg="#07090e")
        self.root.overrideredirect(True) # borderless frameless window

        # Draggable state
        self._drag_x = 0
        self._drag_y = 0

        self.build_ui()
        self.apply_invisibility()

        # WebSocket communication thread
        self.running = True
        self.ws_thread = threading.Thread(target=self.run_ws_client, daemon=True)
        self.ws_thread.start()

    def build_ui(self):
        # Header / Drag Bar
        drag_bar = tk.Frame(self.root, bg="#0e1422", height=28)
        drag_bar.pack(fill="x", side="top")
        drag_bar.bind("<Button-1>", self.start_drag)
        drag_bar.bind("<B1-Motion>", self.do_drag)

        title_lbl = tk.Label(
            drag_bar, 
            text="⚡ SOVEREIGN GHOST HUD  [CLOAKED: INVISIBLE TO ZOOM / TEAMS]",
            font=("Segoe UI", 8, "bold"),
            fg="#00f2fe",
            bg="#0e1422"
        )
        title_lbl.pack(side="left", padx=10)

        self.status_lbl = tk.Label(
            drag_bar,
            text="● WAITING FOR AUDIO",
            font=("Segoe UI", 8, "bold"),
            fg="#10b981",
            bg="#0e1422"
        )
        self.status_lbl.pack(side="left", padx=10)

        close_btn = tk.Label(
            drag_bar,
            text="✕",
            font=("Segoe UI", 9, "bold"),
            fg="#ef4444",
            bg="#0e1422",
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=10)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        # Main Container
        content_frame = tk.Frame(self.root, bg="#07090e", padx=14, pady=8)
        content_frame.pack(fill="both", expand=True)

        # ⚡ 1-Second Opening Hook
        hook_hdr = tk.Label(
            content_frame,
            text="⚡ 1-SECOND OPENING HOOK (SAY THIS FIRST):",
            font=("Segoe UI", 9, "bold"),
            fg="#00f2fe",
            bg="#07090e"
        )
        hook_hdr.pack(anchor="w")

        self.hook_text = tk.Label(
            content_frame,
            text="Listening for interviewer speech stream... Sub-second response will appear here.",
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff",
            bg="#0c1322",
            padx=10,
            pady=6,
            wraplength=840,
            justify="left"
        )
        self.hook_text.pack(fill="x", pady=(2, 8))

        # 🏛 Core Architecture Pillars
        arch_hdr = tk.Label(
            content_frame,
            text="🏛 ARCHITECTURAL MECHANISMS & POINTS:",
            font=("Segoe UI", 8, "bold"),
            fg="#00f2fe",
            bg="#07090e"
        )
        arch_hdr.pack(anchor="w")

        self.arch_text = tk.Label(
            content_frame,
            text="• Ready for live evaluation\n• Zero-network-hop local policy sidecars\n• Sub-millisecond synchronous risk governors",
            font=("Segoe UI", 10),
            fg="#e2e8f0",
            bg="#07090e",
            wraplength=840,
            justify="left"
        )
        self.arch_text.pack(anchor="w", pady=(0, 6))

        # Bottom Bar: Metrics & Counter-Question
        bottom_frame = tk.Frame(content_frame, bg="#07090e")
        bottom_frame.pack(fill="x", side="bottom")

        self.metrics_lbl = tk.Label(
            bottom_frame,
            text="📊 METRICS: 19.9 µs/op | >50k evals/sec | 100% FTMO 5% drawdown compliance",
            font=("Segoe UI", 9, "bold"),
            fg="#10b981",
            bg="#07090e"
        )
        self.metrics_lbl.pack(side="left")

        self.counter_lbl = tk.Label(
            bottom_frame,
            text="🎯 COUNTER-Q: \"How does your team handle partition tolerance?\"",
            font=("Segoe UI", 9, "italic"),
            fg="#a855f7",
            bg="#07090e"
        )
        self.counter_lbl.pack(side="right")
        # Cyber Suite button
        self.cyber_btn = ttk.Button(self.root, text="Cyber Suite", command=self.launch_dashboard)
        self.cyber_btn.place(relx=0.5, rely=0.0, anchor="n", y=5)

    def start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_x)
        y = self.root.winfo_y() + (event.y - self._drag_y)
        self.root.geometry(f"+{x}+{y}")
        # Bind hotkey for dashboard
        self.root.bind_all("<Control-Alt-h>", lambda e: self.launch_dashboard())

    def apply_invisibility(self):
        self.root.update_idletasks()
        hwnd = user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
        res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
        if res:
            print(f"[+] Ghost HUD: WDA_EXCLUDEFROMCAPTURE applied to HWND {hwnd} (Invisible to Screen Share)")
        else:
            err = ctypes.get_last_error()
            print(f"[-] Ghost HUD Error: {err}")
        # Prepare dashboard launch command path
        self._dashboard_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cyber_suite", "dashboard", "hud.py"))
        
    def launch_dashboard(self):
        """Spawn the Cyber Suite dashboard as a separate process."""
        try:
            subprocess.Popen([sys.executable, self._dashboard_path], creationflags=subprocess.CREATE_NO_WINDOW)
            print("[+] Launched Cyber Suite Dashboard")
        except Exception as e:
            print(f"[!] Failed to launch dashboard: {e}")

    def update_hud(self, data):
        topic = data.get("topic", {})
        hook = topic.get("opening_hook", "")
        pts = topic.get("architecture_points", [])
        metrics = topic.get("metrics", [])
        counter = topic.get("counter_question", "")

        self.hook_text.config(text=hook or "Deliver confident direct opening thesis.")
        self.arch_text.config(text="\n".join([f"• {p}" for p in pts[:3]]))
        if metrics:
            self.metrics_lbl.config(text=f"📊 METRICS: {' | '.join(metrics[:2])}")
        if counter:
            self.counter_lbl.config(text=f"🎯 COUNTER-Q: \"{counter[:55]}...\"")
        self.status_lbl.config(text=f"● LIVE MATCH: {topic.get('title', '')[:30]}")

    def run_ws_client(self):
        async def client_loop():
            uri = "ws://127.0.0.1:8888/ws/transcribe"
            while self.running:
                try:
                    async with websockets.connect(uri) as ws:
                        while self.running:
                            msg = await ws.recv()
                            payload = json.loads(msg)
                            if payload.get("type") == "result":
                                data = payload.get("data", {})
                                self.root.after(0, self.update_hud, data)
                except Exception:
                    await asyncio.sleep(2)
        asyncio.run(client_loop())

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StealthOverlay()
    app.start()
