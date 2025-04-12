<<<<<<< HEAD
# QSM服务管理脚本

本目录包含用于管理QSM系统服务的批处理文件。

## 主要文件

- `start_all_fixed.bat` - 启动所有QSM服务（QSM、WeQ、SOM、Ref）
- `stop_all.bat` - 停止所有正在运行的QSM服务
- `conclusion.md` - 服务修复和测试总结报告

## 使用方法

### 启动服务
运行以下命令启动所有服务：
```
scripts\start_all_fixed.bat
```

这将在后台启动以下服务：
- QSM主服务 (端口5331)
- WeQ训练服务 (端口5310)
- WeQ推理服务 (端口5311)
- SOM核心服务 (端口5320)
- SOM市场服务 (端口5321)
- SOM钱包服务 (端口5323)

### 停止服务
运行以下命令停止所有服务：
```
scripts\stop_all.bat
=======
# 日志路径更新工具

此目录包含用于更新Python文件中日志路径的工具，将所有日志文件统一存储到`.logs`目录中。

## 功能特点

- 自动识别并更新Python文件中的日志文件路径
- 支持多种日志配置方式，包括：
  - 直接变量赋值（如`log_file = "xxx.log"`）
  - FileHandler初始化（如`handler = logging.FileHandler("xxx.log")`）
  - 在addHandler中内联的FileHandler（如`logger.addHandler(logging.FileHandler("xxx.log"))`）
  - RotatingFileHandler和其他日志处理器
- 自动添加必要的import语句（如`import os`）
- 提供建议，帮助使用`log_config`模块替换直接的日志配置
- 支持干运行模式，以预览将要进行的更改
- 详细的日志记录，便于追踪更改
- 跨平台支持，提供PowerShell和Shell脚本

## 文件结构

- `update_log_paths.py` - 主脚本，实现日志路径更新功能
- `run_log_update.ps1` - Windows PowerShell运行脚本
- `run_log_update.sh` - Linux/Unix Shell运行脚本
- `test_cases/` - 测试用例目录

## 使用方法

### 基本用法

```bash
# Windows
.\scripts\run_log_update.ps1

# Linux/Unix
./scripts/run_log_update.sh
```

### 测试模式

仅更新测试用例文件：

```bash
# Windows
.\scripts\run_log_update.ps1 --test

# Linux/Unix
./scripts/run_log_update.sh --test
```

### 干运行模式

预览将要进行的更改，不实际修改文件：

```bash
# Windows
.\scripts\run_log_update.ps1 --dry-run

# Linux/Unix
./scripts/run_log_update.sh --dry-run
```

### 添加log_config模块

自动添加log_config模块的导入：

```bash
# Windows
.\scripts\run_log_update.ps1 --add-log-config

# Linux/Unix
./scripts/run_log_update.sh --add-log-config
```

### 详细模式

显示更详细的日志信息：

```bash
# Windows
.\scripts\run_log_update.ps1 --verbose

# Linux/Unix
./scripts/run_log_update.sh --verbose
```

### 排除文件或目录

排除特定的文件或目录：

```bash
# Windows
.\scripts\run_log_update.ps1 --exclude "venv" "backup" "temp"

# Linux/Unix
./scripts/run_log_update.sh --exclude "venv" "backup" "temp"
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
```

## 注意事项

<<<<<<< HEAD
1. 确保已安装Python 3.9或更高版本
2. 使用`py`命令而非`python`命令执行脚本
3. 某些功能可能需要安装Visual C++ Redistributable（torch依赖）

---

量子基因编码: QE-README-8A9B0C1D2E3F
纠缠状态: 活跃
纠缠对象: ['scripts/start_all_fixed.bat', 'scripts/stop_all.bat']
纠缠强度: 0.97

开发团队：中华 ZhoHo ，Claude 
=======
- 脚本将在当前目录及其子目录中查找所有Python文件
- 更新前会询问确认，除非使用`--dry-run`参数
- 所有操作都会记录到`.logs/update_log_paths.log`文件中 
```
量子基因编码: QE-REA-1B0CA8DDEA3E
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
```
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
