# autonomous_trading/data_ingest_tor.py
"""
Data Ingestion via Tor.
Fetches market data securely using the TorSession wrapper.
"""

import sys
import os
import json
import time

# Add parent directory to path to import cyber_suite
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cyber_suite.offensive.tor_i2p_wrapper import TorSession

class SecureDataFeeder:
    def __init__(self):
        # We assume Tor is already running in the background (e.g. via our extracted expert bundle)
        self.session = TorSession(launch_tor=False)
        
    def fetch_crypto_price(self, symbol: str) -> str:
        """
        Fetches current crypto price using a public API via Tor.
        Using CoinGecko's public API as an example.
        """
        # Mapping common symbols to CoinGecko IDs
        symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana"
        }
        
        coin_id = symbol_map.get(symbol.upper())
        if not coin_id:
             return json.dumps({"error": f"Unsupported symbol: {symbol}"})
             
        # Use HTTPS via Tor SOCKS proxy. CoinGecko API is public.
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true"
        
        print(f"[Tor Ingest] Fetching data for {symbol} via Tor circuit...")
        result = self.session.get(url, verify=False, timeout=30)
        
        if result.get("ok"):
            try:
                data = json.loads(result["content"])
                if coin_id in data:
                    formatted_data = {
                        "symbol": symbol,
                        "price_usd": data[coin_id]["usd"],
                        "volume_24h": data[coin_id].get("usd_24h_vol"),
                        "change_24h": data[coin_id].get("usd_24h_change"),
                        "timestamp": time.time()
                    }
                    return json.dumps(formatted_data)
                else:
                    return json.dumps({"error": "Data not found in response", "raw": result["content"]})
            except json.JSONDecodeError:
                return json.dumps({"error": "Failed to parse JSON", "raw": result["content"]})
        else:
            return json.dumps({"error": "Tor request failed", "details": result.get("error", "Unknown error")})

    def fetch_ohlcv(self, symbol: str, days: int = 1) -> str:
        """
        Fetches OHLCV candlestick data via Tor from CoinGecko.
        Returns a JSON string containing a list of [time, open, high, low, close] data points.
        """
        symbol_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana"
        }
        coin_id = symbol_map.get(symbol.upper())
        if not coin_id:
             return json.dumps({"error": f"Unsupported symbol: {symbol}"})
             
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"
        print(f"[Tor Ingest] Fetching OHLCV data for {symbol} via Tor circuit...")
        result = self.session.get(url, verify=False, timeout=30)
        
        if result.get("ok"):
            try:
                data = json.loads(result["content"])
                return json.dumps({"symbol": symbol, "ohlcv": data})
            except json.JSONDecodeError:
                return json.dumps({"error": "Failed to parse OHLCV JSON", "raw": result["content"]})
        else:
            return json.dumps({"error": "Tor request failed", "details": result.get("error", "Unknown error")})
