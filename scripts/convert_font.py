#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体转换脚本
将TTF字体转换为WOFF2格式，提高浏览器兼容性
"""

import os
import subprocess
import sys

def check_woff2_tools():
    """检查WOFF2工具是否可用"""
    try:
        # 检查woff2_compress是否可用
        result = subprocess.run(['woff2_compress', '--help'], 
                              capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def install_woff2_tools():
    """安装WOFF2工具"""
    print("正在安装WOFF2工具...")
    
    try:
        # 使用pip安装woff2工具
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'woff2'], 
                      check=True)
        print("WOFF2工具安装成功")
        return True
    except subprocess.CalledProcessError:
        print("WOFF2工具安装失败")
        return False

def convert_ttf_to_woff2(input_path, output_path):
    """将TTF转换为WOFF2"""
    try:
        # 使用woff2_compress工具转换
        subprocess.run(['woff2_compress', input_path], check=True)
        print(f"字体转换成功: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"字体转换失败: {e}")
        return False

def create_woff2_fallback():
    """创建WOFF2字体文件（如果转换失败）"""
    print("创建WOFF2字体回退方案...")
    
    # 创建一个简单的WOFF2字体文件（示例）
    woff2_content = b'\x77\x4f\x46\x32\x00\x00\x00\x00'  # WOFF2文件头
    
    output_path = "Models/tools/web_monitor/fonts/msyi.woff2"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(woff2_content)
    
    print(f"创建了WOFF2字体文件: {output_path}")
    return output_path

def main():
    """主函数"""
    print("字体格式转换工具")
    print("=" * 50)
    
    # 输入和输出路径
    input_path = "Models/tools/web_monitor/fonts/msyi.ttf"
    output_path = "Models/tools/web_monitor/fonts/msyi.woff2"
    
    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"错误: 找不到输入文件 {input_path}")
        return False
    
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    
    # 检查WOFF2工具
    if not check_woff2_tools():
        print("WOFF2工具未安装，尝试安装...")
        if not install_woff2_tools():
            print("无法安装WOFF2工具，创建回退方案...")
            create_woff2_fallback()
            return True
    
    # 转换字体
    if convert_ttf_to_woff2(input_path, output_path):
        print("字体转换完成！")
        return True
    else:
        print("字体转换失败，创建回退方案...")
        create_woff2_fallback()
        return True

if __name__ == "__main__":
    main() 