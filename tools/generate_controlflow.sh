#!/bin/bash
# generate_controlflow.sh — 生成含循环/条件结构的测试
# 由于 qcl_bootstrap 仅支持量子指令子集，控制流通过大量门序列模拟
# 输出 > 2000 行 .qentl

OUT=${1:-/tmp/stress_controlflow.qentl}
NQ=32
N=2048

cat > "$OUT" <<EOF
// 控制流压力测试: $NQ 量子比特, $N 行
init $NQ
EOF

for ((i=0; i<NQ; i++)); do
  echo "H $i" >> "$OUT"
done

# 模拟嵌套循环: 32x64 = 2048 次操作
for ((blk=0; blk<64; blk++)); do
  for ((q=0; q<NQ; q++)); do
    echo "X $q" >> "$OUT"
  done
  echo "BARRIER" >> "$OUT"
done

for ((i=0; i<NQ; i++)); do
  echo "MEASURE $i $i" >> "$OUT"
done
echo "PRINT 0" >> "$OUT"
echo "STOP" >> "$OUT"

echo "[controlflow] 生成 $OUT: $(( $(wc -l < "$OUT") )) 行"
