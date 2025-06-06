#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复kiwisolver的DLL加载问题
"""

import os
import sys
import subprocess
import platform
import site
from pathlib import Path

print("开始修复kiwisolver的DLL加载问题...")

def get_site_packages():
    """获取site-packages目录路径"""
    return site.getsitepackages()[0]

def fix_dll_issue():
    """修复DLL加载问题"""
    try:
        # 先卸载然后重新安装kiwisolver
        print("卸载kiwisolver...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "kiwisolver"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("重新安装kiwisolver...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "kiwisolver==1.3.2"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 安装matplotlib的特定版本
        print("重新安装matplotlib...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-cache-dir", "matplotlib==3.5.3"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 安装VS C++ Redistributable包的辅助代码
        site_packages = get_site_packages()
        print(f"Python site-packages目录：{site_packages}")
        
        # 检查vc_redist.exe是否存在
        vs_redist_paths = [
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\VC\\Redist\\MSVC\\14.29.30133\\vc_redist.x64.exe",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\VC\\Redist\\MSVC\\14.28.29913\\vc_redist.x64.exe",
            "C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\VC\\Redist\\MSVC\\14.27.29016\\vc_redist.x64.exe"
        ]
        
        redist_found = False
        for path in vs_redist_paths:
            if os.path.exists(path):
                print(f"找到VC++ Redistributable: {path}")
                redist_found = True
                # 运行安装
                print("安装VC++ Redistributable...")
                subprocess.run([path, "/passive", "/norestart"], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                break
        
        if not redist_found:
            print("未找到VC++ Redistributable，请手动安装...")
            print("下载链接: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        
        # 测试kiwisolver是否可以导入
        print("\n测试kiwisolver导入...")
        import kiwisolver
        print(f"成功导入kiwisolver，版本: {kiwisolver.__version__}")
        
        print("\n测试matplotlib导入...")
        import matplotlib
        print(f"成功导入matplotlib，版本: {matplotlib.__version__}")
        
        print("\n测试cirq导入...")
        import cirq
        print(f"成功导入cirq，版本: {cirq.__version__}")
        
        print("\nDLL问题修复成功!")
        return True
        
    except Exception as e:
        print(f"修复过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_dll_issue() 