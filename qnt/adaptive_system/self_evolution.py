"""
自进化交易系统 - 整合版
- 实时数据收集
- 自动模式发现
- 模拟盘交易总结
- 实盘交易总结
- 阶段性策略升级
- 自适应风控调整
"""
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Optional

from .config import SystemConfig
from .data_collector import DataCollector
from .pattern_discovery import PatternDiscovery
from .trade_analyzer import TradeAnalyzer, AdaptiveRiskManager, PhaseUpgradeManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SelfEvolutionSystem')

class SelfEvolutionTradingSystem:
    """自进化交易系统 - 全链路自动学习"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.running = False
        self.thread = None
        
        # 初始化各模块
        self.collector = DataCollector(self.config)
        self.detector = PatternDiscovery(self.config)
        self.analyzer = TradeAnalyzer(self.config.data.db_path)
        self.risk_manager = AdaptiveRiskManager(self.config.data.db_path)
        self.upgrade_manager = PhaseUpgradeManager(self.config.data.db_path)
        
        # 状态
        self.current_strategy = "fat_finger_arb"
        self.current_phase = "data_collection"
        self.last_analysis_time = 0
        self.last_upgrade_check = 0
        self.analysis_interval = 300  # 5分钟分析一次
        self.upgrade_interval = 3600  # 1小时检查升级
    
    def start(self):
        """启动自进化系统"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("=" * 60)
        logger.info("🧬 自进化交易系统启动")
        logger.info("=" * 60)
        logger.info(f"   监控币种: {len(self.config.data.symbols)} 个")
        logger.info(f"   数据收集: 每{self.config.data.update_interval}秒")
        logger.info(f"   策略分析: 每{self.analysis_interval}秒")
        logger.info(f"   升级检查: 每{self.upgrade_interval}秒")
        logger.info("=" * 60)
    
    def stop(self):
        """停止系统"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        self.collector.close()
        self.detector.close()
        self.analyzer.conn.close()
        self.risk_manager.conn.close()
        self.upgrade_manager.conn.close()
        logger.info("🛑 自进化系统已停止")
    
    def _run_loop(self):
        """主循环"""
        while self.running:
            try:
                # 1. 收集实时数据
                ticks = self.collector.collect_tick()
                
                # 2. 定期分析
                now = time.time()
                if now - self.last_analysis_time > self.analysis_interval:
                    self._analyze_and_adapt()
                    self.last_analysis_time = now
                
                # 3. 定期检查升级
                if now - self.last_upgrade_check > self.upgrade_interval:
                    self._check_upgrade()
                    self.last_upgrade_check = now
                
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
        logger.info("📊 开始全链路分析...")
        
        # 1. 发现新模式
        new_patterns = self.detector.analyze_all()
        
        # 2. 分析交易总结（模拟盘+实盘）
        sim_analysis = self.analyzer.analyze_simulated_trades(24)
        live_analysis = self.analyzer.analyze_live_trades(24)
        
        # 3. 分析市场状态
        risk_status = self.risk_manager.get_current_risk_status()
        
        # 4. 更新策略权重
        self._update_strategy_weights(new_patterns)
        
        # 5. 应用风控调整
        self._apply_risk_adjustments(risk_status)
        
        # 6. 打印状态
        self._log_status(sim_analysis, live_analysis, risk_status)
    
    def _check_upgrade(self):
        """检查是否需要升级"""
        logger.info("🔄 检查阶段升级...")
        
        recommendation = self.upgrade_manager.get_upgrade_recommendation()
        
        logger.info(f"   当前阶段: {recommendation['phase']}")
        logger.info(f"   下一步: {recommendation['next_action']}")
        logger.info(f"   消息: {recommendation['message']}")
        
        # 如果建议升级，执行升级
        if recommendation['phase'] == 'complete':
            self._execute_upgrade()
    
    def _execute_upgrade(self):
        """执行策略升级"""
        logger.info("⬆️ 执行策略升级...")
        
        # 1. 保存当前策略快照
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'strategy': self.current_strategy,
            'weights': dict(self.config.strategy.strategies),
            'data_points': self.collector.total_ticks
        }
        
        # 2. 加载最优策略组合
        self._load_best_strategy()
        
        # 3. 记录升级事件
        logger.info(f"   ✅ 升级完成")
        logger.info(f"   📸 快照已保存")
    
    def _load_best_strategy(self):
        """加载最优策略"""
        best_strategy, score = self.detector.get_best_strategy()
        
        if score > 0.1 and best_strategy != self.current_strategy:
            logger.info(f"   🔄 切换策略: {self.current_strategy} → {best_strategy}")
            self.current_strategy = best_strategy
    
    def _update_strategy_weights(self, patterns):
        """根据新模式更新策略权重"""
        for pattern in patterns:
            if pattern.pattern_type == "spread_arbitrage":
                self.config.strategy.strategies["fat_finger_arb"]["weight"] = \
                    min(pattern.confidence * pattern.profitability * 10, 1.0)
            
            elif pattern.pattern_type == "mean_reversion":
                self.config.strategy.strategies["mean_reversion"]["weight"] = \
                    min(pattern.confidence * 0.5, 1.0)
    
    def _apply_risk_adjustments(self, risk_status):
        """应用风控调整"""
        if risk_status['suspension_recommended']:
            logger.warning("⚠️ 极端市场状态，建议暂停交易")
        else:
            adjustments = risk_status['risk_adjustments']
            logger.info(f"   风控调整: 仓位={adjustments.get('position_size', 1.0)}x "
                       f"止损={adjustments.get('stop_loss_pct', 2.0)}%")
    
    def _log_status(self, sim_analysis, live_analysis, risk_status):
        """打印当前状态"""
        logger.info("=" * 60)
        logger.info("📈 自进化系统状态")
        logger.info("=" * 60)
        logger.info(f"   当前策略: {self.current_strategy}")
        logger.info(f"   数据收集: {self.collector.total_ticks} ticks")
        logger.info(f"   模拟盘分析: {sim_analysis.get('total_trades', 0)} trades, "
                   f"胜率{sim_analysis.get('win_rate', 0)*100:.1f}%")
        logger.info(f"   实盘分析: {live_analysis.get('total_trades', 0)} trades")
        logger.info(f"   市场状态: {risk_status['market_regime']['regime']}")
        logger.info(f"   策略权重:")
        for name, params in self.config.strategy.strategies.items():
            if params['weight'] > 0:
                logger.info(f"     {name}: {params['weight']:.3f}")
        logger.info("=" * 60)
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        sim_analysis = self.analyzer.analyze_simulated_trades(24)
        live_analysis = self.analyzer.analyze_live_trades(24)
        risk_status = self.risk_manager.get_current_risk_status()
        upgrade_rec = self.upgrade_manager.get_upgrade_recommendation()
        
        return {
            'running': self.running,
            'current_strategy': self.current_strategy,
            'total_ticks': self.collector.total_ticks,
            'sim_trades': sim_analysis.get('total_trades', 0),
            'live_trades': live_analysis.get('total_trades', 0),
            'market_regime': risk_status['market_regime']['regime'],
            'upgrade_phase': upgrade_rec['phase'],
            'upgrade_next': upgrade_rec['next_action']
        }
