#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一文件管理脚本
整合organize_project.py和move_files.py的功能，并增加对.qent文件的支持
支持PowerShell脚本中的三引号修复
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # 导入文件系统管理器
    from Ref.core.fs_manager import get_fs_manager
    fs_manager = get_fs_manager()
    print("成功导入文件系统管理器")
except ImportError as e:
    print(f"错误: 无法导入文件系统管理器: {str(e)}")
    sys.exit(1)

def create_structure():
    """创建标准目录结构"""
    print("\n=== 创建标准目录结构 ===")
    results = fs_manager.create_standard_structure()
    
    print(f"创建完成: 创建了 {len(results['created_dirs'])} 个目录, "
          f"已存在 {len(results['existing_dirs'])} 个目录, "
          f"发生 {len(results['errors'])} 个错误")
    
    return results

def organize_module(module_name, apply=False):
    """组织指定模块的文件"""
    action = "组织" if apply else "模拟组织"
    print(f"\n=== {action} {module_name} 模块的文件 ===")
    
    results = fs_manager.organize_module_files(module_name, apply)
    
    print(f"{action}完成: 移动 {len(results['moved_files'])} 个文件, "
          f"不变 {len(results['unchanged_files'])} 个文件, "
          f"错误 {len(results['errors'])} 个")
    
    if results['moved_files']:
        print("\n将移动以下文件:")
        for i, file_info in enumerate(results['moved_files'], 1):
            src = os.path.relpath(file_info['from'], fs_manager.project_root)
            
            if 'to' in file_info:
                dst = os.path.relpath(file_info['to'], fs_manager.project_root)
                print(f"  {i}. {src} -> {dst}")
            else:
                print(f"  {i}. {src}")
    
    if results['errors']:
        print("\n错误:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if not apply:
        print("\n注意: 这是模拟运行，未实际移动文件。使用 --apply 参数执行实际移动。")
    
    return results

def organize_all_modules(apply=False):
    """组织所有模块的文件"""
    action = "组织" if apply else "模拟组织"
    print(f"\n=== {action}所有模块的文件 ===")
    
    results = fs_manager.organize_all_modules(apply)
    
    print(f"{action}完成:")
    print(f"- 总移动: {results['total_moved']} 个文件")
    print(f"- 总不变: {results['total_unchanged']} 个文件")
    print(f"- 总错误: {results['total_errors']} 个")
    
    print("\n各模块情况:")
    for module in results['modules']:
        print(f"- {module['name']}: 移动 {module['moved']}, 不变 {module['unchanged']}, 错误 {module['errors']}")
    
    if not apply:
        print("\n注意: 这是模拟运行，未实际移动文件。使用 --apply 参数执行实际移动。")
    
    return results

def clean_empty_dirs():
    """清理空目录"""
    print("\n=== 清理空目录 ===")
    
    results = fs_manager.clean_empty_directories()
    print(f"清理完成，删除了 {len(results['deleted_dirs'])} 个空目录:")
    
    if results['deleted_dirs']:
        for i, dir_path in enumerate(results['deleted_dirs'], 1):
            rel_path = os.path.relpath(dir_path, fs_manager.project_root)
            print(f"  {i}. {rel_path}")
    
    return results

def analyze_project_structure(output_file=None):
    """分析项目结构"""
    print("\n=== 分析项目结构 ===")
    
    report = fs_manager.analyze_project_structure()
    
    # 保存报告到文件
    if output_file:
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"分析报告已保存至: {output_file}")
    
    # 打印简要报告
    print(f"\n项目根目录: {report['project_root']}")
    print(f"总文件数: {report['file_counts']['total']}")
    print(f"总目录数: {report['directory_counts']['total']}")
    
    print("\n模块概况:")
    for module, module_info in report['modules'].items():
        print(f"- {module}: {module_info['file_count']} 文件, {module_info['directory_count']} 目录")
        if module_info.get('missing_standard_dirs'):
            print(f"  缺失目录: {', '.join(module_info['missing_standard_dirs'])}")
    
    print("\n建议:")
    if report.get('recommendations', []):
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
    else:
        print("无优化建议")
    
    return report

def fix_quote_issues():
    """修复三引号问题"""
    print("\n=== 修复三引号问题 ===")
    
    results = fs_manager.process_powershell_cleanup()
    
    print(f"修复完成:")
    print(f"- 处理了 {results['processed_files']} 个文件")
    print(f"- 修复了 {results['fixed_files']} 个文件")
    
    if results['errors']:
        print("\n发生错误:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return results

def merge_directories(source_dir, target_dir, copy_only=False):
    """合并目录"""
    print(f"\n=== {'复制' if copy_only else '移动'}目录内容 ===")
    print(f"从: {source_dir}")
    print(f"到: {target_dir}")
    
    success = fs_manager.merge_directories(source_dir, target_dir, move_files=not copy_only)
    
    if success:
        print("操作成功完成")
    else:
        print("操作失败")
    
    return success

def main():
    parser = argparse.ArgumentParser(description='QSM项目文件管理工具')
    
    # 主要操作
    parser.add_argument('--create-dirs', action='store_true', help='创建标准目录结构')
    parser.add_argument('--organize', type=str, help='组织指定模块的文件')
    parser.add_argument('--organize-all', action='store_true', help='组织所有模块的文件')
    parser.add_argument('--clean', action='store_true', help='清理空目录')
    parser.add_argument('--analyze', action='store_true', help='分析项目结构')
    parser.add_argument('--fix-quotes', action='store_true', help='修复三引号问题')
    parser.add_argument('--merge', type=str, help='合并目录 (源目录:目标目录)')
    
    # 可选参数
    parser.add_argument('--apply', action='store_true', help='应用更改（默认为模拟运行）')
    parser.add_argument('--copy', action='store_true', help='合并目录时复制文件（默认为移动）')
    parser.add_argument('--output', type=str, help='分析报告输出文件')
    
    # 流程组合
    parser.add_argument('--full-cleanup', action='store_true', 
                        help='执行完整清理流程：修复三引号，组织所有模块，清理空目录')
    
    args = parser.parse_args()
    
    # 处理参数
    if args.full_cleanup:
        print("执行完整清理流程...")
        fix_quote_issues()
        organize_all_modules(args.apply)
        if args.apply:
            clean_empty_dirs()
        analyze_project_structure(args.output)
        return
    
    # 单独的操作
    if args.create_dirs:
        create_structure()
    
    if args.organize:
        organize_module(args.organize, args.apply)
    
    if args.organize_all:
        organize_all_modules(args.apply)
    
    if args.clean:
        clean_empty_dirs()
    
    if args.analyze:
        analyze_project_structure(args.output)
    
    if args.fix_quotes:
        fix_quote_issues()
    
    if args.merge:
        try:
            source_dir, target_dir = args.merge.split(':')
            merge_directories(source_dir, target_dir, args.copy)
        except ValueError:
            print("错误: 合并参数格式应为 '源目录:目标目录'")
    
    # 如果没有指定任何操作，显示帮助信息
    if not any([args.create_dirs, args.organize, args.organize_all, args.clean, 
                args.analyze, args.fix_quotes, args.merge, args.full_cleanup]):
        parser.print_help()

if __name__ == '__main__':
    main() 