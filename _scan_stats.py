#!/usr/bin/env python3
"""Scan QSM project for full statistics."""
import os, glob, re

ROOT = "/root/QSM"
qentl_files = sorted(glob.glob(f"{ROOT}/**/*.qentl", recursive=True))
qbc_files = sorted(glob.glob(f"{ROOT}/**/*.qbc", recursive=True))

# Skip truly empty files
qentl_files = [f for f in qentl_files if os.path.getsize(f) > 0]
qbc_files = [f for f in qbc_files if os.path.getsize(f) > 0]

print(f"=== FILE TOTALS ===")
print(f".qentl count: {len(qentl_files)}")
print(f".qbc count: {len(qbc_files)}")
print(f"Total files: {len(qentl_files)+len(qbc_files)}")

# --- .qentl stats ---
total_lines = 0
total_bytes = 0
total_defs = 0
quantum_kw = ["qubit","h","x","y","z","s","sdg","t","tdg","rx","ry","rz","cnot","cx","cy","cz","swap","ch","crx","cry","crz","ccx","toffoli","measure","qstate","entangle","superpose","gate","qgate","qfunc","qcircuit","quantum","qreg"]
qkw_pattern = re.compile(r'\b(' + '|'.join(quantum_kw) + r')\b', re.IGNORECASE)
total_q_kw = 0
for f in qentl_files:
    sz = os.path.getsize(f)
    total_bytes += sz
    try:
        with open(f, 'r', errors='replace') as fh:
            text = fh.read()
    except:
        continue
    lines = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
    total_lines += lines
    # def count: lines starting with "def " or "  def " (QEntL def keyword)
    defs = len(re.findall(r'(?:^|\s)def\s+', text, re.MULTILINE))
    total_defs += defs
    total_q_kw += len(qkw_pattern.findall(text))

print(f"\n=== .qentl SOURCE STATS ===")
print(f"Total lines: {total_lines}")
print(f"Total bytes: {total_bytes}")
print(f"Functions (def): {total_defs}")
print(f"Quantum keywords: {total_q_kw}")

# --- .qbc stats ---
def parse_qbc(filepath):
    """Parse QBC format: code_bytes + sp_len(2B LE) + string_pool.
    Return code_bytes and string_pool.
    """
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
    except:
        return None, None
    if len(data) < 2:
        return None, None
    # Heuristic: find sp_len marker. The code section is everything
    # before the last 2-byte LE integer that makes sense as string pool length.
    # QBC format: code + sp_len(2B LE) + string_pool
    # Try: scan for the sp_len position. The spec says the last 2 bytes before
    # string pool are the pool length. We try finding the right boundary.
    # Approach: for each possible boundary, check if sp_len matches remaining bytes.
    code = None
    for boundary in range(len(data) - 2, 1, -1):
        sp_len = int.from_bytes(data[boundary:boundary+2], 'little')
        if boundary + 2 + sp_len == len(data):
            code = data[:boundary]
            break
    if code is None:
        # fallback: whole file as code
        code = data
    return code, data

valid_0x14 = 0
qinst_files = 0
total_def = 0
total_end = 0
total_qinst = 0
total_code_bytes = 0
total_qbc_bytes = 0
for f in qbc_files:
    code, raw = parse_qbc(f)
    if code is None:
        continue
    total_qbc_bytes += os.path.getsize(f)
    total_code_bytes += len(code)
    if len(code) > 0 and code[0] == 0x14:
        valid_0x14 += 1
    # DEF=0x66, END=0x67 in code bytes only
    cdef = code.count(0x66)
    cend = code.count(0x67)
    total_def += cdef
    total_end += cend
    # quantum instructions 0x01-0x08
    qinst = sum(1 for b in code if 0x01 <= b <= 0x08)
    total_qinst += qinst
    if qinst > 0:
        qinst_files += 1

print(f"\n=== .qbc BYTECODE STATS ===")
print(f"Valid 0x14 first-byte files: {valid_0x14}")
print(f"Files with quantum instructions (0x01-0x08): {qinst_files}")
print(f"Code DEF (0x66): {total_def}")
print(f"Code END (0x67): {total_end}")
print(f"DEF+END total: {total_def + total_end}")
print(f"Quantum instructions (0x01-0x08): {total_qinst}")
print(f"Code bytes: {total_code_bytes}")
print(f"Total file bytes: {total_qbc_bytes}")
if total_def:
    print(f"DEF/END pair rate: {total_end/total_def*100:.1f}%")

print(f"\n=== SUMMARY ===")
print(f"Total functions: {total_defs + total_def} (.qentl def {total_defs} + .qbc DEF {total_def})")
print(f"Total quantum instructions: {total_q_kw + total_qinst} (.qentl keywords {total_q_kw} + .qbc {total_qinst})")
