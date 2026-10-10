# cyber_suite/offensive/metasploit_rpc.py
"""Minimal Metasploit RPC client wrapper.
For demonstration it connects to a locally running Metasploit RPC server (default port 55553).
If the server is not available, it returns a mock response.
All results are persisted via `cyber_suite.persistence.save_session`.
"""

import json
import socket
from typing import Any, Dict

from .. import persistence

class MetasploitRPC:
    def __init__(self, host: str = "127.0.0.1", port: int = 55553, token: str = ""):
        self.host = host
        self.port = port
        self.token = token
        self.sock = None
        self._connect()

    def _connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=3)
        except Exception as e:
            self.sock = None
            persistence.log_event("warning", f"Metasploit RPC not reachable: {e}")

    def _call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if not self.sock:
            return {"error": "Metasploit RPC not connected"}
        request = {"method": method, "params": params, "token": self.token}
        try:
            self.sock.sendall((json.dumps(request) + "\n").encode())
            resp = self.sock.recv(65536).decode().strip()
            data = json.loads(resp)
            return data
        except Exception as e:
            return {"error": str(e)}

    def execute_module(self, **params) -> Dict[str, Any]:
        """Execute a Metasploit module. Expects params like `module_name`, `payload`, `rhost` etc.
        Returns the raw response and persists it as a session.
        """
        result = self._call("module.execute", params)
        session_id = result.get("session", "unknown")
        persistence.save_session(session_id, "metasploit", result)
        return result

    def list_sessions(self) -> Dict[str, Any]:
        result = self._call("session.list", {})
        # Persist each session record
        for sid, info in result.get("sessions", {}).items():
            persistence.save_session(sid, "metasploit", info)
        return result
