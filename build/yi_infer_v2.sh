#!/bin/bash
# yi_infer_v2.sh — 真·4态叠加态并行推理(QVM层并行, bash仅编排+投票)
# 4个QCL处理器各自加载1态权重+数据, 并行前向点积argmax, bash汇聚真多数投票
d=$1; B=$(cd "$(dirname "$0")"/.. && pwd)
cd "$B"
b=$((d/515)); r=$((d%515)); ds=$((r*64+1)); de=$((r*64+64))

# 读取该字64像素(文本bin: 每像素一行 "0" 或 "1")
sed -n "${ds},${de}p" qdfs/ns/data/yi_flat_b${b}.bin > /tmp/yi_data.txt

BIN=$(ls bin/qvm_boot 2>/dev/null)

# 生成并编译4个QCL处理器(各1态)
for s in 0 1 2 3; do
  WPATH=$B/qdfs/ns/models/qscl_b${b}_s${s}.w
  cat > /tmp/yh${s}.qentl <<QEOF
var g_c = 515
var g_W[32960]
var g_D[64]
def main():
    var raw = file_read("/tmp/yi_data.txt")
    var lines = str_split(raw, "\n")
    var i = 0
    while (i < 64):
        g_D[i] = str_to_int(lines[i])
        i = i + 1
    end
    raw = file_read("${WPATH}")
    lines = str_split(raw, "\n")
    i = 0
    while (i < 32960):
        g_W[i] = str_to_int(lines[i])
        i = i + 1
    end
    var best = 0
    var bi = 0
    var si = 0
    while (si < 515):
        var lg = 0
        var sj = 0
        var wbase = si * 64
        while (sj < 64):
            lg = lg + g_W[wbase + sj] * g_D[sj]
            sj = sj + 1
        end
        if (lg > best):
            best = lg
            bi = si
        end
        si = si + 1
    end
    exec("printf '%d' ${bi} > /tmp/yi_res${s}.txt")
end
main()
QEOF
  $BIN compile /tmp/yh${s}.qentl /tmp/yh${s}.qbc 2>/dev/null
done

# 4态真并行(QVM后台 + wait 汇聚)
for s in 0 1 2 3; do
  $BIN run /tmp/yh${s}.qbc 2>/dev/null &
done
wait

v0=$(cat /tmp/yi_res0.txt 2>/dev/null); [ -z "$v0" ] && v0=-1
v1=$(cat /tmp/yi_res1.txt 2>/dev/null); [ -z "$v1" ] && v1=-1
v2=$(cat /tmp/yi_res2.txt 2>/dev/null); [ -z "$v2" ] && v2=-1
v3=$(cat /tmp/yi_res3.txt 2>/dev/null); [ -z "$v3" ] && v3=-1

# 真多数投票(叠加态坍缩)
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