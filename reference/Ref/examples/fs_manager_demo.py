#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件系统管理服务示例
展示如何使用Ref的统一文件系统管理功能
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入文件系统管理器
from Ref.core.fs_manager import get_fs_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FSManagerDemo")

def show_module_structure(module_name):
    """显示模块的目录结构"""
    fs_manager = get_fs_manager()
    
    # 分析模块结构
    report = fs_manager.analyze_project_structure()
    if module_name in report['modules']:
        module_info = report['modules'][module_name]
        
        print(f"\n{module_name}模块结构分析:")
        print(f"  - 文件总数: {module_info['file_count']}")
        print(f"  - 目录总数: {module_info['directory_count']}")
        
        print("\n  子目录:")
        for subdir in module_info['subdirectories']:
            print(f"    - {subdir}")
            
        print("\n  根目录中的文件:")
        for file in module_info['files_in_root']:
            print(f"    - {file}")
            
        print("\n  缺失的标准目录:")
        for missing_dir in module_info['missing_standard_dirs']:
            print(f"    - {missing_dir}")
            
        print("\n  按文件类型统计:")
        for ext, count in module_info['files_by_type'].items():
            print(f"    - {ext or '(无扩展名)'}: {count}个文件")
    else:
        print(f"找不到模块: {module_name}")

def demo_create_standard_structure():
    """演示创建标准目录结构"""
    fs_manager = get_fs_manager()
    
    print("\n创建标准目录结构:")
    results = fs_manager.create_standard_structure()
    
    print(f"  - 新创建的目录: {len(results['created_dirs'])}")
    print(f"  - 已存在的目录: {len(results['existing_dirs'])}")
    print(f"  - 发生的错误: {len(results['errors'])}")
    
    if results['created_dirs']:
        print("\n  新创建的目录:")
        for dir_path in results['created_dirs'][:5]:  # 只显示前5个
            print(f"    - {os.path.relpath(dir_path, project_root)}")
        if len(results['created_dirs']) > 5:
            print(f"    - ...以及其他 {len(results['created_dirs']) - 5} 个目录")

def demo_organize_module(module_name):
    """演示组织模块文件"""
    fs_manager = get_fs_manager()
    
    print(f"\n模拟组织{module_name}模块文件:")
    results = fs_manager.organize_module_files(module_name, apply=False)
    
    if 'error' in results:
        print(f"  错误: {results['error']}")
        return
        
    print(f"  - 将移动的文件: {len(results['moved_files'])}")
    print(f"  - 保持不变的文件: {len(results['unchanged_files'])}")
    
    if results['moved_files']:
        print("\n  将移动的文件:")
        for file_info in results['moved_files'][:5]:  # 只显示前5个
            src = os.path.relpath(file_info['from'], project_root)
            dst = os.path.relpath(file_info['to'], project_root)
            print(f"    - {src} -> {dst}")
        if len(results['moved_files']) > 5:
            print(f"    - ...以及其他 {len(results['moved_files']) - 5} 个文件")

def demo_clean_empty_dirs():
    """演示清理空目录"""
    fs_manager = get_fs_manager()
    
    # 创建一些测试用的空目录
    test_dirs = [
        os.path.join(project_root, "Ref", "temp", "empty1"),
        os.path.join(project_root, "Ref", "temp", "empty2"),
        os.path.join(project_root, "Ref", "temp", "empty3", "nested")
    ]
    
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"创建测试空目录: {os.path.relpath(dir_path, project_root)}")
    
    print("\n清理空目录:")
    results = fs_manager.clean_empty_directories()
    
    print(f"  - 删除的空目录: {len(results['deleted'])}")
    
    if results['deleted']:
        print("\n  删除的空目录:")
        for dir_path in results['deleted']:
            print(f"    - {os.path.relpath(dir_path, project_root)}")

def demo_merge_directories():
    """演示合并目录"""
    fs_manager = get_fs_manager()
    
    # 创建测试目录结构
    source_dir = os.path.join(project_root, "Ref", "temp", "source")
    target_dir = os.path.join(project_root, "Ref", "temp", "target")
    
    # 清理可能存在的旧目录
    import shutil
    if os.path.exists(os.path.join(project_root, "Ref", "temp")):
        shutil.rmtree(os.path.join(project_root, "Ref", "temp"))
    
    # 创建源目录和文件
    os.makedirs(source_dir, exist_ok=True)
    with open(os.path.join(source_dir, "test1.txt"), "w") as f:
        f.write("测试文件1")
    with open(os.path.join(source_dir, "test2.txt"), "w") as f:
        f.write("测试文件2")
    os.makedirs(os.path.join(source_dir, "subdir"), exist_ok=True)
    with open(os.path.join(source_dir, "subdir", "test3.txt"), "w") as f:
        f.write("测试文件3")
    
    # 创建目标目录和文件
    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, "test4.txt"), "w") as f:
        f.write("测试文件4")
    os.makedirs(os.path.join(target_dir, "subdir"), exist_ok=True)
    with open(os.path.join(target_dir, "subdir", "test5.txt"), "w") as f:
        f.write("测试文件5")
    
    print("\n测试目录创建完成:")
    print(f"  - 源目录: {os.path.relpath(source_dir, project_root)}")
    print(f"  - 目标目录: {os.path.relpath(target_dir, project_root)}")
    
    print("\n合并目录:")
    success = fs_manager.merge_directories(source_dir, target_dir, move_files=True)
    print(f"  - 合并{'成功' if success else '失败'}")
    
    if success:
        print("\n合并后的目标目录内容:")
        for root, dirs, files in os.walk(target_dir):
            rel_path = os.path.relpath(root, target_dir)
            if rel_path == '.':
                for file in files:
                    print(f"  - {file}")
            else:
                for file in files:
                    print(f"  - {os.path.join(rel_path, file)}")

def main():
    """主函数"""
    print("=" * 60)
    print("Ref文件系统管理服务演示")
    print("=" * 60)
    
    module_to_analyze = "Ref"
    print(f"\n分析{module_to_analyze}模块结构")
    show_module_structure(module_to_analyze)
    
    print("\n演示创建标准目录结构")
    demo_create_standard_structure()
    
    print(f"\n演示组织模块文件")
    demo_organize_module("Ref")
    
    print("\n演示目录管理功能")
    demo_merge_directories()
    
    print("\n演示清理空目录")
    demo_clean_empty_dirs()
    
    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)

if __name__ == "__main__":
    main() 