"""
自进化交易系统 - 三平台版
- 实时数据收集（三平台：Bitget、HTX、Gate.io）
- 自动模式发现（按平台分别发现规律）
- 三个引擎交易总结（按平台分别总结回测、模拟盘、实盘）
- 阶段性策略升级
- 自适应风控调整
"""
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Optional, List

from .config import SystemConfig
from .data_collector import DataCollector
from .pattern_discovery import PatternDiscovery
from .trade_analyzer import TradeAnalyzer, AdaptiveRiskManager, PhaseUpgradeManager
from .execution_engine import ExecutionEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SelfEvolutionSystem')

class SelfEvolutionTradingSystem:
    """自进化交易系统 - 三平台并行，三引擎各自总结规律"""
    
    PLATFORMS = ['bitget', 'htx', 'gate']
    
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
        
        # 各平台独立策略
        self.exchange_strategies = {p: "fat_finger_arb" for p in self.PLATFORMS}
        
        # 状态
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
        
        # 打印连接状态
        statuses = self.collector.get_exchange_status()
        connected = [s['name'] for s in statuses if s['connected']]
        failed = [s['name'] for s in statuses if not s['connected']]
        
        logger.info("=" * 60)
        logger.info("🧬 自进化交易系统启动（三平台版）")
        logger.info(f"   分析目标: 三平台 × 三引擎（回测/模拟盘/实盘）")
        logger.info(f"   已连接平台: {', '.join(connected)}")
        if failed:
            logger.warning(f"   连接失败: {', '.join(failed)}")
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
                # 1. 收集实时数据（三平台并行）
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
                
                time.sleep(self.config.data.update_interval)
                
            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                time.sleep(5)
    
    def _analyze_and_adapt(self):
        """分析和自适应调整 - 按平台分别分析三引擎数据"""
        logger.info("📊 开始三平台三引擎数据分析...")
        
        # 1. 发现新模式（按平台）
        new_patterns = self.detector.analyze_all()
        
        # 2. 分析三个引擎的交易数据（按平台）
        per_exchange_analysis = {}
        for ex in self.PLATFORMS:
            ex_analysis = self.analyzer.analyze_all_modes(exchange=ex)
            per_exchange_analysis[ex] = ex_analysis
        
        # 3. 分析市场状态
        risk_status = self.risk_manager.get_current_risk_status()
        
        # 4. 按平台更新策略权重
        for ex in self.PLATFORMS:
            ex_patterns = [p for p in new_patterns if p.exchange == ex]
            if ex_patterns:
                self._update_exchange_strategy(ex, ex_patterns)
        
        # 5. 应用风控调整
        self._apply_risk_adjustments(risk_status)
        
        # 6. 打印状态
        self._log_status(per_exchange_analysis, risk_status)
    
    def _check_upgrade(self):
        """检查是否需要升级"""
        logger.info("🔄 检查三平台升级条件...")
        
        recommendation = self.upgrade_manager.get_upgrade_recommendation()
        
        logger.info(f"   当前阶段: {recommendation['phase']}")
        logger.info(f"   下一步: {recommendation['next_action']}")
        logger.info(f"   消息: {recommendation['message']}")
        
        details = recommendation.get('details', {})
        if details:
            logger.info(f"   数据点: {details.get('data_points', 0)}")
            logger.info(f"   模拟盘交易: {details.get('paper_trades', 0)}")
            logger.info(f"   实盘交易: {details.get('live_trades', 0)}")
            logger.info(f"   模拟盘胜率: {details.get('paper_win_rate', 0)*100:.1f}%")
            logger.info(f"   实盘胜率: {details.get('live_win_rate', 0)*100:.1f}%")
        
        if recommendation['phase'] == 'complete':
            self._execute_upgrade()
    
    def _execute_upgrade(self):
        """执行策略升级"""
        logger.info("⬆️ 执行策略升级...")
        
        snapshot = {
            'timestamp': datetime.utcnow().isoformat(),
            'strategies': dict(self.exchange_strategies),
            'weights': dict(self.config.strategy.strategies),
            'data_points': self.collector.total_ticks
        }
        
        self._load_best_strategy()
        logger.info(f"   ✅ 升级完成")
    
    def _load_best_strategy(self):
        """加载最优策略"""
        best_strategy, score = self.detector.get_best_strategy()
        if score > 0.1:
            for ex in self.PLATFORMS:
                self.exchange_strategies[ex] = best_strategy
    
    def _update_exchange_strategy(self, ex_name: str, patterns):
        """更新某个平台的策略权重"""
        for pattern in patterns:
            if pattern.pattern_type == "spread_arbitrage":
                self.config.strategy.strategies["fat_finger_arb"]["weight"] = \
                    min(pattern.confidence * pattern.profitability * 10, 1.0)
            elif pattern.pattern_type == "mean_reversion":
                self.config.strategy.strategies["mean_reversion"]["weight"] = \
                    min(pattern.confidence * 0.5, 1.0)
    
    def _apply_risk_adjustments(self, risk_status):
        """应用风控调整 - 自动修改阈值"""
        if risk_status['suspension_recommended']:
            logger.warning("⚠️ 极端市场状态，建议暂停交易")
            return
        
        adjustments = risk_status['risk_adjustments']
        position_mult = adjustments.get('position_size', 1.0)
        stop_loss_pct = adjustments.get('stop_loss_pct', 2.0)
        
        # 真正调整config中的参数（让自进化生效）
        if position_mult != 1.0:
            old_val = self.config.execution.spread_pct
            # 仓位倍数增大 → 灵敏度提高（阈值降低）
            self.config.execution.spread_pct = old_val / position_mult
            logger.info(f"   🧬 自进化调整: 仓位倍数={position_mult:.2f}x, spread阈值 {old_val:.4f}% → {self.config.execution.spread_pct:.4f}%")
        
        # 根据市场状态调整净利阈值
        market_regime = risk_status.get('market_regime', {}).get('regime', 'normal')
        if market_regime == 'volatile':
            old_net = self.config.execution.net_profit_pct
            self.config.execution.net_profit_pct = old_net * 0.5  # 高波动时降低灵敏度
            logger.info(f"   🧬 自进化调整: 波动市场, net阈值 {old_net:.4f}% → {self.config.execution.net_profit_pct:.4f}%")
        
        # 更新实际交易门槛日志
        actual_threshold = (self.risk_manager.MIN_NET_PROFIT_PCT + ExecutionEngine.BI_SIDE_COST) * 100
        logger.info(f"   风控调整: 仓位={position_mult}x 止损={stop_loss_pct}% | 实际门槛: 价差 > {actual_threshold:.2f}%")
    
    def _log_status(self, per_exchange_analysis: Dict, risk_status):
        """打印当前状态 - 按平台/引擎显示"""
        logger.info("=" * 60)
        logger.info("📈 三平台三引擎自进化系统状态")
        logger.info("=" * 60)
        logger.info(f"   数据收集: {self.collector.total_ticks} ticks")
        
        for ex in self.PLATFORMS:
            connector = self.collector.connectors.get(ex)
            if not connector or not connector.connected:
                continue
            
            ex_ticks = self.collector.ticks_per_exchange.get(ex, 0)
            logger.info("")
            logger.info(f"   🌐 {ex.upper()} ({ex_ticks} ticks)")
            logger.info(f"      策略: {self.exchange_strategies[ex]}")
            
            analysis = per_exchange_analysis.get(ex, {})
            bt = analysis.get('backtest', {})
            pp = analysis.get('paper', {})
            lv = analysis.get('live', {})
            
            logger.info(f"      📊 回测: {bt.get('total_trades', 0)}笔, 胜率{bt.get('win_rate', 0)*100:.1f}%")
            logger.info(f"      📊 模拟盘: {pp.get('total_trades', 0)}笔, 胜率{pp.get('win_rate', 0)*100:.1f}%")
            logger.info(f"      📊 实盘: {lv.get('total_trades', 0)}笔, 执行质量{lv.get('execution_quality', 'N/A')}")
        
        logger.info("")
        logger.info(f"   市场状态: {risk_status['market_regime']['regime']}")
        logger.info(f"   策略权重:")
        for name, params in self.config.strategy.strategies.items():
            if params['weight'] > 0:
                logger.info(f"     {name}: {params['weight']:.3f}")
        logger.info("=" * 60)
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        risk_status = self.risk_manager.get_current_risk_status()
        upgrade_rec = self.upgrade_manager.get_upgrade_recommendation()
        
        ex_status = {}
        for ex in self.PLATFORMS:
            c = self.collector.connectors.get(ex)
            ex_status[ex] = {
                'connected': c.connected if c else False,
                'ticks': self.collector.ticks_per_exchange.get(ex, 0),
                'strategy': self.exchange_strategies.get(ex, 'N/A')
            }
        
        return {
            'running': self.running,
            'total_ticks': self.collector.total_ticks,
            'exchanges': ex_status,
            'market_regime': risk_status['market_regime']['regime'],
            'upgrade_phase': upgrade_rec['phase'],
            'upgrade_next': upgrade_rec['next_action']
        }