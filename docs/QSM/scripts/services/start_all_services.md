# start_all_services

## 模块说明
统一服务启动脚本

该脚本用于启动所有QSM相关服务，包括QSM服务、WeQ服务、SOM服务和Ref服务。
脚本会调用每个模块自己的启动脚本，而不是直接启动各个服务。
支持并行启动多个服务，并提供日志记录功能。

用法:
    python scripts/services/start_all_services.py [--parallel] [--services SERVICE1 SERVICE2 ...]

参数:
    --parallel: 并行启动所有服务
    --services: 指定要启动的服务，可选值: qsm, weq, som, ref, all (默认: all)
    --retry: 启动失败时的重试次数 (默认: 3)
    --health-check: 是否进行健康检查 (默认: True)
    --health-check-interval: 健康检查间隔(秒) (默认: 30)

## 功能概述

### 类

- `ServiceHealthCheck`

### 函数

- `__init__`
- `start`
- `stop`
- `_health_check_loop`
- `_check_all_services`
- `_check_service_health`
- `_handle_service_failure`
- `get_python_executable`
- `create_log_files`
- `start_module`
- `restart_module`
- `start_module_thread`
- `start_modules_parallel`
- `start_modules_sequential`
- `stop_all_modules`
- `parse_args`
- `main`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 15:31:10*