#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件系统管理器使用示例
"""

from fs_manager import get_fs_manager

if __name__ == "__main__":
    fs_manager = get_fs_manager()
    print(f"FSManager实例化成功，项目根目录: {fs_manager.project_root}")
    
    # 查看Ref模块的目录结构
    report = fs_manager.analyze_project_structure()
    ref_module = report['modules'].get('Ref', {})
    print(f"\nRef模块信息:")
    print(f"  - 文件数: {ref_module.get('file_count', 0)}")
    print(f"  - 目录数: {ref_module.get('directory_count', 0)}")
    
    # 显示建议
    print(f"\n优化建议:")
    for recommendation in report.get('recommendations', []):
        print(f"  - {recommendation}") 