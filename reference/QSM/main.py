#!/usr/bin/env python3
"""
QSM项目主入口文件

在项目启动时自动初始化各个子系统，包括文件监控服务
"""
import os
import sys
import argparse
import time
import logging
from typing import Dict, Any

# 配置日志
<<<<<<< HEAD
def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    
    # 确保日志目录存在
    os.makedirs('QSM/logs', exist_ok=True)
    
    # 设置日志格式和处理器
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('QSM/logs/main.log', mode='a'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('QSM')

# 全局日志对象将在parse_args后初始化
logger = None
=======
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('QSM/logs/main.log', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('QSM')

# 创建必要的目录
os.makedirs('QSM/logs', exist_ok=True)

>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea

def init_subsystems(config: Dict[str, Any] = None):
    """
    初始化QSM的各个子系统
    
    Args:
        config: 配置参数
    """
    logger.info("开始初始化QSM子系统...")
    
    # 初始化Ref文件完整性监控系统
    try:
        # 导入Ref启动钩子
<<<<<<< HEAD
        logger.debug("尝试导入Ref文件监控系统...")
        from Ref.auto_monitor.startup_hook import install_startup_hook
        
        # 安装启动钩子，启动文件监控服务
        logger.debug("尝试安装Ref启动钩子...")
=======
        from Ref.auto_monitor.startup_hook import install_startup_hook
        
        # 安装启动钩子，启动文件监控服务
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
        install_startup_hook()
        logger.info("Ref文件监控系统已初始化")
    except ImportError as e:
        logger.error(f"初始化Ref文件监控系统失败: {str(e)}")
<<<<<<< HEAD
        logger.debug(f"导入路径: {sys.path}")
    except Exception as e:
        logger.error(f"启动Ref文件监控系统时发生错误: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
=======
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    
    # 初始化其他子系统
    # TODO: 初始化SOM、WeQ等子系统
    
    logger.info("QSM子系统初始化完成")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="QSM项目主入口")
    
    parser.add_argument(
        "--config", "-c",
        dest="config_file",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--no-monitor",
        dest="disable_monitor",
        action="store_true",
        help="禁用文件监控系统"
    )
    
<<<<<<< HEAD
    parser.add_argument(
        "--port", "-p",
        dest="port",
        type=int,
        default=5000,
        help="API服务器端口"
    )
    
    parser.add_argument(
        "--daemon",
        dest="daemon_mode",
        action="store_true",
        help="以守护进程模式运行"
    )
    
    parser.add_argument(
        "--standalone",
        dest="standalone_mode",
        action="store_true",
        help="以独立模式运行（不依赖其他服务）"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        dest="verbose",
        action="store_true",
        help="启用详细日志输出"
    )
    
=======
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    return parser.parse_args()


def load_config(config_file: str = None) -> Dict[str, Any]:
    """
    加载配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    # 默认配置
    config = {
        "enable_file_monitor": True,
        "subsystems": ["Ref", "SOM", "WeQ"]
    }
    
    # TODO: 从配置文件加载更多配置
    
    return config


def main():
    """主函数"""
<<<<<<< HEAD
    global logger
=======
    print("欢迎使用QSM系统")
    print("正在启动...")
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    
    # 解析命令行参数
    args = parse_args()
    
<<<<<<< HEAD
    # 初始化日志
    logger = setup_logging(args.verbose)
    
    logger.info("欢迎使用QSM系统")
    logger.info(f"命令行参数: {args}")
    logger.info("正在启动...")
    
    # 打印系统信息
    logger.debug(f"Python版本: {sys.version}")
    logger.debug(f"工作目录: {os.getcwd()}")
    logger.debug(f"Python路径: {sys.executable}")
    logger.debug(f"导入路径: {sys.path}")
    
=======
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    # 加载配置
    config = load_config(args.config_file)
    
    # 如果指定了禁用监控，则更新配置
    if args.disable_monitor:
        config["enable_file_monitor"] = False
    
    # 初始化子系统
    if config["enable_file_monitor"]:
        init_subsystems(config)
    else:
        logger.info("文件监控系统已禁用")
    
    # 在这里添加项目的主要逻辑
    print("QSM系统已启动，按Ctrl+C退出")
    
    try:
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止QSM系统...")
        logger.info("QSM系统正常关闭")
        print("QSM系统已停止")


if __name__ == "__main__":
    main() 

"""
<<<<<<< HEAD
=======
"""
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
量子基因编码: QE-MAI-8CBE2EE010A8
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
<<<<<<< HEAD
"""

# 开发团队：中华 ZhoHo ，Claude 
=======
""""""

// 开发团队：中华 ZhoHo ，Claude 
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
