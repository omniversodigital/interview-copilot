# cyber_suite/offensive/impacket_wrapper.py
"""Impacket wrapper providing SMB and remote execution utilities.
This lightweight wrapper offers a subset of impacket functionality required
for advanced penetration testing: SMB login validation and execution of
commands via psexec. It uses impacket's native Python APIs and returns JSON‑serializable
results.
"""

import json
import traceback
from typing import Dict, Any

# impacket imports – will raise informative error if missing
try:
    from impacket.smbconnection import SMBConnection
    from impacket.dcerpc.v5 import transport, srvs
    from impacket.dcerpc.v5.rpcrt import DCERPCException
except Exception as e:
    raise RuntimeError("Impacket library not installed. Install via `pip install impacket`." ) from e


class ImpacketWrapper:
    def __init__(self, domain: str = "", timeout: int = 30):
        self.domain = domain
        self.timeout = timeout

    def _connect(self, target: str, username: str, password: str, lmhash: str = "", nthash: str = ""):
        conn = SMBConnection(target, target, sess_port=445, timeout=self.timeout)
        conn.login(username, password, self.domain, lmhash, nthash)
        return conn

    def smb_login(self, target: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """Validate SMB credentials against a target host.
        Returns a dict with success flag and optional error message.
        """
        try:
            conn = self._connect(target, username, password)
            conn.logoff()
            return {"success": True, "target": target}
        except Exception as exc:
            return {"success": False, "error": str(exc), "trace": traceback.format_exc()}

    def psexec(self, target: str, username: str, password: str, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a command on a remote Windows host via impacket's psexec.
        Returns stdout, stderr and exit code.
        """
        try:
            from impacket.smbconnection import SessionError
            from impacket.examples.psexec import RemoteOperations, execute

            conn = self._connect(target, username, password)
            # RemoteOperations handles SMB session setup
            rop = RemoteOperations(conn, False)
            rop.enable_privilege("SeDebugPrivilege")
            output = execute(conn, rop, command)
            rop.disconnect()
            return {"output": output, "target": target}
        except Exception as exc:
            return {"success": False, "error": str(exc), "trace": traceback.format_exc()}

__all__ = ["ImpacketWrapper"]
