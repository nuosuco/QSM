#!/bin/bash
# QEntL Full Stack Test Script - Fixed (compiler uses positional args: src out)
set -e
cd /root/QSM

QENTL=./bin/qentl_compiler
QVM=./bin/qvm_boot
COMPILE_OUT=test_output/compile_results.txt
QVM_OUT=test_output/qvm_results.txt
ERRORS=test_output/errors.txt

> "$COMPILE_OUT"
> "$QVM_OUT"
> "$ERRORS"

echo "=== QEntL Full Stack Test ===" > "$COMPILE_OUT"
echo "=== QVM Execution Test ===" > "$QVM_OUT"

# Phase 1: Compile all .qentl files
echo "" >> "$COMPILE_OUT"
echo "=== COMPILATION PHASE ===" >> "$COMPILE_OUT"
COMPILE_OK=0
COMPILE_FAIL=0
COMPILE_TOTAL=0

while IFS= read -r f; do
    COMPILE_TOTAL=$((COMPILE_TOTAL+1))
    out="${f%.qentl}.qbc"
    if $QENTL "$f" "$out" >> "$COMPILE_OUT" 2>&1; then
        COMPILE_OK=$((COMPILE_OK+1))
        echo "  [OK] $f -> $out" >> "$COMPILE_OUT"
    else
        COMPILE_FAIL=$((COMPILE_FAIL+1))
        echo "  [FAIL] $f" >> "$ERRORS"
        $QENTL "$f" "$out" >> "$ERRORS" 2>&1 || true
    fi
done < <(find . -name "*.qentl" | sort)

echo "" >> "$COMPILE_OUT"
echo "Compile Results: $COMPILE_OK/$COMPILE_TOTAL OK, $COMPILE_FAIL FAIL" >> "$COMPILE_OUT"

# Phase 2: Run all .qbc files on QVM (skip libqdfs.a which is not bytecode)
echo "" >> "$QVM_OUT"
echo "=== QVM EXECUTION PHASE ===" >> "$QVM_OUT"
QVM_OK=0
QVM_FAIL=0
QVM_TOTAL=0

while IFS= read -r f; do
    QVM_TOTAL=$((QVM_TOTAL+1))
    if $QVM "$f" >> "$QVM_OUT" 2>&1; then
        QVM_OK=$((QVM_OK+1))
    else
        QVM_FAIL=$((QVM_FAIL+1))
        echo "  [FAIL] $f" >> "$ERRORS"
    fi
done < <(find . -name "*.qbc" -not -name "libqdfs.a" | sort)

echo "" >> "$QVM_OUT"
echo "QVM Results: $QVM_OK/$QVM_TOTAL OK, $QVM_FAIL FAIL" >> "$QVM_OUT"

# Summary
echo ""
echo "============================================="
echo "  QEntL FULL STACK TEST SUMMARY"
echo "============================================="
echo "Compilation: $COMPILE_OK/$COMPILE_TOTAL OK, $COMPILE_FAIL FAIL"
echo "QVM Runtime: $QVM_OK/$QVM_TOTAL OK, $QVM_FAIL FAIL"
echo ""
echo "Details:"
echo "  Compile log: $COMPILE_OUT"
echo "  QVM log:     $QVM_OUT"
echo "  Errors:      $ERRORS"
