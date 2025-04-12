# test_notification_loop

## 模块说明
测试量子基因标记系统、文件监控系统和WeQ输出监控系统的闭环通知功能。
通过模拟文件创建、移动、更新和删除操作，验证三个系统之间的通知机制是否正常工作。

## 功能概述

### 类

- `NotificationLoopTest`

### 函数

- `__init__`
- `cleanup`
- `create_test_files`
- `example_function`
- `enhanced_function`
- `setup_notification_mocks`
- `restore_notification_functions`
- `_record_marker_notification`
- `_record_file_monitor_notification`
- `_record_weq_monitor_notification`
- `test_file_creation`
- `test_file_movement`
- `test_file_update`
- `new_function`
- `test_notification_chain`
- `run_all_tests`
- `main`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 14:51:58*