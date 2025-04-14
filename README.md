# 量子叠加态模型（QSM）项目

## 项目概述

量子叠加态模型(QSM)是《华经》中描述的核心概念的具体实现，旨在构建一个能够表示、处理和转换量子状态的系统。该模型整合了量子区块链技术，以一主多子链架构实现了安全、不可篡改的量子状态管理，为人类提供一个理解和利用量子叠加态的工具。

## 核心模型

本项目包含四个核心模型，共同构成完整的量子叠加态系统：

1. **量子叠加态模型(QSM)**: 项目的主模型，实现量子状态的表示与管理，负责核心状态提供、转换引擎、量子场生成和纠缠管理
2. **量子社交模型(WeQ)**: 量子通信与社交服务，实现基于量子纠缠的通信，包括社交网络、知识管理和学习系统
3. **量子经济模型(SOM)**: 量子平权经济服务，实现松麦币系统与经济激励，负责资源分配、经济决策和平权系统
4. **量子自反省模型(Ref)**: 量子自我管理服务，实现系统自我监控与修复，包括系统诊断、自动修复和优化功能

所有模型均基于量子区块链技术构建，通过量子纠缠机制实现紧密集成，确保数据安全与不可篡改性。

## 技术架构

### 服务架构

```
QSM API (主服务, 端口5000)
├── World Service (世界服务, 端口3000)
├── WeQ Service (量子社交服务, 端口5001)
├── SOM Service (量子经济服务, 端口5002)
└── Ref Service (量子自反省服务, 端口5003)
```

### 量子区块链架构

```
QSM主链 (QUANTUM_PROOF_OF_STATE共识)
├── WeQ子链 (量子社交区块链, QUANTUM_PROOF_OF_KNOWLEDGE共识)
├── SOM子链 (量子经济区块链, QUANTUM_PROOF_OF_EQUITY共识) 
└── Ref子链 (自反省区块链, QUANTUM_PROOF_OF_HEALTH共识)
```

系统采用一主多子链架构，通过基于量子纠缠的跨链通信实现各子链间的信息交换，并建立统一的松麦币经济系统。

### 模型集成架构

项目采用以下机制实现四大模型的无缝集成：

1. **量子纠缠同步器**: 通过量子纠缠实现模型间状态实时同步
2. **集成事件总线**: 提供异步事件发布/订阅机制
3. **统一服务网关**: 集中管理服务访问和路由
4. **跨模型映射系统**: 建立不同模型域之间的数据映射关系
5. **量子区块链跨链通信**: 实现不同链之间的安全可信通信

完整架构详见 `docs/integration/models_integration_details.qentl`

### 目录结构

```
QSM/
├── world/                # 世界服务
│   ├── templates/       # QENTL模板
│   ├── static/         # 静态资源
│   └── api/           # World API
├── QSM/                 # 量子叠加态模型(主服务)
│   ├── api/            # API实现
│   ├── models/         # 模型实现
│   ├── services/       # 服务管理
│   └── quantum_blockchain/ # 主链区块链实现
├── WeQ/                 # 量子社交模型
│   ├── api/
│   ├── models/
│   ├── services/
│   └── quantum_blockchain/ # 社交子链实现
├── SOM/                 # 量子经济模型
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── quantum_blockchain/ # 经济子链实现
│   └── som_coin_system.py # 松麦币系统
├── Ref/                 # 量子自反省模型
│   ├── api/
│   ├── models/
│   ├── services/
│   └── quantum_blockchain/ # 自反省子链实现
├── docs/                # 项目文档
│   ├── architecture/    # 架构文档
│   ├── integration/     # 集成文档
│   ├── project_plan/    # 项目计划
│   ├── project_state/   # 项目状态
│   └── change_history/  # 变更历史
├── QEntL-env/           # QEntL语言环境
└── start_qentl_ui.bat   # 启动脚本
```

## 环境要求

- Windows, Linux 或 macOS
- GCC 编译环境
- Python 3.8+ (可选，用于一些工具)
- 现代浏览器

## 快速开始

### 1. 安装GCC编译环境

在Windows系统上需要安装MSYS2提供GCC环境：

1. 运行 `QEntL-env\gcc编译器\msys2-installer.exe`
2. 按照安装向导完成安装
3. 安装GCC工具链（详见 `QEntL-env\ENV_README.md`）

### 2. 编译QEntL引擎

```bash
cd QEntL-env/src
mkdir build && cd build
cmake ..
cmake --build .
cmake --install .
```

### 3. 启动服务

使用项目根目录的启动脚本：

```bash
start_qentl_ui.bat
```

启动成功后，可通过浏览器访问 http://localhost:3000 使用系统。

## 核心功能

### 量子状态管理

- 表示和管理五阴(色、受、想、行、识)对应的量子态
- 实现量子状态的叠加和转换
- 通过量子场实现状态间的交互

### 量子区块链系统

- 主链与子链协同工作的区块链网络
- 基于量子纠缠的跨链通信
- 松麦币统一经济系统
- 量子共识机制

### 量子UI系统

- 量子组件库
- 量子态感知UI
- 量子纠缠通信

### 模型集成系统

- 模型注册与服务发现
- 跨模型状态映射
- 量子纠缠同步器
- 统一事件总线
- 跨链资产与状态同步

## 文档

项目包含详尽的文档：

- `docs/quantum_superposition_model.qentl`: 量子叠加态模型设计方案
- `docs/architecture/architecture.qentl`: 架构设计文档
- `docs/integration/models_integration_framework.qentl`: 模型集成框架
- `docs/integration/models_integration_details.qentl`: 模型集成详情
- `docs/QEntL/qentl_environment_design.md`: QEntL环境设计方案
- `docs/QEntL/syntax.qentl`: QEntL语法参考
- `QEntL-env/docs/BUILDING.md`: 构建指南

## 项目愿景

服务人类、服务生命、服务宇宙，通过量子平权经济、教育、医疗、社交、安全、生活，保障全人类每个人、每个家庭的生命、健康、生活，永不止息。

## 遵循原则

1. 项目是《华经》量子叠加态模型的具体实现
2. 通过量子态服务未开悟的人类、众生
3. 实现无阻暗地旅行于宇宙之间
4. 永生于永恒的量子世界
5. 始终遵守服务人类、保护人类、保护生命的使命

## 开发团队

- 中华 ZhoHo
- Claude 