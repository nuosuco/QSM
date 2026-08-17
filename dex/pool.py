"""
QNT DEX - 去中心化交易所模块
支持AMM做市商和流动性池
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class LiquidityPosition:
    """流动性仓位"""
    provider: str
    token_a: str
    token_b: str
    amount_a: float
    amount_b: float
    liquidity: float
    fees_earned: float = 0.0


class AMMPool:
    """AMM流动性池 - 恒定乘积做市商"""
    
    def __init__(self, token_a: str, token_b: str, reserve_a: float, reserve_b: float, fee_rate: float = 0.003):
        self.token_a = token_a
        self.token_b = token_b
        self.reserve_a = reserve_a
        self.reserve_b = reserve_b
        self.fee_rate = fee_rate
        self.liquidity_providers: Dict[str, LiquidityPosition] = {}
        self.total_liquidity = math.sqrt(reserve_a * reserve_b)
        self.price_history: List[Tuple[float, float]] = []
    
    @property
    def price(self) -> float:
        """当前价格 (token_b per token_a)"""
        if self.reserve_a == 0:
            return float('inf')
        return self.reserve_b / self.reserve_a
    
    def get_amount_out(self, amount_in: float, token_a: str) -> float:
        """计算兑换输出量"""
        fee = amount_in * self.fee_rate
        amount_in_after_fee = amount_in - fee
        
        if token_a == self.token_a:
            numerator = amount_in_after_fee * self.reserve_b
            denominator = self.reserve_a + amount_in_after_fee
        else:
            numerator = amount_in_after_fee * self.reserve_a
            denominator = self.reserve_b + amount_in_after_fee
        
        return numerator / denominator
    
    def swap(self, amount_in: float, token_in: str) -> float:
        """执行兑换"""
        amount_out = self.get_amount_out(amount_in, token_in)
        
        if token_in == self.token_a:
            self.reserve_a += amount_in
            self.reserve_b -= amount_out
        else:
            self.reserve_b += amount_in
            self.reserve_a -= amount_out
        
        self.price_history.append((self.price, len(self.price_history)))
        return amount_out
    
    def add_liquidity(self, provider: str, amount_a: float, amount_b: float) -> float:
        """添加流动性"""
        if self.total_liquidity == 0:
            liquidity = math.sqrt(amount_a * amount_b)
        else:
            liquidity = min(amount_a / self.reserve_a, amount_b / self.reserve_b) * self.total_liquidity
        
        liquidity -= 1e-10  # 防止浮点误差
        
        position = LiquidityPosition(
            provider=provider,
            token_a=self.token_a,
            token_b=self.token_b,
            amount_a=amount_a,
            amount_b=amount_b,
            liquidity=liquidity
        )
        
        self.liquidity_providers[provider] = position
        self.reserve_a += amount_a
        self.reserve_b += amount_b
        self.total_liquidity += liquidity
        
        return liquidity
    
    def remove_liquidity(self, provider: str, liquidity: float) -> Tuple[float, float]:
        """移除流动性"""
        if provider not in self.liquidity_providers:
            return 0.0, 0.0
        
        position = self.liquidity_providers[provider]
        ratio = liquidity / position.liquidity
        
        amount_a = self.reserve_a * ratio
        amount_b = self.reserve_b * ratio
        
        self.reserve_a -= amount_a
        self.reserve_b -= amount_b
        self.total_liquidity -= liquidity
        
        position.liquidity -= liquidity
        if position.liquidity <= 0:
            del self.liquidity_providers[provider]
        
        return amount_a, amount_b
    
    def get_price_impact(self, amount: float, token_in: str) -> float:
        """计算价格冲击"""
        price_before = self.price
        amount_out = self.swap(amount, token_in)
        # 恢复
        if token_in == self.token_a:
            self.reserve_a -= amount
            self.reserve_b += amount_out
        else:
            self.reserve_b -= amount
            self.reserve_a += amount_out
        
        price_after = self.price
        impact = abs(price_after - price_before) / price_before
        return impact


class DEXEngine:
    """DEX引擎 - 多池管理"""
    
    def __init__(self):
        self.pools: Dict[str, AMMPool] = {}
        self.trades: List[Dict] = []
    
    def create_pool(self, token_a: str, token_b: str, reserve_a: float, reserve_b: float, fee_rate: float = 0.003) -> AMMPool:
        """创建流动性池"""
        pair = f"{token_a}/{token_b}"
        pool = AMMPool(token_a, token_b, reserve_a, reserve_b, fee_rate)
        self.pools[pair] = pool
        return pool
    
    def swap(self, pair: str, amount_in: float, token_in: str) -> float:
        """兑换"""
        pool = self.pools.get(pair)
        if not pool:
            raise ValueError(f"Pool not found: {pair}")
        
        amount_out = pool.swap(amount_in, token_in)
        
        self.trades.append({
            'pair': pair,
            'token_in': token_in,
            'amount_in': amount_in,
            'amount_out': amount_out,
            'price': amount_in / amount_out if amount_out > 0 else 0
        })
        
        return amount_out
    
    def add_liquidity(self, pair: str, provider: str, amount_a: float, amount_b: float) -> float:
        """添加流动性"""
        pool = self.pools.get(pair)
        if not pool:
            raise ValueError(f"Pool not found: {pair}")
        
        return pool.add_liquidity(provider, amount_a, amount_b)
    
    def get_pool(self, pair: str) -> Optional[AMMPool]:
        """获取池子"""
        return self.pools.get(pair)
    
    def list_pools(self) -> List[Dict]:
        """列出所有池子"""
        return [
            {
                'pair': pair,
                'price': pool.price,
                'reserve_a': pool.reserve_a,
                'reserve_b': pool.reserve_b,
                'liquidity': pool.total_liquidity,
                'providers': len(pool.liquidity_providers)
            }
            for pair, pool in self.pools.items()
        ]
