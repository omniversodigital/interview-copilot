"""
Sovereign In-Ear Whisper Prompter
Asynchronously speaks the 1-second opening hook and key metrics directly into your private audio device (e.g. Bluetooth earbud).
Uses native Windows SAPI.SpVoice with SVSFlagsAsync (0ms latency, non-blocking).
"""

import sys
import json
import time
import threading
import asyncio
import websockets
import win32com.client

class InEarPrompter:
    def __init__(self, rate=1, volume=85):
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self.speaker.Rate = rate # Slightly faster speech for quick prompts
        self.speaker.Volume = volume
        self.running = True
        self.last_spoken_hook = ""

    def speak_async(self, text: str):
        # 1 = SVSFlagsAsync (does not block execution)
        # 2 = SVSFPurgeBeforeSpeak (stops prior speech immediately if new question arrives)
        flags = 1 | 2
        try:
            self.speaker.Speak(text, flags)
            print(f"[WHISPER IN-EAR]: {text}")
        except Exception as e:
            print(f"[-] SAPI Speak Error: {e}")

    def run_listener(self):
        async def listen_loop():
            uri = "ws://127.0.0.1:8888/ws/transcribe"
            while self.running:
                try:
                    async with websockets.connect(uri) as ws:
                        print("[+] In-Ear Prompter connected to Sovereign Co-Pilot.")
                        while self.running:
                            msg = await ws.recv()
                            payload = json.loads(msg)
                            if payload.get("type") == "result":
                                data = payload.get("data", {})
                                topic = data.get("topic", {})
                                hook = topic.get("opening_hook", "")
                                if hook and hook != self.last_spoken_hook:
                                    self.last_spoken_hook = hook
                                    # Speak the hook into your ear
                                    self.speak_async(hook)
                except Exception:
                    await asyncio.sleep(2)
        asyncio.run(listen_loop())

if __name__ == "__main__":
    prompter = InEarPrompter()
    print("[+] Sovereign In-Ear Whisper Prompter active. Listening to Co-Pilot...")
    try:
        prompter.run_listener()
    except KeyboardInterrupt:
        print("\nStopping In-Ear Prompter...")
