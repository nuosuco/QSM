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