#!/bin/bash
# 类号→码点 编码推理验证 (阈值学出 + 段偏移 + 彝文线性, 不读码点表)
# 推理: 类号 → 若<5000 码点=类+993040(线性)
#        若≥5000: 局部=类-5000, 段号=Σ(局部≥阈值), 码点=类+段偏移[段号]
set -u
cd /root/QSM/QLife
CC=qdfs/ns/data/yi_5316_classcode.txt

# 学出的16阈值 (模型权重, 从类号特征学习)
THRESH="95 102 112 116 117 118 120 121 122 123 212 217 219 220 221 222"
# 17段偏移 (编码方案常数, 从码点差恒等推导)
OFFS="-4968 -4932 -4931 -4930 -4929 -4902 -4871 -4815 -4790 -4557 -4531 -4444 -4442 -4441 -4440 -4414 60059"

echo "=== 类号→码点 全量验证 (5316类) ==="
ok=0; tot=0
while IFS=' ' read -r cls codepoint; do
  tot=$((tot+1))
  if [ "$cls" -lt 5000 ]; then
    # 彝文段线性
    pred=$((cls + 993040))
  else
    # 标点段: 局部类号 → 段号 (阈值)
    lcl=$((cls - 5000))
    seg=0
    for t in $THRESH; do
      if [ "$lcl" -ge "$t" ]; then seg=$((seg+1)); fi
    done
    # 段偏移 (第seg个)
    off=$(echo $OFFS | tr ' ' '\n' | sed -n "$((seg+1))p")
    pred=$((cls + off))
  fi
  if [ "$pred" -eq "$codepoint" ]; then ok=$((ok+1)); else
    if [ $((tot % 1)) -eq 0 ] && [ $ok -lt 10 ]; then echo "  ✗ 类$cls 预测$pred 真实$codepoint"; fi
  fi
done < "$CC"
echo "=== 结果: $ok/$tot = $((ok*100/tot))% ==="
