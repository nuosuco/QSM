#!/usr/bin/env python3
"""QSM QBC Audit: run bin/qvm_bootstrap on every 0x14 .qbc, report per-component stats."""
import os, subprocess

ROOT = "/root/QSM"
QVM = f"{ROOT}/bin/qvm_bootstrap"
TIMEOUT = 15

COMPONENTS = [
    ("QNS (neural)",       ["QEntL/System/Kernel/neural"]),
    ("QDFS (filesystem)",  ["QEntL/System/Kernel/filesystem"]),
    ("Models (四大模型)",   ["QEntL/Models"]),
    ("QCL Compiler",       ["QEntL/System/Compiler"]),
    ("VM",                 ["QEntL/System/VM"]),
    ("Platform",           ["QEntL/System/Platform"]),
    ("QPU 部署",           ["QEntL/System/VM/src/deployment"]),
    ("QCL 模块",           ["QCL模块"]),
    ("docs examples",      ["docs"]),
]

def find_0x14(roots):
    seen = set()
    for base in roots:
        for dp, _, fns in os.walk(os.path.join(ROOT, base)):
            for f in fns:
                if not f.endswith(".qbc"):
                    continue
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, ROOT)
                if rel in seen:
                    continue
                seen.add(rel)
                try:
                    if open(p, "rb").read(1) == b"\x14":
                        yield rel
                except Exception:
                    pass

def run(rel):
    try:
        r = subprocess.run([QVM, os.path.join(ROOT, rel)], capture_output=True, text=True, timeout=TIMEOUT)
        out = (r.stderr or r.stdout).lower()
        sf = any(s in out for s in ("segmentation fault", "segfault", "core dumped"))
        return r.returncode == 0 and not sf, sf
    except subprocess.TimeoutExpired:
        return False, False
    except Exception:
        return False, False

def main():
    print(f"{'='*72}\nQSM QBC Audit — bin/qvm_bootstrap\n{'='*72}")
    grand = {"pass": 0, "fail": 0, "sf": 0}
    for label, roots in COMPONENTS:
        circuits = list(find_0x14(roots))
        n = len(circuits)
        if n == 0:
            print(f"\n[{label}]  — no valid 0x14 .qbc")
            continue
        print(f"\n[{label}]  — {n} circuits")
        p = s = f = 0
        for rel in circuits:
            ok, sf = run(rel)
            if sf:
                s += 1; f += 1
            elif ok:
                p += 1
            else:
                f += 1
        print(f"  PASS={p}  FAIL={f}  SEGFaults={s}")
        grand["pass"] += p; grand["fail"] += f; grand["sf"] += s
    print(f"\n{'='*72}\nTOTAL: PASS={grand['pass']}  FAIL={grand['fail']}  SEGFaults={grand['sf']}")

if __name__ == "__main__":
    main()
