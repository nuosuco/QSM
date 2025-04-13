#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ref API集成模块
用于将Ref API集成到QSM API
"""

import os
import sys
import logging
from typing import Dict, Any, Callable

# 配置日志记录器
logger = logging.getLogger("Ref-Integration")
if not logger.handlers:
    # 避免重复配置
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    try:
        # 确保日志目录存在
        os.makedirs("Ref/logs", exist_ok=True)
        file_handler = logging.FileHandler("Ref/logs/ref_api_integration.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"配置日志处理器时出错: {str(e)}")

# 导入Ref API模块
try:
    from Ref.api.ref_api import create_ref_namespace
    from Ref.ref_core import get_ref_core
    
    ref_api_available = True
except ImportError as e:
    logger.error(f"无法导入create_ref_namespace，请确保Ref API模块已正确安装")
    ref_api_available = False

def integrate_ref_api_to_qsm_api(api):
    """将Ref API集成到QSM API
    
    Args:
        api: QSM API实例
        
    Returns:
        集成成功则返回Ref API命名空间，否则返回None
    """
    if not ref_api_available:
        logger.error("Ref API模块不可用，无法集成到QSM API")
        return None
    
    try:
        logger.info("开始集成Ref API到QSM API...")
        
        # 创建Ref命名空间
        ref_ns = create_ref_namespace(api)
        
        logger.info("Ref API集成成功")
        return ref_ns
    except Exception as e:
        logger.error(f"集成Ref API到QSM API时出错: {str(e)}")
        return None

def add_ref_health_check(health_endpoint):
    """向QSM API的健康检查端点添加Ref健康状态
    
    Args:
        health_endpoint: 健康检查端点函数
        
    Returns:
        装饰后的健康检查端点函数
    """
    if not ref_api_available:
        logger.warning("Ref API模块不可用，健康检查端点不会包含Ref状态")
        return health_endpoint
    
    # 保存原始健康检查函数
    original_health_check = health_endpoint
    
    def health_check_with_ref():
        """添加了Ref状态的健康检查函数"""
        # 获取原始健康状态
        health_status = original_health_check()
        
        # 添加Ref状态
        try:
            ref_core = get_ref_core()
            ref_status = {
                "status": "healthy",
                "version": ref_core.version,
                "quantum_gene": ref_core.quantum_gene
            }
        except Exception as e:
            logger.error(f"获取Ref健康状态时出错: {str(e)}")
            ref_status = {
                "status": "error",
                "error": str(e)
            }
        
        # 将Ref状态添加到健康状态
        health_status["ref"] = ref_status
        
        return health_status
    
    return health_check_with_ref

if __name__ == "__main__":
    print("Ref API集成模块 - 请通过QSM API调用") 

"""

"""
量子基因编码: QE-REF-8811A2B3871F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
