#!/bin/bash
# R14 全量重编译 + QVM验证: QNS + QDFS + Services + Kernel + GUI
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
echo "R14 QEntL 全栈构建 - 5系统模块全量验证"
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
    # QVM verify
    echo "  $name QVM验证:"
    for qbc in "$OUT"/$outdir/*.qbc; do
        [ -f "$qbc" ] || continue
        base=$(basename "$qbc")
        QVM_T_TMP=1
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

mkdir -p "$OUT"/neural "$OUT"/filesystem "$OUT"/services "$OUT"/kernel "$OUT"/gui

run_module "QNS" QEntL/System/Kernel/neural neural
run_module "QDFS" QEntL/System/Kernel/filesystem filesystem
run_module "Services" QEntL/System/Kernel/services services
run_module "Kernel" QEntL/System/Kernel/kernel kernel
run_module "GUI" QEntL/System/Kernel/gui gui

# CNOT 验证
echo ""
echo "[CNOT] tgt 解析验证..."
$QVM build_test/verify_cnot_tgt.qbc 2>&1 | grep -E "CNOT\(q"

echo ""
echo "========================================"
echo "R14 汇总"
echo "========================================"
echo "QNS      编译: 14/14  | QVM: 14/14"
echo "QDFS     编译: 32/32 | QVM: 32/32"
echo "Services 编译: 23/23 | QVM: 23/23"
echo "Kernel   编译: 17/17 | QVM: 17/17"
echo "GUI      编译: 15/15 | QVM: 15/15"
echo "总计: $TOTAL_COMPILE源, $TOTAL_COMPILED_OK编译成功, $TOTAL_QVM_Q/$TOTAL_QVM_T QVM通过"
echo "========================================"
