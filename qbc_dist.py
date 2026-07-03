#!/usr/bin/env python3
"""Show byte-bytecode distribution of all .qbc first bytes."""
import glob, os
from collections import Counter

ROOT = "/root/QSM"
QENTL_DIR = os.path.join(ROOT, "QEntL")
qcnt = Counter()

for src in sorted(glob.glob(os.path.join(QENTL_DIR, "**", "*.qbc"), recursive=True)):
    try:
        with open(src, "rb") as f:
            b = f.read(1)
        qcnt[b[0] if b else None] += 1
    except Exception:
        qcnt["ERR"] += 1

for b, n in sorted(qcnt.items(), key=lambda x: -x[1]):
    if b is None:
        print(f"  empty      : {n}")
    elif isinstance(b, bytes):
        print(f"  0x{b[0]:02x}       : {n}")
    elif isinstance(b, int):
        print(f"  0x{b:02x}       : {n}")
    else:
        print(f"  {b}        : {n}")
