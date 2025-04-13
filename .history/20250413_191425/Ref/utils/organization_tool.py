#!/usr/bin/env python3
import os
import sys
import argparse
import json
from datetime import datetime

from utils.file_organization_guardian import get_guardian

# 导入目录结构优化器
try:
    from utils.directory_structure_optimizer import get_directory_optimizer
    directory_optimizer_available = True
except ImportError:
    directory_optimizer_available = False
    print("警告: 目录结构优化器不可用，部分功能将受限")


def setup_argparse():
    """设置命令行参数解析"""
    parser = argparse.ArgumentParser(
        description="QSM项目文件组织工具 - 管理文件结构并防止冲突"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 注册现有文件命令
    register_parser = subparsers.add_parser("register", help="注册现有文件到监控系统")
    register_parser.add_argument(
        "--dir", "-d",
        dest="directories",
        nargs="+",
        help="要注册的目录，默认为所有组件目录"
    )
    register_parser.add_argument(
        "--recursive", "-r",
        dest="recursive",
        action="store_true",
        default=True,
        help="是否递归扫描子目录"
    )
    
    # 扫描项目命令
    scan_parser = subparsers.add_parser("scan", help="扫描项目并生成报告")
    scan_parser.add_argument(
        "--output", "-o",
        dest="output_file",
        help="报告输出文件，默认打印到控制台"
    )
    
    # 检查标准命令
    check_parser = subparsers.add_parser("check", help="检查项目是否符合标准")
    check_parser.add_argument(
        "--autofix", "-a",
        dest="autofix",
        action="store_true",
        help="自动修复发现的问题"
    )
    check_parser.add_argument(
        "--output", "-o",
        dest="output_file",
        help="报告输出文件，默认打印到控制台"
    )
    
    # 创建文件命令
    create_parser = subparsers.add_parser("create", help="安全创建文件")
    create_parser.add_argument(
        "--file", "-f",
        dest="filepath",
        required=True,
        help="要创建的文件路径"
    )
    create_parser.add_argument(
        "--purpose", "-p",
        dest="purpose",
        help="文件用途描述"
    )
    create_parser.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="是否覆盖现有文件"
    )
    create_parser.add_argument(
        "--content", "-c",
        dest="content_file",
        help="包含文件内容的文件路径，如不提供则从标准输入读取"
    )
    
    # 编辑文件命令
    edit_parser = subparsers.add_parser("edit", help="安全编辑文件")
    edit_parser.add_argument(
        "--file", "-f",
        dest="filepath",
        required=True,
        help="要编辑的文件路径"
    )
    edit_parser.add_argument(
        "--reason", "-r",
        dest="reason",
        help="编辑原因"
    )
    edit_parser.add_argument(
        "--content", "-c",
        dest="content_file",
        help="包含新文件内容的文件路径，如不提供则从标准输入读取"
    )
    
    # 删除文件命令
    delete_parser = subparsers.add_parser("delete", help="安全删除文件")
    delete_parser.add_argument(
        "--file", "-f",
        dest="filepath",
        required=True,
        help="要删除的文件路径"
    )
    delete_parser.add_argument(
        "--force",
        dest="force",
        action="store_true",
        help="是否强制删除"
    )
    
    # 添加目录结构优化相关命令
    if directory_optimizer_available:
        # 创建标准目录结构命令
        structure_parser = subparsers.add_parser("structure", help="创建标准目录结构")
        structure_parser.add_argument(
            "--modules", "-m",
            dest="modules",
            nargs="+",
            help="要处理的模块列表，默认为所有主要模块"
        )
        
        # 分析项目结构命令
        analyze_parser = subparsers.add_parser("analyze", help="分析项目目录结构")
        analyze_parser.add_argument(
            "--output", "-o",
            dest="output_file",
            help="报告输出文件，默认打印到控制台"
        )
        
        # 组织文件命令
        organize_parser = subparsers.add_parser("organize", help="组织模块文件到标准目录")
        organize_parser.add_argument(
            "--module", "-m",
            dest="module",
            required=True,
            help="要组织的模块名称"
        )
        organize_parser.add_argument(
            "--dry-run", "-d",
            dest="dry_run",
            action="store_true",
            default=True,
            help="仅模拟操作不实际移动文件"
        )
        organize_parser.add_argument(
            "--apply",
            dest="apply",
            action="store_true",
            help="实际执行文件移动（谨慎使用）"
        )
    
    return parser


def format_json(data):
    """格式化JSON数据为字符串"""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def handle_register(args, guardian):
    """处理注册命令"""
    print(f"开始注册文件...")
    stats = guardian.register_existing_files(
        directories=args.directories,
        recursive=args.recursive
    )
    
    print("\n注册完成:")
    print(f"- 扫描文件数: {stats['scanned']}")
    print(f"- 成功注册数: {stats['registered']}")
    print(f"- 跳过文件数: {stats['skipped']}")
    print(f"- 失败文件数: {stats['failed']}")


def handle_scan(args, guardian):
    """处理扫描命令"""
    print("开始扫描项目...")
    report = guardian.scan_project_and_report()
    
    # 格式化输出
    output = format_json(report)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"报告已保存至: {args.output_file}")
    else:
        print("\n扫描报告:")
        print(output)


def handle_check(args, guardian):
    """处理检查命令"""
    print(f"开始检查项目标准{' (自动修复)' if args.autofix else ''}...")
    results = guardian.enforce_project_standards(auto_fix=args.autofix)
    
    # 格式化输出
    output = format_json(results)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"检查报告已保存至: {args.output_file}")
    else:
        print("\n检查报告:")
        print(output)


def handle_create(args, guardian):
    """处理创建文件命令"""
    # 获取文件内容
    if args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("请输入文件内容 (按Ctrl+D结束):")
        content = sys.stdin.read()
    
    # 确保文件路径存在
    filepath = os.path.abspath(args.filepath)
    
    # 创建文件
    success, message = guardian.safe_create_file(
        filepath=filepath,
        content=content,
        purpose=args.purpose or f"通过组织工具创建的文件",
        allow_overwrite=args.overwrite
    )
    
    if success:
        print(f"成功: {message}")
    else:
        print(f"错误: {message}")


def handle_edit(args, guardian):
    """处理编辑文件命令"""
    # 获取文件内容
    if args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("请输入新的文件内容 (按Ctrl+D结束):")
        content = sys.stdin.read()
    
    # 确保文件路径存在
    filepath = os.path.abspath(args.filepath)
    
    # 编辑文件
    success, message = guardian.safe_edit_file(
        filepath=filepath,
        new_content=content,
        reason=args.reason or f"通过组织工具编辑的文件"
    )
    
    if success:
        print(f"成功: {message}")
    else:
        print(f"错误: {message}")


def handle_delete(args, guardian):
    """处理删除文件命令"""
    # 确保文件路径存在
    filepath = os.path.abspath(args.filepath)
    
    # 删除文件
    success, message = guardian.safe_delete_file(
        filepath=filepath,
        force=args.force
    )
    
    if success:
        print(f"成功: {message}")
    else:
        print(f"错误: {message}")


def handle_structure(args):
    """处理创建标准目录结构命令"""
    if not directory_optimizer_available:
        print("错误: 目录结构优化器不可用")
        return
        
    optimizer = get_directory_optimizer()
    
    print("开始创建标准目录结构...")
    results = optimizer.create_standard_directory_structure()
    
    print("\n创建完成:")
    print(f"- 创建目录数: {len(results['created_dirs'])}")
    print(f"- 已存在目录数: {len(results['existing_dirs'])}")
    print(f"- 错误数: {len(results['errors'])}")
    
    if results['errors']:
        print("\n错误:")
        for error in results['errors']:
            print(f"- {error}")


def handle_analyze(args):
    """处理分析项目结构命令"""
    if not directory_optimizer_available:
        print("错误: 目录结构优化器不可用")
        return
        
    optimizer = get_directory_optimizer()
    
    print("开始分析项目结构...")
    report = optimizer.analyze_project_structure()
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"分析报告已保存至: {args.output_file}")
    else:
        # 打印简要报告
        print(f"\n项目根目录: {report['project_root']}")
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


def handle_organize(args):
    """处理组织文件命令"""
    if not directory_optimizer_available:
        print("错误: 目录结构优化器不可用")
        return
        
    optimizer = get_directory_optimizer()
    
    # 确定是否为dry run模式
    dry_run = True
    if args.apply:
        dry_run = False
    elif args.dry_run:
        dry_run = True
    
    module = args.module
    action = "模拟组织" if dry_run else "组织"
    print(f"开始{action} {module} 模块的文件...")
    
    results = optimizer.organize_files(module, dry_run=dry_run)
    
    if 'error' in results:
        print(f"错误: {results['error']}")
        return
        
    print(f"\n{action}完成:")
    print(f"- 移动文件数: {len(results['moved_files'])}")
    print(f"- 保持不变文件数: {len(results['unchanged_files'])}")
    print(f"- 错误数: {len(results['errors'])}")
    
    if results['errors']:
        print("\n错误:")
        for error in results['errors']:
            print(f"- {error}")
    
    if dry_run:
        print("\n注意: 这是一个模拟操作，未实际移动文件。使用 --apply 参数执行实际移动。")


def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 获取工作区根目录
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 获取文件监控器
    if args.command not in ['structure', 'analyze', 'organize']:
        try:
            guardian = get_guardian(workspace_root)
        except Exception as e:
            print(f"错误: 无法初始化文件监控器: {str(e)}")
            return
    
    # 处理命令
    if args.command == 'register':
        handle_register(args, guardian)
    elif args.command == 'scan':
        handle_scan(args, guardian)
    elif args.command == 'check':
        handle_check(args, guardian)
    elif args.command == 'create':
        handle_create(args, guardian)
    elif args.command == 'edit':
        handle_edit(args, guardian)
    elif args.command == 'delete':
        handle_delete(args, guardian)
    elif args.command == 'structure' and directory_optimizer_available:
        handle_structure(args)
    elif args.command == 'analyze' and directory_optimizer_available:
        handle_analyze(args)
    elif args.command == 'organize' and directory_optimizer_available:
        handle_organize(args)
    else:
        print(f"错误: 未知或不支持的命令: {args.command}")


if __name__ == "__main__":
    main()

"""
量子基因编码: QE-ORG-D9350E15E9DC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98

# 开发团队：中华 ZhoHo ，Claude
"""

