#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动WeQ量子基因神经网络知识训练程序 - 24小时连续学习模式
支持：
1. Claude教学模式
2. 爬虫自学能力
3. 量子叠加态模型知识学习
4. 持续运行不间断学习
"""

import os
import sys
import logging
import time
import argparse
import threading
import schedule
from datetime import datetime, timedelta

# 确保可以导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)
sys.path.append(os.path.dirname(current_dir))

# 配置日志
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/weq_knowledge_training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("WeQ知识训练")

try:
    # 导入后台训练器
    from background_training import BackgroundTrainer
    logger.info("成功导入WeQ后台训练器")
except ImportError as e:
    logger.error(f"导入WeQ后台训练器失败: {str(e)}")
    # 尝试导入备用训练器
    try:
        from WeQ.knowledge.background_training import BackgroundTrainer
        logger.info("从备用路径成功导入WeQ后台训练器")
    except ImportError as e2:
        logger.error(f"从备用路径导入WeQ后台训练器也失败: {str(e2)}")
        sys.exit(1)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="WeQ 24小时连续学习启动器")
    parser.add_argument("--hours", type=int, default=24, help="运行小时数，默认24小时")
    parser.add_argument("--no-claude", action="store_true", help="禁用Claude教学模式")
    parser.add_argument("--no-crawler", action="store_true", help="禁用爬虫自学能力")
    parser.add_argument("--no-qsm", action="store_true", help="禁用量子叠加态模型学习")
    parser.add_argument("--model-path", type=str, default="models/weq_model_28qubit.json", 
                       help="模型路径，默认使用28量子比特模型")
    return parser.parse_args()

def start_continuous_learning(args):
    """启动连续学习过程"""
    
    logger.info("=" * 60)
    logger.info("启动WeQ量子基因神经网络 24小时连续学习系统")
    logger.info("=" * 60)
    
    # 记录开始时间
    start_time = time.time()
    end_time = start_time + (args.hours * 3600)
    
    logger.info(f"计划运行时间: {args.hours}小时 (至 {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')})")
    
    # 初始化后台训练器
    trainer = BackgroundTrainer(model_path=args.model_path)
    
    # 设置训练选项
    if args.no_claude:
        trainer.enable_claude_training = False
        logger.info("Claude教学模式已禁用")
    
    if args.no_crawler:
        trainer.enable_crawler_training = False
        logger.info("爬虫自学能力已禁用")
    
    if args.no_qsm:
        trainer.enable_qsm_training = False
        logger.info("量子叠加态模型学习已禁用")
    
    try:
        # 启动后台训练
        trainer.start_background_training()
        
        # 打印训练状态
        print("\n===== WeQ 24小时连续学习系统已启动 =====")
        print(f"计划运行时间: {args.hours}小时")
        print("学习模式:")
        print(f"  - Claude教学: {'已启用' if trainer.enable_claude_training else '已禁用'}")
        print(f"  - 爬虫自学: {'已启用' if trainer.enable_crawler_training else '已禁用'}")
        print(f"  - 量子模型学习: {'已启用' if trainer.enable_qsm_training else '已禁用'}")
        print("\n系统正在后台运行，可以查看日志了解详情...")
        
        # 等待结束时间
        try:
            while time.time() < end_time and trainer.is_running:
                remaining = end_time - time.time()
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                
                # 定期打印状态
                if remaining % 1800 < 10:  # 每30分钟打印一次
                    status = trainer.get_training_status()
                    logger.info(f"训练状态: {status['status']}, "
                               f"周期: {status['training_cycles']}, "
                               f"剩余时间: {hours}小时{minutes}分钟")
                
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("收到用户中断，准备停止训练...")
        
        # 停止训练
        trainer.stop_background_training()
        
        # 计算总训练时间
        total_time = time.time() - start_time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = int(total_time % 60)
        
        # 保存最终模型
        final_status = trainer.get_training_status()
        
        # 打印训练结果总结
        print("\n===== 训练完成 =====")
        print(f"总训练时间: {hours}小时{minutes}分钟{seconds}秒")
        print(f"总训练周期: {final_status['training_cycles']}")
        print(f"Claude教学周期: {final_status['claude_cycles']}")
        print(f"爬虫学习周期: {final_status['crawler_cycles']}")
        print(f"量子模型学习周期: {final_status['qsm_cycles']}")
        print(f"学习的主题数量: {len(final_status['topics_trained'])}")
        
        logger.info(f"知识训练成功完成! 总时间: {hours}小时{minutes}分钟{seconds}秒")
        logger.info(f"训练周期: {final_status['training_cycles']}")
        
    except Exception as e:
        logger.error(f"知识训练失败: {str(e)}", exc_info=True)
        print(f"\n错误: 知识训练失败 - {str(e)}")
        return False
    
    return True

def main():
    """主函数"""
    args = parse_arguments()
    success = start_continuous_learning(args)
    
    if success:
        print("\n✅ WeQ 24小时连续学习系统已成功完成!")
    else:
        print("\n❌ WeQ 24小时连续学习系统运行失败，详情请查看日志。")
    
    return success

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-STA-B778B30BC0D5
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
