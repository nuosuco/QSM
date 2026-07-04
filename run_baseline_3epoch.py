#!/usr/bin/env python3
"""
阶段6-7基线训练：全仓库0x14电路 × 3epoch QVM执行
输出：电路总数、总周期、总门数、失败数、按组件分类统计、与基线对比
"""
import os, subprocess, re, json, sys

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
EPOCHS = 3
BASELINE = {"circuits": 78, "cycles": 4566, "gates": 4566, "failures": 0}

# 收集所有.qbc文件（排除.git）
qbc_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath:
        dirnames[:] = []
        continue
    for f in filenames:
        if f.endswith(".qbc"):
            qbc_files.append(os.path.join(dirpath, f))

print(f"== 全仓库.qbc文件总数: {len(qbc_files)} ==", file=sys.stderr)

# 步骤1：过滤有效0x14电路
valid_circuits = []
invalid_by_head = {}
for fp in qbc_files:
    try:
        with open(fp, "rb") as fh:
            head = fh.read(1)
        if head == b'\x14':
            valid_circuits.append(fp)
        else:
            h = head.hex() if head else "empty"
            invalid_by_head[h] = invalid_by_head.get(h, 0) + 1
    except Exception as e:
        print(f"WARN read {fp}: {e}", file=sys.stderr)

print(f"== 有效0x14电路数: {len(valid_circuits)} ==", file=sys.stderr)
print(f"== 无效文件头部分布: {invalid_by_head} ==", file=sys.stderr)

# 组件分类函数
def classify(path):
    """按路径分类组件"""
    rel = os.path.relpath(path, ROOT)
    # root级
    if os.path.dirname(rel) == ".":
        return "root"
    parts = rel.split(os.sep)
    first = parts[0]
    second = parts[1] if len(parts) > 1 else ""
    if first == "QEntL":
        if second == "Models":
            return "Models(四大模型)"
        if second == "System":
            third = parts[2] if len(parts) > 2 else ""
            if third == "Kernel":
                fourth = parts[3] if len(parts) > 3 else ""
                if fourth == "neural":
                    return "QNS(neural)"
                if fourth == "filesystem":
                    return "QDFS"
                return "QNS(kernel跨层)"
            if third == "VM":
                return "VM"
            if third == "Compiler":
                return "QCL模块"
            if third == "Platform":
                return "Platform"
            if third == "Deployment":
                return "Deployment"
            return "QEntL/System"
        if second == "scripts":
            return "scripts"
    if first == "QCL模块":
        return "QCL模块"
    if first == "test":
        return "test"
    if first == "test_output":
        return "test_output"
    if first == "test_programs":
        return "test_programs"
    if first == "tests":
        return "tests"
    if first == "docs":
        return "docs"
    if first == "web":
        return "web"
    return "other"

# 按组件分组
from collections import defaultdict
groups = defaultdict(list)
for fp in valid_circuits:
    groups[classify(fp)].append(fp)

print(f"== 按组件分类电路数 ==", file=sys.stderr)
for comp in sorted(groups.keys()):
    print(f"  {comp}: {len(groups[comp])}电路", file=sys.stderr)

# 步骤2：对每个电路执行 QVM × EPOCHS
CYCLE_RE = re.compile(r'(\d+)\s*周期')
GATE_RE = re.compile(r'(\d+)\s*门')

results = []  # (comp, relpath, total_cycles, total_gates, fail_count)
total_cycles_all = 0
total_gates_all = 0
total_failures = 0
total_executions = 0

for comp in sorted(groups.keys()):
    circuits = groups[comp]
    for fp in circuits:
        rel = os.path.relpath(fp, ROOT)
        c_cycles = 0
        c_gates = 0
        c_fails = 0
        for ep in range(EPOCHS):
            try:
                out = subprocess.run(
                    [QVM, fp],
                    capture_output=True, text=True, timeout=30
                ).stdout
                total_executions += 1
                cyc = CYCLE_RE.findall(out)
                gts = GATE_RE.findall(out)
                cc = int(cyc[-1]) if cyc else 0
                gg = int(gts[-1]) if gts else 0
                c_cycles += cc
                c_gates += gg
            except subprocess.TimeoutExpired:
                c_fails += 1
                total_executions += 1
            except Exception as e:
                c_fails += 1
                total_executions += 1
        total_cycles_all += c_cycles
        total_gates_all += c_gates
        total_failures += c_fails
        results.append((comp, rel, c_cycles, c_gates, c_fails))

# 步骤3：按组件汇总
comp_stats = defaultdict(lambda: {"circuits": 0, "cycles": 0, "gates": 0, "failures": 0})
for comp, rel, cc, gg, ff in results:
    s = comp_stats[comp]
    s["circuits"] += 1
    s["cycles"] += cc
    s["gates"] += gg
    s["failures"] += ff

# 输出结果
print("\n" + "="*70, file=sys.stderr)
print("阶段6-7基线训练结果", file=sys.stderr)
print("="*70, file=sys.stderr)
print(f"\n电路总数: {len(valid_circuits)}", file=sys.stderr)
print(f"总执行次数: {total_executions} ({len(valid_circuits)}电路 × {EPOCHS}epoch)", file=sys.stderr)
print(f"总周期: {total_cycles_all}", file=sys.stderr)
print(f"总门数: {total_gates_all}", file=sys.stderr)
print(f"失败数: {total_failures}", file=sys.stderr)

print("\n--- 按组件分类统计 ---", file=sys.stderr)
print(f"{'组件':<20} {'电路数':>6} {'周期':>8} {'门数':>8} {'失败':>6}", file=sys.stderr)
print("-"*50, file=sys.stderr)
for comp in sorted(comp_stats.keys()):
    s = comp_stats[comp]
    print(f"{comp:<20} {s['circuits']:>6} {s['cycles']:>8} {s['gates']:>8} {s['failures']:>6}", file=sys.stderr)

# 步骤4：与基线对比
print("\n--- 与基线对比 ---", file=sys.stderr)
bl = BASELINE
actual_circuits = len(valid_circuits)
actual_cycles = total_cycles_all
actual_gates = total_gates_all
actual_failures = total_failures

def deviation(actual, base):
    if base == 0:
        return "N/A" if actual == 0 else "∞"
    d = (actual - base) / base * 100
    return f"{d:+.1f}%"

print(f"{'指标':<10} {'基线':>8} {'实际':>8} {'偏差':>10}", file=sys.stderr)
print("-"*40, file=sys.stderr)
print(f"{'电路数':<10} {bl['circuits']:>8} {actual_circuits:>8} {deviation(actual_circuits, bl['circuits']):>10}", file=sys.stderr)
print(f"{'总周期':<10} {bl['cycles']:>8} {actual_cycles:>8} {deviation(actual_cycles, bl['cycles']):>10}", file=sys.stderr)
print(f"{'总门数':<10} {bl['gates']:>8} {actual_gates:>8} {deviation(actual_gates, bl['gates']):>10}", file=sys.stderr)
print(f"{'失败数':<10} {bl['failures']:>8} {actual_failures:>8} {deviation(actual_failures, bl['failures']):>10}", file=sys.stderr)

# 判定偏差是否>10%
def abs_pct(a, b):
    if b == 0:
        return 0.0 if a == 0 else 999.0
    return abs(a - b) / b * 100

deviations = {
    "电路数": abs_pct(actual_circuits, bl["circuits"]),
    "总周期": abs_pct(actual_cycles, bl["cycles"]),
    "总门数": abs_pct(actual_gates, bl["gates"]),
}

any_over_10 = any(v > 10 for v in deviations.values())
if any_over_10:
    print("\n⚠️ 偏差>10%的指标:", file=sys.stderr)
    for k, v in deviations.items():
        if v > 10:
            base_k = bl.get(k.replace("数",""), 0) if k != "总周期" and k != "总门数" else (bl["cycles"] if k == "总周期" else bl["gates"])
            print(f"  {k}: {v:.1f}%", file=sys.stderr)
else:
    print("\n✅ 所有指标偏差≤10%，与基线一致。", file=sys.stderr)

# JSON摘要
summary = {
    "total_qbc": len(qbc_files),
    "valid_circuits_0x14": len(valid_circuits),
    "invalid_head_bytes": invalid_by_head,
    "executions": total_executions,
    "total_cycles": total_cycles_all,
    "total_gates": total_gates_all,
    "total_failures": total_failures,
    "component_stats": dict(comp_stats),
    "baseline": bl,
    "deviations_pct": deviations,
    "any_over_10pct": any_over_10,
}
print("\n" + json.dumps(summary, ensure_ascii=False, indent=2), file=sys.stderr)
print(json.dumps(summary, ensure_ascii=False, indent=2))
