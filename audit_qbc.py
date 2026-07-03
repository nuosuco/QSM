#!/usr/bin/env python3
"""QVM Audit: classify all .qbc files, execute valid (0x14) circuits through qvm_bootstrap, count PASS/FAIL."""
import os
import subprocess
from collections import defaultdict

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")

def classify(rel):
    """Return model category from relative path (no leading slash)."""
    if rel.startswith("QEntL/System/Kernel/neural/") or rel.startswith("QEntL/System/Kernel/qns_qdfs"):
        return "QNS"
    if rel.startswith("QEntL/System/Kernel/filesystem/"):
        return "QDFS"
    if rel.startswith("QEntL/Models/QSM/"):
        return "QSM"
    if rel.startswith("QEntL/Models/Ref/"):
        return "Ref"
    if rel.startswith("QEntL/Models/SOM/"):
        return "SOM"
    if rel.startswith("QEntL/Models/WeQ/"):
        return "WeQ"
    if rel.startswith("QEntL/System/Compiler/"):
        return "Compiler"
    return "Other"

# Walk repo
qbc_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # exclude .git
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for fn in filenames:
        if fn.endswith(".qbc"):
            full = os.path.join(dirpath, fn)
            qbc_files.append(full)

total = len(qbc_files)
first_byte_counts = defaultdict(int)   # hex -> count
valid_0x14 = 0
invalid_0x72 = 0
other_first = 0

files_to_run = []  # list of (abs_path, rel_path, category)

for fp in qbc_files:
    rel = os.path.relpath(fp, ROOT)
    try:
        with open(fp, "rb") as fh:
            b0 = fh.read(1)
            if len(b0) == 0:
                first_byte_counts["0x00(empty)"] += 1
                other_first += 1
                continue
            hb = f"0x{b0[0]:02x}"
            first_byte_counts[hb] += 1
            if b0[0] == 0x14:
                valid_0x14 += 1
                cat = classify(rel)
                files_to_run.append((fp, rel, cat))
            elif b0[0] == 0x72:
                invalid_0x72 += 1
            else:
                other_first += 1
    except Exception as e:
        first_byte_counts["ERROR"] += 1
        other_first += 1

print(f"=== QBC WALK ===")
print(f"Total .qbc files : {total}")
print(f"Valid  0x14      : {valid_0x14}")
print(f"Invalid 0x72     : {invalid_0x72}")
print(f"Other first byte : {other_first}")
print(f"First-byte distribution: {dict(first_byte_counts)}")
print()

# QVM execution
passes = defaultdict(int)
fails  = defaultdict(int)
fail_files = []

for fp, rel, cat in files_to_run:
    try:
        r = subprocess.run([QVM, fp], capture_output=True, timeout=30)
        if r.returncode == 0:
            passes[cat] += 1
        else:
            fails[cat] += 1
            fail_files.append(rel)
    except subprocess.TimeoutExpired:
        fails[cat] += 1
        fail_files.append(rel)
    except Exception as e:
        fails[cat] += 1
        fail_files.append(rel)

total_pass = sum(passes.values())
total_fail = sum(fails.values())

print(f"=== QVM AUDIT (0x14 files) ===")
print(f"PASS : {total_pass}")
print(f"FAIL : {total_fail}")
print(f"EXECUTED : {total_pass + total_fail}")
print()
print("=== By model category ===")
print(f"{'Category':<12}{'PASS':>8}{'FAIL':>8}{'TOTAL':>8}")
print("-"*36)
categories = ["QNS", "QDFS", "QSM", "Ref", "SOM", "WeQ", "Compiler", "Other"]
for cat in categories:
    p = passes[cat]
    f = fails[cat]
    t = p + f
    if t > 0:
        print(f"{cat:<12}{p:>8}{f:>8}{t:>8}")
print("-"*36)
print(f"{'TOTAL':<12}{total_pass:>8}{total_fail:>8}{total_pass+total_fail:>8}")

if fail_files:
    print(f"\n=== FAIL FILES ({len(fail_files)}) ===")
    for f in fail_files:
        print(f"  - {f}")
