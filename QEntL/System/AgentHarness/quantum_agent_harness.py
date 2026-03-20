#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子Agent Harness - 将自我进化框架与量子虚拟机集成

实现：
1. 量子算法自动优化循环
2. 量子门序列自我进化
3. 量子电路性能迭代提升
"""

import sys
import os

# 添加正确的路径
qsm_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, qsm_root)
sys.path.insert(0, os.path.join(qsm_root, 'VM'))

from src.quantum_simulator import QuantumSimulator
from qsm_agent_harness import AgentHarness, ShortTermMemory, SelfFeedback, SelfOptimization
from QEntL.System.AgentHarness.qsm_agent_harness import AgentHarness, ShortTermMemory, SelfFeedback, SelfOptimization


class QuantumEvolutionHarness(AgentHarness):
    """量子自我进化框架"""
    
    def __init__(self):
        super().__init__()
        self.quantum_state = None
    
    def create_quantum_execute_fn(self, n_qubits: int = 2):
        """创建量子执行函数"""
        def execute(state):
            sim = QuantumSimulator(n_qubits)
            
            # 应用量子门序列
            gate_sequence = state.get("gates", [])
            for gate in gate_sequence:
                gate_name = gate.get("name", "H")
                qubit = gate.get("qubit", 0)
                try:
                    sim.apply_gate(gate_name, qubit)
                except Exception as e:
                    return {"error": str(e), "success": False}
            
            # 获取结果 - 只返回概率分布
            probs = sim.get_probabilities()
            
            return {
                "probabilities": probs,
                "n_qubits": n_qubits,
                "success": True
            }
        
        return execute
    
    def create_quantum_evaluate_fn(self, target_state: int = 0):
        """创建量子评测函数"""
        def evaluate(result):
            if not result.get("success"):
                return {"success": False, "score": 0}
            
            probs = result.get("probabilities", [])
            
            # 评分：目标状态概率
            target_prob = probs[target_state] if target_state < len(probs) else 0
            
            # 均匀性评分（对于叠加态）
            n_states = len(probs)
            uniform_prob = 1.0 / n_states
            uniformity = 1.0 - sum(abs(p - uniform_prob) for p in probs) / 2
            
            # 综合分数
            score = (target_prob * 0.5 + uniformity * 0.5)
            
            return {
                "success": True,
                "score": score,
                "target_prob": target_prob,
                "uniformity": uniformity,
                "probabilities": probs
            }
        
        return evaluate
    
    def optimize_quantum_gates(self, target: str = "superposition", n_qubits: int = 2):
        """优化量子门序列"""
        
        # 初始量子门序列
        if target == "superposition":
            initial_state = {
                "gates": [{"name": "H", "qubit": i} for i in range(n_qubits)]
            }
        elif target == "bell":
            initial_state = {
                "gates": [
                    {"name": "H", "qubit": 0},
                    {"name": "X", "qubit": 1}
                ]
            }
        else:
            initial_state = {"gates": [{"name": "H", "qubit": 0}]}
        
        # 运行进化循环
        result = self.run_evolution_loop(
            task_name=f"quantum_{target}",
            initial_state=initial_state,
            execute_fn=self.create_quantum_execute_fn(n_qubits),
            evaluate_fn=self.create_quantum_evaluate_fn(),
            max_iterations=20
        )
        
        return result


class QuantumGateOptimizer:
    """量子门优化器"""
    
    def __init__(self):
        self.available_gates = ["H", "X", "Y", "Z", "S", "T"]
        self.memory = ShortTermMemory()
        self.feedback = SelfFeedback()
        self.optimizer = SelfOptimization()
    
    def search_optimal_gates(self, target_probabilities: list, n_qubits: int = 2, max_iterations: int = 50):
        """搜索最优量子门序列"""
        
        session_id = self.memory.create_session("gate_search")
        best_sequence = []
        best_score = 0
        
        for i in range(max_iterations):
            # 生成候选门序列
            if i == 0:
                # 从简单开始
                sequence = [{"name": "H", "qubit": 0}]
            else:
                # 基于历史优化
                sequence = self._mutate_sequence(best_sequence, n_qubits)
            
            # 执行
            result = self._execute_sequence(sequence, n_qubits)
            
            # 评估
            score = self._evaluate_sequence(result, target_probabilities)
            
            # 记录
            self.memory.record_iteration({
                "state": {"gates": sequence},
                "result": result,
                "score": score,
                "success": score > best_score
            })
            
            # 更新最佳
            if score > best_score:
                best_score = score
                best_sequence = sequence.copy()
            
            print(f"迭代 {i+1}: 分数={score:.4f}, 最佳={best_score:.4f}")
            
            # 达到目标
            if best_score >= 0.95:
                break
        
        return {
            "best_sequence": best_sequence,
            "best_score": best_score,
            "iterations": i + 1
        }
    
    def _mutate_sequence(self, sequence: list, n_qubits: int) -> list:
        """变异门序列"""
        import random
        
        new_sequence = sequence.copy()
        
        # 随机操作
        action = random.choice(["add", "modify", "remove"])
        
        if action == "add" and len(new_sequence) < 10:
            # 添加新门
            gate = {
                "name": random.choice(self.available_gates),
                "qubit": random.randint(0, n_qubits - 1)
            }
            new_sequence.append(gate)
        elif action == "modify" and new_sequence:
            # 修改现有门
            idx = random.randint(0, len(new_sequence) - 1)
            new_sequence[idx]["name"] = random.choice(self.available_gates)
        elif action == "remove" and len(new_sequence) > 1:
            # 移除门
            idx = random.randint(0, len(new_sequence) - 1)
            new_sequence.pop(idx)
        
        return new_sequence
    
    def _execute_sequence(self, sequence: list, n_qubits: int) -> dict:
        """执行门序列"""
        sim = QuantumSimulator(n_qubits)
        
        for gate in sequence:
            try:
                sim.apply_gate(gate["name"], gate["qubit"])
            except:
                return {"probabilities": [0] * (2 ** n_qubits), "success": False}
        
        return {
            "probabilities": sim.get_probabilities(),
            "success": True
        }
    
    def _evaluate_sequence(self, result: dict, target: list) -> float:
        """评估门序列"""
        if not result.get("success"):
            return 0
        
        probs = result.get("probabilities", [])
        
        # 计算与目标的距离
        if len(probs) != len(target):
            return 0
        
        # 余弦相似度
        dot = sum(p * t for p, t in zip(probs, target))
        norm_p = sum(p ** 2 for p in probs) ** 0.5
        norm_t = sum(t ** 2 for t in target) ** 0.5
        
        if norm_p == 0 or norm_t == 0:
            return 0
        
        return dot / (norm_p * norm_t)


# 测试
if __name__ == "__main__":
    print("=== 量子Agent Harness测试 ===\n")
    
    # 测试1：量子叠加态优化
    print("测试1：量子叠加态优化")
    harness = QuantumEvolutionHarness()
    result = harness.optimize_quantum_gates("superposition", n_qubits=2)
    print(f"结果: {result}\n")
    
    # 测试2：量子门搜索
    print("测试2：量子门序列搜索")
    optimizer = QuantumGateOptimizer()
    # 目标：均匀叠加态
    target = [0.25, 0.25, 0.25, 0.25]  # 2量子比特均匀分布
    result = optimizer.search_optimal_gates(target, n_qubits=2, max_iterations=20)
    print(f"最佳序列: {result['best_sequence']}")
    print(f"最佳分数: {result['best_score']:.4f}")
    print(f"迭代次数: {result['iterations']}")
