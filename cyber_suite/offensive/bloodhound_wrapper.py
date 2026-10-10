# cyber_suite/offensive/bloodhound_wrapper.py
"""Bloodhound wrapper using the bloodhound-python library.
Provides a simple interface to collect AD data and return JSON.
"""

import json
import traceback
from typing import Dict, Any, List

try:
    from bloodhound.ad.graph import ADGraph
    from bloodhound.ad.domain import Domain
    from bloodhound.ad.utils import get_domain_controller
except Exception as e:
    raise RuntimeError("bloodhound-python library not installed. Install via `pip install bloodhound-python`.") from e


class BloodhoundWrapper:
    def __init__(self, domain: str = None, username: str = None, password: str = None, dc_ip: str = None):
        self.domain = domain
        self.username = username
        self.password = password
        self.dc_ip = dc_ip

    def _connect(self) -> ADGraph:
        # Resolve domain controller if not provided
        if not self.dc_ip:
            self.dc_ip = get_domain_controller(self.domain)
        domain = Domain(self.domain, self.username, self.password, self.dc_ip)
        return ADGraph(domain)

    def collect(self, sam_name: str = None) -> Dict[str, Any]:
        """Collect Bloodhound data for the given SAM account name (or entire domain)."""
        try:
            graph = self._connect()
            data = {}
            if sam_name:
                data = graph.get_user(sam_name)
            else:
                # Collect all objects – may be heavy, limit to basic info
                data = {"domains": graph.get_all_domains()}
            return {"success": True, "data": data}
        except Exception as exc:
            return {"success": False, "error": str(exc), "trace": traceback.format_exc()}

__all__ = ["BloodhoundWrapper"]
