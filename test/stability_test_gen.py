#!/usr/bin/env python3
"""生成极端稳定性测试文件"""
import sys
import os

# 测试1: 大量量子指令 (>1000)
def gen_large_ops(path, n_ops=1200):
    with open(path, 'w') as f:
        f.write(f"# 大量量子指令测试: {n_ops} ops\n")
        f.write(f"init 4\n")
        for i in range(n_ops):
            q = i % 4
            gate = ['H', 'X', 'Y', 'Z', 'T', 'S', 'H', 'X'][i % 8]
            f.write(f"{gate} {q}\n")
            if i % 10 == 0:
                f.write(f"CNOT {q} {(q+1)%4}\n")
        f.write("MEASURE 0 0\n")
        f.write("PRINT 0\n")
        f.write("STOP\n")
    print(f"[GEN] {path}: {n_ops}+ gate ops")

# 测试2: 大量量子比特 (>64) — 使用简化模式
def gen_large_qubits(path, n_qubits=72):
    with open(path, 'w') as f:
        f.write(f"# 大量量子比特测试: {n_qubits} qubits\n")
        f.write(f"init {n_qubits}\n")
        for i in range(min(n_qubits, 64)):
            f.write(f"H {i}\n")
        for i in range(0, min(n_qubits, 64), 2):
            f.write(f"CNOT {i} {i+1}\n")
        f.write("MEASURE 0 0\n")
        f.write("MEASURE 1 1\n")
        f.write("PRINT 0\n")
        f.write("PRINT 1\n")
        f.write("STOP\n")
    print(f"[GEN] {path}: {n_qubits} qubits (简化模式)")

# 测试3: 复杂控制流（循环+条件） — 使用QEntL高级语法通过qcl_phase2编译
# 但我们测试bootstrap子集的极限：大量嵌套指令序列
def gen_complex_control(path):
    with open(path, 'w') as f:
        f.write("# 复杂控制流测试: 密集门+测量交替\n")
        f.write("init 8\n")
        # 交替门序列模拟控制流模式
        for cycle in range(20):
            for q in range(8):
                f.write(f"H {q}\n")
            for q in range(8):
                f.write(f"X {q}\n")
            for q in range(0, 8, 2):
                f.write(f"CNOT {q} {q+1}\n")
            f.write("BARRIER\n")
            f.write("MEASURE 0 0\n")
        f.write("PRINT 0\n")
        f.write("STOP\n")
    print(f"[GEN] {path}: 复杂控制流")

# 测试4: 极限buffer边界
def gen_buffer_boundary(path):
    with open(path, 'w') as f:
        f.write("# Buffer边界测试\n")
        f.write("init 2\n")
        # 产生接近4096字节的字节码
        for i in range(2000):
            f.write(f"H {i%2}\n")
        f.write("MEASURE 0 0\n")
        f.write("STOP\n")
    print(f"[GEN] {path}: buffer边界")

os.makedirs('test/stability', exist_ok=True)
os.chdir('/root/QSM')
gen_large_ops('test/stability/stress_1000ops.qentl', 1200)
gen_large_qubits('test/stability/stress_72qubits.qentl', 72)
gen_complex_control('test/stability/stress_complex_ctrl.qentl')
gen_buffer_boundary('test/stability/stress_buffer.qentl')
print("[DONE] 稳定性测试文件已生成")
