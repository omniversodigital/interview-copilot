# cyber_suite/offensive/netexec_wrapper.py
"""NetExec wrapper providing remote command execution via NetExec library.
Implements a thin Python API around the `netexec` CLI for quick integration.
"""

import subprocess
import traceback
from typing import Dict, Any

class NetExecWrapper:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def exec_module(self, target: str, module: str, args: str = "", **kwargs) -> Dict[str, Any]:
        """Execute a NetExec module against a target.
        Parameters
        ----------
        target: str
            IP address or hostname of the target.
        module: str
            NetExec module name (e.g., "smbexec", "ssh", "rdp").
        args: str, optional
            Additional arguments passed to the module.
        Returns
        -------
        dict
            JSON‑serialisable result containing stdout, stderr and exit code.
        """
        cmd = ["netexec", module, "-t", target]
        if args:
            cmd.extend(args.split())
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            return {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
                "target": target,
                "module": module,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "trace": traceback.format_exc(),
            }

__all__ = ["NetExecWrapper"]
