"""
捡乌龙指策略 v2.0
核心：同平台跨厅对冲，瞬间锁利，不持仓
"""
import ccxt
import os
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import sqlite3

@dataclass
class OolongSignal:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_pct: float
    net_profit_pct: float
    buy_volume: float
    sell_volume: float
    timestamp: str
    
    def is_profitable(self, threshold: float = 0.002) -> bool:
        return self.net_profit_pct > threshold

class OolongIndexStrategy:
    """
    捡乌龙指策略 v2.0
    - 同平台操作（不能跨平台）
    - 永续开多 + 现货卖单
    - 不持仓过夜
    - 不等价格恢复
    """
    
    def __init__(self, symbol: str = None):
        self.symbol = symbol
        self.env_file = os.path.expanduser('~/.qnt_env')
        self.load_api_keys()
        
        # 交易所实例
        self.bitget = self._create_bitget()
        
        # 数据库
        self.db_path = '/root/SOM/data/trading_system/qnt.db'
        self.conn = sqlite3.connect(self.db_path)
        
    def load_api_keys(self):
        if not os.path.exists(self.env_file):
            raise Exception(f"API密钥文件不存在: {self.env_file}")
        
        for line in open(self.env_file):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
        
        self.bitget_key = os.getenv('BITGET_API_KEY')
        self.bitget_secret = os.getenv('BITGET_API_SECRET')
        self.bitget_passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')
        
    def _create_bitget(self):
        return ccxt.bitget({
            'apiKey': self.bitget_key,
            'secret': self.bitget_secret,
            'password': self.bitget_passphrase,
            'enableRateLimit': True
        })
    
    def detect_oolong_index(self) -> List[OolongSignal]:
        """
        检测捡乌龙指机会
        
        正确理解：
        1. 必须在同平台操作
        2. 永续厅价格异常偏离
        3. 现货厅价格正常（参考系）
        4. 永续开多 + 现货卖单
        5. 不等价格恢复，瞬间对冲
        """
        signals = []
        
        # 只检查Bitget同平台机会
        try:
            # 获取现货价格
            spot = self.bitget.fetch_ticker(f'{self.symbol}/USDT')
            spot_bid = float(spot['bid'])
            spot_ask = float(spot['ask'])
            
            # 获取永续价格
            perp = self.bitget.fetch_ticker(f'{self.symbol}/USDT:USDT')
            perp_bid = float(perp['bid'])
            perp_ask = float(perp['ask'])
            
            # 捡乌龙指核心：永续价格异常偏离
            # 永续ask < 现货bid → 永续打9折，现货原价卖
            
            # 计算价差（永续买 vs 现货卖）
            spread = (spot_bid - perp_ask) / perp_ask * 100
            net_spread = spread - 0.12  # 双边手续费
            
            if net_spread > 0.1:  # 净利超过0.1%
                signal = OolongSignal(
                    symbol=self.symbol,
                    buy_exchange='Bitget永续',
                    sell_exchange='Bitget现货',
                    buy_price=perp_ask,
                    sell_price=spot_bid,
                    spread_pct=spread,
                    net_profit_pct=net_spread,
                    buy_volume=1.0,
                    sell_volume=1.0,
                    timestamp=datetime.now().isoformat()
                )
                signals.append(signal)
                
        except Exception as e:
            pass
        
        return signals
    
    def scan_all_coins(self, coins: List[str]) -> List[OolongSignal]:
        """扫描所有币种"""
        all_signals = []
        
        for coin in coins:
            signals = self.detect_oolong_index()
            if signals:
                all_signals.extend(signals)
        
        return all_signals
    
    def save_signal(self, signal: OolongSignal):
        """保存信号到数据库"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO qnt_signals 
            (symbol, buy_exchange, sell_exchange, buy_price, sell_price, 
             spread_pct, net_profit_pct, created_at, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal.symbol, signal.buy_exchange, signal.sell_exchange,
            signal.buy_price, signal.sell_price, signal.spread_pct,
            signal.net_profit_pct, signal.timestamp, 'oolong_v2'
        ))
        self.conn.commit()
    
    def close(self):
        self.conn.close()


if __name__ == '__main__':
    print("=" * 70)
    print("  捡乌龙指策略 v2.0 - 同平台跨厅对冲")
    print("=" * 70)
    
    strategy = OolongIndexStrategy()
    
    # 测试RVN
    signals = strategy.detect_oolong_index()
    
    if signals:
        print("\n发现机会:")
        for s in signals:
            print(f"  {s.symbol}: {s.buy_exchange}买@{s.buy_price:.6f} → {s.sell_exchange}卖@{s.sell_price:.6f}")
            print(f"  毛利{s.spread_pct:.4f}% 净利{s.net_profit_pct:.4f}%")
    else:
        print("\n当前没有异常价差")
    
    strategy.close()
