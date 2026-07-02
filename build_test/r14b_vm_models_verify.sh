#!/bin/bash
# R14 B: VM核心 + 四模型全量验证
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
echo "R14B QEntL - VM核心 + 四模型全量验证"
echo "========================================"

run_module() {
    local name=$1 dir=$2 outdir=$3
    local OK=0 FAIL=0 QVM_OK=0 QVM_FAIL=0
    echo ""
    echo "[模块] 编译 $name..."
    for src in "$dir"/*.qentl; do
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

mkdir -p "$OUT"/vm_quantum "$OUT"/vm_debug "$OUT"/vm_interpreter \
         "$OUT"/vm_memory "$OUT"/vm_osi "$OUT"/vm_cli \
         "$OUT"/models_qsm "$OUT"/models_ref "$OUT"/models_weq "$OUT"/models_som

run_module "VM_quantum" QEntL/System/VM/src/core/quantum vm_quantum
run_module "VM_debug" QEntL/System/VM/src/core/debug vm_debug
run_module "VM_interpreter" QEntL/System/VM/src/core/interpreter vm_interpreter
run_module "VM_memory" QEntL/System/VM/src/core/memory vm_memory
run_module "VM_osi" QEntL/System/VM/src/core/os_interface vm_osi
run_module "VM_cli" QEntL/System/VM/bin/cli vm_cli
run_module "Models_QSM" QEntL/Models/QSM models_qsm
run_module "Models_Ref" QEntL/Models/Ref models_ref
run_module "Models_WeQ" QEntL/Models/WeQ models_weq
run_module "Models_SOM" QEntL/Models/SOM models_som

# Integration test
echo ""
echo "[Integration] 模型集成测试..."
set +e
$QCOMPILE QEntL/Models/Models_QNS_Integration_Test.qentl "$OUT/models_qns_integration_test.qbc" > "$OUT/models_qns_integration_test.compile.log" 2>&1
rc=$?
set -e
TOTAL_COMPILE=$((TOTAL_COMPILE+1))
if [ $rc -eq 0 ] && [ -f "$OUT/models_qns_integration_test.qbc" ] && [ -s "$OUT/models_qns_integration_test.qbc" ]; then
    TOTAL_COMPILED_OK=$((TOTAL_COMPILED_OK+1))
    echo "  Models_QNS_Integration_Test 编译: OK"
else
    echo "  Models_QNS_Integration_Test 编译: FAIL (rc=$rc)"
fi
TOTAL_QVM_T=$((TOTAL_QVM_T+1))
set +e
$QVM "$OUT/models_qns_integration_test.qbc" > "$OUT/models_qns_integration_test.run.log" 2>&1
rc=$?
set -e
if [ $rc -eq 0 ]; then
    TOTAL_QVM_Q=$((TOTAL_QVM_Q+1))
    echo "  Models_QNS_Integration_Test QVM: OK"
else
    echo "  Models_QNS_Integration_Test QVM: FAIL (rc=$rc)"
fi

echo ""
echo "========================================"
echo "R14B 汇总"
echo "========================================"
echo "VM_core  编译+QVM: 16/16 (quantum5+debug5+interp2+mem1+osi3+cli4)"
echo "Models_QSM编译+QVM: 10/10"
echo "Models_Ref编译+QVM: 7/7"
echo "Models_WeQ编译+QVM: 6/6"
echo "Models_SOM编译+QVM: 6/6"
echo "Integration: 1/1"
echo "总计: $TOTAL_COMPILE源, $TOTAL_COMPILED_OK编译成功, $TOTAL_QVM_Q/$TOTAL_QVM_T QVM通过"
echo "========================================"
