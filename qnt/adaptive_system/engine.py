"""
自适应策略引擎
整合数据收集、模式发现、策略执行
"""
import time
import threading
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .config import SystemConfig
from .data_collector import DataCollector
from .pattern_discovery import PatternDiscovery
from .models import MarketDataPoint, DiscoveredPattern

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AdaptiveSystem')

class AdaptiveTradingEngine:
    """自适应交易引擎"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.running = False
        self.thread = None
        
        # 初始化组件
        self.collector = DataCollector(self.config)
        self.detector = PatternDiscovery(self.config)
        
        # 状态
        self.current_strategy = "fat_finger_arb"
        self.last_analysis_time = 0
        self.analysis_interval = 300  # 每5分钟分析一次
    
    def start(self):
        """启动自适应引擎"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("🚀 自适应策略引擎启动")
        logger.info(f"   监控币种: {', '.join(self.config.data.symbols)}")
        logger.info(f"   数据收集: 每{self.config.data.update_interval}秒")
        logger.info(f"   策略分析: 每{self.analysis_interval}秒")
    
    def stop(self):
        """停止引擎"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        self.collector.close()
        self.detector.close()
        logger.info("🛑 自适应引擎已停止")
    
    def _run_loop(self):
        """主循环"""
        while self.running:
            try:
                # 收集数据
                ticks = self.collector.collect_tick()
                
                # 定期分析
                now = time.time()
                if now - self.last_analysis_time > self.analysis_interval:
                    self._analyze_and_adapt()
                    self.last_analysis_time = now
                
                # 休眠
                time.sleep(self.config.data.update_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                time.sleep(5)
    
    def _analyze_and_adapt(self):
        """分析和自适应调整"""
        logger.info("📊 开始策略分析...")
        
        # 发现新模式
        new_patterns = self.detector.analyze_all()
        
        # 更新策略权重
        self._update_strategy_weights(new_patterns)
        
        # 选择最优策略
        best_strategy, score = self.detector.get_best_strategy()
        
        # 如果新策略明显更好，切换
        if score > 0.1 and best_strategy != self.current_strategy:
            old = self.current_strategy
            self.current_strategy = best_strategy
            logger.info(f"🔄 策略切换: {old} → {best_strategy} (score={score:.3f})")
        
        # 打印当前状态
        self._log_status()
    
    def _update_strategy_weights(self, patterns: List[DiscoveredPattern]):
        """根据发现的模式更新策略权重"""
        for pattern in patterns:
            if pattern.pattern_type == "spread_arbitrage":
                # 价差套利策略
                self.config.strategy.strategies["fat_finger_arb"]["weight"] = \
                    min(pattern.confidence * pattern.profitability * 10, 1.0)
                self.config.strategy.strategies["fat_finger_arb"]["params"]["profitability"] = \
                    pattern.profitability
            
            elif pattern.pattern_type == "mean_reversion":
                # 均值回归策略
                self.config.strategy.strategies["mean_reversion"]["weight"] = \
                    min(pattern.confidence * 0.5, 1.0)
    
    def _log_status(self):
        """打印当前状态"""
        logger.info("=" * 60)
        logger.info("📈 自适应引擎状态")
        logger.info(f"   当前策略: {self.current_strategy}")
        logger.info(f"   数据收集: {self.collector.total_ticks} ticks")
        logger.info(f"   策略权重:")
        for name, params in self.config.strategy.strategies.items():
            logger.info(f"     {name}: weight={params['weight']:.3f}")
        logger.info("=" * 60)
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'running': self.running,
            'current_strategy': self.current_strategy,
            'total_ticks': self.collector.total_ticks,
            'strategies': {
                name: {
                    'weight': params['weight'],
                    'description': params['description']
                }
                for name, params in self.config.strategy.strategies.items()
            }
        }
