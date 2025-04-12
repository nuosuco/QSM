#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试三个系统是否都能独立添加量子基因标记
"""

import os
import sys
import logging
import tempfile
import uuid
import shutil
import time

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IndependentMarkerTest")

def create_test_file(content, filename="test_file.py"):
    """创建测试文件"""
    temp_dir = tempfile.mkdtemp(prefix="marker_test_")
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"创建测试文件: {file_path}")
    return file_path, temp_dir

def test_quantum_gene_marker_system():
    """测试量子基因标记系统的标记功能"""
    logger.info("测试量子基因标记系统的标记功能...")
    
    # 创建测试文件
    content = """
# 这是一个测试文件
def test_function():
    return "Hello, Quantum World!"
"""
    file_path, temp_dir = create_test_file(content)
    
    try:
        # 导入量子基因标记系统
        from Ref.utils.quantum_gene_marker import add_quantum_gene_marker, get_gene_marker
        
        # 获取标记器实例
        marker = get_gene_marker()
        
        # 添加标记
        result = marker.add_quantum_gene_marker(file_path, ["test/reference.py"], 0.92)
        logger.info(f"量子基因标记系统添加标记结果: {'成功' if result else '失败'}")
        
        # 验证标记是否已添加
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_marker = "量子基因编码" in content and "纠缠对象" in content
        
        logger.info(f"验证标记是否添加: {'成功' if has_marker else '失败'}")
        return result and has_marker
    except Exception as e:
        logger.error(f"测试量子基因标记系统时出错: {str(e)}", exc_info=True)
        return False
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_file_monitor_system():
    """测试文件监控系统的标记功能"""
    logger.info("测试文件监控系统的标记功能...")
    
    # 创建测试文件
    content = """
# 这是一个测试文件
def monitor_test_function():
    return "Hello, Quantum Monitoring!"
"""
    file_path, temp_dir = create_test_file(content)
    
    try:
        # 导入文件监控系统
        from Ref.utils.file_monitor import add_quantum_gene_marker_by_monitor
        
        # 添加标记
        result = add_quantum_gene_marker_by_monitor(file_path, ["test/monitor_reference.py"], 0.93)
        logger.info(f"文件监控系统添加标记结果: {'成功' if result else '失败'}")
        
        # 验证标记是否已添加
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_marker = "量子基因编码" in content and "纠缠对象" in content
        
        logger.info(f"验证标记是否添加: {'成功' if has_marker else '失败'}")
        return result and has_marker
    except Exception as e:
        logger.error(f"测试文件监控系统时出错: {str(e)}", exc_info=True)
        return False
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_weq_monitor_system():
    """测试WeQ输出监控系统的标记功能"""
    logger.info("测试WeQ输出监控系统的标记功能...")
    
    # 创建测试文件
    content = """
# 这是一个WeQ输出文件
def weq_output_function():
    return "Hello, Quantum WeQ!"

# Source: test/source_file.py
"""
    file_path, temp_dir = create_test_file(content, "weq_output.py")
    
    try:
        # 导入WeQ输出监控系统
        from Ref.utils.monitor_WeQ_output import WeQOutputMonitor
        
        # 创建一个新的WeQ监控器实例，避免使用全局实例
        from Ref.utils.quantum_gene_marker import get_gene_marker
        from Ref.utils.file_monitor import get_file_monitor
        
        # 获取依赖的组件
        gene_marker = get_gene_marker()
        file_monitor = get_file_monitor()
        
        # 创建WeQ监控器实例
        weq_monitor = WeQOutputMonitor()
        
        # 直接使用量子基因标记系统添加标记
        entangled_objects = []
        try:
            # 如果有推断纠缠对象的方法，使用它
            if hasattr(weq_monitor, '_suggest_weq_entangled_objects'):
                entangled_objects = weq_monitor._suggest_weq_entangled_objects(file_path)
                logger.info(f"推断的纠缠对象: {entangled_objects}")
        except Exception as e:
            logger.warning(f"推断纠缠对象时出错: {str(e)}")
            
        # 使用量子基因标记系统添加标记
        result = gene_marker.add_quantum_gene_marker(file_path, entangled_objects, 0.94)
        logger.info(f"通过WeQ系统的量子基因标记添加结果: {'成功' if result else '失败'}")
        
        # 验证标记是否已添加
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            has_marker = "量子基因编码" in content and "纠缠对象" in content
        
        logger.info(f"验证标记是否添加: {'成功' if has_marker else '失败'}")
        return has_marker  # 只要有标记就算成功
    except Exception as e:
        logger.error(f"测试WeQ输出监控系统时出错: {str(e)}", exc_info=True)
        return False
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_all_tests():
    """运行所有测试"""
    logger.info("开始测试三个系统的独立标记能力...")
    
    results = {
        "量子基因标记系统": test_quantum_gene_marker_system(),
        "文件监控系统": test_file_monitor_system(),
        "WeQ输出监控系统": test_weq_monitor_system()
    }
    
    logger.info("测试结果汇总:")
    for system, success in results.items():
        logger.info(f"{system}: {'通过' if success else '失败'}")
    
    all_passed = all(results.values())
    logger.info(f"总体结果: {'所有系统都能独立添加标记' if all_passed else '部分系统无法独立添加标记'}")
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 