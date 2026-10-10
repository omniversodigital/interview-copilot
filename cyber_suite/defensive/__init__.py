# Defensive Toolkit Wrappers

"""defensive/__init__.py
Provides wrappers for common defensive security tools such as nmap and
OpenVAS. The wrappers expose simple functions that can be invoked from the
FastAPI server or the HUD.
"""

import json
from typing import List, Dict, Any

# ---------- Nmap Wrapper ----------

class NmapWrapper:
    """Thin wrapper around the `python-nmap` library.
    It runs an nmap scan and returns a JSON‑serialisable dictionary of
    results.
    """
    def __init__(self):
        try:
            import nmap
            self.nm = nmap.PortScanner()
        except Exception as e:
            raise RuntimeError(f"python‑nmap import failed: {e}")

    def scan(self, target: str = "127.0.0.1", ports: str = "1-1024", arguments: str = "-sV") -> Dict[str, Any]:
        """Execute an nmap scan.
        Args:
            target: IP address or CIDR.
            ports: Port range string.
            arguments: Additional nmap arguments.
        Returns:
            Dictionary representation of scan results.
        """
        self.nm.scan(hosts=target, ports=ports, arguments=arguments)
        return self.nm.analyse_nmap_xml_scan()

# ---------- OpenVAS Wrapper (placeholder) ----------

class OpenVASWrapper:
    """Simple wrapper for OpenVAS via its REST API.
    This implementation is a placeholder; actual integration would require
    a running OpenVAS manager and proper authentication.
    """
    def __init__(self, base_url: str = "https://localhost:9392", token: str = ""):
        self.base_url = base_url.rstrip('/')
        self.token = token

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        import requests
        url = f"{self.base_url}{endpoint}"
        headers = {"X-Auth-Token": self.token, "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=data, verify=False)
        resp.raise_for_status()
        return resp.json()

    def launch_scan(self, target: str) -> Dict[str, Any]:
        """Launch a simple OpenVAS scan against `target`.
        Returns the job information returned by the API.
        """
        payload = {"target": target}
        return self._post("/scan", payload)

    def get_report(self, report_id: str) -> Dict[str, Any]:
        return self._post(f"/reports/{report_id}", {})
