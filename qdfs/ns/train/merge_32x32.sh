#!/bin/sh
# ============================================================================
# merge_32x32.sh - QSCL 32x32 权重坍缩合并器 (纯 awk/shell, 无 Python/QVM)
#
# 规格 (qscl_32x32_v7b.qentl 头部注释):
#   每态独立:  qscl_32x32_b{batch}_s{state}.w    state=0..3
#   坍缩合并:  qscl_32x32_b{batch}.w
#   元素数:    515类 x 1024像素 = 527360
#   坍缩定义:  v7b merge_state_file() = get_w(idx) + val  -> 4态直接累加, 不归一
#
# 兼容两种分片形态 (v7b 头部命名 vs 实际 save_state_weights 产出):
#   A) 单文件:   qscl_32x32_b{b}_s{s}.w                 527360 逗号值
#   B) 515分片:  qscl_32x32_b{b}_s{s}_c{c}.w  c=0..514  各 1024 逗号值
# 形态 A 优先; 缺失时自动按形态 B 收集。
#
# 用法:
#   sh merge_32x32.sh              # 合并 batch0..7
#   sh merge_32x32.sh 0 3          # 只合并 batch0 和 batch3
#   sh merge_32x32.sh --check 0    # 只校验, 不写输出
#   DIR=/path to/sh merge_32x32.sh 0   # 覆盖权重目录
# ============================================================================
set -eu

DIR="${DIR:-/root/QSM/QLife/qdfs/ns/models}"
NCLASS=${NCLASS:-515}
PIXEL=${PIXEL:-1024}
NELEM=$((NCLASS * PIXEL))          # 527360
STATES=${STATES:-4}

CHECK=0
ARGS=""
for a in "$@"; do
    case "$a" in
        --check) CHECK=1 ;;
        *)       ARGS="$ARGS $a" ;;
    esac
done
[ -n "$ARGS" ] || ARGS="0 1 2 3 4 5 6 7"

norm_one_state() {
    # $1=state 目录前缀, 输出: 该态全部元素, 每行一个值, 无空行
    b=$1; s=$2; base="$DIR/qscl_32x32_b${b}_s${s}"
    if [ -f "${base}.w" ]; then
        cat "${base}.w"
    else
        for c in $(seq 0 $((NCLASS - 1))); do
            f="${base}_c${c}.w"
            [ -f "$f" ] || { echo "ERROR 缺分片: $f" >&2; return 1; }
            cat "$f"
        done
    fi
}

merge_batch() {
    b=$1
    base="$DIR/qscl_32x32_b$b"
    out="${base}.w"
    tmp="${base}.w.tmp.$$"
    norm="$tmp.norm.$$"
    err=0

    echo "--- batch$b: 4态坍缩 (527360 元素 x $STATES 态) ---"

    for s in $(seq 0 $((STATES - 1))); do
        norm_one_state "$b" "$s" > "${norm}.${s}.raw" || err=1
        # 逗号值 -> 每行一值 (跳过注释行/空行)
        awk -F, '{gsub(/\r/,""); if($0 ~ /^[ \t]*#/) next; for(i=1;i<=NF;i++){gsub(/[ \t]/,"",$i); if($i!=""){printf "%s\n",$i}}}' \
            "${norm}.${s}.raw" > "${norm}.${s}" || err=1
        n=$(awk 'END{print NR+0}' "${norm}.${s}")
        if [ "$n" -eq 0 ]; then
            echo "ERROR batch$b 态$s 无可读数值 (文件缺失或空)" >&2
            err=1
        elif [ "$n" -ne "$NELEM" ]; then
            echo "ERROR batch$b 态$s 元素数=$n 期望=$NELEM" >&2
            err=1
        else
            echo "  态$s 读入 $n 元素 OK"
        fi
    done

    if [ "$err" -ne 0 ]; then
        rm -f ${norm}.0 ${norm}.1 ${norm}.2 ${norm}.3 ${norm}.*.raw 2>/dev/null || true
        return 1
    fi

    if [ "$CHECK" -eq 1 ]; then
        rm -f ${norm}.0 ${norm}.1 ${norm}.2 ${norm}.3 ${norm}.*.raw 2>/dev/null || true
        echo "  --check: 4态元素数校验通过 (未写输出)"
        return 0
    fi

    if [ "$err" -eq 0 ]; then
        # 按位置直接累加 (v7b 坍缩定义: get_w(idx)+val, 不归一)
        i=0
        FILES=""
        while [ "$i" -lt "$STATES" ]; do
            FILES="$FILES ${norm}.${i}"
            i=$((i + 1))
        done
        awk -v n="$NELEM" -v ns="$STATES" '
            { acc[FNR] += $1 }
            END {
                if (FNR != n) { printf "ERROR 输出元素数=%d 期望=%d\n", FNR, n > "/dev/stderr"; exit 1 }
                for (i = 1; i <= n; i++) printf "%d\n", acc[i]
            }
        ' $FILES \
            | paste -sd, - > "$tmp" || { echo "ERROR 合并失败" >&2; rm -f "$tmp" ${norm}.* ${norm}.*.raw; return 1; }

        # 输出校验: 元素数 + 首尾值
        got=$(awk -F, 'END{print NF}' "$tmp")
        if [ "$got" -ne "$NELEM" ]; then
            echo "ERROR 输出 $out 元素数=$got 期望=$NELEM" >&2
            rm -f "$tmp" ${norm}.* ${norm}.*.raw; return 1
        fi
        mv "$tmp" "$out"
        rm -f ${norm}.* ${norm}.*.raw
        echo "  写出 $out ($got 元素, $STATES 态累加)"
        echo "  首8: $(cut -d, -f1-8 "$out")"
        echo "  末8: $(awk -F, '{n=NF; for(i=n-7;i<=n;i++) printf "%s%s", (i>n-7?",":""), $i; print ""}' "$out")"
    else
        rm -f "$tmp" ${norm}.* ${norm}.*.raw
        return 1
    fi
}

RC=0
for b in $ARGS; do
    merge_batch "$b" || RC=1
done
echo ""
if [ "$RC" -eq 0 ]; then
    echo "=== 坍缩合并完成 (输出: $DIR/qscl_32x32_b{0..7}.w) ==="
else
    echo "=== 坍缩合并存在失败 ===" >&2
fi
exit "$RC"
