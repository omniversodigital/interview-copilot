# cyber_suite/offensive/tor_i2p_wrapper.py
"""Wrapper for routing HTTP requests through Tor or I2P networks.
Provides simple GET/POST helpers using `requests` with SOCKS5 (Tor) or I2P
HTTP proxy. Relies on `stem` for optional Tor launch and `i2p` package for
I2P proxy configuration.
"""

import os
import threading
import traceback
from typing import Dict, Any

import requests
from stem import Signal
from stem.control import Controller

# Default proxy ports – adjust if your Tor/I2P services listen elsewhere
TOR_SOCKS_HOST = "127.0.0.1"
TOR_SOCKS_PORT = 9050
I2P_HTTP_HOST = "127.0.0.1"
I2P_HTTP_PORT = 4444

class TorSession:
    """Session that routes traffic through Tor's SOCKS5 proxy.
    Optionally can start a Tor process if none is running.
    """

    def __init__(self, proxy_host: str = TOR_SOCKS_HOST, proxy_port: int = TOR_SOCKS_PORT, launch_tor: bool = False):
        self.proxy = f"socks5h://{proxy_host}:{proxy_port}"
        self.session = requests.Session()
        self.session.proxies.update({"http": self.proxy, "https": self.proxy})
        self._controller = None
        if launch_tor:
            self._start_tor()

    def _start_tor(self):
        """Launch a Tor process in a background thread using stem.
        This is a minimal launch; for production you may want a full configuration.
        """
        from stem.process import launch_tor_with_config
        def _run():
            try:
                launch_tor_with_config(config={"SocksPort": str(TOR_SOCKS_PORT)})
            except Exception as e:
                print(f"[Tor] launch failed: {e}")
        threading.Thread(target=_run, daemon=True).start()
        # wait briefly for Tor to start
        import time
        time.sleep(5)
        try:
            self._controller = Controller.from_port(port=9051)
            self._controller.authenticate()
        except Exception as e:
            print(f"[Tor] controller connect failed: {e}")

    def new_identity(self):
        """Signal Tor for a new circuit (new IP)."""
        if self._controller:
            self._controller.signal(Signal.NEWNYM)

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        try:
            # Use provided timeout if specified, otherwise default to 30 seconds
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            resp = self.session.get(url, **kwargs)
            return {"status": resp.status_code, "content": resp.text, "ok": resp.ok}
        except Exception as exc:
            return {"error": str(exc), "trace": traceback.format_exc()}

    def post(self, url: str, data=None, json=None, **kwargs) -> Dict[str, Any]:
        try:
            # Use provided timeout if specified, otherwise default to 30 seconds
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            resp = self.session.post(url, data=data, json=json, **kwargs)
            return {"status": resp.status_code, "content": resp.text, "ok": resp.ok}
        except Exception as exc:
            return {"error": str(exc), "trace": traceback.format_exc()}

class I2PSession:
    """Session that routes traffic through an I2P HTTP proxy.
    Assumes an I2P router is running locally and exposing an HTTP proxy.
    """

    def __init__(self, proxy_host: str = I2P_HTTP_HOST, proxy_port: int = I2P_HTTP_PORT):
        self.proxy = f"http://{proxy_host}:{proxy_port}"
        self.session = requests.Session()
        self.session.proxies.update({"http": self.proxy, "https": self.proxy})

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        try:
            resp = self.session.get(url, timeout=60, **kwargs)
            return {"status": resp.status_code, "content": resp.text, "ok": resp.ok}
        except Exception as exc:
            return {"error": str(exc), "trace": traceback.format_exc()}

    def post(self, url: str, data=None, json=None, **kwargs) -> Dict[str, Any]:
        try:
            resp = self.session.post(url, data=data, json=json, timeout=60, **kwargs)
            return {"status": resp.status_code, "content": resp.text, "ok": resp.ok}
        except Exception as exc:
            return {"error": str(exc), "trace": traceback.format_exc()}

__all__ = ["TorSession", "I2PSession"]
