# autonomous_trading/execution_engine.py
"""
Execution Engine Layer for the Autonomous Trading Ecosystem.
Interfaces with broker APIs to place and manage orders.
Currently implemented in paper-trading (simulation) mode for safety.
"""

import uuid
import time
from typing import Dict, Any
from autonomous_trading.database_manager import DatabaseManager

class SimulatedExecutionEngine:
    """A mock broker interface for paper trading and validation."""

    def __init__(self, initial_capital: float = 100000.0, db_path: str = "trading_state.db"):
        self.db = DatabaseManager(db_path=db_path)
        
        # Try to load state from DB
        state = self.db.load_account_state()
        if state:
            self.capital = state["capital"]
            self.positions = state["positions"]
            print(f"[Engine] Resumed state from DB. Capital: {self.capital}")
        else:
            self.capital = initial_capital
            self.positions = {}
            self.db.update_account_state(self.capital, self.positions)
            
        self.order_history = []
        self.active = True

    def get_account_summary(self) -> Dict[str, Any]:
        """Return current account balance and active positions."""
        return {
            "available_capital": self.capital,
            "open_positions": self.positions,
            "total_trades_executed": len(self.order_history)
        }

    def execute_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """Simulate execution of a validated trade order."""
        if not self.active:
            return {"status": "rejected", "reason": "Engine inactive or circuit breaker tripped."}

        order_id = str(uuid.uuid4())
        cost = quantity * price

        if side.upper() == "BUY":
            if cost > self.capital:
                return {"status": "rejected", "reason": "Insufficient capital."}
            self.capital -= cost
            self.positions[symbol] = self.positions.get(symbol, 0.0) + quantity
        elif side.upper() == "SELL":
            self.capital += cost
            self.positions[symbol] = self.positions.get(symbol, 0.0) - quantity
        else:
            return {"status": "rejected", "reason": f"Unknown side: {side}"}

        order_record = {
            "order_id": order_id,
            "timestamp": time.time(),
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "price": price,
            "cost": cost,
            "status": "filled"
        }
        
        self.order_history.append(order_record)
        
        # Persist to DB
        self.db.save_order(order_record)
        self.db.update_account_state(self.capital, self.positions)
        
        return {"status": "success", "order": order_record}

    def trigger_circuit_breaker(self, reason: str):
        """Halt all trading activity immediately."""
        self.active = False
        print(f"[CIRCUIT BREAKER] Trading halted. Reason: {reason}")
