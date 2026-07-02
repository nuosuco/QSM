#!/bin/bash
set -e
cd /root/QSM
COMPILER=./bin/qcl_bootstrap
QVM=./bin/qvm_bootstrap
LOGFILE="/root/QSM/build_report.txt"
> "$LOGFILE"

compile() {
    local src="$1"
    local base
    base=$(echo "$src" | sed 's/\.qentl$/.qbc/')
    if [ ! -f "$src" ]; then
        echo "[SKIP] 文件不存在: $src" >> "$LOGFILE"
        return 1
    fi
    local out
    out=$($COMPILER "$src" "$base" 2>&1)
    local rc=$?
    if [ $rc -ne 0 ]; then
        echo "[FAIL] $src : $out" >> "$LOGFILE"
        return 1
    fi
    local header
    header=$(xxd -l 2 -g 1 "$base" 2>/dev/null | awk '{print $2}')
    local size
    size=$(stat -c%s "$base" 2>/dev/null || echo "?")
    echo "[OK]   $src -> $base (${size}B, header=0x${header})" >> "$LOGFILE"
    return 0
}

run_qvm() {
    local qbc="$1"
    if [ ! -f "$qbc" ]; then
        echo "[QVM-NA] 无字节码: $qbc" >> "$LOGFILE"
        return
    fi
    local result
    result=$($QVM "$qbc" 2>&1)
    local cycles
    cycles=$(echo "$result" | grep -oP '(\d+) 周期' | head -1 || echo "?")
    local gates
    gates=$(echo "$result" | grep -oP '(\d+) 门' | head -1 || echo "?")
    echo "[QVM]  $qbc: ${cycles}周期 ${gates}门" >> "$LOGFILE"
}

echo "========================================" >> "$LOGFILE"
echo "QCL全量编译报告 - $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE"
echo "========================================" >> "$LOGFILE"
echo "" >> "$LOGFILE"
echo "=== 重点电路 ===" >> "$LOGFILE"
# 1. qns_training_circuit
compile "QEntL/System/Kernel/neural/qns_training_circuit.qentl"
# 2. qns_backprop_circuit
compile "QEntL/System/Kernel/neural/qns_backprop_circuit.qentl"
# 3. qdfs_quantum_circuit
compile "QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qentl"
# 4. grover_search_circuit
compile "QEntL/System/Kernel/filesystem/grover_search_circuit.qentl"
# 四大模型电路
echo "" >> "$LOGFILE"
echo "=== 四大模型电路 ===" >> "$LOGFILE"
compile "QEntL/Models/QSM/qsm_consciousness_circuit.qentl"
compile "QEntL/Models/QSM/qsm_entanglement_circuit.qentl"
compile "QEntL/Models/QSM/qsm_yi_training_circuit.qentl"
compile "QEntL/Models/Ref/ref_healing_circuit.qentl"
compile "QEntL/Models/Ref/ref_monitoring_circuit.qentl"
compile "QEntL/Models/Ref/ref_optimization_circuit.qentl"
compile "QEntL/Models/SOM/som_transaction_circuit.qentl"
compile "QEntL/Models/WeQ/weq_learning_circuit.qentl"
compile "QEntL/Models/WeQ/weq_social_interaction_circuit.qentl"
# QNS其他电路
compile "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qentl"
compile "QEntL/Models/QSM/yi_training_pipeline_circuit.qentl"
echo "" >> "$LOGFILE"
echo "=== QVM验证执行 ===" >> "$LOGFILE"
for qbc in \
    "QEntL/System/Kernel/neural/qns_training_circuit.qbc" \
    "QEntL/System/Kernel/neural/qns_backprop_circuit.qbc" \
    "QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc" \
    "QEntL/System/Kernel/filesystem/grover_search_circuit.qbc" \
    "QEntL/Models/QSM/qsm_consciousness_circuit.qbc" \
    "QEntL/Models/QSM/qsm_entanglement_circuit.qbc" \
    "QEntL/Models/QSM/qsm_yi_training_circuit.qbc" \
    "QEntL/Models/Ref/ref_healing_circuit.qbc" \
    "QEntL/Models/Ref/ref_monitoring_circuit.qbc" \
    "QEntL/Models/Ref/ref_optimization_circuit.qbc" \
    "QEntL/Models/SOM/som_transaction_circuit.qbc" \
    "QEntL/Models/WeQ/weq_learning_circuit.qbc" \
    "QEntL/Models/WeQ/weq_social_interaction_circuit.qbc" \
    "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc" \
    "QEntL/Models/QSM/yi_training_pipeline_circuit.qbc"; do
    run_qvm "$qbc"
done
echo "" >> "$LOGFILE"
echo "=== 统计 ===" >> "$LOGFILE"
total=$(find . -name "*.qbc" 2>/dev/null | wc -l)
ok=$(grep -c "^\[OK\]" "$LOGFILE" || echo 0)
fail=$(grep -c "^\[FAIL\]" "$LOGFILE" || echo 0)
echo "生成.qbc总数: $total" >> "$LOGFILE"
echo "编译成功: $ok" >> "$LOGFILE"
echo "编译失败: $fail" >> "$LOGFILE"
echo "" >> "$LOGFILE"
echo "=== 文件列表 ===" >> "$LOGFILE"
find . -name "*.qbc" -exec ls -l {} \; >> "$LOGFILE" 2>/dev/null
cat "$LOGFILE"
