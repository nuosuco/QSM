#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控增强器测试脚本
"""

import os
import sys
import time
import json
import unittest
import threading
from unittest.mock import patch, MagicMock

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入被测试模块
from system_monitor_enhancer import SystemMonitorEnhancer, SystemHealth

class TestSystemMonitorEnhancer(unittest.TestCase):
    """系统监控增强器测试类"""
    
    def setUp(self):
        """测试前设置"""
        # 创建一个模拟的ref_core
        self.mock_ref_core = MagicMock()
        self.mock_ref_core.registered_models = {
            'qsm': {'path': 'models/qsm/qsm_core.py', 'checksum': 'abc123'},
            'som': {'path': 'models/som/som_core.py', 'checksum': 'def456'},
            'weq': {'path': 'models/weq/weq_core.py', 'checksum': 'ghi789'}
        }
        
        # 创建监控器实例
        self.monitor = SystemMonitorEnhancer(ref_core=self.mock_ref_core)
    
    def tearDown(self):
        """测试后清理"""
        if self.monitor.running:
            self.monitor.stop_monitoring()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertFalse(self.monitor.running)
        self.assertIsNone(self.monitor.monitor_thread)
        self.assertEqual(self.monitor.system_status['health']['status'], SystemHealth.HEALTHY)
        self.assertEqual(self.monitor.system_status['health']['score'], 100)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_resources(self, mock_disk, mock_memory, mock_cpu):
        """测试资源检查"""
        # 配置模拟对象
        mock_cpu.return_value = 75.5
        
        mock_memory_obj = MagicMock()
        mock_memory_obj.percent = 65.3
        mock_memory.return_value = mock_memory_obj
        
        mock_disk_obj = MagicMock()
        mock_disk_obj.percent = 82.1
        mock_disk.return_value = mock_disk_obj
        
        # 执行被测试方法
        self.monitor._check_resources()
        
        # 验证结果
        self.assertEqual(self.monitor.system_metrics['cpu_usage'], 75.5)
        self.assertEqual(self.monitor.system_metrics['memory_usage'], 65.3)
        self.assertEqual(self.monitor.system_metrics['disk_usage'], 82.1)
        
        self.assertEqual(self.monitor.system_status['resources']['cpu'], 75.5)
        self.assertEqual(self.monitor.system_status['resources']['memory'], 65.3)
        self.assertEqual(self.monitor.system_status['resources']['disk'], 82.1)
    
    @patch('os.path.exists')
    def test_check_models_health(self, mock_exists):
        """测试模型健康检查"""
        # 配置模拟对象
        mock_exists.return_value = True
        
        # 执行被测试方法
        self.monitor._check_models_health()
        
        # 验证结果
        self.assertEqual(len(self.monitor.models_health), 3)
        self.assertIn('qsm', self.monitor.models_health)
        self.assertIn('som', self.monitor.models_health)
        self.assertIn('weq', self.monitor.models_health)
        
        # 验证健康状态格式
        for model_id, health_data in self.monitor.models_health.items():
            self.assertIn('health', health_data)
            self.assertIn('status', health_data)
            self.assertIn('last_check', health_data)
            
            # 验证状态值是有效的
            self.assertIn(health_data['status'], 
                         [SystemHealth.HEALTHY, SystemHealth.DEGRADED, SystemHealth.CRITICAL])
            
            # 健康分数应该在0-100之间
            self.assertGreaterEqual(health_data['health'], 0)
            self.assertLessEqual(health_data['health'], 100)
    
    def test_calculate_overall_health(self):
        """测试整体健康分数计算"""
        # 设置测试条件
        self.monitor.system_metrics = {
            'cpu_usage': 90,
            'memory_usage': 85,
            'disk_usage': 75
        }
        
        self.monitor.models_health = {
            'qsm': {'health': 95, 'status': SystemHealth.HEALTHY},
            'som': {'health': 65, 'status': SystemHealth.DEGRADED},
            'weq': {'health': 30, 'status': SystemHealth.CRITICAL}
        }
        
        self.monitor.index_status = {
            'docs/global/qsm_project_index.md': {'exists': True, 'status': 'healthy'},
            'docs/global/detailed_index.md': {'exists': False, 'status': 'missing'}
        }
        
        # 执行被测试方法
        self.monitor._calculate_overall_health()
        
        # 验证结果
        # 预期扣分: CPU过高 (90-80)*0.5=5, 内存过高 (85-80)*0.5=2.5, 
        # 磁盘正常, som降级=5, weq危险=15, 缺少索引=5
        # 100 - 5 - 2.5 - 5 - 15 - 5 = 67.5
        
        # 允许一些浮点数计算误差
        self.assertAlmostEqual(self.monitor.system_status['health']['score'], 67.5, delta=1)
        self.assertEqual(self.monitor.system_status['health']['status'], SystemHealth.DEGRADED)
    
    def test_start_stop_monitoring(self):
        """测试启动和停止监控"""
        # 启动监控
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.running)
        self.assertIsNotNone(self.monitor.monitor_thread)
        self.assertTrue(self.monitor.monitor_thread.is_alive())
        
        # 停止监控
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.running)
        
        # 等待线程完全停止
        time.sleep(0.1)
        self.assertFalse(self.monitor.monitor_thread.is_alive())
    
    def test_get_system_status(self):
        """测试获取系统状态"""
        status = self.monitor.get_system_status()
        
        self.assertIn('health', status)
        self.assertIn('resources', status)
        self.assertIn('last_check', status)
        self.assertIn('models_count', status)
        self.assertIn('anomalies_count', status)
        self.assertIn('suggestions_count', status)
    
    def test_get_detailed_status(self):
        """测试获取详细状态"""
        detailed = self.monitor.get_detailed_status()
        
        self.assertIn('health', detailed)
        self.assertIn('resources', detailed)
        self.assertIn('models', detailed)
        self.assertIn('anomalies', detailed)
        self.assertIn('suggestions', detailed)
        self.assertIn('index_status', detailed)
    
    def test_get_dashboard_data(self):
        """测试获取仪表盘数据"""
        data = self.monitor.get_dashboard_data()
        
        self.assertIn('health', data)
        self.assertIn('resources', data)
        self.assertIn('models', data)
        self.assertIn('suggestions', data)
        self.assertIn('anomalies', data)
        self.assertIn('timestamp', data)
    
    @patch('subprocess.run')
    def test_optimize_indices(self, mock_run):
        """测试优化索引"""
        # 配置模拟对象
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # 模拟脚本存在
        with patch('os.path.exists', return_value=True):
            result = self.monitor._optimize_indices()
            self.assertTrue(result)
            mock_run.assert_called_once()
    
    @patch('os.makedirs')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    @patch('json.dump')
    def test_create_system_backup(self, mock_dump, mock_copy2, mock_copytree, mock_makedirs):
        """测试创建系统备份"""
        # 配置模拟对象
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                # 执行被测试方法
                result = self.monitor._create_system_backup()
                
                # 验证结果
                self.assertTrue(result)
                mock_makedirs.assert_called()
                mock_copytree.assert_called()
                mock_dump.assert_called_once()
    
    def test_anomaly_detection(self):
        """测试异常检测"""
        # 创建一些测试数据
        for i in range(20):
            # 正常数据
            self.monitor.metrics_history['cpu_usage'].append((time.time() - i*60, 50 + i*0.5))
        
        # 添加一个异常值
        self.monitor.metrics_history['cpu_usage'].append((time.time(), 95))
        
        # 执行被测试方法
        self.monitor.detect_anomalies()
        
        # 验证结果
        self.assertGreater(len(self.monitor.anomalies), 0)
        
        # 检查第一个异常
        if self.monitor.anomalies:
            anomaly = self.monitor.anomalies[0]
            self.assertEqual(anomaly['metric'], 'cpu_usage')
            self.assertGreater(anomaly['z_score'], 0)  # 应该是正的z分数（高于均值）
    
    def test_generate_suggestions(self):
        """测试生成优化建议"""
        # 设置一些测试条件
        self.monitor.system_metrics = {
            'cpu_usage': 92,
            'memory_usage': 85,
            'disk_usage': 95
        }
        
        self.monitor.models_health = {
            'qsm': {'health': 95, 'status': SystemHealth.HEALTHY},
            'som': {'health': 35, 'status': SystemHealth.CRITICAL}
        }
        
        self.monitor.index_status = {
            'docs/global/qsm_project_index.md': {'exists': False, 'status': 'missing'}
        }
        
        # 执行被测试方法
        self.monitor.generate_suggestions()
        
        # 验证结果
        self.assertGreater(len(self.monitor.suggestions), 0)
        
        # 应该有CPU、内存、磁盘、模型和索引相关的建议
        suggestion_messages = [s['message'] for s in self.monitor.suggestions]
        self.assertTrue(any('CPU' in msg for msg in suggestion_messages))
        self.assertTrue(any('内存' in msg for msg in suggestion_messages))
        self.assertTrue(any('磁盘' in msg for msg in suggestion_messages))
        self.assertTrue(any('SOM' in msg for msg in suggestion_messages))
        self.assertTrue(any('索引' in msg for msg in suggestion_messages))


if __name__ == '__main__':
    unittest.main() 
# -*- coding: utf-8 -*-

"""
系统监控增强器测试脚本
"""

import os
import sys
import time
import json
import unittest
import threading
from unittest.mock import patch, MagicMock

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入被测试模块
from system_monitor_enhancer import SystemMonitorEnhancer, SystemHealth

class TestSystemMonitorEnhancer(unittest.TestCase):
    """系统监控增强器测试类"""
    
    def setUp(self):
        """测试前设置"""
        # 创建一个模拟的ref_core
        self.mock_ref_core = MagicMock()
        self.mock_ref_core.registered_models = {
            'qsm': {'path': 'models/qsm/qsm_core.py', 'checksum': 'abc123'},
            'som': {'path': 'models/som/som_core.py', 'checksum': 'def456'},
            'weq': {'path': 'models/weq/weq_core.py', 'checksum': 'ghi789'}
        }
        
        # 创建监控器实例
        self.monitor = SystemMonitorEnhancer(ref_core=self.mock_ref_core)
    
    def tearDown(self):
        """测试后清理"""
        if self.monitor.running:
            self.monitor.stop_monitoring()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertFalse(self.monitor.running)
        self.assertIsNone(self.monitor.monitor_thread)
        self.assertEqual(self.monitor.system_status['health']['status'], SystemHealth.HEALTHY)
        self.assertEqual(self.monitor.system_status['health']['score'], 100)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_resources(self, mock_disk, mock_memory, mock_cpu):
        """测试资源检查"""
        # 配置模拟对象
        mock_cpu.return_value = 75.5
        
        mock_memory_obj = MagicMock()
        mock_memory_obj.percent = 65.3
        mock_memory.return_value = mock_memory_obj
        
        mock_disk_obj = MagicMock()
        mock_disk_obj.percent = 82.1
        mock_disk.return_value = mock_disk_obj
        
        # 执行被测试方法
        self.monitor._check_resources()
        
        # 验证结果
        self.assertEqual(self.monitor.system_metrics['cpu_usage'], 75.5)
        self.assertEqual(self.monitor.system_metrics['memory_usage'], 65.3)
        self.assertEqual(self.monitor.system_metrics['disk_usage'], 82.1)
        
        self.assertEqual(self.monitor.system_status['resources']['cpu'], 75.5)
        self.assertEqual(self.monitor.system_status['resources']['memory'], 65.3)
        self.assertEqual(self.monitor.system_status['resources']['disk'], 82.1)
    
    @patch('os.path.exists')
    def test_check_models_health(self, mock_exists):
        """测试模型健康检查"""
        # 配置模拟对象
        mock_exists.return_value = True
        
        # 执行被测试方法
        self.monitor._check_models_health()
        
        # 验证结果
        self.assertEqual(len(self.monitor.models_health), 3)
        self.assertIn('qsm', self.monitor.models_health)
        self.assertIn('som', self.monitor.models_health)
        self.assertIn('weq', self.monitor.models_health)
        
        # 验证健康状态格式
        for model_id, health_data in self.monitor.models_health.items():
            self.assertIn('health', health_data)
            self.assertIn('status', health_data)
            self.assertIn('last_check', health_data)
            
            # 验证状态值是有效的
            self.assertIn(health_data['status'], 
                         [SystemHealth.HEALTHY, SystemHealth.DEGRADED, SystemHealth.CRITICAL])
            
            # 健康分数应该在0-100之间
            self.assertGreaterEqual(health_data['health'], 0)
            self.assertLessEqual(health_data['health'], 100)
    
    def test_calculate_overall_health(self):
        """测试整体健康分数计算"""
        # 设置测试条件
        self.monitor.system_metrics = {
            'cpu_usage': 90,
            'memory_usage': 85,
            'disk_usage': 75
        }
        
        self.monitor.models_health = {
            'qsm': {'health': 95, 'status': SystemHealth.HEALTHY},
            'som': {'health': 65, 'status': SystemHealth.DEGRADED},
            'weq': {'health': 30, 'status': SystemHealth.CRITICAL}
        }
        
        self.monitor.index_status = {
            'docs/global/qsm_project_index.md': {'exists': True, 'status': 'healthy'},
            'docs/global/detailed_index.md': {'exists': False, 'status': 'missing'}
        }
        
        # 执行被测试方法
        self.monitor._calculate_overall_health()
        
        # 验证结果
        # 预期扣分: CPU过高 (90-80)*0.5=5, 内存过高 (85-80)*0.5=2.5, 
        # 磁盘正常, som降级=5, weq危险=15, 缺少索引=5
        # 100 - 5 - 2.5 - 5 - 15 - 5 = 67.5
        
        # 允许一些浮点数计算误差
        self.assertAlmostEqual(self.monitor.system_status['health']['score'], 67.5, delta=1)
        self.assertEqual(self.monitor.system_status['health']['status'], SystemHealth.DEGRADED)
    
    def test_start_stop_monitoring(self):
        """测试启动和停止监控"""
        # 启动监控
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.running)
        self.assertIsNotNone(self.monitor.monitor_thread)
        self.assertTrue(self.monitor.monitor_thread.is_alive())
        
        # 停止监控
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.running)
        
        # 等待线程完全停止
        time.sleep(0.1)
        self.assertFalse(self.monitor.monitor_thread.is_alive())
    
    def test_get_system_status(self):
        """测试获取系统状态"""
        status = self.monitor.get_system_status()
        
        self.assertIn('health', status)
        self.assertIn('resources', status)
        self.assertIn('last_check', status)
        self.assertIn('models_count', status)
        self.assertIn('anomalies_count', status)
        self.assertIn('suggestions_count', status)
    
    def test_get_detailed_status(self):
        """测试获取详细状态"""
        detailed = self.monitor.get_detailed_status()
        
        self.assertIn('health', detailed)
        self.assertIn('resources', detailed)
        self.assertIn('models', detailed)
        self.assertIn('anomalies', detailed)
        self.assertIn('suggestions', detailed)
        self.assertIn('index_status', detailed)
    
    def test_get_dashboard_data(self):
        """测试获取仪表盘数据"""
        data = self.monitor.get_dashboard_data()
        
        self.assertIn('health', data)
        self.assertIn('resources', data)
        self.assertIn('models', data)
        self.assertIn('suggestions', data)
        self.assertIn('anomalies', data)
        self.assertIn('timestamp', data)
    
    @patch('subprocess.run')
    def test_optimize_indices(self, mock_run):
        """测试优化索引"""
        # 配置模拟对象
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        # 模拟脚本存在
        with patch('os.path.exists', return_value=True):
            result = self.monitor._optimize_indices()
            self.assertTrue(result)
            mock_run.assert_called_once()
    
    @patch('os.makedirs')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    @patch('json.dump')
    def test_create_system_backup(self, mock_dump, mock_copy2, mock_copytree, mock_makedirs):
        """测试创建系统备份"""
        # 配置模拟对象
        with patch('os.path.exists', return_value=True):
            with patch('os.path.isdir', return_value=True):
                # 执行被测试方法
                result = self.monitor._create_system_backup()
                
                # 验证结果
                self.assertTrue(result)
                mock_makedirs.assert_called()
                mock_copytree.assert_called()
                mock_dump.assert_called_once()
    
    def test_anomaly_detection(self):
        """测试异常检测"""
        # 创建一些测试数据
        for i in range(20):
            # 正常数据
            self.monitor.metrics_history['cpu_usage'].append((time.time() - i*60, 50 + i*0.5))
        
        # 添加一个异常值
        self.monitor.metrics_history['cpu_usage'].append((time.time(), 95))
        
        # 执行被测试方法
        self.monitor.detect_anomalies()
        
        # 验证结果
        self.assertGreater(len(self.monitor.anomalies), 0)
        
        # 检查第一个异常
        if self.monitor.anomalies:
            anomaly = self.monitor.anomalies[0]
            self.assertEqual(anomaly['metric'], 'cpu_usage')
            self.assertGreater(anomaly['z_score'], 0)  # 应该是正的z分数（高于均值）
    
    def test_generate_suggestions(self):
        """测试生成优化建议"""
        # 设置一些测试条件
        self.monitor.system_metrics = {
            'cpu_usage': 92,
            'memory_usage': 85,
            'disk_usage': 95
        }
        
        self.monitor.models_health = {
            'qsm': {'health': 95, 'status': SystemHealth.HEALTHY},
            'som': {'health': 35, 'status': SystemHealth.CRITICAL}
        }
        
        self.monitor.index_status = {
            'docs/global/qsm_project_index.md': {'exists': False, 'status': 'missing'}
        }
        
        # 执行被测试方法
        self.monitor.generate_suggestions()
        
        # 验证结果
        self.assertGreater(len(self.monitor.suggestions), 0)
        
        # 应该有CPU、内存、磁盘、模型和索引相关的建议
        suggestion_messages = [s['message'] for s in self.monitor.suggestions]
        self.assertTrue(any('CPU' in msg for msg in suggestion_messages))
        self.assertTrue(any('内存' in msg for msg in suggestion_messages))
        self.assertTrue(any('磁盘' in msg for msg in suggestion_messages))
        self.assertTrue(any('SOM' in msg for msg in suggestion_messages))
        self.assertTrue(any('索引' in msg for msg in suggestion_messages))


if __name__ == '__main__':
    unittest.main() 

"""

"""
量子基因编码: QE-TES-DA5BA7143326
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
