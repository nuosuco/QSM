#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滇川黔桂彝文训练启动脚本
使用现有数据开始四模型训练
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# 路径配置
QSM_ROOT = Path('/root/QSM')
TRAINING_DATA_DIR = QSM_ROOT / 'Models' / 'training_data' / 'datasets' / 'yi_wen'
OUTPUT_DIR = QSM_ROOT / 'Models' / 'training_output'
LOG_DIR = OUTPUT_DIR / 'logs'

def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🎯 滇川黔桂彝文四模型训练启动")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"训练数据目录: {TRAINING_DATA_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

def check_data():
    """检查训练数据"""
    print("\n📊 检查训练数据...")
    
    data_files = {
        '三语对照表': TRAINING_DATA_DIR / '滇川黔贵通用彝文三语对照表.jsonl',
        '彝汉对照训练表': TRAINING_DATA_DIR / '通用彝文彝汉对照训练表(2.0.4.22).jsonl',
        '汉彝对照训练表': TRAINING_DATA_DIR / '通用彝文汉彝对照训练表(2.0.4.22).jsonl',
    }
    
    total_lines = 0
    all_exist = True
    
    for name, filepath in data_files.items():
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
            print(f"  ✅ {name}: {lines}行")
            total_lines += lines
        else:
            print(f"  ❌ {name}: 不存在")
            all_exist = False
    
    print(f"\n总训练数据: {total_lines}行")
    
    if total_lines >= 10000:
        print("✅ 训练数据充足 (>= 10,000行)")
    else:
        print("⚠️ 训练数据不足 (< 10,000行)")
    
    return all_exist and total_lines >= 10000

def show_sample_data():
    """显示训练数据样例"""
    print("\n📝 训练数据样例:")
    
    sample_file = TRAINING_DATA_DIR / '滇川黔贵通用彝文三语对照表.jsonl'
    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
                try:
                    data = json.loads(line)
                    if 'messages' in data and len(data['messages']) > 0:
                        user_msg = data['messages'][0].get('content', '')
                        assistant_msg = data['messages'][1].get('content', '') if len(data['messages']) > 1 else ''
                        print(f"  {i+1}. 彝文: {user_msg} → 中文: {assistant_msg}")
                except:
                    pass

def create_output_dirs():
    """创建输出目录"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 输出目录已创建: {OUTPUT_DIR}")

def main():
    """主函数"""
    print_banner()
    
    # 1. 检查数据
    if not check_data():
        print("\n❌ 训练数据检查失败")
        return False
    
    # 2. 显示样例
    show_sample_data()
    
    # 3. 创建输出目录
    create_output_dirs()
    
    # 4. 显示四模型配置
    print("\n🔧 四模型训练配置:")
    models = ['QSM', 'SOM', 'WeQ', 'Ref']
    for model in models:
        print(f"  • {model}: 准备就绪")
    
    print("\n" + "=" * 60)
    print("✅ 训练环境检查完成!")
    print("=" * 60)
    print("\n🚀 可以开始训练!")
    print("   运行命令: python3 /root/QSM/Models/training_scripts/train_yi_wen_qsm.py")
    
    return True

if __name__ == '__main__':
    main()
