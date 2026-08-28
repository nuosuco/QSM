#!/usr/bin/env python3
"""QNT心跳检测 - 检查引擎进程是否存活，死掉则告警"""
import os
import time
import subprocess
import json
from datetime import datetime

HEARTBEAT_DIR = "/root/SOM/qnt/data"
HEARTBEAT_FILE = os.path.join(HEARTBEAT_DIR, "heartbeat.json")
CHECK_INTERVAL = 300  # 每5分钟检查一次

def write_heartbeat():
    """写入心跳文件"""
    os.makedirs(HEARTBEAT_DIR, exist_ok=True)
    data = {
        "timestamp": time.time(),
        "pid": os.getpid(),
        "status": "alive"
    }
    with open(HEARTBEAT_FILE, 'w') as f:
        json.dump(data, f)

def check_heartbeat():
    """检查心跳，如果超过5分钟没有更新则发送告警"""
    if not os.path.exists(HEARTBEAT_FILE):
        print(f"[{datetime.now()}] ⚠️ 心跳文件不存在，引擎可能未启动")
        return
    
    with open(HEARTBEAT_FILE) as f:
        data = json.load(f)
    
    last_beat = data.get("timestamp", 0)
    age = time.time() - last_beat
    
    if age > 600:  # 10分钟
        print(f"[{datetime.now()}] 🚨 心跳超时 {age:.0f}秒，引擎可能已死亡")
        # 发送QQ通知
        subprocess.run([
            "openclaw", "message", "send",
            "--target", "qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447",
            "--message", f"🚨 QNT引擎心跳超时 {int(age/60)} 分钟，请立即检查！"
        ], capture_output=True)
    else:
        print(f"[{datetime.now()}] ✅ 心跳正常 ({age:.0f}秒前)")

if __name__ == "__main__":
    write_heartbeat()
    check_heartbeat()
