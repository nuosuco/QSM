#!/bin/bash
# QNT价差监控 - 有超阈值机会立即通知

LAST_SPREAD=$(cat /tmp/qnt_last_spread 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)

# 检查价差
SPREAD_DATA=$(python3 -c "
import os, ccxt
htx = ccxt.htx({'apiKey': os.getenv('HTX_API_KEY',''), 'secret': os.getenv('HTX_API_SECRET',''), 'enableRateLimit': True})
max_sp = 0
for sym in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']:
    s = htx.fetch_ticker(sym)
    p = htx.fetch_ticker(sym.split('/')[0]+'/USDT:USDT')
    sp = abs((p['bid']+p['ask'])/2 - (s['bid']+s['ask'])/2) / ((s['bid']+s['ask'])/2) * 100
    if sp > max_sp:
        max_sp = sp
print(f'{max_sp:.4f}')
" 2>/dev/null)

if [ -z "$SPREAD_DATA" ]; then
    exit 0
fi

# 检查是否超过阈值
if python3 -c "exit(0 if $SPREAD_DATA > 0.17 else 1)" 2>/dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔥 价差超阈值: ${SPREAD_DATA}%" >> /root/SOM/qnt/qnt_alert.log
    # 发送通知
    openclaw message send --target "qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447" --message "🔥 QNT价差机会！当前价差${SPREAD_DATA}% > 阈值0.17%，系统正在检查执行..." 2>/dev/null
else
    echo "$CURRENT_TIME:$SPREAD_DATA" > /tmp/qnt_last_spread
fi
