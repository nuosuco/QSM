#!/usr/bin/env python3
"""QVM 全量审计：只审计头部为 0x14 的有效量子电路 .qbc 文件。"""
import subprocess, os, sys

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
TIMEOUT = 30  # 单文件超时秒数

# 1. 扫描所有 .qbc
qbc_files = []
for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        if fn.endswith(".qbc"):
            qbc_files.append(os.path.join(dirpath, fn))

qbc_files.sort()
total = len(qbc_files)

# 2. 分类：0x14 / 0x72 / other
valid_0x14 = []
invalid_0x72 = []
other = []

for f in qbc_files:
    try:
        with open(f, "rb") as fh:
            first = fh.read(1)
            if not first:
                other.append((f, "empty"))
                continue
            b = first[0]
            if b == 0x14:
                valid_0x14.append(f)
            elif b == 0x72:
                invalid_0x72.append(f)
            else:
                other.append((f, f"0x{b:02x}"))
    except Exception as e:
        other.append((f, f"error:{e}"))

print(f"=== 扫描结果 ===")
print(f"总 .qbc 文件数: {total}")
print(f"0x14 有效量子电路: {len(valid_0x14)}")
print(f"0x72 无效文本(含 def/import): {len(invalid_0x72)}")
print(f"其他头部: {len(other)}")
if other:
    for f, reason in other:
        print(f"  {reason}: {f}")

# 3. 对每个 0x14 文件执行 QVM
print(f"\n=== QVM 执行 (0x14 文件, 共 {len(valid_0x14)}) ===")
passed = []
failed = []

for i, f in enumerate(valid_0x14):
    rel = os.path.relpath(f, ROOT)
    try:
        r = subprocess.run(
            [QVM, f],
            capture_output=True, timeout=TIMEOUT, cwd=ROOT
        )
        if r.returncode == 0:
            passed.append(rel)
        else:
            failed.append((rel, r.returncode, r.stderr.decode("utf-8", errors="replace")[:200]))
    except subprocess.TimeoutExpired:
        failed.append((rel, "TIMEOUT", ""))
    except Exception as e:
        failed.append((rel, "ERROR", str(e)[:200]))

    # 进度
    if (i + 1) % 20 == 0 or (i + 1) == len(valid_0x14):
        print(f"  [{i+1}/{len(valid_0x14)}] ...", flush=True)

# 4. 汇总
print(f"\n=== 最终统计 ===")
print(f"0x14 文件数: {len(valid_0x14)}")
print(f"PASS (exit 0): {len(passed)}")
print(f"FAIL (exit !=0): {len(failed)}")
print(f"0x72 文件数: {len(invalid_0x72)}")

if failed:
    print(f"\n=== 失败文件列表 ({len(failed)}) ===")
    for rel, code, err in failed:
        err_short = err.replace("\n", " ").strip()[:120]
        print(f"  [{code}] {rel}  |  {err_short}")

# 写结果文件
result_path = os.path.join(ROOT, "qvm_audit_result.txt")
with open(result_path, "w") as out:
    out.write(f"QVM 全量审计报告\n")
    out.write(f"{'='*60}\n")
    out.write(f"总 .qbc 文件数: {total}\n")
    out.write(f"0x14 有效量子电路: {len(valid_0x14)}\n")
    out.write(f"PASS: {len(passed)}\n")
    out.write(f"FAIL: {len(failed)}\n")
    out.write(f"0x72 无效文本: {len(invalid_0x72)}\n")
    out.write(f"其他头部: {len(other)}\n")
    out.write(f"\n失败文件:\n")
    for rel, code, err in failed:
        out.write(f"  [{code}] {rel}\n")
    out.write(f"\nPASS 文件:\n")
    for rel in passed:
        out.write(f"  {rel}\n")
print(f"\n结果已写入: {result_path}")
