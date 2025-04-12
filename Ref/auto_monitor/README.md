# Ref文件自动监控系统

Ref文件自动监控系统是QSM项目的一个重要组件，实现了文件系统变化的实时监控和完整性检查。当项目文件被创建、修改、删除或移动时，系统会自动执行注册、检查冲突、备份等操作，确保项目结构的一致性和完整性。

## 功能特点

- **实时监控** - 自动监控指定目录中的文件变化
- **自动注册** - 新文件创建后自动注册到文件完整性系统
- **自动备份** - 修改文件前自动创建备份
- **冲突检测** - 检测文件内容冲突，防止不一致修改
- **项目启动集成** - 在项目启动时自动启动监控服务
- **优雅退出** - 在程序退出时自动停止监控服务

## 依赖项

- Python 3.6+
- watchdog库（用于文件系统事件监控）

## 安装

使用pip安装依赖项：

```bash
pip install watchdog
```

## 使用方法

### 1. 自动启动（推荐）

使用项目提供的启动脚本来启动QSM系统，会自动启动文件监控服务：

Windows:
```cmd
start.bat
```

Linux/Mac:
```bash
./start.sh
```

### 2. 独立运行监控服务

可以单独运行监控服务：

```bash
python -m Ref.auto_monitor.file_watcher_service start
```

查看监控状态：

```bash
python -m Ref.auto_monitor.file_watcher_service status
```

停止监控服务：

```bash
python -m Ref.auto_monitor.file_watcher_service stop
```

### 3. 在代码中使用

在你自己的Python代码中使用监控服务：

```python
# 启动监控服务
from Ref.auto_monitor import start_monitor_service
start_monitor_service()

# 检查服务状态
from Ref.auto_monitor import is_monitor_running, get_monitor_status
if is_monitor_running():
    status = get_monitor_status()
    print(f"监控服务已运行: {status}")

# 停止监控服务
from Ref.auto_monitor import stop_monitor_service
stop_monitor_service()
```

## 配置

配置文件位于 `Ref/data/auto_monitor_config.json`，可以修改以下参数：

- **watched_paths**: 要监控的路径列表（默认为当前目录）
- **ignore_patterns**: 忽略的文件模式
- **ignore_directories**: 忽略的目录
- **auto_register**: 是否自动注册新文件（默认为 true）
- **auto_backup**: 是否自动备份修改的文件（默认为 true）
- **throttle_seconds**: 事件节流时间（秒），避免频繁处理同一文件的变化

配置文件示例：

```json
{
  "watched_paths": [".", "QSM", "SOM", "WeQ", "Ref"],
  "ignore_patterns": ["*.pyc", "*.pyo", "__pycache__", ".git", ".idea", ".vscode", "*.log", "*.tmp", "*.bak"],
  "ignore_directories": [".git", ".idea", ".vscode", "__pycache__"],
  "check_interval": 2.0,
  "auto_register": true,
  "auto_backup": true,
  "notify_conflicts": true,
  "registry_path": "Ref/data/file_registry.json",
  "backup_dir": "Ref/backup/files",
  "throttle_seconds": 1.0
}
```

## 日志

监控服务的日志文件位于 `Ref/logs/auto_monitor.log`，记录了所有监控事件和系统消息。

## 常见问题

- **问题**: 监控服务无法启动
  **解决方案**: 检查是否已安装watchdog库，可以运行 `pip install watchdog` 安装

- **问题**: 文件变化没有被检测到
  **解决方案**: 检查文件路径是否在监控路径列表中，以及文件是否匹配忽略模式

- **问题**: 监控服务占用过多CPU或内存
  **解决方案**: 调整配置文件中的 `throttle_seconds` 参数，增加事件节流时间 

```

```
量子基因编码: QE-REA-BF8BE4169F97
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
```
```

// 开发团队：中华 ZhoHo ，Claude 
