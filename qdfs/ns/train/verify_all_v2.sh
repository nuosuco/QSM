#!/bin/bash
# 全量识别验证 v2 (gawk PMA, 权重只读一次, 一次遍历全表)
# 权重内积: score_c = Σ WROW[off+i]*x[i], argmax 129类
set -u
cd /root/QSM/QLife
W=qdfs/ns/models/qscl5316_variant_merged_padded.w
DATA=qdfs/ns/data/yi_glyph_5316_32x32_variant.comma.data
OUT=/tmp/verify_all_v2.log

gawk -v W="$W" '
BEGIN{
  FS=","
  # 一次读完 42 行权重: WARR[row, idx]
  r=0
  while((getline line < W)>0){
    r++
    split(line, T, ",")
    for(i=1;i<=length(T);i++) WARR[r,i]=T[i]+0
  }
  close(W)
  # 每批类数
  for(B=0;B<41;B++) NCLS[B]=129
  NCLS[41]=27
  for(B=0;B<41;B++){ LO[B]=B*129 } LO[41]=5289
  for(B=0;B<41;B++){ HI[B]=LO[B]+128 } HI[41]=5315
}
{
  lbl=$1+0
  # 二分/直接: B=int(lbl/129), 末批特判
  B=int(lbl/129)
  if (B>41) B=41
  if (B==41 && lbl>5315) next
  lcl=lbl-LO[B]
  if (lcl<0 || lcl>=NCLS[B]) next
  nr=B+1
  best=-2147483648; bestc=0
  nc=NCLS[B]
  for(c=0;c<nc;c++){
    base=c*1024+1
    s=0
    for(i=1;i<1024;i++){
      xv=$i+0
      if(xv) s+=WARR[nr, base+i-1]*xv
    }
    if(s>best){best=s;bestc=c}
  }
  total++; if(bestc==lcl){correct++; cb[B]++}
  tb[B]++
}
END{
  printf "=== 全量识别验证 (%s) ===\n", strftime("%m-%d %H:%M")
  printf "权重=%s\n数据=%s\n\n", W, FILENAME
  for(B=0;B<=41;B++) printf "b%02d: %d/%d = %.1f%%\n", B, cb[B]+0, tb[B], (tb[B]?cb[B]*100.0/tb[B]:0)
  printf "\n=== 全量: %d/%d = %.2f%% ===\n", correct, total, (total?correct*100.0/total:0)
}' "$DATA" > "$OUT" 2>&1
cat "$OUT"
