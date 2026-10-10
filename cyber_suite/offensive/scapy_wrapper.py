# cyber_suite/offensive/scapy_wrapper.py
"""Lightweight Scapy wrapper for basic network operations.
Provides ARP scan as an example. For full Scapy usage, import directly.
"""

import json
from typing import List, Dict, Any

from .. import persistence

class ScapyWrapper:
    """Simple Scapy utilities.
    Currently implements an ARP ping sweep.
    """
    def __init__(self):
        try:
            from scapy.all import ARP, Ether, srp
            self.ARP = ARP
            self.Ether = Ether
            self.srp = srp
        except Exception as e:
            raise RuntimeError(f"Scapy import failed: {e}")

    def arp_scan(self, network: str = "192.168.1.0/24", timeout: int = 2) -> Dict[str, Any]:
        """Perform an ARP scan on the given network.
        Returns a dict with list of live hosts.
        """
        arp = self.ARP(pdst=network)
        ether = self.Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        answered, _ = self.srp(packet, timeout=timeout, verbose=False)
        hosts = []
        for sent, received in answered:
            hosts.append({"ip": received.psrc, "mac": received.hwsrc})
        result = {"hosts": hosts, "network": network}
        persistence.save_session("scapy_arp", "scapy", result)
        return result
