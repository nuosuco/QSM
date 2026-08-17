"""
QNT 新增Agent策略
"""
from agents.base import AgentBase
from config.settings import AgentConfig


class GridTradingAgent(AgentBase):
    """网格交易Agent"""
    
    def __init__(self, name: str = "GridBot", **kwargs):
        super().__init__(agent_id=None, name=name)
        self.grid_levels = kwargs.get('grid_levels', 5)  # 网格层数
        self.grid_spacing = kwargs.get('grid_spacing', 0.01)  # 网格间距1%
        self.order_size = kwargs.get('order_size', 10.0)  # 每单数量
    
    def think(self, observation: dict) -> dict:
        """网格交易决策"""
        mid_price = observation.get('mid_price', 100.0)
        
        # 生成网格订单
        orders = []
        for i in range(-self.grid_levels, self.grid_levels + 1):
            if i == 0:
                continue
            price = mid_price * (1 + i * self.grid_spacing)
            side = 'buy' if i < 0 else 'sell'
            orders.append({
                'side': side,
                'price': round(price, 2),
                'quantity': self.order_size
            })
        
        return {
            'agent': self.name,
            'decision': 'grid_orders',
            'orders': orders,
            'confidence': 0.9,
            'reason': f'网格交易: {len(orders)}层订单'
        }


class MomentumAgent(AgentBase):
    """动量跟踪Agent"""
    
    def __init__(self, name: str = "MomentumBot", config: dict = None, lookback: int = 20):
        super().__init__(name, config or AgentConfig())
        self.lookback = lookback
        self.prices = []
    
    def think(self, observation: dict) -> dict:
        """动量策略决策"""
        price = observation.get('price', 0)
        self.prices.append(price)
        
        if len(self.prices) < self.lookback:
            return {
                'agent': self.name,
                'decision': 'hold',
                'confidence': 0.5,
                'reason': '数据不足'
            }
        
        # 计算动量
        recent = self.prices[-self.lookback:]
        momentum = (recent[-1] - recent[0]) / recent[0]
        
        # 策略
        if momentum > 0.02:  # 强上涨
            action = 'long'
            confidence = min(0.95, 0.7 + momentum * 10)
        elif momentum < -0.02:  # 强下跌
            action = 'short'
            confidence = min(0.95, 0.7 + abs(momentum) * 10)
        else:
            action = 'hold'
            confidence = 0.5
        
        # 保留最新价格
        self.prices = self.prices[-self.lookback:]
        
        return {
            'agent': self.name,
            'decision': action,
            'momentum': round(momentum, 4),
            'confidence': round(confidence, 2),
            'reason': f'动量: {momentum:.2%}'
        }


class MeanReversionAgent(AgentBase):
    """均值回归Agent"""
    
    def __init__(self, name: str = "MeanRevBot", config: dict = None, lookback: int = 30):
        super().__init__(name, config or AgentConfig())
        self.lookback = lookback
        self.prices = []
    
    def think(self, observation: dict) -> dict:
        """均值回归决策"""
        price = observation.get('price', 0)
        self.prices.append(price)
        
        if len(self.prices) < self.lookback:
            return {
                'agent': self.name,
                'decision': 'hold',
                'confidence': 0.5,
                'reason': '数据不足'
            }
        
        # 计算均值和标准差
        recent = self.prices[-self.lookback:]
        mean = sum(recent) / len(recent)
        std = (sum((p - mean) ** 2 for p in recent) / len(recent)) ** 0.5
        
        # Z-score
        z_score = (price - mean) / std if std > 0 else 0
        
        # 策略
        if z_score > 2:  # 价格远高于均值
            action = 'short'
            confidence = min(0.9, 0.5 + z_score * 0.1)
        elif z_score < -2:  # 价格远低于均值
            action = 'long'
            confidence = min(0.9, 0.5 + abs(z_score) * 0.1)
        else:
            action = 'hold'
            confidence = 0.3
        
        # 保留数据
        self.prices = self.prices[-self.lookback:]
        
        return {
            'agent': self.name,
            'decision': action,
            'z_score': round(z_score, 2),
            'mean': round(mean, 2),
            'std': round(std, 2),
            'confidence': round(confidence, 2),
            'reason': f'Z-Score: {z_score:.2f}'
        }


class VolumeProfileAgent(AgentBase):
    """成交量分析Agent"""
    
    def __init__(self, name: str = "VolProfileBot", config: dict = None, lookback: int = 20):
        super().__init__(name, config or AgentConfig())
        self.lookback = lookback
        self.prices = []
        self.volumes = []
    
    def think(self, observation: dict) -> dict:
        """成交量分析决策"""
        price = observation.get('price', 0)
        volume = observation.get('volume', 0)
        
        self.prices.append(price)
        self.volumes.append(volume)
        
        if len(self.prices) < self.lookback:
            return {
                'agent': self.name,
                'decision': 'hold',
                'confidence': 0.5,
                'reason': '数据不足'
            }
        
        # 计算成交量加权均价
        recent_prices = self.prices[-self.lookback:]
        recent_volumes = self.volumes[-self.lookback:]
        vwap = sum(p * v for p, v in zip(recent_prices, recent_volumes)) / sum(recent_volumes)
        
        # 成交量变化
        avg_vol = sum(recent_volumes) / len(recent_volumes)
        vol_ratio = volume / avg_vol if avg_vol > 0 else 1.0
        
        # 策略
        if price > vwap and vol_ratio > 1.5:  # 价格上涨+放量
            action = 'long'
            confidence = min(0.85, 0.5 + vol_ratio * 0.1)
        elif price < vwap and vol_ratio > 1.5:  # 价格下跌+放量
            action = 'short'
            confidence = min(0.85, 0.5 + vol_ratio * 0.1)
        else:
            action = 'hold'
            confidence = 0.4
        
        # 保留数据
        self.prices = self.prices[-self.lookback:]
        self.volumes = self.volumes[-self.lookback:]
        
        return {
            'agent': self.name,
            'decision': action,
            'vwap': round(vwap, 2),
            'vol_ratio': round(vol_ratio, 2),
            'confidence': round(confidence, 2),
            'reason': f'VWAP:{vwap:.2f}, 量比:{vol_ratio:.2f}x'
        }


def create_agent(agent_type: str, name: str = None, **kwargs) -> AgentBase:
    """工厂函数创建Agent"""
    agents = {
        'grid': GridTradingAgent,
        'momentum': MomentumAgent,
        'mean_reversion': MeanReversionAgent,
        'volume_profile': VolumeProfileAgent,
        'arb': None,  # 已有
        'mm': None,   # 已有
        'trend': None  # 已有
    }
    
    if agent_type in agents and agents[agent_type] is not None:
        return agents[agent_type](name=name or f'{agent_type}_bot', **kwargs)
    
    raise ValueError(f"Unknown agent type: {agent_type}")
