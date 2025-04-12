# cleanup_structure

## 模块说明
项目结构清理脚本

该脚本用于清理项目结构，删除冗余文件和目录，合并重复目录，优化项目结构。
执行前会进行确认，确保不会误删重要文件。

用法:
    python scripts/cleanup_structure.py [--auto-confirm]
        --auto-confirm: 自动确认执行清理操作，无需手动确认

## 功能概述

### 类


### 函数

- `parse_args`
- `is_redundant_file`
- `is_redundant_dir`
- `find_redundant_files`
- `find_redundant_dirs`
- `should_merge_dir`
- `get_merge_target`
- `merge_directory`
- `update_imports_in_file`
- `update_imports`
- `print_plan`
- `get_confirmation`
- `execute_cleanup`
- `main`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 14:51:58*