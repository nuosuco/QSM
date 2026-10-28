#!/bin/bash
# 训练盯守脚本: 每 30 分钟巡检一次, 异常立即报告
# 校验: 最新权重流非0 + 训练日志在推进 + 崩溃检测
set -u
cd /root/QSM/QLife
LOG=/tmp/train_5316_full.log
ALERT=/tmp/train_5316_alert.txt

# 读进度
DONE=$(grep -c '\[v6\]' "$LOG" 2>/dev/null || echo 0)
LAST=$(grep '\[v6\]' "$LOG" | tail -1 2>/dev/null)
STREAMS=$(find qdfs/ns/models -name 'variant_b*_s*_stream.w' -size +0c 2>/dev/null | wc -l)

# 读上一轮的进度 (用于判断是否停滞)
PREVFILE=/tmp/train_5316_last_done
PREV=$(cat "$PREVFILE" 2>/dev/null || echo 0)

# 崩溃检测: 日志尾部有越界/exit=1
CRASH=$(tail -5 "$LOG" 2>/dev/null | grep -c '越界\|exit=1\|error' || echo 0)

# 写入本次进度
echo "$DONE" > "$PREVFILE"

# 判断: 是否停滞 (连续 2 次巡检进度没变)
if [ "$DONE" -eq "$PREV" ] && [ -f /tmp/train_5316_stall_count ]; then
    STALL=$(cat /tmp/train_5316_stall_count)
    STALL=$((STALL+1))
    echo "$STALL" > /tmp/train_5316_stall_count
    if [ "$STALL" -ge 2 ]; then
        echo "⚠️ 训练停滞! 进度停在 $DONE/168 态, 连续 $STALL 次巡检没推进" >> "$ALERT"
        echo "最后一次: $LAST" >> "$ALERT"
        echo "权重流: $STREAMS/168" >> "$ALERT"
    fi
else
    rm -f /tmp/train_5316_stall_count
fi

# 崩溃报告
if [ "$CRASH" -gt 0 ]; then
    echo "🚨 训练崩溃! 日志尾部有越界/exit=1" >> "$ALERT"
    tail -5 "$LOG" >> "$ALERT"
    echo "" >> "$ALERT"
fi

# 全部完成
if [ "$DONE" -ge 168 ]; then
    echo "✅ 训练完成 168/168" >> "$ALERT"
fi

# 巡检记录
echo "巡检 $(date '+%H:%M'): 进度=$DONE/168 权重流=$STREAMS/168" >> /tmp/train_5316_patrol.log

# 有警报就通知
if [ -s "$ALERT" ]; then
    cat "$ALERT"
    rm -f "$ALERT"
fi
