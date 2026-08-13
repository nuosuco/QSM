"""
交易系统主入口
基于碧树西风16年高频量化交易经验
"""

import sqlite3
from datetime import datetime
from config.settings import DB_PATH, CORE_PRINCIPLES
from core.principles import TradingPrinciples
from strategies.patterns import get_strategy, STRATEGY_REGISTRY
import json

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 记忆承载交易系统 - Phase 1")
    print("=" * 60)
    
    # 1. 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2. 打印核心原则
    print("\n【一、核心交易原则】")
    TradingPrinciples.print_all()
    
    # 3. 显示可用策略
    print("\n【二、可用策略】")
    for name, cls in STRATEGY_REGISTRY.items():
        print(f"   • {name}: {cls.__doc__}")
    
    # 4. 统计数据库内容
    print("\n【三、数据库统计】")
    cursor.execute("SELECT COUNT(*) FROM strategies")
    print(f"   策略数: {cursor.fetchone()[0]}条")
    
    cursor.execute("SELECT COUNT(*) FROM trading_keywords")
    print(f"   关键词: {cursor.fetchone()[0]}个")
    
    cursor.execute("SELECT COUNT(*) FROM platform_configs")
    print(f"   平台配置: {cursor.fetchone()[0]}个")
    
    # 5. 测试策略
    print("\n【四、测试趋势跟踪策略】")
    strategy = get_strategy('trend_following')
    
    # 模拟数据
    test_data = [
        {'close': 100, 'volume': 1000, 'ma_20': 98, 'ma_50': 95, 'datetime': '2026-08-13'},
        {'close': 102, 'volume': 1200, 'ma_20': 99, 'ma_50': 96, 'datetime': '2026-08-14'},
        {'close': 105, 'volume': 1500, 'ma_20': 100, 'ma_50': 97, 'datetime': '2026-08-15'},
    ]
    
    for data in test_data:
        signal = strategy.generate_signal(data)
        print(f"   [{data['datetime']}] {signal['action']}: {signal['reason']}")
    
    # 6. 保存策略
    strategy.save_to_db(conn)
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 交易系统Phase 1基础框架完成！")
    print("=" * 60)
    print("\n【下一步】")
    print("   1. 准备历史数据")
    print("   2. 进行回测验证")
    print("   3. 优化策略参数")
    print("   4. 模拟盘测试")
    print("   5. 小资金实盘")

if __name__ == '__main__':
    main()
