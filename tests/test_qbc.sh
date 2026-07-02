#!/bin/bash
# QBC Phase 2 Test Script
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$SCRIPT_DIR/Docs"
BIN="$SCRIPT_DIR/bin"

echo "=================================="
echo "  QBC Phase 2 Test Suite"
echo "=================================="

# Compile utilities
echo ""
echo "[1] Compiling qbc_gen..."
gcc -std=c11 -O2 -o "$BIN/qbc_gen" "$DOCS/qbc_gen.c"
echo "  [OK] qbc_gen compiled"

echo "[2] Compiling qbc_dump..."
gcc -std=c11 -O2 -o "$BIN/qbc_dump" "$DOCS/qbc_dump.c"
echo "  [OK] qbc_dump compiled"

# Generate Bell state QBC
echo ""
echo "[3] Generating bell.qbc..."
"$BIN/qbc_gen"
echo "  [OK] bell.qbc generated"

# Verify file exists and has correct size: 16 header + 7*13 = 107 bytes
FILESIZE=$(stat -c%s "$BIN/bell.qbc")
EXPECTED=107
if [ "$FILESIZE" -eq "$EXPECTED" ]; then
    echo "  [OK] File size: $FILESIZE bytes (expected $EXPECTED)"
else
    echo "  [FAIL] File size: $FILESIZE bytes (expected $EXPECTED)"
    exit 1
fi

# Dump and verify
echo ""
echo "[4] Dumping bell.qbc..."
"$BIN/qbc_dump" "$BIN/bell.qbc"

# Validate magic number from dump output
if "$BIN/qbc_dump" "$BIN/bell.qbc" 2>&1 | grep -q "(OK)"; then
    echo "  [OK] Magic number validated"
else
    echo "  [FAIL] Magic number check failed"
    exit 1
fi

# Check num_qubits
if "$BIN/qbc_dump" "$BIN/bell.qbc" 2>&1 | grep -q "Num Qubits:.2"; then
    echo "  [OK] Num qubits validated"
else
    echo "  [FAIL] Num qubits check failed"
    exit 1
fi

# Check instruction count
if "$BIN/qbc_dump" "$BIN/bell.qbc" 2>&1 | grep -q "Instructions:.7"; then
    echo "  [OK] Instruction count validated"
else
    echo "  [FAIL] Instruction count check failed"
    exit 1
fi

# Check GATE_1 presence
if "$BIN/qbc_dump" "$BIN/bell.qbc" 2>&1 | grep -q "GATE_1"; then
    echo "  [OK] GATE_1 instruction validated"
else
    echo "  [FAIL] GATE_1 instruction check failed"
    exit 1
fi

# Check GATE_2 presence
if "$BIN/qbc_dump" "$BIN/bell.qbc" 2>&1 | grep -q "GATE_2"; then
    echo "  [OK] GATE_2 (CNOT) instruction validated"
else
    echo "  [FAIL] GATE_2 instruction check failed"
    exit 1
fi

# Check STOP presence
if "$BIN/qbc_dump" "$BIN/bell.qbc" 2>&1 | grep -q "STOP"; then
    echo "  [OK] STOP instruction validated"
else
    echo "  [FAIL] STOP instruction check failed"
    exit 1
fi

echo ""
echo "=================================="
echo "  QBC Phase 2 Tests: ALL PASSED"
echo "=================================="
