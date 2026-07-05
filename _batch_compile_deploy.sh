#!/bin/bash
# Batch compile quantum deployment modules and verify

set -o pipefail
C=/root/QSM/bin/qcl_phase2

FILES=(
 "QEntL/System/Deployment/specialized_mode.qentl"
 "QEntL/System/Deployment/production_mode.qentl"
 "QEntL/System/Deployment/development_mode.qentl"
 "QEntL/System/VM/src/deployment/qpu_runtime_detector.qentl"
 "QEntL/System/VM/src/deployment/qpu_deployment_types.qentl"
 "QEntL/System/VM/src/deployment/qpu_deployment_router.qentl"
 "QEntL/System/VM/src/deployment/qpu_deployment_config.qentl"
 "QEntL/System/VM/src/deployment/qpu_bytecode_converter.qentl"
 "QEntL/System/VM/src/deployment/qpu_adapter_qvm.qentl"
 "QEntL/System/VM/src/deployment/qpu_adapter_hardware.qentl"
 "QEntL/System/VM/src/deployment/qpu_adapter_cloud.qentl"
)

OK=0; FAIL=0
for src in "${FILES[@]}"; do
  out="${src%.qentl}.qbc"
  
  # Compile (redirect stdout to capture log)
  outlog=$($C "$src" 2>/tmp/qcl_err)
  rc=$?
  
  if [ $rc -ne 0 ] || [ ! -f "$out" ]; then
    err=$(head -3 /tmp/qcl_err)
    printf "  FAIL  %-65s  rc=%d\n" "$src" "$rc"
    FAIL=$((FAIL+1))
    continue
  fi

  # Verify first byte == 0x14
  firstbyte=$(xxd -l1 -p "$out" 2>/dev/null)
  sz=$(stat -c%s "$out")

  if [ "$firstbyte" != "14" ]; then
    printf "  FAIL  %-65s  first_byte=0x%-2s (expected 0x14)\n" "$src" "$firstbyte"
    FAIL=$((FAIL+1))
    continue
  fi

  OK=$((OK+1))
  printf "  OK    %-65s size=%-6sB  first=0x%-2s  prod=%s\n" "$src" "$sz" "$firstbyte" "$out"
done

echo ""
echo "========================================"
echo "  Batch compile summary"
echo "========================================"
echo "  Total : ${#FILES[@]}"
echo "  OK    : $OK"
echo "  FAIL  : $FAIL"
echo "========================================"
