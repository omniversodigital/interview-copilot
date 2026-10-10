# autonomous_trading/trade_loop.py
"""
Asynchronous Main Trading Loop.
Wires together Data Ingestion (Tor), Technical Analysis, Intelligence Mesh, Risk Governor, and Execution Engine.
"""

import sys
import asyncio
import json
import os

from data_ingest_tor import SecureDataFeeder
from technical_analysis import TechnicalAnalyst
from intelligence_mesh import SwarmOrchestrator
from risk_governor import RiskGovernor
from execution_engine import SimulatedExecutionEngine

async def process_asset(symbol: str, feeder: SecureDataFeeder, ta: TechnicalAnalyst, swarm: SwarmOrchestrator, risk_gov: RiskGovernor, engine: SimulatedExecutionEngine):
    print(f"\n--- Processing {symbol} ---")
    
    # 1. Ingest Data securely via Tor
    # Using asyncio.to_thread because feeder.fetch_ohlcv is synchronous and blocking
    raw_ohlcv = await asyncio.to_thread(feeder.fetch_ohlcv, symbol, days=1)
    if "error" in raw_ohlcv:
        print(f"Data Fetch Error for {symbol}: {raw_ohlcv}")
        return
        
    # 2. Technical Analysis
    ta_results = await asyncio.to_thread(ta.calculate_indicators, raw_ohlcv)
    if "error" in ta_results:
        print(f"TA Error for {symbol}: {ta_results}")
        return
        
    print(f"[{symbol}] TA Computed: Price=${ta_results.get('current_price', 0):.2f}, RSI={ta_results.get('rsi_14', 0):.2f}, Trend={ta_results.get('trend', 'unknown')}")
    
    # 3. Intelligence Swarm Analysis & Decision
    # Process market tick using the new TA results
    signal = await asyncio.to_thread(swarm.process_market_tick, symbol, json.dumps(ta_results))
    
    action = signal.get("action", "HOLD")
    reasoning = signal.get("reasoning", "No reasoning provided")
    print(f"[{symbol}] Swarm Decision: {action} (Reason: {reasoning})")
    
    if action in ["BUY", "SELL"]:
        trade_value_usd = 1000.0
        
        try:
            price = ta_results["current_price"]
            quantity = trade_value_usd / price
        except Exception as e:
            print(f"Error calculating quantity for {symbol}: {e}")
            return
        
        print(f"[{symbol}] Requesting execution: {action} {quantity:.4f} {symbol} @ ${price:.2f}")
        
        # 4. Risk Governor Evaluation
        # Wrapping risk evaluation and execution in a lock-like sequential wrapper is safer, 
        # but for simulation we just run it directly.
        risk_eval = risk_gov.evaluate_trade(symbol, action, quantity, price)
        
        if risk_eval["approved"]:
            print(f"[{symbol}] Risk Governor: APPROVED. Proceeding to execution.")
            # 5. Execution
            result = engine.execute_order(symbol, action, quantity, price)
            print(f"[{symbol}] Execution Result: {json.dumps(result)}")
        else:
            print(f"[{symbol}] Risk Governor: REJECTED - {risk_eval['reason']}")


async def main_loop():
    print("Initializing Asynchronous Autonomous Trading Ecosystem...")
    print("[1/5] Starting Simulated Execution Engine with DB Persistence")
    engine = SimulatedExecutionEngine(initial_capital=100000.0)
    
    print("[2/5] Initializing Risk Governor")
    risk_gov = RiskGovernor(engine, max_daily_drawdown=0.05, max_risk_per_trade=0.02)
    
    print("[3/5] Initializing Tor Data Feeder")
    try:
        feeder = SecureDataFeeder()
    except Exception as e:
        print(f"Error initializing Tor Feeder: {e}")
        return
        
    print("[4/5] Initializing Technical Analyst")
    ta = TechnicalAnalyst()
        
    print("[5/5] Initializing Intelligence Swarm (OpenRouter API)")
    swarm = SwarmOrchestrator()
    
    symbols = ["BTC", "ETH", "SOL"]
    
    print("\nStarting Main Trade Loop (Simulation Mode)...")
    while True:
        # Run asset processing concurrently
        tasks = [process_asset(sym, feeder, ta, swarm, risk_gov, engine) for sym in symbols]
        await asyncio.gather(*tasks)
        
        print(f"\nAccount Summary: {json.dumps(engine.get_account_summary())}")
        print("\nSleeping for 60 seconds before next tick...")
        await asyncio.sleep(60)

def run_loop():
    asyncio.run(main_loop())

if __name__ == "__main__":
    run_loop()
