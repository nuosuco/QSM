#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子虚拟机功能测试
"""

import sys
import os
sys.path.insert(0, '/root/QSM/QEntL/System/VM')

from datetime import datetime

def test_qbc_loader():
    """测试QBC加载器"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试QBC加载器...")
    try:
        from qbc_loader import QBCLoader
        loader = QBCLoader()
        qbc_dir = '/root/QSM/qbc'
        if os.path.exists(qbc_dir):
            files = [f for f in os.listdir(qbc_dir) if f.endswith('.qbc')]
            print(f"  ✅ QBC文件数: {len(files)}")
            return True
        else:
            print(f"  ⚠️ QBC目录不存在")
            return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def test_quantum_registers():
    """测试量子寄存器"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试量子寄存器...")
    try:
        from quantum_registers import QuantumRegisterManager
        manager = QuantumRegisterManager()
        print(f"  ✅ 量子寄存器管理器初始化成功")
        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def test_execution_engine():
    """测试执行引擎"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试执行引擎...")
    try:
        from execution_engine import ExecutionEngine
        engine = ExecutionEngine()
        print(f"  ✅ 执行引擎初始化成功")
        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def test_full_vm():
    """测试完整虚拟机"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完整虚拟机...")
    try:
        from quantum_vm_full import QuantumVM
        vm = QuantumVM()
        print(f"  ✅ 量子虚拟机初始化成功")
        return True
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子虚拟机功能测试")
    print("=" * 60)

    results = []
    results.append(("QBC加载器", test_qbc_loader()))
    results.append(("量子寄存器", test_quantum_registers()))
    results.append(("执行引擎", test_execution_engine()))
    results.append(("完整虚拟机", test_full_vm()))

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)

if __name__ == "__main__":
    main()
