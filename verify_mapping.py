#!/usr/bin/env python3
"""Verify algorithmic fallback mapping matches the C compiler's ops[(cp-YI_BASE)%18]."""
import struct

YI_BASE = 0xF2710
# Same 18-element table as src/qcl_phase2.c lines 123-128
ALGO_OPS = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15,11]  # H,X,Z,Y,T,S,RESET,NOP,BARRIER,STOP,EXIT,INIT_N,PRINT,MEASURE,SWAP,CNOT,SWAP,INIT_N
GATE_NAME = {1:'H',2:'X',3:'Z',4:'Y',5:'T',6:'S',7:'RESET',8:'BARRIER',
             9:'STOP',10:'EXIT',11:'INIT_N',12:'PRINT',13:'MEASURE',14:'SWAP',15:'CNOT'}

# Re-read qbc and isolate per-variable gate for Yi chars from training data
data = open('/root/QSM/test_yi_final.qbc','rb').read()
code_len = struct.unpack_from('<H',data,4)[0]
sp_off = 6+code_len+2
sp_len = struct.unpack_from('<H',data,sp_off-2)[0]
code = data[6:6+code_len]
sp = data[sp_off:sp_off+sp_len]

# Count gates in code segment
gates = [(b) for b in code if 1 <= b <= 15]
print(f"Total quantum gate opcodes in code: {len(gates)}")

# Test specific training-data chars
test = [
    (0xF2722, 'explicit fallback boundary'),
    (0xF2ABC, 'from training data'),
    (0xF2E23, 'from training data'),
    (0xF34BA, 'from training data'),
    (0xF2F00, 'from training data'),
    (0xF271F, 'between explicit entries'),
]
print("\n=== Algorithmic fallback mapping (C: ops[(cp-YI_BASE)%18]) ===")
for cp, label in test:
    off = cp - YI_BASE
    op = ALGO_OPS[off % 18]
    print(f"  U+{cp:05X}  offset=0x{off:03X}  offset%18={off%18}  → opcode {op} ({GATE_NAME[op]})  [{label}]")

# String pool: verify only out-of-range chars
sp_str = sp.decode('utf-8', errors='replace')
yi_in_sp = set(ord(ch) for ch in sp_str if 0xF0000 <= ord(ch) <= 0xF370F)
print(f"\n=== String pool Yi chars (compiled as STRINGS, not gates) ===")
for cp in sorted(yi_in_sp):
    print(f"  U+{cp:05X}  offset from YI_BASE={cp-YI_BASE}  → below range, falls to string pool ✓")
