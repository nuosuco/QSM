#!/usr/bin/env python3
"""
量子超密编码实现
版本: v0.2.0
量子基因编码: QGC-VM-SUPERDENSE-20260308

超密编码：通过一个量子比特传输两个经典比特的信息
利用量子纠缠的特性
"""

import numpy as np
from quantum_simulator import QuantumSimulator

class SuperdenseCoding:
    """超密编码"""
    
    def __init__(self):
        self.sim = QuantumSimulator(num_qubits=2)
        self.messages = {
            '00': '发送 |00⟩ → 不施加任何门',
            '01': '发送 |01⟩ → 对第一个量子比特施加X门',
            '10': '发送 |10⟩ → 对第一个量子比特施加Z门',
            '11': '发送 |11⟩ → 对第一个量子比特施加X门和Z门'
        }
        
    def create_bell_pair(self):
        """创建Bell纠缠态 |Φ+⟩ = (|00⟩ + |11⟩)/√2"""
        print("\n=== 创建Bell纠缠对 ===")
        
        # 重置状态
        self.sim.reset()
        
        # 对第一个量子比特应用Hadamard门
        self.sim.apply_gate('H', 0)
        
        # 应用CNOT门（控制=0，目标=1）
        self.sim.apply_cnot(0, 1)
        
        print("Bell态创建完成: |Φ+⟩ = (|00⟩ + |11⟩)/√2")
        
    def encode(self, message: str):
        """
        编码消息
        
        Args:
            message: 两个经典比特，如 '00', '01', '10', '11'
        """
        print(f"\n=== 编码消息: {message} ===")
        print(self.messages.get(message, '未知消息'))
        
        if message == '00':
            # 不施加任何门
            pass
        elif message == '01':
            # 施加X门
            self.sim.apply_gate('X', 0)
        elif message == '10':
            # 施加Z门
            self.sim.apply_gate('Z', 0)
        elif message == '11':
            # 施加X门和Z门
            self.sim.apply_gate('X', 0)
            self.sim.apply_gate('Z', 0)
    
    def decode(self) -> str:
        """解码消息"""
        print("\n=== 解码消息 ===")
        
        # 应用CNOT门
        self.sim.apply_cnot(0, 1)
        
        # 对第一个量子比特应用Hadamard门
        self.sim.apply_gate('H', 0)
        
        # 测量两个量子比特
        bit0 = self.sim.measure(0)
        bit1 = self.sim.measure(1)
        
        message = f"{bit0}{bit1}"
        print(f"解码结果: {message}")
        
        return message
    
    def get_state_probabilities(self) -> np.ndarray:
        """获取当前状态的概率分布"""
        return self.sim.get_probabilities()


def demo():
    """演示超密编码"""
    print("\n" + "=" * 50)
    print("量子超密编码演示")
    print("=" * 50)
    
    # 测试所有四种消息
    test_messages = ['00', '01', '10', '11']
    
    for msg in test_messages:
        print("\n" + "-" * 50)
        sdc = SuperdenseCoding()
        
        # 创建Bell纠缠对
        sdc.create_bell_pair()
        
        # 编码
        sdc.encode(msg)
        
        # 解码
        result = sdc.decode()
        
        # 验证
        if result == msg:
            print(f"✅ 传输成功！发送: {msg}, 接收: {result}")
        else:
            print(f"❌ 传输失败！发送: {msg}, 接收: {result}")
    
    print("\n" + "=" * 50)
    print("超密编码演示完成")
    print("=" * 50)


if __name__ == "__main__":
    demo()
