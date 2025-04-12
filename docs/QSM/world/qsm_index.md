# QSM(量子叠加态模型)主模型目录索引

## 概述
QSM(量子叠加态模型)是整个项目的主模型，负责协调各子系统的运行，管理量子状态，并提供统一的用户界面。QSM通过量子纠缠信道与SOM、WeQ和Ref子系统进行交互，实现分布式量子计算功能。本文档提供QSM主模型的完整结构索引。

## 目录结构

### 顶级目录
- **app.py**  __QSM应用入口点
- **global/**  __QSM特定全局资源
- **quantum_blockchain/**  __QSM特定区块链实现
- **templates/**  __模板文件

### 全局目录 (global/)
- **js/**  __QSM特定JavaScript文件

### 模板目录 (templates/)
- **api_client.html**  __API客户端界面
- **base_qsm.html**  __QSM特定基础模板
- **css/**  __CSS样式文件
- **images/**  __图片资源
- **index.html**  __主页
- **js/**  __JavaScript文件
  - **quantum_loader.js**  __量子加载器
- **quantum_experience.html**  __量子体验页面
- **quantum_test.html**  __量子测试页面
- **shared/**  __共享模板组件
  - **css/**  __共享CSS样式
  - **head_includes.html**  __头部包含文件
  - **images/**  __共享图片
  - **js/**  __共享JavaScript文件

## 量子核心 (quantum_core/)
- **logs/**  __日志文件
- **quantum_blockchain/**  __核心量子区块链
  - **__init__.py**  __区块链初始化
  - **qsm_main_chain.py**  __QSM主链
  - **quantum_blockchain_core.py**  __量子区块链核心
  - **qsm_knowledge.py**  __QSM知识库

## 文档 (docs/QSM/)
- **global/**  __QSM文档全局资源
- **images/**  __文档图片
- **navigation/**  __导航文档
- **tools/**  __工具文档
- **user_guides/**  __用户指南
  - **quantum_network_connection_guide.md**  __量子网络连接指南

## 关键功能

### 量子区块链
- **quantum_blockchain/**  __QSM特定区块链
- **quantum_core/quantum_blockchain/**  __核心量子区块链

### 用户界面
- **templates/index.html**  __主页
- **templates/quantum_experience.html**  __量子体验页面
- **templates/api_client.html**  __API客户端界面

### 量子纠缠信道
- **global/js/quantum_entanglement_client.js**  __量子纠缠客户端（全局）

## 与子模块的交互
- 通过量子纠缠信道与SOM子系统进行经济数据交互
- 与WeQ子系统进行多模态交互和知识库访问
- 使用Ref子系统进行量子纠错和数据修复

## 子模型索引
- [SOM(量子经济系统)子模型索引](../../SOM/global/som_index.md)
- [WeQ(小趣)子模型索引](../../WeQ/global/weq_index.md)
- [Ref(量子纠错子系统)索引](../../Ref/global/ref_index.md)

## 最近更新
- 完善了QSM导航栏与底部模板
- 统一了量子纠缠信道接口
- 创建了QSM目录索引结构
- 优化了量子区块链性能 

## 概述
QSM(量子叠加态模型)是整个项目的主模型，负责协调各子系统的运行，管理量子状态，并提供统一的用户界面。QSM通过量子纠缠信道与SOM、WeQ和Ref子系统进行交互，实现分布式量子计算功能。本文档提供QSM主模型的完整结构索引。

## 目录结构

### 顶级目录
- **app.py**  __QSM应用入口点
- **global/**  __QSM特定全局资源
- **quantum_blockchain/**  __QSM特定区块链实现
- **templates/**  __模板文件

### 全局目录 (global/)
- **js/**  __QSM特定JavaScript文件

### 模板目录 (templates/)
- **api_client.html**  __API客户端界面
- **base_qsm.html**  __QSM特定基础模板
- **css/**  __CSS样式文件
- **images/**  __图片资源
- **index.html**  __主页
- **js/**  __JavaScript文件
  - **quantum_loader.js**  __量子加载器
- **quantum_experience.html**  __量子体验页面
- **quantum_test.html**  __量子测试页面
- **shared/**  __共享模板组件
  - **css/**  __共享CSS样式
  - **head_includes.html**  __头部包含文件
  - **images/**  __共享图片
  - **js/**  __共享JavaScript文件

## 量子核心 (quantum_core/)
- **logs/**  __日志文件
- **quantum_blockchain/**  __核心量子区块链
  - **__init__.py**  __区块链初始化
  - **qsm_main_chain.py**  __QSM主链
  - **quantum_blockchain_core.py**  __量子区块链核心
  - **qsm_knowledge.py**  __QSM知识库

## 文档 (docs/QSM/)
- **global/**  __QSM文档全局资源
- **images/**  __文档图片
- **navigation/**  __导航文档
- **tools/**  __工具文档
- **user_guides/**  __用户指南
  - **quantum_network_connection_guide.md**  __量子网络连接指南

## 关键功能

### 量子区块链
- **quantum_blockchain/**  __QSM特定区块链
- **quantum_core/quantum_blockchain/**  __核心量子区块链

### 用户界面
- **templates/index.html**  __主页
- **templates/quantum_experience.html**  __量子体验页面
- **templates/api_client.html**  __API客户端界面

### 量子纠缠信道
- **global/js/quantum_entanglement_client.js**  __量子纠缠客户端（全局）

## 与子模块的交互
- 通过量子纠缠信道与SOM子系统进行经济数据交互
- 与WeQ子系统进行多模态交互和知识库访问
- 使用Ref子系统进行量子纠错和数据修复

## 子模型索引
- [SOM(量子经济系统)子模型索引](../../SOM/global/som_index.md)
- [WeQ(小趣)子模型索引](../../WeQ/global/weq_index.md)
- [Ref(量子纠错子系统)索引](../../Ref/global/ref_index.md)

## 最近更新
- 完善了QSM导航栏与底部模板
- 统一了量子纠缠信道接口
- 创建了QSM目录索引结构
- 优化了量子区块链性能 

```
```
量子基因编码: QE-QSM-9D65955790AB
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
