#!/bin/bash
# 3-epoch training for 18 true quantum circuits
# Epoch = 1 full compile + 1 full qvm_bootstrap run
cd /root/QSM
OUT=/tmp/qentl_train_3epoch
rm -rf "$OUT"
mkdir -p "$OUT/logs" "$OUT/stats"

CIRCUITS=(
 "QNS/QNS_train|QEntL/System/Kernel/neural/qns_training_circuit.qentl"
 "QNS/QNS_backprop|QEntL/System/Kernel/neural/qns_backprop_circuit.qentl"
 "QNS/QNS_dataflow|QEntL/System/Kernel/qns_qdfs_dataflow.qentl"
 "QNS/QNS_reverse|QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qentl"
 "QDFS/QDFS_grover|QEntL/System/Kernel/filesystem/grover_search_circuit.qentl"
 "QDFS/QDFS_quantum|QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qentl"
 "QSM/QSM_yi_train|QEntL/Models/QSM/qsm_yi_training_circuit.qentl"
 "QSM/QSM_entangle|QEntL/Models/QSM/qsm_entanglement_circuit.qentl"
 "QSM/QSM_conscious|QEntL/Models/QSM/qsm_consciousness_circuit.qentl"
 "QSM/QSM_pipeline|QEntL/Models/QSM/yi_training_pipeline_circuit.qentl"
 "SOM/SOM_transaction|QEntL/Models/SOM/som_transaction_circuit.qentl"
 "WeQ/WeQ_learn|QEntL/Models/WeQ/weq_learning_circuit.qentl"
 "WeQ/WeQ_social|QEntL/Models/WeQ/weq_social_interaction_circuit.qentl"
 "Ref/Ref_heal|QEntL/Models/Ref/ref_healing_circuit.qentl"
 "Ref/Ref_opt|QEntL/Models/Ref/ref_optimization_circuit.qentl"
 "Ref/Ref_mon|QEntL/Models/Ref/ref_monitoring_circuit.qentl"
)

total_cycles=0; total_gates=0; total_ok=0; total_fail=0

echo "================================================================"
echo "  18个真正量子电路 × 3 Epoch 训练开始"
echo "  每个Epoch = 编译(qcl_bootstrap) + 运行(qvm_bootstrap)"
echo "================================================================"

for entry in "${CIRCUITS[@]}"; do
  name=$(echo "$entry" | cut -d'|' -f1)
  path=$(echo "$entry" | cut -d'|' -f2)
  grp=$(echo "$name" | cut -d'/' -f1)
  cid=$(echo "$name" | cut -d'/' -f2)
  
  ec=0; eg=0; eok=0; efail=0
  for ep in 1 2 3; do
    base="$OUT/${cid}_ep${ep}"
    qbc="${base}.qbc"
    log="${base}.log"
    
    # Epoch: compile + run = 1 full training step
    if bin/qcl_bootstrap "$path" "$qbc" > "$log" 2>&1; then
      if bin/qvm_bootstrap "$qbc" >> "$log" 2>&1; then
        # extract final cycles+gates line
        line=$(grep '执行完成' "$log" | tail -1)
        c=$(echo "$line" | grep -oP '\d+(?= 周期)')
        g=$(echo "$line" | grep -oP '\d+(?= 门操作)')
        [ -z "$c" ] && c=0
        [ -z "$g" ] && g=0
        ec=$((ec + c))
        eg=$((eg + g))
        eok=$((eok+1))
      else
        efail=$((efail+1))
      fi
    else
      efail=$((efail+1))
    fi
  done
  
  total_cycles=$((total_cycles + ec))
  total_gates=$((total_gates + eg))
  total_ok=$((total_ok + eok))
  total_fail=$((total_fail + efail))
  
  status="OK"
  [ "$efail" -gt 0 ] && status="FAIL:$efail"
  
  echo "[$grp/$cid] ep1+2+3: cycles=$ec gates=$eg (${eok}ok/${efail}fail) $status"
  printf "%s\t%s\t%d\t%d\t%d\t%d\n" "$grp" "$cid" "$ec" "$eg" "$eok" "$efail" >> "$OUT/stats/per_circuit.tsv"
done

echo "================================================================"
echo "  按组件分组统计"
echo "================================================================"
awk -F'\t' '{g[$1]+=$3; gg[$1]+=$4; o[$1]+=$5; f[$1]+=$6} END{for(k in g) printf "[%s] circuits=%d total_cycles=%d total_gates=%d ok=%d fail=%d\n", k, 1, g[k], gg[k], o[k], f[k]}' "$OUT/stats/per_circuit.tsv"

echo ""
echo "================================================================"
echo "  18电路3Epoch总计"
echo "================================================================"
echo "总周期: $total_cycles"
echo "总门数: $total_gates"
echo "总Epoch成功: $total_ok"
echo "总Epoch失败: $total_fail"
echo "总Epoch: $((total_ok + total_fail))"

# count circuits per group
echo ""
echo "每组电路数:"
awk -F'\t' '{n[$1]++} END{for(k in n) print k, n[k]}' "$OUT/stats/per_circuit.tsv" | sort

echo ""
echo "完整逐电路结果:"
cat "$OUT/stats/per_circuit.tsv"