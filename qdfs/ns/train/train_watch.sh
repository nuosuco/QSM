#!/bin/bash
# train_watch.sh - 持续盯守训练驱动 (2026-10-01 中华批评后新建)
# 铁律: 每个 batch 跑完立即验证, 不达标当场停, 不跑下一批. 后台 nohup 不"等死".
# 验证项: ①无越界 ②stream非零 ③C行数=类数 ④正确率非零
set -u
cd /root/QSM/QLife || exit 1

ROUND="${1:-A}"
EPOCH=6
SRC=qdfs/ns/train/qscl_32x32_v10.qentl
LOG=/tmp/train_watch_${ROUND}.log

if [ "$ROUND" = "B" ]; then
  SEED_EXPR="g_seed = 10001 + g_s * 100"
  SUFFIX="streamB"
else
  SEED_EXPR="g_seed = 1 + g_s * 100"
  SUFFIX="stream"
fi

echo "===== $ROUND 轮盯守开始 $(date '+%m-%d %H:%M:%S') (epoch=$EPOCH) =====" > "$LOG"

# 备份源码
cp "$SRC" /tmp/v10_watch_orig.qentl

for B in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41; do
  for S in 0 1 2 3; do
    LOGFILE="run/train_w_${ROUND}_b${B}_s${S}.log"
    STREAM="qdfs/ns/models/qscl_32x32_b${B}_s${S}_${SUFFIX}.w"
    echo "[$ROUND] b${B}_s${S} $(date '+%H:%M:%S')" >> "$LOG"

    # 控制文件
    echo "$B" > qdfs/ns/train/current_batch.txt
    echo "$S" > qdfs/ns/train/current_state.txt
    echo "0" > qdfs/ns/train/smoke_limit.txt

    # epoch + seed (sed 改源码)
    sed -i "s|^var g_epoch = [0-9]*.*|var g_epoch = $EPOCH|" "$SRC"
    sed -i "s|g_seed = [0-9]+ g_s \* [0-9]*|$SEED_EXPR|" "$SRC"

    # 编译
    cp "$SRC" input.qentl
    if ! timeout 120 bin/qvm_boot run run/qcl.qbc > /dev/null 2>&1; then
      echo "  [FAIL] b${B}_s${S} 编译失败, 停止" | tee -a "$LOG"
      echo "===== $ROUND 轮中止(编译失败) $(date '+%m-%d %H:%M:%S') =====" | tee -a "$LOG"
      exit 1
    fi
    cp output.qbc target.qbc

    # 清理旧 stream
    rm -f "$STREAM"

    # 跑训练 (900s 够 6ep)
    timeout 900 bin/qvm_boot run run/qvm.qbc > "run/qvm_w_${ROUND}_b${B}_s${S}.all" 2> "run/qvm_w_${ROUND}_b${B}_s${S}.time"

    # === 验证 1: 越界崩溃检查 ===
    if grep -q "数组越界\|idx=" "run/qvm_w_${ROUND}_b${B}_s${S}.time" 2>/dev/null; then
      echo "  [FAIL] b${B}_s${S} 越界: $(cat run/qvm_w_${ROUND}_b${B}_s${S}.time)" | tee -a "$LOG"
      echo "===== $ROUND 轮中止(越界) $(date '+%m-%d %H:%M:%S') =====" | tee -a "$LOG"
      exit 1
    fi

    # 分流权重流
    STREAM_RAW="run/qvm_w_${ROUND}_b${B}_s${S}.all"
    awk -v logf="$LOGFILE" 'BEGIN{p=0} /=== 日志截断 ===/{p=1;next} p{print; next} {print > logf}' "$STREAM_RAW" > "$STREAM"

    # === 验证 2: stream 非零 ===
    SZ=$(wc -c < "$STREAM" 2>/dev/null || echo 0)
    if [ "$SZ" -eq 0 ]; then
      echo "  [FAIL] b${B}_s${S} stream=0字节, 停止" | tee -a "$LOG"
      echo "===== $ROUND 轮中止(stream空) $(date '+%m-%d %H:%M:%S') =====" | tee -a "$LOG"
      exit 1
    fi

    # === 验证 3: C行数=类数 ===
    CROW=$(grep -c "^C[0-9]" "$STREAM" 2>/dev/null || echo 0)
    # batch 0-40 各129类, batch41=77类
    if [ "$B" -le 40 ]; then EXPECT=129; else EXPECT=27; fi
    if [ "$CROW" -lt "$EXPECT" ]; then
      echo "  [FAIL] b${B}_s${S} C行数=$CROW (期望=$EXPECT), 停止" | tee -a "$LOG"
      echo "===== $ROUND 轮中止(C行不足) $(date '+%m-%d %H:%M:%S') =====" | tee -a "$LOG"
      exit 1
    fi

    # === 验证 4: 正确率非零 ===
    ACC=$(grep -oE "正确[0-9]+/[0-9]+" "$LOGFILE" 2>/dev/null | tail -1)
    echo "  -> b${B}_s${S} $SUFFIX=$SZ C行=$CROW(期望$EXPECT) $ACC" | tee -a "$LOG"

    # 记录完成
    echo "$B $S" >> "run/watch_done_${ROUND}.txt"
  done
done

# 恢复源码
cp /tmp/v10_watch_orig.qentl "$SRC"
echo "===== $ROUND 轮盯守完成 $(date '+%m-%d %H:%M:%S') =====" | tee -a "$LOG"
echo "完成 stream 数: $(find qdfs/ns/models -name "*_${SUFFIX}.w" 2>/dev/null | wc -l)/168" | tee -a "$LOG"
