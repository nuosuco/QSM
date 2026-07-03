#!/usr/bin/env python3
"""QSM Full-stack verification — 6 tasks."""
import subprocess, os, re, time, json, glob
from collections import defaultdict

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
TIMEOUT = 30

RE_CYCLES = re.compile(r'(\d+)\s*周期')
RE_GATES  = re.compile(r'(\d+)\s*门操作')

def is_qvm_circuit(path):
    """Check first byte == 0x14."""
    try:
        with open(path, "rb") as f:
            b = f.read(1)
            return b == b'\x14'
    except Exception:
        return False

def run_qvm(path, timeout=TIMEOUT):
    """Run qvm_bootstrap, return (cycles, gates, failed, stdout)."""
    try:
        r = subprocess.run([QVM, path], capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        cycles = int(RE_CYCLES.search(r.stdout).group(1)) if RE_CYCLES.search(r.stdout) else None
        gates  = int(RE_GATES.search(r.stdout).group(1))   if RE_GATES.search(r.stdout)  else None
        failed = r.returncode != 0 or cycles is None
        return cycles or 0, gates or 0, failed, r.stdout[-200:] if r.stdout else ""
    except subprocess.TimeoutExpired:
        return 0, 0, True, "TIMEOUT"
    except Exception as e:
        return 0, 0, True, str(e)

def classify(path):
    """Return category key from relative path."""
    p = path.replace(ROOT, "").strip("/")
    if "/Models/QSM/" in p: return "QSM"
    if "/Models/SOM/" in p: return "SOM"
    if "/Models/WeQ/" in p: return "WeQ"
    if "/Models/Ref/" in p: return "Ref"
    if "/Kernel/neural/" in p: return "QNS"
    if "/Kernel/filesystem/" in p: return "QDFS"
    if "/System/Platform/" in p: return "Platform"
    if "/VM/src/deployment/" in p: return "Deploy"
    return "Other"

def find_qbc(base):
    """Recursively find *.qbc under base (abs path)."""
    out = []
    for root, _, files in os.walk(base):
        for f in files:
            if f.endswith(".qbc"):
                out.append(os.path.join(root, f))
    return out

def print_stats(label, runs, cycles, gates, fails):
    print(f"  [{label}] 执行={runs} 周期={cycles} 门={gates} 失败={fails}")

stats = defaultdict(lambda: {"runs":0,"cycles":0,"gates":0,"fails":0})

# ===================== TASK 1: Four Models =====================
print("=" * 60)
print("TASK 1 — 四大模型量子电路验证")
print("=" * 60)
model_dirs = {
    "QSM": os.path.join(ROOT, "QEntL/Models/QSM"),
    "SOM": os.path.join(ROOT, "QEntL/Models/SOM"),
    "WeQ": os.path.join(ROOT, "QEntL/Models/WeQ"),
    "Ref": os.path.join(ROOT, "QEntL/Models/Ref"),
}
for name, d in model_dirs.items():
    files = find_qbc(d)
    valid = [f for f in files if is_qvm_circuit(f)]
    for f in valid:
        c, g, fl, _ = run_qvm(f)
        stats[name]["runs"]   += 1
        stats[name]["cycles"] += c
        stats[name]["gates"]  += g
        stats[name]["fails"]  += (1 if fl else 0)
    print_stats(name, stats[name]["runs"], stats[name]["cycles"],
                stats[name]["gates"], stats[name]["fails"])

# ===================== TASK 2: QNS =====================
print("=" * 60)
print("TASK 2 — QNS量子神经叠加态验证")
print("=" * 60)
neural_dir = os.path.join(ROOT, "QEntL/System/Kernel/neural")
special = [
    os.path.join(ROOT, "QEntL/System/Kernel/qns_qdfs_dataflow.qbc"),
    os.path.join(ROOT, "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc"),
]
qns_files = find_qbc(neural_dir) + special
valid = [f for f in qns_files if is_qvm_circuit(f)]
for f in valid:
    c, g, fl, _ = run_qvm(f)
    stats["QNS"]["runs"]   += 1
    stats["QNS"]["cycles"] += c
    stats["QNS"]["gates"]  += g
    stats["QNS"]["fails"]  += (1 if fl else 0)
    tag = " <<< SPECIAL" if f in special else ""
    flag = " FAIL" if fl else ""
    print(f"    {os.path.relpath(f, ROOT)}  cyc={c} gate={g}{flag}{tag}")
print_stats("QNS", stats["QNS"]["runs"], stats["QNS"]["cycles"],
            stats["QNS"]["gates"], stats["QNS"]["fails"])

# ===================== TASK 3: QDFS =====================
print("=" * 60)
print("TASK 3 — QDFS量子文件系统验证")
print("=" * 60)
qdfs_dir = os.path.join(ROOT, "QEntL/System/Kernel/filesystem")
files = find_qbc(qdfs_dir)
valid = [f for f in files if is_qvm_circuit(f)]
for f in valid:
    c, g, fl, _ = run_qvm(f)
    stats["QDFS"]["runs"]   += 1
    stats["QDFS"]["cycles"] += c
    stats["QDFS"]["gates"]  += g
    stats["QDFS"]["fails"]  += (1 if fl else 0)
print_stats("QDFS", stats["QDFS"]["runs"], stats["QDFS"]["cycles"],
            stats["QDFS"]["gates"], stats["QDFS"]["fails"])

# ===================== TASK 4: Platform + Deploy =====================
print("=" * 60)
print("TASK 4 — 平台模块 + 部署模块验证")
print("=" * 60)
plat_dir = os.path.join(ROOT, "QEntL/System/Platform")
dep_dir  = os.path.join(ROOT, "QEntL/System/VM/src/deployment")
plat_files = find_qbc(plat_dir)
dep_files  = find_qbc(dep_dir)

# compile count = all .qbc; qvm runs = only 0x14
plat_qvm = [f for f in plat_files if is_qvm_circuit(f)]
dep_qvm  = [f for f in dep_files if is_qvm_circuit(f)]
for f in plat_qvm:
    c, g, fl, _ = run_qvm(f)
    stats["Platform"]["runs"]   += 1
    stats["Platform"]["cycles"] += c
    stats["Platform"]["gates"]  += g
    stats["Platform"]["fails"]  += (1 if fl else 0)
print(f"  [Platform] 编译通过={len(plat_files)} QVM执行={stats['Platform']['runs']} "
      f"周期={stats['Platform']['cycles']} 门={stats['Platform']['gates']} 失败={stats['Platform']['fails']}")

for f in dep_qvm:
    c, g, fl, _ = run_qvm(f)
    stats["Deploy"]["runs"]   += 1
    stats["Deploy"]["cycles"] += c
    stats["Deploy"]["gates"]  += g
    stats["Deploy"]["fails"]  += (1 if fl else 0)
print(f"  [Deploy  ] 编译通过={len(dep_files)} QVM执行={stats['Deploy']['runs']} "
      f"周期={stats['Deploy']['cycles']} 门={stats['Deploy']['gates']} 失败={stats['Deploy']['fails']}")

# ===================== TASK 5: Training data =====================
print("=" * 60)
print("TASK 5 — 训练数据验证")
print("=" * 60)
yi_file = os.path.join(ROOT, "data/yi_4120_merged_for_gemma.jsonl")
exists = os.path.exists(yi_file)
if exists:
    sz = os.path.getsize(yi_file)
    with open(yi_file) as fh:
        yi_lines = sum(1 for _ in fh)
    print(f"  yi_4120_merged_for_gemma.jsonl: 存在=True 大小={sz:,} bytes ({sz/1024/1024:.2f} MiB) 行数={yi_lines}")
else:
    print(f"  yi_4120_merged_for_gemma.jsonl: 存在=False")

jsonl_files = glob.glob(os.path.join(ROOT, "data", "*.jsonl"))
total_records = 0
for jf in jsonl_files:
    try:
        with open(jf) as fh:
            total_records += sum(1 for _ in fh)
    except Exception:
        pass
print(f"  data/*.jsonl: 文件数={len(jsonl_files)} 总条数={total_records:,}")

# ===================== TASK 6: Full-stack 3-epoch training =====================
print("=" * 60)
print("TASK 6 — 全栈训练循环 (3 epoch)")
print("=" * 60)
t0 = time.monotonic()
all_qbc = []
for r, _, fs in os.walk(ROOT):
    if ".git" in r:
        continue
    for f in fs:
        if f.endswith(".qbc"):
            all_qbc.append(os.path.join(r, f))
all_qbc = sorted(set(all_qbc))

valid_all = [f for f in all_qbc if is_qvm_circuit(f)]
print(f"  扫描 .qbc 总数={len(all_qbc)}  有效(0x14)={len(valid_all)}")

fs_stats = defaultdict(lambda: {"runs":0,"cycles":0,"gates":0,"fails":0})
total_runs=total_cyc=total_gates=total_fails=0
for epoch in range(3):
    for f in valid_all:
        c, g, fl, _ = run_qvm(f)
        total_runs   += 1
        total_cyc    += c
        total_gates  += g
        total_fails  += (1 if fl else 0)
        cat = classify(f)
        fs_stats[cat]["runs"]   += 1
        fs_stats[cat]["cycles"] += c
        fs_stats[cat]["gates"]  += g
        fs_stats[cat]["fails"]  += (1 if fl else 0)
    print(f"  epoch {epoch+1}/3 done (累计 runs={total_runs})")

elapsed = time.monotonic() - t0
print(f"  >>> 全栈训练完成: 总执行={total_runs} 周期={total_cyc} 门={total_gates} "
      f"失败={total_fails} 耗时={elapsed:.2f}s")
print("  按模型分类:")
for cat in sorted(fs_stats):
    s = fs_stats[cat]
    print(f"    {cat:10s} runs={s['runs']:4d} cyc={s['cycles']:6d} gates={s['gates']:6d} fails={s['fails']}")

# ===================== SUMMARY =====================
print("=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
summary = {
    "task1_models": dict(stats),
    "task2_qns": dict(stats["QNS"]),
    "task3_qdfs": dict(stats["QDFS"]),
    "task4_platform": {"compile": len(plat_files), **dict(stats["Platform"])},
    "task4_deploy":   {"compile": len(dep_files),  **dict(stats["Deploy"])},
    "task5_data": {
        "yi_4120_exists": exists,
        "yi_4120_size": sz if exists else None,
        "yi_4120_lines": yi_lines if exists else 0,
        "jsonl_count": len(jsonl_files),
        "jsonl_total_records": total_records,
    },
    "task6_fullstack": {
        "total_runs": total_runs,
        "total_cycles": total_cyc,
        "total_gates": total_gates,
        "total_fails": total_fails,
        "elapsed_s": round(elapsed, 2),
        "valid_circuits": len(valid_all),
        "all_qbc": len(all_qbc),
        "by_category": {k: dict(v) for k, v in sorted(fs_stats.items())},
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
