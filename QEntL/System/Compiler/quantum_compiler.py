#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子编译器 - QEntL源码到量子门序列编译
"""

import re
from datetime import datetime

class QuantumCompiler:
    """量子编译器"""

    def __init__(self):
        self.symbols = {}
        self.gates = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子编译器初始化")

    def compile(self, source):
        """
        编译QEntL源码
        返回量子门序列
        """
        # 清理状态
        self.symbols = {}
        self.gates = []

        # 解析源码
        lines = source.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue

            # 解析声明
            if line.startswith('qubit'):
                self._parse_qubit(line)
            elif line.startswith('gate'):
                self._parse_gate(line)
            elif line.startswith('circuit'):
                self._parse_circuit(line)
            elif '=' in line:
                self._parse_assignment(line)
            else:
                # 默认为量子门操作
                self._parse_operation(line)

        return {
            'gates': self.gates,
            'symbols': self.symbols,
            'total_gates': len(self.gates)
        }

    def _parse_qubit(self, line):
        """解析量子比特声明"""
        # qubit q0, q1, q2
        match = re.match(r'qubit\s+(.+)', line)
        if match:
            qubits = [q.strip() for q in match.group(1).split(',')]
            for q in qubits:
                self.symbols[q] = {'type': 'qubit', 'index': len(self.symbols)}

    def _parse_gate(self, line):
        """解析门定义"""
        # gate H q0
        # gate CNOT q0, q1
        match = re.match(r'gate\s+(\w+)\s+(.+)', line)
        if match:
            gate_type = match.group(1)
            targets = [t.strip() for t in match.group(2).split(',')]

            gate = {
                'type': gate_type.upper(),
                'targets': targets,
                'line': line
            }
            self.gates.append(gate)

    def _parse_circuit(self, line):
        """解析电路块"""
        # circuit main { ... }
        pass  # 暂时忽略块结构

    def _parse_assignment(self, line):
        """解析赋值"""
        # |0> = 1
        parts = line.split('=')
        if len(parts) == 2:
            symbol = parts[0].strip()
            value = parts[1].strip()
            self.symbols[symbol] = {'type': 'value', 'value': value}

    def _parse_operation(self, line):
        """解析操作"""
        # H q0
        # CNOT q0 q1
        parts = line.split()
        if len(parts) >= 2:
            gate_type = parts[0].upper()
            targets = parts[1:]

            gate = {
                'type': gate_type,
                'targets': targets,
                'line': line
            }
            self.gates.append(gate)

    def to_qasm(self):
        """转换为OpenQASM格式"""
        qasm = ['OPENQASM 2.0;', 'include "qelib1.inc";']

        # 声明量子比特
        qubits = [k for k, v in self.symbols.items() if v.get('type') == 'qubit']
        for i, q in enumerate(qubits):
            qasm.append(f'qreg {q}[1];')

        # 声明经典寄存器
        if qubits:
            qasm.append(f'creg c[{len(qubits)}];')

        # 添加门操作
        for gate in self.gates:
            gate_type = gate['type']
            targets = gate['targets']

            if gate_type == 'H':
                qasm.append(f'h {targets[0]};')
            elif gate_type == 'X':
                qasm.append(f'x {targets[0]};')
            elif gate_type == 'Y':
                qasm.append(f'y {targets[0]};')
            elif gate_type == 'Z':
                qasm.append(f'z {targets[0]};')
            elif gate_type == 'CNOT':
                qasm.append(f'cx {targets[0]}, {targets[1]};')
            elif gate_type == 'MEASURE':
                qasm.append(f'measure {targets[0]} -> c[0];')

        return '\n'.join(qasm)

    def to_json(self):
        """转换为JSON格式"""
        return {
            'format': 'quantum_gates',
            'gates': self.gates,
            'symbols': self.symbols
        }

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子编译器测试")
    print("=" * 60)

    compiler = QuantumCompiler()

    # 测试源码
    source = """
    // Bell态电路
    qubit q0, q1
    
    H q0
    CNOT q0 q1
    
    measure q0
    measure q1
    """

    print("\n编译QEntL源码:")
    print(source)

    result = compiler.compile(source)
    print(f"\n编译结果:")
    print(f"  量子门数: {result['total_gates']}")
    print(f"  符号表: {list(result['symbols'].keys())}")

    for gate in result['gates']:
        print(f"  门: {gate['type']} {gate['targets']}")

    # 转换为QASM
    print("\n转换为OpenQASM:")
    qasm = compiler.to_qasm()
    print(qasm)

    # 测试GHZ态
    print("\n" + "=" * 60)
    print("编译GHZ态电路:")

    source2 = """
    qubit q0, q1, q2
    
    H q0
    CNOT q0 q1
    CNOT q1 q2
    """

    compiler2 = QuantumCompiler()
    result2 = compiler2.compile(source2)
    print(f"  量子门数: {result2['total_gates']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
