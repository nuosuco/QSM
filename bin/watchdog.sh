#!/bin/bash
# QEntL HTTP服务器看门狗脚本
# 如果服务器挂了，自动重启
SERVER_PORT=9802
SERVER_BIN="/root/QSM/bin/qcl_bootstrap"
SERVER_QBC="/root/QSM/build/server.qbc"
SERVER_LOG="/root/QSM/server.log"

# 检查端口是否在监听
if ! ss -tlnp | grep -q "$SERVER_PORT"; then
    echo "[$(date)] QEntL HTTP服务器离线，重启中..." >> "$SERVER_LOG"
    cd /root/QSM && nohup "$SERVER_BIN" run "$SERVER_QBC" >> "$SERVER_LOG" 2>&1 &
    echo "[$(date)] 启动 PID=$!" >> "$SERVER_LOG"
fi