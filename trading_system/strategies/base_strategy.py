"""
策略基类
所有交易策略继承此类
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        self.is_running = False
        self.trades = []
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'max_drawdown': 0.0
        }
    
    @abstractmethod
    def generate_signal(self, data: Dict) -> Optional[Dict]:
        """
        生成交易信号
        返回: {'action': 'buy'/'sell'/'hold', 'price': float, 'quantity': int, 'reason': str}
        """
        pass
    
    @abstractmethod
    def get_stop_loss(self, entry_price: float) -> float:
        """获取止损价格"""
        pass
    
    @abstractmethod
    def get_take_profit(self, entry_price: float) -> float:
        """获取止盈价格"""
        pass
    
    @abstractmethod
    def get_position_size(self, capital: float, entry_price: float) -> int:
        """计算仓位大小"""
        pass
    
    def backtest(self, historical_data: List[Dict], initial_capital: float = 10000) -> Dict:
        """
        回测策略
        """
        capital = initial_capital
        position = 0
        entry_price = 0
        trade_log = []
        
        for bar in historical_data:
            signal = self.generate_signal(bar)
            
            if signal and signal['action'] != 'hold':
                # 执行交易
                price = bar['close']
                quantity = self.get_position_size(capital, price)
                
                if signal['action'] == 'buy' and position == 0:
                    position = quantity
                    entry_price = price
                    trade_log.append({
                        'type': 'buy',
                        'price': price,
                        'quantity': quantity,
                        'time': bar['datetime']
                    })
                
                elif signal['action'] == 'sell' and position > 0:
                    profit = (price - entry_price) * position
                    capital += profit
                    trade_log.append({
                        'type': 'sell',
                        'price': price,
                        'quantity': position,
                        'profit': profit,
                        'time': bar['datetime']
                    })
                    position = 0
            
            # 检查止损止盈
            if position > 0:
                stop_loss = self.get_stop_loss(entry_price)
                take_profit = self.get_take_profit(entry_price)
                
                if bar['low'] <= stop_loss:
                    # 触发止损
                    profit = (stop_loss - entry_price) * position
                    capital += profit
                    trade_log.append({
                        'type': 'stop_loss',
                        'price': stop_loss,
                        'quantity': position,
                        'profit': profit,
                        'time': bar['datetime']
                    })
                    position = 0
                
                elif bar['high'] >= take_profit:
                    # 触发止盈
                    profit = (take_profit - entry_price) * position
                    capital += profit
                    trade_log.append({
                        'type': 'take_profit',
                        'price': take_profit,
                        'quantity': position,
                        'profit': profit,
                        'time': bar['datetime']
                    })
                    position = 0
        
        # 计算绩效
        performance = self.calculate_performance(trade_log, initial_capital)
        
        return {
            'strategy': self.name,
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return': (capital - initial_capital) / initial_capital * 100,
            'trades': len([t for t in trade_log if t['type'] in ['buy', 'sell']]) // 2,
            'trade_log': trade_log,
            'performance': performance
        }
    
    def calculate_performance(self, trade_log: List[Dict], initial_capital: float) -> Dict:
        """计算绩效指标"""
        wins = [t for t in trade_log if t.get('profit', 0) > 0]
        losses = [t for t in trade_log if t.get('profit', 0) < 0]
        
        total_profit = sum(t.get('profit', 0) for t in trade_log)
        win_rate = len(wins) / (len(wins) + len(losses)) * 100 if (len(wins) + len(losses)) > 0 else 0
        
        return {
            'total_profit': total_profit,
            'win_rate': win_rate,
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'avg_win': sum(t['profit'] for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t['profit'] for t in losses) / len(losses) if losses else 0
        }
    
    def save_to_db(self, conn: sqlite3.Connection):
        """保存策略到数据库"""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO strategies (name, category, description, keywords)
            VALUES (?, ?, ?, ?)
        ''', (
            self.name,
            '自定义策略',
            '基于碧树西风交易思想',
            '量化,策略,交易系统'
        ))
        conn.commit()
