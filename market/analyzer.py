"""
QNT 订单簿深度分析模块
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DepthSnapshot:
    """深度快照"""
    timestamp: float
    bids: List[Tuple[float, float]]  # (price, volume)
    asks: List[Tuple[float, float]]
    mid_price: float
    spread: float
    spread_pct: float


class OrderBookAnalyzer:
    """订单簿深度分析器"""
    
    def __init__(self, depth_levels: int = 20):
        self.depth_levels = depth_levels
        self._snapshots: List[DepthSnapshot] = []
    
    def analyze(self, bids: List[Tuple[float, float]], 
                asks: List[Tuple[float, float]]) -> DepthSnapshot:
        """分析订单簿深度"""
        # 排序
        sorted_bids = sorted(bids, key=lambda x: x[0], reverse=True)[:self.depth_levels]
        sorted_asks = sorted(asks, key=lambda x: x[0])[:self.depth_levels]
        
        if not sorted_bids or not sorted_asks:
            return DepthSnapshot(
                timestamp=__import__('time').time(),
                bids=[], asks=[],
                mid_price=0, spread=0, spread_pct=0
            )
        
        best_bid = sorted_bids[0][0]
        best_ask = sorted_asks[0][0]
        mid_price = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        spread_pct = (spread / mid_price) * 100 if mid_price > 0 else 0
        
        # 计算累积深度
        bid_volume = sum(b[1] for b in sorted_bids)
        ask_volume = sum(a[1] for a in sorted_asks)
        
        # 计算深度不对称性
        depth_ratio = bid_volume / ask_volume if ask_volume > 0 else float('inf')
        
        snapshot = DepthSnapshot(
            timestamp=__import__('time').time(),
            bids=sorted_bids,
            asks=sorted_asks,
            mid_price=mid_price,
            spread=spread,
            spread_pct=spread_pct
        )
        
        self._snapshots.append(snapshot)
        
        return snapshot
    
    def get_imbalance(self, snapshot: DepthSnapshot) -> float:
        """获取买卖不平衡度 (-1 ~ 1)"""
        bid_vol = sum(b[1] for b in snapshot.bids)
        ask_vol = sum(a[1] for a in snapshot.asks)
        total = bid_vol + ask_vol
        if total == 0:
            return 0
        return (bid_vol - ask_vol) / total
    
    def detect_anomaly(self, snapshot: DepthSnapshot) -> bool:
        """检测深度异常"""
        # 异常1: 价差过大
        if snapshot.spread_pct > 0.5:
            return True
        
        # 异常2: 深度极度不对称
        imbalance = abs(self.get_imbalance(snapshot))
        if imbalance > 0.8:
            return True
        
        # 异常3: 买盘或卖盘突然消失
        if len(snapshot.bids) < 2 or len(snapshot.asks) < 2:
            return True
        
        return False
    
    def get_weighted_mid(self, snapshot: DepthSnapshot) -> float:
        """计算加权中间价"""
        bid_vol = sum(b[1] for b in snapshot.bids)
        ask_vol = sum(a[1] for a in snapshot.asks)
        
        if bid_vol + ask_vol == 0:
            return snapshot.mid_price
        
        # 成交量加权
        weighted_bid = sum(b[0] * b[1] for b in snapshot.bids) / bid_vol if bid_vol > 0 else 0
        weighted_ask = sum(a[0] * a[1] for a in snapshot.asks) / ask_vol if ask_vol > 0 else 0
        
        return (weighted_bid + weighted_ask) / 2
    
    def get_recent_snapshots(self, seconds: float = 60) -> List[DepthSnapshot]:
        """获取最近N秒的快照"""
        cutoff = __import__('time').time() - seconds
        return [s for s in self._snapshots if s.timestamp >= cutoff]
    
    def get_statistics(self) -> Dict[str, float]:
        """获取统计信息"""
        if not self._snapshots:
            return {}
        
        spreads = [s.spread_pct for s in self._snapshots]
        imbalances = [self.get_imbalance(s) for s in self._snapshots]
        
        return {
            'avg_spread_pct': np.mean(spreads),
            'std_spread_pct': np.std(spreads),
            'avg_imbalance': np.mean(imbalances),
            'anomaly_count': sum(1 for s in self._snapshots if self.detect_anomaly(s)),
            'total_snapshots': len(self._snapshots)
        }


class MarketImpactEstimator:
    """市场冲击估算器"""
    
    def __init__(self, slippage_model: str = 'square_root'):
        self.slippage_model = slippage_model
    
    def estimate(self, order_size: float, snapshot: DepthSnapshot) -> Dict[str, float]:
        """估算市场冲击"""
        if snapshot.mid_price == 0:
            return {'impact_bps': 0, 'slippage': 0}
        
        if self.slippage_model == 'square_root':
            # 平方根模型: 冲击 ∝ sqrt(订单量/流动性)
            liquidity = sum(a[1] for a in snapshot.asks) + sum(b[1] for b in snapshot.bids)
            if liquidity == 0:
                return {'impact_bps': float('inf'), 'slippage': float('inf')}
            
            impact_bps = 10000 * np.sqrt(order_size / liquidity) * 0.1
            slippage = order_size * snapshot.mid_price * impact_bps / 10000
        
        else:
            # 线性模型
            impact_bps = 10000 * (order_size / (snapshot.asks[0][1] if snapshot.asks else 1)) * 0.01
            slippage = order_size * snapshot.mid_price * impact_bps / 10000
        
        return {
            'impact_bps': impact_bps,
            'slippage': slippage,
            'order_size': order_size,
            'mid_price': snapshot.mid_price
        }


# 全局分析器实例
_analyzer: Optional[OrderBookAnalyzer] = None


def get_analyzer(depth_levels: int = 20) -> OrderBookAnalyzer:
    """获取订单簿分析器实例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = OrderBookAnalyzer(depth_levels)
    return _analyzer
