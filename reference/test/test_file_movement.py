#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
纠缠对象路径自动更新简单测试脚本
测试当文件移动时，是否自动更新所有相关文件中的纠缠对象路径
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("测试")

# 首先创建测试文件
def setup_test():
    """创建测试环境"""
    logger.info("===== 创建测试环境 =====")
    
    # 创建测试目录
    test_dir = os.path.join(project_root, "test", "temp")
    os.makedirs(test_dir, exist_ok=True)
    
    moved_dir = os.path.join(project_root, "test", "temp_moved")
    os.makedirs(moved_dir, exist_ok=True)
    
    # 创建测试文件
    file1_path = os.path.join(test_dir, "source_file.py")
    file2_path = os.path.join(test_dir, "reference_file.py")
    
    # 写入基本内容
    with open(file1_path, "w", encoding="utf-8") as f:
        f.write('"""Source file for testing"""')
    
    with open(file2_path, "w", encoding="utf-8") as f:
        f.write('"""Reference file for testing"""')
    
    logger.info(f"创建了测试文件: {file1_path} 和 {file2_path}")
    
    return {
        "source_file": file1_path,
        "reference_file": file2_path,
        "moved_dir": moved_dir
    }

# 主测试函数
def manual_test():
    """手动测试文件移动和路径更新"""
    test_files = setup_test()
    
    source_file = test_files["source_file"]
    reference_file = test_files["reference_file"]
    moved_dir = test_files["moved_dir"]
    
    # 打印说明
    logger.info("\n===== 测试说明 =====")
    logger.info("1. 在两个文件中手动添加量子基因标记，让它们相互引用")
    logger.info("2. 然后将source_file移动到temp_moved目录")
    logger.info("3. 观察路径是否自动更新")
    
    # 打印可执行命令
    logger.info("\n要添加量子基因标记，可以运行:")
    logger.info(f'python -c "from Ref.utils.quantum_gene_marker import add_quantum_gene_marker; add_quantum_gene_marker(\'{source_file}\', [\'{reference_file}\'])"')
    logger.info(f'python -c "from Ref.utils.quantum_gene_marker import add_quantum_gene_marker; add_quantum_gene_marker(\'{reference_file}\', [\'{source_file}\'])"')
    
    # 打印移动命令
    logger.info("\n要移动文件，可以运行:")
    new_path = os.path.join(moved_dir, os.path.basename(source_file))
    logger.info(f"shutil.move('{source_file}', '{new_path}')")
    
    # 打印检查命令
    logger.info("\n要检查路径是否更新，可以运行:")
    logger.info(f'python -c "from Ref.utils.quantum_gene_marker import get_gene_marker; m=get_gene_marker(); print(m._parse_entangled_objects(open(\'{new_path}\', \'r\', encoding=\'utf-8\').read()))"')
    logger.info(f'python -c "from Ref.utils.quantum_gene_marker import get_gene_marker; m=get_gene_marker(); print(m._parse_entangled_objects(open(\'{reference_file}\', \'r\', encoding=\'utf-8\').read()))"')
    
    return test_files

if __name__ == "__main__":
    manual_test() 

"""
"""
量子基因编码: QE-TES-E635515067EA
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
