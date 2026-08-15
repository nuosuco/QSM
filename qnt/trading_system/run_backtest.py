"""
记忆承载·碧树西风交易系统 - 回测入口
独立运行：python run_backtest.py
"""
import sys
import os
import time
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, '/root/SOM/qnt')

from trading_system.config import SystemConfig, BacktestConfig
from trading_system.backtest import BacktestEngine


def main():
    """主函数"""
    print("=" * 60)
    print("记忆承载·碧树西风交易系统 - 回测引擎 v1.0")
    print("=" * 60)
    print()
    
    # 创建配置
    config = SystemConfig(
        backtest=BacktestConfig(
            initial_capital=10000.0,
            duration_days=30,
        )
    )
    
    # 运行回测
    print(f"📊 初始资金: ${config.backtest.initial_capital:,.2f}")
    print(f"📅 回测周期: {config.backtest.duration_days}天")
    print(f"🎯 乌龙指概率: {config.backtest.fat_finger_probability*100:.2f}% per tick")
    print()
    
    engine = BacktestEngine(config.backtest)
    
    start_time = time.time()
    result = engine.run()
    elapsed = time.time() - start_time
    
    print(f"⏱️  回测耗时: {elapsed:.2f}秒")
    print(f"📈 生成信号: {result.total_signals}")
    print(f"✅ 执行交易: {result.executed_signals}")
    print()
    
    # 输出结果
    print(result.summary())
    
    # 详细统计
    print("\n" + "=" * 60)
    print("详细统计")
    print("=" * 60)
    print(f"盈利交易:     {result.winning_trades}")
    print(f"亏损交易:     {result.losing_trades}")
    print(f"最大单笔亏损: {result.bishu_max_loss_pct:.2f}%")
    print(f"最大单笔盈利: {result.bishu_max_gain_pct:.2f}%")
    print()
    
    # 碧树西风标准总结
    checks = result.bishu_check()
    passed = sum(1 for v in checks.values() if v)
    print(f"✅ 通过标准: {passed}/5")
    
    if passed == 5:
        print("\n🎉 完美通过碧树西风所有标准!")
    elif passed >= 4:
        print("\n✅ 基本通过碧树西风标准")
    else:
        print("\n⚠️ 未通过碧树西风标准，需要调整参数")
    
    return result


if __name__ == "__main__":
    main()
