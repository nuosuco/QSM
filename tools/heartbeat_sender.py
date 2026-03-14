#!/usr/bin/env python3
"""
QEntL项目心跳发送器
版本: 1.0.0
描述: 自动发送项目进度报告到QQBot
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

def get_project_progress():
    """获取项目进度信息"""
    progress = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phase": "运行时开发",
        "day": 1,
        "completed": [],
        "in_progress": [],
        "next_milestone": "编译器自举验证",
        "status": "正常"
    }
    
    # 检查运行时组件
    runtime_files = [
        "/root/QSM/runtime/src/memory.c",
        "/root/QSM/runtime/src/string.c", 
        "/root/QSM/runtime/src/array.c",
        "/root/QSM/runtime/src/value.c",
        "/root/QSM/runtime/src/logging.c",
        "/root/QSM/runtime/src/vm.c"
    ]
    
    completed = []
    for file in runtime_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            name = os.path.basename(file)
            completed.append(f"{name} ({size}字节)")
    
    progress["completed"] = completed
    
    # 检查编译状态
    if os.path.exists("/root/QSM/runtime/libqentl_runtime.a"):
        lib_size = os.path.getsize("/root/QSM/runtime/libqentl_runtime.a")
        progress["in_progress"] = [f"静态库编译完成 ({lib_size}字节)"]
    else:
        progress["in_progress"] = ["正在编译运行时库"]
    
    return progress

def format_progress_message(progress):
    """格式化进度消息"""
    lines = [
        f"⚛️ QEntL编译器进度报告 ({progress['timestamp']})",
        f"阶段: {progress['phase']} - 第{progress['day']}天",
        "",
        "✅ 已完成:"
    ]
    
    for item in progress["completed"]:
        lines.append(f"  • {item}")
    
    lines.append("")
    lines.append("⚡ 进行中:")
    for item in progress["in_progress"]:
        lines.append(f"  • {item}")
    
    lines.append("")
    lines.append(f"🎯 下一个里程碑: {progress['next_milestone']}")
    lines.append(f"📊 状态: {progress['status']}")
    lines.append("")
    lines.append("量子革命工具链开发稳步推进中！✨")
    
    return "\n".join(lines)

def send_to_qqbot(message):
    """发送消息到QQBot"""
    try:
        # 使用moltbot CLI发送消息
        cmd = [
            "moltbot", "sessions", "send",
            "--sessionKey", "agent:main:main",
            message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 消息发送成功")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 异常: {e}")
        return False

def main():
    """主函数"""
    print("🔧 QEntL心跳发送器启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 获取进度
    progress = get_project_progress()
    
    # 格式化消息
    message = format_progress_message(progress)
    print("📋 进度信息:")
    print(message)
    print("=" * 50)
    
    # 发送消息
    print("📤 发送消息到QQBot...")
    if send_to_qqbot(message):
        print("✅ 心跳发送完成")
    else:
        print("❌ 心跳发送失败，将使用备用方案")
        # 备用方案：写入文件，下次会话时读取
        with open("/tmp/qentl_heartbeat_last.txt", "w", encoding="utf-8") as f:
            f.write(message)
        print("📝 已写入备份文件: /tmp/qentl_heartbeat_last.txt")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())