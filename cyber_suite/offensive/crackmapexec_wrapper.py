# cyber_suite/offensive/crackmapexec_wrapper.py
"""CrackMapExec (CME) wrapper using the CME Python package.
Provides a thin interface to run CME modules and return JSON results.
"""

import subprocess
import json
import traceback
from typing import Dict, Any

class CrackMapExecWrapper:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run_module(self, module: str, targets: str, args: str = "", **kwargs) -> Dict[str, Any]:
        """Execute a CME module against one or more targets.
        Parameters
        ----------
        module: str
            CME module name, e.g., "smb", "mssql", "ssh".
        targets: str
            Target specification (IP, CIDR, file list).
        args: str, optional
            Additional module arguments.
        Returns
        -------
        dict
            JSON‑serialisable result containing stdout, stderr and exit code.
        """
        cmd = ["cme", module, targets]
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
                "module": module,
                "targets": targets,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "trace": traceback.format_exc(),
            }

__all__ = ["CrackMapExecWrapper"]
