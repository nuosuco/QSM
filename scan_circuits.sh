#!/usr/bin/env bash
# Scan QEntL for pure circuit files: contains `init` statement but NO high-level QEntL keywords.
# Circuit files only have gate-level instructions (H,X,Y,Z,T,S,CNOT,SWAP,MEASURE,RESET,BARRIER).
set -u
OUTDIR="/root/QSM/.qentl_build"
mkdir -p "$OUTDIR"
cd /root/QSM

COMPILE_OK=0; COMPILE_FAIL=0
QVM_OK=0; QVM_FAIL=0
CIRCUIT_LIST=""
DEF_FILE="highlevel"
SKIP_FILE="skip_reason"

for f in $(find QEntL/ -name '*.qentl' | sort); do
  has_init=0; has_def=0
  # has_init: line starts with `init ` (whitespace then number)
  grep -qE '^\s*init\s+[0-9]' "$f" 2>/dev/null && has_init=1
  # has_def: contains any high-level QEntL syntax
  grep -qE '^\s*(def |函数|量子模块|类型|导入|class |struct |module |import\b)' "$f" 2>/dev/null && has_def=1
  # also: lines containing "对于" (for-loop), "如果" (if in QEntL), "返回" (return), etc. are high-level too
  grep -qE '^\s*(对于|如果|否则|返回|循环|跳出|继续)\b' "$f" 2>/dev/null && has_def=1

  if [ "$has_init" -eq 1 ] && [ "$has_def" -eq 0 ]; then
    CIRCUIT_LIST="$CIRCUIT_LIST $f"
  else
    if [ "$has_init" -eq 0 ]; then
      echo "SKIP_no_init:$f"
    else
      echo "SKIP_highlevel:$f"
    fi
  fi
done

echo "===CIRCUITS==="
echo "$CIRCUIT_LIST"

# Now compile+QVM each circuit file
for f in $CIRCUIT_LIST; do
  bname=$(basename "$f" .qentl)
  outqbc="$OUTDIR/$bname.qbc"
  if ./bin/qcl_bootstrap "$f" "$outqbc" >/dev/null 2>&1; then
    COMPILE_OK=$((COMPILE_OK+1))
    echo "COMPILE_OK:$f"
    if ./bin/qvm_bootstrap "$outqbc" >/dev/null 2>&1; then
      QVM_OK=$((QVM_OK+1))
      echo "QVM_OK:$f"
    else
      QVM_FAIL=$((QVM_FAIL+1))
      echo "QVM_FAIL:$f"
    fi
  else
    COMPILE_FAIL=$((COMPILE_FAIL+1))
    echo "COMPILE_FAIL:$f"
  fi
done

echo ""
echo "===FINAL==="
echo "TOTAL_QENTL=$(find QEntL/ -name '*.qentl' | wc -l)"
echo "CIRCUIT_COUNT=$(echo $CIRCUIT_LIST | wc -w)"
echo "COMPILE_OK=$COMPILE_OK"
echo "COMPILE_FAIL=$COMPILE_FAIL"
echo "QVM_OK=$QVM_OK"
echo "QVM_FAIL=$QVM_FAIL"
