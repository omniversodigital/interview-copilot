"""
One-click Launcher for Sovereign Interview Co-Pilot
Launches FastAPI backend and opens distraction-free Chrome HUD window.
"""

import os
import sys
import subprocess
import time
import webbrowser

def launch():
    copilot_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(copilot_dir, "server.py")
    
    print("=" * 60)
    print("  ⚡ SOVEREIGN INTERVIEW CO-PILOT ('THE CYRANO ENGINE') ⚡")
    print("  Candidate: Jean Carlo Ferreira | Principal Systems Architect")
    print("=" * 60)
    print("  Starting FastAPI & WebSocket backend on http://127.0.0.1:8888 ...")

    # Start server in background or current process
    server_process = subprocess.Popen([sys.executable, server_script])

    # Wait for server to bind
    time.sleep(1.5)

    url = "http://127.0.0.1:8888"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if os.path.exists(chrome_path):
        print("  Launching sleek Chrome App HUD Window...")
        # App mode opens a frameless window perfect for teleprompter positioning
        subprocess.Popen([
            chrome_path,
            f"--app={url}",
            "--window-size=1100,820",
            "--window-position=100,50"
        ])
    else:
        print(f"  Opening default browser at {url} ...")
        webbrowser.open(url)

    print("\n  [STATUS] Co-Pilot is active.")
    print("  - Press [Space] or [M] in the HUD to toggle live microphone transcription.")
    print("  - Press [T] to toggle the compact Teleprompter mode under your camera.")
    print("  - Press [1-8] to quickly select specific architectural defense pillars.")
    print("\n  Press Ctrl+C to stop the server.")

    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("\n  Shutting down Sovereign Co-Pilot...")
        server_process.terminate()

if __name__ == "__main__":
    launch()
