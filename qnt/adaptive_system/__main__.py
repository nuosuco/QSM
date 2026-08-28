"""允许通过 python -m adaptive_system 运行（三平台版 + 双引擎 + 自进化）"""
import sys
from datetime import datetime
sys.path.insert(0, '/root/SOM/qnt')
from adaptive_system.engine import AdaptiveTradingEngine
from adaptive_system.execution_engine import ExecutionEngine
from adaptive_system.self_evolution import SelfEvolutionTradingSystem
from adaptive_system.dual_engine import DualEngineSystem
from adaptive_system.live_trading_controller import LiveTradingController

if __name__ == "__main__":
    # 加载API密钥
    import subprocess
    result = subprocess.run(['bash', '-c', 'source ~/.bashrc && env | grep -E "(BITGET|HTX|GATE)_API"'], 
                          capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if '=' in line:
            key, val = line.split('=', 1)
            import os
            os.environ[key] = val
    
    from adaptive_system.config import SystemConfig
    config = SystemConfig()
    config.load_api_keys()
    
    # 启动双引擎（回测 + 模拟，不受暂停影响）
    dual_engine = DualEngineSystem(config)
    dual_engine.start()
    
    # 启动自进化引擎（数据采集+模式发现+自动调整）
    evolution = SelfEvolutionTradingSystem(config)
    evolution.start()
    
    # 启动交易执行引擎（含风控）
    exec_engine = ExecutionEngine(config)
    exec_engine.start()
    
    # 启动实盘自动开关控制器
    live_controller = LiveTradingController(
        config, config.data.db_path, dual_engine, exec_engine
    )
    live_controller.start()
    
    try:
        import time
        last_status = 0
        while True:
            time.sleep(1)
            now = time.time()
            
            # 每分钟打印状态
            if now - last_status > 60:
                print(f"\n{'='*60}")
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 三平台版本 v2.0")
                print(f"{'='*60}")
                
                # 执行引擎状态
                exec_status = exec_engine.get_status()
                risk = exec_status.get('risk', {})
                print(f"💰 权益: ${risk.get('equity', 0):.2f}")
                print(f"📈 实盘PnL: ${risk.get('total_profit', 0):+.2f}")
                print(f"🛑 暂停: {risk.get('is_suspended', False)} {risk.get('suspension_reason', '')}")
                
                # 双引擎状态
                dual_status = dual_engine.get_status()
                bt = dual_status.get('backtest', {})
                pp = dual_status.get('paper', {})
                print(f"📊 回测: {bt.get('total_trades', 0)}笔, 胜率{bt.get('win_rate', 0)*100:.1f}%")
                print(f"📝 模拟: 余额${pp.get('balance', 0):.2f}, PnL${pp.get('total_pnl', 0):+.2f}")
                
                # 自进化状态
                print(f"📊 ticks: {evolution.collector.total_ticks}")
                print(f"🧬 阶段: {evolution.current_phase}")
                
                # 实盘开关状态
                lc = live_controller.get_status()
                print(f"🎛️ 实盘: {'✅已开' if lc['live_enabled'] else '🔒已关'} | 原因: {lc['suspension_reasons'] or '无'}")
                print(f"{'='*60}")
                last_status = now
                
    except KeyboardInterrupt:
        live_controller.stop()
        dual_engine.stop()
        evolution.stop()
        exec_engine.stop()
        print("\n🛑 引擎已停止")
