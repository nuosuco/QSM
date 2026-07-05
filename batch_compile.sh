#!/bin/bash
set -euo pipefail
COMPILER="bin/qcl_phase2"
FILES=(
  "QEntL/System/Deployment/development_mode.qentl"
  "QEntL/System/Deployment/production_mode.qentl"
  "QEntL/System/Deployment/specialized_mode.qentl"
  "QEntL/System/VM/src/deployment/qpu_adapter_cloud.qentl"
  "QEntL/System/VM/src/deployment/qpu_adapter_hardware.qentl"
  "QEntL/System/VM/src/deployment/qpu_adapter_qvm.qentl"
  "QEntL/System/VM/src/deployment/qpu_bytecode_converter.qentl"
  "QEntL/System/VM/src/deployment/qpu_deployment_config.qentl"
  "QEntL/System/VM/src/deployment/qpu_deployment_router.qentl"
  "QEntL/System/VM/src/deployment/qpu_deployment_types.qentl"
  "QEntL/System/VM/src/deployment/qpu_runtime_detector.qentl"
)

echo "=== BATCH COMPILE: Quantum 3 Deployment ==="
echo ""

OK=0
FAIL=0
FAIL_LIST=""

for src in "${FILES[@]}"; do
  base="${src%.qentl}"
  out="build_output/${base}.qbc"
  # ensure output dir
  mkdir -p "$(dirname "$out")"
  
  if $COMPILER "$src" "$out" > /dev/null 2>&1; then
    OK=$((OK+1))
    printf "  OK    %-65s -> %s\n" "$src" "$out"
  else
    FAIL=$((FAIL+1))
    FAIL_LIST="$FAIL_LIST $src"
    printf "  FAIL  %-65s\n" "$src"
  fi
done

echo ""
echo "Result: OK=$OK  FAIL=$FAIL  TOTAL=${#FILES[@]}"
[ -n "$FAIL_LIST" ] && echo "Failed:$FAIL_LIST"
