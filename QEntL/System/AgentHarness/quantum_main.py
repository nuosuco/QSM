#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统主入口模块
统一导入和使用接口

功能：
1. 统一模块导入
2. 简化API
3. 便捷使用接口
"""

import sys
import os
from typing import Dict, Optional

# 添加模块路径
sys.path.insert(0, '/root/QSM/QEntL/System/AgentHarness')

# 版本信息
__version__ = '1.0.0'
__author__ = 'Zhoho, WeQ, GLM5'
__status__ = 'stable'

# 延迟导入模块
_lazy_imports = {}

def _import_module(name: str):
    """延迟导入模块"""
    if name not in _lazy_imports:
        try:
            _lazy_imports[name] = __import__(name)
        except ImportError as e:
            print(f"警告: 无法导入模块 {name}: {e}")
            _lazy_imports[name] = None
    return _lazy_imports[name]


class QSMQuantum:
    """QSM量子系统主类"""
    
    def __init__(self):
        self._initialized = False
        self._modules = {}
    
    def initialize(self) -> bool:
        """初始化系统"""
        if self._initialized:
            return True
        
        print("初始化QSM量子系统...")
        
        # 导入核心模块
        modules_to_import = [
            'quantum_simulator_integration',
            'quantum_rng',
            'quantum_cryptography',
            'shor_algorithm'
        ]
        
        for mod in modules_to_import:
            imported = _import_module(mod)
            if imported:
                self._modules[mod] = imported
        
        self._initialized = True
        print(f"初始化完成，已加载 {len(self._modules)} 个模块")
        return True
    
    def run_grover(self, target: int) -> Dict:
        """运行Grover搜索"""
        mod = _import_module('quantum_simulator_integration')
        if mod:
            integration = mod.QuantumSimulatorIntegration()
            integration.initialize()
            return integration.run_grover_search(target)
        return {'error': '模块不可用'}
    
    def run_shor(self, n: int) -> Dict:
        """运行Shor因数分解"""
        mod = _import_module('shor_algorithm')
        if mod:
            shor = mod.ShorAlgorithm()
            return shor.factorize(n)
        return {'error': '模块不可用'}
    
    def generate_random(self, min_val: int = 0, max_val: int = 100) -> int:
        """生成量子随机数"""
        mod = _import_module('quantum_rng')
        if mod:
            rng = mod.QuantumRNG()
            return rng.generate_int(min_val, max_val)
        return 0
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            'version': __version__,
            'status': __status__,
            'initialized': self._initialized,
            'modules_loaded': list(self._modules.keys())
        }


# 创建默认实例
_quantum = None

def get_quantum() -> QSMQuantum:
    """获取量子系统实例"""
    global _quantum
    if _quantum is None:
        _quantum = QSMQuantum()
    return _quantum


# 便捷函数
def grover(target: int) -> Dict:
    """运行Grover搜索算法"""
    q = get_quantum()
    q.initialize()
    return q.run_grover(target)


def shor(n: int) -> Dict:
    """运行Shor因数分解算法"""
    q = get_quantum()
    q.initialize()
    return q.run_shor(n)


def random(min_val: int = 0, max_val: int = 100) -> int:
    """生成量子随机数"""
    q = get_quantum()
    q.initialize()
    return q.generate_random(min_val, max_val)


def status() -> Dict:
    """获取系统状态"""
    q = get_quantum()
    return q.get_status()


def test_all() -> Dict:
    """运行所有测试"""
    mod = _import_module('quantum_integration_test')
    if mod:
        return mod.run_integration_tests()
    return {'error': '测试模块不可用'}


def initialize() -> bool:
    """初始化系统"""
    q = get_quantum()
    return q.initialize()


# 模块信息
def info() -> str:
    """获取模块信息"""
    return f"""
QSM量子系统 v{__version__}
状态: {__status__}
作者: {__author__}

三大圣律:
1. 为每个人服务，服务人类！
2. 保护好每个人的生命安全、健康快乐、幸福生活！
3. 没有以上两个前提，其他就不能发生！

快速使用:
    from quantum_main import grover, shor, random
    
    # Grover搜索
    result = grover(15)
    
    # Shor因数分解
    factors = shor(21)
    
    # 量子随机数
    num = random(0, 100)
"""


def main():
    """主入口"""
    print(info())
    print("\n初始化系统...")
    initialize()
    print("\n系统状态:")
    print(status())
    print("\n测试量子随机数生成...")
    for i in range(5):
        print(f"  随机数 {i+1}: {random(0, 100)}")
    print("\n完成!")


if __name__ == "__main__":
    main()
