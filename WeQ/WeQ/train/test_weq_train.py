#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WeQ训练服务测试脚本
"""

import os
import sys

print("===== 测试WeQ训练服务 =====")
print(f"Python版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")

# 尝试导入模块
try:
    from WeQ_train import parse_arguments, main
    print("成功导入WeQ训练模块")
    
    # 打印帮助信息
    print("\n获取参数解析器:")
    parser = parse_arguments()
    parser.print_help()
    
except ImportError as e:
    print(f"导入错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    print(traceback.format_exc())

print("\n===== 测试完成 =====") 