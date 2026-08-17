"""
QNT 交易策略回测引擎
"""
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float
    Sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_profit: float
    avg_loss: float
    profit_factor: float


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 100000.0, fee_rate: float = 0.001):
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self._capital = initial_capital
        self._trades: List[Dict] = []
        self._equity_curve: List[float] = []
    
    def run(self, strategy, market_data: List[Dict]) -> BacktestResult:
        """运行回测"""
        self._capital = self.initial_capital
        self._trades = []
        self._equity_curve = [self.initial_capital]
        
        for i, data in enumerate(market_data):
            # 执行策略
            decision = strategy.think(data, self._get_state())
            
            if decision.get('action') in ['buy', 'sell']:
                self._execute_trade(decision, data)
            
            # 记录权益
            self._equity_curve.append(self._capital)
        
        return self._calculate_results()
    
    def _execute_trade(self, decision: Dict, market_data: Dict):
        """执行交易"""
        action = decision['action']
        quantity = decision.get('quantity', 0)
        price = market_data['price']
        
        # 计算费用
        fee = quantity * price * self.fee_rate
        
        if action == 'buy':
            cost = quantity * price + fee
            self._capital -= cost
        elif action == 'sell':
            revenue = quantity * price - fee
            self._capital += revenue
        
        self._trades.append({
            'action': action,
            'quantity': quantity,
            'price': price,
            'fee': fee,
            'timestamp': market_data.get('timestamp', 0)
        })
    
    def _get_state(self) -> Dict:
        """获取当前状态"""
        return {
            'capital': self._capital,
            'trades': len(self._trades),
            'equity': self._equity_curve[-1] if self._equity_curve else self._capital
        }
    
    def _calculate_results(self) -> BacktestResult:
        """计算回测结果"""
        total_return = (self._capital - self.initial_capital) / self.initial_capital
        
        # 计算收益率序列
        returns = np.diff(self._equity_curve) / self._equity_curve[:-1]
        
        # Sharpe ratio (假设无风险利率为0)
        Sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # 最大回撤
        peak = self._equity_curve[0]
        max_drawdown = 0
        for equity in self._equity_curve:
            peak = max(peak, equity)
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # 胜率分析
        winning = [t for t in self._trades if t['action'] == 'sell']
        losing = [t for t in self._trades if t['action'] == 'buy']
        
        win_rate = len(winning) / len(self._trades) if self._trades else 0
        
        # 平均盈亏
        avg_profit = np.mean([t['price'] * t['quantity'] for t in winning]) if winning else 0
        avg_loss = np.mean([t['price'] * t['quantity'] for t in losing]) if losing else 0
        
        profit_factor = abs(sum(t['price'] * t['quantity'] for t in winning) / 
                           sum(t['price'] * t['quantity'] for t in losing)) if losing else float('inf')
        
        return BacktestResult(
            total_return=total_return,
            Sharpe_ratio=Sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(self._trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor
        )
    
    def get_equity_curve(self) -> List[float]:
        """获取权益曲线"""
        return self._equity_curve
    
    def get_trades(self) -> List[Dict]:
        """获取交易记录"""
        return self._trades


class MockStrategy:
    """模拟策略 - 用于测试"""
    
    def __init__(self, buy_threshold: float = 0.95, sell_threshold: float = 1.05):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.price_history = []
    
    def think(self, data: Dict, state: Dict) -> Dict:
        """策略决策"""
        price = data['price']
        self.price_history.append(price)
        
        if len(self.price_history) < 2:
            return {'action': 'hold'}
        
        prev_price = self.price_history[-2]
        
        # 简单均值回归策略
        if price < prev_price * self.buy_threshold:
            return {'action': 'buy', 'quantity': state['capital'] * 0.1 / price}
        elif price > prev_price * self.sell_threshold:
            return {'action': 'sell', 'quantity': state.get('position', 0)}
        
        return {'action': 'hold'}


def generate_mock_data(days: int = 30, initial_price: float = 100.0) -> List[Dict]:
    """生成模拟市场数据"""
    np.random.seed(42)
    data = []
    price = initial_price
    
    for i in range(days * 24):  # 每小时一条数据
        # 随机游走
        change = np.random.randn() * 0.01 * price
        price = max(0.01, price + change)
        
        data.append({
            'price': price,
            'volume': np.random.uniform(100, 1000),
            'timestamp': datetime.now().timestamp() - (days * 24 - i) * 3600
        })
    
    return data


if __name__ == '__main__':
    # 示例回测
    engine = BacktestEngine(initial_capital=100000.0)
    strategy = MockStrategy()
    data = generate_mock_data(days=7)
    
    result = engine.run(strategy, data)
    
    print(f"=== 回测结果 ===")
    print(f"总收益率: {result.total_return:.2%}")
    print(f"Sharpe比率: {result.Sharpe_ratio:.2f}")
    print(f"最大回撤: {result.max_drawdown:.2%}")
    print(f"胜率: {result.win_rate:.2%}")
    print(f"总交易次数: {result.total_trades}")
    print(f"盈利因子: {result.profit_factor:.2f}")
