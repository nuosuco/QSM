#!/bin/bash
# 全量识别验证 v3 - 跳零+转置提速
# 原理: 彝文像素稀疏(点亮~21%), 只累加点亮像素
# 每样本: 对每个点亮像素p, 累加 score[c]+=W[c*1024+p]
# 复杂度: 31896样本 × ~215点亮像素 × 129类 → 还是慢
# 真正提速: 预先把每批权重按"点亮像素列"提取, 但类间像素不同, 只能跳零
set -u
cd /root/QSM/QLife
W=qdfs/ns/models/qscl5316_variant_merged_padded.w
DATA=qdfs/ns/data/yi_glyph_5316_32x32_variant_v6.comma.data
OUT=/tmp/verify_all_v3.log

gawk -v W="$W" '
BEGIN{
  FS=","
  r=0
  while((getline line < W)>0){ r++; split(line,T,","); for(i=1;i<=length(T);i++) WARR[r,i]=T[i]+0 }
  close(W)
}
{
  lbl=strtonum("0x"$1); B=int(lbl/129); if(B>41)B=41
  if(B==41 && lbl>5315) next
  lcl=lbl-(B==41?5289:B*129)
  nc=(B==41)?27:129
  if(lcl<0||lcl>=nc) next
  nr=B+1
  # 收集点亮像素
  for(i=2;i<=NF;i++) if($i!=0) PIX[i-2]=1
  # 对每类, 只算点亮像素
  best=-2147483648; bestc=0
  for(c=0;c<nc;c++){
    base=c*1024
    s=0
    for(i in PIX){ s+=WARR[nr, base+i+1]*1 }   # 点亮像素 x=1
    delete PIX
    if(s>best){best=s;bestc=c}
  }
  total++; tb[B]++; if(bestc==lcl){correct++;cb[B]++}
}
END{
  printf "=== 全量识别验证 v3 跳零 (%s) ===\n", strftime("%m-%d %H:%M")
  for(B=0;B<=41;B++) printf "b%02d: %d/%d = %.1f%%\n", B, cb[B]+0, tb[B], (tb[B]?cb[B]*100.0/tb[B]:0)
  printf "\n=== 全量: %d/%d = %.2f%% ===\n", correct, total, (total?correct*100.0/total:0)
}' "$DATA" > "$OUT" 2>&1
cat "$OUT"
