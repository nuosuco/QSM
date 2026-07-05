#!/usr/bin/env python3
"""扫描 QEntL 目录，找出有 .qentl 但无对应 .qbc 的文件，并尝试编译。"""
import os, glob

ROOT = "/root/QSM"
QENTL_DIR = os.path.join(ROOT, "QEntL")
BUILD_DIR = os.path.join(ROOT, "build", "compiled")

# 所有 .qbc 文件集合
qbc_files = set(os.path.basename(p) for p in glob.glob(os.path.join(BUILD_DIR, "*.qbc")))

# 仅扫描 Models/ 下的 .qentl 文件（这些是需要编译成 .qbc 的模型文件）
model_qentl = sorted(
    p for p in glob.glob(os.path.join(QENTL_DIR, "Models", "**", "*.qentl"), recursive=True)
    if "/docs/" not in p and not p.endswith("Models_QNS_Integration_Test.qentl")
)

missing = []
found = []

for qentl_path in model_qentl:
    name = os.path.basename(qentl_path)
    rel = os.path.relpath(qentl_path, QENTL_DIR)
    parts = rel.split(os.sep)
    model_prefix = parts[0]  # QSM, Ref, SOM, WeQ

    # 编译产物命名规则: ModelName_filename.qentl.qbc
    qbc_name = f"{model_prefix}_{name}.qbc"
    # 也尝试不带前缀的命名
    qbc_name2 = f"{name}.qbc"

    if qbc_name in qbc_files or qbc_name2 in qbc_files:
        found.append(qentl_path)
    else:
        missing.append(qentl_path)

print("=" * 60)
print(f"扫描 QEntL/Models/ 下的模型文件")
print(f"总模型文件: {len(model_qentl)}")
print(f"已有 .qbc:  {len(found)}")
print(f"缺失 .qbc:  {len(missing)}")
print("=" * 60)
if missing:
    print("\n缺失 .qbc 的文件列表:")
    for f in missing:
        print(f"  - {os.path.relpath(f, ROOT)}")
else:
    print("\n✅ 所有模型 .qentl 文件都有对应 .qbc！")

# 额外：列出没有前缀匹配的
print("\n详细匹配检查:")
for qentl_path in model_qentl:
    name = os.path.basename(qentl_path)
    rel = os.path.relpath(qentl_path, QENTL_DIR)
    parts = rel.split(os.sep)
    model_prefix = parts[0]
    qbc_name = f"{model_prefix}_{name}.qbc"
    status = "✓" if qbc_name in qbc_files else "✗ MISSING"
    if status == "✗ MISSING":
        print(f"  {status}: {qbc_name}  <- {os.path.relpath(qentl_path, ROOT)}")
