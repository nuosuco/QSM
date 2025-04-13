#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # """
量子基因编码: QE-STA-ADCB741974BF
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
"""
"""
启动 WeQ YOLO 模式 - 快速学习模式
特点：
1. 更快的训练间隔
2. 更激进的学习策略
3. 并行训练多个模型
"""

import os
import sys
import logging
from background_training import BackgroundTrainer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/yolo_mode.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WeQ-YOLO模式")

def start_yolo_mode():
    """启动 YOLO 模式"""
    logger.info("=" * 60)
    logger.info("启动 WeQ YOLO 模式 - 快速学习系统")
    logger.info("=" * 60)
    
    # 创建训练器实例
    trainer = BackgroundTrainer()
    
    # 设置 YOLO 模式参数
    trainer.claude_training_interval = 15  # 15分钟
    trainer.crawler_training_interval = 60  # 1小时
    trainer.qsm_training_interval = 30  # 30分钟
    
    # 确保所有学习功能开启
    trainer.enable_claude_training = True
    trainer.enable_crawler_training = True
    trainer.enable_qsm_training = True
    
    # 启动后台训练
    trainer.start_background_training()
    
    logger.info("YOLO 模式已启动")
    logger.info("系统将在后台快速学习")
    logger.info("输入 'q' 或 'quit' 退出训练")

if __name__ == "__main__":
    start_yolo_mode() 