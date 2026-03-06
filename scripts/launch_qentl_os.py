#!/usr/bin/env python3
"""
QEntL量子操作系统启动器
Launch QEntL Quantum Operating System
"""

import os
import sys
from pathlib import Path

def main():
    """启动QEntL量子操作系统"""
    print("🌟 QEntL量子操作系统启动器")
    print("=" * 60)
    print("🧠 五大量子模型: QSM, SOM, WeQ, Ref, QEntL")
    print("🌍 三语支持: 中文, English, 滇川黔贵通用彝文")
    print("⚡ 量子特性: 叠加态, 纠缠, 24小时学习")
    print("=" * 60)
    
    # 启动量子执行引擎
    engine_path = Path(__file__).parent / "QEntL" / "System" / "quantum_execution_engine.py"
    
    if engine_path.exists():
        print(f"🚀 启动量子执行引擎: {engine_path}")
        os.system(f"python {engine_path}")
    else:
        print("❌ 量子执行引擎未找到，请先运行训练系统")
        print("💡 运行命令: python QEntL/unified_training_system.py")

if __name__ == "__main__":
    main()
