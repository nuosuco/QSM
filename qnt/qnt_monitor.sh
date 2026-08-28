#!/bin/bash
# QNT监控脚本 - 定期检查和推送

LOGFILE="/root/SOM/qnt/qnt_monitor.log"
ALERT_LOG="/root/SOM/qnt/qnt_alert.log"
THRESHOLD=0.17

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

check_spread() {
    python3 -c "
import os, ccxt
htx = ccxt.htx({'apiKey': os.getenv('HTX_API_KEY',''), 'secret': os.getenv('HTX_API_SECRET',''), 'enableRateLimit': True})
max_sp = 0
for sym in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']:
    s = htx.fetch_ticker(sym)
    p = htx.fetch_ticker(sym.split('/')[0]+'/USDT:USDT')
    sp = abs((p['bid']+p['ask'])/2 - (s['bid']+s['ask'])/2) / ((s['bid']+s['ask'])/2) * 100
    if sp > max_sp:
        max_sp = sp
        best_sym = sym
print(f'{best_sym}: {max_sp:.4f}')
" 2>/dev/null
}

# 检查价差
SPREAD=$(check_spread)
if [ -n "$SPREAD" ]; then
    log "价差: $SPREAD"
    
    # 检查是否超阈值
    if python3 -c "exit(0 if $SPREAD > $THRESHOLD else 1)" 2>/dev/null; then
        log "🔥 发现机会！$SPREAD > 阈值$THRESHOLD%"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔥 QNT价差机会！$SPREAD" >> "$ALERT_LOG"
        
        # 发送通知
        openclaw message send --target "qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447" \
            --message "🔥 QNT价差机会！$(echo $SPREAD | cut -d: -f1)价差$(echo $SPREAD | cut -d: -f2) > 阈值0.17%，系统正在处理..." 2>/dev/null
    fi
fi
