#!/bin/bash
# 展开 5316 各态独立 42批行文件 (variant_b{B}_s{S}_stream.w → state{S}_row_b{B}.w)
# 每个态 s0~s3 各自一套 42 行×132096 权重 (真叠加态独立权重, 非坍缩合并)
# 与 merged_row_b{B}.w (4态相加坍缩单份) 并存, 识别端可各态独立 argmax + 投票
set -u
cd /root/QSM/QLife
MD=qdfs/ns/models

# 提取 stream 的 C 行 → 129行×1024值 (与 merge_variants.sh extract 同款)
extract() {
  gawk '/^C[0-9]+:/{
    n=split($0,a,": "); split(a[2],px,",")
    line=""
    for(i=1;i<=1024;i++){v=px[i]; if(v==""||v==0)v=0; line=line v; if(i<1024) line=line ","}
    print line
  }' "$1"
}

for S in 0 1 2 3; do
  for B in $(seq 0 41); do
    SF=$MD/variant_b${B}_s${S}_stream.w
    OF=$MD/state${S}_row_b${B}.w
    if [ ! -f "$SF" ]; then
      # 缺 stream → 补全零 42行 (b41=27类, 其余129类)
      NC=129; [ $B -eq 41 ] && NC=27
      gawk -v nc="$NC" 'BEGIN{for(c=0;c<nc;c++){for(i=0;i<1024;i++) printf "0%s",(i<1023?",":"\n")}}' > "$OF"
      echo "态s$S 批b$B: 缺stream 补零"
      continue
    fi
    extract "$SF" > /tmp/s${S}_part.txt
    L=$(wc -l < /tmp/s${S}_part.txt)
    if [ $L -lt 129 ]; then
      gawk -v nc="$((129-L))" 'BEGIN{for(c=0;c<nc;c++){for(i=0;i<1024;i++) printf "0%s",(i<1023?",":"\n")}}' >> /tmp/s${S}_part.txt
    elif [ $L -gt 129 ]; then
      head -129 /tmp/s${S}_part.txt > /tmp/s${S}_part.h && mv /tmp/s${S}_part.h /tmp/s${S}_part.txt
    fi
    # b41: 129行里只保留 27 类 (C0-C26), 截断为 27 行
    if [ $B -eq 41 ]; then
      head -27 /tmp/s${S}_part.txt > /tmp/s${S}_part.h && mv /tmp/s${S}_part.h /tmp/s${S}_part.txt
    fi
    # 129行×1024 → 1行×132096 (27行→27648)
    gawk -F',' 'BEGIN{first=1} {for(i=1;i<=NF;i++){if(first && i==1) first=0; else printf ","; printf "%s",$i}} END{print ""}' /tmp/s${S}_part.txt > "$OF"
  done
done
rm -f /tmp/s*_part.txt

echo '=== 展开完成, 校验各态 42 行 + 非零量(验证4态独立) ==='
for S in 0 1 2 3; do
  L=$(cat $MD/state${S}_row_b0.w 2>/dev/null | wc -l)
  VALS=$(head -1 $MD/state${S}_row_b0.w 2>/dev/null | gawk -F',' '{print NF}')
  NZ=$(gawk -F',' '{for(i=1;i<=NF;i++) if($i!=0) n++} END{print n+0}' $MD/state${S}_row_b0.w 2>/dev/null)
  TOT=$(ls $MD/state${S}_row_b*.w 2>/dev/null | wc -l)
  echo "态s$S: b0行数=$L 首行值数=$VALS b0非零=$NZ 总文件=$TOT/42"
done
echo '=== 各态 b0 独立验证 (非零量应互不相同) ==='
for S in 0 1 2 3; do
  NZ=$(gawk -F',' '{for(i=1;i<=NF;i++) if($i!=0) n++} END{print n+0}' $MD/state${S}_row_b0.w 2>/dev/null)
  echo "态s$S b0 非零=$NZ"
done
