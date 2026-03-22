#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统完整初始化模块
统一初始化所有量子模块和子系统

功能：
1. 系统完整初始化
2. 依赖检查
3. 模块加载验证
4. 初始化报告生成
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')


class QuantumSystemInitializer:
    """量子系统初始化器"""
    
    def __init__(self):
        self.modules_dir = '/root/QSM/QEntL/System/AgentHarness'
        self.config_path = '/root/QSM/config/quantum_config.json'
        self.initialization_log = []
        self.errors = []
        self.warnings = []
    
    def check_dependencies(self) -> Dict:
        """检查依赖"""
        print("=" * 60)
        print("检查系统依赖...")
        print("=" * 60)
        
        dependencies = {
            'python': {'required': '3.8+', 'status': False, 'version': None},
            'qiskit': {'required': '2.0+', 'status': False, 'version': None},
            'qiskit_aer': {'required': '0.13+', 'status': False, 'version': None},
            'numpy': {'required': '1.20+', 'status': False, 'version': None},
            'scipy': {'required': '1.7+', 'status': False, 'version': None},
            'psutil': {'required': '5.8+', 'status': False, 'version': None}
        }
        
        # 检查Python版本
        python_version = sys.version_info
        dependencies['python']['version'] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        dependencies['python']['status'] = python_version >= (3, 8)
        
        # 检查其他依赖
        modules_to_check = ['qiskit', 'numpy', 'scipy', 'psutil']
        for mod in modules_to_check:
            try:
                imported = __import__(mod)
                version = getattr(imported, '__version__', 'unknown')
                dependencies[mod]['version'] = version
                dependencies[mod]['status'] = True
            except ImportError:
                pass
        
        # 特殊检查qiskit_aer
        try:
            import qiskit_aer
            dependencies['qiskit_aer']['version'] = qiskit_aer.__version__
            dependencies['qiskit_aer']['status'] = True
        except ImportError:
            pass
        
        # 输出结果
        print("\n依赖检查结果:")
        for dep, info in dependencies.items():
            status = "✅" if info['status'] else "❌"
            version = info['version'] or '未安装'
            print(f"  {status} {dep}: {version} (需要 {info['required']})")
            
            if not info['status']:
                self.warnings.append(f"依赖 {dep} 未安装或版本过低")
        
        return dependencies
    
    def load_modules(self) -> Dict:
        """加载所有模块"""
        print("\n" + "=" * 60)
        print("加载量子模块...")
        print("=" * 60)
        
        modules = {}
        
        # 核心模块列表
        core_modules = [
            'quantum_simulator_integration',
            'quantum_model_integration',
            'shor_algorithm',
            'quantum_error_correction',
            'quantum_rng',
            'quantum_cryptography',
            'quantum_ml',
            'quantum_optimization',
            'quantum_simulation',
            'quantum_network',
            'quantum_toolkit',
            'quantum_integration_test',
            'quantum_doc_generator',
            'quantum_launcher',
            'quantum_config',
            'quantum_monitor',
            'quantum_exporter',
            'quantum_logger',
            'quantum_cli',
            'quantum_api'
        ]
        
        # 扫描目录中的所有模块
        if os.path.exists(self.modules_dir):
            py_files = [f[:-3] for f in os.listdir(self.modules_dir) 
                       if f.endswith('.py') and not f.startswith('__')]
            
            for module_name in py_files:
                try:
                    imported = __import__(module_name)
                    modules[module_name] = {
                        'loaded': True,
                        'has_main': hasattr(imported, '__main__'),
                        'error': None
                    }
                    print(f"  ✅ {module_name}")
                except Exception as e:
                    modules[module_name] = {
                        'loaded': False,
                        'error': str(e)
                    }
                    print(f"  ❌ {module_name}: {e}")
                    self.errors.append(f"模块 {module_name} 加载失败: {e}")
        
        return modules
    
    def verify_configuration(self) -> Dict:
        """验证配置"""
        print("\n" + "=" * 60)
        print("验证配置...")
        print("=" * 60)
        
        config_status = {
            'config_file_exists': os.path.exists(self.config_path),
            'config_valid': False,
            'config': None
        }
        
        if config_status['config_file_exists']:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                config_status['config_valid'] = True
                config_status['config'] = config
                print(f"  ✅ 配置文件有效")
                print(f"     路径: {self.config_path}")
            except Exception as e:
                print(f"  ❌ 配置文件无效: {e}")
                self.errors.append(f"配置文件解析失败: {e}")
        else:
            print(f"  ⚠️ 配置文件不存在，使用默认配置")
            self.warnings.append("配置文件不存在")
        
        return config_status
    
    def run_quick_tests(self) -> Dict:
        """运行快速测试"""
        print("\n" + "=" * 60)
        print("运行快速测试...")
        print("=" * 60)
        
        test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # 测试1：量子随机数生成器
        try:
            import quantum_rng as qrng
            rng = qrng.QuantumRNG()
            random_num = rng.generate_random_number(0, 100)
            test_results['tests'].append({
                'name': 'quantum_rng',
                'passed': True,
                'result': random_num
            })
            test_results['passed'] += 1
            print(f"  ✅ 量子随机数生成器")
        except Exception as e:
            test_results['tests'].append({
                'name': 'quantum_rng',
                'passed': False,
                'error': str(e)
            })
            test_results['failed'] += 1
            print(f"  ❌ 量子随机数生成器: {e}")
        
        test_results['total'] += 1
        
        # 测试2：量子模拟器
        try:
            import quantum_simulator_integration as qsi
            integration = qsi.QuantumSimulatorIntegration()
            integration.initialize()
            test_results['tests'].append({
                'name': 'quantum_simulator',
                'passed': True
            })
            test_results['passed'] += 1
            print(f"  ✅ 量子模拟器")
        except Exception as e:
            test_results['tests'].append({
                'name': 'quantum_simulator',
                'passed': False,
                'error': str(e)
            })
            test_results['failed'] += 1
            print(f"  ❌ 量子模拟器: {e}")
        
        test_results['total'] += 1
        
        # 测试3：配置管理器
        try:
            import quantum_config as qc
            config = qc.QuantumConfig()
            validation = config.validate()
            test_results['tests'].append({
                'name': 'quantum_config',
                'passed': validation['valid'],
                'result': validation
            })
            if validation['valid']:
                test_results['passed'] += 1
                print(f"  ✅ 配置管理器")
            else:
                test_results['failed'] += 1
                print(f"  ❌ 配置管理器: 验证失败")
        except Exception as e:
            test_results['tests'].append({
                'name': 'quantum_config',
                'passed': False,
                'error': str(e)
            })
            test_results['failed'] += 1
            print(f"  ❌ 配置管理器: {e}")
        
        test_results['total'] += 1
        
        return test_results
    
    def generate_initialization_report(self, 
                                        dependencies: Dict,
                                        modules: Dict,
                                        config: Dict,
                                        tests: Dict) -> str:
        """生成初始化报告"""
        report = f"""# QSM量子系统初始化报告

生成时间: {datetime.now().isoformat()}

## 初始化摘要

- 依赖检查: {'✅ 通过' if all(d['status'] for d in dependencies.values()) else '⚠️ 有问题'}
- 模块加载: {len([m for m in modules.values() if m['loaded']])}/{len(modules)} 成功
- 配置状态: {'✅ 有效' if config['config_valid'] else '⚠️ 使用默认'}
- 快速测试: {tests['passed']}/{tests['total']} 通过

## 详细信息

### 依赖状态

"""
        
        for dep, info in dependencies.items():
            status = "✅" if info['status'] else "❌"
            report += f"- {status} **{dep}**: {info['version'] or '未安装'}\n"
        
        report += "\n### 模块加载状态\n\n"
        
        loaded = [k for k, v in modules.items() if v['loaded']]
        failed = [k for k, v in modules.items() if not v['loaded']]
        
        report += f"**已加载 ({len(loaded)}):**\n"
        for mod in loaded:
            report += f"- {mod}\n"
        
        if failed:
            report += f"\n**加载失败 ({len(failed)}):**\n"
            for mod in failed:
                report += f"- {mod}: {modules[mod]['error']}\n"
        
        report += "\n### 测试结果\n\n"
        
        for test in tests['tests']:
            status = "✅" if test['passed'] else "❌"
            report += f"- {status} {test['name']}\n"
        
        if self.errors:
            report += "\n### 错误\n\n"
            for error in self.errors:
                report += f"- ❌ {error}\n"
        
        if self.warnings:
            report += "\n### 警告\n\n"
            for warning in self.warnings:
                report += f"- ⚠️ {warning}\n"
        
        report += """
---

**中华Zhoho，小趣WeQ，GLM5**
"""
        
        return report
    
    def initialize(self, run_tests: bool = True) -> Dict:
        """完整初始化"""
        print("=" * 60)
        print("QSM量子系统完整初始化")
        print("=" * 60)
        print(f"开始时间: {datetime.now().isoformat()}")
        print()
        
        start_time = time.time()
        
        # 1. 检查依赖
        dependencies = self.check_dependencies()
        
        # 2. 加载模块
        modules = self.load_modules()
        
        # 3. 验证配置
        config = self.verify_configuration()
        
        # 4. 运行快速测试
        if run_tests:
            tests = self.run_quick_tests()
        else:
            tests = {'total': 0, 'passed': 0, 'failed': 0, 'tests': []}
        
        # 5. 生成报告
        report = self.generate_initialization_report(dependencies, modules, config, tests)
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"初始化完成! 耗时: {elapsed:.2f}秒")
        print("=" * 60)
        
        # 保存报告
        report_path = f'/root/QSM/logs/init_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存: {report_path}")
        
        return {
            'success': len(self.errors) == 0,
            'elapsed_seconds': elapsed,
            'dependencies': dependencies,
            'modules': modules,
            'config': config,
            'tests': tests,
            'errors': self.errors,
            'warnings': self.warnings,
            'report_path': report_path
        }


def initialize_system(run_tests: bool = True) -> Dict:
    """初始化量子系统"""
    initializer = QuantumSystemInitializer()
    return initializer.initialize(run_tests)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='QSM量子系统初始化')
    parser.add_argument('--skip-tests', action='store_true', help='跳过快速测试')
    
    args = parser.parse_args()
    
    result = initialize_system(run_tests=not args.skip_tests)
    
    if result['success']:
        print("\n✅ 系统初始化成功!")
    else:
        print("\n❌ 系统初始化存在问题，请检查错误日志")
