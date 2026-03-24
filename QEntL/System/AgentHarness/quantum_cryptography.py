#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子密码学模块
实现量子密钥分发和量子加密功能

主要功能：
1. BB84量子密钥分发协议
2. 量子一次一密加密
3. 量子哈希函数
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import hashlib
import time
import secrets

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    import qiskit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


class BB84Protocol:
    """BB84量子密钥分发协议"""
    
    def __init__(self, key_length: int = 256):
        self.key_length = key_length
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
        
    def generate_basis_choices(self, length: int) -> List[int]:
        """生成基底选择序列"""
        return [secrets.randbelow(2) for _ in range(length)]
    
    def encode_qubit(self, bit: int, basis: int) -> Dict:
        """编码量子比特"""
        results = {
            'bit': bit,
            'basis': basis,  # 0 = Z基, 1 = X基
            'encoded': False
        }
        
        if not QISKIT_AVAILABLE:
            results['classical_fallback'] = True
            return results
        
        try:
            qr = QuantumRegister(1, 'q')
            qc = QuantumCircuit(qr)
            
            # 编码
            if bit == 1:
                qc.x(0)
            
            # 基底变换
            if basis == 1:  # X基
                qc.h(0)
            
            results['encoded'] = True
            results['circuit'] = qc
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def measure_qubit(self, basis: int) -> int:
        """测量量子比特"""
        if not QISKIT_AVAILABLE:
            return secrets.randbelow(2)
        
        try:
            qr = QuantumRegister(1, 'q')
            cr = ClassicalRegister(1, 'c')
            qc = QuantumCircuit(qr, cr)
            
            # Hadamard创建叠加态
            qc.h(0)
            
            # 根据基底选择测量
            if basis == 1:  # X基测量
                qc.h(0)
            
            qc.measure(qr, cr)
            
            job = self.simulator.run(qc, shots=1)
            result = job.result().get_counts()
            
            return int(list(result.keys())[0])
        except:
            return secrets.randbelow(2)
    
    def simulate_transmission(self, n_qubits: int = 100) -> Dict:
        """模拟量子传输"""
        results = {
            'n_qubits': n_qubits,
            'alice_bits': [],
            'alice_bases': [],
            'bob_bases': [],
            'bob_measurements': [],
            'matching_indices': [],
            'raw_key_length': 0
        }
        
        # Alice生成随机比特和基底
        results['alice_bits'] = [secrets.randbelow(2) for _ in range(n_qubits)]
        results['alice_bases'] = self.generate_basis_choices(n_qubits)
        
        # Bob选择测量基底
        results['bob_bases'] = self.generate_basis_choices(n_qubits)
        
        # Bob测量
        for i in range(n_qubits):
            if QISKIT_AVAILABLE:
                try:
                    qr = QuantumRegister(1, 'q')
                    cr = ClassicalRegister(1, 'c')
                    qc = QuantumCircuit(qr, cr)
                    
                    # Alice编码
                    if results['alice_bits'][i] == 1:
                        qc.x(0)
                    if results['alice_bases'][i] == 1:
                        qc.h(0)
                    
                    # Bob测量
                    if results['bob_bases'][i] == 1:
                        qc.h(0)
                    
                    qc.measure(qr, cr)
                    
                    job = self.simulator.run(qc, shots=1)
                    measurement = int(list(job.result().get_counts().keys())[0])
                    results['bob_measurements'].append(measurement)
                except:
                    results['bob_measurements'].append(secrets.randbelow(2))
            else:
                # 经典降级
                if results['alice_bases'][i] == results['bob_bases'][i]:
                    results['bob_measurements'].append(results['alice_bits'][i])
                else:
                    results['bob_measurements'].append(secrets.randbelow(2))
        
        # 找出基底匹配的索引
        for i in range(n_qubits):
            if results['alice_bases'][i] == results['bob_bases'][i]:
                results['matching_indices'].append(i)
        
        results['raw_key_length'] = len(results['matching_indices'])
        
        return results
    
    def generate_key(self, transmission_result: Dict) -> Dict:
        """从传输结果生成密钥"""
        results = {
            'raw_key_alice': [],
            'raw_key_bob': [],
            'matching': False,
            'key': None
        }
        
        # 提取匹配位置的比特
        for idx in transmission_result['matching_indices']:
            results['raw_key_alice'].append(transmission_result['alice_bits'][idx])
            results['raw_key_bob'].append(transmission_result['bob_measurements'][idx])
        
        # 验证匹配
        results['matching'] = results['raw_key_alice'] == results['raw_key_bob']
        
        if results['matching']:
            results['key'] = ''.join(map(str, results['raw_key_alice']))
        
        return results
    
    def perform_qkd(self, n_qubits: int = 256) -> Dict:
        """执行完整QKD流程"""
        print("=" * 60)
        print("BB84量子密钥分发协议")
        print("=" * 60)
        
        results = {
            'qiskit_available': QISKIT_AVAILABLE,
            'transmission': None,
            'key_generation': None,
            'success': False
        }
        
        # 步骤1：量子传输
        print("\n[1] 模拟量子传输...")
        transmission = self.simulate_transmission(n_qubits)
        results['transmission'] = transmission
        print(f"    发送量子比特: {n_qubits}")
        print(f"    基底匹配数: {transmission['raw_key_length']}")
        
        # 步骤2：密钥生成
        print("\n[2] 生成密钥...")
        key_gen = self.generate_key(transmission)
        results['key_generation'] = key_gen
        
        if key_gen['matching']:
            print(f"    ✅ 密钥匹配成功")
            print(f"    密钥长度: {len(key_gen['key'])} 比特")
            results['success'] = True
        else:
            print(f"    ❌ 密钥不匹配")
        
        print("\n" + "=" * 60)
        
        return results


class QuantumOneTimePad:
    """量子一次一密"""
    
    def __init__(self):
        self.bb84 = BB84Protocol()
    
    def encrypt(self, message: str, key: str) -> Dict:
        """使用量子密钥加密"""
        results = {
            'message': message,
            'encrypted': False,
            'ciphertext': None
        }
        
        if len(key) < len(message) * 8:
            results['error'] = '密钥长度不足'
            return results
        
        # 将消息转换为二进制
        binary_message = ''.join(format(ord(c), '08b') for c in message)
        
        # XOR加密
        ciphertext = ''
        for i, bit in enumerate(binary_message):
            ciphertext += str(int(bit) ^ int(key[i]))
        
        results['encrypted'] = True
        results['ciphertext'] = ciphertext
        results['key_used'] = len(binary_message)
        
        return results
    
    def decrypt(self, ciphertext: str, key: str) -> Dict:
        """使用量子密钥解密"""
        results = {
            'ciphertext': ciphertext,
            'decrypted': False,
            'message': None
        }
        
        if len(key) < len(ciphertext):
            results['error'] = '密钥长度不足'
            return results
        
        # XOR解密
        binary_message = ''
        for i, bit in enumerate(ciphertext):
            binary_message += str(int(bit) ^ int(key[i]))
        
        # 转换为字符串
        message = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            message += chr(int(byte, 2))
        
        results['decrypted'] = True
        results['message'] = message
        
        return results
    
    def perform_encryption(self, message: str) -> Dict:
        """执行完整加密流程"""
        print("=" * 60)
        print("量子一次一密加密")
        print("=" * 60)
        
        results = {
            'qkd': None,
            'encryption': None,
            'decryption': None,
            'success': False
        }
        
        # 步骤1：生成量子密钥
        print("\n[1] 生成量子密钥...")
        qkd_result = self.bb84.perform_qkd(n_qubits=len(message) * 16)
        results['qkd'] = qkd_result
        
        if not qkd_result['success']:
            print("    ❌ 密钥生成失败")
            return results
        
        key = qkd_result['key_generation']['key']
        
        # 步骤2：加密
        print("\n[2] 加密消息...")
        encrypt_result = self.encrypt(message, key)
        results['encryption'] = encrypt_result
        
        if encrypt_result['encrypted']:
            print(f"    ✅ 加密成功")
            print(f"    密文长度: {len(encrypt_result['ciphertext'])} 比特")
        
        # 步骤3：解密
        print("\n[3] 解密验证...")
        decrypt_result = self.decrypt(encrypt_result['ciphertext'], key)
        results['decryption'] = decrypt_result
        
        if decrypt_result['decrypted']:
            print(f"    ✅ 解密成功")
            print(f"    原文: {decrypt_result['message']}")
            results['success'] = True
        
        print("\n" + "=" * 60)
        
        return results


class QuantumHash:
    """量子哈希函数"""
    
    def __init__(self):
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
    
    def hash_message(self, message: str, output_bits: int = 256) -> Dict:
        """计算量子哈希"""
        results = {
            'message': message,
            'output_bits': output_bits,
            'hash': None,
            'qiskit_used': QISKIT_AVAILABLE
        }
        
        # 将消息转换为数值
        message_bytes = message.encode('utf-8')
        message_int = int.from_bytes(message_bytes, 'big')
        
        # 使用经典SHA-256作为基础
        sha256_hash = hashlib.sha256(message_bytes).digest()
        
        if QISKIT_AVAILABLE:
            # 量子增强：使用量子随机性混合
            try:
                quantum_randomness = []
                n_qubits = min(8, output_bits // 32)
                
                for _ in range(n_qubits):
                    qr = QuantumRegister(1, 'q')
                    cr = ClassicalRegister(1, 'c')
                    qc = QuantumCircuit(qr, cr)
                    qc.h(0)
                    qc.measure(qr, cr)
                    
                    job = self.simulator.run(qc, shots=1)
                    bit = int(list(job.result().get_counts().keys())[0])
                    quantum_randomness.append(bit)
                
                # 混合量子随机性和经典哈希
                quantum_int = int(''.join(map(str, quantum_randomness)), 2)
                combined = int.from_bytes(sha256_hash, 'big') ^ (quantum_int << (output_bits - n_qubits))
                
                results['hash'] = hex(combined % (2 ** output_bits))[2:].zfill(output_bits // 4)
                results['quantum_enhanced'] = True
                
            except Exception as e:
                results['hash'] = sha256_hash.hex()
                results['quantum_enhanced'] = False
                results['error'] = str(e)
        else:
            results['hash'] = sha256_hash.hex()
            results['quantum_enhanced'] = False
        
        return results
    
    def verify_hash(self, message: str, expected_hash: str) -> Dict:
        """验证哈希"""
        results = {
            'message': message,
            'expected_hash': expected_hash,
            'verified': False
        }
        
        hash_result = self.hash_message(message, len(expected_hash) * 4)
        actual_hash = hash_result['hash']
        
        results['actual_hash'] = actual_hash
        results['verified'] = actual_hash == expected_hash
        
        return results


class QuantumCryptographySuite:
    """量子密码学套件"""
    
    def __init__(self):
        self.bb84 = BB84Protocol()
        self.otp = QuantumOneTimePad()
        self.qhash = QuantumHash()
    
    def run_demonstration(self) -> Dict:
        """运行演示"""
        print("=" * 60)
        print("量子密码学套件演示")
        print("=" * 60)
        
        results = {
            'qiskit_available': QISKIT_AVAILABLE,
            'tests': {}
        }
        
        # 测试1：BB84 QKD
        print("\n[1] 测试BB84量子密钥分发...")
        qkd_result = self.bb84.perform_qkd(n_qubits=128)
        results['tests']['bb84'] = qkd_result
        
        # 测试2：量子哈希
        print("\n[2] 测试量子哈希...")
        hash_result = self.qhash.hash_message("Hello, Quantum World!")
        print(f"    消息: Hello, Quantum World!")
        print(f"    哈希: {hash_result['hash'][:32]}...")
        results['tests']['hash'] = hash_result
        
        print("\n" + "=" * 60)
        print("量子密码学演示完成")
        print("=" * 60)
        
        return results


def test_quantum_cryptography():
    """测试量子密码学"""
    suite = QuantumCryptographySuite()
    results = suite.run_demonstration()
    return results


if __name__ == "__main__":
    test_quantum_cryptography()
