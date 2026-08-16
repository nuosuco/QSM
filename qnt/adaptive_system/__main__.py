"""允许通过 python -m adaptive_system 运行（三平台版）"""
import sys
sys.path.insert(0, '/root/SOM/qnt')
from adaptive_system.engine import AdaptiveTradingEngine

if __name__ == "__main__":
    engine = AdaptiveTradingEngine()
    engine.start()
    try:
        import time
        while True:
            time.sleep(60)
            status = engine.get_status()
            exchanges = status.get('exchanges', {})
            conn_count = sum(1 for ex in exchanges.values() if ex.get('connected'))
            print(f"自适应引擎运行中... 连接{conn_count}个平台, ticks={status['total_ticks']}")
    except KeyboardInterrupt:
        engine.stop()
        print("引擎已停止")