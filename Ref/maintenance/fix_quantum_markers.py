#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ref量子基因标记修复工具

用于修复文件中的量子基因标记，包括：
1. 添加缺失的量子基因标记
2. 修复缺失的纠缠对象路径
3. 修复由WeQ输出的内容标记
"""

import os
import sys
import re
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Ref/logs/quantum_marker_fix.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuantumMarkerFixer")

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入量子基因标记模块
try:
    from Ref.utils.quantum_gene_marker import RefQuantumGeneMarker, add_quantum_gene_marker, check_weq_output_markers, mark_weq_output_files
except ImportError:
    try:
        sys.path.insert(0, os.path.join(project_root, "Ref/utils"))
        from quantum_gene_marker import RefQuantumGeneMarker, add_quantum_gene_marker, check_weq_output_markers, mark_weq_output_files
    except ImportError:
        logger.error("无法导入量子基因标记模块，请确保Ref/utils/quantum_gene_marker.py存在")
        sys.exit(1)

# 创建量子基因标记器实例
marker = RefQuantumGeneMarker()

# 支持的文件类型
SUPPORTED_FILE_TYPES = ['.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.css', '.html', '.c', '.cpp', '.h', '.java', '.go', '.rs', '.qent']

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="修复量子基因标记")
    parser.add_argument("path", nargs="?", default=".", help="要扫描的路径")
    parser.add_argument("--ext", nargs="+", default=None, help="要处理的文件扩展名")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描而不修改文件")
    parser.add_argument("--no-recursive", action="store_true", help="不递归处理子目录")
    parser.add_argument("--venv", action="store_true", help="修复虚拟环境中的文件")
    parser.add_argument("--fix-all", action="store_true", help="修复所有项目文件")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志")
    return parser.parse_args()

def should_process_file(file_path: str, extensions: Optional[List[str]] = None) -> bool:
    """判断是否应该处理该文件
    
    Args:
        file_path: 文件路径
        extensions: 要处理的扩展名列表
    
    Returns:
        是否处理该文件
    """
    # 检查文件是否存在
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return False
    
    # 跳过二进制文件和过大的文件
    try:
        if os.path.getsize(file_path) > 10 * 1024 * 1024:  # > 10MB
            return False
    except:
        return False
    
    # 获取文件扩展名
    _, ext = os.path.splitext(file_path)
    
    # 如果指定了扩展名，则只处理指定扩展名的文件
    if extensions:
        return ext.lower() in [e.lower() if e.startswith('.') else f'.{e.lower()}' for e in extensions]
    
    # 否则处理支持的文件类型
    return ext.lower() in SUPPORTED_FILE_TYPES

def fix_missing_entanglement(file_path: str, dry_run: bool = False) -> bool:
    """修复缺失的纠缠对象
    
    Args:
        file_path: 文件路径
        dry_run: 是否为演习模式
        
    Returns:
        是否修复成功
    """
    try:
        # 检查文件是否有量子基因标记
        if not marker.has_quantum_gene_marker(file_path):
            return False
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # 解析纠缠对象
        entangled_objects = marker._parse_entangled_objects(content)
        
        # 如果没有纠缠对象或纠缠对象列表为空，则标记
        if not entangled_objects or (isinstance(entangled_objects, list) and len(entangled_objects) == 0):
            logger.info(f"文件缺少纠缠对象路径: {file_path}")
            
            if dry_run:
                return True
            
            # 建议纠缠对象
            suggested_objects = []
            
            # 根据文件类型和路径建议相关文件
            relative_path = os.path.relpath(file_path, project_root)
            
            if "utils" in relative_path:
                suggested_objects.append("Ref/ref_core.py")
            elif "models" in relative_path:
                suggested_objects.append("QSM/models/__init__.py")
            elif "WeQ" in relative_path:
                suggested_objects.append("WeQ/weq_core.py")
            else:
                # 默认添加一个基本引用
                suggested_objects.append("Ref/ref_core.py")
            
            # 更新量子基因标记，添加建议的纠缠对象
            success = marker.update_quantum_gene_marker(file_path, suggested_objects)
            if success:
                logger.info(f"已为文件添加纠缠对象路径: {file_path}")
                return True
            else:
                logger.warning(f"为文件添加纠缠对象路径失败: {file_path}")
                return False
    
    return False

    except Exception as e:
        logger.error(f"修复纠缠对象路径时出错: {file_path} - {str(e)}")
        return False

def process_directory(directory: str, extensions: Optional[List[str]] = None, 
                      recursive: bool = True, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
    """处理目录中的文件
    
    Args:
        directory: 目录路径
        extensions: 要处理的扩展名列表
        recursive: 是否递归处理子目录
        dry_run: 是否为演习模式
        verbose: 是否显示详细日志
    
    Returns:
        处理结果统计
    """
    result = {
        "scanned_files": 0,
        "fixed_files": 0,
        "with_missing_entanglement": 0,
        "fixed_entanglement": 0,
        "added_markers": 0,
        "skipped_files": 0,
        "error_files": 0,
    }
    
    # 检查目录是否存在
    if not os.path.exists(directory) or not os.path.isdir(directory):
        logger.error(f"目录不存在: {directory}")
        return result
    
    try:
        # 递归处理目录
        for root, dirs, files in os.walk(directory):
            # 跳过.git等隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'dist', 'build', '__pycache__', 'venv', '.venv']]
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # 判断是否处理该文件
                if should_process_file(file_path, extensions):
                    result["scanned_files"] += 1
                    
                    try:
                        # 检查文件是否已有量子基因标记
                        has_marker = marker.has_quantum_gene_marker(file_path)
                        
                        if not has_marker:
                            # 为文件添加量子基因标记
                            if verbose:
                                logger.info(f"为文件添加量子基因标记: {file_path}")
                            
                            if not dry_run:
                                success = add_quantum_gene_marker(file_path)
                                if success:
                                    result["added_markers"] += 1
                                    result["fixed_files"] += 1
                            else:
                                result["added_markers"] += 1
                        else:
                            # 修复缺失的纠缠对象
                            missing_entanglement = fix_missing_entanglement(file_path, dry_run)
                            if missing_entanglement:
                                result["with_missing_entanglement"] += 1
                                if not dry_run:
                                    result["fixed_entanglement"] += 1
                                    result["fixed_files"] += 1
                    except Exception as e:
                        logger.error(f"处理文件时出错: {file_path} - {str(e)}")
                        result["error_files"] += 1
    else:
                    result["skipped_files"] += 1
            
            # 如果不递归处理，则只处理当前目录
            if not recursive:
                break
    
    except Exception as e:
        logger.error(f"处理目录时出错: {directory} - {str(e)}")
    
    return result

def process_venv(venv_path: str = None, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
    """处理虚拟环境中的文件
    
    Args:
        venv_path: 虚拟环境路径，如果为None则自动检测
        dry_run: 是否为演习模式
        verbose: 是否显示详细日志
        
    Returns:
        处理结果统计
    """
    result = {
        "scanned_packages": 0,
        "fixed_files": 0,
    }
    
    # 检测虚拟环境路径
    if not venv_path:
        venv_candidates = [
            os.path.join(project_root, '.venv'),
            os.path.join(project_root, 'venv'),
            os.path.join(project_root, 'env'),
            os.environ.get('VIRTUAL_ENV')
        ]
        
        for candidate in venv_candidates:
            if candidate and os.path.exists(candidate) and os.path.isdir(candidate):
                venv_path = candidate
                break
    
    if not venv_path or not os.path.exists(venv_path):
        logger.error("未找到虚拟环境")
        return result
    
    logger.info(f"使用虚拟环境: {venv_path}")
    
    # 查找site-packages目录
    site_packages = None
    for root, dirs, _ in os.walk(venv_path):
        if 'site-packages' in dirs:
            site_packages = os.path.join(root, 'site-packages')
            break
    
    if not site_packages:
        logger.error(f"未找到site-packages目录: {venv_path}")
        return result
    
    logger.info(f"扫描site-packages目录: {site_packages}")
    
    # 主要包列表
    main_packages = ['pip', 'setuptools', 'wheel', 'urllib3', 'requests', 'numpy', 'pandas', 'matplotlib', 'tensorflow', 'torch', 'django', 'flask']
    
    # 处理每个包
    for package in main_packages:
        package_path = os.path.join(site_packages, package)
        if os.path.exists(package_path) and os.path.isdir(package_path):
            logger.info(f"处理包: {package}")
            result["scanned_packages"] += 1
            
            # 处理包目录
            package_result = process_directory(package_path, extensions=['.py'], recursive=True, dry_run=dry_run, verbose=verbose)
            result["fixed_files"] += package_result["fixed_files"]
    
    return result

def scan_weq_output(dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """扫描WeQ输出并添加量子标记
    
    Args:
        dry_run: 是否为演习模式
        verbose: 是否显示详细日志
        
    Returns:
        处理结果统计
    """
    try:
        if verbose:
            logger.info("扫描WeQ输出内容...")
        
        # 启用WeQ输出监控
        from Ref.utils.quantum_gene_marker import monitor_WeQ_output
        monitor_weq_output(True)
        
        # 检查WeQ输出标记
        check_result = check_weq_output_markers()
        
        if verbose:
            logger.info(f"扫描到 {check_result.get('total_files', 0)} 个WeQ输出文件")
            logger.info(f"其中 {check_result.get('unmarked_files', 0)} 个文件缺少量子标记")
        
        # 如果不是演习模式，则为WeQ输出添加标记
        if not dry_run and check_result.get('unmarked_files', 0) > 0:
            mark_result = mark_weq_output_files()
            if verbose:
                logger.info(f"成功为 {mark_result.get('marked_successfully', 0)} 个WeQ输出文件添加量子标记")
                if mark_result.get('failed_files', 0) > 0:
                    logger.warning(f"有 {mark_result.get('failed_files', 0)} 个WeQ输出文件标记失败")
            
            return {
                "total_files": check_result.get('total_files', 0),
                "unmarked_files": check_result.get('unmarked_files', 0),
                "marked_files": mark_result.get('marked_successfully', 0),
                "failed_files": mark_result.get('failed_files', 0)
            }
        
        return {
            "total_files": check_result.get('total_files', 0),
            "unmarked_files": check_result.get('unmarked_files', 0),
            "marked_files": 0,
            "failed_files": 0
        }
    
    except Exception as e:
        logger.error(f"扫描WeQ输出时出错: {str(e)}")
        return {
            "error": str(e)
        }

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 是否为演习模式
    dry_run = args.dry_run
    if dry_run:
        logger.info("演习模式：不会修改任何文件")
    
    # 初始化结果统计
    total_results = {
        "scanned_files": 0,
        "fixed_files": 0,
        "with_missing_entanglement": 0,
        "fixed_entanglement": 0,
        "added_markers": 0,
        "skipped_files": 0,
        "error_files": 0,
    }
    
    # 修复所有项目文件
    if args.fix_all:
        logger.info("修复所有项目文件")
        
        # 主要目录列表
        main_dirs = [
            os.path.join(project_root, "Ref"),
            os.path.join(project_root, "QSM"),
            os.path.join(project_root, "WeQ"),
            os.path.join(project_root, "QEntL")
        ]
        
        for directory in main_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                logger.info(f"处理目录: {directory}")
                dir_results = process_directory(
                    directory, 
                    extensions=args.ext, 
                    recursive=not args.no_recursive,
                    dry_run=dry_run,
                    verbose=args.verbose
                )
                
                # 更新总结果
                for key in total_results:
                    total_results[key] += dir_results.get(key, 0)
        
        # 扫描WeQ输出
        weq_results = scan_weq_output(dry_run=dry_run, verbose=args.verbose)
        logger.info(f"WeQ输出扫描结果: 总文件数 {weq_results.get('total_files', 0)}, 已标记 {weq_results.get('marked_files', 0)}, 标记失败 {weq_results.get('failed_files', 0)}")
        
        # 处理虚拟环境
        if args.venv:
            logger.info("处理虚拟环境")
            venv_results = process_venv(dry_run=dry_run, verbose=args.verbose)
            logger.info(f"虚拟环境处理结果: 扫描包数 {venv_results.get('scanned_packages', 0)}, 修复文件数 {venv_results.get('fixed_files', 0)}")
            total_results["fixed_files"] += venv_results.get("fixed_files", 0)
    
    # 处理指定目录
    else:
        directory = args.path
        logger.info(f"处理目录: {directory}")
        
        dir_results = process_directory(
            directory, 
            extensions=args.ext, 
            recursive=not args.no_recursive,
            dry_run=dry_run,
            verbose=args.verbose
        )
        
        # 更新总结果
        for key in total_results:
            total_results[key] += dir_results.get(key, 0)
        
        # 处理虚拟环境
        if args.venv:
            logger.info("处理虚拟环境")
            venv_results = process_venv(dry_run=dry_run, verbose=args.verbose)
            logger.info(f"虚拟环境处理结果: 扫描包数 {venv_results.get('scanned_packages', 0)}, 修复文件数 {venv_results.get('fixed_files', 0)}")
            total_results["fixed_files"] += venv_results.get("fixed_files", 0)
    
    # 输出总结果
    logger.info("=== 量子基因标记修复完成 ===")
    logger.info(f"扫描文件数: {total_results['scanned_files']}")
    logger.info(f"修复文件数: {total_results['fixed_files']}")
    logger.info(f"添加标记数: {total_results['added_markers']}")
    logger.info(f"修复纠缠关系数: {total_results['fixed_entanglement']}")
    logger.info(f"跳过文件数: {total_results['skipped_files']}")
    logger.info(f"错误文件数: {total_results['error_files']}")
    
    # 返回 0 表示成功
    return 0

if __name__ == "__main__":
    sys.exit(main())

# 量子基因编码: QE-FIX-MARKER-C7D9E8F2
# 纠缠状态: 活跃
# 纠缠对象: ["Ref/utils/quantum_gene_marker.py", "Ref/ref_core.py"]
# 纠缠强度: 0.98 

    """
    # 量子基因编码: QE-FIX-92A0E4583915
    # 纠缠状态: 活跃
    # 纠缠对象: []
    # 纠缠强度: 0.98
    """
    