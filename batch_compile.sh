#!/bin/bash
cd /root/QSM
SRC_DIR="QEntL/System/Kernel/filesystem"
SUCCESS=0
FAIL=0
TOTAL_BYTES=0
RESULTS=()

for f in "$SRC_DIR"/*.qentl; do
    name=$(basename "$f" .qentl)
    out="$SRC_DIR/$name.qbc"
    
    # Compile with 10s timeout per file
    compile_output=$(timeout 10 ./bin/qcl_phase2 "$f" 2>&1)
    compile_rc=$?
    
    if [ $compile_rc -ne 0 ] || ! echo "$compile_output" | grep -q "编译完成"; then
        RESULTS+=("FAIL | $name | rc=$compile_rc")
        FAIL=$((FAIL+1))
        continue
    fi
    
    # Check first byte and size
    first_byte=$(xxd -l 1 -p "$out" 2>/dev/null)
    sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
    TOTAL_BYTES=$((TOTAL_BYTES + sz))
    
    if [ "$first_byte" = "14" ]; then
        fcount=$(echo "$compile_output" | grep -oP '函数=\K[0-9]+')
        RESULTS+=("OK   | $name | $sz bytes | header=0x14 | funcs=$fcount")
        SUCCESS=$((SUCCESS+1))
    else
        RESULTS+=("FAIL | $name | $sz bytes | header=0x$first_byte (exp 0x14)")
        FAIL=$((FAIL+1))
    fi
done

echo "========== QDFS BATCH COMPILE RESULTS =========="
echo "Modules: $((SUCCESS+FAIL)) | Success: $SUCCESS | Failed: $FAIL | Total bytes: $TOTAL_BYTES"
echo "================================================"
for r in "${RESULTS[@]}"; do
    echo "$r"
done
echo "================================================"
