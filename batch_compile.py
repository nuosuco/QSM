#!/usr/bin/env python3
"""Batch compile all .qentl files in QEntL/ and classify results."""
import subprocess, glob, os, sys

ROOT = "/root/QSM"
QCL = os.path.join(ROOT, "bin", "qcl_bootstrap")
QENTL_DIR = os.path.join(ROOT, "QEntL")
QBC_OUT = os.path.join(ROOT, "QEntL")  # write .qbc next to source

files = sorted(glob.glob(os.path.join(QENTL_DIR, "**", "*.qentl"), recursive=True))
total = len(files)

success = 0
fail = 0
fail_list = []

# First pass: compile
for src in files:
    bcf = src.rsplit(".", 1)[0] + ".qbc"
    # Run with stdout/stderr capture, no interactive
    try:
        r = subprocess.run(
            [QCL, src, bcf],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode == 0:
            success += 1
        else:
            fail += 1
            if len(fail_list) < 20:
                fail_list.append((os.path.relpath(src, QENTL_DIR), r.returncode, (r.stderr or "")[:120]))
    except subprocess.TimeoutExpired:
        fail += 1
        if len(fail_list) < 20:
            fail_list.append((os.path.relpath(src, QENTL_DIR), "TIMEOUT", ""))
    except Exception as e:
        fail += 1
        if len(fail_list) < 20:
            fail_list.append((os.path.relpath(src, QENTL_DIR), "ERR", str(e)[:120]))

# Second pass: classify .qbc first byte
hex14 = 0
hex72 = 0
other = 0
other_list = []
no_qbc = 0

for src in files:
    bcf = src.rsplit(".", 1)[0] + ".qbc"
    if not os.path.exists(bcf):
        no_qbc += 1
        continue
    try:
        with open(bcf, "rb") as f:
            first = f.read(1)
        if len(first) == 0:
            other += 1
            other_list.append((os.path.relpath(bcf, QENTL_DIR), "empty"))
            continue
        b = first[0]
        if b == 0x14:
            hex14 += 1
        elif b == 0x72:
            hex72 += 1
        else:
            other += 1
            if len(other_list) < 30:
                other_list.append((os.path.relpath(bcf, QENTL_DIR), f"0x{b:02x}"))
    except Exception as e:
        other += 1
        other_list.append((os.path.relpath(bcf, QENTL_DIR), f"ERR:{e}"))

print("=" * 60)
print("QEntL Batch Compilation Report")
print("=" * 60)
print(f"  .qentl total files : {total}")
print(f"  Compile SUCCESS    : {success}")
print(f"  Compile FAILED     : {fail}")
print()
print("  Classification (by .qbc first byte):")
print(f"    0x14 valid QC    : {hex14}")
print(f"    0x72 invalid txt : {hex72}")
print(f"    other            : {other}")
print(f"    (no .qbc file    : {no_qbc})")
print("=" * 60)

if fail_list:
    print(f"\nFirst {len(fail_list)} failures:")
    for rel, rc, msg in fail_list:
        print(f"  [{rc}] {rel}  :: {msg}")

if other_list:
    print(f"\nFirst {len(other_list)} other-class .qbc files:")
    for rel, why in other_list:
        print(f"  {rel} :: {why}")
