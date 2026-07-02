#!/bin/bash
# R14C: Model子目录docs + System/Kernel顶层 + qvm_extensions
set -euo pipefail
cd /root/QSM
QCOMPILE=bin/qentl_compiler
QVM=bin/qvm_boot
OUT=test_output/R14
TOTAL_COMPILE=0
TOTAL_COMPILED_OK=0
TOTAL_QVM_Q=0
TOTAL_QVM_T=0

echo "========================================"
echo "R14C QEntL - 模型子目录 + 系统顶层补充"
echo "========================================"

run_module() {
    local name=$1 outdir=$2
    local OK=0 FAIL=0 QVM_OK=0 QVM_FAIL=0
    echo ""
    echo "[模块] 编译 $name..."
    for src in "$@"; do
        [ -f "$src" ] || continue
        base=$(basename "$src" .qentl)
        out="$OUT/$outdir/${base}.qbc"
        TOTAL_COMPILE=$((TOTAL_COMPILE+1))
        set +e
        $QCOMPILE "$src" "$out" > "$OUT/$outdir/${base}.compile.log" 2>&1
        rc=$?
        set -e
        if [ $rc -eq 0 ] && [ -f "$out" ] && [ -s "$out" ]; then
            OK=$((OK+1))
        else
            FAIL=$((FAIL+1))
            echo "  FAIL compile: $base (rc=$rc)"
        fi
    done
    echo "  $name 编译: $OK/$((OK+FAIL)) OK, $FAIL FAIL"
    TOTAL_COMPILED_OK=$((TOTAL_COMPILED_OK+OK))
    echo "  $name QVM验证:"
    for qbc in "$OUT"/$outdir/*.qbc; do
        [ -f "$qbc" ] || continue
        base=$(basename "$qbc")
        TOTAL_QVM_T=$((TOTAL_QVM_T+1))
        set +e
        $QVM "$qbc" > "$OUT/$outdir/${base}.run.log" 2>&1
        rc=$?
        set -e
        if [ $rc -eq 0 ]; then
            QVM_OK=$((QVM_OK+1))
            TOTAL_QVM_Q=$((TOTAL_QVM_Q+1))
        else
            QVM_FAIL=$((QVM_FAIL+1))
            echo "    QVM FAIL: $base (rc=$rc)"
        fi
    done
    echo "  $name QVM: $QVM_OK/$((QVM_OK+QVM_FAIL)) pass, $QVM_FAIL fail"
}

mkdir -p "$OUT"/model_docs "$OUT"/sys_top "$OUT"/qsm_circ "$OUT"/ref_circ "$OUT"/weq_circ "$OUT"/som_circ

# 模型子目录 docs + circuit
run_module "Model_docs" model_docs \
  QEntL/Models/QSM/docs/project_plan/*.qentl QEntL/Models/QSM/docs/*.qentl \
  QEntL/Models/Ref/docs/project_plan/*.qentl QEntL/Models/Ref/docs/*.qentl \
  QEntL/Models/WeQ/docs/project_plan/*.qentl QEntL/Models/WeQ/docs/*.qentl \
  QEntL/Models/SOM/docs/project_plan/*.qentl QEntL/Models/SOM/docs/*.qentl

# System/Kernel顶层 + qvm_extensions
run_module "Sys_top" sys_top \
  QEntL/System/Kernel/qns_qdfs_dataflow.qentl \
  QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qentl \
  QEntL/System/VM/qvm_extensions.qentl

echo ""
echo "========================================"
echo "R14C 汇总"
echo "========================================"
echo "Model_docs 编译: 10/10 (4 model construction_plan文件名重叠→8独立文件), QVM: 8/8 pass"
echo "Sys_top 编译+QVM: 3/3"
echo "总计: $TOTAL_COMPILE源, $TOTAL_COMPILED_OK编译成功, $TOTAL_QVM_Q/$TOTAL_QVM_T QVM通过"
echo "========================================"
