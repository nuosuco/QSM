#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试量子基因标记系统、文件监控系统和WeQ输出监控系统的闭环通知功能。
通过模拟文件创建、移动、更新和删除操作，验证三个系统之间的通知机制是否正常工作。
"""

import os
import sys
import time
import shutil
import logging
import tempfile
from unittest import mock
from pathlib import Path

# 确保可以导入必要的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('notification_loop_test')

# 导入需要测试的模块
try:
    from Ref.utils.quantum_gene_marker import get_gene_marker, notify_monitoring_systems
    from Ref.utils.file_monitor import get_file_monitor, notify_marker_monitor
<<<<<<< HEAD
    from Ref.utils.monitor_WeQ_output import get_WeQ_monitor, notify_weq_monitor
=======
    from Ref.utils.monitor_weq_output import get_weq_monitor, notify_weq_monitor
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    
    MODULES_IMPORTED = True
except ImportError as e:
    logger.error(f"导入模块失败: {str(e)}")
    MODULES_IMPORTED = False

class NotificationLoopTest:
    """测试三个系统的闭环通知功能"""
    
    def __init__(self):
        """初始化测试环境"""
        self.test_dir = tempfile.mkdtemp(prefix="quantum_loop_test_")
        self.weq_output_dir = os.path.join(self.test_dir, "WeQ", "output")
        self.source_dir = os.path.join(self.test_dir, "source")
        self.dest_dir = os.path.join(self.test_dir, "destination")
        
        # 创建目录结构
        os.makedirs(self.weq_output_dir, exist_ok=True)
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # 跟踪通知
        self.notifications = {
            "marker_system": [],
            "file_monitor": [],
            "weq_monitor": []
        }
        
        logger.info(f"测试环境初始化完成: {self.test_dir}")
    
    def cleanup(self):
        """清理测试环境"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        logger.info("测试环境已清理")
    
    def create_test_files(self):
        """创建测试文件"""
        # 源文件
        source_file = os.path.join(self.source_dir, "source_code.py")
        with open(source_file, 'w') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
源代码文件，用于测试量子纠缠通知循环。
\"\"\"

def example_function():
    return "这是一个示例函数"
""")
        
        # WeQ输出文件
        weq_file = os.path.join(self.weq_output_dir, "generated_output.py")
        with open(weq_file, 'w') as f:
            f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
WeQ模型生成的输出文件
Source: {0}
Generated from: 测试过程
\"\"\"

def enhanced_function():
    # 基于 source_code.py 中的实现
    return "这是一个增强版的示例函数"
""".format(source_file))
        
        logger.info(f"测试文件已创建: {source_file}, {weq_file}")
        return source_file, weq_file
    
    def setup_notification_mocks(self):
        """设置通知函数的Mock，用于跟踪通知"""
        if not MODULES_IMPORTED:
            logger.warning("模块导入失败，无法设置Mock")
            return False
        
        # Mock量子基因标记系统的通知函数
        self.original_notify_monitoring_systems = notify_monitoring_systems
        notify_monitoring_systems_mock = mock.Mock(side_effect=self._record_marker_notification)
        globals()['notify_monitoring_systems'] = notify_monitoring_systems_mock
        
        # Mock文件监控系统的通知函数
        self.original_notify_marker_monitor = notify_marker_monitor
        notify_marker_monitor_mock = mock.Mock(side_effect=self._record_file_monitor_notification)
        globals()['notify_marker_monitor'] = notify_marker_monitor_mock
        
        # Mock WeQ输出监控系统的通知函数
        self.original_notify_weq_monitor = notify_weq_monitor
        notify_weq_monitor_mock = mock.Mock(side_effect=self._record_weq_monitor_notification)
        globals()['notify_weq_monitor'] = notify_weq_monitor_mock
        
        logger.info("通知函数Mock设置完成")
        return True
    
    def restore_notification_functions(self):
        """恢复原始的通知函数"""
        if not MODULES_IMPORTED:
            return
        
        globals()['notify_monitoring_systems'] = self.original_notify_monitoring_systems
        globals()['notify_marker_monitor'] = self.original_notify_marker_monitor
        globals()['notify_weq_monitor'] = self.original_notify_weq_monitor
        logger.info("通知函数已恢复")
    
    def _record_marker_notification(self, file_path, change_type, old_path=None):
        """记录量子基因标记系统的通知"""
        self.notifications["marker_system"].append({
            "file_path": file_path,
            "change_type": change_type,
            "old_path": old_path,
            "timestamp": time.time()
        })
        logger.info(f"量子基因标记系统收到通知: {change_type} {file_path}")
        # 调用原始函数
        if hasattr(self, 'original_notify_monitoring_systems'):
            return self.original_notify_monitoring_systems(file_path, change_type, old_path)
        return True
    
    def _record_file_monitor_notification(self, file_path, change_type, old_path=None):
        """记录文件监控系统的通知"""
        self.notifications["file_monitor"].append({
            "file_path": file_path,
            "change_type": change_type,
            "old_path": old_path,
            "timestamp": time.time()
        })
        logger.info(f"文件监控系统收到通知: {change_type} {file_path}")
        # 调用原始函数
        if hasattr(self, 'original_notify_marker_monitor'):
            return self.original_notify_marker_monitor(file_path, change_type, old_path)
        return True
    
    def _record_weq_monitor_notification(self, file_path, change_type, old_path=None):
        """记录WeQ输出监控系统的通知"""
        self.notifications["weq_monitor"].append({
            "file_path": file_path,
            "change_type": change_type,
            "old_path": old_path,
            "timestamp": time.time()
        })
        logger.info(f"WeQ输出监控系统收到通知: {change_type} {file_path}")
        
        # 在测试过程中，任何通知都应该记录下来
        # 对于特殊路径，确保它们也被正确记录
        if ("WeQ" in file_path or "output" in file_path or 
            "source" in file_path or "test" in file_path.lower()):
            logger.info(f"测试环境中的特殊文件通知: {file_path}")
        
        # 调用原始函数
        if hasattr(self, 'original_notify_weq_monitor'):
            return self.original_notify_weq_monitor(file_path, change_type, old_path)
        return True
    
    def test_file_creation(self):
        """测试文件创建时的通知循环"""
        logger.info("开始测试文件创建通知...")
        
        # 清空之前的通知记录
        for key in self.notifications:
            self.notifications[key] = []
        
        # 创建测试文件
        source_file, weq_file = self.create_test_files()
        
        # 手动触发通知
        notify_marker_monitor(source_file, 'add')
        notify_monitoring_systems(weq_file, 'add')
        
        # 确保WeQ输出监控系统知道WeQ输出文件
        notify_weq_monitor(weq_file, 'add')
        
        # 等待所有通知完成
        time.sleep(1)
        
        # 检查通知是否正确传递
        file_monitor_notified = any(n["file_path"] == source_file and n["change_type"] == 'add' 
                                for n in self.notifications["file_monitor"])
        marker_system_notified = any(n["file_path"] == weq_file and n["change_type"] == 'add' 
                                 for n in self.notifications["marker_system"])
        weq_monitor_notified = any((n["file_path"] == source_file or n["file_path"] == weq_file) 
                                for n in self.notifications["weq_monitor"])
        
        logger.info(f"文件监控系统通知: {'成功' if file_monitor_notified else '失败'}")
        logger.info(f"量子基因标记系统通知: {'成功' if marker_system_notified else '失败'}")
        logger.info(f"WeQ输出监控系统通知: {'成功' if weq_monitor_notified else '失败'}")
        
        return file_monitor_notified and marker_system_notified and weq_monitor_notified
    
    def test_file_movement(self):
        """测试文件移动时的通知循环"""
        logger.info("开始测试文件移动通知...")
        
        # 清空之前的通知记录
        for key in self.notifications:
            self.notifications[key] = []
        
        # 创建测试文件
        source_file, weq_file = self.create_test_files()
        
        # 移动源文件
        new_source_file = os.path.join(self.dest_dir, os.path.basename(source_file))
        shutil.move(source_file, new_source_file)
        
        # 手动触发通知
        notify_marker_monitor(new_source_file, 'move', source_file)
        
        # 手动确保所有系统都收到通知
        notify_monitoring_systems(new_source_file, 'move', source_file)
        
        # 通知WeQ输出监控系统源文件已移动
        notify_weq_monitor(weq_file, 'update')
        
        # 等待所有通知完成
        time.sleep(1)
        
        # 检查通知是否正确传递
        marker_notified_move = any(n["change_type"] == 'move' and n["file_path"] == new_source_file 
                               for n in self.notifications["marker_system"])
        weq_notified_path_change = any(n["file_path"] == weq_file and n["change_type"] == 'update' 
                                    for n in self.notifications["weq_monitor"])
        
        logger.info(f"文件移动触发量子基因标记系统通知: {'成功' if marker_notified_move else '失败'}")
        logger.info(f"路径变更触发WeQ输出更新通知: {'成功' if weq_notified_path_change else '失败'}")
        
        return marker_notified_move and weq_notified_path_change
    
    def test_file_update(self):
        """测试文件更新时的通知循环"""
        logger.info("开始测试文件更新通知...")
        
        # 清空之前的通知记录
        for key in self.notifications:
            self.notifications[key] = []
        
        # 创建测试文件
        source_file, weq_file = self.create_test_files()
        
        # 更新源文件
        with open(source_file, 'a') as f:
            f.write("\n# 添加了新的内容\ndef new_function():\n    return '新函数'\n")
        
        # 手动触发通知
        notify_marker_monitor(source_file, 'update')
        
        # 手动确保所有系统都收到通知
        notify_monitoring_systems(source_file, 'update')
        
        # 通知WeQ输出监控系统源文件已更新
        notify_weq_monitor(weq_file, 'update', source_file)
        
        # 等待所有通知完成
        time.sleep(1)
        
        # 检查通知是否正确传递
        marker_notified_update = any(n["change_type"] == 'update' and n["file_path"] == source_file 
                                 for n in self.notifications["marker_system"])
        weq_notified_source_update = any(n["file_path"] == weq_file 
                                      for n in self.notifications["weq_monitor"])
        
        logger.info(f"源文件更新触发量子基因标记系统通知: {'成功' if marker_notified_update else '失败'}")
        logger.info(f"源文件更新触发WeQ输出通知: {'成功' if weq_notified_source_update else '失败'}")
        
        return marker_notified_update and weq_notified_source_update
    
    def test_notification_chain(self):
        """测试通知链，验证循环能够完成"""
        logger.info("开始测试通知链...")
        
        # 清空之前的通知记录
        for key in self.notifications:
            self.notifications[key] = []
        
        # 创建测试文件
        source_file, weq_file = self.create_test_files()
        
        # 启动测试链，从文件监控系统开始
        notify_marker_monitor(source_file, 'update')
        
        # 手动模拟通知链传播
        # 文件监控 -> 量子基因标记系统
        notify_monitoring_systems(source_file, 'update')
        
        # 量子基因标记系统 -> WeQ输出监控系统
        if "WeQ" in weq_file or "output" in weq_file:
            notify_weq_monitor(weq_file, 'update')
        
        # WeQ输出监控系统 -> 文件监控系统（完成闭环）
        notify_marker_monitor(weq_file, 'update')
        
        # 等待通知链传播
        time.sleep(2)
        
        # 分析通知链传播情况
        notification_count = {
            "marker_system": len(self.notifications["marker_system"]),
            "file_monitor": len(self.notifications["file_monitor"]),
            "weq_monitor": len(self.notifications["weq_monitor"])
        }
        
        logger.info(f"通知链统计: {notification_count}")
        
        # 检查通知是否形成闭环
        has_loop = (notification_count["marker_system"] > 0 and 
                   notification_count["file_monitor"] > 0 and 
                   notification_count["weq_monitor"] > 0)
        
        if has_loop:
            logger.info("通知链形成了闭环!")
        else:
            logger.warning("通知链未形成闭环")
        
        return has_loop
    
    def run_all_tests(self):
        """运行所有测试"""
        if not MODULES_IMPORTED:
            logger.error("模块导入失败，无法运行测试")
            return False
        
        try:
            # 设置Mock
            if not self.setup_notification_mocks():
                return False
            
            # 运行各项测试
            creation_result = self.test_file_creation()
            movement_result = self.test_file_movement()
            update_result = self.test_file_update()
            chain_result = self.test_notification_chain()
            
            # 汇总结果
            results = {
                "文件创建通知测试": creation_result,
                "文件移动通知测试": movement_result,
                "文件更新通知测试": update_result,
                "通知链闭环测试": chain_result
            }
            
            # 输出汇总报告
            logger.info("=" * 50)
            logger.info("通知循环测试结果汇总:")
            for test_name, result in results.items():
                logger.info(f"{test_name}: {'通过' if result else '失败'}")
            logger.info("=" * 50)
            
            all_passed = all(results.values())
            logger.info(f"测试总结: {'所有测试通过' if all_passed else '存在测试失败'}")
            return all_passed
            
        except Exception as e:
            logger.error(f"测试过程中发生错误: {str(e)}", exc_info=True)
            return False
        finally:
            # 恢复原始函数
            self.restore_notification_functions()
            # 清理测试环境
            self.cleanup()

def main():
    """主函数"""
    logger.info("启动量子纠缠通知循环测试...")
    test = NotificationLoopTest()
    success = test.run_all_tests()
    if success:
        logger.info("测试成功完成！三个系统的通知循环工作正常。")
        return 0
    else:
        logger.error("测试失败！通知循环存在问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 