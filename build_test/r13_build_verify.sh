#!/bin/bash
# R13 全量重编译 + QVM验证
set -euo pipefail
cd /root/QSM
QCOMPILE=bin/qentl_compiler
QVM=bin/qvm_boot
OUT=test_output/R13
mkdir -p "$OUT"/neural "$OUT"/filesystem

echo "========================================"
echo "R13 QEntL 全栈构建 - QNS + QDFS 重编译验证"
echo "========================================"

# ---- QNS 编译 ----
echo ""; echo "[1/4] 编译 QNS (14源文件)..."
QNS_OK=0; QNS_FAIL=0; QNS_FILES=()
for src in QEntL/System/Kernel/neural/*.qentl; do
    base=$(basename "$src" .qentl)
    out="$OUT/neural/${base}.qbc"
    set +e
    $QCOMPILE "$src" "$out" > "$OUT/neural/${base}.compile.log" 2>&1
    rc=$?
    set -e
    if [ $rc -eq 0 ] && [ -f "$out" ] && [ -s "$out" ]; then
        QNS_OK=$((QNS_OK+1))
    else
        QNS_FAIL=$((QNS_FAIL+1))
        echo "  FAIL compile: $base (rc=$rc)"
    fi
    QNS_FILES+=("$out")
done
echo "  QNS 编译: $QNS_OK/$((QNS_OK+QNS_FAIL)) OK, $QNS_FAIL FAIL"

# ---- QDFS 编译 ----
echo ""; echo "[2/4] 编译 QDFS (32源文件)..."
QDFS_OK=0; QDFS_FAIL=0; QDFS_FILES=()
for src in QEntL/System/Kernel/filesystem/*.qentl; do
    base=$(basename "$src" .qentl)
    out="$OUT/filesystem/${base}.qbc"
    set +e
    $QCOMPILE "$src" "$out" > "$OUT/filesystem/${base}.compile.log" 2>&1
    rc=$?
    set -e
    if [ $rc -eq 0 ] && [ -f "$out" ] && [ -s "$out" ]; then
        QDFS_OK=$((QDFS_OK+1))
    else
        QDFS_FAIL=$((QDFS_FAIL+1))
        echo "  FAIL compile: $base (rc=$rc)"
    fi
    QDFS_FILES+=("$out")
done
echo "  QDFS 编译: $QDFS_OK/$((QDFS_OK+QDFS_FAIL)) OK, $QDFS_FAIL FAIL"

# ---- QVM 验证 ----
echo ""; echo "[3/4] QVM验证..."
echo "QNS QVM:"
QNS_QVM_OK=0; QNS_QVM_FAIL=0
for qbc in "$OUT"/neural/*.qbc; do
    [ -f "$qbc" ] || continue
    base=$(basename "$qbc")
    set +e
    $QVM "$qbc" > "$OUT/neural/${base}.run.log" 2>&1
    rc=$?
    set -e
    if [ $rc -eq 0 ]; then
        QNS_QVM_OK=$((QNS_QVM_OK+1))
    else
        QNS_QVM_FAIL=$((QNS_QVM_FAIL+1))
        echo "  QVM FAIL: $base (rc=$rc)"
    fi
done
echo "  QNS QVM: $QNS_QVM_OK/$((QNS_QVM_OK+QNS_QVM_FAIL)) pass, $QNS_QVM_FAIL fail"

echo "QDFS QVM:"
QDFS_QVM_OK=0; QDFS_QVM_FAIL=0
for qbc in "$OUT"/filesystem/*.qbc; do
    [ -f "$qbc" ] || continue
    base=$(basename "$qbc")
    set +e
    $QVM "$qbc" > "$OUT/filesystem/${base}.run.log" 2>&1
    rc=$?
    set -e
    if [ $rc -eq 0 ]; then
        QDFS_QVM_OK=$((QDFS_QVM_OK+1))
    else
        QDFS_QVM_FAIL=$((QDFS_QVM_FAIL+1))
        echo "  QVM FAIL: $base (rc=$rc)"
    fi
done
echo "  QDFS QVM: $QDFS_QVM_OK/$((QDFS_QVM_OK+QDFS_QVM_FAIL)) pass, $QDFS_QVM_FAIL fail"

# ---- CNOT 验证 ----
echo ""; echo "[4/4] CNOT tgt 解析验证..."
$QVM build_test/verify_cnot_tgt.qbc 2>&1 | grep -E "CNOT\(q"

# ---- 汇总 ----
echo ""
echo "========================================"
echo "R13 汇总"
echo "========================================"
echo "QNS  编译: $QNS_OK/$((QNS_OK+QNS_FAIL)) | QVM: $QNS_QVM_OK/$((QNS_QVM_OK+QNS_QVM_FAIL))"
echo "QDFS 编译: $QDFS_OK/$((QDFS_OK+QDFS_FAIL)) | QVM: $QDFS_QVM_OK/$((QDFS_QVM_OK+QDFS_QVM_FAIL))"
TOTAL_COMPILE=$((QNS_OK+QNS_FAIL+QDFS_OK+QDFS_FAIL))
echo "总计: $TOTAL_COMPILE源, $((QNS_OK+QDFS_OK))编译成功, $((QNS_QVM_OK+QDFS_QVM_OK))/$((QNS_QVM_OK+QNS_QVM_FAIL+QDFS_QVM_OK+QDFS_QVM_FAIL)) QVM通过"
echo "========================================"
