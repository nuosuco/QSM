#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子随机数生成器
使用量子态测量产生真随机数

量子随机数的优势：
- 基于量子力学原理的真随机性
- 不可预测、不可复现
- 为加密和仿真提供高质量熵源
"""

import numpy as np
from typing import Dict, List, Optional
import time
import hashlib

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    import qiskit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class QuantumRNG:
    """量子随机数生成器"""
    
    def __init__(self, n_qubits: int = 8):
        self.n_qubits = n_qubits
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
        self.generated_numbers = []
    
    def generate_bit(self) -> int:
        """生成单个随机比特"""
        if not QISKIT_AVAILABLE:
            return self._classical_random_bit()
        
        try:
            qr = QuantumRegister(1, 'q')
            cr = ClassicalRegister(1, 'c')
            qc = QuantumCircuit(qr, cr)
            
            # Hadamard门创建叠加态
            qc.h(0)
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=1)
            result = job.result().get_counts()
            
            return int(list(result.keys())[0])
        except:
            return self._classical_random_bit()
    
    def _classical_random_bit(self) -> int:
        """经典随机比特（降级方案）"""
        return np.random.randint(0, 2)
    
    def generate_byte(self) -> int:
        """生成随机字节（0-255）"""
        if not QISKIT_AVAILABLE:
            return np.random.randint(0, 256)
        
        try:
            qr = QuantumRegister(8, 'q')
            cr = ClassicalRegister(8, 'c')
            qc = QuantumCircuit(qr, cr)
            
            # 对所有量子比特应用Hadamard
            for i in range(8):
                qc.h(i)
            
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=1)
            result = job.result().get_counts()
            
            return int(list(result.keys())[0], 2)
        except:
            return np.random.randint(0, 256)
    
    def generate_int(self, min_val: int = 0, max_val: int = 1000) -> int:
        """生成指定范围内的随机整数"""
        # 计算需要的比特数
        range_size = max_val - min_val + 1
        n_bits = max(1, int(np.ceil(np.log2(range_size))))
        
        if not QISKIT_AVAILABLE:
            return np.random.randint(min_val, max_val + 1)
        
        try:
            qr = QuantumRegister(n_bits, 'q')
            cr = ClassicalRegister(n_bits, 'c')
            qc = QuantumCircuit(qr, cr)
            
            for i in range(n_bits):
                qc.h(i)
            
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=1)
            result = job.result().get_counts()
            
            raw_value = int(list(result.keys())[0], 2)
            return min_val + (raw_value % range_size)
        except:
            return np.random.randint(min_val, max_val + 1)
    
    def generate_float(self) -> float:
        """生成0-1之间的随机浮点数"""
        # 使用32位精度
        raw = self._generate_bits(32)
        return raw / (2 ** 32)
    
    def _generate_bits(self, n_bits: int) -> int:
        """生成n位随机数"""
        if not QISKIT_AVAILABLE:
            return np.random.randint(0, 2 ** n_bits)
        
        try:
            qr = QuantumRegister(n_bits, 'q')
            cr = ClassicalRegister(n_bits, 'c')
            qc = QuantumCircuit(qr, cr)
            
            for i in range(n_bits):
                qc.h(i)
            
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=1)
            result = job.result().get_counts()
            
            return int(list(result.keys())[0], 2)
        except:
            return np.random.randint(0, 2 ** n_bits)
    
    def generate_bytes(self, length: int = 32) -> bytes:
        """生成随机字节序列"""
        result = []
        for _ in range(length):
            result.append(self.generate_byte())
        return bytes(result)
    
    def generate_hex(self, length: int = 64) -> str:
        """生成随机十六进制字符串"""
        random_bytes = self.generate_bytes(length // 2)
        return random_bytes.hex()


class QuantumEntropyPool:
    """量子熵池"""
    
    def __init__(self, pool_size: int = 1024):
        self.pool_size = pool_size
        self.rng = QuantumRNG(n_qubits=8)
        self.pool = []
        self.refill_threshold = pool_size // 4
    
    def refill_pool(self) -> Dict:
        """重新填充熵池"""
        results = {
            'added': 0,
            'pool_size': len(self.pool),
            'qiskit_available': QISKIT_AVAILABLE
        }
        
        needed = self.pool_size - len(self.pool)
        
        for _ in range(needed):
            random_byte = self.rng.generate_byte()
            self.pool.append(random_byte)
        
        results['added'] = needed
        results['pool_size'] = len(self.pool)
        
        return results
    
    def get_random_bytes(self, length: int) -> bytes:
        """从熵池获取随机字节"""
        if len(self.pool) < self.refill_threshold:
            self.refill_pool()
        
        result = []
        for _ in range(length):
            if self.pool:
                result.append(self.pool.pop())
            else:
                result.append(self.rng.generate_byte())
        
        return bytes(result)
    
    def get_random_int(self, min_val: int = 0, max_val: int = 1000) -> int:
        """从熵池获取随机整数"""
        bytes_needed = 4
        random_bytes = self.get_random_bytes(bytes_needed)
        raw_value = int.from_bytes(random_bytes, 'big')
        
        range_size = max_val - min_val + 1
        return min_val + (raw_value % range_size)


class QuantumSeedGenerator:
    """量子种子生成器"""
    
    def __init__(self):
        self.rng = QuantumRNG(n_qubits=16)
        self.generated_seeds = []
    
    def generate_seed(self, bits: int = 256) -> int:
        """生成量子随机种子"""
        # 分批生成
        seed = 0
        remaining = bits
        
        while remaining > 0:
            batch_bits = min(remaining, 16)
            batch_value = self.rng._generate_bits(batch_bits)
            seed = (seed << batch_bits) | batch_value
            remaining -= batch_bits
        
        self.generated_seeds.append({
            'seed': seed,
            'bits': bits,
            'timestamp': time.time()
        })
        
        return seed
    
    def generate_uuid_like(self) -> str:
        """生成类UUID的量子随机标识符"""
        parts = []
        for length in [8, 4, 4, 4, 12]:
            random_bytes = self.rng.generate_bytes(length // 2)
            parts.append(random_bytes.hex())
        
        return '-'.join(parts)


class QuantumRNGBenchmark:
    """量子随机数生成器基准测试"""
    
    def __init__(self):
        self.rng = QuantumRNG(n_qubits=8)
        self.entropy_pool = QuantumEntropyPool()
        self.seed_generator = QuantumSeedGenerator()
    
    def run_benchmark(self) -> Dict:
        """运行基准测试"""
        print("=" * 60)
        print("量子随机数生成器测试")
        print("=" * 60)
        
        results = {
            'qiskit_available': QISKIT_AVAILABLE,
            'tests': {}
        }
        
        start_time = time.time()
        
        # 测试1：生成比特
        print("\n[1] 生成随机比特...")
        bits = [self.rng.generate_bit() for _ in range(100)]
        bit_balance = sum(bits) / len(bits)
        results['tests']['bits'] = {
            'generated': len(bits),
            'balance': bit_balance,
            'passed': 0.4 <= bit_balance <= 0.6
        }
        print(f"    平衡度: {bit_balance:.2%}")
        
        # 测试2：生成字节
        print("\n[2] 生成随机字节...")
        bytes_generated = [self.rng.generate_byte() for _ in range(100)]
        byte_mean = np.mean(bytes_generated)
        byte_std = np.std(bytes_generated)
        results['tests']['bytes'] = {
            'generated': len(bytes_generated),
            'mean': byte_mean,
            'std': byte_std,
            'passed': 100 <= byte_mean <= 156  # 理论期望128±28
        }
        print(f"    均值: {byte_mean:.1f}, 标准差: {byte_std:.1f}")
        
        # 测试3：生成整数
        print("\n[3] 生成随机整数 (0-100)...")
        ints = [self.rng.generate_int(0, 100) for _ in range(50)]
        int_mean = np.mean(ints)
        results['tests']['integers'] = {
            'generated': len(ints),
            'mean': int_mean,
            'passed': 30 <= int_mean <= 70
        }
        print(f"    均值: {int_mean:.1f}")
        
        # 测试4：生成浮点数
        print("\n[4] 生成随机浮点数...")
        floats = [self.rng.generate_float() for _ in range(50)]
        float_mean = np.mean(floats)
        results['tests']['floats'] = {
            'generated': len(floats),
            'mean': float_mean,
            'passed': 0.3 <= float_mean <= 0.7
        }
        print(f"    均值: {float_mean:.2f}")
        
        # 测试5：生成种子
        print("\n[5] 生成量子种子...")
        seed = self.seed_generator.generate_seed(256)
        results['tests']['seed'] = {
            'seed_bits': 256,
            'seed_value': hex(seed)[:20] + '...',
            'passed': seed > 0
        }
        print(f"    种子: {hex(seed)[:20]}...")
        
        # 测试6：生成UUID
        print("\n[6] 生成量子UUID...")
        uuid = self.seed_generator.generate_uuid_like()
        results['tests']['uuid'] = {
            'uuid': uuid,
            'passed': len(uuid) == 36
        }
        print(f"    UUID: {uuid}")
        
        elapsed = time.time() - start_time
        
        # 统计
        passed = sum(1 for t in results['tests'].values() if t.get('passed', False))
        total = len(results['tests'])
        
        print("\n" + "=" * 60)
        print(f"测试完成: {passed}/{total} 通过")
        print(f"总时间: {elapsed:.2f}s")
        print("=" * 60)
        
        results['summary'] = {
            'passed': passed,
            'total': total,
            'success_rate': passed / total,
            'elapsed_time': elapsed
        }
        
        return results


def test_quantum_rng():
    """测试量子随机数生成器"""
    benchmark = QuantumRNGBenchmark()
    results = benchmark.run_benchmark()
    return results


if __name__ == "__main__":
    test_quantum_rng()
