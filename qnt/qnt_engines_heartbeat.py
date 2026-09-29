"""QNT引擎心跳 - 写心跳文件，供 qnt_heartbeat.py / qnt_patrol.py 检查引擎是否存活

引擎端(adaptive_system)写，cron 端只读。2026-09-13 新增。
用法: python3 qnt_engines_heartbeat.py
"""
import os, time, json

HEARTBEAT_FILE = "/root/SOM/qnt/data/heartbeat.json"

def main():
    os.makedirs(os.path.dirname(HEARTBEAT_FILE), exist_ok=True)
    with open(HEARTBEAT_FILE, "w") as f:
        json.dump({"timestamp": time.time(), "pid": os.getpid(), "status": "alive"}, f)

if __name__ == "__main__":
    main()
