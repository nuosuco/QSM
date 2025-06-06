#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子基因标记器日志配置修复工具
修复日志配置部分的缩进问题
"""

import os
import re
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_logging_indentation(target_file):
    """修复日志配置部分的缩进"""
    try:
        # 读取文件内容
        with open(target_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # 修复日志配置的缩进
        # 定义正则表达式匹配模式，匹配从"# 配置日志记录器"到"尝试导入QEntL的工具模块"之间的内容
        pattern = r'# 配置日志记录器.*?(?=class RefQuantumGeneMarker)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.error("无法找到日志配置部分")
            return False
            
        old_logging_config = match.group(0)
        
        # 替换为正确缩进的版本
        new_logging_config = """# 配置日志记录器
logger = logging.getLogger("Ref.utils.quantum_gene_marker")
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
        file_handler = logging.FileHandler("Ref/logs/quantum_gene_marker.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except:
        pass  # 如果目录不存在，则忽略文件处理器

# 将QEntL工具库添加到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
qentl_path = os.path.join(project_root, "QEntL")

if qentl_path not in sys.path:
    sys.path.append(qentl_path)

# 尝试导入QEntL的工具模块，但始终使用内部实现
try:
    import utils as qentl_utils
    logger.info("已找到QEntL工具模块，但将优先使用内部实现")
    qentl_utils = None  # 确保使用内部实现
except ImportError:
    logger.warning("未找到QEntL工具模块，将使用内部实现")
    qentl_utils = None

"""
        
        # 替换内容
        new_content = content.replace(old_logging_config, new_logging_config)
        
        # 写回文件
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        logger.info("成功修复日志配置部分的缩进")
        return True
    except Exception as e:
        logger.error(f"修复时出错: {str(e)}")
        return False

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确定量子基因标记器文件路径
    target_file = os.path.abspath(os.path.join(current_dir, '..', 'utils', 'quantum_gene_marker.py'))
    
    if not os.path.exists(target_file):
        logger.error(f"目标文件不存在: {target_file}")
        return 1
        
    # 创建备份
    backup_file = target_file + '.log_backup'
    try:
        import shutil
        shutil.copy2(target_file, backup_file)
        logger.info(f"已创建备份: {backup_file}")
    except Exception as e:
        logger.error(f"创建备份时出错: {str(e)}")
        return 1
        
    # 修复日志配置部分
    if not fix_logging_indentation(target_file):
        logger.error("修复日志配置部分失败")
        return 1
        
    logger.info("修复完成")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 

    """
    # 
"""
量子基因编码: QE-FIX-1A4409C5B587
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
    """
    