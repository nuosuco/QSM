"""
QNT交易执行器 - 支持真实交易和纸面交易
"""

import ccxt
import json
import sqlite3
from datetime import datetime
from typing import Dict, Optional, List
import time

class TradeExecutor:
    """交易执行器"""
    
    def __init__(self, config_path: str = '/root/SOM/qnt/config/api_keys.json'):
        self.config = self._load_config(config_path)
        self.db_path = '/root/SOM/data/trading_system/qnt.db'
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.mode = self.config.get('trading_config', {}).get('mode', 'paper')
        self.init_exchanges()
    
    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {"exchanges": {}, "trading_config": {"mode": "paper"}}
    
    def init_exchanges(self):
        """初始化有API Key的交易所"""
        for name, cfg in self.config.get('exchanges', {}).items():
            if not cfg.get('enabled'):
                continue
            try:
                cls = getattr(ccxt, name)
                kwargs = {'enableRateLimit': True, 'timeout': 10000}
                if cfg.get('api_key'):
                    kwargs['apiKey'] = cfg['api_key']
                if cfg.get('api_secret'):
                    kwargs['secret'] = cfg['api_secret']
                if cfg.get('password'):
                    kwargs['password'] = cfg['password']
                if cfg.get('passphrase'):
                    kwargs['password'] = cfg['passphrase']
                
                ex = cls(kwargs)
                # 测试连接
                balance = ex.fetch_balance()
                self.exchanges[name] = ex
                print(f"✅ {name} API连接成功")
            except Exception as e:
                print(f"❌ {name} API连接失败: {e}")
    
    def _log(self, message: str, level: str = 'INFO'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO qnt_logs (level, message, module, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (level, message, 'executor', datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def check_balance(self, exchange: str, currency: str = 'USDT') -> Optional[Dict]:
        """检查账户余额"""
        if exchange not in self.exchanges:
            return None
        try:
            balance = self.exchanges[exchange].fetch_balance()
            return {
                'free': float(balance.get(currency, {}).get('free', 0)),
                'used': float(balance.get(currency, {}).get('used', 0)),
                'total': float(balance.get(currency, {}).get('total', 0))
            }
        except Exception as e:
            self._log(f'获取{exchange}余额失败: {e}', 'ERROR')
            return None
    
    def place_order(self, exchange: str, symbol: str, side: str, order_type: str, 
                    amount: float, price: float = None) -> Optional[Dict]:
        """下单"""
        if exchange not in self.exchanges:
            return None
        
        # 安全检查：不允许自动提现
        if self.mode == 'live' and not self.config.get('trading_config', {}).get('auto_execute', False):
            return {'error': '需要手动确认', 'status': 'pending'}
        
        try:
            ex = self.exchanges[exchange]
            
            # 构建订单参数
            params = {
                'type': order_type,  # 'market' or 'limit'
                'side': side,  # 'buy' or 'sell'
                'symbol': symbol,
                'amount': amount,
            }
            
            if order_type == 'limit' and price:
                params['price'] = price
            
            order = ex.create_order(**params)
            
            self._log(f"✅ 下单成功: {side} {amount} {symbol} @ {order.get('price', 'market')}")
            return order
            
        except Exception as e:
            self._log(f"❌ 下单失败: {e}", 'ERROR')
            return {'error': str(e)}
    
    def cancel_order(self, exchange: str, order_id: str, symbol: str) -> bool:
        """撤单"""
        if exchange not in self.exchanges:
            return False
        try:
            self.exchanges[exchange].cancel_order(order_id, symbol)
            self._log(f"✅ 撤单成功: {order_id}")
            return True
        except Exception as e:
            self._log(f"❌ 撤单失败: {e}", 'ERROR')
            return False
    
    def execute_spread_trade(self, opportunity: Dict) -> Dict:
        """
        执行跨所价差套利
        买低卖高，锁定价差
        """
        result = {
            'symbol': opportunity['symbol'],
            'spread_pct': opportunity['spread_pct'],
            'buy_side': {},
            'sell_side': {},
            'status': 'pending',
            'executed': False
        }
        
        # 买入侧
        buy_ex = opportunity['buy_exchange']
        buy_symbol = opportunity['symbol']
        buy_price = opportunity['buy_price']
        
        # 卖出侧  
        sell_ex = opportunity['sell_exchange']
        sell_symbol = opportunity['symbol']
        sell_price = opportunity['sell_price']
        
        # 检查是否有足够的资金
        if self.mode != 'paper':
            balance = self.check_balance(buy_ex, 'USDT')
            if not balance or balance['free'] < 100:
                result['status'] = 'insufficient_funds'
                result['error'] = f'{buy_ex}余额不足(需要≥$100)'
                return result
        
        # 模拟执行
        if self.mode == 'paper':
            result['status'] = 'paper_executed'
            result['executed'] = True
            result['expected_profit'] = opportunity['spread_pct'] * 0.8  # 扣除手续费
        else:
            result['status'] = 'live_pending'
        
        return result


class PaperTrader:
    """纸面交易器 - 用于模拟回测"""
    
    def __init__(self, initial_balance: float = 10000):
        self.balance_usdt = initial_balance
        self.positions = {}
        self.trades = []
        self.start_time = datetime.now()
    
    def buy(self, symbol: str, price: float, amount: float) -> Dict:
        """买入"""
        cost = price * amount
        if cost > self.balance_usdt:
            amount = self.balance_usdt / price
            cost = price * amount
        
        self.balance_usdt -= cost
        if symbol not in self.positions:
            self.positions[symbol] = {'amount': 0, 'avg_price': 0, 'cost': 0}
        
        pos = self.positions[symbol]
        total_amount = pos['amount'] + amount
        pos['avg_price'] = (pos['avg_price'] * pos['amount'] + price * amount) / total_amount
        pos['amount'] = total_amount
        pos['cost'] += cost
        
        trade = {
            'type': 'buy',
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'cost': cost,
            'time': datetime.now().isoformat()
        }
        self.trades.append(trade)
        return trade
    
    def sell(self, symbol: str, price: float, amount: float = None) -> Dict:
        """卖出"""
        if symbol not in self.positions or self.positions[symbol]['amount'] < amount:
            amount = self.positions.get(symbol, {}).get('amount', 0)
        
        revenue = price * amount
        self.balance_usdt += revenue
        
        pos = self.positions[symbol]
        profit = (price - pos['avg_price']) * amount
        pos['amount'] -= amount
        if pos['amount'] <= 0:
            del self.positions[symbol]
        
        trade = {
            'type': 'sell',
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'revenue': revenue,
            'profit': profit,
            'time': datetime.now().isoformat()
        }
        self.trades.append(trade)
        return trade
    
    def get_pnl(self) -> Dict:
        """计算盈亏"""
        total_value = self.balance_usdt
        for symbol, pos in self.positions.items():
            total_value += pos['amount'] * 0  # 需要实时价格
        
        return {
            'balance_usdt': self.balance_usdt,
            'positions': self.positions,
            'total_trades': len(self.trades),
            'start_time': self.start_time.isoformat()
        }


if __name__ == '__main__':
    print("=" * 60)
    print("      QNT交易执行器测试")
    print("=" * 60)
    
    # 测试纸面交易
    paper = PaperTrader(initial_balance=10000)
    print(f"\n💰 初始资金: ${paper.balance_usdt:,.2f}")
    
    # 模拟买卖
    paper.buy('BTC/USDT', 63500, 0.1)
    print(f"  买入 0.1 BTC @ $63,500")
    print(f"  剩余USDT: ${paper.balance_usdt:,.2f}")
    
    paper.sell('BTC/USDT', 64000, 0.1)
    print(f"  卖出 0.1 BTC @ $64,000")
    print(f"  剩余USDT: ${paper.balance_usdt:,.2f}")
    
    pnl = paper.get_pnl()
    print(f"\n📊 盈亏: ${pnl['balance_usdt'] - 10000:+,.2f}")
    print("=" * 60)
