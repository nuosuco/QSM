#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子状态和量子比特实现
为QEntL量子纠缠网络提供基础的量子计算抽象
"""

import math
import random
import numpy as np
from enum import Enum
from typing import List, Dict, Tuple, Optional, Union


class QubitState(Enum):
    """量子比特状态枚举"""
    ZERO = 0  # |0⟩状态
    ONE = 1   # |1⟩状态
    SUPERPOSITION = 2  # 叠加态
    ENTANGLED = 3  # 纠缠态


class Qubit:
    """量子比特类
    
    表示单个量子比特，支持基本的量子门操作和测量
    """
    
    def __init__(self, id: Optional[str] = None):
        """初始化量子比特
        
        Args:
            id: 量子比特的唯一标识符，如果为None则自动生成
        """
        self.id = id or f"qubit_{random.randint(10000, 99999)}"
        self._alpha = complex(1.0, 0.0)  # |0⟩的振幅
        self._beta = complex(0.0, 0.0)   # |1⟩的振幅
        self._state = QubitState.ZERO
        self._entangled_with = []  # 与此量子比特纠缠的其他量子比特ID列表
        
    @property
    def state(self) -> QubitState:
        """获取量子比特的当前状态"""
        return self._state
    
    @property
    def is_entangled(self) -> bool:
        """检查量子比特是否处于纠缠态"""
        return self._state == QubitState.ENTANGLED
    
    @property
    def amplitudes(self) -> Tuple[complex, complex]:
        """获取量子比特的振幅
        
        Returns:
            包含|0⟩和|1⟩振幅的元组
        """
        return (self._alpha, self._beta)
    
    def flip(self) -> 'Qubit':
        """应用X门（NOT门）到量子比特
        
        将|0⟩变为|1⟩，将|1⟩变为|0⟩
        
        Returns:
            自身，用于链式调用
        """
        self._alpha, self._beta = self._beta, self._alpha
        
        if self._state == QubitState.ZERO:
            self._state = QubitState.ONE
        elif self._state == QubitState.ONE:
            self._state = QubitState.ZERO
            
        return self
    
    def hadamard(self) -> 'Qubit':
        """应用Hadamard门到量子比特
        
        将量子比特置于叠加态
        
        Returns:
            自身，用于链式调用
        """
        # 应用Hadamard变换矩阵
        alpha = (self._alpha + self._beta) / math.sqrt(2)
        beta = (self._alpha - self._beta) / math.sqrt(2)
        self._alpha, self._beta = alpha, beta
        
        # 更新状态
        if abs(self._alpha) > 0 and abs(self._beta) > 0:
            self._state = QubitState.SUPERPOSITION
            
        return self
    
    def phase(self, theta: float) -> 'Qubit':
        """应用相位旋转门到量子比特
        
        Args:
            theta: 旋转角度（弧度）
        
        Returns:
            自身，用于链式调用
        """
        # 应用相位旋转
        self._beta *= complex(math.cos(theta), math.sin(theta))
        
        return self
    
    def entangle_with(self, other: 'Qubit') -> None:
        """与另一个量子比特形成纠缠
        
        Args:
            other: 要纠缠的量子比特
        """
        if self.is_entangled or other.is_entangled:
            # 如果任一量子比特已经处于纠缠态，合并纠缠组
            all_entangled = set(self._entangled_with + other._entangled_with)
            all_entangled.add(self.id)
            all_entangled.add(other.id)
            self._entangled_with = list(all_entangled)
            other._entangled_with = self._entangled_with
        else:
            # 创建新的纠缠对
            self._entangled_with = [self.id, other.id]
            other._entangled_with = [self.id, other.id]
            
        self._state = QubitState.ENTANGLED
        other._state = QubitState.ENTANGLED
    
    def measure(self) -> int:
        """测量量子比特
        
        Returns:
            测量结果: 0或1
        """
        # 计算测量为|1⟩的概率
        prob_one = abs(self._beta) ** 2
        
        # 根据概率随机选择结果
        result = 1 if random.random() < prob_one else 0
        
        # 测量后量子比特坍缩到确定状态
        if result == 0:
            self._alpha = complex(1.0, 0.0)
            self._beta = complex(0.0, 0.0)
            self._state = QubitState.ZERO
        else:
            self._alpha = complex(0.0, 0.0)
            self._beta = complex(1.0, 0.0)
            self._state = QubitState.ONE
            
        return result
    
    def __str__(self) -> str:
        """返回量子比特的字符串表示"""
        if self._state == QubitState.ZERO:
            return "|0⟩"
        elif self._state == QubitState.ONE:
            return "|1⟩"
        elif self._state == QubitState.SUPERPOSITION:
            return f"{self._alpha:.2f}|0⟩ + {self._beta:.2f}|1⟩"
        else:  # ENTANGLED
            return f"|Ψ⟩ (entangled with {len(self._entangled_with)-1} qubit(s))"


class QuantumState:
    """量子态类
    
    表示多量子比特系统的状态
    """
    
    def __init__(self):
        """初始化空的量子态"""
        self.qubits: List[Qubit] = []
        self.entangled_sets: List[List[int]] = []  # 存储纠缠组，每个组是qubits中的索引列表
        
    def add_qubit(self, qubit: Optional[Qubit] = None) -> Qubit:
        """添加量子比特到量子态
        
        Args:
            qubit: 要添加的量子比特，如果为None则创建新的量子比特
            
        Returns:
            添加的量子比特
        """
        if qubit is None:
            qubit = Qubit()
            
        self.qubits.append(qubit)
        return qubit
    
    def apply_gate(self, gate: str, qubit_indices: List[int], **params) -> 'QuantumState':
        """应用量子门到指定的量子比特
        
        Args:
            gate: 量子门名称 ("x", "h", "phase", "cnot", "swap")
            qubit_indices: 要应用门的量子比特索引列表
            **params: 门的参数，如相位旋转的角度
            
        Returns:
            自身，用于链式调用
        """
        # 检查索引是否有效
        for idx in qubit_indices:
            if idx < 0 or idx >= len(self.qubits):
                raise IndexError(f"量子比特索引{idx}超出范围(0-{len(self.qubits)-1})")
        
        # 应用单量子比特门
        if gate.lower() == "x":
            self.qubits[qubit_indices[0]].flip()
        elif gate.lower() == "h":
            self.qubits[qubit_indices[0]].hadamard()
        elif gate.lower() == "phase":
            if "theta" not in params:
                raise ValueError("相位门需要theta参数")
            self.qubits[qubit_indices[0]].phase(params["theta"])
            
        # 应用双量子比特门
        elif gate.lower() == "cnot":
            if len(qubit_indices) != 2:
                raise ValueError("CNOT门需要2个量子比特索引")
            # 如果控制位为1，则翻转目标位
            control, target = qubit_indices
            if self.qubits[control].state == QubitState.ONE:
                self.qubits[target].flip()
        elif gate.lower() == "swap":
            if len(qubit_indices) != 2:
                raise ValueError("SWAP门需要2个量子比特索引")
            # 交换两个量子比特的状态
            i, j = qubit_indices
            self.qubits[i], self.qubits[j] = self.qubits[j], self.qubits[i]
            
        return self
    
    def create_bell_pair(self, first_idx: int, second_idx: int) -> None:
        """创建Bell对（最大纠缠对）
        
        Args:
            first_idx: 第一个量子比特的索引
            second_idx: 第二个量子比特的索引
        """
        # 将第一个量子比特置于叠加态
        self.qubits[first_idx].hadamard()
        
        # 应用CNOT门，从第一个量子比特到第二个
        self.apply_gate("cnot", [first_idx, second_idx])
        
        # 标记这两个量子比特为纠缠态
        self.qubits[first_idx].entangle_with(self.qubits[second_idx])
        
        # 更新纠缠组
        for group in self.entangled_sets:
            if first_idx in group or second_idx in group:
                if first_idx not in group:
                    group.append(first_idx)
                if second_idx not in group:
                    group.append(second_idx)
                break
        else:
            # 没有找到包含这些量子比特的组，创建新组
            self.entangled_sets.append([first_idx, second_idx])
    
    def measure_all(self) -> List[int]:
        """测量所有量子比特
        
        Returns:
            测量结果的列表
        """
        results = []
        
        # 处理纠缠组
        entangled_results = {}  # 存储已测量的纠缠组的结果
        
        for i, qubit in enumerate(self.qubits):
            # 检查此量子比特是否在已测量的纠缠组中
            for group_idx, group in enumerate(self.entangled_sets):
                if i in group and group_idx in entangled_results:
                    # 使用相同的纠缠组的测量结果
                    results.append(entangled_results[group_idx][i % 2])
                    break
            else:
                # 此量子比特不在已测量的纠缠组中
                if qubit.is_entangled:
                    # 找到包含此量子比特的纠缠组
                    for group_idx, group in enumerate(self.entangled_sets):
                        if i in group:
                            # 测量整个纠缠组
                            group_result = random.choice([0, 1])
                            group_results = {}
                            
                            for q_idx in group:
                                # 根据纠缠逻辑决定每个量子比特的结果
                                q_result = group_result if (q_idx - i) % 2 == 0 else 1 - group_result
                                group_results[q_idx] = q_result
                                if q_idx == i:
                                    results.append(q_result)
                            
                            entangled_results[group_idx] = group_results
                            break
                else:
                    # 非纠缠量子比特，正常测量
                    results.append(qubit.measure())
        
        return results
    
    def measure(self, qubit_idx: int) -> int:
        """测量指定的量子比特
        
        Args:
            qubit_idx: 要测量的量子比特索引
            
        Returns:
            测量结果: 0或1
        """
        if qubit_idx < 0 or qubit_idx >= len(self.qubits):
            raise IndexError(f"量子比特索引{qubit_idx}超出范围(0-{len(self.qubits)-1})")
        
        qubit = self.qubits[qubit_idx]
        
        if not qubit.is_entangled:
            # 非纠缠量子比特，直接测量
            return qubit.measure()
        else:
            # 纠缠量子比特，找到其纠缠组
            for group in self.entangled_sets:
                if qubit_idx in group:
                    # 随机选择一个测量结果
                    result = random.choice([0, 1])
                    
                    # 更新组中所有量子比特的状态
                    for i, q_idx in enumerate(group):
                        if i % 2 == 0:  # 保持相同的结果
                            self.qubits[q_idx]._state = QubitState.ZERO if result == 0 else QubitState.ONE
                            self.qubits[q_idx]._alpha = complex(1.0, 0.0) if result == 0 else complex(0.0, 0.0)
                            self.qubits[q_idx]._beta = complex(0.0, 0.0) if result == 0 else complex(1.0, 0.0)
                        else:  # 相反的结果
                            self.qubits[q_idx]._state = QubitState.ZERO if result == 1 else QubitState.ONE
                            self.qubits[q_idx]._alpha = complex(1.0, 0.0) if result == 1 else complex(0.0, 0.0)
                            self.qubits[q_idx]._beta = complex(0.0, 0.0) if result == 1 else complex(1.0, 0.0)
                    
                    # 移除纠缠组
                    self.entangled_sets.remove(group)
                    
                    # 清除所有相关量子比特的纠缠信息
                    for q_idx in group:
                        self.qubits[q_idx]._entangled_with = []
                        self.qubits[q_idx]._state = QubitState.ZERO if self.qubits[q_idx]._alpha == complex(1.0, 0.0) else QubitState.ONE
                    
                    return result if qubit_idx == group[0] else (1 - result)
    
    def to_binary_string(self) -> str:
        """将量子态转换为二进制字符串表示
        
        Returns:
            表示当前量子态的二进制字符串，如 "010110"
        """
        return ''.join(str(self.measure(i)) for i in range(len(self.qubits)))
    
    def encode_string(self, text: str) -> None:
        """将字符串编码为量子态
        
        每个字符使用8个量子比特（ASCII编码）
        
        Args:
            text: 要编码的字符串
        """
        self.qubits = []  # 清除现有量子比特
        self.entangled_sets = []
        
        for char in text:
            # 获取字符的ASCII码，并转换为8位二进制
            bits = format(ord(char), '08b')
            for bit in bits:
                qubit = Qubit()
                if bit == '1':
                    qubit.flip()  # 如果是1，翻转到|1⟩态
                self.add_qubit(qubit)
    
    def decode_string(self) -> str:
        """将量子态解码为字符串
        
        假设量子态是使用encode_string方法编码的
        
        Returns:
            解码后的字符串
        """
        # 测量所有量子比特
        bits = self.measure_all()
        
        # 将比特转换回字符
        chars = []
        for i in range(0, len(bits), 8):
            # 确保有完整的8位
            if i + 8 <= len(bits):
                byte = bits[i:i+8]
                char_code = int(''.join(map(str, byte)), 2)
                chars.append(chr(char_code))
        
        return ''.join(chars)
    
    def __len__(self) -> int:
        """返回量子态中的量子比特数量"""
        return len(self.qubits)
    
    def __str__(self) -> str:
        """返回量子态的字符串表示"""
        if not self.qubits:
            return "|empty⟩"
        
        # 对于小型量子态，显示每个量子比特
        if len(self.qubits) <= 8:
            return " ⊗ ".join(str(q) for q in self.qubits)
        
        # 对于大型量子态，显示摘要
        entangled_count = sum(1 for q in self.qubits if q.is_entangled)
        return f"|Ψ⟩ ({len(self.qubits)} qubits, {entangled_count} entangled)" 

"""
"""
量子基因编码: QE-QUA-3331F16AB1CE
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
