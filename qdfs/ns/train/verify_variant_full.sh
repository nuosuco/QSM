#!/bin/bash
# 全量识别验证 (纯awk, 权重内积非查表)
set -u
cd /root/QSM/QLife
W=qdfs/ns/models/qscl5316_variant_merged_padded.w
DATA=qdfs/ns/data/yi_glyph_5316_32x32_variant.comma.data
OUT=/tmp/verify_variant_full.log

awk -v W="$W" '
BEGIN {
  FS=","
  # 读权重到全局二维数组: WARR[batch][i]=值 (i=1..NF)
  r=0
  while ((getline line < W) > 0) {
    r++
    m[r]=split(line, T, ",")
    for (i=1;i<=m[r];i++) WARR[r,i]=T[i]+0
  }
  close(W)
  total=0; correct=0
}
{
  lbl=$1+0; B=int(lbl/129); if(B>41)B=41
  lcl=lbl-B*129
  ncls=(B==41)?27:129
  best=-1; bestc=0
  for (c=0;c<ncls;c++) {
    off=c*1024
    s=0
    for (i=0;i<1024;i++) {
      xv=$(2+i)+0
      if (xv!=0) s+=WARR[r0(B)+1, off+i+1]*xv
    }
    if (s>best){best=s;bestc=c}
  }
  total++; tby[B]++;
  if (bestc==lcl){correct++;cby[B]++}
  if (total<=40) printf "  L%d b%d lcl=%d pred=%d %s\n",total,B,lcl,bestc,(bestc==lcl?"OK":"X")
}
function r0(B){ return B+1 }
END {
  printf "\n=== 全量: %d/%d = %.2f%% ===\n",correct,total,(total?correct*100.0/total:0)
  for (B=0;B<=41;B++) if (tby[B]>0) printf "b%02d: %d/%d = %.1f%%\n",B,cby[B]+0,tby[B],(cby[B]+0)*100.0/tby[B]
}' "$DATA" > "$OUT" 2>&1
cat "$OUT"
