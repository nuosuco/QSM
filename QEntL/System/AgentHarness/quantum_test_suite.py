#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统完整测试套件
全面的系统测试和验证

功能：
1. 模块导入测试
2. 功能验证测试
3. 性能基准测试
4. 完整性检查
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')


class QuantumTestSuite:
    """量子系统完整测试套件"""
    
    def __init__(self):
        self.results = {
            'start_time': None,
            'end_time': None,
            'tests': {},
            'summary': {}
        }
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("=" * 70)
        print("QSM量子系统完整测试套件")
        print("=" * 70)
        print(f"开始时间: {datetime.now().isoformat()}")
        print()
        
        self.results['start_time'] = time.time()
        
        # 1. 模块导入测试
        self._test_module_imports()
        
        # 2. 量子算法测试
        self._test_quantum_algorithms()
        
        # 3. 系统基础设施测试
        self._test_infrastructure()
        
        # 4. 集成测试
        self._test_integration()
        
        self.results['end_time'] = time.time()
        
        # 生成汇总
        self._generate_summary()
        
        return self.results
    
    def _test_module_imports(self) -> None:
        """测试模块导入"""
        print("\n" + "-" * 70)
        print("模块导入测试")
        print("-" * 70)
        
        modules = [
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
            'quantum_api',
            'quantum_initializer',
            'quantum_packager',
            'quantum_summary',
            'quantum_version',
            'quantum_main'
        ]
        
        for mod in modules:
            test_name = f"import_{mod}"
            try:
                __import__(mod)
                self._record_pass(test_name)
                print(f"  ✅ {mod}")
            except ImportError as e:
                self._record_fail(test_name, str(e))
                print(f"  ❌ {mod}: {e}")
    
    def _test_quantum_algorithms(self) -> None:
        """测试量子算法"""
        print("\n" + "-" * 70)
        print("量子算法测试")
        print("-" * 70)
        
        # Grover测试
        try:
            import quantum_simulator_integration as qsi
            integration = qsi.QuantumSimulatorIntegration()
            integration.initialize()
            result = integration.run_grover_search(5)
            if result.get('found'):
                self._record_pass('grover_search')
                print(f"  ✅ Grover搜索")
            else:
                self._record_fail('grover_search', '未找到目标')
                print(f"  ❌ Grover搜索: 未找到目标")
        except Exception as e:
            self._record_fail('grover_search', str(e))
            print(f"  ❌ Grover搜索: {e}")
        
        # Shor测试
        try:
            import shor_algorithm as shor
            shor_instance = shor.ShorAlgorithm()
            result = shor_instance.factorize(15)
            if result.get('factors'):
                self._record_pass('shor_algorithm')
                print(f"  ✅ Shor因数分解")
            else:
                self._record_fail('shor_algorithm', '未找到因子')
                print(f"  ❌ Shor因数分解: 未找到因子")
        except Exception as e:
            self._record_fail('shor_algorithm', str(e))
            print(f"  ❌ Shor因数分解: {e}")
        
        # RNG测试
        try:
            import quantum_rng as qrng
            rng = qrng.QuantumRNG()
            num = rng.generate_int(0, 100)
            if 0 <= num <= 100:
                self._record_pass('quantum_rng')
                print(f"  ✅ 量子随机数生成器")
            else:
                self._record_fail('quantum_rng', '数值超出范围')
                print(f"  ❌ 量子随机数生成器: 数值超出范围")
        except Exception as e:
            self._record_fail('quantum_rng', str(e))
            print(f"  ❌ 量子随机数生成器: {e}")
    
    def _test_infrastructure(self) -> None:
        """测试基础设施"""
        print("\n" + "-" * 70)
        print("基础设施测试")
        print("-" * 70)
        
        # 配置管理器
        try:
            import quantum_config as qc
            config = qc.QuantumConfig()
            validation = config.validate()
            if validation['valid']:
                self._record_pass('config_manager')
                print(f"  ✅ 配置管理器")
            else:
                self._record_fail('config_manager', validation.get('errors', []))
                print(f"  ❌ 配置管理器: 验证失败")
        except Exception as e:
            self._record_fail('config_manager', str(e))
            print(f"  ❌ 配置管理器: {e}")
        
        # 日志记录器
        try:
            import quantum_logger as ql
            logger = ql.QuantumLogger(name="TestLogger", console_output=False)
            logger.info("测试日志")
            self._record_pass('logger')
            print(f"  ✅ 日志记录器")
        except Exception as e:
            self._record_fail('logger', str(e))
            print(f"  ❌ 日志记录器: {e}")
        
        # 版本管理器
        try:
            import quantum_version as qv
            manager = qv.QuantumVersionManager()
            version = manager.get_version_string()
            if version:
                self._record_pass('version_manager')
                print(f"  ✅ 版本管理器 (v{version})")
            else:
                self._record_fail('version_manager', '无法获取版本')
                print(f"  ❌ 版本管理器: 无法获取版本")
        except Exception as e:
            self._record_fail('version_manager', str(e))
            print(f"  ❌ 版本管理器: {e}")
    
    def _test_integration(self) -> None:
        """测试集成"""
        print("\n" + "-" * 70)
        print("集成测试")
        print("-" * 70)
        
        # 主入口测试
        try:
            import quantum_main as qm
            q = qm.get_quantum()
            status = q.get_status()
            if status.get('version'):
                self._record_pass('main_entry')
                print(f"  ✅ 主入口模块")
            else:
                self._record_fail('main_entry', '状态无效')
                print(f"  ❌ 主入口模块: 状态无效")
        except Exception as e:
            self._record_fail('main_entry', str(e))
            print(f"  ❌ 主入口模块: {e}")
        
        # 初始化器测试
        try:
            import quantum_initializer as qi
            initializer = qi.QuantumSystemInitializer()
            result = initializer.check_dependencies()
            if result.get('python', {}).get('status'):
                self._record_pass('initializer')
                print(f"  ✅ 系统初始化器")
            else:
                self._record_fail('initializer', '依赖检查失败')
                print(f"  ❌ 系统初始化器: 依赖检查失败")
        except Exception as e:
            self._record_fail('initializer', str(e))
            print(f"  ❌ 系统初始化器: {e}")
    
    def _record_pass(self, test_name: str) -> None:
        """记录通过"""
        self.results['tests'][test_name] = {'status': 'PASS'}
        self.passed += 1
    
    def _record_fail(self, test_name: str, error: any) -> None:
        """记录失败"""
        self.results['tests'][test_name] = {'status': 'FAIL', 'error': str(error)}
        self.failed += 1
    
    def _record_skip(self, test_name: str, reason: str) -> None:
        """记录跳过"""
        self.results['tests'][test_name] = {'status': 'SKIP', 'reason': reason}
        self.skipped += 1
    
    def _generate_summary(self) -> None:
        """生成汇总"""
        duration = self.results['end_time'] - self.results['start_time']
        
        self.results['summary'] = {
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'total': self.passed + self.failed + self.skipped,
            'duration_seconds': round(duration, 2),
            'success_rate': round(self.passed / max(self.passed + self.failed, 1) * 100, 1)
        }
        
        print("\n" + "=" * 70)
        print("测试汇总")
        print("=" * 70)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"跳过: {self.skipped}")
        print(f"总计: {self.results['summary']['total']}")
        print(f"成功率: {self.results['summary']['success_rate']}%")
        print(f"耗时: {self.results['summary']['duration_seconds']}秒")
        print("=" * 70)


def run_full_test_suite():
    """运行完整测试套件"""
    suite = QuantumTestSuite()
    return suite.run_all_tests()


if __name__ == "__main__":
    results = run_full_test_suite()
    
    # 保存结果
    output_dir = '/root/QSM/results'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存: {output_file}")
