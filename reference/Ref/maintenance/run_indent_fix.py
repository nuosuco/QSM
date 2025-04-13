#!/usr/bin/env python
# -*- coding: utf-8 -*-

# # 
"""
量子基因编码: QE-RUN-ECCA068EFAFC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""
运行缩进修复工具和测试的脚本

这个脚本提供了一个简单的命令行界面，用于运行缩进修复工具和相关测试。
它可以单独运行修复工具或测试，或者两者都运行。

用法：
    python run_indent_fix.py [选项]

选项：
    --fix        仅运行修复工具
    --test       仅运行测试
    --all        运行修复工具和测试（默认）
    --dir=PATH   指定要修复的目录
    --file=PATH  指定要修复的文件
    --help       显示此帮助信息
"""

import os
import sys
import argparse
import importlib.util

# 颜色定义
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_status(message):
    """打印状态消息，使用绿色。"""
    print(f"{GREEN}[+] {message}{RESET}")

def print_warning(message):
    """打印警告消息，使用黄色。"""
    print(f"{YELLOW}[!] {message}{RESET}")

def print_error(message):
    """打印错误消息，使用红色。"""
    print(f"{RED}[-] {message}{RESET}")

def import_module(module_path):
    """动态导入指定路径的模块"""
    module_name = os.path.basename(module_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_fix(args):
    """运行修复工具"""
    print_status("开始运行缩进修复工具...")
    
    # 导入修复模块
    current_dir = os.path.dirname(os.path.abspath(__file__))
    fix_module_path = os.path.join(current_dir, 'fix_indent_errors.py')
    
    if not os.path.exists(fix_module_path):
        print_error(f"错误：找不到修复工具 {fix_module_path}")
        return False
    
    fix_module = import_module(fix_module_path)
    
    # 确定要修复的目标
    if args.file:
        if not os.path.exists(args.file):
            print_error(f"错误：文件不存在 {args.file}")
            return False
        
        print_status(f"修复文件：{args.file}")
        result = fix_module.fix_indentation_errors(args.file)
        if result:
            print_status("文件修复成功！")
        else:
            print_warning("文件无需修复或修复失败")
    
    elif args.dir:
        if not os.path.exists(args.dir) or not os.path.isdir(args.dir):
            print_error(f"错误：目录不存在 {args.dir}")
            return False
        
        print_status(f"扫描并修复目录：{args.dir}")
        fixed_count = fix_module.scan_and_fix_directory(args.dir)
        print_status(f"修复完成！共修复 {fixed_count} 个文件")
    
    else:
        # 默认修复所有Python文件
        project_root = os.path.dirname(os.path.dirname(current_dir))
        print_status(f"未指定目标，默认扫描项目根目录：{project_root}")
        fixed_count = fix_module.scan_and_fix_directory(project_root)
        print_status(f"修复完成！共修复 {fixed_count} 个文件")
    
    return True

def run_tests():
    """运行测试"""
    print_status("开始运行缩进修复工具测试...")
    
    # 导入测试模块
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_module_path = os.path.join(current_dir, 'test_indent_fixer.py')
    
    if not os.path.exists(test_module_path):
        print_error(f"错误：找不到测试模块 {test_module_path}")
        return False
    
    # 导入并运行测试
    test_module = import_module(test_module_path)
    test_module.main()
    
    return True

def main():
    """主函数，解析命令行参数并运行相应功能"""
    parser = argparse.ArgumentParser(description="运行缩进修复工具和测试")
    
    # 定义参数组，互斥的选项
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--fix', action='store_true', help='仅运行修复工具')
    mode_group.add_argument('--test', action='store_true', help='仅运行测试')
    mode_group.add_argument('--all', action='store_true', help='运行修复工具和测试（默认）')
    
    # 修复目标参数组，互斥的选项
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument('--dir', type=str, help='指定要修复的目录')
    target_group.add_argument('--file', type=str, help='指定要修复的文件')
    
    # 解析参数
    args = parser.parse_args()
    
    # 设置默认选项
    if not (args.fix or args.test or args.all):
        args.all = True  # 默认运行所有
    
    # 根据参数执行相应操作
    if args.fix or args.all:
        if not run_fix(args):
            return 1
    
    if args.test or args.all:
        if not run_tests():
            return 1
    
    print_status("所有操作完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 