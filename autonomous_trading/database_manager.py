# autonomous_trading/database_manager.py
import sqlite3
import json
import os
from typing import Dict, Any, List

class DatabaseManager:
    """Manages SQLite state persistence for the trading ecosystem."""
    
    def __init__(self, db_path: str = "trading_state.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                timestamp REAL,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                price REAL,
                cost REAL,
                status TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                capital REAL,
                positions TEXT
            )
        ''')
        self.conn.commit()
        
    def save_order(self, order: Dict[str, Any]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO orders (order_id, timestamp, symbol, side, quantity, price, cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order['order_id'], order['timestamp'], order['symbol'], 
            order['side'], order['quantity'], order['price'], 
            order['cost'], order['status']
        ))
        self.conn.commit()
        
    def update_account_state(self, capital: float, positions: Dict[str, float]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO account_state (id, capital, positions)
            VALUES (1, ?, ?)
        ''', (capital, json.dumps(positions)))
        self.conn.commit()
        
    def load_account_state(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT capital, positions FROM account_state WHERE id = 1')
        row = cursor.fetchone()
        if row:
            return {
                "capital": row['capital'],
                "positions": json.loads(row['positions'])
            }
        return None
        
    def close(self):
        self.conn.close()
