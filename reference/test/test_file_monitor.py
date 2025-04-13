#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件监控系统
验证当文件移动时量子基因标记的自动更新功能
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path

# 添加父目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Ref核心
from Ref.ref_core import RefCore
from Ref.utils.quantum_gene_marker import get_gene_marker, add_quantum_gene_marker
from Ref.utils.file_monitor import get_file_monitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_file_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_test_files():
    """创建测试文件"""
    # 创建测试目录
    test_dir = Path('test/test_files')
    source_dir = test_dir / 'source'
    target_dir = test_dir / 'target'
    
    # 清理旧目录
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    # 创建目录
    source_dir.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试文件A
    file_a_path = source_dir / 'file_a.py'
    with open(file_a_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件A
"""

def function_a():
    """测试函数A"""
    return "This is file A"
''')
    
    # 创建测试文件B
    file_b_path = source_dir / 'file_b.py'
    with open(file_b_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文件B
"""

def function_b():
    """测试函数B"""
    return "This is file B"
''')
    
    # 创建引用文件
    ref_file_path = source_dir / 'reference.py'
    with open(ref_file_path, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
引用文件，引用了文件A和文件B
"""

from source.file_a import function_a
from source.file_b import function_b

def combined_function():
    """组合函数"""
    return function_a() + " and " + function_b()
''')
    
    return {
        'file_a': file_a_path,
        'file_b': file_b_path,
        'reference': ref_file_path,
        'target_dir': target_dir
    }

def add_quantum_gene_markers(files):
    """为测试文件添加量子基因标记"""
    gene_marker = get_gene_marker()
    
    # 为文件A添加标记
    add_quantum_gene_marker(files['file_a'], [str(files['file_a']), str(files['reference'])])
    
    # 为文件B添加标记  
    add_quantum_gene_marker(files['file_b'], [str(files['file_b']), str(files['reference'])])
    
    # 为引用文件添加标记
    add_quantum_gene_marker(files['reference'], [str(files['file_a']), str(files['file_b']), str(files['reference'])])
    
    logger.info("已为测试文件添加量子基因标记")

def test_file_movement(files):
    """测试文件移动功能"""
    # 移动文件A到目标目录
    source_path = files['file_a']
    target_path = files['target_dir'] / 'moved_file_a.py'
    
    logger.info(f"准备移动文件: {source_path} -> {target_path}")
    
    # 执行移动
    shutil.move(source_path, target_path)
    
    # 等待文件监控系统处理
    logger.info("等待文件监控系统处理...")
    time.sleep(5)
    
    # 验证引用文件中的量子基因标记是否已更新
    with open(files['reference'], 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查量子基因标记是否包含新的路径
    if str(target_path) in content:
        logger.info("✅ 成功: 引用文件中的量子基因标记已更新")
    else:
        logger.error("❌ 失败: 引用文件中的量子基因标记未更新")
        logger.debug(f"引用文件内容: {content}")

def main():
    """主函数"""
    logger.info("开始测试文件监控系统")
    
    # 初始化Ref核心
    ref_core = RefCore()
    
    # 获取文件监控器
    file_monitor = get_file_monitor(ref_core)
    
    # 启动文件监控
    file_monitor.start()
    
    try:
        # 创建测试文件
        logger.info("创建测试文件...")
        files = create_test_files()
        
        # 添加量子基因标记
        logger.info("添加量子基因标记...")
        add_quantum_gene_markers(files)
        
        # 测试文件移动
        logger.info("测试文件移动...")
        test_file_movement(files)
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
    finally:
        # 停止文件监控
        file_monitor.stop()
        logger.info("测试完成")

if __name__ == "__main__":
    main() 

"""
"""
量子基因编码: QE-TES-5F2B72732077
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
