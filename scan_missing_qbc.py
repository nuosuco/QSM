#!/usr/bin/env python3
"""扫描 QEntL 目录，找出有 .qentl 但无对应 .qbc 的文件，并尝试编译。"""
import os, glob

ROOT = "/root/QSM"
QENTL_DIR = os.path.join(ROOT, "QEntL")
BUILD_DIR = os.path.join(ROOT, "build", "compiled")

qbc_files = set(os.path.basename(p) for p in glob.glob(os.path.join(BUILD_DIR, "*.qbc")))

model_qentl = sorted(
    p for p in glob.glob(os.path.join(QENTL_DIR, "Models", "**", "*.qentl"), recursive=True)
    if "/docs/" not in p and not p.endswith("Models_QNS_Integration_Test.qentl")
)

missing = []
found = []

for qentl_path in model_qentl:
    name = os.path.basename(qentl_path)
    base = os.path.splitext(name)[0]  # 去掉 .qentl
    rel = os.path.relpath(qentl_path, QENTL_DIR)
    parts = rel.split(os.sep)
    model_dir = parts[1]
    qbc_name = f"{model_dir}_{base}.qentl.qbc"
    if qbc_name in qbc_files:
        found.append((qentl_path, qbc_name))
    else:
        missing.append((qentl_path, qbc_name))

print("=" * 60)
print(f"扫描 QEntL/Models/ 下的模型文件")
print(f"总模型文件: {len(model_qentl)}")
print(f"已有 .qbc:  {len(found)}")
print(f"缺失 .qbc:  {len(missing)}")
print("=" * 60)
if missing:
    print(f"\n✗ 缺失 .qbc 的文件 ({len(missing)} 个):")
    for fpath, qbc in missing:
        print(f"  - {os.path.relpath(fpath, ROOT)}  -> 期望 {qbc}")
else:
    print("\n✅ 所有模型 .qentl 文件都有对应 .qbc！")
print(f"\n✓ 已有 .qbc 的文件 ({len(found)} 个):")
for fpath, qbc in found:
    print(f"  - {os.path.relpath(fpath, ROOT)}  ->  {qbc}")
