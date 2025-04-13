#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志配置测试用例

此文件包含各种日志配置情况，用于测试日志路径更新脚本的功能。
"""

import logging
import os
from datetime import datetime

# 测试用例1: 简单的日志文件路径
log_file = "test.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file
)

# 测试用例2: 直接使用FileHandler
file_handler = logging.FileHandler("direct_handler.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 测试用例3: 使用RotatingFileHandler
rotating_handler = logging.handlers.RotatingFileHandler(
    "rotating.log", 
    maxBytes=10485760, 
    backupCount=5
)

# 测试用例4: 变量赋值形式
LOG_PATH = "variable_path.log"
LOG_FILE = "variable_file.log"
log_path = "another_path.log"

# 测试用例5: 已经使用os.path.join的路径
correct_path = os.path.join(".logs", "already_correct.log")

# 测试用例6: 多级路径
nested_path = "logs/nested/deep/path.log"

# 测试用例7: 在字符串中包含.log但不是日志文件
not_log_file = "This is a string containing .log but not a file path"

# 测试用例8: 使用字符串格式化的路径
timestamp = datetime.now().strftime("%Y%m%d")
formatted_log = f"log_{timestamp}.log"

# 测试用例9: 在注释中的路径
# 这是一个注释 file_path.log 不应该被更新

# 测试用例10: 文件名中包含点号
dotted_file = "file.name.with.dots.log"

# 测试用例12: 没有变量名的日志处理器
def direct_handler_test():
    logger = logging.getLogger("direct_test")
    logger.addHandler(logging.FileHandler("direct_no_var.log"))
    return logger

def test_function():
    # 测试用例11: 函数内的日志配置
    local_log = "function_local.log"
    handler = logging.FileHandler(local_log)
    logger = logging.getLogger("test_function")
    logger.addHandler(handler)
    
    # 使用Path对象
    from pathlib import Path
    path_obj = Path("path_object.log")
    
    return logger 
"""
量子基因编码: QE-TES-25546620E7F3
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
"""