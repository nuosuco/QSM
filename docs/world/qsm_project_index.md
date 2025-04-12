# 量子叠加态模型(QSM)项目目录索引

## 项目概述
量子叠加态模型(QSM)是一个基于量子计算原理的分布式系统，由多个核心子模型组成，包括主模型QSM、SOM(量子经济系统)、WeQ(小趣)和Ref(量子纠错子系统)。本文档提供了项目的完整结构索引，帮助开发者快速了解和导航项目。

## 目录结构

### 顶级目录
- **api/**  __API接口定义和实现
- **docs/**  __项目文档
- **frontend/**  __前端共享组件和工具
- **global/**  __全局配置、模板和工具
- **models/**  __模型定义和检查点
- **quantum_core/**  __量子核心功能实现
- **quantum_data/**  __量子数据存储
- **quantum_economy/**  __量子经济系统
- **quantum_shared/**  __共享的量子工具和存储
- **QSM/**  __主模型实现
- **Ref/**  __量子纠错子系统
- **SOM/**  __量子经济子系统
- **src/**  __源代码通用组件
- **static/**  __静态资源
- **WeQ/**  __小趣子系统

### 文档目录 (docs/)
- **api/**  __API文档
- **global/**  __全局文档和索引
- **QSM/**  __主模型文档
- **quantum_core/**  __量子核心功能文档
- **quantum_shared/**  __共享功能文档
- **Ref/**  __量子纠错子系统文档
- **SOM/**  __量子经济子系统文档
- **WeQ/**  __小趣子系统文档

### 全局目录 (global/)
- **config/**  __全局配置文件
- **js/**  __全局JavaScript文件
- **static/**  __全局静态资源
  - **css/**  __全局CSS样式
  - **images/**  __全局图片资源
  - **js/**  __全局JavaScript库
    - **multimodal/**  __多模态交互JavaScript
- **templates/**  __全局模板
- **tools/**  __全局工具

### 量子核心 (quantum_core/)
- **logs/**  __日志文件
- **quantum_blockchain/**  __量子区块链实现
- **quantum_gene/**  __量子基因实现
  - **claude_weq_bridge/**  __Claude到WeQ的桥接
  - **network_expansion/**  __网络扩展
  - **physical_medium/**  __物理媒介
  - **quantum_attention/**  __量子注意力机制
  - **quantum_memory/**  __量子记忆
  - **quantum_reasoning/**  __量子推理
  - **quantum_semantic/**  __量子语义

### 主模型 (QSM/)
- **global/**  __QSM特定全局资源
- **quantum_blockchain/**  __QSM特定区块链实现
- **templates/**  __QSM模板
  - **css/**  __CSS样式
  - **images/**  __图片资源
  - **js/**  __JavaScript文件
  - **shared/**  __共享模板组件

### 量子纠错子系统 (Ref/)
- **api/**  __Ref API
- **backup/**  __备份功能
- **data/**  __数据
- **gene/**  __基因实现
  - **test_output_entanglement/**  __输出纠缠测试
- **global/**  __Ref特定全局资源
- **monitor/**  __监控功能
- **quantum_blockchain/**  __Ref特定区块链
- **repair/**  __修复功能
- **static/**  __静态资源
- **templates/**  __模板文件

### 量子经济子系统 (SOM/)
- **global/**  __SOM特定全局资源
- **quantum_blockchain/**  __SOM特定区块链
- **static/**  __静态资源
- **templates/**  __模板文件
  - **MQB/**  __MQB模板
  - **shared/**  __共享模板组件

### 小趣子系统 (WeQ/)
- **api/**  __WeQ API
- **global/**  __WeQ特定全局资源
- **knowledge/**  __知识库
  - **crawler_data/**  __爬虫数据
  - **logs/**  __日志
  - **models/**  __模型
  - **training_data/**  __训练数据
- **neural/**  __神经网络实现
- **quantum_blockchain/**  __WeQ特定区块链
- **static/**  __静态资源
- **templates/**  __模板文件

## 关键功能目录

### 多模态交互
- **global/static/js/multimodal/**  __全局多模态交互实现
- **WeQ/global/js/weq_multimodal_interactions.js**  __WeQ多模态交互实现
- **WeQ/templates/weq_multimodal_demo.html**  __WeQ多模态演示页面

### 量子区块链
- **quantum_core/quantum_blockchain/**  __核心量子区块链
- **QSM/quantum_blockchain/**  __QSM特定区块链
- **SOM/quantum_blockchain/**  __SOM特定区块链
- **WeQ/quantum_blockchain/**  __WeQ特定区块链
- **Ref/quantum_blockchain/**  __Ref特定区块链

### 量子纠缠信道
- **global/js/quantum_entanglement_client.js**  __全局量子纠缠客户端
- **global/static/js/quantum_entanglement.js**  __量子纠缠实现

## 自动化工具
- **frontend/tools/auto_template_watcher.py**  __模板自动监视
- **frontend/tools/create_page.py**  __页面自动创建
- **frontend/tools/install_auto_template.py**  __自动模板安装
- **frontend/tools/start_template_watcher.py**  __启动模板监视

## 最近更新
- 添加了WeQ多模态演示页面
- 统一了全局量子纠缠信道模块
- 完善了所有子模型的导航栏与底部模板
- 创建了项目索引和文档结构 

## 项目概述
量子叠加态模型(QSM)是一个基于量子计算原理的分布式系统，由多个核心子模型组成，包括主模型QSM、SOM(量子经济系统)、WeQ(小趣)和Ref(量子纠错子系统)。本文档提供了项目的完整结构索引，帮助开发者快速了解和导航项目。

## 目录结构

### 顶级目录
- **api/**  __API接口定义和实现
- **docs/**  __项目文档
- **frontend/**  __前端共享组件和工具
- **global/**  __全局配置、模板和工具
- **models/**  __模型定义和检查点
- **quantum_core/**  __量子核心功能实现
- **quantum_data/**  __量子数据存储
- **quantum_economy/**  __量子经济系统
- **quantum_shared/**  __共享的量子工具和存储
- **QSM/**  __主模型实现
- **Ref/**  __量子纠错子系统
- **SOM/**  __量子经济子系统
- **src/**  __源代码通用组件
- **static/**  __静态资源
- **WeQ/**  __小趣子系统

### 文档目录 (docs/)
- **api/**  __API文档
- **global/**  __全局文档和索引
- **QSM/**  __主模型文档
- **quantum_core/**  __量子核心功能文档
- **quantum_shared/**  __共享功能文档
- **Ref/**  __量子纠错子系统文档
- **SOM/**  __量子经济子系统文档
- **WeQ/**  __小趣子系统文档

### 全局目录 (global/)
- **config/**  __全局配置文件
- **js/**  __全局JavaScript文件
- **static/**  __全局静态资源
  - **css/**  __全局CSS样式
  - **images/**  __全局图片资源
  - **js/**  __全局JavaScript库
    - **multimodal/**  __多模态交互JavaScript
- **templates/**  __全局模板
- **tools/**  __全局工具

### 量子核心 (quantum_core/)
- **logs/**  __日志文件
- **quantum_blockchain/**  __量子区块链实现
- **quantum_gene/**  __量子基因实现
  - **claude_weq_bridge/**  __Claude到WeQ的桥接
  - **network_expansion/**  __网络扩展
  - **physical_medium/**  __物理媒介
  - **quantum_attention/**  __量子注意力机制
  - **quantum_memory/**  __量子记忆
  - **quantum_reasoning/**  __量子推理
  - **quantum_semantic/**  __量子语义

### 主模型 (QSM/)
- **global/**  __QSM特定全局资源
- **quantum_blockchain/**  __QSM特定区块链实现
- **templates/**  __QSM模板
  - **css/**  __CSS样式
  - **images/**  __图片资源
  - **js/**  __JavaScript文件
  - **shared/**  __共享模板组件

### 量子纠错子系统 (Ref/)
- **api/**  __Ref API
- **backup/**  __备份功能
- **data/**  __数据
- **gene/**  __基因实现
  - **test_output_entanglement/**  __输出纠缠测试
- **global/**  __Ref特定全局资源
- **monitor/**  __监控功能
- **quantum_blockchain/**  __Ref特定区块链
- **repair/**  __修复功能
- **static/**  __静态资源
- **templates/**  __模板文件

### 量子经济子系统 (SOM/)
- **global/**  __SOM特定全局资源
- **quantum_blockchain/**  __SOM特定区块链
- **static/**  __静态资源
- **templates/**  __模板文件
  - **MQB/**  __MQB模板
  - **shared/**  __共享模板组件

### 小趣子系统 (WeQ/)
- **api/**  __WeQ API
- **global/**  __WeQ特定全局资源
- **knowledge/**  __知识库
  - **crawler_data/**  __爬虫数据
  - **logs/**  __日志
  - **models/**  __模型
  - **training_data/**  __训练数据
- **neural/**  __神经网络实现
- **quantum_blockchain/**  __WeQ特定区块链
- **static/**  __静态资源
- **templates/**  __模板文件

## 关键功能目录

### 多模态交互
- **global/static/js/multimodal/**  __全局多模态交互实现
- **WeQ/global/js/weq_multimodal_interactions.js**  __WeQ多模态交互实现
- **WeQ/templates/weq_multimodal_demo.html**  __WeQ多模态演示页面

### 量子区块链
- **quantum_core/quantum_blockchain/**  __核心量子区块链
- **QSM/quantum_blockchain/**  __QSM特定区块链
- **SOM/quantum_blockchain/**  __SOM特定区块链
- **WeQ/quantum_blockchain/**  __WeQ特定区块链
- **Ref/quantum_blockchain/**  __Ref特定区块链

### 量子纠缠信道
- **global/js/quantum_entanglement_client.js**  __全局量子纠缠客户端
- **global/static/js/quantum_entanglement.js**  __量子纠缠实现

## 自动化工具
- **frontend/tools/auto_template_watcher.py**  __模板自动监视
- **frontend/tools/create_page.py**  __页面自动创建
- **frontend/tools/install_auto_template.py**  __自动模板安装
- **frontend/tools/start_template_watcher.py**  __启动模板监视

## 最近更新
- 添加了WeQ多模态演示页面
- 统一了全局量子纠缠信道模块
- 完善了所有子模型的导航栏与底部模板
- 创建了项目索引和文档结构 

```
```
量子基因编码: QE-QSM-C48EE05D2C67
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
