"""
Sovereign WASAPI Loopback Audio Listener
Intercepts digital PCM audio from system output (speakers/headphones) using PyAudioWPatch.
Zero room noise, zero mic bleed, pure digital interviewer voice sniffer.
"""

import sys
import time
import json
import io
import wave
import threading
import asyncio
import websockets
import pyaudiowpatch as pyaudio
import speech_recognition as sr

CHUNK_SIZE = 1024
SAMPLE_RATE = 48000 # Typical WASAPI output rate
SILENCE_THRESHOLD = 500
SILENCE_LIMIT_SEC = 1.0

class LoopbackListener:
    def __init__(self, language="en-US"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.p = pyaudio.PyAudio()
        self.loopback_device = self._find_loopback_device()
        self.running = True

    def _find_loopback_device(self):
        wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        
        # Look for the matching loopback device
        for loopback in self.p.get_loopback_device_info_generator():
            if default_speakers["name"] in loopback["name"]:
                print(f"[+] Found WASAPI Loopback Device: {loopback['name']} (Index {loopback['index']})")
                return loopback

        # Fallback to first loopback
        for loopback in self.p.get_loopback_device_info_generator():
            print(f"[!] Using Fallback Loopback: {loopback['name']} (Index {loopback['index']})")
            return loopback

        raise RuntimeError("No WASAPI Loopback device found on this system!")

    def send_to_copilot(self, text):
        async def send():
            try:
                async with websockets.connect("ws://127.0.0.1:8888/ws/transcribe") as ws:
                    await ws.send(json.dumps({
                        "action": "speech",
                        "text": text,
                        "is_final": True
                    }))
                    print(f"[+] Sent to Co-Pilot HUD: '{text}'")
            except Exception as e:
                print(f"[-] WS Send Error: {e}")
        asyncio.run(send())

    def start_listening(self):
        channels = self.loopback_device["maxInputChannels"]
        rate = int(self.loopback_device["defaultSampleRate"])

        print(f"[+] Listening to digital audio at {rate}Hz ({channels} channels)...")
        print("[+] Ready to intercept interviewer speech.")

        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=self.loopback_device["index"],
            frames_per_buffer=CHUNK_SIZE
        )

        audio_buffer = []
        silence_frames = 0
        has_speech = False

        while self.running:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                # Compute simple RMS energy
                # Unpack 16-bit PCM
                import audioop
                rms = audioop.rms(data, 2)

                if rms > SILENCE_THRESHOLD:
                    has_speech = True
                    silence_frames = 0
                    audio_buffer.append(data)
                elif has_speech:
                    audio_buffer.append(data)
                    silence_frames += 1
                    # If silence duration reached, transcribe buffer
                    if (silence_frames * CHUNK_SIZE / rate) > SILENCE_LIMIT_SEC:
                        raw_data = b"".join(audio_buffer)
                        audio_buffer = []
                        has_speech = False
                        silence_frames = 0
                        
                        # Process speech in separate thread
                        threading.Thread(
                            target=self._transcribe_and_dispatch,
                            args=(raw_data, rate, channels),
                            daemon=True
                        ).start()
            except Exception as e:
                print(f"[-] Stream read error: {e}")
                time.sleep(0.1)

        stream.stop_stream()
        stream.close()
        self.p.terminate()

    def _transcribe_and_dispatch(self, raw_pcm, rate, channels):
        try:
            # Downmix to mono if stereo
            import audioop
            if channels == 2:
                raw_pcm = audioop.tomono(raw_pcm, 2, 0.5, 0.5)

            audio_data = sr.AudioData(raw_pcm, rate, 2)
            # Transcribe
            text = self.recognizer.recognize_google(audio_data, language=self.language)
            print(f"[INTERVIEWER]: {text}")
            self.send_to_copilot(text)
        except sr.UnknownValueError:
            pass # Unintelligible sound or music
        except Exception as e:
            print(f"[-] Transcription error: {e}")

if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "en-US"
    listener = LoopbackListener(language=lang)
    try:
        listener.start_listening()
    except KeyboardInterrupt:
        print("\nStopping Loopback Listener...")
