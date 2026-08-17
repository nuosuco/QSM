"""
趋势跟踪策略
基于碧树西风"捡乌龙指"思想
"""

from strategies.base_strategy import BaseStrategy
from typing import Dict, Optional
import sqlite3

class TrendFollowingStrategy(BaseStrategy):
    """趋势跟踪策略"""
    
    def __init__(self, config: Dict = None):
        super().__init__('趋势跟踪', config)
        self.config = config or {
            'stop_loss_pct': 0.02,  # 2%止损
            'take_profit_pct': 0.05,  # 5%止盈
            'position_size_pct': 0.2  # 单品种20%仓位
        }
    
    def generate_signal(self, data: Dict) -> Optional[Dict]:
        """
        生成交易信号
        基于趋势判断：价格在均线上方且成交量放大，买入
        """
        close = data.get('close', 0)
        volume = data.get('volume', 0)
        ma_20 = data.get('ma_20', 0)
        ma_50 = data.get('ma_50', 0)
        
        # 趋势判断：短期均线上穿长期均线
        if close > ma_20 > ma_50 and volume > 0:
            return {
                'action': 'buy',
                'price': close,
                'quantity': 1,
                'reason': '趋势向上，均线多头排列'
            }
        elif close < ma_20 < ma_50:
            return {
                'action': 'sell',
                'price': close,
                'quantity': 1,
                'reason': '趋势向下，均线空头排列'
            }
        
        return {'action': 'hold', 'price': close, 'quantity': 0, 'reason': '观望'}
    
    def get_stop_loss(self, entry_price: float) -> float:
        """获取止损价格（向下有限）"""
        return entry_price * (1 - self.config['stop_loss_pct'])
    
    def get_take_profit(self, entry_price: float) -> float:
        """获取止盈价格（向上无限）"""
        return entry_price * (1 + self.config['take_profit_pct'])
    
    def get_position_size(self, capital: float, entry_price: float) -> int:
        """计算仓位大小"""
        position_value = capital * self.config['position_size_pct']
        return int(position_value / entry_price)
    
    def save_to_db(self, conn: sqlite3.Connection):
        """保存策略到数据库"""
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO strategies (name, category, description, keywords)
            VALUES (?, ?, ?, ?)
        ''', (
            self.name,
            '趋势跟踪',
            '基于碧树西风"捡乌龙指"思想，顺势而为',
            '趋势,跟踪,均线,止损,止盈'
        ))
        conn.commit()


class ArbitrageStrategy(BaseStrategy):
    """量化套利策略
    基于碧树西风《从26个美股坐庄被罚5亿的中国牛散，来聊职业量化对冲套利交易》
    """
    
    def __init__(self, config: Dict = None):
        super().__init__('量化套利', config)
        self.config = config or {
            'spread_threshold': 0.01,  # 价差阈值
            'position_size_pct': 0.15
        }
    
    def generate_signal(self, data: Dict) -> Optional[Dict]:
        """套利信号"""
        # 这里需要根据具体品种实现
        spread = data.get('spread', 0)
        spread_threshold = self.config['spread_threshold']
        
        if spread > spread_threshold:
            return {
                'action': 'sell_high_buy_low',
                'price': data.get('price_high', 0),
                'quantity': 1,
                'reason': f'价差{spread:.2%}超过阈值{spread_threshold:.2%}'
            }
        elif spread < -spread_threshold:
            return {
                'action': 'buy_high_sell_low',
                'price': data.get('price_low', 0),
                'quantity': 1,
                'reason': f'价差{spread:.2%}低于阈值-{spread_threshold:.2%}'
            }
        
        return {'action': 'hold', 'price': 0, 'quantity': 0, 'reason': '等待价差回归'}
    
    def get_stop_loss(self, entry_price: float) -> float:
        return entry_price * 0.98
    
    def get_take_profit(self, entry_price: float) -> float:
        return entry_price * 1.02
    
    def get_position_size(self, capital: float, entry_price: float) -> int:
        position_value = capital * self.config['position_size_pct']
        return int(position_value / entry_price)


class OptionsHedgeStrategy(BaseStrategy):
    """期权对冲策略"""
    
    def __init__(self, config: Dict = None):
        super().__init__('期权对冲', config)
        self.config = config or {
            'hedge_ratio': 0.3,  # 对冲比例
            'max_hedge_cost': 0.02  # 最大对冲成本
        }
    
    def generate_signal(self, data: Dict) -> Optional[Dict]:
        """期权对冲信号"""
        # 简化实现
        return {'action': 'hold', 'price': data.get('price', 0), 'quantity': 0, 'reason': '观望'}
    
    def get_stop_loss(self, entry_price: float) -> float:
        return entry_price * 0.95
    
    def get_take_profit(self, entry_price: float) -> float:
        return entry_price * 1.10
    
    def get_position_size(self, capital: float, entry_price: float) -> int:
        position_value = capital * self.config['hedge_ratio']
        return int(position_value / entry_price)


# 策略注册表
STRATEGY_REGISTRY = {
    'trend_following': TrendFollowingStrategy,
    'arbitrage': ArbitrageStrategy,
    'options_hedge': OptionsHedgeStrategy
}

def get_strategy(name: str, config: Dict = None) -> BaseStrategy:
    """获取策略实例"""
    strategy_class = STRATEGY_REGISTRY.get(name.lower())
    if strategy_class:
        return strategy_class(config)
    raise ValueError(f"未知策略: {name}")
