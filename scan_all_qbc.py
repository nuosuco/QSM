#!/usr/bin/env python3
"""全面扫描: 所有 .qentl 文件是否都有对应 .qbc（含 QCL 等根目录文件）"""
import os, glob

ROOT = "/root/QSM"
QENTL_DIR = os.path.join(ROOT, "QEntL")
BUILD_DIR = os.path.join(ROOT, "build", "compiled")

qbc_files = set(os.path.basename(p) for p in glob.glob(os.path.join(BUILD_DIR, "*.qbc")))

# 收集 QEntL 下所有 .qentl（排除 web/apps 和 cli 工具）
all_qentl = sorted(glob.glob(os.path.join(QENTL_DIR, "**", "*.qentl"), recursive=True))
qentl = [p for p in all_qentl
         if "web/apps" not in p
         and not p.endswith("Models_QNS_Integration_Test.qentl")]

# 根目录 .qentl
root_qentl = glob.glob(os.path.join(ROOT, "*.qentl"))

print(f"QEntL/ 下 .qentl: {len(qentl)} (排除了 web/apps/cli/Integration_Test)")
print(f"根目录 .qentl:   {len(root_qentl)}")
print(f"build/compiled/ 下 .qbc: {len(qbc_files)}")
print()

# 已知 .qbc 命名规则:
#  1) Models/{dir}/{name}.qentl  -> {dir}_{name}.qentl.qbc
#  2) docs/{dir}/{name}.qentl  -> {dir}_{name}.qentl.qbc (文档也有)
#  3) QCL 根目录 .qentl  -> QCL引导器.qbc / QVM.qbc 等特殊命名
#  4) web/ 下 .qentl -> web 下同名 .qbc（不在 build/compiled/）

docs_qentl = sorted(p for p in glob.glob(os.path.join(QENTL_DIR, "Models", "**", "*.qentl"), recursive=True)
                    if "/docs/" in p)
missing_docs = []
for p in docs_qentl:
    name = os.path.splitext(os.path.basename(p))[0]
    parts = p.split(os.sep)
    idx = parts.index("docs")
    model_dir = parts[idx-1]
    qbc = f"{model_dir}_{name}.qentl.qbc"
    if qbc not in qbc_files:
        missing_docs.append((p, qbc))

print(f"{'='*60}")
print(f"文档文件 (/docs/) 检查: {len(docs_qentl)} 个")
if missing_docs:
    print(f"  缺失: {len(missing_docs)} 个")
    for p, qbc in missing_docs:
        print(f"    - {os.path.relpath(p, ROOT)}  ->  {qbc}")
else:
    print("  ✅ 全部有 .qbc")

# 根目录 .qentl 特殊检查
print(f"\n{'='*60}")
print(f"根目录 .qentl 检查:")
for p in root_qentl:
    base = os.path.basename(p)
    qbc_base = base.replace(".qentl", ".qbc")
    qbc_path = os.path.join(ROOT, qbc_base)
    print(f"  - {base}  ->  {qbc_base}  {'✓' if os.path.exists(qbc_path) else '✗ MISSING'}")

# QCL 模块
print(f"\n{'='*60}")
print(f"QCL模块/ 下 .qentl:")
for p in sorted(glob.glob(os.path.join(ROOT, "QCL模块", "**", "*.qentl"), recursive=True)):
    name = os.path.splitext(os.path.basename(p))[0]
    qbc_path = os.path.join(os.path.dirname(p), name + ".qbc")
    qbc_build = os.path.join(BUILD_DIR, name + ".qbc")
    print(f"  - {os.path.relpath(p, ROOT)}  ->  {'✓' if os.path.exists(qbc_path) or os.path.exists(qbc_build) else '✗ MISSING'}")
