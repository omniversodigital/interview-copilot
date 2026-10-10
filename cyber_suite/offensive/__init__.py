# Offensive Toolkit Wrappers
"""Expose offensive tool wrappers for the Cyber Suite.
Only imports are provided here; the actual implementations live in the
sub‑modules within this package.
"""

from .metasploit_rpc import MetasploitRPC
from .scapy_wrapper import ScapyWrapper
from .empire_wrapper import EmpireWrapper
