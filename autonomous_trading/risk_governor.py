# autonomous_trading/risk_governor.py
"""
Risk Governor for the Autonomous Trading Ecosystem.
Enforces strict mathematical invariants on trade signals before execution.
Based on the Fintech Risk Governor concept (e.g., FTMO limits).
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

class RiskGovernor:
    def __init__(self, engine, max_daily_drawdown: float = 0.05, max_risk_per_trade: float = 0.02):
        """
        :param engine: The ExecutionEngine instance to monitor.
        :param max_daily_drawdown: Maximum percentage of capital allowed to be lost in a day (default 5%).
        :param max_risk_per_trade: Maximum capital percentage allocated per single trade (default 2%).
        """
        self.engine = engine
        self.max_daily_drawdown = max_daily_drawdown
        self.max_risk_per_trade = max_risk_per_trade
        self.initial_daily_capital = engine.capital

    def evaluate_trade(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        Evaluates a proposed trade against risk invariants.
        Returns {"approved": bool, "reason": str}
        """
        if not self.engine.active:
            return {"approved": False, "reason": "Execution engine is inactive (circuit breaker tripped)."}

        cost = quantity * price
        current_capital = self.engine.capital

        # 1. Max Risk Per Trade Check
        if side.upper() == "BUY":
            max_allowed_cost = current_capital * self.max_risk_per_trade
            if cost > max_allowed_cost:
                return {
                    "approved": False, 
                    "reason": f"Trade cost ({cost}) exceeds max risk per trade ({max_allowed_cost})."
                }

        # 2. Max Daily Drawdown Check (simplified for simulation based on realized capital)
        drawdown = (self.initial_daily_capital - current_capital) / self.initial_daily_capital
        if drawdown >= self.max_daily_drawdown:
            # Trip the circuit breaker if drawdown is breached
            self.engine.trigger_circuit_breaker(f"Max daily drawdown of {self.max_daily_drawdown*100}% breached.")
            return {
                "approved": False, 
                "reason": f"Max daily drawdown breached ({drawdown*100}% >= {self.max_daily_drawdown*100}%)."
            }

        return {"approved": True, "reason": "Risk parameters satisfied."}

    def compute_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Historical Value-at-Risk (VaR) for a series of portfolio returns.
        Returns the loss amount (positive number) representing the worst loss at the given confidence level.
        """
        if returns.empty:
            return 0.0
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        var = -np.percentile(returns, (1 - confidence) * 100)
        return var

    def monte_carlo_risk(self, portfolio_weights: np.ndarray, asset_returns: pd.DataFrame, iterations: int = 10000) -> Dict[str, float]:
        """Run Monte‑Carlo simulation to estimate portfolio risk metrics.
        Returns a dict with mean, std, VaR at 95% and 99%.
        """
        # Asset returns matrix (rows: scenarios, cols: assets)
        cov_matrix = asset_returns.cov().values
        mean_returns = asset_returns.mean().values
        # Generate random returns using multivariate normal distribution
        simulated = np.random.multivariate_normal(mean_returns, cov_matrix, size=iterations)
        # Portfolio returns per simulation
        portfolio_returns = simulated.dot(portfolio_weights)
        results = {
            "mean": float(np.mean(portfolio_returns)),
            "std": float(np.std(portfolio_returns)),
            "var_95": float(self.compute_var(pd.Series(portfolio_returns), confidence=0.95)),
            "var_99": float(self.compute_var(pd.Series(portfolio_returns), confidence=0.99)),
        }
        return results

    def reset_daily_metrics(self):
        """Called at the start of a new trading day to reset the drawdown baseline."""
        self.initial_daily_capital = self.engine.capital

