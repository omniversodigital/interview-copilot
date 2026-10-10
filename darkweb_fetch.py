# darkweb_fetch.py
"""Fetch a hidden service via Tor using the TorSession wrapper.
The script launches a Tor process (if none is running) and performs a GET request.
Result is printed as JSON for easy inspection.
"""
import json
from cyber_suite.offensive.tor_i2p_wrapper import TorSession


def main():
    # launch Tor in background if needed
    sess = TorSession(launch_tor=False)
    # Example .onion site (check.torproject.org style service)
    url = "http://duskgytldkxiuqc6.onion"
    import time
    time.sleep(5)
    result = sess.get(url, verify=False, timeout=60)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
