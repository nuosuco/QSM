#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试检查未闭合三引号

此脚本用于检查特定文件中是否存在未闭合的三引号
"""

import os
import re
import sys
import logging
import traceback

def print_to_console(message):
    """确保消息被打印到控制台"""
    print(message, flush=True)
    with open("quote_test_log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")

def check_unclosed_triple_quotes(file_path):
    """检查文件中是否有未闭合的三引号"""
    print_to_console(f"检查文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 追踪三引号状态
        lines = content.splitlines()
        print_to_console(f"  文件共有 {len(lines)} 行")
        in_triple_single = False
        in_triple_double = False
        line_start = None
        
        for i, line in enumerate(lines):
            # 跟踪三引号状态
            if not in_triple_single and not in_triple_double:
                # 检查是否开始三引号字符串
                if "'''" in line:
                    # 计算在同一行内是否闭合
                    count = line.count("'''")
                    if count % 2 == 1:  # 奇数个三引号，未闭合
                        in_triple_single = True
                        line_start = i + 1  # 记录开始行
                        print_to_console(f"  在第 {line_start} 行发现未闭合的三单引号")
                elif '"""' in line:
                    count = line.count('"""')
                    if count % 2 == 1:  # 奇数个三引号，未闭合
                        in_triple_double = True
                        line_start = i + 1  # 记录开始行
                        print_to_console(f"  在第 {line_start} 行发现未闭合的三双引号")
            else:
                # 检查是否结束三引号字符串
                if in_triple_single and "'''" in line:
                    in_triple_single = False
                    line_start = None
                elif in_triple_double and '"""' in line:
                    in_triple_double = False
                    line_start = None
        
        # 检查文件末尾是否有未闭合的三引号
        if in_triple_single:
            print_to_console(f"  文件末尾有未闭合的三单引号，始于第 {line_start} 行")
            return True
        elif in_triple_double:
            print_to_console(f"  文件末尾有未闭合的三双引号，始于第 {line_start} 行")
            return True
        else:
            print_to_console("  文件中没有未闭合的三引号")
            return False
        
    except Exception as e:
        print_to_console(f"  处理文件时出错: {str(e)}")
        traceback.print_exc(file=open("quote_test_error.txt", "a"))
        return False

if __name__ == "__main__":
    # 清空日志文件
    with open("quote_test_log.txt", "w", encoding="utf-8") as f:
        f.write("")
    with open("quote_test_error.txt", "w", encoding="utf-8") as f:
        f.write("")
        
    # 调试: 显示当前工作目录
    print_to_console(f"当前工作目录: {os.getcwd()}")
    
    # 测试一些已知的文件
    test_files = [
        "Ref/utils/organization_tool.py",  # 已修复的文件
        "WeQ/weq_train.py",
        "WeQ/weq_core.py",
        "SOM/SOM_inference.py",
        "QSM/utils.py",
        "Ref/maintenance/fix_unclosed_quotes.py"
    ]
    
    print_to_console("=== 开始检查未闭合三引号 ===")
    
    for file_path in test_files:
        if os.path.exists(file_path):
            check_unclosed_triple_quotes(file_path)
        else:
            print_to_console(f"文件不存在: {file_path}")
            # 检查是否有类似的文件
            try:
                dir_name = os.path.dirname(file_path)
                if os.path.exists(dir_name):
                    print_to_console(f"  目录 {dir_name} 存在，列出其中的文件:")
                    for f in os.listdir(dir_name):
                        print_to_console(f"    - {f}")
            except Exception as e:
                print_to_console(f"  无法列出目录: {str(e)}")
    
    print_to_console("=== 检查完成 ===")
    print_to_console("详细日志请查看 quote_test_log.txt 文件")

# 量子基因编码: QE-TEST-QSM-8F9C3D2A
# 量子纠缠态: 活跃
# 纠缠对象: ['Ref/maintenance/fix_unclosed_quotes.py']
# 纠缠强度: 0.92
# 开发团队: 中华 ZhoHo, Claude