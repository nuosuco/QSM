"""
QNT 数据库层 - SQLite持久化
"""
import sqlite3
import json
import os
import time
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class Database:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "data/qnt.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_tables()
    
    @contextmanager
    def _connect(self):
        """连接上下文"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_tables(self):
        """初始化表"""
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # 账户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    address TEXT UNIQUE NOT NULL,
                    balance REAL DEFAULT 0.0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            
            # 交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT UNIQUE NOT NULL,
                    sender TEXT NOT NULL,
                    receiver TEXT NOT NULL,
                    amount REAL NOT NULL,
                    block_height INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # 订单表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT UNIQUE NOT NULL,
                    account TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    status TEXT DEFAULT 'open',
                    created_at REAL NOT NULL,
                    filled_quantity REAL DEFAULT 0.0
                )
            ''')
            
            # 成交记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE NOT NULL,
                    buy_order_id TEXT NOT NULL,
                    sell_order_id TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    fee REAL DEFAULT 0.0,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # N态训练记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nstate_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    state_id INTEGER NOT NULL,
                    round INTEGER NOT NULL,
                    weights BLOB NOT NULL,
                    error REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # Agent决策记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    confidence REAL DEFAULT 0.0,
                    parameters TEXT,
                    timestamp REAL NOT NULL
                )
            ''')
    
    # ============ 账户操作 ============
    def create_account(self, address: str, initial_balance: float = 0.0) -> bool:
        """创建账户"""
        now = time.time()
        with self._connect() as conn:
            try:
                conn.execute(
                    'INSERT INTO accounts (address, balance, created_at, updated_at) VALUES (?, ?, ?, ?)',
                    (address, initial_balance, now, now)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_balance(self, address: str) -> float:
        """查询余额"""
        with self._connect() as conn:
            row = conn.execute('SELECT balance FROM accounts WHERE address = ?', (address,)).fetchone()
            return row['balance'] if row else 0.0
    
    def update_balance(self, address: str, amount: float) -> bool:
        """更新余额"""
        now = time.time()
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE accounts SET balance = balance + ?, updated_at = ? WHERE address = ?', 
                          (amount, now, address))
            return cursor.rowcount > 0
    
    # ============ 交易操作 ============
    def add_transaction(self, tx_hash: str, sender: str, receiver: str, 
                       amount: float, block_height: int) -> bool:
        """添加交易记录"""
        now = time.time()
        with self._connect() as conn:
            try:
                conn.execute(
                    '''INSERT INTO transactions 
                       (tx_hash, sender, receiver, amount, block_height, timestamp, status)
                       VALUES (?, ?, ?, ?, ?, ?, 'confirmed')''',
                    (tx_hash, sender, receiver, amount, block_height, now)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """查询地址交易"""
        with self._connect() as conn:
            rows = conn.execute(
                '''SELECT * FROM transactions 
                   WHERE sender = ? OR receiver = ? 
                   ORDER BY timestamp DESC LIMIT ?''',
                (address, address, limit)
            ).fetchall()
            return [dict(r) for r in rows]
    
    # ============ 订单操作 ============
    def save_order(self, order_id: str, account: str, side: str, 
                   quantity: float, price: float) -> bool:
        """保存订单"""
        now = time.time()
        with self._connect() as conn:
            try:
                conn.execute(
                    '''INSERT INTO orders 
                       (order_id, account, side, quantity, price, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (order_id, account, side, quantity, price, now)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def update_order_status(self, order_id: str, status: str, filled: float = 0.0):
        """更新订单状态"""
        with self._connect() as conn:
            conn.execute(
                'UPDATE orders SET status = ?, filled_quantity = ? WHERE order_id = ?',
                (status, filled, order_id)
            )
    
    # ============ 成交操作 ============
    def add_trade(self, trade_id: str, buy_order_id: str, sell_order_id: str,
                  quantity: float, price: float, fee: float = 0.0) -> bool:
        """添加成交记录"""
        now = time.time()
        with self._connect() as conn:
            try:
                conn.execute(
                    '''INSERT INTO trades 
                       (trade_id, buy_order_id, sell_order_id, quantity, price, fee, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (trade_id, buy_order_id, sell_order_id, quantity, price, fee, now)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    # ============ N态操作 ============
    def save_nstate_record(self, state_id: int, round_num: int, 
                           weights: bytes, error: float) -> bool:
        """保存N态训练记录"""
        now = time.time()
        with self._connect() as conn:
            try:
                conn.execute(
                    '''INSERT INTO nstate_history 
                       (state_id, round, weights, error, timestamp)
                       VALUES (?, ?, ?, ?, ?)''',
                    (state_id, round_num, weights, error, now)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    # ============ Agent操作 ============
    def save_agent_decision(self, agent_id: str, decision_type: str, 
                           action: str, confidence: float, parameters: Dict) -> bool:
        """保存Agent决策"""
        now = time.time()
        with self._connect() as conn:
            try:
                conn.execute(
                    '''INSERT INTO agent_decisions 
                       (agent_id, decision_type, action, confidence, parameters, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (agent_id, decision_type, action, confidence, 
                     json.dumps(parameters), now)
                )
                return True
            except sqlite3.IntegrityError:
                return False


# 全局数据库实例
db = Database()
