#!/usr/bin/env python3
import subprocess, os, glob

WORKDIR = '/root/QSM'
os.chdir(WORKDIR)

COMPONENTS = {'neural', 'filesystem', 'models', 'compiler', 'kernel', 'services', 'gui', 'vm', 'scripts'}

def get_component(relpath):
    """Map QEntL file path to the MOST SPECIFIC (deepest) recognized component.
    E.g. 'QEntL/System/Kernel/neural/xxx.qbc' -> 'neural' not 'kernel'."""
    parts = relpath.split(os.sep)
    if 'QEntL' not in parts:
        return 'other'
    idx = parts.index('QEntL')
    tail = parts[idx+1:]
    # scan right-to-left so deepest recognized name wins
    for p in reversed(tail):
        if p.lower() in COMPONENTS:
            return p.lower()
    return 'other'

qbc_files = sorted(glob.glob('QEntL/**/*.qbc', recursive=True))

comp_stats = {}
total_pass = total_fail = total_skip = 0

for f in qbc_files:
    comp = get_component(f)
    if comp not in comp_stats:
        comp_stats[comp] = {'pass': 0, 'fail': 0, 'skip': 0}

    try:
        with open(f, 'rb') as fh:
            first = fh.read(1)
        if first != b'\x14':
            total_skip += 1; comp_stats[comp]['skip'] += 1
            continue
    except Exception:
        total_skip += 1; comp_stats[comp]['skip'] += 1
        continue

    r = subprocess.run(['bin/qvm_bootstrap', f], capture_output=True, text=True, timeout=10)
    if r.returncode == 0:
        total_pass += 1; comp_stats[comp]['pass'] += 1
    else:
        total_fail += 1; comp_stats[comp]['fail'] += 1

print(f"QVM: PASS={total_pass} FAIL={total_fail} SKIP={total_skip} TOTAL_VALID={total_pass+total_fail} TOTAL_QBC={len(qbc_files)}")
print()
print(f"{'组件':<15} {'PASS':>6} {'FAIL':>6} {'SKIP':>6} {'TOTAL':>6}")
print("-" * 45)
for comp in sorted(comp_stats.keys()):
    s = comp_stats[comp]
    total = s['pass'] + s['fail'] + s['skip']
    print(f"{comp:<15} {s['pass']:>6} {s['fail']:>6} {s['skip']:>6} {total:>6}")
print("-" * 45)
print(f"{'合计':<15} {total_pass:>6} {total_fail:>6} {total_skip:>6} {total_pass+total_fail+total_skip:>6}")
