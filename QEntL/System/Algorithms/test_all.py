#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子算法库统一测试入口
运行所有量子算法的测试
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from QEntL.System.Algorithms.qft import QFTTestSuite
from QEntL.System.Algorithms.shor import ShorTestSuite
from QEntL.System.Algorithms.teleportation import TeleportationTest
from QEntL.System.Algorithms.grover import GroverTest


def run_all_tests():
    """运行所有量子算法测试"""
    
    print("=" * 60)
    print("     QSM量子算法库完整测试")
    print("=" * 60)
    
    results = {}
    
    # 测试QFT
    print("\n" + "=" * 60)
    print("1. 量子傅里叶变换（QFT）测试")
    print("=" * 60)
    qft_suite = QFTTestSuite()
    qft_passed = qft_suite.run_all_tests()
    results['QFT'] = qft_passed
    
    # 测试Shor
    print("\n" + "=" * 60)
    print("2. Shor算法测试")
    print("=" * 60)
    shor_suite = ShorTestSuite()
    shor_passed = shor_suite.run_all_tests()
    results['Shor'] = shor_passed
    
    # 测试量子隐形传态
    print("\n" + "=" * 60)
    print("3. 量子隐形传态测试")
    print("=" * 60)
    teleport_suite = TeleportationTest()
    teleport_passed = teleport_suite.run_all_tests()
    results['Teleportation'] = teleport_passed
    
    # 测试Grover
    print("\n" + "=" * 60)
    print("4. Grover搜索算法测试")
    print("=" * 60)
    grover_suite = GroverTest()
    grover_passed = grover_suite.run_all_tests()
    results['Grover'] = grover_passed
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("     测试汇总")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    
    print("\n" + "=" * 60)
    print(f"  总计: {passed_count}/{total} 算法测试通过")
    print("=" * 60)
    
    return passed_count == total


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🎉 所有量子算法测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分测试失败，请检查")
        sys.exit(1)
