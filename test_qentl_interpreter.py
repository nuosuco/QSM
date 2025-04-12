#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QEntL解释器测试脚本
测试增强后的QEntL解释器的文件路径管理功能
"""

import os
import sys
from pathlib import Path

print("= 测试QEntL解释器的文件路径管理功能 =")

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
print(f"项目根目录: {project_root}")

sys.path.insert(0, project_root)

try:
    # 导入解释器
    print("\n1. 尝试导入解释器...")
    from QEntL.parser.interpreter import Interpreter, resolve_path, find_file
    print("解释器导入成功")
    
    # 创建解释器实例
    print("\n2. 创建解释器实例...")
    interpreter = Interpreter()
    print(f"解释器实例创建成功，项目根目录: {interpreter.project_root}")
    
    # 测试文件解析功能
    print("\n3. 测试文件路径解析功能...")
    test_files = [
        "QEntL/core.qent",
        "QEntL/quantum_network.qent",
        "QEntL/templates/node_template.qentl",
        "QSM/QEntL/qsm_module.qent",
        "WeQ/QEntL/weq_module.qent",
        "SOM/QEntL/som_module.qent",
        "Ref/QEntL/ref_module.qent"
    ]
    
    for file_path in test_files:
        resolved_path = interpreter.resolve_path(file_path)
        print(f"\n原始路径: {file_path}")
        print(f"解析后路径: {resolved_path}")
        print(f"文件是否存在: {os.path.exists(resolved_path)}")
    
    # 测试全局函数
    print("\n4. 测试全局便捷函数...")
    
    for file_name in ["core.qent", "quantum_network.qent", "node_template.qentl"]:
        found_path = find_file(file_name)
        print(f"\n查找文件: {file_name}")
        print(f"找到路径: {found_path}")
        print(f"文件是否存在: {os.path.exists(found_path) if found_path else False}")
    
    # 测试导入语句解析
    print("\n5. 测试导入语句解析...")
    test_imports = [
        '@import "../../QEntL/core.qent" as CoreLib;',
        '@import("../templates/node_template.qentl") as NodeTemplate;',
        '@import "../../QEntL/quantum_network.qent";'
    ]
    
    # 设置一个文件路径，以便解释器可以解析相对路径
    interpreter.file_path = os.path.join(project_root, "QSM", "QEntL", "module.qentl")
    
    for import_statement in test_imports:
        print(f"\n解析导入语句: {import_statement}")
        result = interpreter.parse_import(import_statement)
        if result:
            print(f"解析结果: 类型={result['type']}, 路径={result['path']}, 别名={result['alias']}")
            print(f"文件是否存在: {os.path.exists(result['path'])}")
        else:
            print("解析失败")
    
    print("\n测试完成")
    
except ImportError as e:
    print(f"导入失败: {str(e)}")
except Exception as e:
    print(f"测试过程中发生错误: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n= 测试结束 =") 