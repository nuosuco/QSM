#!/usr/bin/env python3
"""QVM 全量审计 — 只对 0x14 有效 qbc 执行 QVM，统计 PASS/FAIL 及周期/门数。"""
import subprocess, os, glob, re, sys

REPO = "/root/QSM"
QVM = os.path.join(REPO, "bin/qvm_bootstrap")
os.chdir(REPO)

# 权威 qbc 只取 QEntL/ 树
qentl_files = sorted(glob.glob("QEntL/**/*.qbc", recursive=True))

CORE = [
    "QEntL/System/Kernel/neural/qns_training_circuit.qbc",
    "QEntL/System/Kernel/neural/qns_backprop_circuit.qbc",
    "QEntL/System/Kernel/qns_qdfs_dataflow.qbc",
    "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc",
    "QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc",
    "QEntL/System/Kernel/filesystem/grover_search_circuit.qbc",
    "QEntL/Models/QSM/qsm_entanglement_circuit.qbc",
    "QEntL/Models/QSM/qsm_consciousness_circuit.qbc",
    "QEntL/Models/QSM/yi_training_pipeline_circuit.qbc",
    "QEntL/Models/QSM/qsm_yi_training_circuit.qbc",
    "QEntL/Models/QSM/qsm_entry.qbc",
    "QEntL/Models/Ref/ref_healing_circuit.qbc",
    "QEntL/Models/Ref/ref_monitoring_circuit.qbc",
    "QEntL/Models/Ref/ref_optimization_circuit.qbc",
    "QEntL/Models/Ref/ref_entry.qbc",
    "QEntL/Models/SOM/som_transaction_circuit.qbc",
    "QEntL/Models/SOM/som_entry.qbc",
    "QEntL/Models/WeQ/weq_learning_circuit.qbc",
    "QEntL/Models/WeQ/weq_social_interaction_circuit.qbc",
    "QEntL/Models/WeQ/weq_entry.qbc",
    "QEntL/Models/Models_QNS_Integration_Test.qbc",
]

def audit(qbc_path):
    # 读头部
    try:
        with open(qbc_path, "rb") as fh:
            head = fh.read(2)
    except Exception as e:
        return {"status": "ERR_READ", "err": str(e)}
    if not head:
        return {"status": "EMPTY"}
    first = head[0]
    if first == 0x14:
        r = subprocess.run([QVM, qbc_path], capture_output=True, text=True, timeout=15)
        out = (r.stdout + "\n" + r.stderr).strip()
        rc = r.returncode
        # 解析最后一行 "执行完成: N 周期, M 门操作"
        m = re.search(r"(\d+)\s*周期.*?(\d+)\s*门", out)
        cycles = int(m.group(1)) if m else None
        gates  = int(m.group(2)) if m else None
        # 检查 CNOT 是否有报错/异常
        cnot_lines = [l for l in out.split("\n") if "CNOT" in l]
        cnot_err = any("ERROR" in l or "error" in l or "Invalid" in l for l in cnot_lines)
        cnot_ok = (not cnot_err) and (len(cnot_lines) >= 0)  # 无 CNOT 也视为 ok
        return {
            "status": "PASS" if rc == 0 else "FAIL",
            "rc": rc,
            "cycles": cycles,
            "gates": gates,
            "cnot_ok": cnot_ok,
            "cnot_count": len(cnot_lines),
            "err": out[-300:] if rc != 0 else "",
        }
    elif first == 0x72:
        return {"status": "SKIP_ASCII"}
    else:
        return {"status": "SKIP_OTHER", "first_byte": f"0x{first:02x}"}

# ---------- 全量审计 ----------
results = {}
n_total_qbc = 0
n_valid = 0
n_pass = 0
n_fail = 0
n_skip_ascii = 0
n_skip_other = 0
fail_list = []

for f in qentl_files:
    n_total_qbc += 1
    r = audit(f)
    results[f] = r
    st = r["status"]
    if st == "PASS":
        n_valid += 1; n_pass += 1
    elif st == "FAIL":
        n_valid += 1; n_fail += 1
        fail_list.append((f, r.get("err", "")))
    elif st == "SKIP_ASCII":
        n_skip_ascii += 1
    elif st == "SKIP_OTHER":
        n_skip_other += 1
    else:
        n_skip_other += 1  # ERR/EMPTY

# ---------- 21 核心电路 ----------
print("=" * 72)
print("【全量审计结果】QEntL/ 树")
print("=" * 72)
print(f"  .qbc 文件总数:     {n_total_qbc}")
print(f"  有效 qbc (0x14):   {n_valid}")
print(f"  PASS:              {n_pass}")
print(f"  FAIL:              {n_fail}")
print(f"  跳过 ASCII (0x72): {n_skip_ascii}")
print(f"  跳过其他:          {n_skip_other}")
print()

print("=" * 72)
print("【21 核心量子电路 逐文件报告】")
print("=" * 72)
print(f"{'电路路径':<66} {'状态':>5} {'周期':>5} {'门数':>5} {'CNOT':>6}")
print("-" * 90)
core_pass = core_fail = 0
core_missing = []
for c in CORE:
    r = results.get(c)
    if r is None:
        core_missing.append(c)
        print(f"{c:<66} {'MISS':>5} {'-':>5} {'-':>5} {'-':>6}")
        continue
    st = r["status"]
    cyc = str(r.get("cycles")) if r.get("cycles") is not None else "-"
    gat = str(r.get("gates"))  if r.get("gates")  is not None else "-"
    cnot = "OK" if r.get("cnot_ok") else "BAD"
    print(f"{c:<66} {st:>5} {cyc:>5} {gat:>5} {cnot:>6}")
    if st == "PASS":
        core_pass += 1
    else:
        core_fail += 1

print("-" * 90)
print(f"核心电路: PASS={core_pass}  FAIL={core_fail}  MISSING={len(core_missing)}")
if core_missing:
    print("缺失文件:")
    for m in core_missing:
        print(f"  - {m}")

print()
print("=" * 72)
print("【FAIL 列表（全量）】")
print("=" * 72)
if fail_list:
    for f, err in fail_list:
        print(f"  FAIL  {f}")
        print(f"        {err.strip()[:200]}")
else:
    print("  (无)")

print()
print("审计完成。")
