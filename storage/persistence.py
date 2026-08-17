"""
QNT 持久化存储层 - 集成数据库
"""
import json
import time
import pickle
from typing import Dict, List, Optional, Any
from database import Database


class PersistenceManager:
    """持久化管理器"""
    
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()
    
    # ============ 区块链持久化 ============
    def save_block(self, block_data: Dict[str, Any]) -> bool:
        """保存区块"""
        try:
            # 保存交易
            for tx in block_data.get('transactions', []):
                self.db.add_transaction(
                    tx_hash=block_data.get('hash'),
                    sender=tx.get('sender'),
                    receiver=tx.get('receiver'),
                    amount=tx.get('amount'),
                    block_height=block_data.get('index', 0)
                )
            return True
        except Exception as e:
            print(f"❌ 保存区块失败: {e}")
            return False
    
    def save_transaction(self, tx_hash: str, sender: str, receiver: str, 
                        amount: float, block_height: int) -> bool:
        """保存交易"""
        return self.db.add_transaction(tx_hash, sender, receiver, amount, block_height)
    
    # ============ 交易所持久化 ============
    def save_order(self, order_id: str, account: str, side: str, 
                   quantity: float, price: float) -> bool:
        """保存订单"""
        return self.db.save_order(order_id, account, side, quantity, price)
    
    def update_order(self, order_id: str, status: str, filled: float = 0.0):
        """更新订单"""
        self.db.update_order_status(order_id, status, filled)
    
    def save_trade(self, trade_id: str, buy_order_id: str, sell_order_id: str,
                   quantity: float, price: float, fee: float = 0.0) -> bool:
        """保存成交"""
        return self.db.add_trade(trade_id, buy_order_id, sell_order_id, 
                                quantity, price, fee)
    
    # ============ N态持久化 ============
    def save_nstate_record(self, state_id: int, round_num: int, 
                           weights: List[float], error: float) -> bool:
        """保存N态训练记录"""
        import pickle
        weights_bytes = pickle.dumps(weights)
        return self.db.save_nstate_record(state_id, round_num, weights_bytes, error)
    
    # ============ Agent持久化 ============
    def save_agent_decision(self, agent_id: str, decision_type: str, 
                           action: str, confidence: float, 
                           parameters: Dict[str, Any]) -> bool:
        """保存Agent决策"""
        return self.db.save_agent_decision(agent_id, decision_type, 
                                          action, confidence, parameters)
    
    # ============ 查询接口 ============
    def get_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """查询地址交易"""
        return self.db.get_transactions(address, limit)
    
    def get_account_balance(self, address: str) -> float:
        """查询账户余额"""
        return self.db.get_balance(address)
    
    def get_orderbook_snapshot(self) -> Dict[str, Any]:
        """获取订单簿快照"""
        # 这里可以扩展为从数据库加载历史订单簿数据
        return {
            'timestamp': time.time(),
            'snapshot_count': 0
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        from utils.monitor import monitor
        return monitor.get_stats()


# 全局实例
persistence = PersistenceManager()
