#!/bin/bash
# compile_recognize.sh — 编译 recognize_v1.qentl → run/recognize_v1.qbc
# 用 qvm_boot + run/qcl.qbc (QEntL编译器) 编译
cd /root/QSM/QLife || exit 1

SRC="qdfs/ns/train/recognize_v1.qentl"
OUT="run/recognize_v1.qbc"

echo "===== 编译 $SRC → $OUT (via qvm_boot + run/qcl.qbc) ====="
cp "$SRC" input.qentl

OUTLOG=$(bin/qvm_boot run run/qcl.qbc 2>&1)
RC=$?
echo "$OUTLOG"
ERRS=$(grep -o 'errors=[0-9]*' <<<"$OUTLOG" | head -1 | cut -d= -f2)
echo "--- rc=$RC errors=$ERRS ---"
if [ -z "$ERRS" ] || [ "$ERRS" != "0" ]; then
    echo "!!! 编译失败 errors=$ERRS, 中止"
    exit 2
fi
if [ ! -f output.qbc ]; then
    echo "!!! output.qbc 未生成, 中止"
    exit 3
fi
cp output.qbc "$OUT"
echo "编译成功: $SRC → $OUT ($(wc -c <"$OUT") bytes)"
