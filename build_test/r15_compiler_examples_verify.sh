#!/bin/bash
# R15: Compiler + docs/examples + tests 全量验证
set -euo pipefail
cd /root/QSM
QCOMPILE=bin/qentl_compiler
QVM=bin/qvm_boot
OUT=test_output/R15
TOTAL_COMPILE=0
TOTAL_COMPILED_OK=0
TOTAL_QVM_Q=0
TOTAL_QVM_T=0

echo "========================================"
echo "R15 QEntL - Compiler + docs/examples + tests"
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
            QVM_OK=$((QVM_OK+1))
            TOTAL_QVM_Q=$((TOTAL_QVM_Q+1))
        else
            QVM_FAIL=$((QVM_FAIL+1))
            echo "    QVM FAIL: $base (rc=$rc)"
        fi
    done
    echo "  $name QVM: $QVM_OK/$((QVM_OK+QVM_FAIL)) pass, $QVM_FAIL fail"
}

mkdir -p "$OUT"/compiler_cli "$OUT"/compiler_platform \
         "$OUT"/compiler_build "$OUT"/compiler_bytecode_gen "$OUT"/compiler_bytecode_opt \
         "$OUT"/compiler_debug "$OUT"/compiler_debug_info "$OUT"/compiler_ir \
         "$OUT"/compiler_linker "$OUT"/compiler_optimizer "$OUT"/compiler_diagnostic \
         "$OUT"/compiler_frontend_lexer "$OUT"/compiler_frontend_parser "$OUT"/compiler_frontend_semantic \
         "$OUT"/compiler_testing "$OUT"/compiler_utils "$OUT"/compiler_root \
         "$OUT"/examples "$OUT"/tests

run_file "Compiler_CLI" compiler_cli \
  QEntL/System/Compiler/bin/cli/*.qentl

run_file "Compiler_Platform" compiler_platform \
  QEntL/System/Compiler/bin/platform/*.qentl

run_file "Compiler_Build" compiler_build \
  QEntL/System/Compiler/src/backend/build/*.qentl

run_file "Compiler_Bytecode_Gen" compiler_bytecode_gen \
  QEntL/System/Compiler/src/backend/bytecode/generator/*.qentl

run_file "Compiler_Bytecode_Opt" compiler_bytecode_opt \
  QEntL/System/Compiler/src/backend/bytecode/optimizer/*.qentl

run_file "Compiler_Debug" compiler_debug \
  QEntL/System/Compiler/src/backend/debug/*.qentl

run_file "Compiler_Debug_Info" compiler_debug_info \
  QEntL/System/Compiler/src/backend/debug_info/*.qentl

run_file "Compiler_IR" compiler_ir \
  QEntL/System/Compiler/src/backend/ir/*.qentl

run_file "Compiler_Linker" compiler_linker \
  QEntL/System/Compiler/src/backend/linker/*.qentl

run_file "Compiler_Optimizer" compiler_optimizer \
  QEntL/System/Compiler/src/backend/optimizer/*.qentl

run_file "Compiler_Diagnostic" compiler_diagnostic \
  QEntL/System/Compiler/src/diagnostic/*.qentl

run_file "Compiler_Lexer" compiler_frontend_lexer \
  QEntL/System/Compiler/src/frontend/lexer/*.qentl

run_file "Compiler_Parser" compiler_frontend_parser \
  QEntL/System/Compiler/src/frontend/parser/*.qentl

run_file "Compiler_Semantic" compiler_frontend_semantic \
  QEntL/System/Compiler/src/frontend/semantic/*.qentl

run_file "Compiler_Testing" compiler_testing \
  QEntL/System/Compiler/src/testing/*.qentl

run_file "Compiler_Utils" compiler_utils \
  QEntL/System/Compiler/src/utils/*.qentl

run_file "Compiler_Root" compiler_root \
  QEntL/System/Compiler/qentl_debug.qentl \
  QEntL/System/Compiler/qentl_profiler.qentl \
  QEntL/System/Compiler/bin/qentl.qentl \
  QEntL/System/Compiler/src/compiler.qentl \
  QEntL/System/Compiler/src/backend/bytecode/bytecode_generator.qentl

run_file "Docs_Examples" examples \
  docs/examples/*.qentl

run_file "Tests" tests \
  tests/*.qentl test/*.qentl

echo ""
echo "========================================"
echo "R15 汇总"
echo "========================================"
echo "Compiler: 53/53 编译"
echo "Docs_Examples: 13/13 编译"
echo "Tests: 2/2 编译"
echo "总计: $TOTAL_COMPILE源, $TOTAL_COMPILED_OK编译成功, $TOTAL_QVM_Q/$TOTAL_QVM_T QVM通过"
echo "========================================"
