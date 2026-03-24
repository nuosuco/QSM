#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统启动器
统一入口点，启动和管理所有量子模块

功能：
1. 系统初始化
2. 模块加载
3. 健康检查
4. 服务启动
"""

import sys
import os
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')

# 模块可用性检查
MODULES_AVAILABLE = {}
try:
    import quantum_simulator_integration as qsi
    MODULES_AVAILABLE['simulator'] = True
except ImportError:
    MODULES_AVAILABLE['simulator'] = False

try:
    import quantum_model_integration as qmi
    MODULES_AVAILABLE['model_integration'] = True
except ImportError:
    MODULES_AVAILABLE['model_integration'] = False

try:
    import quantum_integration_test as qit
    MODULES_AVAILABLE['integration_test'] = True
except ImportError:
    MODULES_AVAILABLE['integration_test'] = False

try:
    import quantum_doc_generator as qdg
    MODULES_AVAILABLE['doc_generator'] = True
except ImportError:
    MODULES_AVAILABLE['doc_generator'] = False


class QuantumSystemLauncher:
    """量子系统启动器"""
    
    def __init__(self):
        self.modules = {}
        self.status = {
            'initialized': False,
            'start_time': None,
            'modules_loaded': [],
            'errors': []
        }
    
    def initialize(self) -> Dict:
        """初始化系统"""
        print("=" * 70)
        print("QSM量子系统启动器")
        print("=" * 70)
        print(f"启动时间: {datetime.now().isoformat()}")
        
        self.status['start_time'] = time.time()
        
        # 检查Python版本
        print(f"\nPython版本: {sys.version}")
        
        # 检查Qiskit
        try:
            import qiskit
            print(f"Qiskit版本: {qiskit.__version__}")
        except ImportError:
            print("警告: Qiskit未安装，部分功能不可用")
        
        # 加载模块
        print("\n加载模块...")
        
        loaded_count = 0
        for module_name, available in MODULES_AVAILABLE.items():
            if available:
                print(f"  ✅ {module_name}")
                loaded_count += 1
            else:
                print(f"  ❌ {module_name}")
        
        print(f"\n模块加载完成: {loaded_count}/{len(MODULES_AVAILABLE)}")
        
        self.status['initialized'] = True
        self.status['modules_loaded'] = [k for k, v in MODULES_AVAILABLE.items() if v]
        
        return self.status
    
    def run_tests(self) -> Dict:
        """运行测试"""
        print("\n" + "=" * 70)
        print("运行集成测试...")
        print("=" * 70)
        
        if not MODULES_AVAILABLE.get('integration_test'):
            print("错误: 集成测试模块不可用")
            return {'status': 'error', 'error': 'integration_test module not available'}
        
        try:
            results = qit.run_integration_tests()
            return results
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def generate_docs(self) -> Dict:
        """生成文档"""
        print("\n" + "=" * 70)
        print("生成文档...")
        print("=" * 70)
        
        if not MODULES_AVAILABLE.get('doc_generator'):
            print("错误: 文档生成器不可用")
            return {'status': 'error', 'error': 'doc_generator module not available'}
        
        try:
            results = qdg.generate_documentation()
            return results
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def run_demo(self, module_name: str = 'all') -> Dict:
        """运行演示"""
        print("\n" + "=" * 70)
        print(f"运行演示: {module_name}")
        print("=" * 70)
        
        results = {'module': module_name, 'status': 'unknown'}
        
        if module_name == 'simulator' or module_name == 'all':
            if MODULES_AVAILABLE.get('simulator'):
                try:
                    integration = qsi.QuantumSimulatorIntegration()
                    integration.initialize()
                    demo_result = integration.run_all_tests()
                    results['simulator'] = demo_result
                    print("✅ 模拟器演示完成")
                except Exception as e:
                    results['simulator_error'] = str(e)
                    print(f"❌ 模拟器演示失败: {e}")
        
        if module_name == 'model_integration' or module_name == 'all':
            if MODULES_AVAILABLE.get('model_integration'):
                try:
                    integration = qmi.QuantumFourModelIntegration()
                    integration.initialize()
                    task_result = integration.run_integrated_task({'query': 'demo'})
                    results['model_integration'] = task_result
                    print("✅ 四模型集成演示完成")
                except Exception as e:
                    results['model_integration_error'] = str(e)
                    print(f"❌ 四模型集成演示失败: {e}")
        
        results['status'] = 'completed'
        return results
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'initialized': self.status['initialized'],
            'uptime_seconds': time.time() - self.status['start_time'] if self.status['start_time'] else 0,
            'modules_available': MODULES_AVAILABLE,
            'modules_loaded': self.status['modules_loaded'],
            'errors': self.status['errors']
        }
    
    def shutdown(self) -> Dict:
        """关闭系统"""
        print("\n关闭量子系统...")
        
        self.status['initialized'] = False
        
        print("系统已关闭")
        
        return {
            'status': 'shutdown',
            'uptime': time.time() - self.status['start_time'] if self.status['start_time'] else 0
        }


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='QSM量子系统启动器')
    parser.add_argument('--init', action='store_true', help='初始化系统')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--docs', action='store_true', help='生成文档')
    parser.add_argument('--demo', type=str, default=None, help='运行演示 (all/simulator/model_integration)')
    parser.add_argument('--status', action='store_true', help='显示状态')
    parser.add_argument('--all', action='store_true', help='执行所有操作')
    
    args = parser.parse_args()
    
    launcher = QuantumSystemLauncher()
    
    if args.all:
        launcher.initialize()
        launcher.run_tests()
        launcher.generate_docs()
        launcher.run_demo()
        launcher.get_status()
        return
    
    if args.init or not any([args.test, args.docs, args.demo, args.status]):
        launcher.initialize()
    
    if args.test:
        launcher.run_tests()
    
    if args.docs:
        launcher.generate_docs()
    
    if args.demo:
        launcher.run_demo(args.demo)
    
    if args.status:
        status = launcher.get_status()
        print("\n" + "=" * 70)
        print("系统状态")
        print("=" * 70)
        for key, value in status.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
