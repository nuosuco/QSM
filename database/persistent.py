"""
QNT 数据持久化模块
"""
import json
import sqlite3
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class PersistentStore:
    """持久化存储管理器"""
    
    def __init__(self, db_path: str = "data/qnt.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 区块链表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index INTEGER UNIQUE,
                hash TEXT,
                previous_hash TEXT,
                timestamp REAL,
                transactions TEXT,
                nonce INTEGER,
                difficulty INTEGER
            )
        ''')
        
        # 交易表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_hash TEXT UNIQUE,
                sender TEXT,
                receiver TEXT,
                amount REAL,
                block_index INTEGER,
                timestamp REAL,
                FOREIGN KEY (block_index) REFERENCES blocks(index)
            )
        ''')
        
        # N态训练记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round INTEGER,
                state_id INTEGER,
                weights TEXT,
                reward REAL,
                timestamp REAL
            )
        ''')
        
        # 坍缩记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collapses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round INTEGER,
                merged_weights TEXT,
                best_agent TEXT,
                best_error REAL,
                timestamp REAL
            )
        ''')
        
        # 成交记录
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                order_id_1 TEXT,
                order_id_2 TEXT,
                price REAL,
                quantity REAL,
                timestamp REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_block(self, block: Dict[str, Any]):
        """保存区块"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO blocks 
            (index, hash, previous_hash, timestamp, transactions, nonce, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            block['index'],
            block['hash'],
            block['previous_hash'],
            block['timestamp'],
            json.dumps(block.get('transactions', [])),
            block.get('nonce', 0),
            block.get('difficulty', 2)
        ))
        
        conn.commit()
        conn.close()
    
    def save_transaction(self, tx: Dict[str, Any]):
        """保存交易"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO transactions
            (tx_hash, sender, receiver, amount, block_index, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            tx.get('tx_hash'),
            tx.get('sender'),
            tx.get('receiver'),
            tx.get('amount'),
            tx.get('block_index'),
            tx.get('timestamp', datetime.now().timestamp())
        ))
        
        conn.commit()
        conn.close()
    
    def save_trade(self, trade: Dict[str, Any]):
        """保存成交"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO trades
            (trade_id, order_id_1, order_id_2, price, quantity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            trade.get('trade_id'),
            trade.get('order_id_1'),
            trade.get('order_id_2'),
            trade.get('price'),
            trade.get('quantity'),
            trade.get('timestamp', datetime.now().timestamp())
        ))
        
        conn.commit()
        conn.close()
    
    def save_training_record(self, record: Dict[str, Any]):
        """保存训练记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_records
            (round, state_id, weights, reward, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            record['round'],
            record['state_id'],
            json.dumps(record['weights']),
            record['reward'],
            record.get('timestamp', datetime.now().timestamp())
        ))
        
        conn.commit()
        conn.close()
    
    def save_collapse(self, collapse: Dict[str, Any]):
        """保存坍缩记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO collapses
            (round, merged_weights, best_agent, best_error, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            collapse['round'],
            json.dumps(collapse.get('merged_weights', {})),
            collapse.get('best_agent'),
            collapse.get('best_error'),
            collapse.get('timestamp', datetime.now().timestamp())
        ))
        
        conn.commit()
        conn.close()
    
    def get_chain_info(self) -> Dict[str, Any]:
        """获取链信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM blocks')
        block_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM transactions')
        tx_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM trades')
        trade_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'blocks': block_count,
            'transactions': tx_count,
            'trades': trade_count
        }
    
    def get_history(self, limit: int = 100) -> Dict[str, List[Dict]]:
        """获取历史记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM blocks ORDER BY index DESC LIMIT ?', (limit,))
        blocks = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?', (limit,))
        transactions = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?', (limit,))
        trades = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'blocks': blocks,
            'transactions': transactions,
            'trades': trades
        }


# 全局存储实例
store = PersistentStore()
