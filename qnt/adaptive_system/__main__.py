"""
自适应进化交易系统 - 主入口（三引擎 + 自进化）
铁律：
1. 回测、模拟必须真实运行，完整BUY+SELL周期
2. 回测+模拟盈利后才能开实盘
3. 风控层层收紧，自适应进化
"""
import sys
import os
import signal
import time
from datetime import datetime
sys.path.insert(0, '/root/SOM/qnt')

from adaptive_system.config import SystemConfig
from adaptive_system.dual_engine import DualEngineSystem, BacktestEngine, PaperEngine
from adaptive_system.execution_engine import ExecutionEngine
from adaptive_system.live_trading_controller import LiveTradingController
from adaptive_system.evolution_manager import EvolutionManager
from adaptive_system.data_collector import DataCollector
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('/root/SOM/qnt/evolution_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AdaptiveEvolutionSystem')


class AdaptiveEvolutionSystem:
    """
    自适应进化交易系统 - 完整版
    
    架构：
    - BacktestEngine: 历史数据回放 + 实时追加回测（完整BUY+SELL周期）
    - PaperEngine: 实时模拟交易（完整BUY+SELL周期，真实风控检查）
    - ExecutionEngine: 实盘执行（受LiveTradingController控制）
    - LiveTradingController: 实盘自动开关（根据模拟盘表现自动决定）
    - EvolutionManager: 策略自进化管理器（分析交易记录，优化策略参数）
    """

    def __init__(self, config: SystemConfig):
        self.config = config
        
        # 启动双引擎（回测 + 模拟）
        logger.info("=" * 70)
        logger.info("🚀 自适应进化交易系统 v1.0 启动")
        logger.info("=" * 70)
        
        self.dual_engine = DualEngineSystem(config)
        self.dual_engine.start()
        
        # 启动实盘执行引擎（初始状态：未启用）
        self.exec_engine = ExecutionEngine(config)
        
        # 启动实盘自动开关控制器
        self.live_controller = LiveTradingController(
            config, config.data.db_path, self.dual_engine, self.exec_engine
        )
        self.live_controller.start()
        
        # 启动自进化管理器（每24小时分析一次）
        self.evolution_manager = EvolutionManager(config.data.db_path, config)
        
        # 启动数据收集器（三平台并行采集）
        self.data_collector = DataCollector(config)
        self.data_collector.start()
        
        logger.info("✅ 系统初始化完成")
        logger.info("📊 铁律确认:")
        logger.info("   1. 回测 + 模拟 真实运行，完整BUY+SELL周期")
        logger.info("   2. 只有回测+模拟盈利后，才能开启实盘")
        logger.info("   3. 实盘由LiveTradingController自动控制")
        logger.info("   4. 每24小时自进化分析，优化策略参数")
        logger.info("=" * 70)

    def run(self):
        """主运行循环"""
        last_evolution_time = time.time()
        last_status_time = time.time()
        evolution_interval = 86400  # 24小时
        status_interval = 60       # 1分钟
        
        try:
            while True:
                now = time.time()
                
                # 每分钟打印状态
                if now - last_status_time >= status_interval:
                    self._print_status()
                    last_status_time = now
                
                # 每24小时执行一次进化分析
                if now - last_evolution_time >= evolution_interval:
                    self._run_evolution()
                    last_evolution_time = now
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 收到停止信号，正在关闭系统...")
            self.stop()
            
    def _print_status(self):
        """打印系统状态"""
        logger.info("=" * 70)
        logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 自适应进化交易系统 v1.0")
        logger.info("=" * 70)
        
        # 双引擎状态
        dual_status = self.dual_engine.get_status()
        bt = dual_status.get('backtest', {})
        pp = dual_status.get('paper', {})
        
        logger.info(f"📊 回测引擎:")
        logger.info(f"   交易数: {bt.get('total_trades', 0)} 笔")
        logger.info(f"   胜率: {bt.get('win_rate', 0)*100:.1f}%")
        logger.info(f"   总盈亏: ${bt.get('total_pnl', 0):+.2f} U")
        
        logger.info(f"📝 模拟引擎:")
        logger.info(f"   余额: ${pp.get('balance', 0):.2f} U")
        logger.info(f"   交易数: {pp.get('total_trades', 0)} 笔")
        logger.info(f"   胜率: {pp.get('win_rate', 0)*100:.1f}%")
        logger.info(f"   总盈亏: ${pp.get('total_pnl', 0):+.2f} U")
        logger.info(f"   持仓: {pp.get('open_positions', 0)} 个")
        
        # 实盘状态
        lc_status = self.live_controller.get_status()
        logger.info(f"🎛️ 实盘控制器:")
        logger.info(f"   状态: {'✅ 已开启' if lc_status['live_enabled'] else '🔒 已关闭'}")
        if lc_status['suspension_reasons']:
            logger.info(f"   原因: {'; '.join(lc_status['suspension_reasons'])}")
        
        # 进化状态
        ev_status = self.evolution_manager.get_status()
        logger.info(f"🧬 自进化:")
        logger.info(f"   进化次数: {ev_status['evolution_count']}")
        logger.info(f"   上次分析: {ev_status['last_analysis']}")
        
        logger.info("=" * 70)
        
    def _run_evolution(self):
        """执行一次自进化分析"""
        logger.info("🧬 开始执行自进化分析...")
        
        try:
            report = self.evolution_manager.analyze_and_evolve()
            
            # 如果有紧急停止建议，立即执行
            for action in report.get('actions', []):
                if action.get('type') == 'emergency_stop':
                    logger.critical(f"🔴 {action['message']}")
                    # 立即停止实盘
                    self.live_controller._disable_live()
                    break
            
            # 如果有参数变更建议，等待下次循环自动应用
            
        except Exception as e:
            logger.error(f"自进化分析失败: {e}")

    def stop(self):
        """停止所有引擎"""
        logger.info("🛑 正在停止所有引擎...")
        
        self.live_controller.stop()
        self.dual_engine.stop()
        
        if self.exec_engine and self.exec_engine.running:
            self.exec_engine.stop()
        
        logger.info("✅ 系统已完全停止")


def main():
    """主函数"""
    # 加载环境变量
    import subprocess
    result = subprocess.run(['bash', '-c', 'source ~/.bashrc && env | grep -E "(BITGET|HTX|GATE)_API"'], 
                          capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if '=' in line:
            key, val = line.split('=', 1)
            os.environ[key] = val
    
    # 加载配置
    config = SystemConfig()
    config.load_api_keys()
    
    # 创建系统
    system = AdaptiveEvolutionSystem(config)
    
    # 运行
    system.run()


if __name__ == "__main__":
    main()
