"""
QNT 订单簿分析测试
"""
import pytest
from market.analyzer import OrderBookAnalyzer, MarketImpactEstimator


class TestOrderBookAnalyzer:
    """订单簿分析器测试"""
    
    def setup_method(self):
        """每个测试前重置"""
        self.analyzer = OrderBookAnalyzer(depth_levels=10)
    
    def test_basic_analysis(self):
        """基础分析测试"""
        bids = [(99.5, 100), (99.0, 200), (98.5, 150)]
        asks = [(100.5, 100), (101.0, 200), (101.5, 150)]
        
        snapshot = self.analyzer.analyze(bids, asks)
        
        assert snapshot.mid_price == 100.0
        assert snapshot.spread == 1.0
        assert snapshot.spread_pct == pytest.approx(1.0, abs=0.01)
    
    def test_empty_book(self):
        """空订单簿测试"""
        snapshot = self.analyzer.analyze([], [])
        assert snapshot.mid_price == 0
        assert snapshot.spread == 0
    
    def test_imbalance(self):
        """买卖不平衡测试"""
        # 买盘远大于卖盘
        bids = [(100, 1000), (99, 1000)]
        asks = [(101, 10)]
        
        snapshot = self.analyzer.analyze(bids, asks)
        imbalance = self.analyzer.get_imbalance(snapshot)
        
        assert imbalance > 0.5  # 强买入压力
    
    def test_depth_anomaly(self):
        """深度异常检测测试"""
        # 价差过大
        bids = [(90, 100)]
        asks = [(110, 100)]
        
        snapshot = self.analyzer.analyze(bids, asks)
        assert self.analyzer.detect_anomaly(snapshot) == True
    
    def test_weighted_mid(self):
        """加权中间价测试"""
        bids = [(100, 200), (99, 100)]  # 大单在100
        asks = [(101, 100), (102, 200)]  # 大单在102
        
        snapshot = self.analyzer.analyze(bids, asks)
        weighted = self.analyzer.get_weighted_mid(snapshot)
        
        # 加权价应该偏向有大单的价格
        assert weighted > 100
    
    def test_get_statistics(self):
        """统计信息测试"""
        for _ in range(5):
            bids = [(100, 100), (99, 50)]
            asks = [(101, 100), (102, 50)]
            self.analyzer.analyze(bids, asks)
        
        stats = self.analyzer.get_statistics()
        assert stats['total_snapshots'] == 5
        assert 'avg_spread_pct' in stats


class TestMarketImpactEstimator:
    """市场冲击估算器测试"""
    
    def test_estimate_impact(self):
        """冲击估算测试"""
        estimator = MarketImpactEstimator()
        analyzer = OrderBookAnalyzer()
        
        bids = [(100, 500), (99, 500)]
        asks = [(101, 500), (102, 500)]
        snapshot = analyzer.analyze(bids, asks)
        
        result = estimator.estimate(100.0, snapshot)
        
        assert result['impact_bps'] >= 0
        assert result['slippage'] >= 0
    
    def test_large_order_impact(self):
        """大单冲击测试"""
        estimator = MarketImpactEstimator()
        analyzer = OrderBookAnalyzer()
        
        bids = [(100, 100), (99, 100)]
        asks = [(101, 100), (102, 100)]
        snapshot = analyzer.analyze(bids, asks)
        
        small = estimator.estimate(10.0, snapshot)
        large = estimator.estimate(1000.0, snapshot)
        
        # 大单冲击应该更大
        assert large['impact_bps'] > small['impact_bps']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
