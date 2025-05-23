#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SOM服务启动脚本
启动所有自组织映射服务，包括API服务、训练服务和推理服务
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# 设置路径
script_dir = os.path.dirname(os.path.abspath(__file__))
som_dir = os.path.dirname(os.path.dirname(script_dir))
root_dir = os.path.dirname(som_dir)
os.chdir(root_dir)  # 将工作目录设置为项目根目录

# 确保存在日志目录
os.makedirs('.logs', exist_ok=True)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('.logs', 'som_service_starter.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SOM服务启动器')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="SOM服务启动器")
    parser.add_argument("--all", action="store_true", help="启动所有服务")
    parser.add_argument("--train", action="store_true", help="启动SOM训练服务")
    parser.add_argument("--inference", action="store_true", help="启动SOM推理服务")
    parser.add_argument("--market", action="store_true", help="启动量子市场服务")
    parser.add_argument("--trade", action="store_true", help="启动量子交易服务")
    parser.add_argument("--wallet", action="store_true", help="启动量子钱包服务")
    parser.add_argument("--core", action="store_true", help="启动SOM核心服务")
    parser.add_argument("--port", type=int, default=5001, help="API服务端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    return parser.parse_args()

def start_background_service(script_path, service_name, args=""):
    """启动后台服务"""
    try:
        # 确保脚本路径存在
        if not os.path.exists(script_path):
            logger.error(f"服务脚本不存在: {script_path}")
            return False
            
        # 创建日志文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join('.logs', f"{service_name}_{timestamp}.log")
        err_file = os.path.join('.logs', f"{service_name}_{timestamp}.err")
        
        # 构建命令
        cmd = [sys.executable, script_path]
        if args:
            if isinstance(args, str):
                cmd.extend(args.split())
            else:
                cmd.extend(args)
            
        # 启动进程，重定向输出到日志文件
        with open(log_file, 'w', encoding='utf-8') as out_f, open(err_file, 'w', encoding='utf-8') as err_f:
            process = subprocess.Popen(
                cmd,
                stdout=out_f,
                stderr=err_f,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
        logger.info(f"成功启动服务: {service_name}, PID: {process.pid}, 日志: {log_file}")
        return True
        
    except Exception as e:
        logger.error(f"启动服务失败: {service_name}, 错误: {str(e)}")
        return False

def find_script(relative_paths):
    """查找脚本文件"""
    for path in relative_paths:
        full_path = os.path.join(som_dir, path)
        if os.path.exists(full_path):
            return full_path
    
    # 如果在SOM目录中找不到，尝试在根目录中查找
    for path in relative_paths:
        full_path = os.path.join(root_dir, path)
        if os.path.exists(full_path):
            return full_path
            
    return None

def start_som_core_service():
    """启动SOM核心服务"""
    logger.info("启动SOM核心服务...")
    
    # 查找核心服务脚本
    core_script_paths = ["core/som_core.py", "som_core.py"]
    core_script = find_script(core_script_paths)
    
    if not core_script:
        logger.error("未找到SOM核心服务脚本")
        return False
    
    # 构建参数
    core_args = ["--daemon"]
    
    # 启动服务
    return start_background_service(core_script, "SOM核心服务", core_args)

def start_som_api_service(args):
    """启动SOM API服务"""
    logger.info("启动SOM API服务...")
    
    # 查找API脚本 - 按照新的目录结构标准查找
    api_script_paths = [
        "api/som_api.py",
        "api/app.py", 
        "scripts/api/som_api.py",
        "scripts/api/app.py"
    ]
    api_script = find_script(api_script_paths)
    
    if not api_script:
        logger.error("未找到SOM API服务脚本")
        return False
    
    # 构建参数
    api_args = ["--port", str(args.port)]
    if args.debug:
        api_args.append("--debug")
    
    # 启动服务
    return start_background_service(api_script, "SOM API服务", api_args)

def start_som_train_service():
    """启动SOM训练服务"""
    logger.info("启动SOM训练服务...")
    
    # 查找训练服务脚本
    train_script_paths = [
        "train/som_train.py", 
        "som_train.py", 
        "scripts/train/train_service.py"
    ]
    train_script = find_script(train_script_paths)
    
    if not train_script:
        logger.error("未找到SOM训练服务脚本")
        return False
    
    # 构建参数
    train_args = ["--daemon", "--auto_save"]
    
    # 启动服务
    return start_background_service(train_script, "SOM训练服务", train_args)

def start_som_inference_service():
    """启动SOM推理服务"""
    logger.info("启动SOM推理服务...")
    
    # 查找推理服务脚本
    inference_script_paths = [
        "inference/som_inference.py", 
        "som_inference.py", 
        "scripts/inference/inference_service.py"
    ]
    inference_script = find_script(inference_script_paths)
    
    if not inference_script:
        logger.error("未找到SOM推理服务脚本")
        return False
    
    # 构建参数
    inference_args = ["--daemon", "--batch_size", "32", "--model", "latest"]
    
    # 启动服务
    return start_background_service(inference_script, "SOM推理服务", inference_args)

def start_som_market_service():
    """启动量子市场服务"""
    logger.info("启动量子市场服务...")
    
    # 查找市场服务脚本
    market_script_paths = [
        "market/quantum_ecommerce.py",
        "quantum_ecommerce.py",
        "ecommerce/som_market.py",
        "scripts/market/market_service.py"
    ]
    market_script = find_script(market_script_paths)
    
    if not market_script:
        logger.error("未找到量子市场服务脚本")
        return False
    
    # 构建参数
    market_args = ["--daemon", "--auto_update"]
    
    # 启动服务
    return start_background_service(market_script, "量子市场服务", market_args)

def start_som_trade_service():
    """启动量子交易服务"""
    logger.info("启动量子交易服务...")
    
    # 查找交易服务脚本
    trade_script_paths = [
        "trade/som_coin_system.py",
        "som_coin_system.py",
        "coin/som_trade.py",
        "scripts/trade/trade_service.py"
    ]
    trade_script = find_script(trade_script_paths)
    
    if not trade_script:
        logger.error("未找到量子交易服务脚本")
        return False
    
    # 构建参数
    trade_args = ["--daemon", "--secure"]
    
    # 启动服务
    return start_background_service(trade_script, "量子交易服务", trade_args)

def start_som_wallet_service():
    """启动量子钱包服务"""
    logger.info("启动量子钱包服务...")
    
    # 查找钱包服务脚本
    wallet_script_paths = [
        "wallet/quantum_wallet.py",
        "quantum_wallet.py",
        "scripts/wallet/wallet_service.py"
    ]
    wallet_script = find_script(wallet_script_paths)
    
    if not wallet_script:
        logger.error("未找到量子钱包服务脚本")
        return False
    
    # 构建参数
    wallet_args = ["--daemon"]
    
    # 启动服务
    return start_background_service(wallet_script, "量子钱包服务", wallet_args)

def main():
    """主函数"""
    args = parse_args()
    
    # 服务计数器
    services_started = 0
    
    # 判断是否启动所有服务
    start_all = args.all or not any([
        args.train, args.inference, args.market, 
        args.trade, args.wallet, args.core
    ])
    
    # 启动SOM核心服务
    if args.core or start_all:
        if start_som_core_service():
            services_started += 1
            time.sleep(2)  # 等待核心服务初始化
    
    # 启动训练服务
    if args.train or start_all:
        if start_som_train_service():
            services_started += 1
    
    # 启动推理服务
    if args.inference or start_all:
        if start_som_inference_service():
            services_started += 1
    
    # 启动市场服务
    if args.market or start_all:
        if start_som_market_service():
            services_started += 1
    
    # 启动交易服务
    if args.trade or start_all:
        if start_som_trade_service():
            services_started += 1
    
    # 启动钱包服务
    if args.wallet or start_all:
        if start_som_wallet_service():
            services_started += 1
    
    logger.info(f"启动服务完成, 总共启动 {services_started} 个服务")
    return services_started > 0

if __name__ == "__main__":
    main()

"""
量子基因编码: QE-SRV-SOM-E5F4G3H2
纠缠状态: 活跃
纠缠对象: ['SOM/core/som_core.py', 'SOM/train/som_train.py', 'SOM/inference/som_inference.py', 'SOM/market/quantum_ecommerce.py', 'SOM/trade/som_coin_system.py', 'SOM/wallet/quantum_wallet.py']
纠缠强度: 0.98
"""

# 开发团队：中华 ZhoHo，Claude 