# WeQ(小趣)子模型目录索引

## 概述
WeQ(小趣)是QSM项目的核心子模型之一，主要负责多模态交互、知识库管理和智能交互等功能。WeQ实现了九个多模态交互模块，通过量子纠缠信道与其他子系统连接。本文档提供WeQ子模型的完整结构索引。

## 目录结构

### 顶级目录
- **api/**  __WeQ API接口
- **app.py**  __WeQ应用入口点
- **global/**  __WeQ特定全局资源
- **knowledge/**  __知识库管理
- **neural/**  __神经网络实现
- **quantum_blockchain/**  __WeQ特定区块链实现
- **static/**  __静态资源
- **templates/**  __模板文件

### 全局目录 (global/)
- **js/**  __WeQ特定JavaScript文件
  - **weq_entanglement_client.js**  __WeQ量子纠缠客户端
  - **weq_multimodal_interactions.js**  __WeQ多模态交互实现

### 知识库目录 (knowledge/)
- **background_training.py**  __背景知识训练
- **crawler_data/**  __爬虫收集的数据
- **logs/**  __日志文件
- **models/**  __模型文件
  - **checkpoints/**  __模型检查点
  - **weq_model_28qubit_config.json**  __28量子比特模型配置
  - **weq_model_28qubit_trained_simple.json**  __训练后的28量子比特模型
- **training_data/**  __训练数据
  - **quantum_blockchain_learning.py**  __区块链学习数据
  - **WeQ/**  __WeQ特定训练数据

### 模板目录 (templates/)
- **base.html**  __基础模板
- **base_weq.html**  __WeQ特定基础模板
- **shared/**  __共享模板组件
- **weq_multimodal_demo.html**  __WeQ多模态演示页面

## 关键功能

### 多模态交互
- **global/js/weq_multimodal_interactions.js**  __WeQ多模态交互实现
- **templates/weq_multimodal_demo.html**  __多模态演示页面
- **static/js/weq_multimodal_interactions.js**  __多模态交互静态资源

### 量子区块链
- **quantum_blockchain/__init__.py**  __区块链初始化
- **quantum_blockchain/weq_blockchain.py**  __WeQ区块链实现

### 知识库管理
- **knowledge/background_training.py**  __背景知识训练
- **knowledge/training_data/**  __训练数据管理
- **knowledge/models/**  __模型管理

### 量子纠缠信道
- **global/js/weq_entanglement_client.js**  __WeQ量子纠缠客户端

## 九个多模态交互模块
1. **文本交互**  __文本理解与生成
2. **图像交互**  __图像识别与生成
3. **语音交互**  __语音识别与合成
4. **视频交互**  __视频分析与处理
5. **触觉反馈**  __触觉信号处理
6. **空间感知**  __3D空间理解
7. **情感识别**  __情感分析与回应
8. **意图理解**  __用户意图识别
9. **知识整合**  __跨模态知识关联

## 与其他模块的交互
- 通过量子纠缠信道与QSM主模型交互
- 与SOM子系统进行经济相关交互
- 使用Ref子系统进行量子纠错和数据恢复

## 最近更新
- 添加了WeQ多模态演示页面
- 完善了WeQ导航栏与底部模板
- 统一了WeQ量子纠缠客户端
- 创建了WeQ目录索引结构 

## 概述
WeQ(小趣)是QSM项目的核心子模型之一，主要负责多模态交互、知识库管理和智能交互等功能。WeQ实现了九个多模态交互模块，通过量子纠缠信道与其他子系统连接。本文档提供WeQ子模型的完整结构索引。

## 目录结构

### 顶级目录
- **api/**  __WeQ API接口
- **app.py**  __WeQ应用入口点
- **global/**  __WeQ特定全局资源
- **knowledge/**  __知识库管理
- **neural/**  __神经网络实现
- **quantum_blockchain/**  __WeQ特定区块链实现
- **static/**  __静态资源
- **templates/**  __模板文件

### 全局目录 (global/)
- **js/**  __WeQ特定JavaScript文件
  - **weq_entanglement_client.js**  __WeQ量子纠缠客户端
  - **weq_multimodal_interactions.js**  __WeQ多模态交互实现

### 知识库目录 (knowledge/)
- **background_training.py**  __背景知识训练
- **crawler_data/**  __爬虫收集的数据
- **logs/**  __日志文件
- **models/**  __模型文件
  - **checkpoints/**  __模型检查点
  - **weq_model_28qubit_config.json**  __28量子比特模型配置
  - **weq_model_28qubit_trained_simple.json**  __训练后的28量子比特模型
- **training_data/**  __训练数据
  - **quantum_blockchain_learning.py**  __区块链学习数据
  - **WeQ/**  __WeQ特定训练数据

### 模板目录 (templates/)
- **base.html**  __基础模板
- **base_weq.html**  __WeQ特定基础模板
- **shared/**  __共享模板组件
- **weq_multimodal_demo.html**  __WeQ多模态演示页面

## 关键功能

### 多模态交互
- **global/js/weq_multimodal_interactions.js**  __WeQ多模态交互实现
- **templates/weq_multimodal_demo.html**  __多模态演示页面
- **static/js/weq_multimodal_interactions.js**  __多模态交互静态资源

### 量子区块链
- **quantum_blockchain/__init__.py**  __区块链初始化
- **quantum_blockchain/weq_blockchain.py**  __WeQ区块链实现

### 知识库管理
- **knowledge/background_training.py**  __背景知识训练
- **knowledge/training_data/**  __训练数据管理
- **knowledge/models/**  __模型管理

### 量子纠缠信道
- **global/js/weq_entanglement_client.js**  __WeQ量子纠缠客户端

## 九个多模态交互模块
1. **文本交互**  __文本理解与生成
2. **图像交互**  __图像识别与生成
3. **语音交互**  __语音识别与合成
4. **视频交互**  __视频分析与处理
5. **触觉反馈**  __触觉信号处理
6. **空间感知**  __3D空间理解
7. **情感识别**  __情感分析与回应
8. **意图理解**  __用户意图识别
9. **知识整合**  __跨模态知识关联

## 与其他模块的交互
- 通过量子纠缠信道与QSM主模型交互
- 与SOM子系统进行经济相关交互
- 使用Ref子系统进行量子纠错和数据恢复

## 最近更新
- 添加了WeQ多模态演示页面
- 完善了WeQ导航栏与底部模板
- 统一了WeQ量子纠缠客户端
- 创建了WeQ目录索引结构 

```
```
量子基因编码: QE-WEQ-819EE8B6C90F
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
