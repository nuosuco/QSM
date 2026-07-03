#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM 项目全面审计脚本"""
import os, subprocess, json, sys

ROOT = "/root/QSM"
QVM = os.path.join(ROOT, "bin", "qvm_bootstrap")

def find_all(suffix):
    r = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # skip .git
        if ".git" in dirpath:
            continue
        for f in filenames:
            if f.endswith(suffix):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, ROOT)
                r.append(rel)
    return sorted(r)

def classify_dir(relpath):
    """relpath is like QEntL/Models/QSM/qsm_core.qentl"""
    parts = relpath.split(os.sep)
    top = parts[0]
    if top == "QEntL":
        segs = parts[1:]  # Models/QSM/...
        joined = "/".join(segs)
        # QNS = QEntL/System/Kernel/neural + cross-layer Kernel/qns_qdfs_*
        if "System/Kernel/neural" in joined and parts[1] == "System":
            return "QNS(Kernel/neural)"
        # QNS cross-layer: Kernel/qns_qdfs_*
        if "System/Kernel" in joined:
            fname = parts[-1]
            if fname.startswith("qns_qdfs_"):
                return "QNS(跨层qns_qdfs)"
        # QDFS filesystem
        if "System/Kernel/filesystem" in joined:
            return "QDFS(filesystem)"
        # QNS core (System/)
        if parts[1] == "System":
            return "QNS(QEntL/System)"
        if "Models/QSM" in joined:
            return "Models/QSM"
        if "Models/SOM" in joined:
            return "Models/SOM"
        if "Models/WeQ" in joined:
            return "Models/WeQ"
        if "Models/Ref" in joined:
            return "Models/Ref"
        if parts[1] == "docs":
            return "docs(QEntL/docs)"
        if parts[1] == "scripts" or parts[1] == "engine":
            return "QEntL(其他)"
        return "QEntL(其他)"
    elif top == "QCL模块":
        return "QCL模块"
    elif top == "docs":
        return "docs"
    elif top == "test":
        return "test"
    elif top == "test_output":
        return "test_output"
    elif top == "web":
        return "web"
    elif top in ("api", "aurora", "bin", "build", "build_test", "data", "full_verify_output", "Installer"):
        return top
    else:
        return top

def first_byte(fpath):
    full = os.path.join(ROOT, fpath)
    try:
        with open(full, "rb") as fh:
            b = fh.read(1)
            if len(b) == 0:
                return None
            return b[0]
    except Exception:
        return None

def qvm_audit(qbc_rel):
    full = os.path.join(ROOT, qbc_rel)
    try:
        out = subprocess.run(
            [QVM, full], capture_output=True, text=True, timeout=30, cwd=ROOT
        )
        combined = (out.stdout or "") + (out.stderr or "")
        rc = out.returncode
        # heuristic: PASS if rc==0 or 'PASS'/'OK' in combined
        pass_fail = "PASS" if (rc == 0 or "PASS" in combined or "OK" in combined.upper()) else "FAIL"
        return pass_fail, rc, combined[:200]
    except subprocess.TimeoutExpired:
        return "TIMEOUT", None, ""
    except Exception as e:
        return "ERROR", None, str(e)

# ===== MAIN =====
qentl_all = find_all(".qentl")
qbc_all = find_all(".qbc")

print(f"[文件计数] .qentl = {len(qentl_all)}, .qbc = {len(qbc_all)}")

qentl_set = set(qentl_all)
qbc_set = set(qbc_all)

# 同名配对：去掉后缀比较
def stem(p):
    return os.path.splitext(p)[0]

qentl_stems = set(stem(p) for p in qentl_all)
qbc_stems = set(stem(p) for p in qbc_all)

missing_qbc = sorted(qentl_stems - qbc_stems)  # 有qentl无qbc
orphan_qbc = sorted(qbc_stems - qentl_stems)    # 有qbc无qentl

print(f"[缺失qbc] 有qentl无qbc: {len(missing_qbc)}")
for m in missing_qbc:
    print(f"  - {m}")
print(f"[孤儿qbc] 有qbc无qentl: {len(orphan_qbc)}")
for o in orphan_qbc:
    print(f"  - {o}")

# 首字节分类 (只对 .qbc)
fb_stat = {"14": [], "72": [], "other": []}
for qbc in qbc_all:
    fb = first_byte(qbc)
    if fb == 14:
        fb_stat["14"].append(qbc)
    elif fb == 72:
        fb_stat["72"].append(qbc)
    else:
        fb_stat["other"].append((qbc, fb))

print(f"\n[首字节分类] 0x14(有效)={len(fb_stat['14'])}, 0x72(无效)={len(fb_stat['72'])}, 其他={len(fb_stat['other'])}")
for k, v in fb_stat["other"]:
    print(f"  其他: {k} -> 0x{v:02x}" if v is not None else f"  其他: {k} -> None(空)")

# QVM审计：只对 0x14
print("\n[QVM审计] 执行 bin/qvm_bootstrap 于 0x14 .qbc ...")
qvm_results = []
pass_count = 0
fail_count = 0
for qbc in fb_stat["14"]:
    pf, rc, msg = qvm_audit(qbc)
    qvm_results.append((qbc, pf, rc, msg))
    if pf == "PASS":
        pass_count += 1
    else:
        fail_count += 1
    if pf != "PASS":
        print(f"  {pf} rc={rc} | {qbc} | {msg[:80]}")

print(f"\n[QVM汇总] PASS={pass_count}, FAIL={fail_count}, 总计={len(fb_stat['14'])}")

# 分组件统计
print("\n===== 分组件统计 =====")
component_stats = {}
def add_component(comp, **kw):
    if comp not in component_stats:
        component_stats[comp] = {"qentl":0,"qbc":0,"valid_qbc":0,"invalid_qbc":0,"qvm_pass":0,"qvm_fail":0}
    for k,v in kw.items():
        component_stats[comp][k] += v

# qentl by component
for p in qentl_all:
    comp = classify_dir(p)
    add_component(comp, qentl=1)

# qbc by component + first byte
qbc_fb_map = {}
for qbc in qbc_all:
    fb = first_byte(qbc)
    qbc_fb_map[qbc] = fb

qvm_pass_set = set(q for q,p,rc,m in qvm_results if p == "PASS")

for qbc in qbc_all:
    comp = classify_dir(qbc)
    fb = qbc_fb_map.get(qbc)
    add_component(comp, qbc=1)
    if fb == 14:
        add_component(comp, valid_qbc=1)
        if qbc in qvm_pass_set:
            add_component(comp, qvm_pass=1)
        else:
            add_component(comp, qvm_fail=1)
    elif fb == 72:
        add_component(comp, invalid_qbc=1)

# sort and print
for comp in sorted(component_stats.keys()):
    s = component_stats[comp]
    line = (f"{comp:30s} | qentl={s['qentl']:3d} qbc={s['qbc']:3d} "
            f"(有效={s['valid_qbc']:2d} 无效={s['invalid_qbc']:2d}) "
            f"QVM PASS={s['qvm_pass']:2d} FAIL={s['qvm_fail']:2d}")
    print(line)

# total
total_qentl = sum(s["qentl"] for s in component_stats.values())
total_qbc = sum(s["qbc"] for s in component_stats.values())
total_valid = sum(s["valid_qbc"] for s in component_stats.values())
total_invalid = sum(s["invalid_qbc"] for s in component_stats.values())
total_pass = sum(s["qvm_pass"] for s in component_stats.values())
total_fail = sum(s["qvm_fail"] for s in component_stats.values())
print(f"\n{'总计':30s} | qentl={total_qentl:3d} qbc={total_qbc:3d} "
      f"(有效={total_valid:2d} 无效={total_invalid:2d}) "
      f"QVM PASS={total_pass:2d} FAIL={total_fail:2d}")

print("\n[DONE] 审计完成")
