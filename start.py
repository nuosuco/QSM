#!/usr/bin/env python3
"""
QEntL量子操作系统统一启动器
版本: v0.3.0
量子基因编码: QGC-STARTER-20260308

支持三种启动模式
"""

import sys
import os

def print_banner():
    """打印启动横幅"""
    print("\n" + "=" * 60)
    print("🌟 QEntL量子操作系统 - 统一启动器")
    print("   Quantum Entanglement Language Operating System")
    print("=" * 60)
    print("\n三种启动模式:")
    print("  1. Web操作系统 - 浏览器访问")
    print("  2. 量子虚拟机   - 桌面应用")
    print("  3. 原生操作系统 - 直接启动")
    print("\n三大圣律:")
    print("  1. 为每个人服务，服务人类！")
    print("  2. 保护好每个人的生命安全、健康快乐、幸福生活！")
    print("  3. 没有以上两个前提，其他就不能发生！")
    print("=" * 60)


def start_web():
    """启动Web操作系统"""
    print("\n🌐 启动Web操作系统...")
    print("   访问地址: https://som.top")
    print("   或本地启动Web服务器...")
    # 这里可以启动本地Web服务器


def start_vm():
    """启动量子虚拟机"""
    print("\n⚛️ 启动量子虚拟机...")
    vm_path = os.path.join(os.path.dirname(__file__), 'VM', 'src', 'main.py')
    if os.path.exists(vm_path):
        os.system(f'python3 {vm_path}')
    else:
        print("   VM模块未找到")


def start_os():
    """启动原生操作系统"""
    print("\n🖥️ 启动原生操作系统...")
    os_path = os.path.join(os.path.dirname(__file__), 'OS', 'kernel', 'init.py')
    if os.path.exists(os_path):
        os.system(f'python3 {os_path}')
    else:
        print("   OS内核未找到")


def main():
    """主函数"""
    print_banner()
    
    while True:
        print("\n请选择启动模式 (1/2/3) 或按 q 退出:")
        choice = input("> ").strip().lower()
        
        if choice == '1':
            start_web()
        elif choice == '2':
            start_vm()
        elif choice == '3':
            start_os()
        elif choice in ['q', 'quit', 'exit']:
            print("\n👋 再见！服务人类，为每个人服务！")
            break
        else:
            print("   无效选择，请输入 1, 2, 3 或 q")


if __name__ == "__main__":
    main()
