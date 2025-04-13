# 量子超位态模型 (QSM) 项目

量子超位态模型是一个基于量子技术的综合系统，包含多个协同工作的组件，提供量子计算、量子社交、量子经济和自反省管理功能。

## 项目架构

该项目由以下主要模块组成：

- **QSM** - 量子超位态模型：核心服务，管理量子状态和预测功能
- **WeQ** - 量子社交引擎：管理量子社交网络和情感分析
- **SOM** - 量子自组织市场：管理量子经济和市场系统
- **Ref** - 量子自反省管理：监控和优化系统性能
- **World** - 世界服务：管理用户界面和数据可视化

## 技术栈

- 量子编程语言：QEntl (Quantum Entangled Language)
- 量子文件格式：.qpy, .qjs, .qcss, .qentl 等
- 量子基因编码和纠缠信道技术
- RESTful API 服务

## 快速开始

### Windows 系统

1. 确保安装了 Python 3.8 或更高版本
2. 双击 `start_project.bat` 启动项目
3. 访问 http://localhost:5999 查看服务状态
4. 使用 `stop_project.bat` 停止项目

### Linux/MacOS 系统

1. 确保安装了 Python 3.8 或更高版本
2. 赋予脚本执行权限：`chmod +x start_project.sh stop_project.sh`
3. 运行 `./start_project.sh` 启动项目
4. 访问 http://localhost:5999 查看服务状态
5. 使用 `./stop_project.sh` 停止项目

## 项目管理

项目提供了量子管理器脚本，用于项目结构分析、量子转换和纠缠管理：

```
python scripts/quantum_manager.qpy <命令> [参数]
```

可用命令：
- `structure`: 分析项目结构
- `convert`: 转换文件为量子格式
- `entangle`: 分析量子纠缠关系
- `monitor`: 监控量子组件性能
- `all`: 运行所有管理功能

## 服务 API

所有服务均提供 RESTful API 接口：

- QSM API: http://localhost:5000
- WeQ API: http://localhost:5001
- SOM API: http://localhost:5002
- Ref API: http://localhost:5003
- World: http://localhost:5004

主控制器 API: http://localhost:5999
- `/status`: 获取服务状态
- `/health`: 获取服务健康状态
- `/start/<service_id>`: 启动服务
- `/stop/<service_id>`: 停止服务
- `/restart/<service_id>`: 重启服务
- `/restart_all`: 重启所有服务

## 项目结构

```
QSM/                   # 项目根目录
├── QSM/               # 量子超位态模型
│   ├── api/           # API服务
│   ├── models/        # 模型定义
│   └── services/      # 服务实现
├── WeQ/               # 量子社交引擎
│   ├── api/
│   └── models/
├── SOM/               # 量子自组织市场
│   ├── api/
│   └── models/
├── Ref/               # 量子自反省管理
│   └── api/
├── world/             # 世界服务
│   ├── templates/
│   └── static/
├── scripts/           # 工具脚本
│   └── utils/
├── config/            # 配置文件
├── .logs/             # 日志文件
├── reference/         # 参考文件
├── run.qpy            # 主程序入口
├── start_project.bat  # Windows启动脚本
├── stop_project.bat   # Windows停止脚本
├── start_project.sh   # Linux/MacOS启动脚本
└── stop_project.sh    # Linux/MacOS停止脚本
``` 