#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目文件列表工具 - 列出项目中的文件

此脚本会扫描项目目录，列出所有符合条件的文件，
可以根据文件类型、大小、修改时间等进行过滤。
"""

import os
import sys
import time
import logging
import argparse
import fnmatch
import datetime
from collections import defaultdict

# 目录设置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(ROOT_DIR, '.logs')

# 创建日志目录
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler(os.path.join(LOG_DIR, 'list_files.log')),
    logging.StreamHandler()
  ]
)
logger = logging.getLogger('List-Project-Files')

# 默认情况下忽略的目录
DEFAULT_IGNORE_DIRS = [
  '.git',
  'reference',
  '__pycache__',
  'node_modules',
  'venv',
  'env',
  '.vscode',
  '.idea',
  '.logs'
]

# 默认情况下忽略的文件
DEFAULT_IGNORE_FILES = [
  '*.pyc',
  '*.pyo',
  '*.so',
  '*.o',
  '*.a',
  '*.log',
  '*.tmp',
  '*.bak',
  '*.swp',
  '.DS_Store',
  'Thumbs.db'
]

def get_file_info(file_path):
  """获取文件信息
  
  Args:
      file_path: 文件路径
      
  Returns:
      dict: 包含文件信息的字典
  """
  stat = os.stat(file_path)
  return {
    'path': file_path,
    'size': stat.st_size,
    'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
    'created': datetime.datetime.fromtimestamp(stat.st_ctime),
    'extension': os.path.splitext(file_path)[1].lower(),
    'type': 'file'
  }

def filter_files(files, args):
  """根据条件过滤文件
  
  Args:
      files: 文件信息列表
      args: 命令行参数
      
  Returns:
      list: 过滤后的文件列表
  """
  filtered = []
  
  for file_info in files:
    file_path = file_info['path']
    
    # 检查是否匹配扩展名
    if args.extension and not file_info['extension'] in args.extension:
      continue
    
    # 检查是否匹配模式
    if args.pattern and not any(fnmatch.fnmatch(os.path.basename(file_path), p) for p in args.pattern):
      continue
    
    # 检查是否排除
    if args.exclude and any(fnmatch.fnmatch(os.path.basename(file_path), p) for p in args.exclude):
      continue
    
    # 检查最小文件大小
    if args.min_size and file_info['size'] < args.min_size:
      continue
    
    # 检查最大文件大小
    if args.max_size and file_info['size'] > args.max_size:
      continue
    
    # 检查最早修改时间
    if args.after and file_info['modified'] < args.after:
      continue
    
    # 检查最晚修改时间
    if args.before and file_info['modified'] > args.before:
      continue
    
    filtered.append(file_info)
  
  return filtered

def scan_directory(dir_path, ignore_dirs=None, ignore_files=None):
  """扫描目录并收集文件信息
  
  Args:
      dir_path: 要扫描的目录路径
      ignore_dirs: 要忽略的目录列表
      ignore_files: 要忽略的文件列表
      
  Returns:
      list: 文件信息列表
  """
  if ignore_dirs is None:
    ignore_dirs = DEFAULT_IGNORE_DIRS
  
  if ignore_files is None:
    ignore_files = DEFAULT_IGNORE_FILES
  
  all_files = []
  
  for root, dirs, files in os.walk(dir_path):
    # 忽略指定目录
    dirs[:] = [d for d in dirs if d not in ignore_dirs and not any(fnmatch.fnmatch(d, p) for p in ignore_dirs)]
    
    for file in files:
      file_path = os.path.join(root, file)
      
      # 忽略指定文件
      if any(fnmatch.fnmatch(file, p) for p in ignore_files):
        continue
      
      try:
        all_files.append(get_file_info(file_path))
      except Exception as e:
        logger.warning(f"无法获取文件信息 {file_path}: {str(e)}")
  
  return all_files

def format_size(size):
  """格式化文件大小
  
  Args:
      size: 字节大小
      
  Returns:
      str: 格式化后的大小字符串
  """
  for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
    if size < 1024.0:
      return f"{size:.2f} {unit}"
    size /= 1024.0
  
  return f"{size:.2f} PB"

def parse_date(date_str):
  """解析日期字符串
  
  Args:
      date_str: 日期字符串（YYYY-MM-DD）
      
  Returns:
      datetime.datetime: 解析后的日期对象
  """
  try:
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')
  except ValueError:
    logger.error(f"无效的日期格式: {date_str}，请使用YYYY-MM-DD格式")
    sys.exit(1)

def parse_size(size_str):
  """解析大小字符串
  
  Args:
      size_str: 大小字符串（例如 1KB, 2MB, 3GB）
      
  Returns:
      int: 字节大小
  """
  units = {
    'b': 1,
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
    'tb': 1024 * 1024 * 1024 * 1024
  }
  
  size_str = size_str.lower()
  
  if size_str.isdigit():
    return int(size_str)
  
  for unit, multiplier in units.items():
    if size_str.endswith(unit):
      try:
        value = float(size_str[:-len(unit)])
        return int(value * multiplier)
      except ValueError:
        logger.error(f"无效的大小格式: {size_str}")
        sys.exit(1)
  
  logger.error(f"无效的大小格式: {size_str}")
  sys.exit(1)

def sort_files(files, sort_by='path', reverse=False):
  """对文件列表进行排序
  
  Args:
      files: 文件信息列表
      sort_by: 排序字段
      reverse: 是否降序排序
      
  Returns:
      list: 排序后的文件列表
  """
  if sort_by == 'path':
    return sorted(files, key=lambda x: x['path'], reverse=reverse)
  elif sort_by == 'name':
    return sorted(files, key=lambda x: os.path.basename(x['path']), reverse=reverse)
  elif sort_by == 'extension':
    return sorted(files, key=lambda x: x['extension'], reverse=reverse)
  elif sort_by == 'size':
    return sorted(files, key=lambda x: x['size'], reverse=reverse)
  elif sort_by == 'modified':
    return sorted(files, key=lambda x: x['modified'], reverse=reverse)
  elif sort_by == 'created':
    return sorted(files, key=lambda x: x['created'], reverse=reverse)
  else:
    logger.warning(f"未知排序字段: {sort_by}，使用路径排序")
    return sorted(files, key=lambda x: x['path'], reverse=reverse)

def group_by_extension(files):
  """按文件扩展名分组
  
  Args:
      files: 文件信息列表
      
  Returns:
      dict: 按扩展名分组的文件字典
  """
  groups = defaultdict(list)
  
  for file_info in files:
    ext = file_info['extension'] or '(无扩展名)'
    groups[ext].append(file_info)
  
  return groups

def print_files(files, args):
  """打印文件列表
  
  Args:
      files: 文件信息列表
      args: 命令行参数
  """
  if not files:
    print("找不到匹配的文件")
    return
  
  if args.group_by == 'extension':
    groups = group_by_extension(files)
    
    for ext, group_files in sorted(groups.items()):
      total_size = sum(file_info['size'] for file_info in group_files)
      print(f"\n扩展名: {ext} ({len(group_files)}个文件, 总大小: {format_size(total_size)})")
      print("-" * 80)
      
      sorted_files = sort_files(group_files, args.sort_by, args.reverse)
      for file_info in sorted_files:
        relative_path = os.path.relpath(file_info['path'], ROOT_DIR)
        modified = file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')
        
        if args.details:
          print(f"{relative_path} ({format_size(file_info['size'])}, 修改时间: {modified})")
        else:
          print(relative_path)
  else:
    sorted_files = sort_files(files, args.sort_by, args.reverse)
    
    for file_info in sorted_files:
      relative_path = os.path.relpath(file_info['path'], ROOT_DIR)
      modified = file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')
      
      if args.details:
        print(f"{relative_path} ({format_size(file_info['size'])}, 修改时间: {modified})")
      else:
        print(relative_path)
  
  total_size = sum(file_info['size'] for file_info in files)
  print(f"\n总计: {len(files)}个文件, 总大小: {format_size(total_size)}")

def parse_arguments():
  """解析命令行参数
  
  Returns:
      argparse.Namespace: 解析后的参数
  """
  parser = argparse.ArgumentParser(
    description='列出项目中的文件'
  )
  
  parser.add_argument(
    '--pattern', '-p',
    type=str,
    nargs='+',
    help='文件匹配模式（支持通配符）'
  )
  
  parser.add_argument(
    '--exclude', '-e',
    type=str,
    nargs='+',
    help='要排除的文件模式（支持通配符）'
  )
  
  parser.add_argument(
    '--extension', '-x',
    type=str,
    nargs='+',
    help='文件扩展名过滤（例如 .py .js .html）'
  )
  
  parser.add_argument(
    '--ignore-dirs',
    type=str,
    nargs='+',
    default=DEFAULT_IGNORE_DIRS,
    help='要忽略的目录'
  )
  
  parser.add_argument(
    '--ignore-files',
    type=str,
    nargs='+',
    default=DEFAULT_IGNORE_FILES,
    help='要忽略的文件模式'
  )
  
  parser.add_argument(
    '--min-size',
    type=parse_size,
    help='最小文件大小（例如 1KB, 2MB）'
  )
  
  parser.add_argument(
    '--max-size',
    type=parse_size,
    help='最大文件大小（例如 1KB, 2MB）'
  )
  
  parser.add_argument(
    '--after',
    type=parse_date,
    help='在此日期之后修改的文件（YYYY-MM-DD）'
  )
  
  parser.add_argument(
    '--before',
    type=parse_date,
    help='在此日期之前修改的文件（YYYY-MM-DD）'
  )
  
  parser.add_argument(
    '--sort-by', '-s',
    choices=['path', 'name', 'extension', 'size', 'modified', 'created'],
    default='path',
    help='排序方式'
  )
  
  parser.add_argument(
    '--reverse', '-r',
    action='store_true',
    help='降序排序'
  )
  
  parser.add_argument(
    '--group-by', '-g',
    choices=['none', 'extension'],
    default='none',
    help='分组方式'
  )
  
  parser.add_argument(
    '--details', '-d',
    action='store_true',
    help='显示详细信息'
  )
  
  parser.add_argument(
    '--output', '-o',
    type=str,
    help='输出结果到文件'
  )
  
  return parser.parse_args()

def main():
  """主函数"""
  args = parse_arguments()
  
  logger.info("===== 项目文件列表工具 =====")
  start_time = time.time()
  
  # 扫描目录
  all_files = scan_directory(ROOT_DIR, args.ignore_dirs, args.ignore_files)
  logger.info(f"扫描完成，找到 {len(all_files)} 个文件")
  
  # 过滤文件
  filtered_files = filter_files(all_files, args)
  logger.info(f"过滤后有 {len(filtered_files)} 个文件")
  
  # 如果指定了输出文件，则将结果写入文件
  if args.output:
    original_stdout = sys.stdout
    try:
      with open(args.output, 'w', encoding='utf-8') as f:
        sys.stdout = f
        print_files(filtered_files, args)
      logger.info(f"结果已写入文件: {args.output}")
    finally:
      sys.stdout = original_stdout
  else:
    print_files(filtered_files, args)
  
  end_time = time.time()
  logger.info(f"处理完成，耗时 {end_time - start_time:.2f} 秒")
  
  return 0

# 主入口
if __name__ == "__main__":
  sys.exit(main()) 