#!/bin/bash
# 重新切分 v6 变体批次 (十进制标签, 按类号范围 129类/批×6变体)
# 输入: yi_glyph_5316_32x32_variant_v6.comma.data (31896行=5316×6)
# 保留全零行 (775标点类编码侧要训, 不能丢)
set -u
cd /root/QSM/QLife
IN=qdfs/ns/data/yi_glyph_5316_32x32_variant_v6.comma.data
OUTD=qdfs/ns/data
rm -f $OUTD/variant_b*.comma.data

# 不去全零, 直接用全表切分 (775标点类要参与编码训练)
for B in $(seq 0 41); do
  S=$((B*129)); E=$((S+128))
  [ $E -gt 5315 ] && E=5315
  gawk -F':' -v s="$S" -v e="$E" '{c=strtonum("0x"$1); if(c>=s && c<=e) print}' "$IN" > $OUTD/variant_b${B}.comma.data
  L=$(wc -l < $OUTD/variant_b${B}.comma.data)
  echo "b${B}: 类${S}-${E} ${L}行"
done
