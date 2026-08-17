"""
记忆承载·碧树西风交易系统 - 主入口
用法:
  python main.py --mode backtest    # 回测模式
  python main.py --mode paper       # 模拟盘
  python main.py --mode live        # 实盘（需API配置）
  python main.py --mode scan        # 扫描模式
"""
import argparse
import sys
import os

# 添加父目录到路径
sys.path.insert(0, '/root/SOM/qnt')

from trading_system.config import SystemConfig
from trading_system.engine import TradingEngine
from trading_system.run_backtest import main as run_backtest


def main():
    parser = argparse.ArgumentParser(description='记忆承载·碧树西风交易系统')
    parser.add_argument('--mode', choices=['backtest', 'paper', 'live', 'scan'],
                        default='backtest', help='运行模式')
    parser.add_argument('--config', default=None, help='配置文件路径')
    
    args = parser.parse_args()
    
    # 加载配置
    config = SystemConfig()
    config.load_api_keys()
    
    if args.mode == 'backtest':
        run_backtest()
    elif args.mode == 'scan':
        engine = TradingEngine(config)
        engine.start(mode='scan')
    elif args.mode == 'live':
        # 检查API配置
        if not os.getenv('BITGET_API_KEY'):
            print("❌ 请先配置Bitget API密钥")
            print("在 ~/.qnt_env 中添加:")
            print("  BITGET_API_KEY=xxx")
            print("  BITGET_API_SECRET=xxx")
            print("  BITGET_API_PASSPHRASE=xxx")
            sys.exit(1)
        
        # 切换到实盘模式
        config.exchanges['bitget'].testnet = False
        engine = TradingEngine(config)
        engine.start(mode='live')
    elif args.mode == 'paper':
        config.exchanges['bitget'].testnet = True
        engine = TradingEngine(config)
        engine.start(mode='paper')
    
    print("\n运行完成!")


if __name__ == "__main__":
    main()