#!/bin/bash
# 合并 168 个变体 stream (42批×4态) → 42行 padded 权重
# 每批4态逐元素相加(每个C行是1024个像素值), b41=27类
# 2026-10-09: b33-b38 已补数据重训, 全部批次正常累加(不再填零)
set -u
cd /root/QSM/QLife
MD=qdfs/ns/models
OUT=$MD/qscl5316_variant_merged_padded.w
rm -f "$OUT"

# 129行全零 (每行1024个0, 逗号分隔)
gen_zero() {
  local NCL=$1
  gawk -v nc="$NCL" 'BEGIN{
    for(c=0;c<nc;c++){
      for(i=0;i<1024;i++) printf "0%s", (i<1023?",":"\n")
    }
  }'
}
gen_zero 129 > /tmp/zero129.txt

# 提取 stream 的 C 行 → 129行×1024值
extract() {
  gawk '/^C[0-9]+:/{
    n=split($0,a,": "); split(a[2],px,",")
    line=""
    for(i=1;i<=1024;i++){v=px[i]; if(v==""||v==0)v=0; line=line v; if(i<1024) line=line ","}
    print line
  }' "$1"
}

# 逐元素相加两个 1024值文件 → 输出 1024值
add2() {
  # 读两个文件(各1024值逗号行), 输出逐元素和
  gawk -F',' 'NR==FNR{a[FNR]=$0; n=FNR; next} {for(i=1;i<=NF;i++) s[i]+=a[i]; for(i=1;i<=n;i++) printf "%d%s", s[i], (i<n?",":"\n")}' "$1" "$2"
}

for B in $(seq 0 41); do
  if [ $B -eq 41 ]; then
    # b41: 27类 (C0-C26), 4态逐元素相加 → 1行×27648值
    for S in 0 1 2 3; do
      SF=$MD/variant_b41_s${S}_stream.w
      [ -f "$SF" ] || { : > /tmp/b41_s${S}.txt; continue; }
      gawk '/^C[0-9]+:/{cls=$0; sub(/:.*/,"",cls); sub(/^C/,"",cls)
        if (cls+0<27) print}' "$SF" > /tmp/b41_s${S}.txt
    done
    gawk -F',' -v f0=/tmp/b41_s0.txt -v f1=/tmp/b41_s1.txt -v f2=/tmp/b41_s2.txt -v f3=/tmp/b41_s3.txt '
      BEGIN{
        for(f=0;f<4;f++){
          fn=(f==0?f0:f==1?f1:f==2?f2:f3)
          nr=0
          while((getline line < fn)>0){
            nr++
            if (nr>27) break
            n=split(line,px,",")
            for(i=1;i<=1024;i++) A[f,nr,i]=(i<=n)?px[i]+0:0
          }
          close(fn)
        }
        # 缺文件/缺行补0
        for(f=0;f<4;f++) for(row=1;row<=27;row++) for(col=1;col<=1024;col++) if(!( (f,row,col) in A )) A[f,row,col]=0
      }
      END{
        for(row=1;row<=27;row++){
          for(col=1;col<=1024;col++){
            v=A[0,row,col]+A[1,row,col]+A[2,row,col]+A[3,row,col]
            printf "%d%s", v, (row<27 || col<1024 ? "," : "\n")
          }
        }
      }' /dev/null >> "$OUT"
    rm -f /tmp/b41_s0.txt /tmp/b41_s1.txt /tmp/b41_s2.txt /tmp/b41_s3.txt
    continue
  fi

  # 普通批: 129类, 4态逐元素相加
  cat /tmp/zero129.txt > /tmp/sumb.txt
  for S in 0 1 2 3; do
    SF=$MD/variant_b${B}_s${S}_stream.w
    [ -f "$SF" ] || continue
    extract "$SF" > /tmp/stream_part.txt
    L=$(wc -l < /tmp/stream_part.txt)
    if [ "$L" -lt 129 ]; then
      gen_zero $((129-L)) >> /tmp/stream_part.txt
    elif [ "$L" -gt 129 ]; then
      head -129 /tmp/stream_part.txt > /tmp/stream_part.h && mv /tmp/stream_part.h /tmp/stream_part.txt
    fi
    # 逐元素相加 (两个都是 129行×1024值) — 累加两个文件的值
    gawk -F',' 'NR==FNR{for(i=1;i<=NF;i++) a[FNR","i]=$i+0; nr=FNR; next} {for(i=1;i<=1024;i++) s[FNR","i]=a[FNR","i]+($i+0); } END{for(r=1;r<=nr;r++){for(i=1;i<=1024;i++) printf "%d%s", s[r","i], (i<1024?",":"\n")}}' /tmp/sumb.txt /tmp/stream_part.txt > /tmp/sumb.new
    mv /tmp/sumb.new /tmp/sumb.txt
  done
  # 关键修复: 129行×1024值 → 合并成1行×132096值 (129类连成一行)
  gawk -F',' 'BEGIN{first=1} {for(i=1;i<=NF;i++){if(first && i==1) first=0; else printf ","; printf "%s", $i}} END{print ""}' /tmp/sumb.txt >> "$OUT"
done

echo "=== 合并完成 $(date '+%H:%M') ==="
echo "行数: $(wc -l < "$OUT") (应=42)"
echo "首行值数: $(head -1 "$OUT" | awk -F',' '{print NF}') (应=132096)"
echo "末行值数: $(tail -1 "$OUT" | awk -F',' '{print NF}') (b41应=27648)"
echo "非零值: $(gawk -F',' '{for(i=1;i<=NF;i++) if($i!=0) n++} END{print n+0}' "$OUT")"
echo "总值: $(gawk -F',' '{n+=NF} END{print n}' "$OUT")"
rm -f /tmp/sumb.txt /tmp/sumb.new /tmp/stream_part.txt /tmp/zero129.txt
