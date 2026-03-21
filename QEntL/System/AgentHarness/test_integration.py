#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Harness 与量子算法集成测试
验证自我进化框架在量子算法优化中的应用
"""

import sys
import os
sys.path.insert(0, '/root/QSM')

from qsm_agent_harness import AgentHarness, ShortTermMemory, SelfFeedback, SelfOptimization
from iteration_evaluator import QuantumAlgorithmEvaluator

def test_grover_integration():
    """测试Grover算法与Agent Harness集成"""
    print("=" * 50)
    print("测试1: Grover算法集成")
    print("=" * 50)
    
    harness = AgentHarness()
    evaluator = QuantumAlgorithmEvaluator()
    
    # 定义Grover执行函数
    def grover_execute(state):
        n_qubits = state.get('n_qubits', 3)
        # 模拟Grover搜索结果
        return {
            'n_qubits': n_qubits,
            'iterations': int(2 ** (n_qubits / 2)),
            'found': True
        }
    
    # 定义评测函数
    def grover_evaluate(result):
        # Grover算法评测：检查是否找到目标
        return {
            'success': result.get('found', False),
            'score': 1.0 if result.get('found') else 0.0,
            'metrics': {'iterations': result.get('iterations', 0)}
        }
    
    # 运行进化循环
    initial_state = {'n_qubits': 3}
    result = harness.run_evolution_loop(
        task_name='grover_optimization',
        initial_state=initial_state,
        execute_fn=grover_execute,
        evaluate_fn=grover_evaluate,
        max_iterations=5
    )
    
    print(f"\n结果: {result}")
    return result.get('success', False)

def test_qft_integration():
    """测试QFT与Agent Harness集成"""
    print("\n" + "=" * 50)
    print("测试2: QFT算法集成")
    print("=" * 50)
    
    harness = AgentHarness()
    
    def qft_execute(state):
        n_qubits = state.get('n_qubits', 3)
        return {
            'n_qubits': n_qubits,
            'transform_successful': True,
            'output_size': 2 ** n_qubits
        }
    
    def qft_evaluate(result):
        return {
            'success': result.get('transform_successful', False),
            'score': 1.0 if result.get('transform_successful') else 0.0,
            'metrics': {'output_size': result.get('output_size', 0)}
        }
    
    initial_state = {'n_qubits': 4}
    result = harness.run_evolution_loop(
        task_name='qft_optimization',
        initial_state=initial_state,
        execute_fn=qft_execute,
        evaluate_fn=qft_evaluate,
        max_iterations=3
    )
    
    print(f"\n结果: {result}")
    return result.get('success', False)

def test_100_iterations():
    """测试100+轮迭代循环"""
    print("\n" + "=" * 50)
    print("测试3: 100轮迭代循环")
    print("=" * 50)
    
    harness = AgentHarness()
    harness.max_iterations = 100
    
    import random
    
    def adaptive_execute(state):
        # 自适应执行：根据迭代次数调整参数
        iteration = state.get('iteration', 1)
        param = state.get('param', 0.5)
        
        # 模拟学习过程：参数逐渐优化
        new_param = param + random.uniform(-0.1, 0.2) * (1 - iteration/100)
        new_param = max(0, min(1, new_param))
        
        return {
            'param': new_param,
            'output': f"执行结果_{iteration}",
            'improved': new_param > param
        }
    
    def adaptive_evaluate(result):
        param = result.get('param', 0)
        # 分数随参数优化而提高
        score = 0.3 + param * 0.7
        return {
            'success': score > 0.8,
            'score': score,
            'metrics': {'param': param}
        }
    
    initial_state = {'param': 0.3, 'iteration': 0}
    
    # 自定义执行循环以跟踪迭代次数
    def tracked_execute(state):
        state['iteration'] = state.get('iteration', 0) + 1
        return adaptive_execute(state)
    
    result = harness.run_evolution_loop(
        task_name='100_iteration_test',
        initial_state=initial_state,
        execute_fn=tracked_execute,
        evaluate_fn=adaptive_evaluate,
        max_iterations=100
    )
    
    print(f"\n总迭代次数: {result.get('iterations', 0)}")
    print(f"最佳分数: {result.get('best_score', 0):.4f}")
    return result.get('iterations', 0) >= 50

def run_all_integration_tests():
    """运行所有集成测试"""
    print("=" * 50)
    print("Agent Harness 与量子算法集成测试")
    print("=" * 50)
    
    results = []
    
    # 测试1: Grover集成
    try:
        results.append(('Grover集成', test_grover_integration()))
    except Exception as e:
        print(f"Grover测试失败: {e}")
        results.append(('Grover集成', False))
    
    # 测试2: QFT集成
    try:
        results.append(('QFT集成', test_qft_integration()))
    except Exception as e:
        print(f"QFT测试失败: {e}")
        results.append(('QFT集成', False))
    
    # 测试3: 100轮迭代
    try:
        results.append(('100轮迭代', test_100_iterations()))
    except Exception as e:
        print(f"迭代测试失败: {e}")
        results.append(('100轮迭代', False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = run_all_integration_tests()
    print(f"\n{'所有测试通过!' if success else '部分测试失败'}")
