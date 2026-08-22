#!/bin/bash
# ================================================================
# yi_infer_v4.sh — 真·4态叠加态并行推理(升级后生态入口)
# 架构铁律: 所有计算必须4态不同起点叠加态并行, 严禁串行伪并行
# 4个QVM进程各自加载1态预编译处理器, 并行前向点积argmax, bash仅编排+真多数投票
# 用法: ./yi_infer_v4.sh <char_idx d>
# 输出: "OK|NO d r v0 v1 v2 v3 votes=N top=X"
# ================================================================
set -e
d=$1; B=$(cd "$(dirname "$0")"/.. && pwd); cd "$B"
b=$((d/515)); r=$((d%515)); ds=$((r*64+1)); de=$((r*64+64))

# 取该字64像素
sed -n "${ds},${de}p" qdfs/ns/data/yi_flat_b${b}.bin > /tmp/yi_data.txt

BIN=$(ls bin/qvm_boot 2>/dev/null)
H=build/par_handlers

# 4态真并行: 各自一个QVM进程, 同时前向(不是串行的for循环)
$BIN run "$H/h${b}_0.qbc" >/dev/null 2>&1 &
$BIN run "$H/h${b}_1.qbc" >/dev/null 2>&1 &
$BIN run "$H/h${b}_2.qbc" >/dev/null 2>&1 &
$BIN run "$H/h${b}_3.qbc" >/dev/null 2>&1 &
wait

v0=$(cat /tmp/yi_res0.txt 2>/dev/null); [ -z "$v0" ] && v0=-1
v1=$(cat /tmp/yi_res1.txt 2>/dev/null); [ -z "$v1" ] && v1=-1
v2=$(cat /tmp/yi_res2.txt 2>/dev/null); [ -z "$v2" ] && v2=-1
v3=$(cat /tmp/yi_res3.txt 2>/dev/null); [ -z "$v3" ] && v3=-1

# 真多数投票(叠加态坍缩: 4态独立起点, 出现最多的标签=坍缩结果)
max_votes=0; top=$v0
for cand in $v0 $v1 $v2 $v3; do
  cnt=0
  for v in $v0 $v1 $v2 $v3; do [ "$v" = "$cand" ] && cnt=$((cnt+1)); done
  [ $cnt -gt $max_votes ] && { max_votes=$cnt; top=$cand; }
done
votes=0
[ "$v0" = "$r" ] && votes=$((votes+1))
[ "$v1" = "$r" ] && votes=$((votes+1))
[ "$v2" = "$r" ] && votes=$((votes+1))
[ "$v3" = "$r" ] && votes=$((votes+1))
if [ $max_votes -ge 2 ] && [ "$top" = "$r" ]; then ok="OK"; else ok="NO"; fi
printf "%s %d %d %s %s %s %s votes=%d top=%d" "$ok" "$d" "$r" "$v0" "$v1" "$v2" "$v3" "$votes" "$top"