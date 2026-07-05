#!/bin/bash
# Batch compile all QEntL/System/Platform modules (经典5平台)
set -uo pipefail
cd /root/QSM
COMPILER=./bin/qcl_phase2
SUCCESS=0
FAIL=0
TOTAL_BYTES=0
RESULTS=()

ORDER=(
    "QEntL/System/Platform/platform_types.qentl"
    "QEntL/System/Platform/platform_registry.qentl"
    "QEntL/System/Platform/formats/pe_format.qentl"
    "QEntL/System/Platform/formats/macho_format.qentl"
    "QEntL/System/Platform/formats/elf_format.qentl"
    "QEntL/System/Platform/formats/harmony_format.qentl"
    "QEntL/System/Platform/conversion/binary_converter.qentl"
    "QEntL/System/Platform/platform_entry.qentl"
)

for f in "${ORDER[@]}"; do
    if [ ! -f "$f" ]; then
        RESULTS+=("FAIL | $f | source file not found")
        FAIL=$((FAIL+1))
        continue
    fi
    name=$(basename "$f" .qentl)
    out="${f%.qentl}.qbc"

    compile_output=$(timeout 30 "$COMPILER" "$f" 2>&1) || true

    if ! echo "$compile_output" | grep -q "编译完成" || [ ! -f "$out" ]; then
        RESULTS+=("FAIL | $name | compile failed")
        FAIL=$((FAIL+1))
        echo "  [FAIL] $name -- compile failed" >&2
        continue
    fi

    sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
    TOTAL_BYTES=$((TOTAL_BYTES + sz))
    first_byte=$(xxd -l 1 -p "$out" 2>/dev/null)

    def_count=$(grep -cE '^DEF' "$f" 2>/dev/null || echo 0)
    end_count=$(grep -cE 'END' "$f" 2>/dev/null || echo 0)
    pair_ok="OK"
    if [ "$def_count" != "$end_count" ]; then
        pair_ok="MISMATCH(DEF=$def_count END=$end_count)"
    fi

    if [ "$first_byte" = "14" ]; then
        RESULTS+=("OK   | $name | ${sz}B | 0x14 | $pair_ok")
        SUCCESS=$((SUCCESS+1))
        echo "  [OK  ] $name -- ${sz}B, 0x14, $pair_ok" >&2
    else
        RESULTS+=("FAIL | $name | ${sz}B | header=0x$first_byte (exp 0x14)")
        FAIL=$((FAIL+1))
        echo "  [FAIL] $name -- header=0x$first_byte" >&2
    fi
done

TOTAL=$((SUCCESS+FAIL))
echo ""
echo "========== PLATFORM BATCH COMPILE RESULTS =========="
echo "Modules: $TOTAL | Success: $SUCCESS | Failed: $FAIL | Total bytes: $TOTAL_BYTES"
echo "======================================================"
printf "%-6s %-45s %s\n" "Status" "Module" "Details"
echo "------------------------------------------------------"
for r in "${RESULTS[@]}"; do
    echo "$r"
done
echo "======================================================"
echo "OVERALL: $( [ $FAIL -eq 0 ] && echo 'ALL PASSED' || echo "$FAIL FAILURES" )"
echo "======================================================"
