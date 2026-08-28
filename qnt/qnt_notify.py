#!/usr/bin/env python3
"""QNT交易通知 - 主动发送消息"""
import subprocess
import sys

def send_message(msg):
    """通过message工具发送消息"""
    # 使用openclaw命令行发送
    result = subprocess.run(
        ['openclaw', 'message', 'send', '--target', 'qqbot:c2c:861B1B2CC9C89FC4A3E0325F10407447', '--message', msg],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ 消息已发送")
    else:
        print(f"❌ 发送失败: {result.stderr}")
    return result.returncode == 0

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "QNT系统通知"
    send_message(msg)
