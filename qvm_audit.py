#!/usr/bin/env python3
"""Full QVM audit: 0x14-header .qbc scan + 21 core-circuit detail."""
import subprocess, os, re, sys, time

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")
QCL = os.path.join(ROOT, "bin", "qcl_bootstrap")

CORE_CIRCUITS = [
    "QEntL/Models/QSM/qsm_entry.qbc",
    "QEntL/Models/QSM/qsm_consciousness_circuit.qbc",
    "QEntL/Models/QSM/qsm_entanglement_circuit.qbc",
    "QEntL/Models/QSM/qsm_yi_training_circuit.qbc",
    "QEntL/Models/QSM/yi_training_pipeline_circuit.qbc",
    "QEntL/Models/Ref/ref_entry.qbc",
    "QEntL/Models/Ref/ref_monitoring_circuit.qbc",
    "QEntL/Models/Ref/ref_optimization_circuit.qbc",
    "QEntL/Models/Ref/ref_healing_circuit.qbc",
    "QEntL/Models/SOM/som_entry.qbc",
    "QEntL/Models/SOM/som_transaction_circuit.qbc",
    "QEntL/Models/WeQ/weq_entry.qbc",
    "QEntL/Models/WeQ/weq_learning_circuit.qbc",
    "QEntL/Models/WeQ/weq_social_interaction_circuit.qbc",
    "QEntL/System/Kernel/neural/qns_training_circuit.qbc",
    "QEntL/System/Kernel/neural/qns_backprop_circuit.qbc",
    "QEntL/System/Kernel/qns_qdfs_dataflow.qbc",
    "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc",
    "QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc",
    "QEntL/System/Kernel/filesystem/grover_search_circuit.qbc",
    "QEntL/Models/QNS_Integration_Test.qbc",
]

# ------------------------------------------------------------------
# Phase 0: compile missing core-circuit .qbc from .qentl if source exists
# ------------------------------------------------------------------
compiled_this_run = []
for qbc in CORE_CIRCUITS:
    full = os.path.join(ROOT, qbc)
    if not os.path.isfile(full):
        qentl = full[:-3] + ".qentl"
        if os.path.isfile(qentl):
            r = subprocess.run([QCL, qentl], capture_output=True, text=True, cwd=ROOT, timeout=60)
            if r.returncode == 0 and os.path.isfile(full):
                compiled_this_run.append((qentl, "OK"))
            else:
                compiled_this_run.append((qentl, f"FAIL rc={r.returncode}"))
        else:
            compiled_this_run.append((qentl, "NO_SOURCE"))

# ------------------------------------------------------------------
# Phase 1: find all .qbc (exclude .git)
# ------------------------------------------------------------------
out = subprocess.check_output(
    ["find", ROOT, "-name", "*.qbc", "-not", "-path", "*/.git/*"],
    text=True, stderr=subprocess.DEVNULL,
)
all_qbc = sorted([p.strip() for p in out.splitlines() if p.strip()])
print(f"[PHASE 1] Found {len(all_qbc)} .qbc files under {ROOT}")

# ------------------------------------------------------------------
# Phase 2: read first byte; 0x14 = valid QBC
# ------------------------------------------------------------------
valid_qbc = []
invalid_qbc = []
for p in all_qbc:
    try:
        with open(p, "rb") as f:
            b = f.read(1)
        if len(b) == 1 and b[0] == 0x14:
            valid_qbc.append(p)
        else:
            invalid_qbc.append((p, f"0x{b[0]:02x}" if len(b) else "EMPTY"))
    except Exception as e:
        invalid_qbc.append((p, f"ERR {e}"))
print(f"[PHASE 2] Valid (0x14) = {len(valid_qbc)}, invalid = {len(invalid_qbc)}")

# ------------------------------------------------------------------
# Phase 3: run qvm_bootstrap on every valid .qbc; tally PASS/FAIL
# ------------------------------------------------------------------
pass_set, fail_set = [], []
cycle_gate = {}   # full_path -> (cycles, gates)

for p in valid_qbc:
    r = subprocess.run([QVM, p], capture_output=True, text=True, cwd=ROOT, timeout=30)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip().splitlines() else ""
    m = re.search(r"(\d+)\s*周期.*?(\d+)\s*门", last)
    if m:
        cycles, gates = int(m.group(1)), int(m.group(2))
    else:
        cycles, gates = None, None
    cycle_gate[p] = (cycles, gates)
    if r.returncode == 0 and m:
        pass_set.append(p)
    else:
        err = last[:120] if last else (r.stderr.strip()[-120:] if r.stderr.strip() else f"rc={r.returncode}")
        fail_set.append((p, err))

print(f"\n[PHASE 3] Full scan PASS={len(pass_set)} FAIL={len(fail_set)}")

# ------------------------------------------------------------------
# Phase 4: 21 core circuits detail
# ------------------------------------------------------------------
print(f"\n{'='*10}")
print("PHASE 4: 21 CORE CIRCUITS")
print(f"{'='*10}")
print(f"{'Path':<70} {'Cycles':>8} {'Gates':>8} {'Status':>8}")
print("-"*100)
core_results = []
for rel in CORE_CIRCUITS:
    full = os.path.join(ROOT, rel)
    exists = os.path.isfile(full)
    valid_header = False
    if exists:
        with open(full, "rb") as f:
            valid_header = (f.read(1)[0] == 0x14)
    cycles, gates = (None, None)
    status = "MISSING"
    if exists and valid_header:
        cycles, gates = cycle_gate.get(full, (None, None))
        status = "PASS" if full in pass_set else "FAIL"
    elif exists and not valid_header:
        status = "BAD_HEADER"
    core_results.append((rel, status, cycles, gates))
    print(f"{rel:<70} {str(cycles):>8} {str(gates):>8} {status:>8}")

# ------------------------------------------------------------------
# Final report
# ------------------------------------------------------------------
print(f"\n{'#'*80}")
print("FINAL QVM AUDIT REPORT")
print(f"{'#'*80}")
print(f"Total .qbc found : {len(all_qbc)}")
print(f"Valid 0x14 header: {len(valid_qbc)}")
print(f"Invalid header    : {len(invalid_qbc)}")
print(f"QVM PASS          : {len(pass_set)}")
print(f"QVM FAIL          : {len(fail_set)}")
print(f"Compiled this run : {len(compiled_this_run)}")
if compiled_this_run:
    print("\n--- Compilation actions ---")
    for src, info in compiled_this_run:
        print(f"  {src}: {info}")
if fail_set:
    print("\n--- FAIL file paths ---")
    for p, err in fail_set[:80]:
        print(f"  FAIL: {os.path.relpath(p, ROOT)}  |  {err}")
if len(fail_set) > 80:
    print(f"  ... and {len(fail_set)-80} more failures")
if invalid_qbc:
    print("\n--- Non-0x14 files (first 40) ---")
    for p, b in invalid_qbc[:40]:
        print(f"  {os.path.relpath(p, ROOT)}  first_byte={b}")
