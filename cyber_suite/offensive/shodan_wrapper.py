# cyber_suite/offensive/shodan_wrapper.py
"""Shodan wrapper using the official shodan Python library.
Provides a simple search interface and returns raw JSON results.
"""

import os
import json
import traceback
from typing import Dict, Any

try:
    import shodan
except Exception as e:
    raise RuntimeError("Shodan library not installed. Install via `pip install shodan`.") from e

class ShodanWrapper:
    def __init__(self, api_key: str = None):
        # API key can be provided directly or via SHODAN_API_KEY env var
        self.api_key = api_key or os.getenv("SHODAN_API_KEY")
        if not self.api_key:
            raise ValueError("Shodan API key not provided. Set SHODAN_API_KEY env variable.")
        self.client = shodan.Shodan(self.api_key)

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Execute a Shodan search.
        Returns a dict with success flag and results or error information.
        """
        try:
            results = self.client.search(query, limit=limit)
            return {"success": True, "query": query, "total": results.get("total"), "matches": results.get("matches", [])}
        except Exception as exc:
            return {"success": False, "error": str(exc), "trace": traceback.format_exc()}

__all__ = ["ShodanWrapper"]
