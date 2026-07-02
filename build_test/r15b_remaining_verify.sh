#!/bin/bash
# R15B: 剩余docs/aurora/scripts/web/Installer全量验证
set -euo pipefail
cd /root/QSM
QCOMPILE=bin/qentl_compiler
QVM=bin/qvm_boot
OUT=test_output/R15
TOTAL_COMPILE=0; TOTAL_COMPILED_OK=0; TOTAL_QVM_Q=0; TOTAL_QVM_T=0

echo "========================================"
echo "R15B QEntL - 剩余docs/aurora/scripts/web"
echo "========================================"

run_file() {
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
            QVM_OK=$((QVM_OK+1)); TOTAL_QVM_Q=$((TOTAL_QVM_Q+1))
        else
            QVM_FAIL=$((QVM_FAIL+1))
            echo "    QVM FAIL: $base (rc=$rc)"
        fi
    done
    echo "  $name QVM: $QVM_OK/$((QVM_OK+QVM_FAIL)) pass, $QVM_FAIL fail"
}

mkdir -p "$OUT"/docs_arch "$OUT"/docs_philosophy "$OUT"/docs_integration \
         "$OUT"/docs_root "$OUT"/aurora "$OUT"/scripts "$OUT"/web "$OUT"/installer "$OUT"/build_test

run_file "Docs_Architecture" docs_arch docs/architecture/*.qentl

run_file "Docs_Philosophy" docs_philosophy docs/philosophy/*.qentl

run_file "Docs_Integration" docs_integration docs/integration/*.qentl

run_file "Docs_Root" docs_root \
  docs/MASTER_PLAN.qentl docs/MASTER_PLAN_V3.qentl \
  docs/change_history.qentl docs/project_construction_plan.qentl \
  docs/quantum_superposition_model.qentl docs/quantum_vm_runtime.qentl

run_file "Aurora" aurora aurora/*.qentl

run_file "Scripts" scripts QEntL/scripts/*.qentl

run_file "Web" web \
  web/apps/qentl-playground/stdlib.qentl \
  web/apps/desktop-assistant/api/web_desktop_api.qentl

run_file "Installer" installer Installer/qentl_installer.qentl

run_file "Build_Test" build_test \
  build_test/cnot_test.qentl build_test/verify_cnot_tgt.qentl

echo ""
echo "========================================"
echo "R15B 汇总"
echo "========================================"
echo "总计: $TOTAL_COMPILE源, $TOTAL_COMPILED_OK编译成功, $TOTAL_QVM_Q/$TOTAL_QVM_T QVM通过"
echo "========================================"
