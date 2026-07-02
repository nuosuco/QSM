#!/usr/bin/env python3
"""QEntL full compilation sweep + QVM verification."""
import subprocess, os, glob, sys

REPO = "/root/QSM"
BIN = os.path.join(REPO, "bin")
QCL = os.path.join(BIN, "qcl_bootstrap")
QVM = os.path.join(BIN, "qvm_bootstrap")

# Step 1: Find all .qentl files (exclude node_modules, web playground if desired — include all)
qentl_files = []
for root, dirs, files in os.walk(REPO):
    # Skip web playground stdlib + node_modules
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
    for f in files:
        if f.endswith(".qentl"):
            qentl_files.append(os.path.join(root, f))

qentl_files.sort()
total = len(qentl_files)

# Step 1: Compile ALL .qentl files unconditionally, then classify outputs.
compiled = 0
fail_compile = 0
compiled_list = []
fail_list = []

print(f"Total .qentl files found: {total}")
print("=" * 60)
print("Compiling... (this may take a minute)")

for fpath in qentl_files:
    qbc = fpath + "c"  # .qentl -> .qbc
    r = subprocess.run([QCL, fpath, qbc], capture_output=True, text=True, timeout=15)
    if r.returncode == 0 and os.path.exists(qbc) and os.path.getsize(qbc) > 0:
        compiled += 1
        compiled_list.append(qbc)
    else:
        fail_compile += 1
        fail_list.append((fpath, r.returncode, (r.stderr[-200:] if r.stderr else r.stdout[-200:])))

print(f"Compiled (produced valid .qbc): {compiled}")
print(f"Compile failures: {fail_compile}")
if fail_list:
    print("\nCompile failures:")
    for fp, rc, err in fail_list[:30]:
        print(f"  FAIL [{rc}] {fp} -> {err.strip()[:120]}")

# Step 2: QVM verification on all .qbc files
print("\n" + "=" * 60)
qbc_files = []
for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
    for f in files:
        if f.endswith(".qbc"):
            qbc_files.append(os.path.join(root, f))
qbc_files.sort()

qvm_pass = 0
qvm_fail = 0
skip_ascii = 0
qvm_fail_list = []
skip_list = []

for qbc in qbc_files:
    try:
        with open(qbc, "rb") as fh:
            first_byte = fh.read(1)
        if not first_byte:
            continue
        b = first_byte[0]
        if b == 0x14:  # Valid quantum bytecode
            r = subprocess.run([QVM, qbc], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                qvm_pass += 1
            else:
                qvm_fail += 1
                qvm_fail_list.append((qbc, r.returncode, r.stderr[-150:] if r.stderr else r.stdout[-150:]))
        elif b == 0x72:  # ASCII text (def/import) — skip
            skip_ascii += 1
        else:
            # Unknown header — try run anyway
            r = subprocess.run([QVM, qbc], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                qvm_pass += 1
            else:
                qvm_fail += 1
                qvm_fail_list.append((qbc, r.returncode, f"header=0x{b:02x}"))
    except Exception as e:
        qvm_fail += 1
        qvm_fail_list.append((qbc, "ERR", str(e)[:150]))

print(f"\nQVM verification results:")
print(f"  QVM PASS:      {qvm_pass}")
print(f"  QVM FAIL:      {qvm_fail}")
print(f"  SKIP (ASCII):  {skip_ascii}")
print(f"  Total .qbc:    {len(qbc_files)}")

if qvm_fail_list:
    print("\nQVM FAIL details:")
    for fp, rc, err in qvm_fail_list[:40]:
        print(f"  FAIL [{rc}] {fp} -> {str(err).strip()[:120]}")

print("\n" + "=" * 60)
print("=== FINAL SUMMARY ===")
print(f"  Repo path:       {REPO}")
print(f"  Total .qentl:    {total}")
print(f"  Compiled (.qbc): {compiled}")
print(f"  Compile fail:    {fail_compile}")
print(f"  QVM PASS:        {qvm_pass}")
print(f"  QVM FAIL:        {qvm_fail}")
print(f"  QVM skip(ASCII): {skip_ascii}")
print(f"  Total .qbc files:{len(qbc_files)}")
