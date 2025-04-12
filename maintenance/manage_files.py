#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QSM项目文件管理脚本
使用Ref.core.fs_manager管理项目文件和目录结构
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
print(f"当前目录: {current_dir}")
print(f"Python路径: {sys.path}")

# 尝试不同的导入方式
try:
    from Ref.core.fs_manager import get_fs_manager
    print("成功导入 from Ref.core.fs_manager import get_fs_manager")
    fs_manager = get_fs_manager()
    print(f"文件系统管理器初始化成功，项目根目录: {fs_manager.project_root}")
except ImportError as e:
    print(f"错误1: 无法导入文件系统管理器 (from Ref.core.fs_manager): {str(e)}")
    try:
        import Ref.core.fs_manager
        print("成功导入 import Ref.core.fs_manager")
        fs_manager = Ref.core.fs_manager.get_fs_manager()
        print(f"文件系统管理器初始化成功，项目根目录: {fs_manager.project_root}")
    except ImportError as e:
        print(f"错误2: 无法导入文件系统管理器 (import Ref.core.fs_manager): {str(e)}")
        try:
            sys.path.append(os.path.join(current_dir, "Ref", "core"))
            from fs_manager import get_fs_manager
            print("成功导入 from fs_manager import get_fs_manager")
            fs_manager = get_fs_manager()
            print(f"文件系统管理器初始化成功，项目根目录: {fs_manager.project_root}")
        except ImportError as e:
            print(f"错误3: 无法导入文件系统管理器 (from fs_manager): {str(e)}")
            print("请确保Ref核心模块已正确安装并且在Python路径中")
            sys.exit(1)

# 打印已导入的模块，帮助调试
print("\n已导入的模块:")
for module_name, module in sys.modules.items():
    if 'Ref' in module_name:
        print(f"  - {module_name}")

def create_standard_structure(args):
    """创建标准目录结构"""
    print("创建标准目录结构...")
    results = fs_manager.create_standard_structure()
    print(f"创建了 {len(results['created_dirs'])} 个目录，已存在 {len(results['existing_dirs'])} 个目录")
    
    if results['created_dirs']:
        print("\n新创建的目录:")
        for dir_path in results['created_dirs'][:10]:  # 只显示前10个
            print(f"  - {os.path.relpath(dir_path, fs_manager.project_root)}")
        if len(results['created_dirs']) > 10:
            print(f"  - ...以及其他 {len(results['created_dirs']) - 10} 个目录")

def organize_module(args):
    """组织指定模块的文件"""
    module = args.module
    apply = args.apply
    
    action = "组织" if apply else "模拟组织"
    print(f"{action} {module} 模块的文件...")
    
    results = fs_manager.organize_module_files(module, apply)
    
    if 'error' in results:
        print(f"错误: {results['error']}")
        return
    
    print(f"{action}完成:")
    print(f"- 移动文件数: {len(results['moved_files'])}")
    print(f"- 保持不变文件数: {len(results['unchanged_files'])}")
    print(f"- 错误数: {len(results['errors'])}")
    
    if results['moved_files']:
        print("\n移动的文件:")
        for i, file_info in enumerate(results['moved_files'][:10], 1):  # 只显示前10个
            src = os.path.relpath(file_info['from'], fs_manager.project_root)
            dst = os.path.relpath(file_info['to'], fs_manager.project_root)
            print(f"  {i}. {src} -> {dst}")
        if len(results['moved_files']) > 10:
            print(f"  ...以及其他 {len(results['moved_files']) - 10} 个文件")
    
    if apply:
        print("\n文件已实际移动")
    else:
        print("\n注意: 这是一个模拟操作，未实际移动文件。使用 --apply 参数执行实际移动。")

def organize_all_modules(args):
    """组织所有模块的文件"""
    apply = args.apply
    
    action = "组织" if apply else "模拟组织"
    print(f"{action}所有模块的文件...")
    
    results = fs_manager.organize_all_modules(apply)
    
    for module, module_results in results.items():
        print(f"\n模块: {module}")
        
        if 'error' in module_results:
            print(f"  错误: {module_results['error']}")
            continue
            
        print(f"  - 移动文件数: {len(module_results['moved_files'])}")
        print(f"  - 保持不变文件数: {len(module_results['unchanged_files'])}")
        print(f"  - 错误数: {len(module_results['errors'])}")
    
    if apply:
        print("\n文件已实际移动")
    else:
        print("\n注意: 这是一个模拟操作，未实际移动文件。使用 --apply 参数执行实际移动。")

def clean_empty_dirs(args):
    """清理空目录"""
    print("清理空目录...")
    
    results = fs_manager.clean_empty_directories()
    
    print(f"删除了 {len(results['deleted'])} 个空目录")
    
    if results['deleted']:
        print("\n删除的空目录:")
        for i, dir_path in enumerate(results['deleted'][:10], 1):  # 只显示前10个
            print(f"  {i}. {os.path.relpath(dir_path, fs_manager.project_root)}")
        if len(results['deleted']) > 10:
            print(f"  ...以及其他 {len(results['deleted']) - 10} 个目录")

def analyze_project(args):
    """分析项目结构"""
    print("分析项目结构...")
    
    report = fs_manager.analyze_project_structure()
    
    print(f"项目根目录: {report['project_root']}")
    print(f"总文件数: {report['file_counts']['total']}")
    print(f"总目录数: {report['directory_counts']['total']}")
    
    print("\n模块概况:")
    for module, module_info in report['modules'].items():
        print(f"- {module}: {module_info['file_count']} 文件, {module_info['directory_count']} 目录")
        if module_info['missing_standard_dirs']:
            print(f"  缺失目录: {', '.join(module_info['missing_standard_dirs'])}")
    
    print("\n建议:")
    if report['recommendations']:
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
    else:
        print("无优化建议")
    
    if args.output:
        # 保存报告到文件
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n分析报告已保存至: {args.output}")

def merge_dirs(args):
    """合并目录"""
    source_dir = args.source
    target_dir = args.target
    copy_only = args.copy_only
    
    action = "复制合并" if copy_only else "移动合并"
    print(f"{action}目录: {source_dir} -> {target_dir}")
    
    if not os.path.isdir(source_dir):
        print(f"错误: 源目录不存在: {source_dir}")
        return
        
    if not os.path.isdir(target_dir):
        print(f"错误: 目标目录不存在: {target_dir}")
        return
    
    success = fs_manager.merge_directories(source_dir, target_dir, move_files=not copy_only)
    
    if success:
        print(f"{action}成功")
        
        # 显示合并后的目标目录内容
        print("\n合并后的目标目录内容:")
        for root, dirs, files in os.walk(target_dir):
            rel_path = os.path.relpath(root, target_dir)
            if rel_path == '.':
                for file in files[:10]:  # 只显示前10个
                    print(f"  - {file}")
                if len(files) > 10:
                    print(f"  - ...以及其他 {len(files) - 10} 个文件")
            elif dirs or files:  # 只显示非空子目录
                print(f"  - {rel_path}/")
    else:
        print(f"{action}失败")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QSM项目文件管理工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # 创建标准目录结构
    parser_create = subparsers.add_parser('create', help='创建标准目录结构')
    parser_create.set_defaults(func=create_standard_structure)
    
    # 组织模块文件
    parser_organize = subparsers.add_parser('organize', help='组织模块文件')
    parser_organize.add_argument('module', help='模块名称')
    parser_organize.add_argument('--apply', action='store_true', help='实际执行操作，而不是模拟')
    parser_organize.set_defaults(func=organize_module)
    
    # 组织所有模块文件
    parser_organize_all = subparsers.add_parser('organize-all', help='组织所有模块文件')
    parser_organize_all.add_argument('--apply', action='store_true', help='实际执行操作，而不是模拟')
    parser_organize_all.set_defaults(func=organize_all_modules)
    
    # 清理空目录
    parser_clean = subparsers.add_parser('clean', help='清理空目录')
    parser_clean.set_defaults(func=clean_empty_dirs)
    
    # 分析项目结构
    parser_analyze = subparsers.add_parser('analyze', help='分析项目结构')
    parser_analyze.add_argument('--output', type=str, help='输出报告到指定文件')
    parser_analyze.set_defaults(func=analyze_project)
    
    # 合并目录
    parser_merge = subparsers.add_parser('merge', help='合并目录')
    parser_merge.add_argument('source', help='源目录路径')
    parser_merge.add_argument('target', help='目标目录路径')
    parser_merge.add_argument('--copy-only', action='store_true', help='仅复制文件，不移动')
    parser_merge.set_defaults(func=merge_dirs)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    print("======== 开始执行 ========")
    main()
    print("======== 执行完成 ========") 