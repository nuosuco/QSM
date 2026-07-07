#!/bin/bash
# generate_stress_test.sh — 生成极端压力测试 .qentl
# $1 = 量子比特数 (默认 80), $2 = 指令数 (默认 1200)
NQ=${1:-80}
NOPS=${2:-1200}
OUT=${3:-/tmp/stress_test.qentl}

cat > "$OUT" <<EOF
// 压力测试: $NQ 量子比特, $NOPS 条指令
init $NQ
EOF

n=0
for ((i=0; i<NQ && n<NOPS; i++)); do
  echo "H $i" >> "$OUT"
  n=$((n+1))
done

# 填充剩余指令用混合门
for ((i=0; n<NOPS; i++)); do
  q=$((i % NQ))
  case $((i % 6)) in
    0) echo "X $q" >> "$OUT";;
    1) echo "Y $q" >> "$OUT";;
    2) echo "Z $q" >> "$OUT";;
    3) echo "T $q" >> "$OUT";;
    4) echo "S $q" >> "$OUT";;
    5) echo "CNOT $q $(( (q+1) % NQ ))" >> "$OUT";;
  esac
  n=$((n+1))
done

# 测量 + 复杂控制流(简化)
for ((i=0; i<8 && n<NOPS; i++)); do
  echo "MEASURE $i $i" >> "$OUT"
  n=$((n+1))
done

echo "PRINT 0" >> "$OUT"
echo "STOP" >> "$OUT"

echo "[stress] 生成 $OUT: $NQ 量子比特, $n 条指令"
