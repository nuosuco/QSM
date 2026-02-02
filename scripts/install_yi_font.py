#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝文字体安装脚本
将LSTY-Yi-Black字体安装到系统中
"""

import os
import shutil
import platform
import subprocess
import sys

def get_font_directory():
    """获取系统字体目录"""
    system = platform.system()
    
    if system == "Windows":
        # Windows字体目录
        return os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
    elif system == "Darwin":  # macOS
        return "/Library/Fonts"
    elif system == "Linux":
        # Linux字体目录
        home = os.path.expanduser("~")
        return os.path.join(home, ".fonts")
    else:
        raise Exception(f"不支持的操作系统: {system}")

def install_font_windows(font_path, font_dir):
    """在Windows上安装字体"""
    try:
        # 复制字体文件到系统字体目录
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(font_dir, font_name)
        
        if not os.path.exists(dest_path):
            shutil.copy2(font_path, dest_path)
            print(f"字体已复制到: {dest_path}")
        else:
            print(f"字体已存在: {dest_path}")
        
        # 注册字体
        try:
            subprocess.run(['reg', 'add', 'HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts', 
                          '/v', 'LSTY-Yi-Black (TrueType)', '/t', 'REG_SZ', '/d', font_name, '/f'], 
                         check=True, capture_output=True)
            print("字体已注册到系统")
        except subprocess.CalledProcessError:
            print("字体注册失败，可能需要管理员权限")
        
        return True
    except Exception as e:
        print(f"Windows字体安装失败: {e}")
        return False

def install_font_linux(font_path, font_dir):
    """在Linux上安装字体"""
    try:
        # 创建字体目录
        os.makedirs(font_dir, exist_ok=True)
        
        # 复制字体文件
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(font_dir, font_name)
        
        if not os.path.exists(dest_path):
            shutil.copy2(font_path, dest_path)
            print(f"字体已复制到: {dest_path}")
        else:
            print(f"字体已存在: {dest_path}")
        
        # 更新字体缓存
        try:
            subprocess.run(['fc-cache', '-f', '-v'], check=True, capture_output=True)
            print("字体缓存已更新")
        except subprocess.CalledProcessError:
            print("字体缓存更新失败")
        
        return True
    except Exception as e:
        print(f"Linux字体安装失败: {e}")
        return False

def install_font_macos(font_path, font_dir):
    """在macOS上安装字体"""
    try:
        # 复制字体文件
        font_name = os.path.basename(font_path)
        dest_path = os.path.join(font_dir, font_name)
        
        if not os.path.exists(dest_path):
            shutil.copy2(font_path, dest_path)
            print(f"字体已复制到: {dest_path}")
        else:
            print(f"字体已存在: {dest_path}")
        
        return True
    except Exception as e:
        print(f"macOS字体安装失败: {e}")
        return False

def test_font_installation():
    """测试字体安装是否成功"""
    print("\n=== 字体安装测试 ===")
    
    # 测试彝文字符
    test_chars = ['󲜐', '󲜑', '󲜒', '󲜓', '󲜔']
    
    print("彝文字符测试:")
    for char in test_chars:
        print(f"字符: {char} (U+{ord(char):X})")
    
    print("\n如果字符显示为方框，请重启应用程序或系统。")

def main():
    """主函数"""
    print("彝文字体安装工具")
    print("=" * 50)
    
    # 字体文件路径
    font_path = "Models/tools/web_monitor/fonts/msyi.ttf"
    
    if not os.path.exists(font_path):
        print(f"错误: 找不到字体文件 {font_path}")
        return False
    
    # 获取系统字体目录
    try:
        font_dir = get_font_directory()
        print(f"系统字体目录: {font_dir}")
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    # 根据操作系统安装字体
    system = platform.system()
    success = False
    
    if system == "Windows":
        success = install_font_windows(font_path, font_dir)
    elif system == "Linux":
        success = install_font_linux(font_path, font_dir)
    elif system == "Darwin":  # macOS
        success = install_font_macos(font_path, font_dir)
    else:
        print(f"不支持的操作系统: {system}")
        return False
    
    if success:
        print("\n字体安装完成！")
        test_font_installation()
        
        print("\n下一步:")
        print("1. 重启Cursor或其他应用程序")
        print("2. 在Cursor设置中配置字体: 'LSTY-Yi-Black'")
        print("3. 打开 yi_test_chars.txt 文件测试字体显示")
    else:
        print("\n字体安装失败！")
        print("请尝试以管理员权限运行此脚本。")
    
    return success

if __name__ == "__main__":
    main() 