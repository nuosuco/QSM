#!/bin/bash
# QSM 三种部署实施脚本
# 版本: 1.0.0
# 日期: 2026-03-19

echo "==================================="
echo "QSM 三种部署实施"
echo "==================================="
echo ""

# 部署状态检查
echo "=== 1. 检查核心文件 ==="

# 部署一：操作系统核心
echo "部署一 - 操作系统核心文件:"
ls -la QEntL/System/Kernel/kernel/microkernel_core.qentl 2>/dev/null && echo "✅ 微内核核心存在" || echo "❌ 微内核核心缺失"
ls -la QEntL/System/Kernel/kernel/quantum_processor.qentl 2>/dev/null && echo "✅ 量子处理器存在" || echo "❌ 量子处理器缺失"

# 部署二：虚拟机核心
echo ""
echo "部署二 - 虚拟机核心文件:"
ls -la QEntL/System/VM/quantum_vm_core.qentl 2>/dev/null && echo "✅ 虚拟机核心存在" || echo "❌ 虚拟机核心缺失"
ls -la QEntL/System/Compiler/quantum_compiler_v2.qentl 2>/dev/null && echo "✅ 编译器存在" || echo "❌ 编译器缺失"

# 部署三：Web系统
echo ""
echo "部署三 - Web系统文件:"
ls -la QEntL/System/Kernel/filesystem/view_renderer.qentl 2>/dev/null && echo "✅ 视图渲染器存在" || echo "❌ 视图渲染器缺失"
ls -la QEntL/System/Kernel/gui/ 2>/dev/null | head -5 && echo "✅ GUI模块存在" || echo "❌ GUI模块缺失"

# 安装器检查
echo ""
echo "=== 2. 检查安装器 ==="
ls -la Installer/qentl_installer.qentl 2>/dev/null && echo "✅ 安装器存在" || echo "❌ 安装器缺失"
ls -la Installer/setup.bat 2>/dev/null && echo "✅ 安装脚本存在" || echo "❌ 安装脚本缺失"

# Web服务检查
echo ""
echo "=== 3. 检查Web服务 ==="
systemctl status nginx | head -3
curl -s -o /dev/null -w "HTTP状态: %{http_code}\n" https://som.top

# Git状态
echo ""
echo "=== 4. 检查Git状态 ==="
git branch | head -3
git log --oneline -3

echo ""
echo "==================================="
echo "部署状态检查完成"
echo "==================================="
