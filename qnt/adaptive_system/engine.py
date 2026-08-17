"""
自适应策略引擎（三平台版）
整合数据收集、模式发现、策略执行，支持 Bitget/HTX/Gate 三平台并行
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AdaptiveSystem')

class AdaptiveTradingEngine:
    """自适应交易引擎（三平台版）"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.running = False
        self.thread = None
        
        # 初始化组件
        self.collector = DataCollector(self.config)
        self.detector = PatternDiscovery(self.config)
        
        # 各平台独立策略
        self.exchange_strategies = {
            'bitget': 'fat_finger_arb',
            'htx': 'fat_finger_arb',
            'gate': 'fat_finger_arb',
        }
        
        # 状态
        self.last_analysis_time = 0
        self.analysis_interval = 300  # 每5分钟分析一次
    
    def start(self):
        """启动自适应引擎"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        # 打印连接状态
        statuses = self.collector.get_exchange_status()
        connected = [s['name'] for s in statuses if s['connected']]
        failed = [s['name'] for s in statuses if not s['connected']]
        
        logger.info("=" * 60)
        logger.info("🚀 自适应策略引擎启动（三平台版）")
        logger.info(f"   监控币种: {', '.join(self.config.data.symbols)}")
        logger.info(f"   数据收集: 每{self.config.data.update_interval}秒")
        logger.info(f"   策略分析: 每{self.analysis_interval}秒")
        logger.info(f"   已连接: {', '.join(connected)}")
        if failed:
            logger.warning(f"   连接失败: {', '.join(failed)}")
        logger.info("=" * 60)
    
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
                # 收集数据（三平台并行）
                ticks = self.collector.collect_tick()
                
                # 定期分析
                now = time.time()
                if now - self.last_analysis_time > self.analysis_interval:
                    self._analyze_and_adapt()
                    self.last_analysis_time = now
                
                time.sleep(self.config.data.update_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                time.sleep(5)
    
    def _analyze_and_adapt(self):
        """分析和自适应调整"""
        logger.info("📊 开始三平台策略分析...")
        
        # 发现新模式（按平台）
        new_patterns = self.detector.analyze_all()
        
        # 按平台更新策略
        for ex_name in ['bitget', 'htx', 'gate']:
            ex_patterns = [p for p in new_patterns if p.exchange == ex_name]
            if ex_patterns:
                self._update_exchange_strategy(ex_name, ex_patterns)
        
        # 打印状态
        self._log_status()
    
    def _update_exchange_strategy(self, ex_name: str, patterns: List[DiscoveredPattern]):
        """更新某个平台的策略权重"""
        for pattern in patterns:
            if pattern.pattern_type == "spread_arbitrage":
                score = min(pattern.confidence * pattern.profitability * 10, 1.0)
                self.config.strategy.strategies["fat_finger_arb"]["weight"] = max(
                    self.config.strategy.strategies["fat_finger_arb"]["weight"], score
                )
            elif pattern.pattern_type == "market_maker":
                score = min(pattern.confidence * pattern.profitability * 10, 1.0)
                self.config.strategy.strategies["market_maker"]["weight"] = max(
                    self.config.strategy.strategies["market_maker"]["weight"], score
                )
    
    def _log_status(self):
        """打印当前状态"""
        stats = self.collector.get_all_statistics()
        statuses = self.collector.get_exchange_status()
        
        logger.info("=" * 60)
        logger.info("📈 三平台自适应引擎状态")
        logger.info(f"   总数据点数: {self.collector.total_ticks}")
        
        for s in statuses:
            ex_name = s['name']
            ex_ticks = self.collector.ticks_per_exchange.get(ex_name, 0)
            icon = "✅" if s['connected'] else "❌"
            logger.info(f"   {icon} {ex_name}: {ex_ticks} ticks")
            
            # 显示各币种价差
            if ex_name in stats:
                for sym, data in stats[ex_name].items():
                    logger.info(f"      {sym}: 价差均值={data['spread_mean']:.4f}%, 最大={data['spread_max']:.4f}%")
        
        logger.info(f"   策略权重:")
        for name, params in self.config.strategy.strategies.items():
            if params['weight'] > 0:
                logger.info(f"     {name}: weight={params['weight']:.3f}")
        logger.info("=" * 60)
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'running': self.running,
            'total_ticks': self.collector.total_ticks,
            'exchanges': {
                ex_name: {
                    'connected': c.connected,
                    'ticks': self.collector.ticks_per_exchange.get(ex_name, 0),
                    'strategy': self.exchange_strategies.get(ex_name, 'N/A')
                }
                for ex_name, c in self.collector.connectors.items()
            },
            'strategies': {
                name: {'weight': params['weight'], 'description': params['description']}
                for name, params in self.config.strategy.strategies.items()
            }
        }