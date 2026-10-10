# autonomous_trading/technical_analysis.py
import pandas as pd
import numpy as np
import json
from typing import Dict, Any

class TechnicalAnalyst:
    """Calculates technical indicators from OHLCV data."""
    
    def calculate_indicators(self, raw_ohlcv_json: str) -> Dict[str, Any]:
        """
        Parses raw CoinGecko OHLCV JSON and computes RSI, MACD, and SMA.
        """
        try:
            data = json.loads(raw_ohlcv_json)
            if "error" in data:
                return {"error": data["error"]}
                
            symbol = data.get("symbol", "UNKNOWN")
            ohlcv_list = data.get("ohlcv", [])
            
            if not ohlcv_list:
                return {"error": "No OHLCV data found."}
                
            # CoinGecko OHLC: [time, open, high, low, close]
            df = pd.DataFrame(ohlcv_list, columns=["time", "open", "high", "low", "close"])
            df['close'] = pd.to_numeric(df['close'])
            
            # Simple Moving Average (SMA) - 7 and 14 periods
            df['sma_7'] = df['close'].rolling(window=7, min_periods=1).mean()
            df['sma_14'] = df['close'].rolling(window=14, min_periods=1).mean()
            
            # Relative Strength Index (RSI) - 14 periods
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = loss.replace(0, np.nan)
            rs = gain / loss
            df['rsi_14'] = 100 - (100 / (1 + rs))
            df['rsi_14'] = df['rsi_14'].fillna(50) # Neutral RSI if insufficient data
            
            # MACD (12, 26, 9)
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            # Get latest values
            latest = df.iloc[-1]
            
            return {
                "symbol": symbol,
                "current_price": latest['close'],
                "sma_7": latest['sma_7'],
                "sma_14": latest['sma_14'],
                "rsi_14": latest['rsi_14'],
                "macd_line": macd.iloc[-1],
                "macd_signal": signal.iloc[-1],
                "macd_histogram": macd.iloc[-1] - signal.iloc[-1],
                "trend": "bullish" if latest['sma_7'] > latest['sma_14'] else "bearish"
            }
        except Exception as e:
            return {"error": f"Failed to compute indicators: {str(e)}"}
