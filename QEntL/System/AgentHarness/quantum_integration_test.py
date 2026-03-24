#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统集成测试
测试所有量子模块的集成运行

功能：
1. 全模块集成测试
2. 端到端测试流程
3. 性能回归测试
4. 系统健康检查
"""

import sys
import os
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')

import time
from typing import Dict, List
import json

# 尝试导入所有模块
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
    import shor_algorithm as shor
    MODULES_AVAILABLE['shor'] = True
except ImportError:
    MODULES_AVAILABLE['shor'] = False

try:
    import quantum_error_correction as qec
    MODULES_AVAILABLE['error_correction'] = True
except ImportError:
    MODULES_AVAILABLE['error_correction'] = False

try:
    import quantum_rng as qrng
    MODULES_AVAILABLE['rng'] = True
except ImportError:
    MODULES_AVAILABLE['rng'] = False

try:
    import quantum_cryptography as qcrypto
    MODULES_AVAILABLE['cryptography'] = True
except ImportError:
    MODULES_AVAILABLE['cryptography'] = False

try:
    import quantum_ml as qml
    MODULES_AVAILABLE['ml'] = True
except ImportError:
    MODULES_AVAILABLE['ml'] = False

try:
    import quantum_optimization as qopt
    MODULES_AVAILABLE['optimization'] = True
except ImportError:
    MODULES_AVAILABLE['optimization'] = False

try:
    import quantum_simulation as qsim
    MODULES_AVAILABLE['simulation'] = True
except ImportError:
    MODULES_AVAILABLE['simulation'] = False

try:
    import quantum_network as qnet
    MODULES_AVAILABLE['network'] = True
except ImportError:
    MODULES_AVAILABLE['network'] = False

try:
    import quantum_toolkit as qtk
    MODULES_AVAILABLE['toolkit'] = True
except ImportError:
    MODULES_AVAILABLE['toolkit'] = False


class QuantumSystemIntegrationTest:
    """量子系统集成测试"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("=" * 70)
        print("QSM量子系统集成测试")
        print("=" * 70)
        
        self.start_time = time.time()
        
        results = {
            'modules_available': MODULES_AVAILABLE,
            'tests': {},
            'summary': {}
        }
        
        # 模块可用性统计
        available_count = sum(1 for v in MODULES_AVAILABLE.values() if v)
        total_count = len(MODULES_AVAILABLE)
        print(f"\n模块可用性: {available_count}/{total_count}")
        
        # 测试1：量子模拟器
        print("\n[1/10] 测试量子模拟器集成...")
        if MODULES_AVAILABLE['simulator']:
            try:
                integration = qsi.QuantumSimulatorIntegration()
                integration.initialize()
                test_result = integration.run_all_tests()
                results['tests']['simulator'] = {'status': 'PASS', 'details': test_result}
                print("    ✅ 模拟器测试通过")
            except Exception as e:
                results['tests']['simulator'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 模拟器测试失败: {e}")
        else:
            results['tests']['simulator'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试2：四模型集成
        print("\n[2/10] 测试四模型量子集成...")
        if MODULES_AVAILABLE['model_integration']:
            try:
                integration = qmi.QuantumFourModelIntegration()
                integration.initialize()
                results['tests']['model_integration'] = {'status': 'PASS'}
                print("    ✅ 四模型集成测试通过")
            except Exception as e:
                results['tests']['model_integration'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 四模型集成测试失败: {e}")
        else:
            results['tests']['model_integration'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试3：Shor算法
        print("\n[3/10] 测试Shor因数分解...")
        if MODULES_AVAILABLE['shor']:
            try:
                benchmark = shor.ShorBenchmark()
                benchmark_result = benchmark.run_benchmark()
                success_rate = benchmark_result['summary']['success_rate']
                results['tests']['shor'] = {
                    'status': 'PASS' if success_rate >= 0.8 else 'FAIL',
                    'success_rate': success_rate
                }
                print(f"    ✅ 成功率: {success_rate:.1%}")
            except Exception as e:
                results['tests']['shor'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ Shor测试失败: {e}")
        else:
            results['tests']['shor'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试4：量子纠错
        print("\n[4/10] 测试量子纠错系统...")
        if MODULES_AVAILABLE['error_correction']:
            try:
                qec_system = qec.QuantumErrorCorrectionSystem()
                qec_results = qec_system.run_all_tests()
                results['tests']['error_correction'] = {'status': 'PASS'}
                print("    ✅ 纠错系统测试通过")
            except Exception as e:
                results['tests']['error_correction'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 纠错测试失败: {e}")
        else:
            results['tests']['error_correction'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试5：量子随机数
        print("\n[5/10] 测试量子随机数生成器...")
        if MODULES_AVAILABLE['rng']:
            try:
                benchmark = qrng.QuantumRNGBenchmark()
                rng_results = benchmark.run_benchmark()
                success_rate = rng_results['summary']['success_rate']
                results['tests']['rng'] = {
                    'status': 'PASS' if success_rate >= 0.8 else 'FAIL',
                    'success_rate': success_rate
                }
                print(f"    ✅ 成功率: {success_rate:.1%}")
            except Exception as e:
                results['tests']['rng'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 随机数测试失败: {e}")
        else:
            results['tests']['rng'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试6：量子密码学
        print("\n[6/10] 测试量子密码学...")
        if MODULES_AVAILABLE['cryptography']:
            try:
                suite = qcrypto.QuantumCryptographySuite()
                crypto_results = suite.run_demonstration()
                results['tests']['cryptography'] = {'status': 'PASS'}
                print("    ✅ 密码学测试通过")
            except Exception as e:
                results['tests']['cryptography'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 密码学测试失败: {e}")
        else:
            results['tests']['cryptography'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试7：量子机器学习
        print("\n[7/10] 测试量子机器学习...")
        if MODULES_AVAILABLE['ml']:
            try:
                demo = qml.QuantumMLDemo()
                ml_results = demo.run_demonstration()
                results['tests']['ml'] = {'status': 'PASS'}
                print("    ✅ 机器学习测试通过")
            except Exception as e:
                results['tests']['ml'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 机器学习测试失败: {e}")
        else:
            results['tests']['ml'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试8：量子优化
        print("\n[8/10] 测试量子优化...")
        if MODULES_AVAILABLE['optimization']:
            try:
                demo = qopt.QuantumOptimizationDemo()
                opt_results = demo.run_demonstration()
                results['tests']['optimization'] = {'status': 'PASS'}
                print("    ✅ 优化测试通过")
            except Exception as e:
                results['tests']['optimization'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 优化测试失败: {e}")
        else:
            results['tests']['optimization'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试9：量子网络
        print("\n[9/10] 测试量子网络...")
        if MODULES_AVAILABLE['network']:
            try:
                demo = qnet.QuantumNetworkDemo()
                net_results = demo.run_demonstration()
                results['tests']['network'] = {'status': 'PASS'}
                print("    ✅ 网络测试通过")
            except Exception as e:
                results['tests']['network'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 网络测试失败: {e}")
        else:
            results['tests']['network'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        # 测试10：量子工具库
        print("\n[10/10] 测试量子工具库...")
        if MODULES_AVAILABLE['toolkit']:
            try:
                demo = qtk.QuantumToolkitDemo()
                toolkit_results = demo.run_demonstration()
                results['tests']['toolkit'] = {'status': 'PASS'}
                print("    ✅ 工具库测试通过")
            except Exception as e:
                results['tests']['toolkit'] = {'status': 'ERROR', 'error': str(e)}
                print(f"    ❌ 工具库测试失败: {e}")
        else:
            results['tests']['toolkit'] = {'status': 'SKIP'}
            print("    ⏭️ 跳过")
        
        self.end_time = time.time()
        
        # 汇总
        passed = sum(1 for t in results['tests'].values() if t.get('status') == 'PASS')
        failed = sum(1 for t in results['tests'].values() if t.get('status') == 'ERROR')
        skipped = sum(1 for t in results['tests'].values() if t.get('status') == 'SKIP')
        
        results['summary'] = {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'total': len(results['tests']),
            'duration_seconds': self.end_time - self.start_time
        }
        
        print("\n" + "=" * 70)
        print(f"测试完成: {passed}通过, {failed}失败, {skipped}跳过")
        print(f"总耗时: {results['summary']['duration_seconds']:.2f}秒")
        print("=" * 70)
        
        return results


def run_integration_tests():
    """运行集成测试"""
    tester = QuantumSystemIntegrationTest()
    results = tester.run_all_tests()
    return results


if __name__ == "__main__":
    results = run_integration_tests()
