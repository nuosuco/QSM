#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四模型协作机制测试
"""

import sys
import os
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')

from datetime import datetime

def test_four_model_coordinator():
    """测试四模型协调器"""
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 四模型协作机制测试")
    print("=" * 60)

    try:
        from four_model_coordinator import FourModelCoordinator
        print(f"\n✅ FourModelCoordinator 导入成功")

        # 初始化协调器
        coordinator = FourModelCoordinator()
        print(f"✅ 四模型协调器初始化成功")

        # 检查模型状态
        print(f"\n模型状态:")
        status = coordinator.get_status() if hasattr(coordinator, 'get_status') else "方法不存在"
        print(f"  {status}")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def test_agent_harness():
    """测试Agent Harness"""
    print("\n" + "-" * 40)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试Agent Harness")
    print("-" * 40)

    try:
        from qsm_agent_harness import AgentHarness, ShortTermMemory, SelfFeedback, SelfOptimization
        print(f"✅ AgentHarness 导入成功")

        harness = AgentHarness()
        print(f"✅ Agent Harness 初始化成功")

        # 测试三大模块
        stm = ShortTermMemory()
        feedback = SelfFeedback()
        optimizer = SelfOptimization()
        print(f"✅ 短时记忆、自反馈、自优化模块初始化成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def test_iteration_evaluator():
    """测试迭代评测系统"""
    print("\n" + "-" * 40)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试迭代评测系统")
    print("-" * 40)

    try:
        from iteration_evaluator import IterationEvaluator
        print(f"✅ IterationEvaluator 导入成功")

        evaluator = IterationEvaluator()
        print(f"✅ 迭代评测系统初始化成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

def main():
    results = []
    results.append(("四模型协调器", test_four_model_coordinator()))
    results.append(("Agent Harness", test_agent_harness()))
    results.append(("迭代评测系统", test_iteration_evaluator()))

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)

if __name__ == "__main__":
    main()
