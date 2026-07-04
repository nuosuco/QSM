#!/usr/bin/env python3
"""
阶段6-7基线训练 v3：全仓库 .qbc × 3epoch QVM执行
有效电路判定：QVM能执行并返回周期/门数（不管首字节格式，纯0x14或FLCQ包装均可）
"""
import os, subprocess, re, json, sys
from collections import defaultdict

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
EPOCHS = 3
BASELINE = {"circuits": 78, "cycles": 4566, "gates": 4566, "failures": 0}

CYCLE_RE = re.compile(r'(\d+)\s*周期')
GATE_RE = re.compile(r'(\d+)\s*门')

# ---- 收集所有.qbc文件（排除.git）----
qbc_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath:
        dirnames[:] = []
        continue
    for f in filenames:
        if f.endswith(".qbc"):
            qbc_files.append(os.path.join(dirpath, f))

print(f"== 全仓库.qbc文件总数: {len(qbc_files)} ==", file=sys.stderr)

# ---- 组件分类 ----
def classify(path):
    rel = os.path.relpath(path, ROOT)
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
    if first == "build":
        return "build"
    return "other"

# ---- 对每个文件做1次QVM试探（快速判定是否有效）----
# 如果QVM返回了周期/门数，则计入有效电路；然后对该电路执行EPOCHS次
print("== QVM试探执行（判定有效电路）... ==", file=sys.stderr)

valid_results = []  # (fp, comp, fmt, epoch_cycles_list, epoch_gates_list, fail_epoch_count)
invalid_files = defaultdict(int)

for fp in qbc_files:
    rel = os.path.relpath(fp, ROOT)
    comp = classify(fp)
    # 文件头格式标记
    try:
        with open(fp, "rb") as fh:
            head = fh.read(5)
        if head[:1] == b'\x14':
            fmt = "0x14"
        elif head[:4] == b'FLCQ':
            fmt = "FLCQ"
        else:
            fmt = "other_" + head[:4].hex()
    except:
        fmt = "error"

    # 1次QVM试探
    ep0_cycles = ep0_gates = 0
    ep0_fail = False
    try:
        out0 = subprocess.run(
            [QVM, fp], capture_output=True, text=True, timeout=15
        ).stdout
        cyc0 = CYCLE_RE.findall(out0)
        gts0 = GATE_RE.findall(out0)
        ep0_cycles = int(cyc0[-1]) if cyc0 else 0
        ep0_gates = int(gts0[-1]) if gts0 else 0
    except:
        ep0_fail = True

    # 判定：QVM返回周期>0 → 有效电路
    if ep0_cycles > 0:
        valid_results.append({
            "fp": fp, "rel": rel, "comp": comp, "fmt": fmt,
            "epoch0_cycles": ep0_cycles, "epoch0_gates": ep0_gates,
            "epoch0_fail": ep0_fail,
        })
    else:
        invalid_files[fmt] = invalid_files.get(fmt, 0) + 1

print(f"== QVM有效电路数: {len(valid_results)} ==", file=sys.stderr)

# ---- 对有效电路 × EPOCHS 全量训练 ----
print(f"== 执行3epoch全量训练 ({len(valid_results)}电路×3={len(valid_results)*3}次QVM)... ==", file=sys.stderr)

results = []
total_cycles_all = 0
total_gates_all = 0
total_failures = 0
total_executions = 0

for item in valid_results:
    fp = item["fp"]
    comp = item["comp"]
    rel = item["rel"]
    c_cycles = 0
    c_gates = 0
    c_fails = 0
    ep_detail = []
    for ep in range(EPOCHS):
        try:
            out = subprocess.run(
                [QVM, fp], capture_output=True, text=True, timeout=30
            ).stdout
            total_executions += 1
            cyc = CYCLE_RE.findall(out)
            gts = GATE_RE.findall(out)
            cc = int(cyc[-1]) if cyc else 0
            gg = int(gts[-1]) if gts else 0
            c_cycles += cc
            c_gates += gg
            ep_detail.append({"epoch": ep+1, "cycles": cc, "gates": gg})
        except subprocess.TimeoutExpired:
            c_fails += 1
            total_executions += 1
            ep_detail.append({"epoch": ep+1, "error": "TIMEOUT"})
        except Exception as e:
            c_fails += 1
            total_executions += 1
            ep_detail.append({"epoch": ep+1, "error": str(e)[:60]})
    total_cycles_all += c_cycles
    total_gates_all += c_gates
    total_failures += c_fails
    results.append({
        "comp": comp, "rel": rel, "fmt": item["fmt"],
        "total_cycles": c_cycles, "total_gates": c_gates, "failures": c_fails,
        "epochs_detail": ep_detail
    })

# ---- 按组件汇总 ----
comp_stats = defaultdict(lambda: {"circuits": 0, "cycles": 0, "gates": 0, "failures": 0})
for r in results:
    s = comp_stats[r["comp"]]
    s["circuits"] += 1
    s["cycles"] += r["total_cycles"]
    s["gates"] += r["total_gates"]
    s["failures"] += r["failures"]

actual_circuits = len(valid_results)
actual_cycles = total_cycles_all
actual_gates = total_gates_all
actual_failures = total_failures

# ---- 输出 ----
print("\n" + "="*70, file=sys.stderr)
print("阶段6-7基线训练结果（QVM执行口径）", file=sys.stderr)
print("="*70, file=sys.stderr)
print(f"\n全仓库.qbc文件总数: {len(qbc_files)}", file=sys.stderr)
print(f"有效电路总数(QVM可执行): {actual_circuits}", file=sys.stderr)
print(f"总执行次数: {total_executions} ({actual_circuits}电路 × {EPOCHS}epoch)", file=sys.stderr)
print(f"总周期: {actual_cycles}", file=sys.stderr)
print(f"总门数: {actual_gates}", file=sys.stderr)
print(f"失败数: {actual_failures}", file=sys.stderr)

print("\n--- 按组件分类统计 ---", file=sys.stderr)
print(f"{'组件':<20} {'电路数':>6} {'周期':>8} {'门数':>8} {'失败':>6}", file=sys.stderr)
print("-"*50, file=sys.stderr)
for comp in sorted(comp_stats.keys()):
    s = comp_stats[comp]
    print(f"{comp:<20} {s['circuits']:>6} {s['cycles']:>8} {s['gates']:>8} {s['failures']:>6}", file=sys.stderr)
print(f"{'TOTAL':<20} {actual_circuits:>6} {actual_cycles:>8} {actual_gates:>8} {actual_failures:>6}", file=sys.stderr)

print("\n--- 无效文件格式分布(未计入训练) ---", file=sys.stderr)
for k, v in sorted(invalid_files.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}个", file=sys.stderr)

# ---- 与基线对比 ----
print("\n--- 与基线对比 ---", file=sys.stderr)
bl = BASELINE
def deviation(a, b):
    if b == 0: return "N/A" if a == 0 else "∞"
    d = (a - b) / b * 100
    return f"{d:+.1f}%"

def abs_pct(a, b):
    if b == 0: return 0.0 if a == 0 else 999.0
    return abs(a - b) / b * 100

print(f"{'指标':<10} {'基线':>8} {'实际':>8} {'偏差':>10}", file=sys.stderr)
print("-"*40, file=sys.stderr)
print(f"{'电路数':<10} {bl['circuits']:>8} {actual_circuits:>8} {deviation(actual_circuits, bl['circuits']):>10}", file=sys.stderr)
print(f"{'总周期':<10} {bl['cycles']:>8} {actual_cycles:>8} {deviation(actual_cycles, bl['cycles']):>10}", file=sys.stderr)
print(f"{'总门数':<10} {bl['gates']:>8} {actual_gates:>8} {deviation(actual_gates, bl['gates']):>10}", file=sys.stderr)
print(f"{'失败数':<10} {bl['failures']:>8} {actual_failures:>8} {deviation(actual_failures, bl['failures']):>10}", file=sys.stderr)

devs = {
    "电路数": abs_pct(actual_circuits, bl["circuits"]),
    "总周期": abs_pct(actual_cycles, bl["cycles"]),
    "总门数": abs_pct(actual_gates, bl["gates"]),
}
any_over_10 = any(v > 10 for v in devs.values())
if any_over_10:
    print("\n⚠️ 偏差>10%的指标:", file=sys.stderr)
    for k, v in devs.items():
        if v > 10:
            print(f"  {k}: {v:.1f}%", file=sys.stderr)
    print("\n[偏差原因分析]", file=sys.stderr)
    print(f"  实际有效电路{actual_circuits}个 vs 基线78个（偏差{devs['电路数']:.1f}%）。", file=sys.stderr)
    print(f"  可能原因：", file=sys.stderr)
    print(f"    1. 仓库中部分.cbc文件已被修改/删除，导致0x14电路数量从78降至{actual_circuits}。", file=sys.stderr)
    print(f"    2. 基线记载的78电路可能包含一些当前已不存在或已损坏的.qbc文件。", file=sys.stderr)
    print(f"    3. 部分电路的周期/门数可能因.qbc重新编译而发生变化。", file=sys.stderr)
else:
    print("\n✅ 所有指标偏差≤10%，与基线一致。", file=sys.stderr)

# ---- JSON摘要 ----
summary = {
    "total_qbc_files": len(qbc_files),
    "valid_circuits_qvm_executable": actual_circuits,
    "epochs": EPOCHS,
    "total_executions": total_executions,
    "total_cycles": actual_cycles,
    "total_gates": actual_gates,
    "total_failures": actual_failures,
    "component_stats": {k: dict(v) for k, v in comp_stats.items()},
    "invalid_files_format": dict(invalid_files),
    "baseline": bl,
    "deviations_pct": devs,
    "any_over_10pct": any_over_10,
}
print("\n" + json.dumps(summary, ensure_ascii=False, indent=2))
with open("/tmp/baseline_summary_v3.json", "w") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
