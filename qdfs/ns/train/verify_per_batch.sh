#!/bin/bash
# 逐批全量识别验证 (纯awk权重内积, 非查表)
# 每批: 读该批数据行 + 合并权重对应行, 129类argmax
# 输出: /tmp/verify_batch_B.txt  每行: B 正确数 总数 准确率%
set -u
cd /root/QSM/QLife
W=qdfs/ns/models/qscl5316_variant_merged_padded.w
SUMMARY=/tmp/verify_all_summary.txt

for B in $(seq 0 41); do
  NCLS=129
  [ $B -eq 41 ] && NCLS=27
  # 该批的全局类号范围: base=B*129, 类 base..base+NCLS-1 (b41=5289..5315)
  LO=$((B*129))
  HI=$((LO+NCLS-1))
  OUT=/tmp/verify_batch_${B}.txt
  awk -v B=$B -v NCLS=$NCLS -v LO=$LO -v HI=$HI -v W="$W" '
  BEGIN{
    FS=","
    # 读合并权重的第 B+1 行到 WROW[i]
    r=0
    while((getline line < W)>0){
      r++
      if (r==B+1) { m=split(line,T,","); for(i=1;i<=m;i++) WROW[i]=T[i]+0 }
      if (r>B+1) break
    }
    close(W)
    total=0; correct=0
  }
  {
    lbl=$1+0
    if (lbl<LO || lbl>HI) next
    lcl=lbl-LO
    if (lcl>=NCLS) next
    best=-1; bestc=0
    for (c=0;c<NCLS;c++){
      off=c*1024
      s=0
      for(i=0;i<1024;i++){
        xv=$(2+i)+0
        if (xv!=0) s+=WROW[off+i+1]*xv
      }
      if (s>best){best=s;bestc=c}
    }
    total++
    if (bestc==lcl) correct++
  }
  END{
    printf "%d %d %d %.2f\n", B, correct, total, (total?correct*100.0/total:0) > OUT
  }' qdfs/ns/data/yi_glyph_5316_32x32_variant.comma.data
done

cat /tmp/verify_batch_*.txt | sort -n | awk '{
  tc+=$2; tt+=$3
  printf "b%02d: %d/%d = %s%%\n", $1,$2,$3,$4
}
END{
  printf "\n=== 全量 42批: %d/%d = %.2f%% ===\n", tc, tt, (tt?tc*100.0/tt:0)
}' > "$SUMMARY"
cat "$SUMMARY"
