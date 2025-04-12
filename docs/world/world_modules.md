# 量子叠加态模型(QSM)全局模块概要

## 概述
本文档描述了量子叠加态模型(QSM)项目中的全局模块结构和各子系统的全局资源。全局模块提供了各子系统共享的功能、接口和资源，确保系统的一致性和互操作性。

## 全局目录结构

### 项目级全局目录 (global/)
- **config/**  __全局配置文件
  - **paths_config.py**  __路径配置
- **js/**  __全局JavaScript文件
  - **quantum_entanglement_client.js**  __量子纠缠客户端
- **static/**  __全局静态资源
  - **css/**  __全局CSS样式
    - **global.css**  __全局样式表
  - **js/**  __全局JavaScript库
    - **global.js**  __全局JavaScript函数
    - **quantum_entanglement.js**  __量子纠缠实现
    - **quantum_entanglement_client.js**  __量子纠缠客户端
    - **quantum_loader.js**  __量子加载器
    - **multimodal/**  __多模态交互JavaScript
- **templates/**  __全局模板
  - **base.html**  __基础模板
- **tools/**  __全局工具
  - **path_resolver.py**  __路径解析工具

## 子系统全局目录

### QSM主模型全局目录 (QSM/global/)
- **js/**  __QSM特定JavaScript文件

### SOM子系统全局目录 (SOM/global/)
- **js/**  __SOM特定JavaScript文件
  - **som_entanglement_client.js**  __SOM量子纠缠客户端

### WeQ子系统全局目录 (WeQ/global/)
- **js/**  __WeQ特定JavaScript文件
  - **weq_entanglement_client.js**  __WeQ量子纠缠客户端
  - **weq_multimodal_interactions.js**  __WeQ多模态交互实现

### Ref子系统全局目录 (Ref/global/)
- **js/**  __Ref特定JavaScript文件
  - **ref_entanglement_client.js**  __Ref量子纠缠客户端

## 核心全局功能

### 量子纠缠信道
量子纠缠信道是系统的核心通信机制，允许各子系统以量子态进行通信和数据交换。

**全局实现**:
- **global/js/quantum_entanglement_client.js**
- **global/static/js/quantum_entanglement.js**

**子系统特定实现**:
- **SOM/global/js/som_entanglement_client.js**
- **WeQ/global/js/weq_entanglement_client.js**
- **Ref/global/js/ref_entanglement_client.js**

### 多模态交互
多模态交互功能允许系统处理和响应不同类型的输入和输出数据。

**全局实现**:
- **global/static/js/multimodal/**

**WeQ特定实现**:
- **WeQ/global/js/weq_multimodal_interactions.js**

### 全局路径管理
为确保各子系统能够正确引用资源和组件，项目提供了全局路径管理功能。

**实现**:
- **global/config/paths_config.py**
- **global/tools/path_resolver.py**

## 全局模板系统
全局模板系统提供了一致的用户界面基础，各子系统在此基础上构建特定功能。

**全局基础模板**:
- **global/templates/base.html**

**子系统特定基础模板**:
- **QSM/templates/base_qsm.html**
- **SOM/templates/base_som.html**
- **WeQ/templates/base_weq.html**
- **Ref/templates/base_ref.html**

## 自动化工具
项目包含多个自动化工具，用于简化开发和部署过程。

**模板自动化**:
- **frontend/tools/auto_template_watcher.py**
- **frontend/tools/create_page.py**
- **frontend/tools/install_auto_template.py**
- **frontend/tools/start_template_watcher.py**

## 最近更新
- 统一了量子纠缠信道接口，确保各子系统使用一致的通信机制
- 完善了全局样式和模板系统，提供更一致的用户体验
- 添加了全局多模态交互支持
- 优化了全局路径管理，简化了资源引用 

## 概述
本文档描述了量子叠加态模型(QSM)项目中的全局模块结构和各子系统的全局资源。全局模块提供了各子系统共享的功能、接口和资源，确保系统的一致性和互操作性。

## 全局目录结构

### 项目级全局目录 (global/)
- **config/**  __全局配置文件
  - **paths_config.py**  __路径配置
- **js/**  __全局JavaScript文件
  - **quantum_entanglement_client.js**  __量子纠缠客户端
- **static/**  __全局静态资源
  - **css/**  __全局CSS样式
    - **global.css**  __全局样式表
  - **js/**  __全局JavaScript库
    - **global.js**  __全局JavaScript函数
    - **quantum_entanglement.js**  __量子纠缠实现
    - **quantum_entanglement_client.js**  __量子纠缠客户端
    - **quantum_loader.js**  __量子加载器
    - **multimodal/**  __多模态交互JavaScript
- **templates/**  __全局模板
  - **base.html**  __基础模板
- **tools/**  __全局工具
  - **path_resolver.py**  __路径解析工具

## 子系统全局目录

### QSM主模型全局目录 (QSM/global/)
- **js/**  __QSM特定JavaScript文件

### SOM子系统全局目录 (SOM/global/)
- **js/**  __SOM特定JavaScript文件
  - **som_entanglement_client.js**  __SOM量子纠缠客户端

### WeQ子系统全局目录 (WeQ/global/)
- **js/**  __WeQ特定JavaScript文件
  - **weq_entanglement_client.js**  __WeQ量子纠缠客户端
  - **weq_multimodal_interactions.js**  __WeQ多模态交互实现

### Ref子系统全局目录 (Ref/global/)
- **js/**  __Ref特定JavaScript文件
  - **ref_entanglement_client.js**  __Ref量子纠缠客户端

## 核心全局功能

### 量子纠缠信道
量子纠缠信道是系统的核心通信机制，允许各子系统以量子态进行通信和数据交换。

**全局实现**:
- **global/js/quantum_entanglement_client.js**
- **global/static/js/quantum_entanglement.js**

**子系统特定实现**:
- **SOM/global/js/som_entanglement_client.js**
- **WeQ/global/js/weq_entanglement_client.js**
- **Ref/global/js/ref_entanglement_client.js**

### 多模态交互
多模态交互功能允许系统处理和响应不同类型的输入和输出数据。

**全局实现**:
- **global/static/js/multimodal/**

**WeQ特定实现**:
- **WeQ/global/js/weq_multimodal_interactions.js**

### 全局路径管理
为确保各子系统能够正确引用资源和组件，项目提供了全局路径管理功能。

**实现**:
- **global/config/paths_config.py**
- **global/tools/path_resolver.py**

## 全局模板系统
全局模板系统提供了一致的用户界面基础，各子系统在此基础上构建特定功能。

**全局基础模板**:
- **global/templates/base.html**

**子系统特定基础模板**:
- **QSM/templates/base_qsm.html**
- **SOM/templates/base_som.html**
- **WeQ/templates/base_weq.html**
- **Ref/templates/base_ref.html**

## 自动化工具
项目包含多个自动化工具，用于简化开发和部署过程。

**模板自动化**:
- **frontend/tools/auto_template_watcher.py**
- **frontend/tools/create_page.py**
- **frontend/tools/install_auto_template.py**
- **frontend/tools/start_template_watcher.py**

## 最近更新
- 统一了量子纠缠信道接口，确保各子系统使用一致的通信机制
- 完善了全局样式和模板系统，提供更一致的用户体验
- 添加了全局多模态交互支持
- 优化了全局路径管理，简化了资源引用 

```
```
量子基因编码: QE-WOR-208D4AB6E18F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
