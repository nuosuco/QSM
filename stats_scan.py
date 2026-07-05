#!/usr/bin/env python3
"""QSM 项目进度扫描：.qentl/.qbc 数量、字节码首字节分布、指令计数。"""
import os, json
from collections import Counter

ROOT = "/root/QSM"
qentl, qbc = [], []
qentl_by_dir, qbc_by_dir = Counter(), Counter()

for dp, _, fs in os.walk(ROOT):
    if '.git' in dp:
        continue
    for f in fs:
        rel = os.path.relpath(os.path.join(dp, f), ROOT)
        if f.endswith('.qentl'):
            qentl.append(rel); qentl_by_dir[rel.split(os.sep)[0]] += 1
        elif f.endswith('.qbc'):
            qbc.append(rel)
            parts = rel.split(os.sep)
            key = '/'.join(parts[:3]) if len(parts) >= 3 and parts[0] == 'QEntL' else (parts[0] or '/')
            qbc_by_dir[key] += 1

# .qentl 行数
qentl_lines = sum(len(open(os.path.join(ROOT, f), 'r', errors='ignore').readlines()) for f in qentl)

# .qbc 字节码分析
stats = Counter()
total_bytes = 0
quantum_instr = 0
for f in qbc:
    try:
        data = open(os.path.join(ROOT, f), 'rb').read()
        total_bytes += len(data)
        if not data:
            stats['empty'] += 1; continue
        key = {0x14: '0x14_valid', 0x72: '0x72_text', 0x0c: '0x0c_empty', 0x46: '0x46_magic', 0x0b: '0x0b', 0x01: '0x01'}.get(data[0], 'other')
        stats[key] += 1
        if data[0] == 0x14:
            quantum_instr += data.count(0x14)
    except Exception:
        pass

# 输出
SEP = "=" * 60
print(SEP)
print("QSM PROJECT STATS - LIVE SCAN")
print(SEP)
print(f"\n.qentl 总数: {len(qentl)}")
print(f".qentl 总行数: {qentl_lines}")
print(f"\n.qbc 总数: {len(qbc)}")
print(f".qbc 总字节数: {total_bytes}")
print(f"\n--- 字节码首字节分布 ---")
for k in ['0x14_valid', '0x72_text', '0x0c_empty', '0x46_magic', '0x0b', '0x01', 'other', 'empty']:
    if stats[k]: print(f"  {k}: {stats[k]}")
print(f"\n--- 有效0x14量子字节码 ---")
print(f"  有效0x14文件数: {stats['0x14_valid']}")
print(f"  0x14字节码指令总数: {quantum_instr}")
print(f"\n--- .qbc 子目录分布 (Top) ---")
for k, v in qbc_by_dir.most_common(20):
    print(f"  {k}: {v}")
print(f"\n--- .qentl 顶级目录分布 ---")
for k, v in qentl_by_dir.most_common(20):
    print(f"  {k}: {v}")
print("\n### JSON SUMMARY ###")
summary = {
    'qentl_count': len(qentl), 'qentl_lines': qentl_lines,
    'qbc_count': len(qbc), 'qbc_bytes': total_bytes,
    'bytecode_0x14': stats['0x14_valid'],
    'bytecode_0x72': stats['0x72_text'],
    'bytecode_0x0c': stats['0x0c_empty'],
    'bytecode_0x46': stats['0x46_magic'],
    'quantum_instr_total': quantum_instr,
}
print(json.dumps(summary, ensure_ascii=False))
