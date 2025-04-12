# 量子系统架构与组件说明

## 项目概述

量子系统是一个基于量子概念的多模型集成系统，包含四个主要子模型，共同构建了一个完整的量子应用平台。系统采用模块化设计，各子模型既可以独立运行，也可以集成在主应用中，共享统一的导航和页脚组件。

### 主要子系统

1. **QSM (量子叠加态模型)** - 核心模型，处理量子计算和叠加态功能，提供基础的量子比特操作和量子门电路实现
2. **WeQ (量子情感模型)** - 处理多模态交互和情感分析，支持多种输入方式（文本、语音、图像等）的情感识别
3. **SOM (量子经济模型)** - 实现基于量子原理的经济系统和数字资产管理，包括量子钱包、量子合约等功能
4. **Ref (量子自反省模型)** - 提供自监控、自优化功能，确保系统完整性和性能，实现系统自我修复能力

## 系统架构

![系统架构图](/world/static/images/system_architecture.svg)

系统采用了三层架构设计：

1. **前端层** - 负责用户界面渲染和客户端交互
2. **服务层** - 提供API和业务逻辑处理
3. **基础层** - 包含核心量子算法和数据存储

## 关键组件

### 客户端JavaScript组件

客户端JavaScript组件是系统前端的核心，实现了量子交互的模拟和可视化效果。

- **quantum_loader.js** - 负责加载所有必要的客户端脚本，按需加载策略减少初始加载时间
  ```javascript
  // 调用示例
  document.addEventListener('DOMContentLoaded', function() {
    // quantum_loader.js会自动初始化
  });
  ```

- **web_quantum_client.js** - 建立量子纠缠信道的客户端库，实现浏览器与服务器之间的"量子纠缠"通信
  ```javascript
  // 获取量子客户端实例
  const quantumClient = window.webQuantumInstance;
  ```

- **quantum_entanglement.js** - 实现跨模块量子纠缠通信功能，模拟量子态和量子现象
  ```javascript
  // 监听量子事件
  window.QuantumEntanglement.addEventListener('entangled', function(data) {
    console.log('量子纠缠已建立', data);
  });
  ```

### 服务器组件

服务器组件基于Flask框架构建，实现了各模型的业务逻辑和API功能。

- **app.py** - 主服务器，处理请求分发到各个子模型
- **QSM/app.py** - QSM模型的服务器实现
- **WeQ/app.py** - WeQ模型的服务器实现
- **SOM/app.py** - SOM模型的服务器实现
- **Ref/app.py** - Ref模型的服务器实现

### 模板系统

模板系统基于Jinja2，实现了统一的页面结构和样式。

- **统一导航栏** - 使用shared/navigation.html实现，包含所有模型的导航链接和量子态阵图
- **统一页脚** - 使用shared/footer.html实现，包含系统信息和相关链接
- **基础模板** - 各模型的base_{model}.html文件定义了基本页面结构
- **内容模板** - 各功能页面继承基础模板，只需实现content块

### 量子经济系统

量子经济系统是SOM模型的核心功能，实现了数字资产的管理和交易。

- **quantum_economy/** - 包含区块链、钱包等经济组件
- **quantum_economy/som/** - SOM模型中的经济功能实现
- **quantum_economy/blockchain/** - 区块链基础实现
- **som_wallet.py** - 量子钱包实现
- **som_economy.py** - 经济系统核心逻辑

## 文件结构

```
QSM/
├── app.py               # QSM模型服务器入口
├── main.py              # QSM核心功能
├── quantum_economy/     # 量子经济组件
├── quantum_blockchain/  # 量子区块链组件
├── static/              # 静态资源
└── templates/           # 模板文件
    ├── base_qsm.html    # QSM基础模板
    ├── index.html       # QSM首页
    └── shared/          # 共享模板组件
        ├── navigation.html  # 统一导航栏
        └── footer.html      # 统一页脚

WeQ/
├── app.py               # WeQ模型服务器入口
├── static/              # 静态资源
└── templates/           # 模板文件

SOM/
├── app.py               # SOM模型服务器入口
├── static/              # 静态资源
└── templates/           # 模板文件

Ref/
├── app.py               # Ref模型服务器入口
├── static/              # 静态资源
└── templates/           # 模板文件

world/
├── static/              # 全局静态资源
│   ├── js/              # 全局JavaScript
│   └── css/             # 全局CSS
└── templates/           # 全局模板
    ├── home.html        # 系统首页
    └── components/      # 全局组件

app.py                   # 主服务器入口
```

## 使用说明

### 启动系统

系统可以通过两种方式启动：集成模式和独立模式。

#### 集成模式（推荐）

在集成模式下，所有模型都运行在同一个Flask应用中，共享相同的端口。

```bash
# 在项目根目录下
python app.py
```

#### 独立模式

在独立模式下，各模型运行在不同的端口上，互相通过API通信。

```bash
# 启动QSM服务 (端口5000)
cd QSM && python app.py

# 启动SOM服务 (端口5001)
cd SOM && python app.py

# 启动Ref服务 (端口5002)
cd Ref && python app.py

# 启动WeQ服务 (端口5003)
cd WeQ && python app.py
```

### 访问入口

- 系统主页: http://localhost:5000/
- QSM模型: http://localhost:5000/QSM/
- WeQ模型: http://localhost:5000/WeQ/
- SOM模型: http://localhost:5000/SOM/
- Ref模型: http://localhost:5000/Ref/

### 配置

系统配置可以通过环境变量或配置文件修改：

```bash
# 启用独立服务模式
export STANDALONE_SERVICES=true

# 修改端口
export PORT=8080
```

主要配置文件：
- `config/app_config.json` - 主应用配置
- `config/{model}_config.json` - 各模型配置

## 开发指南

### 添加新页面

1. 在对应模型的templates目录下创建新的HTML文件：

```html
{% extends "base_{model}.html" %}

{% block title %}新页面标题{% endblock %}

{% block content %}
<div class="container">
    <!-- 页面内容 -->
</div>
{% endblock %}
```

2. 在对应模型的app.py中添加路由：

```python
@app.route('/{model}/new_page')
def new_page():
    return render_template('new_page.html')
```

### 添加新API

1. 在对应模型的app.py中添加API路由：

```python
@app.route('/api/{model}/new_endpoint', methods=['POST'])
def new_api_endpoint():
    data = request.json
    # 处理请求
    return jsonify({
        'status': 'success',
        'data': result
    })
```

## 特性和功能

- **统一的用户界面** - 所有模型共享相同的导航栏和页脚
- **量子纠缠通信** - 模拟量子纠缠的通信机制
- **多模态交互** - 支持文本、语音、图像等多种交互方式
- **量子经济系统** - 实现数字资产管理和交易
- **自监控和自优化** - 系统能够自我监控和优化性能

## 常见问题

**Q: 如何修改统一导航栏？**

A: 编辑`templates/shared/navigation.html`文件。

**Q: 系统支持哪些浏览器？**

A: 系统支持现代浏览器，包括Chrome、Firefox、Edge、Safari等。

**Q: 如何添加新的模型？**

A: 创建新的模型目录，实现app.py和必要的模板，然后在主app.py中添加路由代理。

## 结语

量子系统是一个模块化、可扩展的框架，可以通过添加新的模型和功能不断扩展。开发人员可以基于现有模型开发自己的功能，或者创建全新的模型来扩展系统能力。 

```
```
量子基因编码: QE-SYS-FBACEAAA06A8
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
