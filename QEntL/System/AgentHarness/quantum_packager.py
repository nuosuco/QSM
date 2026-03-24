#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统完整打包器
将量子系统打包为可分发的格式

功能：
1. 系统完整性验证
2. 依赖收集
3. 配置打包
4. 安装脚本生成
"""

import os
import sys
import json
import shutil
import tarfile
import zipfile
from datetime import datetime
from typing import Dict, List, Optional


class QuantumPackager:
    """量子系统打包器"""
    
    def __init__(self, 
                 source_dir: str = '/root/QSM/QEntL/System/AgentHarness',
                 output_dir: str = '/root/QSM/dist'):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.package_name = 'qsm_quantum_modules'
        self.version = '1.0.0'
        
        # 核心模块列表
        self.core_modules = [
            'quantum_simulator_integration.py',
            'quantum_model_integration.py',
            'shor_algorithm.py',
            'quantum_error_correction.py',
            'quantum_rng.py',
            'quantum_cryptography.py',
            'quantum_ml.py',
            'quantum_optimization.py',
            'quantum_simulation.py',
            'quantum_network.py',
            'quantum_toolkit.py',
            'quantum_integration_test.py',
            'quantum_doc_generator.py',
            'quantum_launcher.py',
            'quantum_config.py',
            'quantum_monitor.py',
            'quantum_exporter.py',
            'quantum_logger.py',
            'quantum_cli.py',
            'quantum_api.py',
            'quantum_initializer.py'
        ]
    
    def verify_integrity(self) -> Dict:
        """验证系统完整性"""
        print("=" * 60)
        print("验证系统完整性...")
        print("=" * 60)
        
        results = {
            'valid': True,
            'missing_files': [],
            'present_files': [],
            'total_files': len(self.core_modules)
        }
        
        for module in self.core_modules:
            path = os.path.join(self.source_dir, module)
            if os.path.exists(path):
                results['present_files'].append(module)
                print(f"  ✅ {module}")
            else:
                results['missing_files'].append(module)
                results['valid'] = False
                print(f"  ❌ {module} - 缺失")
        
        print(f"\n完整性: {len(results['present_files'])}/{results['total_files']}")
        
        return results
    
    def collect_dependencies(self) -> Dict:
        """收集依赖信息"""
        print("\n" + "=" * 60)
        print("收集依赖信息...")
        print("=" * 60)
        
        dependencies = {
            'python': '>=3.8',
            'packages': []
        }
        
        # 检测依赖
        packages_to_check = [
            ('qiskit', '>=2.0'),
            ('qiskit-aer', '>=0.13'),
            ('numpy', '>=1.20'),
            ('scipy', '>=1.7'),
            ('psutil', '>=5.8'),
            ('pyyaml', '>=6.0')
        ]
        
        for package, version in packages_to_check:
            package_name = package.replace('-', '_')
            try:
                imported = __import__(package_name)
                actual_version = getattr(imported, '__version__', 'unknown')
                dependencies['packages'].append({
                    'name': package,
                    'version': version,
                    'actual': actual_version,
                    'status': 'ok'
                })
                print(f"  ✅ {package}: {actual_version}")
            except ImportError:
                dependencies['packages'].append({
                    'name': package,
                    'version': version,
                    'status': 'missing'
                })
                print(f"  ❌ {package}: 未安装")
        
        return dependencies
    
    def create_package_structure(self, target_dir: str) -> Dict:
        """创建包结构"""
        print("\n" + "=" * 60)
        print("创建包结构...")
        print("=" * 60)
        
        structure = {
            'directories': [],
            'files': []
        }
        
        # 创建目录结构
        dirs = [
            'qsm_quantum',
            'qsm_quantum/modules',
            'qsm_quantum/config',
            'qsm_quantum/tests',
            'qsm_quantum/docs'
        ]
        
        for d in dirs:
            path = os.path.join(target_dir, d)
            os.makedirs(path, exist_ok=True)
            structure['directories'].append(d)
            print(f"  创建目录: {d}")
        
        # 复制模块文件
        for module in self.core_modules:
            src = os.path.join(self.source_dir, module)
            dst = os.path.join(target_dir, 'qsm_quantum/modules', module)
            
            if os.path.exists(src):
                shutil.copy2(src, dst)
                structure['files'].append(module)
                print(f"  复制: {module}")
        
        return structure
    
    def create_setup_py(self, target_dir: str) -> str:
        """创建setup.py"""
        setup_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QSM量子系统安装脚本"""

from setuptools import setup, find_packages

setup(
    name='qsm-quantum',
    version='{self.version}',
    description='QSM量子计算系统',
    author='Zhoho, WeQ, GLM5',
    author_email='contact@som.top',
    packages=find_packages(),
    install_requires=[
        'qiskit>=2.0',
        'qiskit-aer>=0.13',
        'numpy>=1.20',
        'scipy>=1.7',
        'psutil>=5.8',
        'pyyaml>=6.0'
    ],
    python_requires='>=3.8',
    entry_points={{
        'console_scripts': [
            'qsm-quantum=qsm_quantum.cli:main',
        ]
    }},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Quantum Computing',
    ]
)
'''
        
        setup_path = os.path.join(target_dir, 'setup.py')
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        
        print(f"  创建: setup.py")
        return setup_path
    
    def create_readme(self, target_dir: str) -> str:
        """创建README"""
        readme_content = f'''# QSM量子计算系统

版本: {self.version}

## 简介

QSM量子计算系统提供了完整的量子计算能力，包括：

- 量子算法实现（Grover、Shor、QFT等）
- 量子机器学习
- 量子密码学
- 量子网络
- 量子物理模拟

## 安装

```bash
pip install qsm-quantum
```

## 快速开始

```python
from qsm_quantum.modules.quantum_rng import QuantumRNG

rng = QuantumRNG()
print(rng.generate_random_number(0, 100))
```

## 模块列表

- quantum_simulator_integration - 量子模拟器集成
- shor_algorithm - Shor因数分解
- quantum_rng - 量子随机数生成器
- quantum_cryptography - 量子密码学
- quantum_ml - 量子机器学习
- quantum_optimization - 量子优化算法
- quantum_simulation - 量子物理模拟
- quantum_network - 量子网络

## 依赖

- Python >= 3.8
- Qiskit >= 2.0
- NumPy >= 1.20
- SciPy >= 1.7

## 许可证

MIT License

## 作者

中华Zhoho，小趣WeQ，GLM5

---

**三大圣律**
1. 为每个人服务，服务人类！
2. 保护好每个人的生命安全、健康快乐、幸福生活！
3. 没有以上两个前提，其他就不能发生！
'''
        
        readme_path = os.path.join(target_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  创建: README.md")
        return readme_path
    
    def create_manifest(self, target_dir: str) -> str:
        """创建MANIFEST.in"""
        manifest_content = '''include README.md
include LICENSE
include requirements.txt
recursive-include qsm_quantum *.py
recursive-include qsm_quantum/config *.json *.yaml
recursive-include qsm_quantum/docs *.md
'''
        
        manifest_path = os.path.join(target_dir, 'MANIFEST.in')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        print(f"  创建: MANIFEST.in")
        return manifest_path
    
    def create_package(self, format: str = 'tar.gz') -> Dict:
        """创建完整包"""
        print("=" * 60)
        print("QSM量子系统打包器")
        print("=" * 60)
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 创建临时目录
        temp_dir = os.path.join(self.output_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. 验证完整性
        integrity = self.verify_integrity()
        if not integrity['valid']:
            print("\n❌ 系统完整性验证失败")
            return {'success': False, 'error': 'Integrity check failed'}
        
        # 2. 收集依赖
        dependencies = self.collect_dependencies()
        
        # 3. 创建包结构
        structure = self.create_package_structure(temp_dir)
        
        # 4. 创建安装文件
        self.create_setup_py(temp_dir)
        self.create_readme(temp_dir)
        self.create_manifest(temp_dir)
        
        # 5. 创建__init__.py
        init_path = os.path.join(temp_dir, 'qsm_quantum', '__init__.py')
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(f'"""QSM量子计算系统 v{self.version}"""\n__version__ = "{self.version}"\n')
        print(f"  创建: __init__.py")
        
        # 6. 打包
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        package_filename = f'{self.package_name}_{self.version}_{timestamp}'
        
        if format == 'tar.gz':
            archive_path = os.path.join(self.output_dir, f'{package_filename}.tar.gz')
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(os.path.join(temp_dir, 'qsm_quantum'), arcname='qsm_quantum')
            print(f"\n✅ 打包完成: {archive_path}")
        
        elif format == 'zip':
            archive_path = os.path.join(self.output_dir, f'{package_filename}.zip')
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(os.path.join(temp_dir, 'qsm_quantum')):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            print(f"\n✅ 打包完成: {archive_path}")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return {
            'success': True,
            'archive_path': archive_path if 'archive_path' in dir() else None,
            'integrity': integrity,
            'dependencies': dependencies,
            'structure': structure
        }


def create_distribution():
    """创建分发包"""
    packager = QuantumPackager()
    result = packager.create_package(format='tar.gz')
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='QSM量子系统打包器')
    parser.add_argument('--format', type=str, default='tar.gz', 
                       choices=['tar.gz', 'zip'], help='打包格式')
    
    args = parser.parse_args()
    
    packager = QuantumPackager()
    result = packager.create_package(format=args.format)
    
    if result['success']:
        print("\n✅ 打包成功!")
    else:
        print(f"\n❌ 打包失败: {result.get('error', 'Unknown error')}")
