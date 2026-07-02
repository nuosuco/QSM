#!/usr/bin/env python3
"""QEntL全栈训练循环：对所有有效电路执行3个epoch QVM训练"""
import subprocess, re, os, sys
from collections import defaultdict

BASE = "/root/QSM"
QVM = os.path.join(BASE, "bin/qvm_bootstrap")
RESULTS_FILE = os.path.join(BASE, "train_3epoch_results.json")

# 21个有效电路（首字节0x14）
CIRCUITS = [
    # QSM模型
    "QEntL/Models/QSM/qsm_consciousness_circuit.qbc",
    "QEntL/Models/QSM/qsm_entanglement_circuit.qbc",
    "QEntL/Models/QSM/qsm_entry.qbc",
    "QEntL/Models/QSM/qsm_yi_training_circuit.qbc",
    "QEntL/Models/QSM/yi_training_pipeline_circuit.qbc",
    # Ref模型
    "QEntL/Models/Ref/ref_entry.qbc",
    "QEntL/Models/Ref/ref_healing_circuit.qbc",
    "QEntL/Models/Ref/ref_monitoring_circuit.qbc",
    "QEntL/Models/Ref/ref_optimization_circuit.qbc",
    # SOM模型
    "QEntL/Models/SOM/som_transaction_circuit.qbc",
    "QEntL/Models/SOM/som_entry.qbc",
    # WeQ模型
    "QEntL/Models/WeQ/weq_entry.qbc",
    "QEntL/Models/WeQ/weq_learning_circuit.qbc",
    "QEntL/Models/WeQ/weq_social_interaction_circuit.qbc",
    # QNS集成测试
    "QEntL/Models/Models_QNS_Integration_Test.qbc",
    # QDFS
    "QEntL/System/Kernel/filesystem/grover_search_circuit.qbc",
    "QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc",
    # QNS
    "QEntL/System/Kernel/neural/qns_backprop_circuit.qbc",
    "QEntL/System/Kernel/neural/qns_training_circuit.qbc",
    # QNS-QDFS数据流
    "QEntL/System/Kernel/qns_qdfs_dataflow.qbc",
    "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc",
]

def classify(path):
    if "Models/QSM/" in path: return "QSM"
    if "Models/Ref/" in path: return "Ref"
    if "Models/SOM/" in path: return "SOM"
    if "Models/WeQ/" in path: return "WeQ"
    if "Models_QNS_Integration" in path: return "QNS"
    if "qdfs" in path.lower() or "grover" in path.lower(): return "QDFS"
    if "qns_" in path.lower(): return "QNS"
    if "Compiler" in path: return "Compiler"
    return "Other"

def run_circuit(path, epoch):
    full = os.path.join(BASE, path)
    name = os.path.basename(path).replace(".qbc","")
    try:
        r = subprocess.run([QVM, full], capture_output=True, text=True, timeout=60)
        out = (r.stdout + "\n" + r.stderr)
        m = re.search(r"执行完成:\s*(\d+)\s*周期,\s*(\d+)\s*门操作", out)
        if m:
            return {"name": name, "path": path, "ok": True, "cycles": int(m.group(1)), "gates": int(m.group(2)), "error": ""}
        else:
            return {"name": name, "path": path, "ok": False, "cycles": 0, "gates": 0, "error": out[-200:] if out else "(empty)"}
    except subprocess.TimeoutExpired:
        return {"name": name, "path": path, "ok": False, "cycles": 0, "gates": 0, "error": "timeout"}
    except Exception as e:
        return {"name": name, "path": path, "ok": False, "cycles": 0, "gates": 0, "error": str(e)}

results = {}   # path -> list of 3 epoch results
per_model = defaultdict(lambda: {"cycles": 0, "gates": 0, "runs": 0, "fails": 0, "circuits": set()})

for ep in range(3):
    print(f"\n===== EPOCH {ep+1}/3 =====")
    for cp in CIRCUITS:
        r = run_circuit(cp, ep)
        results.setdefault(cp, []).append(r)
        mod = classify(cp)
        per_model[mod]["circuits"].add(cp)
        per_model[mod]["runs"] += 1
        if r["ok"]:
            per_model[mod]["cycles"] += r["cycles"]
            per_model[mod]["gates"] += r["gates"]
        else:
            per_model[mod]["fails"] += 1
            print(f"  FAIL [{ep+1}] {r['name']}: {r['error'][:80]}")

# per-circuit stats
total_cycles = 0; total_gates = 0; total_fails = 0
print("\n" + "="*80)
print("PER-CIRCUIT 详情 (3 epoch平均)")
print("="*80)
for cp in CIRCUITS:
    runs = results[cp]
    oks = [x for x in runs if x["ok"]]
    fails = [x for x in runs if not x["ok"]]
    total_fails += len(fails)
    if oks:
        avg_c = sum(x["cycles"] for x in oks) / len(oks)
        avg_g = sum(x["gates"] for x in oks) / len(oks)
        total_cycles += int(avg_c * 3)  # 近似总
        total_gates += int(avg_g * 3)
        print(f"  {classify(cp):6s} | {runs[0]['name']:35s} | 周期={avg_c:6.1f} | 门数={avg_g:6.1f} | 失败={len(fails)}")
    else:
        print(f"  {classify(cp):6s} | {runs[0]['name']:35s} | 全部失败                    | 失败={len(fails)}")

print("\n" + "="*80)
print("按模型分类统计 (3 epoch 汇总)")
print("="*80)
for mod in ["QSM","Ref","SOM","WeQ","QNS","QDFS","Compiler","Other"]:
    d = per_model.get(mod)
    if not d: continue
    n = len(d["circuits"])
    print(f"  {mod:8s} | 电路数={n} | 总周期={d['cycles']:8d} | 总门数={d['gates']:8d} | 失败={d['fails']}")

print("\n" + "="*80)
print(f"总计: {len(CIRCUITS)}个电路 x 3 epoch = {len(CIRCUITS)*3}次运行")
print(f"总周期 = {per_model['QSM']['cycles']+per_model['Ref']['cycles']+per_model['SOM']['cycles']+per_model['WeQ']['cycles']+per_model['QNS']['cycles']+per_model['QDFS']['cycles']}")
print(f"总门数 = {per_model['QSM']['gates']+per_model['Ref']['gates']+per_model['SOM']['gates']+per_model['WeQ']['gates']+per_model['QNS']['gates']+per_model['QDFS']['gates']}")
print(f"总失败 = {sum(d['fails'] for d in per_model.values())}")
print("="*80)
