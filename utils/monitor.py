"""
QNT 性能监控
"""
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: float
    trades_per_second: float
    orders_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self._start_time = time.time()
        self._trade_count = 0
        self._order_count = 0
        self._metrics_history: List[PerformanceMetrics] = []
        self._lock = threading.Lock()
    
    def record_trade(self):
        """记录成交"""
        with self._lock:
            self._trade_count += 1
    
    def record_order(self):
        """记录订单"""
        with self._lock:
            self._order_count += 1
    
    def get_metrics(self) -> Dict[str, any]:
        """获取当前指标"""
        with self._lock:
            elapsed = time.time() - self._start_time
            return {
                'uptime_seconds': elapsed,
                'total_trades': self._trade_count,
                'total_orders': self._order_count,
                'trades_per_second': self._trade_count / elapsed if elapsed > 0 else 0,
                'orders_per_second': self._order_count / elapsed if elapsed > 0 else 0
            }
    
    def snapshot(self) -> PerformanceMetrics:
        """生成性能快照"""
        import psutil
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            trades_per_second=self.get_metrics()['trades_per_second'],
            orders_per_second=self.get_metrics()['orders_per_second'],
            memory_usage_mb=psutil.Process().memory_info().rss / 1024 / 1024,
            cpu_usage_percent=psutil.Process().cpu_percent()
        )
        with self._lock:
            self._metrics_history.append(metrics)
            # 只保留最近1000个快照
            if len(self._metrics_history) > 1000:
                self._metrics_history = self._metrics_history[-1000:]
        return metrics
    
    def get_stats(self) -> Dict[str, any]:
        """获取统计信息"""
        metrics = self.get_metrics()
        with self._lock:
            history = self._metrics_history[-100:] if self._metrics_history else []
        
        return {
            **metrics,
            'samples_count': len(history),
            'avg_tps': sum(m.trades_per_second for m in history) / len(history) if history else 0,
            'avg_ops': sum(m.orders_per_second for m in history) / len(history) if history else 0
        }


# 全局监控实例
monitor = PerformanceMonitor()
