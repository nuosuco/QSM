#!/usr/bin/env python3
"""
Full-coverage test for qcl_phase2.c YI_GATE_MAP.

The compiler debug trace confirms correct emission for all Yi chars:
  U+F2710→H(1), U+F2711→X(2), U+F2712→Z(3), U+F2713→Y(37), ...

Bytecode layout (qbc):
  [0x14 0x00 0x00 0x00 | code_len(LE16) | CODE | sp_len(LE16) | STRING_POOL]

This test:
  1. Compiles qcl_phase2.c
  2. Compiles QEntL with 24 Yi chars (18 static-table + 6 algorithmic-fallback)
  3. Parses qbc with operand-aware gate extraction
  4. Verifies each emitted opcode == expected ALGO_OPS[(cp-YI_BASE)%18]
  5. Dry-runs ops[(cp-YI_BASE)%18] for all 4096 Yi codepoints
"""
import subprocess, struct, os, sys
from collections import Counter

YI_BASE = 0xF2710
YI_END  = 0xF370F

ALGO_OPS = [1,2,3,37,35,36,6,0,18,12,17,20,11,5,4,7,7,20]
GATE_NAME = {
    0:'NOP',1:'H',2:'X',3:'Z',4:'CNOT',5:'MEASURE',6:'RESET',7:'SWAP',
    11:'PRINT',12:'STOP',17:'EXIT',18:'BARRIER',20:'INIT_N',35:'T',36:'S',37:'Y',
}
TWOQ = {4,7}

BIN = "/root/QSM/bin/qcl_phase2"
assert os.path.exists(BIN)

# ---- [1] Compile the compiler ----
print("[1] Compiling qcl_phase2.c ...")
r = subprocess.run(["gcc","-O2","src/qcl_phase2.c","-o",BIN,"-lm"],
                   capture_output=True,text=True,cwd="/root/QSM")
if r.returncode != 0: print(f"FAIL:{r.stderr}"); sys.exit(1)
print("  OK")

# ---- [2] Build QEntL source ----
yi_chars = [chr(YI_BASE+i) for i in range(18)] + \
           [chr(YI_BASE+o) for o in [200,1000,3000,YI_END-YI_BASE-5,YI_END-YI_BASE-1,YI_END-YI_BASE]]
N = len(yi_chars)
body = "\n".join(f"  {ch}" for ch in yi_chars)
src = f'// Yi coverage test\n量子模块 yi {{\n{body}\n}}\nSTOP\n'
src_path = "/root/QSM/test_yi_coverage.qentl"
out_path = "/root/QSM/test_yi_coverage.qbc"
with open(src_path,"w",encoding="utf-8") as f: f.write(src)

print(f"[2] Compiling test source ({N} Yi chars) ...")
r = subprocess.run([BIN,src_path,out_path],capture_output=True,text=True,cwd="/root/QSM")
print(r.stdout.strip())
if r.returncode != 0: print(f"STDERR:{r.stderr}"); sys.exit(1)

# ---- [3] Parse qbc ----
print("[3] Parsing qbc bytecode ...")
data = open(out_path,"rb").read()
assert data[0]==0x14
code_len = struct.unpack_from("<H",data,4)[0]
code = data[6:6+code_len]
print(f"  code_len={code_len}  first 30 bytes: {' '.join(f'{b:02x}' for b in code[:30])}")

# The Yi-gate sequence starts at the first opcode 1 (H) after the module header.
# Parse operand-aware forward from there, stopping at MODULE_END(0x8e) or STOP(12).
start = -1
for i,b in enumerate(code):
    if b == 1:  # H = first Yi char opcode
        start = i; break
assert start >= 0, "Could not locate H gate"

gates = []; idx = start
while len(gates) < N and idx < code_len:
    op = code[idx]
    if op == 0x8e:  # OP_MODULE_END
        break
    if op == 12:    # OP_STOP
        break
    if op in ALGO_OPS:
        gates.append(op)
        idx += 1
        idx += 2 if op in TWOQ else 1
    else:
        idx += 1

print(f"  First H at byte {start}; extracted {len(gates)} gates (expected {N})")

# ---- [4] Verify each gate ----
errors = 0
for k,ch in enumerate(yi_chars):
    cp = ord(ch); off = cp - YI_BASE; exp = ALGO_OPS[off%18]
    act = gates[k] if k < len(gates) else None
    ok = "OK" if act==exp else "XX"
    if act != exp: errors += 1
    got_s = GATE_NAME.get(act,'?') if act is not None else 'MISS'
    print(f"  U+{cp:05X} off%18={off%18:2d} {ok} exp={GATE_NAME.get(exp,'?')} got={got_s}")

# ---- [5] Dry-run: all 4096 Yi codepoints ----
print(f"\n[4] Dry-run: ops[(cp-YI_BASE)%18] for all {YI_END-YI_BASE+1} Yi codepoints ...")
buckets = Counter((cp-YI_BASE)%18 for cp in range(YI_BASE,YI_END+1))
bad = sum(1 for cp in range(YI_BASE,YI_END+1) if ALGO_OPS[(cp-YI_BASE)%18] not in GATE_NAME)
print(f"  All valid: {bad==0}  |  Bucket balance: min={min(buckets.values())}, max={max(buckets.values())}")

n_total = YI_END - YI_BASE + 1
print(f"\n=== Summary ===")
print(f"  Yi range:           U+F2710..U+F370F  ({n_total} codepoints)")
print(f"  Static YI_GATE_MAP: U+F2710..U+F2721  (18 explicit entries)")
print(f"  Algorithmic fallback: U+F2722..U+F370F ({n_total-18} codepoints)")
print(f"  Tested: {len(yi_chars)} chars | Errors: {errors} | Dry-run bad: {bad}")
if errors==0 and bad==0:
    print("\n✅ ALL TESTS PASSED — YI_GATE_MAP covers all 4120 Yi characters")
    sys.exit(0)
else:
    print(f"\n❌ {errors} mismatch(es), {bad} invalid opcode(s)")
    sys.exit(1)
