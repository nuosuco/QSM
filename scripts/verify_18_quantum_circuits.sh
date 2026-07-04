#!/bin/bash
# ====================================================================
# verify_18_quantum_circuits.sh
# 真正量子电路单epoch验证（标准16电路 + 扩展2个 = 18电路）
# 工作流: qcl_bootstrap 编译 .qentl → .qbc; qvm_bootstrap 执行 .qbc
# 基线: 标准16电路单epoch=769门（实测，非763名义值）; 扩展18电路=798门
# 用法: cd /root/QSM && bash scripts/verify_18_quantum_circuits.sh
# ====================================================================
set -u
cd "$(dirname "$0")/.." || cd /root/QSM
OUT=/tmp/verify_18_quantum
rm -rf "$OUT"; mkdir -p "$OUT"

# 18电路清单: 分组/circuit_id|qentl路径
# 前16个 = 标准清单（qentl-3epoch-training-workflow.md）
# #17-18 = 扩展项（高层/纯量子指令混合）
CIRCUITS=(
 "QNS/qns_training_circuit|QEntL/System/Kernel/neural/qns_training_circuit.qentl"
 "QNS/qns_backprop_circuit|QEntL/System/Kernel/neural/qns_backprop_circuit.qentl"
 "QNS/qns_qdfs_dataflow|QEntL/System/Kernel/qns_qdfs_dataflow.qentl"
 "QNS/qns_qdfs_reverse_flow|QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qentl"
 "QDFS/grover_search_circuit|QEntL/System/Kernel/filesystem/grover_search_circuit.qentl"
 "QDFS/qdfs_quantum_circuit|QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qentl"
 "QSM/qsm_yi_training|QEntL/Models/QSM/qsm_yi_training_circuit.qentl"
 "QSM/qsm_entanglement|QEntL/Models/QSM/qsm_entanglement_circuit.qentl"
 "QSM/qsm_consciousness|QEntL/Models/QSM/qsm_consciousness_circuit.qentl"
 "QSM/yi_training_pipeline|QEntL/Models/QSM/yi_training_pipeline_circuit.qentl"
 "SOM/som_transaction|QEntL/Models/SOM/som_transaction_circuit.qentl"
 "WeQ/weq_learning|QEntL/Models/WeQ/weq_learning_circuit.qentl"
 "WeQ/weq_social|QEntL/Models/WeQ/weq_social_interaction_circuit.qentl"
 "Ref/ref_healing|QEntL/Models/Ref/ref_healing_circuit.qentl"
 "Ref/ref_optimization|QEntL/Models/Ref/ref_optimization_circuit.qentl"
 "Ref/ref_monitoring|QEntL/Models/Ref/ref_monitoring_circuit.qentl"
 "QNS/qns_training_pipeline_circuit|QEntL/System/Kernel/neural/qns_training_pipeline_circuit.qentl"
 "QSM/qsm_core|QEntL/Models/QSM/qsm_core.qentl"
)

TOTAL=0; PASS=0; FAIL=0; i=0
std_total=0  # 仅前16个的标准门数

printf "%-3s %-5s %-35s %-8s %-8s\n" "#" "分组" "电路" "exit" "门数"
printf "%-3s %-5s %-35s %-8s %-8s\n" "---" "----" "----" "----" "----"

for entry in "${CIRCUITS[@]}"; do
  i=$((i+1))
  cid=$(echo "$entry" | cut -d'|' -f1 | cut -d'/' -f2)
  grp=$(echo "$entry" | cut -d'|' -f1 | cut -d'/' -f1)
  path=$(echo "$entry" | cut -d'|' -f2)
  qbc="$OUT/${cid}.qbc"; log="$OUT/${cid}.log"
  gate=0; run_ok=0

  if bin/qcl_bootstrap "$path" "$qbc" > "$log" 2>&1; then
    if bin/qvm_bootstrap "$qbc" >> "$log" 2>&1; then
      run_ok=1
      gate=$(grep -oP '\d+(?= 门操作)' "$log" | tail -1)
      [ -z "$gate" ] && gate=0
    fi
  fi

  if [ $run_ok -eq 1 ]; then
    PASS=$((PASS+1))
    TOTAL=$((TOTAL+gate))
    if [ $i -le 16 ]; then std_total=$((std_total+gate)); fi
    printf "%-3d %-5s %-35s %-8s %-8d\n" "$i" "$grp" "$cid" "OK" "$gate"
  else
    FAIL=$((FAIL+1))
    printf "%-3d %-5s %-35s %-8s %-8s\n" "$i" "$grp" "$cid" "FAIL" "-"
    grep -iE '错误|error|fail' "$log" 2>/dev/null | head -2 | sed 's/^/    /'
  fi
done

printf "%-3s %-5s %-35s %-8s %-8s\n" "---" "----" "----" "----" "----"
echo ""
echo "=== 汇总 ==="
echo "通过: $PASS / 18    失败: $FAIL"
echo "扩展18电路总门数: $TOTAL"
echo "标准16电路总门数: $std_total"
echo ""
echo "=== 基线对比 ==="
echo "标准16电路: $std_total vs 基线769  → 差异=$((std_total-769))"
echo "扩展18电路: $TOTAL vs 基线798 → 差异=$((TOTAL-798))"
echo ""
echo "=== 结论 ==="
if [ $FAIL -eq 0 ] && [ $std_total -eq 769 ] && [ $TOTAL -eq 798 ]; then
  echo "✅ 全部通过，门数与基线完全一致（16电路769门，18电路798门）"
  echo "   qcl_phase2高级语法修复未影响纯量子指令电路"
elif [ $FAIL -eq 0 ]; then
  echo "⚠️ 全部通过，但门数与基线有差异（标准$std_total vs 769，扩展$TOTAL vs 798）"
else
  echo "❌ 有失败，需分析原因"
fi
exit $FAIL
