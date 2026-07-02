#!/bin/bash
# QEntL全栈训练 - 21电路 x 3 epoch = 63次QVM执行
cd /root/QSM

VALID_FILES=(
"QEntL/System/Kernel/neural/qns_training_circuit.qbc"
"QEntL/System/Kernel/neural/qns_backprop_circuit.qbc"
"QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc"
"QEntL/System/Kernel/filesystem/grover_search_circuit.qbc"
"QEntL/Models/QSM/qsm_consciousness_circuit.qbc"
"QEntL/Models/QSM/qsm_entanglement_circuit.qbc"
"QEntL/Models/QSM/qsm_entry.qbc"
"QEntL/Models/QSM/qsm_yi_training_circuit.qbc"
"QEntL/Models/QSM/yi_training_pipeline_circuit.qbc"
"QEntL/Models/Ref/ref_entry.qbc"
"QEntL/Models/Ref/ref_healing_circuit.qbc"
"QEntL/Models/Ref/ref_monitoring_circuit.qbc"
"QEntL/Models/Ref/ref_optimization_circuit.qbc"
"QEntL/Models/SOM/som_entry.qbc"
"QEntL/Models/SOM/som_transaction_circuit.qbc"
"QEntL/Models/WeQ/weq_entry.qbc"
"QEntL/Models/WeQ/weq_learning_circuit.qbc"
"QEntL/Models/WeQ/weq_social_interaction_circuit.qbc"
"QEntL/Models/Models_QNS_Integration_Test.qbc"
"QEntL/System/Kernel/qns_qdfs_dataflow.qbc"
"QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc"
)

# Per-file accumulators
declare -A FILE_CYCLES
declare -A FILE_GATES
declare -A FILE_FAILS
TOTAL_CYCLES=0
TOTAL_GATES=0
TOTAL_RUNS=0
TOTAL_FAILS=0

for epoch in 1 2 3; do
    for f in "${VALID_FILES[@]}"; do
        out=$(bin/qvm_bootstrap "$f" 2>&1)
        TOTAL_RUNS=$((TOTAL_RUNS+1))
        if echo "$out" | grep -q "执行完成"; then
            cycles=$(echo "$out" | grep -oP '\d+(?= 周期)')
            gates=$(echo "$out" | grep -oP '\d+(?= 门)')
            cycles=${cycles:-0}
            gates=${gates:-0}
            TOTAL_CYCLES=$((TOTAL_CYCLES+cycles))
            TOTAL_GATES=$((TOTAL_GATES+gates))
            FILE_CYCLES["$f"]=$(( ${FILE_CYCLES["$f"]:-0} + cycles ))
            FILE_GATES["$f"]=$(( ${FILE_GATES["$f"]:-0} + gates ))
        else
            TOTAL_FAILS=$((TOTAL_FAILS+1))
            FILE_FAILS["$f"]=$(( ${FILE_FAILS["$f"]:-0} + 1 ))
        fi
    done
done

echo "=============================================="
echo "QEntL全栈训练完成报告"
echo "=============================================="
echo "EPOCHS=3  CIRCUITS=21  TOTAL_RUNS=$TOTAL_RUNS"
echo "TOTAL_CYCLES=$TOTAL_CYCLES  TOTAL_GATES=$TOTAL_GATES"
echo "FAILS=$TOTAL_FAILS"
echo "=============================================="
echo ""
echo "--- 每电路详情 (3 epoch累计) ---"
printf "%-55s %8s %8s %s\n" "电路文件" "周期" "门数" "状态"
echo "----------------------------------------------------------------"
for f in "${VALID_FILES[@]}"; do
    c=${FILE_CYCLES["$f"]:-0}
    g=${FILE_GATES["$f"]:-0}
    fail=${FILE_FAILS["$f"]:-0}
    if [ "$fail" -gt 0 ]; then
        status="FAIL($fail)"
    else
        status="OK"
    fi
    printf "%-55s %8d %8d %s\n" "$f" "$c" "$g" "$status"
done

echo ""
echo "--- 按模型分类统计 (3 epoch累计) ---"
# QNS
qns_files=("QEntL/System/Kernel/neural/qns_training_circuit.qbc" "QEntL/System/Kernel/neural/qns_backprop_circuit.qbc")
qns_c=0; qns_g=0; qns_f=0
for f in "${qns_files[@]}"; do qns_c=$((qns_c+${FILE_CYCLES["$f"]:-0})); qns_g=$((qns_g+${FILE_GATES["$f"]:-0})); qns_f=$((qns_f+${FILE_FAILS["$f"]:-0})); done
echo "QNS:          cycles=$qns_c  gates=$qns_g  fails=$qns_f  circuits=2"

# QDFS
qdfs_files=("QEntL/System/Kernel/filesystem/qdfs_quantum_circuit.qbc" "QEntL/System/Kernel/filesystem/grover_search_circuit.qbc" "QEntL/System/Kernel/qns_qdfs_dataflow.qbc" "QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qbc")
qdfs_c=0; qdfs_g=0; qdfs_f=0
for f in "${qdfs_files[@]}"; do qdfs_c=$((qdfs_c+${FILE_CYCLES["$f"]:-0})); qdfs_g=$((qdfs_g+${FILE_GATES["$f"]:-0})); qdfs_f=$((qdfs_f+${FILE_FAILS["$f"]:-0})); done
echo "QDFS:         cycles=$qdfs_c  gates=$qdfs_g  fails=$qdfs_f  circuits=4"

# QSM
qsm_files=("QEntL/Models/QSM/qsm_entry.qbc" "QEntL/Models/QSM/qsm_consciousness_circuit.qbc" "QEntL/Models/QSM/qsm_entanglement_circuit.qbc" "QEntL/Models/QSM/qsm_yi_training_circuit.qbc" "QEntL/Models/QSM/yi_training_pipeline_circuit.qbc")
qsm_c=0; qsm_g=0; qsm_f=0
for f in "${qsm_files[@]}"; do qsm_c=$((qsm_c+${FILE_CYCLES["$f"]:-0})); qsm_g=$((qsm_g+${FILE_GATES["$f"]:-0})); qsm_f=$((qsm_f+${FILE_FAILS["$f"]:-0})); done
echo "QSM:          cycles=$qsm_c  gates=$qsm_g  fails=$qsm_f  circuits=5"

# Ref
ref_files=("QEntL/Models/Ref/ref_entry.qbc" "QEntL/Models/Ref/ref_healing_circuit.qbc" "QEntL/Models/Ref/ref_monitoring_circuit.qbc" "QEntL/Models/Ref/ref_optimization_circuit.qbc")
ref_c=0; ref_g=0; ref_f=0
for f in "${ref_files[@]}"; do ref_c=$((ref_c+${FILE_CYCLES["$f"]:-0})); ref_g=$((ref_g+${FILE_GATES["$f"]:-0})); ref_f=$((ref_f+${FILE_FAILS["$f"]:-0})); done
echo "Ref:          cycles=$ref_c  gates=$ref_g  fails=$ref_f  circuits=4"

# SOM
som_files=("QEntL/Models/SOM/som_entry.qbc" "QEntL/Models/SOM/som_transaction_circuit.qbc")
som_c=0; som_g=0; som_f=0
for f in "${som_files[@]}"; do som_c=$((som_c+${FILE_CYCLES["$f"]:-0})); som_g=$((som_g+${FILE_GATES["$f"]:-0})); som_f=$((som_f+${FILE_FAILS["$f"]:-0})); done
echo "SOM:          cycles=$som_c  gates=$som_g  fails=$som_f  circuits=2"

# WeQ
weq_files=("QEntL/Models/WeQ/weq_entry.qbc" "QEntL/Models/WeQ/weq_learning_circuit.qbc" "QEntL/Models/WeQ/weq_social_interaction_circuit.qbc")
weq_c=0; weq_g=0; weq_f=0
for f in "${weq_files[@]}"; do weq_c=$((weq_c+${FILE_CYCLES["$f"]:-0})); weq_g=$((weq_g+${FILE_GATES["$f"]:-0})); weq_f=$((weq_f+${FILE_FAILS["$f"]:-0})); done
echo "WeQ:          cycles=$weq_c  gates=$weq_g  fails=$weq_f  circuits=3"

# Other
other_files=("QEntL/Models/Models_QNS_Integration_Test.qbc")
other_c=0; other_g=0; other_f=0
for f in "${other_files[@]}"; do other_c=$((other_c+${FILE_CYCLES["$f"]:-0})); other_g=$((other_g+${FILE_GATES["$f"]:-0})); other_f=$((other_f+${FILE_FAILS["$f"]:-0})); done
echo "Other:        cycles=$other_c  gates=$other_g  fails=$other_f  circuits=1"

echo ""
echo "=============================================="
echo "GRAND TOTAL:  cycles=$TOTAL_CYCLES  gates=$TOTAL_GATES  fails=$TOTAL_FAILS"
echo "=============================================="
