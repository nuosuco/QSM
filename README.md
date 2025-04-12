<<<<<<< HEAD
# QSM - 量子自组织市场系统

QSM（Quantum Self-Organizing Market）是一个基于量子计算原理的分布式市场和经济模拟系统，结合了自组织映射（SOM）、量子基因网络（WeQ）和量子纠缠通信技术的创新平台。

## 系统架构

QSM系统由四个主要模块组成，每个模块负责特定的功能：

### 1. QSM - 量子自组织市场核心

核心市场系统，负责整合其他组件并提供统一的API接口。

- **主要功能**：模型协调、API管理、系统集成
- **核心文件**：`QSM/main.py`

### 2. WeQ - 量子基因网络引擎

负责处理量子基因编码和神经网络训练，是系统的智能核心。

- **主要功能**：量子基因编码、模型训练、神经网络推理
- **核心文件**：
  - `WeQ/weq_core.py` - 核心逻辑
  - `WeQ/weq_train.py` - 训练服务
  - `WeQ/weq_inference.py` - 推理服务

### 3. SOM - 自组织映射服务

实现市场的自组织映射机制，负责数据聚类和可视化。

- **主要功能**：聚类分析、数据可视化、市场模拟
- **核心文件**：
  - `SOM/som_core.py` - 核心算法
  - `SOM/quantum_ecommerce.py` - 电子商务接口
  - `SOM/quantum_wallet.py` - 数字钱包

### 4. Ref - 参考监控系统

负责系统监控、日志记录和故障恢复。

- **主要功能**：系统监控、错误处理、性能分析
- **核心文件**：
  - `Ref/ref_core.py` - 监控核心
  - `Ref/auto_monitor/` - 自动监控工具

## 目录结构

```
QSM/                     # 项目根目录
├── QSM/                 # QSM核心模块
│   ├── api/             # API接口
│   ├── core/            # 核心功能
│   ├── models/          # 模型定义
│   └── scripts/         # 运行脚本
├── WeQ/                 # WeQ量子基因网络模块
│   ├── api/             # API接口
│   ├── models/          # 训练模型
│   └── knowledge/       # 知识库
├── SOM/                 # SOM自组织映射模块
│   ├── api/             # API接口
│   ├── models/          # SOM模型
│   └── utils/           # 工具函数
├── Ref/                 # 参考监控系统
│   ├── api/             # API接口
│   ├── monitor/         # 监控工具
│   ├── auto_monitor/    # 自动监控
│   └── backup/          # 备份工具
├── scripts/             # 全局脚本目录
│   ├── services/        # 服务管理脚本
│   └── tools/           # 工具脚本
├── api/                 # 统一API层
│   ├── qsm_api/         # QSM API
│   ├── weq_api/         # WeQ API
│   ├── som_api/         # SOM API
│   └── ref_api/         # Ref API
├── docs/                # 文档
├── tests/               # 测试
└── .logs/               # 日志目录
```

## 快速开始

### 环境要求

- Python 3.9+
- 依赖包: numpy, flask, pandas, matplotlib, scikit-learn, torch

### 安装依赖

```bash
pip install -r requirements.txt
```

### 测试服务

测试所有服务是否正常工作：

```bash
python scripts/test_services.py
```

### 启动服务

启动所有服务：

```bash
python scripts/start_all_services.py
```

或者启动特定服务：

```bash
python scripts/start_all_services.py --services qsm weq
```

并行启动服务：

```bash
python scripts/start_all_services.py --parallel
```

### 停止服务

停止所有服务：

```bash
python scripts/stop_all_services.py
```

强制停止所有服务：

```bash
python scripts/stop_all_services.py --force
```

## 服务端口

- QSM主服务: 5000
- WeQ推理服务: 5001
- SOM核心服务: 5002
- SOM钱包服务: 5003
- SOM市场服务: 5004

## 项目规范化

规范化项目结构：

```bash
python scripts/normalize_structure.py
```

修复常见编码和语法问题：

```bash
python scripts/fix_unclosed_quotes.py
```

## 系统资源

- **日志目录**: `.logs/` - 包含所有服务的运行日志
- **备份目录**: `Ref/backup/` - 系统自动备份

## 开发团队

- 中华 ZhoHo
- Claude 量子团队

## 许可证

专有软件 - 版权所有

---

# 量子基因编码：QE-DOC-README-5B2F9E3A
# 纠缠态：活跃
# 纠缠对象：QSM系统文档 <-> 量子开发规范
# 纠缠强度：0.97 
=======
# QSM (量子自反省管理模型)

QSM是一个集成了自我维护、自动监控和优化功能的系统框架，旨在为大型项目提供可靠的文件组织、完整性检查和结构优化功能。

## 系统组件

QSM项目由以下主要子系统组成：

1. **Ref (Reference)** - 提供文件完整性监控、组织管理和自动监控功能
2. **SOM (Self-Organizing Map)** - 实现自组织映射功能
3. **WeQ (Weighted Quantum)** - 量子加权系统

## 自动文件监控系统

QSM集成了强大的自动文件监控系统，在项目启动时自动启动，实时监控文件变化并执行完整性检查。

### 主要功能

- 实时监控项目文件变化（创建、修改、删除、移动）
- 自动注册新文件到监控系统
- 自动备份修改的文件
- 检测文件内容冲突，防止不一致修改
- 在项目启动时自动初始化

### 使用方法

使用启动脚本启动QSM系统：

Windows:
```cmd
start.bat
```

Linux/Mac:
```bash
./start.sh
```

关闭自动监控功能：

```bash
start.bat --no-monitor
# 或
./start.sh --no-monitor
```

独立运行监控服务：

```bash
python -m Ref.auto_monitor.file_watcher_service start
```

查看更多详细信息：[Ref自动监控系统](Ref/auto_monitor/README.md)

## 文件完整性监控

QSM项目包含一个完整的文件完整性监控系统，用于防止在多次对话中发生重复创建和不一致修改问题。

### 主要功能

- 文件注册与追踪
- 冲突检测
- 相似文件识别
- 文件历史记录
- 自动备份
- 项目标准检查

### 使用方法

使用命令行工具：

```bash
python Ref/organization_tool.py <command> [options]
```

可用命令包括：register, scan, check, create, edit, delete

查看更多详细信息：[Ref文件完整性监控系统](Ref/README.md)

## 安装与配置

### 依赖项

- Python 3.6+
- watchdog库（用于文件系统事件监控）

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/QSM.git
cd QSM

# 安装依赖
pip install watchdog
```

## 配置

QSM系统的配置文件位于：

- `Ref/data/auto_monitor_config.json` - 自动监控系统配置
- `Ref/data/file_registry.json` - 文件注册表

## 项目结构

```
QSM/
├── QSM/            # 主系统代码
│   └── main.py     # 项目入口
├── Ref/            # 文件完整性监控系统
│   ├── auto_monitor/   # 自动监控系统
│   ├── utils/          # 工具模块
│   └── README.md       # Ref系统说明
├── SOM/            # SOM子系统
├── WeQ/            # WeQ子系统
├── start.bat       # Windows启动脚本
├── start.sh        # Linux/Mac启动脚本
└── README.md       # 项目说明
```

## 贡献

欢迎提交问题报告和功能请求。如果您想贡献代码，请先fork项目并创建拉取请求。

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。

# 量子叠加态模型 (QSM)

> 量子基因编码: QG-QSM01-DOC-20250402-A7F5E3-ENT7235

量子叠加态模型是一个基于量子理论的创新型自进化系统，集成了神经网络、量子计算和区块链技术的优势，打造下一代分布式智能生态系统。

## 文档指南

详细文档请参阅 [docs/QSM](docs/QSM) 目录：

- [QSM简介](docs/QSM/QSM_Intro.md) - 项目简介和快速上手
- [QSM概述](docs/QSM/QSM_overview.md) - 项目的全面概述和定义
- [开发文档](docs/QSM/QSM_Development.md) - 详细的开发指南
- [系统导航](docs/QSM/QSM_Navigation.md) - 项目地图和导航
- [用户指南](docs/QSM/QSM_User_Guide.md) - 用户使用指南
- [项目管理工具](docs/QSM/tools/project_tools_guide.md) - 项目管理工具使用说明

## 快速开始

```bash
# 克隆仓库
git clone https://gitee.com/nuosuco/qsm.git
cd QSM

# 安装依赖
pip install -r requirements.txt

# 启动自反省核心
python Ref/ref_core.py

# 启动API服务
# 启动主量子API服务（集成所有子系统API）
python api/qsm_api/qsm_api.py

# 或使用统一启动脚本启动所有API服务
python api/qsm_api/run_api.py --all
```

---

> "在量子世界中，万物皆相连，时空皆可超越。" - QSM开发理念 

# QSM项目

## 简介

QSM项目是一个集成了量子模拟、量子基因标记和Ref智能系统的综合框架。

## 项目自动化

本项目提供了多种自动化工具，用于简化开发工作流程和提高效率。

### 环境设置

首次使用项目前，需要设置Python虚拟环境：

```bash
# 创建虚拟环境
python -m venv .venv

# Windows激活环境
.venv\Scripts\activate

# Linux/Mac激活环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 自动启动所有服务

我们提供了自动激活环境并启动所有服务的脚本：

- **Windows**: 在PowerShell中运行 `.\activate_env.ps1`
- **Linux/Mac**: 在终端中运行 `source ./activate_env.sh`

这将自动：
1. 激活Python虚拟环境
2. 启动Ref核心系统
3. 启动量子基因标记监视器
4. 启动WeQ后台训练系统（如果存在）

### VSCode集成

如果使用VSCode，我们已配置了自动化任务：

1. 打开命令面板（Ctrl+Shift+P）
2. 输入 "Tasks: Run Task"
3. 选择 "激活环境并启动所有服务"

您还可以设置VSCode在打开项目文件夹时自动启动所有服务。

### 量子基因标记

量子基因标记功能现在不依赖于Ref系统也可以独立使用：

```bash
# 标记单个文件
python QEntL/cli.py mark --file path/to/file.py

# 标记整个目录
python QEntL/cli.py mark --directory ./project --recursive
```

## 项目组件

### QEntL (量子纠缠语言)

管理量子基因标记和量子纠缠的框架。

### Ref系统

智能引用系统，提供自动化和优化功能。

### WeQ系统

后台训练和学习系统。

## 注意事项

- 虚拟环境的激活是所有功能正常工作的前提
- 当所有任务完成后，可以通过运行`deactivate`命令退出虚拟环境 
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
