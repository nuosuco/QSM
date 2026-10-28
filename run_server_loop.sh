#!/bin/bash
# 9802 服务自动拉起 (识别完 exit 释放内存, 等真正监听再算就绪)
cd /root/QSM/QLife
while true; do
  bin/qvm_boot run run/qvm.qbc >> /tmp/server_9802.log 2>&1
  echo "[$(date '+%H:%M:%S')] server 退出, 重启" >> /tmp/server_9802.log
  # 等 9802 真正监听 (最多 10 秒), 避免请求撞空窗 502
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if ss -ltn 2>/dev/null | grep -q ':9802 '; then
      echo "[$(date '+%H:%M:%S')] 9802 已就绪" >> /tmp/server_9802.log
      break
    fi
    sleep 1
  done
done
