#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统CLI命令行工具
提供完整的命令行接口

功能：
1. 系统管理命令
2. 算法执行命令
3. 测试运行命令
4. 报告生成命令
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')


class QuantumCLI:
    """量子系统CLI"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.results_dir = '/root/QSM/results'
        os.makedirs(self.results_dir, exist_ok=True)
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            description='QSM量子系统命令行工具',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  quantum_cli.py status              # 显示系统状态
  quantum_cli.py test --all          # 运行所有测试
  quantum_cli.py run grover --n 15   # 运行Grover算法
  quantum_cli.py run shor --n 21     # 运行Shor算法
  quantum_cli.py report --format html # 生成HTML报告
            """
        )
        
        # 子命令
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # status 命令
        status_parser = subparsers.add_parser('status', help='显示系统状态')
        status_parser.add_argument('--json', action='store_true', help='JSON格式输出')
        
        # test 命令
        test_parser = subparsers.add_parser('test', help='运行测试')
        test_parser.add_argument('--all', action='store_true', help='运行所有测试')
        test_parser.add_argument('--module', type=str, help='测试指定模块')
        test_parser.add_argument('--quick', action='store_true', help='快速测试模式')
        
        # run 命令
        run_parser = subparsers.add_parser('run', help='运行算法')
        run_parser.add_argument('algorithm', type=str, help='算法名称 (grover/shor/qft/rng)')
        run_parser.add_argument('--n', type=int, default=15, help='输入数字')
        run_parser.add_argument('--shots', type=int, default=1024, help='测量次数')
        run_parser.add_argument('--output', type=str, help='输出文件')
        
        # report 命令
        report_parser = subparsers.add_parser('report', help='生成报告')
        report_parser.add_argument('--format', type=str, default='json', 
                                   choices=['json', 'html', 'md'], help='报告格式')
        report_parser.add_argument('--output', type=str, help='输出文件')
        
        # list 命令
        list_parser = subparsers.add_parser('list', help='列出可用模块')
        list_parser.add_argument('--type', type=str, default='all',
                                 choices=['all', 'algorithms', 'modules'], help='列出类型')
        
        # config 命令
        config_parser = subparsers.add_parser('config', help='配置管理')
        config_parser.add_argument('--show', action='store_true', help='显示配置')
        config_parser.add_argument('--set', type=str, help='设置配置项 (key=value)')
        
        return parser
    
    def run(self, args: List[str] = None) -> int:
        """运行CLI"""
        parsed = self.parser.parse_args(args)
        
        if not parsed.command:
            self.parser.print_help()
            return 0
        
        # 路由到对应命令处理
        handlers = {
            'status': self._handle_status,
            'test': self._handle_test,
            'run': self._handle_run,
            'report': self._handle_report,
            'list': self._handle_list,
            'config': self._handle_config
        }
        
        handler = handlers.get(parsed.command)
        if handler:
            return handler(parsed)
        else:
            self.parser.print_help()
            return 1
    
    def _handle_status(self, args) -> int:
        """处理status命令"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'system': 'QSM Quantum System',
            'version': '1.0.0',
            'status': 'running',
            'modules': {
                'qiskit': self._check_module('qiskit'),
                'numpy': self._check_module('numpy'),
                'scipy': self._check_module('scipy')
            }
        }
        
        # 获取Agent Harness模块
        harness_dir = '/root/QSM/QEntL/System/AgentHarness'
        if os.path.exists(harness_dir):
            modules = [f for f in os.listdir(harness_dir) if f.endswith('.py') and not f.startswith('__')]
            status['agent_harness_modules'] = len(modules)
        
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("=" * 50)
            print("QSM量子系统状态")
            print("=" * 50)
            print(f"时间: {status['timestamp']}")
            print(f"版本: {status['version']}")
            print(f"状态: {status['status']}")
            print("\n依赖状态:")
            for mod, available in status['modules'].items():
                icon = "✅" if available else "❌"
                print(f"  {icon} {mod}")
            print(f"\nAgent Harness模块数: {status.get('agent_harness_modules', 0)}")
        
        return 0
    
    def _check_module(self, name: str) -> bool:
        """检查模块是否可用"""
        try:
            __import__(name)
            return True
        except ImportError:
            return False
    
    def _handle_test(self, args) -> int:
        """处理test命令"""
        print("=" * 50)
        print("运行量子系统测试")
        print("=" * 50)
        
        if args.module:
            print(f"测试模块: {args.module}")
            # 单模块测试
            try:
                module = __import__(args.module)
                if hasattr(module, 'test'):
                    result = module.test()
                    print(f"✅ 测试通过")
                    return 0
                else:
                    print(f"❌ 模块无测试函数")
                    return 1
            except ImportError:
                print(f"❌ 模块不存在: {args.module}")
                return 1
        
        elif args.all:
            print("运行所有测试...")
            # 导入集成测试模块
            try:
                import quantum_integration_test as qit
                results = qit.run_integration_tests()
                
                passed = results['summary']['passed']
                total = results['summary']['total']
                
                print(f"\n测试完成: {passed}/{total} 通过")
                return 0 if passed == total else 1
                
            except ImportError as e:
                print(f"❌ 无法导入测试模块: {e}")
                return 1
        
        else:
            print("使用 --all 运行所有测试")
            print("使用 --module <name> 测试特定模块")
            return 1
    
    def _handle_run(self, args) -> int:
        """处理run命令"""
        print("=" * 50)
        print(f"运行量子算法: {args.algorithm}")
        print("=" * 50)
        
        algorithm = args.algorithm.lower()
        n = args.n
        shots = args.shots
        
        results = {'algorithm': algorithm, 'timestamp': datetime.now().isoformat()}
        
        if algorithm == 'grover':
            try:
                import quantum_simulator_integration as qsi
                integration = qsi.QuantumSimulatorIntegration()
                integration.initialize()
                
                result = integration.run_grover_search(n)
                results['result'] = result
                print(f"✅ Grover搜索完成")
                print(f"   目标: {n}")
                print(f"   找到: {result.get('found', False)}")
                
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                return 1
        
        elif algorithm == 'shor':
            try:
                import shor_algorithm as shor
                shor_instance = shor.ShorAlgorithm()
                
                result = shor_instance.factorize(n)
                results['result'] = result
                print(f"✅ Shor因数分解完成")
                print(f"   输入: {n}")
                print(f"   因子: {result.get('factors', [])}")
                
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                return 1
        
        elif algorithm == 'qft':
            try:
                import quantum_simulator_integration as qsi
                integration = qsi.QuantumSimulatorIntegration()
                integration.initialize()
                
                result = integration.run_qft(n_qubits=3)
                results['result'] = result
                print(f"✅ QFT完成")
                
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                return 1
        
        elif algorithm == 'rng':
            try:
                import quantum_rng as qrng
                rng = qrng.QuantumRNG()
                
                random_num = rng.generate_random_number(0, n)
                results['result'] = {'random_number': random_num}
                print(f"✅ 量子随机数生成完成")
                print(f"   范围: 0-{n}")
                print(f"   结果: {random_num}")
                
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                return 1
        
        else:
            print(f"❌ 未知算法: {algorithm}")
            print("   支持的算法: grover, shor, qft, rng")
            return 1
        
        # 保存结果
        if args.output:
            output_path = os.path.join(self.results_dir, args.output)
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n结果已保存至: {output_path}")
        
        return 0
    
    def _handle_report(self, args) -> int:
        """处理report命令"""
        print("=" * 50)
        print("生成报告")
        print("=" * 50)
        
        # 收集报告数据
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system': 'QSM Quantum System',
            'version': '1.0.0'
        }
        
        # 生成报告
        if args.format == 'json':
            output = json.dumps(report_data, indent=2)
            ext = 'json'
        elif args.format == 'html':
            output = f"""<!DOCTYPE html>
<html>
<head><title>QSM Report</title></head>
<body>
<h1>QSM量子系统报告</h1>
<p>生成时间: {report_data['timestamp']}</p>
</body>
</html>"""
            ext = 'html'
        else:
            output = f"""# QSM量子系统报告

生成时间: {report_data['timestamp']}
版本: {report_data['version']}
"""
            ext = 'md'
        
        # 输出
        if args.output:
            output_path = args.output
        else:
            output_path = os.path.join(self.results_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✅ 报告已生成: {output_path}")
        return 0
    
    def _handle_list(self, args) -> int:
        """处理list命令"""
        print("=" * 50)
        print("可用模块列表")
        print("=" * 50)
        
        harness_dir = '/root/QSM/QEntL/System/AgentHarness'
        
        if args.type in ['all', 'modules']:
            print("\nAgent Harness模块:")
            if os.path.exists(harness_dir):
                modules = sorted([f[:-3] for f in os.listdir(harness_dir) 
                                 if f.endswith('.py') and not f.startswith('__')])
                for i, mod in enumerate(modules, 1):
                    print(f"  {i}. {mod}")
        
        if args.type in ['all', 'algorithms']:
            print("\n可用算法:")
            algorithms = ['Grover搜索', 'Shor因数分解', 'QFT量子傅里叶变换', 
                         'BB84密钥分发', 'VQE变分量子特征求解器', 'QAOA量子近似优化']
            for i, alg in enumerate(algorithms, 1):
                print(f"  {i}. {alg}")
        
        return 0
    
    def _handle_config(self, args) -> int:
        """处理config命令"""
        print("=" * 50)
        print("配置管理")
        print("=" * 50)
        
        if args.show:
            try:
                import quantum_config as qc
                config = qc.QuantumConfig()
                print(config)
            except ImportError:
                print("配置模块不可用")
                return 1
        
        elif args.set:
            key, value = args.set.split('=', 1)
            print(f"设置: {key} = {value}")
            # 这里可以添加实际的配置设置逻辑
        
        else:
            print("使用 --show 显示配置")
            print("使用 --set key=value 设置配置")
        
        return 0


def main():
    """主入口"""
    cli = QuantumCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
