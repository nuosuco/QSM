#!/usr/bin/env python3
"""QVM全量审计脚本 - 扫描所有.qbc文件，过滤0x14有效电路，执行qvm_bootstrap审计"""
import os
import subprocess
import re
import sys

QSM_ROOT = '/root/QSM'
QVM_BIN = os.path.join(QSM_ROOT, 'bin/qvm_bootstrap')
KEY_CIRCUITS = [
    'QEntL/System/Kernel/neural/qns_training_circuit.qbc',
    'QEntL/System/Kernel/neural/qns_backprop_circuit.qbc',
    'QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc',
    'QEntL/System/Kernel/grover_search_circuit.qbc',
    'QEntL/Models/QSM/qsm_entanglement_circuit.qbc',
    'QEntL/Models/SOM/som_transaction_circuit.qbc',
    'QEntL/Models/WeQ/weq_learning_circuit.qbc',
    'QEntL/Models/Ref/ref_monitoring_circuit.qbc',
]

# Step 1: 收集所有.qbc文件（排除.git）
qbc_files = []
for root, dirs, files in os.walk(QSM_ROOT):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.qbc'):
            qbc_files.append(os.path.join(root, f))

print(f"=== 扫描完成：共发现 {len(qbc_files)} 个 .qbc 文件 ===\n")

# Step 2: 按首字节分类
valid_0x14 = []
invalid_0x72 = []
other_bytes = []
byte_stats = {}

for fp in qbc_files:
    try:
        with open(fp, 'rb') as fh:
            b = fh.read(1)
        hex_val = b.hex()
        byte_stats[hex_val] = byte_stats.get(hex_val, 0) + 1
        if b == b'\x14':
            valid_0x14.append(fp)
        elif b == b'\x72':
            invalid_0x72.append(fp)
        else:
            other_bytes.append((fp, hex_val))
    except Exception as e:
        print(f"[ERROR] 读取失败: {fp} - {e}")

print("=== 首字节统计 ===")
for hex_v in sorted(byte_stats.keys()):
    print(f"  0x{hex_v}: {byte_stats[hex_v]} 个文件")
print(f"\n有效电路 (0x14): {len(valid_0x14)} 个")
print(f"无效电路 (0x72): {len(invalid_0x72)} 个")
print(f"其他字节: {len(other_bytes)} 个")

# Step 3: 对每个0x14文件执行qvm_bootstrap
results = []  # (filepath, status, cycles, gates, error_msg)
pattern = re.compile(r'执行完成:\s*(\d+)\s*周期,\s*(\d+)\s*门操作')

print(f"\n=== 开始执行QVM审计 ({len(valid_0x14)} 个文件) ===\n")

pass_count = 0
fail_count = 0
fail_list = []

for i, fp in enumerate(valid_0x14, 1):
    rel_path = os.path.relpath(fp, QSM_ROOT)
    try:
        proc = subprocess.run(
            [QVM_BIN, fp],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=QSM_ROOT,
        )
        combined = proc.stdout + proc.stderr
        m = pattern.search(combined)
        if m:
            cycles = int(m.group(1))
            gates = int(m.group(2))
            status = 'PASS'
            pass_count += 1
            results.append((rel_path, status, cycles, gates, ''))
            # 标记关键电路
            if fp in KEY_CIRCUITS or rel_path in KEY_CIRCUITS:
                print(f"  [{i}/{len(valid_0x14)}] ⭐ KEY [{status}] {rel_path} -> {cycles}周期, {gates}门")
            else:
                print(f"  [{i}/{len(valid_0x14)}]     [{status}] {rel_path} -> {cycles}周期, {gates}门")
        else:
            status = 'FAIL'
            fail_count += 1
            fail_list.append(rel_path)
            err = combined.strip()[-200:] if combined.strip() else '无输出'
            results.append((rel_path, status, 0, 0, err))
            print(f"  [{i}/{len(valid_0x14)}] ❌ [{status}] {rel_path} -> 无完成标记 (输出: {err[:100]})")
    except subprocess.TimeoutExpired:
        fail_count += 1
        fail_list.append(rel_path)
        results.append((rel_path, 'TIMEOUT', 0, 0, '超时30秒'))
        print(f"  [{i}/{len(valid_0x14)}] ⏱️ [TIMEOUT] {rel_path} -> 超时30秒")
    except Exception as e:
        fail_count += 1
        fail_list.append(rel_path)
        results.append((rel_path, 'ERROR', 0, 0, str(e)))
        print(f"  [{i}/{len(valid_0x14)}] 💥 [ERROR] {rel_path} -> {e}")

# Step 4: 汇总报告
print("\n" + "=" * 60)
print("📊 QVM全量审计报告")
print("=" * 60)
print(f"  (a) 总有效0x14电路数: {len(valid_0x14)}")
print(f"  (b) PASS数量: {pass_count}")
print(f"  (c) FAIL数量: {fail_count}")
if fail_list:
    print(f"\n  ❌ 失败文件列表 ({len(fail_list)}):")
    for f in fail_list:
        print(f"    - {f}")

# Step 5: 关键电路详细报告
print("\n" + "=" * 60)
print("⭐ 8个关键电路详细验证")
print("=" * 60)
for kc in KEY_CIRCUITS:
    fp_full = os.path.join(QSM_ROOT, kc)
    if os.path.exists(fp_full):
        # 找结果
        found = False
        for r in results:
            if r[0] == kc:
                print(f"  ⭐ {kc}")
                print(f"     状态: {r[1]}, 周期: {r[2]}, 门操作: {r[3]}")
                found = True
                break
        if not found:
            print(f"  ⭐ {kc} -> 未在审计结果中找到")
    else:
        print(f"  ❌ {kc} -> 文件不存在")

# 检查是否有类似grover的文件
print("\n=== 查找类似grover_search的电路 ===")
for fp in valid_0x14:
    rel = os.path.relpath(fp, QSM_ROOT)
    if 'grover' in rel.lower():
        print(f"  找到: {rel}")

print("\n审计完成。")
