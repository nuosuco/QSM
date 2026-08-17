"""允许通过 python -m adaptive_system 运行（三平台版 + 交易执行 + 自进化）"""
import sys
sys.path.insert(0, '/root/SOM/qnt')
from adaptive_system.engine import AdaptiveTradingEngine
from adaptive_system.execution_engine import ExecutionEngine
from adaptive_system.self_evolution import SelfEvolutionTradingSystem

if __name__ == "__main__":
    # 加载API密钥 - 先source bashrc确保环境变量可用
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
    
    # 启动自进化引擎（数据采集+模式发现+自动调整）
    evolution = SelfEvolutionTradingSystem(config)
    evolution.start()
    
    # 启动交易执行引擎（含风控）
    exec_engine = ExecutionEngine(config)
    exec_engine.start()
    
    try:
        import time
        last_status = 0
        while True:
            time.sleep(1)
            now = time.time()
            
            # 每分钟打印状态
            if now - last_status > 60:
                status = exec_engine.get_status()
                risk = status.get('risk', {})
                print(f"\n{'='*50}")
                print(f"⏰ 状态 | 连接{status.get('exchanges', [])}")
                print(f"💰 权益: ${risk.get('equity', 0):.2f}")
                print(f"📈 累计PnL: ${risk.get('total_profit', 0):+.2f}")
                print(f"🛑 暂停: {risk.get('is_suspended', False)} {risk.get('suspension_reason', '')}")
                print(f"📊 ticks: {evolution.collector.total_ticks}")
                print(f"🧬 阶段: {evolution.current_phase}")
                print(f"{'='*50}")
                last_status = now
    except KeyboardInterrupt:
        evolution.stop()
        exec_engine.stop()
        print("引擎已停止")
