#!/usr/bin/env python3
"""QEntL full-stack training: multi-epoch QNS training loop simulation."""
import subprocess, os, sys, json, re
from collections import defaultdict

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
EPOCHS = 3
TIMEOUT = 30

# ── 1. Scan all .qbc, keep only valid 0x14 circuits ──────────────────────────
def find_qbc():
    out = subprocess.run(
        ["find", ROOT, "-name", "*.qbc", "-not", "-path", "*/.git/*"],
        capture_output=True, text=True, timeout=30
    ).stdout
    return sorted(p.strip() for p in out.splitlines() if p.strip())

def first_byte(path):
    """Return hex of first byte via xxd -l1 -p."""
    try:
        out = subprocess.run(
            ["xxd", "-l1", "-p", path],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        return out
    except Exception:
        return None

valid = []
invalid = []
for p in find_qbc():
    fb = first_byte(p)
    if fb == "14":
        valid.append(p)
    else:
        invalid.append((p, fb))

print(f"[SCAN] Total .qbc files: {len(valid)+len(invalid)}")
print(f"[SCAN] Valid 0x14 circuits: {len(valid)}")
print(f"[SCAN] Invalid/other: {len(invalid)}")
for p, fb in invalid:
    print(f"       SKIP {os.path.relpath(p, ROOT)} (first_byte={fb})")

# ── 2. Classify by model ────────────────────────────────────────────────────
def classify(path):
    rel = os.path.relpath(path, ROOT)
    if rel.startswith("QEntL/System/Kernel/neural/") or "qns_" in rel.lower() or rel.startswith("QEntL/Models/Models_QNS"):
        return "QNS"
    if "qdfs" in rel.lower() or "filesystem" in rel.lower():
        return "QDFS"
    if rel.startswith("QEntL/Models/QSM/"):
        return "QSM"
    if rel.startswith("QEntL/Models/Ref/"):
        return "Ref"
    if rel.startswith("QEntL/Models/WeQ/"):
        return "WeQ"
    if rel.startswith("QEntL/Models/SOM/"):
        return "SOM"
    if "Compiler" in rel or "compiler" in rel or "qentl" in rel.lower():
        return "Compiler"
    return "Other"

# ── 3. Run qvm_bootstrap ×3 epochs per circuit ──────────────────────────────
def run_qvm(path, epoch):
    try:
        r = subprocess.run(
            [QVM, path],
            capture_output=True, text=True, timeout=TIMEOUT
        )
        out = r.stdout + r.stderr
        # Extract cycles and gates from Chinese output: "执行完成: N 周期, M 门操作"
        cycles = gates = None
        m = re.search(r'(\d+)\s*周期', out)
        if m: cycles = int(m.group(1))
        m = re.search(r'(\d+)\s*门操作', out)
        if m: gates = int(m.group(1))
        return {"cycles": cycles, "gates": gates, "rc": r.returncode, "err": r.stderr.strip()[:200] if r.returncode != 0 else ""}
    except subprocess.TimeoutExpired:
        return {"cycles": None, "gates": None, "rc": -1, "err": "TIMEOUT"}
    except Exception as e:
        return {"cycles": None, "gates": None, "rc": -2, "err": str(e)[:200]}

results = {}  # path -> list of epoch results
failures = 0
total_exec = 0

for path in valid:
    rel = os.path.relpath(path, ROOT)
    res = []
    for ep in range(EPOCHS):
        r = run_qvm(path, ep)
        res.append(r)
        total_exec += 1
        if r["cycles"] is None or r["rc"] != 0:
            failures += 1
    results[path] = res

# ── 4. Aggregate ────────────────────────────────────────────────────────────
total_cycles = 0
total_gates = 0
cat_stats = defaultdict(lambda: {"circuits": 0, "cycles": 0, "gates": 0, "execs": 0, "fails": 0})

print("\n" + "="*90)
print("PER-CIRCUIT DETAILS")
print("="*90)
for path in valid:
    rel = os.path.relpath(path, ROOT)
    cat = classify(path)
    runs = results[path]
    # use first successful epoch for stats
    cycles = gates = None
    for r in runs:
        if r["cycles"] is not None:
            cycles = r["cycles"]
            gates = r["gates"]
            break
    if cycles is None:
        cycles = gates = 0
    total_cycles += cycles * EPOCHS  # sum across epochs (use per-epoch if available)
    total_gates += gates * EPOCHS
    # Actually sum actual epoch values
    ec = sum(r["cycles"] or 0 for r in runs)
    eg = sum(r["gates"] or 0 for r in runs)
    ef = sum(1 for r in runs if r["cycles"] is None or r["rc"] != 0)
    total_cycles_adj = ec
    total_gates_adj = eg
    cat_stats[cat]["circuits"] += 1
    cat_stats[cat]["cycles"] += ec
    cat_stats[cat]["gates"] += eg
    cat_stats[cat]["execs"] += EPOCHS
    cat_stats[cat]["fails"] += ef

    status = "OK" if ef == 0 else f"FAIL×{ef}"
    print(f"[{cat:8s}] {rel:65s} cycles={ec:5d} gates={eg:5d} [{status}]")

# Recompute totals from cat_stats
total_cycles = sum(v["cycles"] for v in cat_stats.values())
total_gates = sum(v["gates"] for v in cat_stats.values())
total_fails = sum(v["fails"] for v in cat_stats.values())

print("\n" + "="*90)
print("CLASSIFICATION STATISTICS")
print("="*90)
print(f"{'Category':10s} {'Circuits':>9s} {'Execs':>7s} {'Cycles':>9s} {'Gates':>7s} {'Fails':>6s}")
print("-"*50)
for cat in ["QNS","QDFS","QSM","Ref","WeQ","SOM","Compiler","Other"]:
    if cat in cat_stats:
        v = cat_stats[cat]
        print(f"{cat:10s} {v['circuits']:>9d} {v['execs']:>7d} {v['cycles']:>9d} {v['gates']:>7d} {v['fails']:>6d}")

print("\n" + "="*90)
print("SUMMARY")
print("="*90)
print(f"Valid 0x14 circuits : {len(valid)}")
print(f"Total executions    : {total_exec} (expected {len(valid)*EPOCHS})")
print(f"Total cycles        : {total_cycles} (baseline 4494)")
print(f"Total gates         : {total_gates} (baseline 4494)")
print(f"Total failures      : {total_fails} (expected 0)")
print(f"Invalid files skipped: {len(invalid)}")
print("="*90)
