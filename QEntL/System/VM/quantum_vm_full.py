#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子虚拟机完整集成
QEntL Quantum Virtual Machine Integration

创建时间: 2026-03-18
开发者: 小趣WeQ

功能:
- 完整的量子虚拟机实现
- 整合QBC加载器、量子寄存器、执行引擎
- 支持运行QEntL量子程序
"""

import os
import sys
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# 添加项目路径
VM_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VM_DIR)

# 导入组件
from qbc_loader import QBCLoader, QBCProgram
from quantum_registers import QuantumRegisters
from execution_engine import QuantumExecutionEngine, ExecutionResult

# 量子基因编码
QUANTUM_GENES = {
    "心": "\U000f2737",
    "乾坤": "\U000f2735",
    "天": "\U000f27ad",
    "火": "\U000f27ae",
    "王": "\U000f27b0",
}


@dataclass
class VMConfig:
    """虚拟机配置"""
    max_qubits: int = 64
    debug_mode: bool = False
    trace_execution: bool = False
    memory_limit_mb: int = 256


class QuantumVM:
    """QEntL量子虚拟机"""
    
    def __init__(self, config: Optional[VMConfig] = None):
        """初始化量子虚拟机"""
        self.config = config or VMConfig()
        
        # 初始化组件
        self.loader = QBCLoader()
        self.registers = QuantumRegisters(max_qubits=self.config.max_qubits)
        self.engine = QuantumExecutionEngine(max_qubits=self.config.max_qubits)
        
        # 程序状态
        self.current_program: Optional[QBCProgram] = None
        self.execution_history: List[Dict] = []
        
        print(f"🔮 QEntL量子虚拟机启动")
        print(f"   最大量子比特: {self.config.max_qubits}")
        print(f"   内存限制: {self.config.memory_limit_mb}MB")
        print(f"   调试模式: {'开启' if self.config.debug_mode else '关闭'}")
    
    # ==================== 程序加载 ====================
    
    def load_program(self, filepath: str) -> bool:
        """加载QBC程序"""
        try:
            self.current_program = self.loader.load(filepath)
            print(f"✅ 程序加载成功: {os.path.basename(filepath)}")
            return True
        except Exception as e:
            print(f"❌ 程序加载失败: {e}")
            return False
    
    def load_source(self, source: str) -> bool:
        """直接从源代码创建程序"""
        self.current_program = QBCProgram(
            filepath="<memory>",
            magic=b'QBC\x01',
            source_code=source,
            metadata={"source": "direct"}
        )
        print(f"✅ 源代码加载成功 ({len(source)} 字符)")
        return True
    
    # ==================== 程序执行 ====================
    
    def run(self) -> ExecutionResult:
        """运行当前程序"""
        if not self.current_program:
            return ExecutionResult(
                success=False,
                output=None,
                message="未加载程序"
            )
        
        print(f"\n🚀 开始执行程序...")
        start_time = time.time()
        
        # 执行源代码
        result = self.engine.execute_source(self.current_program.source_code)
        
        execution_time = time.time() - start_time
        
        # 记录执行历史
        self.execution_history.append({
            "program": self.current_program.filepath,
            "success": result.success,
            "execution_time": execution_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        
        print(f"⏱️ 执行时间: {execution_time*1000:.2f}ms")
        print(f"📊 结果: {result.message}")
        
        return result
    
    def run_file(self, filepath: str) -> ExecutionResult:
        """加载并运行程序"""
        if self.load_program(filepath):
            return self.run()
        return ExecutionResult(
            success=False,
            output=None,
            message="程序加载失败"
        )
    
    # ==================== 量子操作接口 ====================
    
    def allocate_qubit(self) -> int:
        """分配量子比特"""
        return self.registers.allocate_qubit()
    
    def hadamard(self, qubit_id: int):
        """应用Hadamard门"""
        self.registers.hadamard(qubit_id)
    
    def measure(self, qubit_id: int) -> int:
        """测量量子比特"""
        return self.registers.measure(qubit_id)
    
    def cnot(self, control: int, target: int):
        """应用CNOT门"""
        self.registers.cnot(control, target)
    
    # ==================== 状态查询 ====================
    
    def get_status(self) -> Dict:
        """获取虚拟机状态"""
        return {
            "config": {
                "max_qubits": self.config.max_qubits,
                "debug_mode": self.config.debug_mode,
            },
            "registers": self.registers.get_status(),
            "engine": self.engine.get_status(),
            "current_program": self.current_program.filepath if self.current_program else None,
            "executions": len(self.execution_history),
        }
    
    def get_quantum_genes(self) -> List[str]:
        """获取量子基因编码"""
        if self.current_program:
            return self.current_program.get_quantum_genes()
        return []


def main():
    """测试函数"""
    print("=" * 60)
    print("🚀 QEntL量子虚拟机完整测试")
    print("=" * 60)
    
    # 创建虚拟机
    config = VMConfig(
        max_qubits=16,
        debug_mode=True,
        memory_limit_mb=128
    )
    vm = QuantumVM(config)
    
    # 测试1: 直接源代码执行
    print("\n" + "=" * 60)
    print("📊 测试1: 源代码执行")
    print("=" * 60)
    
    source = """
    配置 {
        版本: "1.0.0"
        量子基因: "王"
    }
    
    函数 量子计算演示() {
        // 分配量子比特
        let q0 = 分配量子比特()
        
        // 应用Hadamard门
        Hadamard(q0)
        
        // 测量
        let 结果 = 测量(q0)
        
        返回 结果
    }
    """
    
    vm.load_source(source)
    result = vm.run()
    print(f"输出: {result.output}")
    
    # 测试2: 加载QBC文件
    print("\n" + "=" * 60)
    print("📊 测试2: 加载QBC文件")
    print("=" * 60)
    
    qbc_file = "/root/QSM/qbc/system/kernel/filesystem/access_control.qbc"
    if os.path.exists(qbc_file):
        vm.load_program(qbc_file)
        print(f"量子基因: {vm.get_quantum_genes()}")
        print(f"函数定义: {vm.current_program.get_functions()[:3]}")
    
    # 测试3: 量子比特操作
    print("\n" + "=" * 60)
    print("📊 测试3: 量子比特操作")
    print("=" * 60)
    
    q0 = vm.allocate_qubit()
    q1 = vm.allocate_qubit()
    
    print(f"分配: q{q0}, q{q1}")
    
    vm.hadamard(q0)
    print(f"Hadamard(q{q0})")
    
    vm.cnot(q0, q1)
    print(f"CNOT(q{q0}, q{q1})")
    
    r0 = vm.measure(q0)
    r1 = vm.measure(q1)
    print(f"测量结果: q{q0}={r0}, q{q1}={r1}")
    
    # 最终状态
    print("\n" + "=" * 60)
    print("📊 虚拟机最终状态")
    print("=" * 60)
    
    status = vm.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()
