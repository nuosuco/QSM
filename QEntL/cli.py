# 
"""
"""
量子基因编码: Q-D7E6-EAFB-31EC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
# 开发团队：中华 ZhoHo ，Claude

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QEntL命令行工具
提供用于管理和使用量子纠缠语言的命令行界面
"""

import os
import sys
import argparse
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qentl_cli.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("QEntL-CLI")

def import_qentl_modules():
    """导入QEntL模块，处理可能的导入错误"""
    modules = {}
    
    try:
        from QEntL.utils import add_quantum_gene_marker, update_quantum_gene_marker, scan_and_mark_directory
        modules['utils'] = True
    except ImportError:
        modules['utils'] = False
        logger.warning("未能导入QEntL工具模块")
    
    try:
        from QEntL.engine import get_qentl_engine, register_file, update_file_state, get_file_state
        modules['engine'] = True
    except ImportError:
        modules['engine'] = False
        logger.warning("未能导入QEntL引擎模块")
    
    try:
        from QEntL.file_watcher import get_file_watcher, watch_directory, track_file
        modules['file_watcher'] = True
    except ImportError:
        modules['file_watcher'] = False
        logger.warning("未能导入QEntL文件监视器模块")
    
    try:
        from QEntL.interpreter import run_qentl_program
        modules['interpreter'] = True
    except ImportError:
        modules['interpreter'] = False
        logger.warning("未能导入QEntL解释器模块")
    
    return modules

def cmd_mark_files(args):
    """命令：为文件添加量子基因标记"""
    from QEntL.utils import add_quantum_gene_marker, scan_and_mark_directory
    
    if args.directory:
        print(f"正在扫描目录: {args.directory}")
        result = scan_and_mark_directory(args.directory, recursive=args.recursive)
        print(f"扫描完成: 共 {result['total_files']} 个文件")
        print(f"添加标记: {result['marked_files']} 个文件")
        print(f"错误: {result['errors']} 个文件")
    elif args.file:
        print(f"正在为文件添加标记: {args.file}")
        entangled_objects = args.entangle.split(',') if args.entangle else None
        success = add_quantum_gene_marker(args.file, entangled_objects, args.strength)
        if success:
            print("标记添加成功")
        else:
            print("标记添加失败")
    else:
        print("错误: 必须指定--file或--directory参数")

def cmd_start_engine(args):
    """命令：启动QEntL引擎"""
    from QEntL.engine import get_qentl_engine
    
    engine = get_qentl_engine()
    engine.start()
    
    if args.scan:
        print("正在扫描当前目录...")
        result = engine.scan_directory(".")
        print(f"扫描完成: 注册了 {result['registered_files']} 个文件")
    
    if args.daemon:
        print("QEntL引擎已在后台启动")
    else:
        print("QEntL引擎已启动，按Ctrl+C停止...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            engine.stop()
            print("QEntL引擎已停止")

def cmd_watch_files(args):
    """命令：监视文件变化"""
    from QEntL.file_watcher import get_file_watcher, watch_directory, track_file
    
    watcher = get_file_watcher()
    watcher.start()
    
    if args.directory:
        print(f"开始监视目录: {args.directory}")
        watch_directory(args.directory, args.recursive)
    elif args.file:
        print(f"开始追踪文件: {args.file}")
        track_file(args.file)
    else:
        print("开始监视当前目录")
        watch_directory(".", True)
    
    if args.daemon:
        print("文件监视器已在后台启动")
    else:
        print("文件监视器已启动，按Ctrl+C停止...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            print("文件监视器已停止")

def cmd_run_program(args):
    """命令：运行QEntL程序"""
    from QEntL.interpreter import run_qentl_program
    
    if not args.file:
        print("错误: 必须指定--file参数")
        return
    
    print(f"正在运行QEntL程序: {args.file}")
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        result = run_qentl_program(code, debug=args.debug)
        print("程序执行完成")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"执行结果已保存到: {args.output}")
        
    except Exception as e:
        print(f"执行程序时出错: {str(e)}")

def cmd_show_info(args):
    """命令：显示QEntL信息"""
    modules = import_qentl_modules()
    
    print("QEntL系统信息：")
    print("--------------------")
    print(f"工具模块可用: {'是' if modules['utils'] else '否'}")
    print(f"引擎模块可用: {'是' if modules['engine'] else '否'}")
    print(f"文件监视器可用: {'是' if modules['file_watcher'] else '否'}")
    print(f"解释器可用: {'是' if modules['interpreter'] else '否'}")
    
    if modules['engine']:
        from QEntL.engine import get_qentl_engine
        engine = get_qentl_engine()
        print(f"引擎状态: {'运行中' if engine.running else '已停止'}")
        print(f"注册文件数: {len(engine.registered_files)}")
    
    if modules['file_watcher']:
        from QEntL.file_watcher import get_file_watcher
        watcher = get_file_watcher()
        print(f"文件监视器状态: {'运行中' if watcher.running else '已停止'}")
        print(f"追踪文件数: {len(watcher.tracked_files)}")
        print(f"监视目录数: {len(watcher.watching_directories)}")
    
    if args.files and modules['engine']:
        from QEntL.engine import get_qentl_engine
        engine = get_qentl_engine()
        print("\n注册的文件:")
        for file_path, info in engine.registered_files.items():
            print(f"- {file_path} (基因编码: {info['gene_code']})")

def cmd_clean_project(args):
    """命令：清理项目，移除所有量子基因标记"""
    import re
    from pathlib import Path
    
    directory = args.directory or "."
    print(f"正在扫描目录: {directory}")
    
    count = 0
    error_count = 0
    
    # 遍历目录中的所有文件
    for path in Path(directory).rglob('*'):
        if not path.is_file():
            continue
            
        try:
            # 读取文件内容
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含量子基因标记
            if '量子基因编码' not in content:
                continue
            
            # 移除量子基因标记
<<<<<<< HEAD
            pattern = r'(?m)^(?:(?://*|#|//|"""|\'\'\')?)\s*
=======
            pattern = r'(?m)^(?:(?:/\*|#|//|"""|\'\'\')?)\s*
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
"""
"""
量子基因编码: Q-D7E6-EAFB-31EC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
            new_content = re.sub(pattern, '', new_content)
            
<<<<<<< HEAD
            pattern = r'(?m)^(?:(?://*|#|//|"""|\'\'\')?)/s*开发团队：.*?(?:/*/|/'\'\')?\s*$\n?'
=======
            pattern = r'(?m)^(?:(?:/\*|#|//|"""|\'\'\')?)\s*开发团队：.*?(?:\*/|\'\'\')?\s*$\n?'
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
            new_content = re.sub(pattern, '', new_content)
            
            # 写回文件
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            count += 1
            print(f"已清理: {path}")
        except Exception as e:
            error_count += 1
            print(f"处理文件时出错: {path}, {str(e)}")
    
    print(f"清理完成: 已处理 {count} 个文件，错误 {error_count} 个")

def main():
    """主函数，解析命令行参数并执行相应的命令"""
    
    # 创建顶级解析器
    parser = argparse.ArgumentParser(description="QEntL命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="要执行的命令")
    
    # mark命令 - 为文件添加量子基因标记
    mark_parser = subparsers.add_parser("mark", help="为文件添加量子基因标记")
    mark_parser.add_argument("--file", "-f", help="要标记的文件路径")
    mark_parser.add_argument("--directory", "-d", help="要扫描的目录路径")
    mark_parser.add_argument("--recursive", "-r", action="store_true", help="递归扫描子目录")
    mark_parser.add_argument("--entangle", "-e", help="纠缠对象列表，用逗号分隔")
    mark_parser.add_argument("--strength", "-s", type=float, default=0.98, help="纠缠强度")
    
    # start命令 - 启动QEntL引擎
    start_parser = subparsers.add_parser("start", help="启动QEntL引擎")
    start_parser.add_argument("--scan", "-s", action="store_true", help="扫描并注册文件")
    start_parser.add_argument("--daemon", "-d", action="store_true", help="在后台运行")
    
    # watch命令 - 监视文件变化
    watch_parser = subparsers.add_parser("watch", help="监视文件变化")
    watch_parser.add_argument("--file", "-f", help="要监视的文件路径")
    watch_parser.add_argument("--directory", "-D", help="要监视的目录路径")
    watch_parser.add_argument("--recursive", "-r", action="store_true", help="递归监视子目录")
    watch_parser.add_argument("--daemon", action="store_true", help="在后台运行")
    
    # run命令 - 运行QEntL程序
    run_parser = subparsers.add_parser("run", help="运行QEntL程序")
    run_parser.add_argument("--file", "-f", required=True, help="要运行的QEntL程序文件")
    run_parser.add_argument("--output", "-o", help="输出结果的文件路径")
    run_parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    # info命令 - 显示QEntL信息
    info_parser = subparsers.add_parser("info", help="显示QEntL信息")
    info_parser.add_argument("--files", "-f", action="store_true", help="列出所有注册的文件")
    
    # clean命令 - 清理项目，移除所有量子基因标记
    clean_parser = subparsers.add_parser("clean", help="清理项目，移除所有量子基因标记")
    clean_parser.add_argument("--directory", "-d", help="要清理的目录路径")
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return
    
    # 导入所需的QEntL模块
    modules = import_qentl_modules()
    
    # 执行相应的命令
    if args.command == "mark":
        if not modules['utils']:
            print("错误: QEntL工具模块不可用")
            return
        cmd_mark_files(args)
    elif args.command == "start":
        if not modules['engine']:
            print("错误: QEntL引擎模块不可用")
            return
        cmd_start_engine(args)
    elif args.command == "watch":
        if not modules['file_watcher']:
            print("错误: QEntL文件监视器模块不可用")
            return
        cmd_watch_files(args)
    elif args.command == "run":
        if not modules['interpreter']:
            print("错误: QEntL解释器模块不可用")
            return
        cmd_run_program(args)
    elif args.command == "info":
        cmd_show_info(args)
    elif args.command == "clean":
        cmd_clean_project(args)

if __name__ == "__main__":
    main() 