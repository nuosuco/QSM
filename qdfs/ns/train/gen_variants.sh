#!/bin/bash
# 变体生成: 每字6变体(原字+右移1/下移1/右1下1/左移1/上移1)
# 修复: 每变体先全0初始化, 只保留移动方向的有效像素, 清空边界行/列
# 不镜像不旋转, 小幅平移
set -u
cd /root/QSM/QLife
IN=qdfs/ns/data/yi_glyph_5316_32x32.comma.data
# 原始数据标签是hex补零格式(0000-14a3), 转十进制类号
INDEC=$(gawk 'BEGIN{FS=":"}{printf "%d", $1+0}' "$IN" | head -1)
# 检测: 标签最大值若>5315说明是hex, 需转十进制
# 直接用十进制: 行号I-1 = 类号
echo "=== 输入数据标签检查: 行2标签=$(sed -n '2p' "$IN" | cut -d: -f1) ==="
OUT=qdfs/ns/data/yi_glyph_5316_32x32_variant.comma.data
> "$OUT"

echo "=== 变体生成 $(date '+%H:%M:%S') ==="

awk '
function joinP(A,    s,i) {
  s = A[0]
  for (i=1;i<1024;i++) s = s "," A[i]
  return s
}
function zeroarr(A,   i) { for(i=0;i<1024;i++) A[i]=0 }
function gen(label, P, A, r, c) {
  # A 是输出数组, 调用前已清零
}
BEGIN { FS=":"; clsn=0 }
{
  clsn = NR - 1   # 十进制类号 = 行号-1 (0..5315)
  px = $2
  n = split(px, a, ",")
  for (i=0;i<1024;i++) P[i] = (a[i+1]=="1"?1:0)

  # V0 原字
  for(i=0;i<1024;i++) V0[i]=P[i]
  print clsn ":" joinP(V0)

  # V1 右移1列
  zeroarr(V1)
  for (r=0;r<32;r++) for (c=0;c<31;c++) V1[r*32+c+1]=P[r*32+c]
  print clsn ":" joinP(V1)

  # V2 下移1行
  zeroarr(V2)
  for (r=0;r<31;r++) for (c=0;c<32;c++) V2[(r+1)*32+c]=P[r*32+c]
  print clsn ":" joinP(V2)

  # V3 右1下1
  zeroarr(V3)
  for (r=0;r<31;r++) for (c=0;c<31;c++) V3[(r+1)*32+c+1]=P[r*32+c]
  print clsn ":" joinP(V3)

  # V4 左移1列
  zeroarr(V4)
  for (r=0;r<32;r++) for (c=1;c<32;c++) V4[r*32+c-1]=P[r*32+c]
  print clsn ":" joinP(V4)

  # V5 上移1行
  zeroarr(V5)
  for (r=1;r<32;r++) for (c=0;c<32;c++) V5[(r-1)*32+c]=P[r*32+c]
  print clsn ":" joinP(V5)

  for(i=0;i<1024;i++){P[i]=0;V0[i]=0}
}
' "$IN" > "$OUT"

echo "=== 完成 $(date '+%H:%M:%S') ==="
echo "输入: $(wc -l < "$IN")  输出: $(wc -l < "$OUT")  预期: $((5316*6))"
echo "=== 双逗号行数(应为0) ==="
grep -c ",," "$OUT"
echo "=== 每标签变体数分布 ==="
cut -d: -f1 "$OUT" | uniq -c | awk '{print $1}' | sort | uniq -c
echo "=== 标签0000的6变体 非零像素数 ==="
grep "^0000:" "$OUT" | awk -F: '{n=split($2,b,","); o=0; for(i=1;i<=n;i++) if(b[i]=="1")o++; print "变体"NR"非零="o}'
echo "=== 走样检查: 原字非零 vs 各变体非零差值 ==="
grep "^0000:" "$OUT" | head -1 | cut -d: -f2 | awk -F, '{o=0;for(i=1;i<=NF;i++)if($i=="1")o++} END{print "原字非零="o}'
