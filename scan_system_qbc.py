#!/usr/bin/env python3
"""扫描 System/Compiler, System/Kernel, System/VM 下的 .qentl 是否都有 .qbc"""
import os, glob

ROOT = "/root/QSM"
BUILD_DIR = os.path.join(ROOT, "build", "compiled")

qbc_files = set(os.path.basename(p) for p in glob.glob(os.path.join(BUILD_DIR, "*.qbc")))

# System/ 下的所有 .qentl（排除 cli 工具）
sys_qentl = sorted(glob.glob(os.path.join(ROOT, "QEntL", "System", "**", "*.qentl"), recursive=True))
cli_skip = [p for p in sys_qentl if "/bin/cli/" in p or "/bin/platform/" in p]
sys_source = [p for p in sys_qentl if p not in cli_skip]

# 根脚本
root_scripts = sorted(glob.glob(os.path.join(ROOT, "QEntL", "scripts", "*.qentl")))

print(f"System/ 下 .qentl (含 cli): {len(sys_qentl)}")
print(f"  其中 cli/platform 工具:   {len(cli_skip)}")
print(f"  系统源码文件:             {len(sys_source)}")
print(f"根脚本 .qentl:              {len(root_scripts)}")
print()

# 检查每个文件是否有 .qbc
all_missing = []

for p in sys_source + root_scripts:
    name = os.path.splitext(os.path.basename(p))[0]
    qbc_name = name + ".qbc"
    qbc_name2 = name + ".qentl.qbc"
    qbc_path = os.path.join(BUILD_DIR, qbc_name)
    qbc_path2 = os.path.join(BUILD_DIR, qbc_name2)
    if not (os.path.exists(qbc_path) or os.path.exists(qbc_path2)):
        all_missing.append(p)

print(f"{'='*60}")
print(f"System/ + scripts 中缺失 .qbc 的文件: {len(all_missing)} 个")
print("="*60)
if all_missing:
    for p in all_missing:
        print(f"  - {os.path.relpath(p, ROOT)}")
else:
    print("  ✅ 全部有 .qbc")
