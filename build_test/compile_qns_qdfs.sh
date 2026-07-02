#!/bin/bash
# QNS/QDFS full recompile + QVM verification (after CNOT fix)
set -e
cd /root/QSM
QENTL=./bin/qentl_compiler
QVM=./bin/qvm_boot
OUTDIR=test_output/round12
mkdir -p "$OUTDIR"

COMPILE_LOG="$OUTDIR/compile.log"
QVM_LOG="$OUTDIR/qvm.log"
> "$COMPILE_LOG"
> "$QVM_LOG"

QNS_SRC="QEntL/System/Kernel/neural"
QNS_BIN="bin/qns"
QDFS_SRC="QEntL/System/Kernel/filesystem"
QDFS_BIN="bin/qdfs"

ok_c=0; fail_c=0; total_c=0
ok_v=0; fail_v=0; total_v=0

compile_group() {
    local label=$1 src=$2 destdir=$3
    mkdir -p "$destdir"
    local c_ok=0 c_fail=0 c_tot=0
    local v_ok=0 v_fail=0 v_tot=0
    echo "=== COMPILATION: $label ==="
    for f in "$src"/*.qentl; do
        [ -f "$f" ] || continue
        c_tot=$((c_tot+1))
        base=$(basename "$f" .qentl)
        out="$destdir/$base.qbc"
        if $QENTL "$f" "$out" >> "$COMPILE_LOG" 2>&1; then
            c_ok=$((c_ok+1))
        else
            c_fail=$((c_fail+1))
            echo "  [FAIL] $base" >> "$COMPILE_LOG"
        fi
    done
    echo "  Compiled: $c_ok/$c_tot (fail=$c_fail)"
    echo ""
    echo "=== QVM: $label ==="
    for qbc in "$destdir"/*.qbc; do
        [ -f "$qbc" ] || continue
        v_tot=$((v_tot+1))
        base=$(basename "$qbc")
        set +e
        $QVM "$qbc" >> "$QVM_LOG" 2>&1
        rc=$?
        set -e
        if [ $rc -eq 0 ]; then
            v_ok=$((v_ok+1))
        else
            v_fail=$((v_fail+1))
            echo "  [QVM FAIL rc=$rc] $base" >> "$QVM_LOG"
        fi
    done
    echo "  QVM pass: $v_ok/$v_tot (fail=$v_fail)"
    echo ""
    ok_c=$((ok_c+c_ok)); fail_c=$((fail_c+c_fail)); total_c=$((total_c+c_tot))
    ok_v=$((ok_v+v_ok)); fail_v=$((fail_v+v_fail)); total_v=$((total_v+v_tot))
}

compile_group "QNS" "$QNS_SRC" "$QNS_BIN"
compile_group "QDFS" "$QDFS_SRC" "$QDFS_BIN"

echo "========================================"
echo "SUMMARY"
echo "  Compilation: $ok_c/$total_c ok, $fail_c fail"
echo "  QVM:         $ok_v/$total_v pass, $fail_v fail"

# Also show key detailed outputs
echo ""
echo "=== Sample QNS QVM output ==="
grep -A0 "训练\|backprop\|training_circuit\|dataflow\|reverse" "$QVM_LOG" | tail -5
echo ""
echo "=== Detailed QVM stats for circuit files ==="
for qbc in "$QNS_BIN/qns_*.qbc" "$QDFS_BIN/qdfs_quantum_circuit.qbc" "$QDFS_BIN/grover_search_circuit.qbc"; do
    [ -f "$qbc" ] || continue
    echo "--- $(basename $qbc) ---"
    $QVM "$qbc" 2>&1 | grep -E "QVM\] (CNOT|执行完成|初始化|门操作)" | head -3
done
