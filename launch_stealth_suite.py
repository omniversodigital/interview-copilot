"""
Sovereign Stealth Interview Defense Suite Launcher
Orchestrates:
1. FastAPI & WebSocket Engine (server.py)
2. Ghost HUD Overlay with WDA_EXCLUDEFROMCAPTURE (stealth_overlay.py)
3. WASAPI Loopback Audio Listener (loopback_listener.py)
"""

import os
import sys
import subprocess
import time

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 65)
    print("  ⚡ SOVEREIGN STEALTH GHOST SUITE (CLOAKED & UNDETECTABLE) ⚡")
    print("  Candidate: Jean Carlo Ferreira | Principal Systems Architect")
    print("=" * 65)
    print("  [1/3] Launching Core Telemetry Engine (server.py)...")
    
    server_proc = subprocess.Popen([sys.executable, os.path.join(script_dir, "server.py")])
    time.sleep(1.5)

    print("  [2/3] Launching WASAPI Loopback Audio Interceptor...")
    loopback_proc = subprocess.Popen([sys.executable, os.path.join(script_dir, "loopback_listener.py")])
    time.sleep(1.0)

    print("  [3/3] Launching Ghost HUD Overlay (Invisible to Screen Share)...")
    print("\n  🛡️ STEALTH STATUS: ACTIVE")
    print("  - The HUD window is rendered on your screen but 100% INVISIBLE to Zoom/Meet.")
    print("  - Digital audio from your headphones is automatically transcribed.")
    print("  - To solve screen content / LeetCode, run screen_sniffer.py (Ctrl+Alt+S).")
    print("  - Close the Ghost HUD window to terminate the suite.\n")

    overlay_proc = subprocess.Popen([sys.executable, os.path.join(script_dir, "stealth_overlay.py")])

    try:
        overlay_proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  Shutting down Sovereign Stealth Suite...")
        for p in [overlay_proc, loopback_proc, server_proc]:
            try:
                p.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    main()
