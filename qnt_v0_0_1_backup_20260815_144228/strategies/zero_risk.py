"""
QNT交易策略 - 零风险捡乌龙指
基于碧树西风核心思想：等错来、对冲思维、风险管理
"""

from typing import Dict, List, Optional
import sqlite3
from datetime import datetime
import json

class ZeroRiskStrategy:
    """零风险交易策略"""
    
    def __init__(self, engine):
        self.engine = engine
        self.name = '零风险捡乌龙指'
        self.stats = {
            'total_scans': 0,
            'opportunities_found': 0,
            'high_confidence': 0,
            'executed': 0
        }
    
    def scan_for_arbitrage(self, symbols: List[str], min_spread: float = 0.001) -> List[Dict]:
        """
        扫描套利机会
        核心逻辑：检测价格异常（价差、深度异常等）
        """
        self.stats['total_scans'] += 1
        opportunities = []
        
        for symbol in symbols:
            # 获取深度数据
            orderbook = self.engine.get_orderbook(symbol, limit=20)
            if not orderbook:
                continue
            
            bids = orderbook['bids']
            asks = orderbook['asks']
            
            if not bids or not asks:
                continue
            
            bid = bids[0]
            ask = asks[0]
            
            # 计算价差
            bid_price = bid[0]
            ask_price = ask[0]
            spread = (ask_price - bid_price) / bid_price
            
            # 检查价差异常（捡乌龙指）
            if abs(spread) > min_spread:
                opportunity = {
                    'symbol': symbol,
                    'type': 'spread_anomaly',
                    'direction': 'buy' if spread > 0 else 'sell',
                    'bid_price': bid_price,
                    'ask_price': ask_price,
                    'spread': spread,
                    'bid_volume': bid[1],
                    'ask_volume': ask[1],
                    'confidence': min(abs(spread) / min_spread * 0.5, 1.0),
                    'risk': 'low',
                    'reason': f'价差{spread:.4%}超过阈值{min_spread:.4%}',
                    'timestamp': datetime.now().isoformat()
                }
                opportunities.append(opportunity)
                self.stats['opportunities_found'] += 1
                
                if opportunity['confidence'] > 0.7:
                    self.stats['high_confidence'] += 1
        
        return opportunities
    
    def analyze_order_flow(self, symbol: str) -> Optional[Dict]:
        """分析订单流 - 检测大单异动"""
        orderbook = self.engine.get_orderbook(symbol, limit=50)
        if not orderbook:
            return None
        
        bids = orderbook['bids']
        asks = orderbook['asks']
        
        # 计算各档位的累计量
        bid_levels = []
        ask_levels = []
        bid_cumsum = 0
        ask_cumsum = 0
        
        for i, (price, vol) in enumerate(bids[:10]):
            bid_cumsum += vol
            bid_levels.append({
                'price': price,
                'volume': vol,
                'cumsum': bid_cumsum,
                'depth_percent': bid_cumsum / max(sum(b[1] for b in bids), 1) * 100
            })
        
        for i, (price, vol) in enumerate(asks[:10]):
            ask_cumsum += vol
            ask_levels.append({
                'price': price,
                'volume': vol,
                'cumsum': ask_cumsum,
                'depth_percent': ask_cumsum / max(sum(a[1] for a in asks), 1) * 100
            })
        
        # 检测异常
        anomalies = []
        
        # 1. 买单堆积（可能即将下跌）
        if bid_levels and bid_levels[0]['volume'] > sum(a[1] for a in asks[:3]) * 3:
            anomalies.append({
                'type': 'buy_wall',
                'description': f'买一挂单{bid_levels[0]["volume"]:.4f}远大于卖盘',
                'signal': 'bearish'
            })
        
        # 2. 卖单堆积（可能即将上涨）
        if asks and asks[0][1] > sum(b[1] for b in bids[:3]) * 3:
            anomalies.append({
                'type': 'sell_wall',
                'description': f'卖一挂单{asks[0][1]:.4f}远大于买盘',
                'signal': 'bullish'
            })
        
        # 3. 买卖不平衡
        total_bid = sum(b[1] for b in bids[:20])
        total_ask = sum(a[1] for a in asks[:20])
        
        if total_bid > total_ask * 2:
            anomalies.append({
                'type': 'imbalance_bid',
                'description': f'买盘总量{total_bid:.4f}远大于卖盘{total_ask:.4f}',
                'signal': 'bearish'
            })
        elif total_ask > total_bid * 2:
            anomalies.append({
                'type': 'imbalance_ask',
                'description': f'卖盘总量{total_ask:.4f}远大于买盘{total_bid:.4f}',
                'signal': 'bullish'
            })
        
        if anomalies:
            return {
                'symbol': symbol,
                'anomalies': anomalies,
                'bid_levels': bid_levels,
                'ask_levels': ask_levels,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def get_stats(self) -> Dict:
        """获取策略统计"""
        return {
            'strategy': self.name,
            'scans': self.stats['total_scans'],
            'opportunities': self.stats['opportunities_found'],
            'high_confidence': self.stats['high_confidence'],
            'executed': self.stats['executed']
        }


class TrendStrategy(ZeroRiskStrategy):
    """趋势跟踪策略"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = '趋势跟踪'
    
    def analyze_trend(self, symbol: str, timeframe: str = '1h') -> Optional[Dict]:
        """分析趋势"""
        ohlcv = self.engine.get_ohlcv(symbol, timeframe, limit=100)
        if not ohlcv or len(ohlcv) < 50:
            return None
        
        closes = [c[4] for c in ohlcv]
        
        # 计算均线
        ma_20 = sum(closes[-20:]) / 20
        ma_50 = sum(closes[-50:]) / 50
        ma_100 = sum(closes[-100:]) / 100 if len(closes) >= 100 else ma_50
        
        current_price = closes[-1]
        
        # 趋势判断
        trend = None
        if current_price > ma_20 > ma_50 > ma_100:
            trend = 'strong_up'
        elif current_price > ma_20 > ma_50:
            trend = 'up'
        elif current_price < ma_20 < ma_50 < ma_100:
            trend = 'strong_down'
        elif current_price < ma_20 < ma_50:
            trend = 'down'
        else:
            trend = 'sideways'
        
        return {
            'symbol': symbol,
            'trend': trend,
            'price': current_price,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'ma_100': ma_100,
            'strength': self._calculate_strength(closes, ma_20, ma_50),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_strength(self, closes: List[float], ma20: float, ma50: float) -> float:
        """计算趋势强度"""
        if ma50 == 0:
            return 0
        return (ma20 - ma50) / ma50


class ArbitrageStrategy(ZeroRiskStrategy):
    """量化套利策略"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.name = '量化套利'
    
    def scan_funding_rate(self, symbols: List[str]) -> List[Dict]:
        """
        扫描资金费率异常
        碧树西风《从26个美股坐庄被罚5亿的中国牛散，来聊职业量化对冲套利交易》
        """
        opportunities = []
        
        for symbol in symbols:
            try:
                funding = self.engine.exchanges['okx'].fetch_funding_rate(symbol.replace('/', '-').replace('USDT', '-USDT'))
                if funding and 'fundingRate' in funding:
                    rate = funding['fundingRate']
                    if rate and abs(rate) > 0.0001:  # 资金费率超过0.01%
                        opportunities.append({
                            'symbol': symbol,
                            'type': 'funding_arbitrage',
                            'rate': rate,
                            'annualized': rate * 24 * 365 * 100,  # 年化
                            'action': 'short' if rate > 0 else 'long',
                            'confidence': min(abs(rate) * 1000, 1.0),
                            'reason': f'资金费率{rate:.4%}，年化{abs(rate) * 24 * 365 * 100:.2f}%'
                        })
            except Exception as e:
                continue
        
        return opportunities


# 策略注册表
STRATEGY_REGISTRY = {
    'zero_risk': ZeroRiskStrategy,
    'trend': TrendStrategy,
    'arbitrage': ArbitrageStrategy
}


def get_strategy(name: str, engine) -> Optional[ZeroRiskStrategy]:
    """获取策略实例"""
    cls = STRATEGY_REGISTRY.get(name.lower())
    if cls:
        return cls(engine)
    return None
