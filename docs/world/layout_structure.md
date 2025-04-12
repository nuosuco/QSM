# QSM项目布局结构文档

## 1. 概述

QSM项目采用模块化的架构设计，由一个全局共享模块（world）和四个子模型（QSM、SOM、WeQ、Ref）组成。每个模块都有自己特定的功能和界面特性，同时也共享一些全局组件和服务。

本文档详细描述了项目的布局结构，包括全局布局和各子模型特有的布局及特性。

## 2. 全局布局（world）

全局模块（world）提供了在所有子模型中共享的基础组件、服务和布局结构。

### 2.1 目录结构

```
world/
  ├── config/            # 全局配置文件
  │   └── paths_config.py  # 路径配置
  ├── static/            # 静态资源
  │   ├── css/           # 全局CSS样式
  │   │   └── global.css # 全局样式
  │   ├── js/            # 全局JavaScript
  │   │   ├── global.js  # 全局脚本
  │   │   ├── quantum_entanglement.js      # 量子纠缠通信
  │   │   ├── quantum_entanglement_client.js # 客户端
  │   │   └── quantum_loader.js            # 资源加载器
  │   └── images/        # 全局图片
  ├── templates/         # 全局模板
  │   └── base.html      # 基础模板
  └── tools/             # 全局工具
      └── path_resolver.py # 路径解析器
```

### 2.2 基础模板结构

全局基础模板（`world/templates/base.html`）提供了所有页面共享的布局结构，包括：

- 头部区域：包含全局导航栏
- 主内容区域：由各子模型填充
- 页脚区域：包含通用链接和版权信息

基础模板定义了以下区块，可由子模型覆盖：

- `title`：页面标题
- `model_css`：模型特定的CSS
- `model_nav`：模型特定的导航
- `content`：主内容区域
- `model_js`：模型特定的JavaScript
- `head_extra`：额外的头部内容
- `scripts_extra`：额外的脚本

### 2.3 全局组件

#### 2.3.1 量子纠缠信道

全局模块提供了量子纠缠信道机制，允许不同子模型之间进行实时通信。主要文件：

- `world/static/js/quantum_entanglement.js`：核心实现
- `world/static/js/quantum_entanglement_client.js`：客户端封装

该组件支持以下功能：
- 自动建立量子纠缠连接
- 在模型间发送和接收数据
- 支持心跳检测和连接状态监控
- 支持集成模式和独立模式

## 3. 子模型特有布局与特性

### 3.1 QSM（量子叠加态模型）

QSM是项目的主模型，提供了量子计算的核心功能。

#### 3.1.1 目录结构

```
QSM/
  ├── static/            # 静态资源
  │   ├── css/           # CSS样式
  │   │   └── qsm.css    # QSM特定样式
  │   ├── js/            # JavaScript
  │   │   └── qsm_core.js # QSM核心脚本
  │   └── images/        # 图片资源
  ├── templates/         # 模板
  │   ├── base_qsm.html  # QSM基础模板
  │   ├── index.html     # 首页
  │   ├── quantum_test.html # 量子测试页
  │   ├── quantum_experience.html # 量子体验页
  │   └── api_client.html # API客户端页
  └── world/             # QSM特有的全局文件
```

#### 3.1.2 特有组件与特性

- **QSM导航栏**：提供QSM特定的导航选项，包括QSM首页、量子测试、量子体验和API客户端
- **量子计算核心**：提供基于量子算法的计算能力
- **QSM模型展示**：可视化展示量子叠加态模型的工作原理

### 3.2 WeQ（量子纠缠模型）

WeQ子模型专注于多模态交互和信息纠缠功能。

#### 3.2.1 目录结构

```
WeQ/
  ├── static/            # 静态资源
  │   ├── css/           # CSS样式
  │   │   └── weq.css    # WeQ特定样式
  │   ├── js/            # JavaScript
  │   │   └── weq_core.js # WeQ核心脚本
  │   └── images/        # 图片资源
  ├── templates/         # 模板
  │   ├── base_weq.html  # WeQ基础模板
  │   ├── index.html     # 首页
  │   └── weq_multimodal_demo.html # 多模态演示页
  └── world/             # WeQ特有的全局文件
      └── js/
          └── weq_multimodal_interactions.js # 多模态交互
```

#### 3.2.2 特有组件与特性

- **九大多模态交互方式**：
  1. 点击交互 (click)
  2. 视线追踪交互 (gaze)
  3. 语音交互 (voice)
  4. 手势交互 (gesture)
  5. 脑电波交互 (brainwave) - 模拟
  6. 触觉交互 (touch)
  7. 动作捕捉交互 (motion)
  8. 生物反馈交互 (biofeedback)
  9. 情感识别交互 (emotion)

- **WeQ特有导航**：包括WeQ首页、量子交互、量子媒体、多模态演示和知识库
- **多模态演示界面**：展示和测试多种交互方式
- **量子纠缠客户端**：提供专用的纠缠通信客户端

### 3.3 SOM（量子经济模型）

SOM子模型专注于量子经济和交易功能。

#### 3.3.1 目录结构

```
SOM/
  ├── static/            # 静态资源
  │   ├── css/           # CSS样式
  │   │   └── som.css    # SOM特定样式
  │   ├── js/            # JavaScript
  │   │   └── som_core.js # SOM核心脚本
  │   └── images/        # 图片资源
  ├── templates/         # 模板
  │   ├── base_som.html  # SOM基础模板
  │   ├── index.html     # 首页
  │   └── MQB/           # 量子经济组件模板
  └── world/             # SOM特有的全局文件
```

#### 3.3.2 特有组件与特性

- **SOM特有导航**：包括SOM首页、量子电商、量子钱包、支付网关和量子合约
- **量子经济界面**：具有量子安全特性的经济交互界面
- **量子钱包组件**：管理量子资产的界面组件
- **量子合约界面**：创建和管理量子合约的界面

### 3.4 Ref（量子参考系统）

Ref子模型负责量子纠错、监控和参考功能。

#### 3.4.1 目录结构

```
Ref/
  ├── static/            # 静态资源
  │   ├── css/           # CSS样式
  │   │   └── ref.css    # Ref特定样式
  │   ├── js/            # JavaScript
  │   │   └── ref_core.js # Ref核心脚本
  │   └── images/        # 图片资源
  ├── templates/         # 模板
  │   ├── base_ref.html  # Ref基础模板
  │   ├── index.html     # 首页
  │   └── dashboard.html # 监控仪表板
  └── world/             # Ref特有的全局文件
```

#### 3.4.2 特有组件与特性

- **Ref特有导航**：包括Ref首页、量子纠缠通讯、基因系统、监控系统和修复系统
- **量子纠缠通讯界面**：测试和管理量子纠缠通信的界面
- **基因系统界面**：管理量子基因编码的界面
- **监控仪表板**：监控整个量子系统状态的可视化界面
- **修复系统界面**：检测和修复量子错误的界面

## 4. 集成与独立模式

QSM项目支持两种运行模式：

### 4.1 集成模式

在集成模式下，所有子模型通过主QSM服务器集成在一起，共享同一个全局配置。URL路径以子模型名称为前缀（如`/QSM/`, `/WeQ/`等）。

### 4.2 独立模式

在独立模式下，每个子模型可以作为独立服务运行，使用各自的全局配置。URL路径不包含子模型前缀。

## 5. 布局系统的未来演进

随着项目的发展，布局系统将朝着以下方向演进：

1. **完全模块化**：每个子模型将能完全独立运行，使用自己的全局文件
2. **动态布局适配**：根据用户设备和偏好自动调整布局
3. **主题系统**：支持多种视觉主题和风格
4. **插件架构**：允许通过插件扩展布局功能

## 6. 总结

QSM项目的布局结构采用了模块化和层次化的设计，既保证了各子模型的独立性和特色，又提供了全局共享的组件和服务。通过全局模块（world）和各子模型特有模块的组合，实现了灵活而强大的界面系统。 

```
```
量子基因编码: QE-LAY-7CD1AEF20352
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
