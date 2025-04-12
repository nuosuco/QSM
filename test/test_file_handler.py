#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试QuantumFileEventHandler的文件移动处理逻辑
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

# 导入需要的模块
from Ref.utils.quantum_gene_marker import add_quantum_gene_marker, get_gene_marker
from Ref.utils.file_monitor import QuantumFileEventHandler
from watchdog.events import FileMovedEvent

class MockRefCore:
    """模拟的Ref核心类"""
    def __init__(self):
        self.project_root = project_root

def main():
    """测试QuantumFileEventHandler的处理逻辑"""
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
    
    # 添加量子基因标记
    marker = get_gene_marker()
    
    # 文件1引用文件2
    add_quantum_gene_marker(file1_path, [file2_path])
    logger.info(f"已添加量子基因标记到 {file1_path}，引用 {file2_path}")
    
    # 文件2引用文件1
    add_quantum_gene_marker(file2_path, [file1_path])
    logger.info(f"已添加量子基因标记到 {file2_path}，引用 {file1_path}")
    
    # 检查标记
    with open(file1_path, "r", encoding="utf-8") as f:
        content1 = f.read()
    with open(file2_path, "r", encoding="utf-8") as f:
        content2 = f.read()
    
    logger.info(f"文件1的纠缠对象: {marker._parse_entangled_objects(content1)}")
    logger.info(f"文件2的纠缠对象: {marker._parse_entangled_objects(content2)}")
    
    # 创建事件处理器
    mock_core = MockRefCore()
    handler = QuantumFileEventHandler(mock_core)
    
    # 模拟文件移动
    src_path = file1_path
    dest_path = os.path.join(moved_dir, "source_file.py")
    
    # 移动文件
    logger.info(f"移动文件: {src_path} -> {dest_path}")
    shutil.copy2(src_path, dest_path)  # 复制而不是移动，以保留原文件
    
    # 创建文件移动事件
    event = FileMovedEvent(src_path, dest_path)
    
    # 直接调用处理方法
    logger.info("调用事件处理器的on_moved方法...")
    handler.on_moved(event)
    
    # 等待处理完成
    logger.info("等待处理完成...")
    time.sleep(2)
    
    # 检查更新后的标记
    if os.path.exists(dest_path):
        with open(dest_path, "r", encoding="utf-8") as f:
            content_moved = f.read()
        
        logger.info(f"移动后文件的纠缠对象: {marker._parse_entangled_objects(content_moved)}")
    else:
        logger.error(f"移动后的文件不存在: {dest_path}")
    
    with open(file2_path, "r", encoding="utf-8") as f:
        content2_after = f.read()
    
    logger.info(f"引用文件的纠缠对象: {marker._parse_entangled_objects(content2_after)}")
    
    # 检查引用路径是否更新
    entangled_objects_moved = marker._parse_entangled_objects(content_moved)
    entangled_objects_ref = marker._parse_entangled_objects(content2_after)
    
    if file2_path in entangled_objects_moved:
        logger.info("✓ 被移动文件中的引用路径正确")
    else:
        logger.error(f"✗ 被移动文件中的引用路径不正确: {entangled_objects_moved}")
    
    if dest_path in entangled_objects_ref:
        logger.info("✓ 引用文件中的路径已更新")
    elif src_path in entangled_objects_ref:
        logger.error("✗ 引用文件中的路径未更新")
    else:
        logger.error(f"✗ 引用文件中找不到任何相关路径: {entangled_objects_ref}")

if __name__ == "__main__":
    main() 
"""
量子基因编码: QE-TES-3E75A8AFBE7A
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
"""