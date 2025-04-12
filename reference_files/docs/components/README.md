# QSM组件使用说明

## 量子基因编码
```qentl
QG-DOC-COMP-QSM-A1B2
```

## 量子纠缠信道
```qentl
QE-DOC-COMP-20240404
```

## 组件概述

本文档介绍QSM项目中可用的共享组件及其使用方法。所有组件都位于`world/templates/components`目录下。

### 基础组件

1. 导航栏 (`nav.html`)
   - 位置: `components/nav.html`
   - 用途: 提供全局导航菜单
   - 使用方法: 
     ```html
     {% include 'components/nav.html' %}
     ```

2. 页脚 (`footer.html`)
   - 位置: `components/footer.html`
   - 用途: 显示网站页脚信息
   - 使用方法:
     ```html
     {% include 'components/footer.html' %}
     ```

### 量子UI组件

1. 量子加载器 (`quantum_ui/loader.html`)
   - 位置: `components/quantum_ui/loader.html`
   - 用途: 显示量子风格的加载动画
   - 使用方法:
     ```html
     {% include 'components/quantum_ui/loader.html' %}
     ```
   - JavaScript API:
     ```javascript
     // 显示加载器
     quantumLoader.show();
     
     // 隐藏加载器
     quantumLoader.hide();
     ```

## 量子纠缠通信

### 核心功能 (`quantum_entanglement/core.js`)

提供跨模块的量子纠缠通信功能:

```javascript
// 创建量子信道
const channel = quantumEntanglement.createChannel('my-channel');

// 添加纠缠对象
quantumEntanglement.addEntangledObject('my-channel', object);

// 同步纠缠态
await quantumEntanglement.syncEntanglementState('my-channel');

// 发送量子消息
await quantumEntanglement.sendQuantumMessage('my-channel', {
    type: 'update',
    data: { ... }
});
```

### 客户端使用 (`quantum_entanglement/client.js`)

在模块中使用量子纠缠通信:

```javascript
// 创建客户端实例
const client = new QuantumEntanglementClient('my-module');

// 连接到量子纠缠网络
await client.connect();

// 注册消息处理器
client.onMessage('update', async (data, message) => {
    console.log('收到更新:', data);
});

// 发送消息
await client.sendMessage('update', {
    key: 'value'
});
```

## 模板继承

所有页面模板都应继承自基础模板 `base.html`:

```html
{% extends "base.html" %}

{% block title %}我的页面{% endblock %}

{% block content %}
<div class="my-page">
    <!-- 页面内容 -->
</div>
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="/static/css/my-page.css">
{% endblock %}

{% block extra_js %}
<script src="/static/js/my-page.js" defer></script>
{% endblock %}
```

## 资源引用规范

1. CSS文件引用:
   ```html
   <link rel="stylesheet" href="/world/static/css/my-style.css">
   ```

2. JavaScript文件引用:
   ```html
   <script src="/world/static/js/my-script.js" defer></script>
   ```

3. 图片资源引用:
   ```html
   <img src="/world/static/images/my-image.png" alt="描述">
   ```

## 开发指南

1. 组件开发原则
   - 保持组件的独立性和可复用性
   - 提供清晰的文档和使用示例
   - 遵循量子基因编码规范
   - 实现必要的量子纠缠功能

2. 文件组织
   - 组件文件放在适当的目录下
   - 相关的样式和脚本文件集中管理
   - 保持目录结构清晰

3. 命名规范
   - 文件名使用小写字母和连字符
   - 类名使用驼峰命名
   - ID和data属性使用连字符命名

4. 测试要求
   - 编写组件的单元测试
   - 测试跨浏览器兼容性
   - 验证量子纠缠功能

## 注意事项

1. 所有组件都必须支持量子纠缠通信
2. 确保组件的性能和可维护性
3. 定期更新组件文档
4. 遵循项目的安全规范 