#!/usr/bin/env python3
"""Scan QSM project for .qentl/.qbc stats and bytecode details."""
import os, struct

ROOT = "/root/QSM"
qentl_files = []
qbc_files = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip .git
    if '.git' in dirpath:
        continue
    for f in filenames:
        full = os.path.join(dirpath, f)
        rel = os.path.relpath(full, ROOT)
        if f.endswith('.qentl'):
            qentl_files.append(rel)
        elif f.endswith('.qbc'):
            qbc_files.append(rel)

# Count lines per .qentl
qentl_lines = 0
qentl_by_ext = {}
for f in qentl_files:
    try:
        with open(os.path.join(ROOT, f), 'r', errors='ignore') as fh:
            lines = fh.readlines()
        qentl_lines += len(lines)
        key = f.split(os.sep)[0]
        qentl_by_ext[key] = qentl_by_ext.get(key, 0) + 1
    except:
        pass

# Bytecode analysis for .qbc
bytecode_stats = {
    '0x14_valid': 0,   # valid quantum bytecode
    '0x72_text': 0,    # text (high-level syntax)
    '0x0c_empty': 0,   # empty/STOP shell
    '0x46_magic': 0,   # QCLF_MAGIC text header
    '0x0b_other': 0,
    '0x01_other': 0,
    'other_first': 0,
    'empty_file': 0,
}
qbc_total_bytes = 0
qbc_func_count = 0
qbc_quantum_instr = 0

# Function-level stats from .qbc: count 0x14-prefixed function blocks
# A valid .qbc starts with 0x14. We count:
#   - total files with 0x14 start
#   - count 0x14 bytes across all files as "quantum instructions"
#   - estimate function count by counting 0x14 occurrences at start of logical blocks

for f in qbc_files:
    full = os.path.join(ROOT, f)
    try:
        with open(full, 'rb') as fh:
            data = fh.read()
        qbc_total_bytes += len(data)
        if len(data) == 0:
            bytecode_stats['empty_file'] += 1
            continue
        first = data[0]
        if first == 0x14:
            bytecode_stats['0x14_valid'] += 1
            # Count all 0x14 occurrences as quantum instructions
            qbc_quantum_instr += data.count(0x14)
        elif first == 0x72:
            bytecode_stats['0x72_text'] += 1
        elif first == 0x0c:
            bytecode_stats['0x0c_empty'] += 1
        elif first == 0x46:
            bytecode_stats['0x46_magic'] += 1
        elif first == 0x0b:
            bytecode_stats['0x0b_other'] += 1
        elif first == 0x01:
            bytecode_stats['0x01_other'] += 1
        else:
            bytecode_stats['other_first'] += 1
    except:
        pass

# Subdirectory breakdown for .qbc
qbc_by_dir = {}
for f in qbc_files:
    parts = f.split(os.sep)
    key = parts[0] if len(parts) > 1 else '/'
    if len(parts) >= 3 and parts[0] == 'QEntL':
        key = '/'.join(parts[:3])
    qbc_by_dir[key] = qbc_by_dir.get(key, 0) + 1

print("=" * 60)
print("QSM PROJECT STATS - LIVE SCAN")
print("=" * 60)
print(f"\n.qentl 总数: {len(qentl_files)}")
print(f".qentl 总行数: {qentl_lines}")
print(f"\n.qbc 总数: {len(qbc_files)}")
print(f".qbc 总字节数: {qbc_total_bytes}")

print(f"\n--- 字节码首字节分布 ---")
for k, v in bytecode_stats.items():
    print(f"  {k}: {v}")

print(f"\n--- 有效0x14量子字节码 ---")
print(f"  有效0x14文件数: {bytecode_stats['0x14_valid']}")
print(f"  0x14字节码指令总数: {qbc_quantum_instr}")

print(f"\n--- .qbc 子目录分布 (Top) ---")
for k, v in sorted(qbc_by_dir.items(), key=lambda x: -x[1])[:20]:
    print(f"  {k}: {v}")

print(f"\n--- .qentl 顶级目录分布 ---")
for k, v in sorted(qentl_by_ext.items(), key=lambda x: -x[1])[:20]:
    print(f"  {k}: {v}")

# Export as compact dict for MEMORY update
print("\n### JSON SUMMARY ###")
import json
summary = {
    'qentl_count': len(qentl_files),
    'qentl_lines': qentl_lines,
    'qbc_count': len(qbc_files),
    'qbc_bytes': qbc_total_bytes,
    'bytecode_0x14': bytecode_stats['0x14_valid'],
    'bytecode_0x72': bytecode_stats['0x72_text'],
    'bytecode_0x0c': bytecode_stats['0x0c_empty'],
    'bytecode_0x46': bytecode_stats['0x46_magic'],
    'quantum_instr_total': qbc_quantum_instr,
}
print(json.dumps(summary, ensure_ascii=False))
