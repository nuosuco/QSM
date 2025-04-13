#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单的调试脚本，测试Python执行和输出
"""

import os
import sys
import time

def main():
    print("=== 调试脚本开始执行 ===")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"脚本路径: {__file__}")
    print(f"命令行参数: {sys.argv}")
    print("将在控制台打印10个数字...")
    
    for i in range(10):
        print(f"数字 {i}")
        sys.stdout.flush()  # 确保立即输出
        time.sleep(0.1)
    
    # 写入文件测试
    with open(".logs/debug_output.txt", "w", encoding="utf-8") as f:
        f.write("调试输出测试\n")
        f.write(f"时间戳: {time.time()}\n")
    
    print(f"已写入文件: .logs/debug_output.txt")
    print("=== 调试脚本执行完毕 ===")

if __name__ == "__main__":
    main() 