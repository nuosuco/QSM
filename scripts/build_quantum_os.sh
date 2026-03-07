#!/bin/bash
# QEntL量子操作系统构建脚本
echo "🚀 开始构建QEntL量子操作系统..."

echo "📦 编译量子内核..."
qentl-compile QEntL/System/Kernel/quantum_kernel.qentl

echo "🔧 编译量子编译器..."
qentl-compile QEntL/System/Compiler/quantum_compiler.qentl

echo "⚙️ 编译量子虚拟机..."
qentl-compile QEntL/System/VM/quantum_vm.qentl

echo "🌐 编译模型集成模块..."
qentl-compile QEntL/System/quantum_model_integration.qentl

echo "🎮 编译演示程序..."
qentl-compile QEntL/Programs/trilingual_quantum_demo.qentl

echo "✅ QEntL量子操作系统构建完成！"
echo "🌟 支持中文、English、滇川黔贵通用彝文三语编程"
echo "🧠 集成五大量子模型：QSM、SOM、WeQ、Ref、QEntL"
