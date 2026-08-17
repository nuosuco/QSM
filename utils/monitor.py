"""
QNT 监控系统
"""
import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metrics:
    """指标数据"""
    timestamp: float
    blocks: int
    transactions: int
    trades: int
    nstate_rounds: int
    nstate_collapses: int
    agent_count: int
    active_agents: int


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self._metrics: List[Metrics] = []
        self._max_history = 10000
        self._lock = threading.Lock()
    
    def record(self, metrics: Metrics):
        """记录指标"""
        with self._lock:
            self._metrics.append(metrics)
            if len(self._metrics) > self._max_history:
                self._metrics = self._metrics[-self._max_history:]
    
    def get_latest(self) -> Optional[Metrics]:
        """获取最新指标"""
        with self._lock:
            return self._metrics[-1] if self._metrics else None
    
    def get_history(self, minutes: int = 60) -> List[Metrics]:
        """获取历史指标"""
        cutoff = time.time() - (minutes * 60)
        with self._lock:
            return [m for m in self._metrics if m.timestamp >= cutoff]
    
    def get_summary(self) -> Dict[str, Any]:
        """获取汇总数据"""
        with self._lock:
            if not self._metrics:
                return {}
            
            recent = [m for m in self._metrics if m.timestamp >= time.time() - 3600]
            
            return {
                'total_blocks': self._metrics[-1].blocks if self._metrics else 0,
                'total_transactions': self._metrics[-1].transactions if self._metrics else 0,
                'total_trades': self._metrics[-1].trades if self._metrics else 0,
                'total_nstate_rounds': self._metrics[-1].nstate_rounds if self._metrics else 0,
                'total_nstate_collapses': self._metrics[-1].nstate_collapses if self._metrics else 0,
                'agent_count': self._metrics[-1].agent_count if self._metrics else 0,
                'history_points': len(self._metrics),
                'recent_hours': len(recent)
            }


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self._checks: Dict[str, bool] = {}
        self._last_check: Dict[str, float] = {}
    
    def add_check(self, name: str, check_func):
        """添加检查项"""
        self._checks[name] = check_func
    
    def run_all(self) -> Dict[str, Dict[str, Any]]:
        """运行所有检查"""
        results = {}
        now = time.time()
        
        for name, check_func in self._checks.items():
            try:
                status = check_func()
                results[name] = {
                    'status': 'healthy' if status else 'unhealthy',
                    'timestamp': now,
                    'latency_ms': 0
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': now
                }
            
            self._last_check[name] = now
        
        return results


class MonitorService:
    """监控服务"""
    
    def __init__(self, interval: float = 60.0):
        self.interval = interval
        self.collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self):
        """启动监控"""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print("📊 Monitor service started")
    
    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("📊 Monitor service stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                # 收集指标
                metrics = self._collect_metrics()
                if metrics:
                    self.collector.record(metrics)
                
                # 健康检查
                health = self.health_checker.run_all()
                
                time.sleep(self.interval)
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
    
    def _collect_metrics(self) -> Optional[Metrics]:
        """收集指标（由外部注入）"""
        # 这里需要外部提供数据源
        # 暂时返回None
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            'running': self._running,
            'metrics': self.collector.get_summary(),
            'health': self.health_checker.run_all()
        }


# 全局监控实例
monitor = MonitorService()
