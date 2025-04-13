#!/usr/bin/env python3
import os
import sys
import argparse
import json
from datetime import datetime

from utils.file_organization_guardian import get_guardian


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
        print("请输入新文件内容 (按Ctrl+D结束):")
        content = sys.stdin.read()
    
    # 确保文件路径存在
    filepath = os.path.abspath(args.filepath)
    
    # 编辑文件
    success, message = guardian.safe_edit_file(
        filepath=filepath,
        new_content=content,
        reason=args.reason
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


def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助
    if not args.command:
        parser.print_help()
        return
    
    # 获取当前工作目录
    workspace_root = os.path.abspath(os.getcwd())
    
    # 获取文件组织监护器实例
    guardian = get_guardian(
        workspace_root=workspace_root,
        registry_path='Ref/data/file_registry.json',
        backup_dir='Ref/backup/files'
    )
    
    # 根据命令执行相应的处理
    command_handlers = {
        'register': handle_register,
        'scan': handle_scan,
        'check': handle_check,
        'create': handle_create,
        'edit': handle_edit,
        'delete': handle_delete
    }
    
    if args.command in command_handlers:
        command_handlers[args.command](args, guardian)
    else:
        print(f"未知命令: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main() 

"""

"""
量子基因编码: QE-ORG-D9350E15E9DC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
