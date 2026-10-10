# cyber_suite/defensive/openvas_wrapper.py
"""OpenVAS / Greenbone Vulnerability Management wrapper.
Uses the official `python-gvm` library to communicate with a local GVM daemon.
Only a subset of functionality is exposed for the Cyber Suite:
- authenticate (once per instance)
- launch a scan against a target host/network
- fetch a report by its ID
- list recent tasks

Configuration:
- `host` defaults to "127.0.0.1" and `port` defaults to 9390 (GVM daemon).
- `username`/`password` should be set via environment variables or passed in.
"""

import os
from typing import Dict, Any, List

# Lazy import – will raise informative error if python-gvm is missing.
try:
    from gvm.connections import UnixSocketConnection, TcpSocketConnection
    from gvm.protocols.gmp import Gmp
    _GVM_AVAILABLE = True
except Exception:
    _GVM_AVAILABLE = False


class OpenVASWrapper:
    def __init__(self, host: str = "127.0.0.1", port: int = 9390, username: str = None, password: str = None):
        if not _GVM_AVAILABLE:
            raise RuntimeError("python-gvm library is not installed. Install with `pip install python-gvm`.")
        self.host = host
        self.port = port
        self.username = username or os.getenv("GVM_USER")
        self.password = password or os.getenv("GVM_PASS")
        if not self.username or not self.password:
            raise RuntimeError("GVM credentials not provided via args or GVM_USER/GVM_PASS env vars.")
        # Prefer Unix socket if available, otherwise TCP.
        socket_path = os.getenv("GVM_SOCKET")
        if socket_path and os.path.exists(socket_path):
            self.conn = UnixSocketConnection(path=socket_path)
        else:
            self.conn = TcpSocketConnection(host=self.host, port=self.port)
        # Establish GMP session.
        self.gmp = Gmp(connection=self.conn)
        self.gmp.authenticate(self.username, self.password)

    # ----------------------- Helper utilities -----------------------
    def _to_dict(self, gmp_obj) -> Dict[str, Any]:
        """Convert python-gvm response objects (XML-derived) to plain dicts.
        Very lightweight – only extracts attributes and text for common objects.
        """
        result = {}
        for elem in gmp_obj:
            tag = elem.tag.split('}')[-1]  # strip namespace
            if len(elem):
                result[tag] = self._to_dict(elem)
            else:
                result[tag] = elem.text
        return result

    # ----------------------- Public API -----------------------
    def launch_scan(self, target: str) -> Dict[str, Any]:
        """Create a target, a task and start a scan.
        Returns the task information dictionary.
        """
        # Create a target
        target_id = self.gmp.create_target(name=f"auto-{target}", hosts=[target])
        # Create a task using the default scan config ("Full and fast")
        task_id = self.gmp.create_task(name=f"scan-{target}", config_id="daba56c8-73ec-11df-a475-002264764cea", target_id=target_id)
        # Start the task
        self.gmp.start_task(task_id)
        return {"task_id": task_id, "target_id": target_id, "status": "started"}

    def get_report(self, task_id: str) -> Dict[str, Any]:
        """Retrieve the most recent report for a given task.
        Returns a dict with report XML parsed into primitive types.
        """
        # Find the latest report for the task
        reports = self.gmp.get_reports(task_id=task_id, details=True)
        # `reports` is a generator of XML elements; we take the first.
        report = next(reports, None)
        if not report:
            return {"error": "No report available for task"}
        # Convert to dict for JSON serialisation
        return self._to_dict(report)

    def list_tasks(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Return a short list of recent tasks with their status.
        """
        tasks_xml = self.gmp.get_tasks()
        tasks = []
        count = 0
        for t in tasks_xml:
            if count >= max_results:
                break
            tasks.append(self._to_dict(t))
            count += 1
        return tasks

# Export class for package import
__all__ = ["OpenVASWrapper"]
