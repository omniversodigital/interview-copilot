"""
Sovereign Screen-Sniffer (Vision OCR & LeetCode/Diagram Solver)
Captures active screen area upon hotkey trigger (Ctrl+Alt+S) and extracts text via EasyOCR.
Sends extracted question directly to the Co-Pilot HUD.
"""

import time
import json
import asyncio
import numpy as np
import mss
from PIL import Image
import keyboard
import websockets
import easyocr

class ScreenSniffer:
    def __init__(self, hotkey="ctrl+alt+s", langs=["en"]):
        self.hotkey = hotkey
        print(f"[+] Initializing EasyOCR for languages: {langs} ...")
        self.reader = easyocr.Reader(langs, gpu=False) # CPU / GPU fallback
        self.sct = mss.mss()
        print(f"[+] Screen Sniffer ready! Press [{self.hotkey.upper()}] to sniff and solve screen content.")

    def sniff_and_solve(self):
        print("\n[+] Capturing screen for OCR analysis...")
        try:
            # Capture main monitor
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Convert to numpy for EasyOCR
            img_np = np.array(img)
            
            print("[+] Running OCR extraction...")
            results = self.reader.readtext(img_np, detail=0)
            extracted_text = " ".join(results).strip()

            if not extracted_text:
                print("[-] No text detected on screen.")
                return

            print(f"[+] Extracted ({len(extracted_text)} chars): {extracted_text[:120]}...")
            
            # Send to Co-Pilot WebSocket
            self._dispatch_to_hud(extracted_text)
        except Exception as e:
            print(f"[-] Screen Sniff Error: {e}")

    def _dispatch_to_hud(self, text):
        async def send():
            try:
                async with websockets.connect("ws://127.0.0.1:8888/ws/transcribe") as ws:
                    await ws.send(json.dumps({
                        "action": "query",
                        "text": text
                    }))
                    print("[+] Screen text dispatched to Sovereign Co-Pilot HUD!")
            except Exception as e:
                print(f"[-] WS Dispatch Error: {e}")
        asyncio.run(send())

    def start_listening(self):
        keyboard.add_hotkey(self.hotkey, self.sniff_and_solve)
        print(f"[+] Global hotkey [{self.hotkey.upper()}] active. Press Ctrl+C to exit.")
        keyboard.wait()

if __name__ == "__main__":
    sniffer = ScreenSniffer(hotkey="ctrl+alt+s", langs=["en"])
    sniffer.start_listening()
