"""
QNT量子交易系统 v2.0 - 主入口
核心：同平台跨厅捡乌龙指，永续开多+现货卖单，瞬间锁利
"""
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import sqlite3

sys.path.insert(0, str(Path(__file__).parent))
from strategies.oolong_index_v2 import OolongIndexStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QNT')

# 币种列表
MAIN_SYMBOLS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE']
SMALL_SYMBOLS = ['RVN', 'AXS', 'LINK', 'DOT', 'UNI', 'ATOM', 'MATIC', 'AVAX', 'LTC', 'BCH', 
                 'FIL', 'SAND', 'MANA', 'ALGO', 'XTZ', 'EGLD', 'FTM', 'ONE', 'ZEC', 'DASH']

def load_api_keys():
    """加载API密钥"""
    env_file = Path.home() / '.qnt_env'
    if not env_file.exists():
        logger.error(f"❌ API密钥文件不存在: {env_file}")
        return None
    
    for line in open(env_file):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    api_key = os.getenv('BITGET_API_KEY')
    api_secret = os.getenv('BITGET_API_SECRET')
    api_passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')
    
    if not api_key or not api_secret:
        logger.error("❌ API密钥加载失败")
        return None
    
    return {
        'key': api_key,
        'secret': api_secret,
        'passphrase': api_passphrase
    }

def scan_all_symbols(strategy, symbols):
    """扫描所有币种"""
    all_signals = []
    
    for sym in symbols:
        try:
            strategy.symbol = sym
            signals = strategy.detect_oolong_index()
            all_signals.extend(signals)
            
            if len(all_signals) % 5 == 0:
                logger.info(f"已扫描 {len(all_signals)} 个币种...")
                
        except Exception as e:
            logger.debug(f"扫描{sym}失败: {e}")
        
        time.sleep(0.05)
    
    return all_signals

def run_scan():
    """运行扫描"""
    logger.info("\n" + "=" * 70)
    logger.info("  QNT量子交易系统 v2.0 - 捡乌龙指扫描")
    logger.info("=" * 70)
    logger.info("\n核心逻辑：同平台跨厅对冲")
    logger.info("永续开多 + 现货卖单 → 瞬间锁利 → 不持仓\n")
    
    strategy = OolongIndexStrategy()
    
    # 扫描主流币
    logger.info("🔍 扫描主流币种...")
    main_signals = scan_all_symbols(strategy, MAIN_SYMBOLS)
    
    # 扫描小币种
    logger.info("🔍 扫描冷门币种...")
    small_signals = scan_all_symbols(strategy, SMALL_SYMBOLS)
    
    # 汇总
    all_signals = main_signals + small_signals
    all_signals.sort(key=lambda x: x.net_profit_pct, reverse=True)
    
    if all_signals:
        logger.info(f"\n🎯 发现 {len(all_signals)} 个机会!\n")
        for s in all_signals[:10]:
            emoji = "🎯" if s.net_profit_pct > 1.0 else "  "
            print(f"{emoji} {s.symbol:<8} | {s.buy_exchange:<12}买@{s.buy_price:.6f} → {s.sell_exchange:<12}卖@{s.sell_price:.6f} | 净利{s.net_profit_pct:.4f}%")
    else:
        logger.info("✅ 当前没有异常价差机会")
    
    strategy.close()
    
    logger.info("\n" + "=" * 70)
    return all_signals

def run_monitor(interval=30):
    """实时监控"""
    logger.info(f"\n🔄 启动实时监控 (间隔{interval}秒)")
    logger.info("按 Ctrl+C 停止\n")
    
    last_signals = set()
    
    try:
        while True:
            current_time = time.time()
            strategy = OolongIndexStrategy()
            
            all_signals = scan_all_symbols(strategy, MAIN_SYMBOLS + SMALL_SYMBOLS)
            
            for s in all_signals:
                sig_id = f"{s.symbol}_{s.buy_price}_{s.sell_price}"
                if sig_id not in last_signals:
                    logger.info(f"🎯 {s.symbol}: {s.buy_exchange}买@{s.buy_price:.6f} → {s.sell_exchange}卖@{s.sell_price:.6f} 净利{s.net_profit_pct:.4f}%")
                    last_signals.add(sig_id)
            
            strategy.close()
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        logger.info("\n👋 监控已停止")

def show_status():
    """显示账户状态"""
    logger.info("\n" + "=" * 70)
    logger.info("  当前账户状态")
    logger.info("=" * 70)
    
    try:
        strategy = OolongIndexStrategy()
        balance = strategy.bitget.fetch_balance()
        
        btc_hold = float(balance.get('BTC', {}).get('total', 0))
        eth_hold = float(balance.get('ETH', {}).get('total', 0))
        usdt_hold = float(balance.get('USDT', {}).get('total', 0))
        
        btc_price = float(strategy.bitget.fetch_ticker('BTC/USDT')['last'])
        eth_price = float(strategy.bitget.fetch_ticker('ETH/USDT')['last'])
        
        total = btc_hold * btc_price + eth_hold * eth_price + usdt_hold
        
        print(f"\nBTC: {btc_hold} ≈ ${btc_hold * btc_price:.2f}")
        print(f"ETH: {eth_hold} ≈ ${eth_hold * eth_price:.2f}")
        print(f"USDT: ${usdt_hold:.2f}")
        print(f"总计: ${total:.2f}")
        
        strategy.close()
    except Exception as e:
        logger.error(f"获取账户状态失败: {e}")

def show_help():
    """显示帮助"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         QNT量子交易系统 v2.0 - 捡乌龙指               ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  核心逻辑:                                               ║
║    1. 同平台操作（不能跨平台）                            ║
║    2. 永续开多 + 现货卖单                                ║
║    3. 不等价格恢复，瞬间锁利                             ║
║    4. 不持仓过夜                                         ║
║                                                          ║
║  命令:                                                   ║
║    scan     - 单次扫描所有币种                           ║
║    monitor  - 实时监控                                   ║
║    status   - 查看账户状态                               ║
║    help     - 显示帮助                                   ║
║                                                          ║
║  风险管理:                                               ║
║    单笔止损 ≤ 2%本金                                     ║
║    单品种仓位 ≤ 20%本金                                  ║
║    盈利取出 50% 永不回流                                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='QNT量子交易系统')
    parser.add_argument('command', nargs='?', default='scan',
                        choices=['scan', 'monitor', 'status', 'help'])
    parser.add_argument('--interval', type=int, default=30,
                        help='监控间隔（秒）')
    
    args = parser.parse_args()
    
    # 加载API密钥
    api_keys = load_api_keys()
    if not api_keys:
        sys.exit(1)
    
    # 执行命令
    if args.command == 'help':
        show_help()
    elif args.command == 'scan':
        run_scan()
    elif args.command == 'monitor':
        run_monitor(args.interval)
    elif args.command == 'status':
        show_status()

if __name__ == '__main__':
    main()
