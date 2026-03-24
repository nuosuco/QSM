#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子调试器 - 量子程序调试工具
"""

import json
from datetime import datetime

class QuantumDebugger:
    """量子调试器"""

    def __init__(self):
        self.breakpoints = []
        self.watch_list = []
        self.execution_trace = []
        self.current_step = 0
        self.state_history = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子调试器初始化")

    def set_breakpoint(self, gate_index, condition=None):
        """设置断点"""
        bp = {
            'index': gate_index,
            'condition': condition,
            'enabled': True,
            'hit_count': 0
        }
        self.breakpoints.append(bp)
        return len(self.breakpoints) - 1

    def add_watch(self, qubit_name):
        """添加监视变量"""
        self.watch_list.append({
            'name': qubit_name,
            'values': []
        })

    def step_into(self, gates, state):
        """单步执行（进入）"""
        if self.current_step >= len(gates):
            return {'status': 'end_of_circuit'}

        gate = gates[self.current_step]

        # 记录执行前状态
        pre_state = state.copy()

        # 执行门操作（简化模拟）
        post_state = self._execute_gate(gate, state)

        # 记录执行轨迹
        trace = {
            'step': self.current_step,
            'gate': gate,
            'pre_state': pre_state[:4] if len(pre_state) > 4 else pre_state,
            'post_state': post_state[:4] if len(post_state) > 4 else post_state,
            'timestamp': datetime.now().isoformat()
        }
        self.execution_trace.append(trace)
        self.state_history.append(post_state.copy())

        self.current_step += 1

        return {
            'status': 'stepped',
            'step': self.current_step - 1,
            'gate': gate,
            'state': post_state
        }

    def step_over(self, gates, state):
        """单步执行（跳过）"""
        return self.step_into(gates, state)

    def continue_execution(self, gates, state):
        """继续执行直到断点"""
        while self.current_step < len(gates):
            result = self.step_into(gates, state)

            # 检查断点
            for bp in self.breakpoints:
                if bp['enabled'] and bp['index'] == self.current_step:
                    bp['hit_count'] += 1
                    if bp['condition'] is None or bp['condition'](state):
                        return {
                            'status': 'breakpoint_hit',
                            'breakpoint': bp,
                            'state': state
                        }

        return {'status': 'completed', 'final_state': state}

    def _execute_gate(self, gate, state):
        """执行单个门操作"""
        import math
        gate_type = gate.get('type', '').upper()

        # 简化模拟
        if gate_type == 'H':
            # Hadamard门
            return [s / math.sqrt(2) for s in state]
        elif gate_type == 'X':
            # X门（NOT）
            return state[::-1] if len(state) == 2 else state
        elif gate_type == 'CNOT':
            # CNOT门
            return state  # 简化
        else:
            return state

    def inspect_state(self, state):
        """检查量子态"""
        import math

        probabilities = [abs(s)**2 for s in state]
        entropy = self._calculate_entropy(probabilities)

        return {
            'dimension': len(state),
            'probabilities': probabilities,
            'entropy': entropy,
            'norm': math.sqrt(sum(p for p in probabilities)),
            'dominant_states': self._get_dominant_states(probabilities, 3)
        }

    def _calculate_entropy(self, probs):
        """计算冯诺依曼熵"""
        import math
        entropy = 0
        for p in probs:
            if 0 < p < 1:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    def _get_dominant_states(self, probs, n):
        """获取主导态"""
        indexed = [(i, p) for i, p in enumerate(probs)]
        sorted_probs = sorted(indexed, key=lambda x: -x[1])
        return [{'state': f'|{i}⟩', 'probability': round(p, 4)} for i, p in sorted_probs[:n]]

    def get_trace(self):
        """获取执行轨迹"""
        return {
            'total_steps': len(self.execution_trace),
            'trace': self.execution_trace[-10:] if len(self.execution_trace) > 10 else self.execution_trace
        }

    def reset(self):
        """重置调试器"""
        self.current_step = 0
        self.execution_trace = []
        self.state_history = []
        for bp in self.breakpoints:
            bp['hit_count'] = 0

    def export_debug_info(self):
        """导出调试信息"""
        return {
            'breakpoints': self.breakpoints,
            'execution_trace': self.execution_trace,
            'state_history_length': len(self.state_history),
            'current_step': self.current_step
        }

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子调试器测试")
    print("=" * 60)

    debugger = QuantumDebugger()

    # 模拟量子电路
    gates = [
        {'type': 'H', 'targets': ['q0']},
        {'type': 'CNOT', 'targets': ['q0', 'q1']},
        {'type': 'H', 'targets': ['q1']},
        {'type': 'X', 'targets': ['q0']}
    ]

    # 初始状态
    state = [1, 0, 0, 0]  # |00⟩

    print("\n设置断点:")
    bp0 = debugger.set_breakpoint(0)
    print(f"  断点0: 在第0个门")

    bp2 = debugger.set_breakpoint(2)
    print(f"  断点1: 在第2个门")

    print("\n单步执行:")
    for i in range(3):
        result = debugger.step_into(gates, state)
        print(f"  步骤{i}: {result['gate']['type']}")
        state = result['state']

    print("\n检查量子态:")
    inspection = debugger.inspect_state(state)
    print(f"  维度: {inspection['dimension']}")
    print(f"  熵: {inspection['entropy']}")
    print(f"  主导态: {inspection['dominant_states']}")

    print("\n获取执行轨迹:")
    trace = debugger.get_trace()
    print(f"  总步数: {trace['total_steps']}")

    print("\n重置调试器:")
    debugger.reset()
    print(f"  当前步骤: {debugger.current_step}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
