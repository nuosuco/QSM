# project_manager

## 模块说明
项目自动归类与管理系统
功能：
1. 自动归类文件到合适的目录
2. 监控项目性能，防止系统卡顿
3. 智能搜索文件
4. 自动备份修改的文件

## 功能概述

### 类

- `ProjectManager`
- `BackupSystem`
- `IndexingSystem`
- `PerformanceMonitor`
- `FileOrganizer`
- `FileChangeHandler`

### 函数

- `__init__`
- `load_config`
- `save_config`
- `create_directory_structure`
- `start`
- `start_file_monitoring`
- `find_file`
- `backup_file`
- `stop`
- `__init__`
- `start`
- `backup_worker`
- `backup_single_file`
- `cleanup_old_backups`
- `schedule_auto_backup`
- `create_full_backup`
- `stop`
- `__init__`
- `build_index`
- `save_index`
- `get_file_category`
- `schedule_index_rebuild`
- `search`
- `_calculate_relevance`
- `__init__`
- `start`
- `monitor_loop`
- `check_thresholds`
- `take_action`
- `clean_memory`
- `clean_disk`
- `stop`
- `__init__`
- `organize_files`
- `organize_file`
- `__init__`
- `on_modified`
- `on_created`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 14:51:57*