# 量子系统模板架构指南

## 模板系统概述

量子系统使用基于Jinja2的模板系统，实现了统一的页面结构和组件复用。通过精心设计的模板继承关系，确保了所有模型都具有统一的外观和用户体验，同时又能保持各自的特色。

## 模板继承层级

量子系统的模板继承关系如下：

```
world/templates/base.html (根基础模板)
├── QSM/templates/base_qsm.html (QSM基础模板)
│   └── QSM/templates/index.html (QSM首页)
│   └── QSM/templates/quantum_test.html (量子测试页)
│   └── ...
├── WeQ/templates/base_weq.html (WeQ基础模板)
│   └── WeQ/templates/index.html (WeQ首页)
│   └── ...
├── SOM/templates/base_som.html (SOM基础模板)
│   └── SOM/templates/index.html (SOM首页)
│   └── ...
├── Ref/templates/base_ref.html (Ref基础模板)
│   └── Ref/templates/index.html (Ref首页)
│   └── ...
```

每个模型都有自己的基础模板（如`base_qsm.html`），这些基础模板继承自全局的`base.html`，然后各模型的具体页面（如`index.html`）再继承自对应的基础模板。

## 统一导航栏和页脚

### 导航栏实现

统一导航栏通过`shared/navigation.html`实现，包含以下主要部分：

1. **系统Logo和品牌**：显示当前模型的Logo和名称
2. **主导航链接**：链接到各个模型的首页
3. **量子态阵图按钮**：展示量子态交互菜单
4. **用户菜单**：用户登录、注册和个人中心入口

导航栏示例代码：

```html
<!-- 统一导航栏模板 -->
<header class="unified-nav-header">
  <div class="nav-container">
    <!-- 系统Logo和品牌 -->
    <div class="nav-brand">
      <a href="/QSM/" class="logo-link">
        <img id="nav-logo" src="/templates/shared/images/qsm-logo.svg" alt="QSM Logo" class="nav-logo">
        <span class="brand-text">量子叠加态模型</span>
      </a>
    </div>
    
    <!-- 主导航链接 -->
    <nav class="main-nav">
      <ul class="nav-links">
        <li>
          <a href="/QSM/" class="system-link" data-system="qsm">
            <span class="nav-icon">⚛️</span>
            <span class="nav-text">主量子区块链</span>
          </a>
        </li>
        <!-- 其他导航链接 -->
      </ul>
    </nav>
    
    <!-- 量子态阵图按钮 -->
    <div class="quantum-state-container">
      <button id="quantum-state-btn" class="quantum-state-btn" aria-label="量子态阵图">
        <!-- 量子态阵图内容 -->
      </button>
    </div>
    
    <!-- 用户菜单 -->
    <div class="user-menu-container">
      <!-- 用户菜单内容 -->
    </div>
  </div>
</header>
```

### 页脚实现

统一页脚通过`shared/footer.html`实现，包含以下主要部分：

1. **顶部Logo展示区**：显示各模型的Logo和口号
2. **底部导航链接区**：提供各种相关链接分组
3. **底部社交媒体链接**：链接到社交媒体账号
4. **底部版权和备案信息**：显示版权信息和备案号

页脚示例代码：

```html
<!-- 统一底部栏模板 -->
<footer class="footer">
  <div class="footer-container">
    <!-- 顶部Logo展示区 -->
    <div class="footer-logos">
      <!-- 各模型Logo -->
    </div>

    <!-- 底部导航链接区 -->
    <div class="footer-links">
      <!-- 链接分组 -->
    </div>

    <!-- 底部社交媒体链接 -->
    <div class="footer-social">
      <!-- 社交媒体链接 -->
    </div>

    <!-- 底部版权和备案信息 -->
    <div class="footer-bottom">
      <p>© <span id="currentYear">2025</span> 量子叠加态模型(QSM) 版权所有</p>
      <p>沪ICP备XXXXXXXX号-X · 沪公网安备 XXXXXXXXXXXX号</p>
    </div>
  </div>
</footer>
```

## 模板嵌套块设计

量子系统的模板使用了以下主要块（Block）：

- **title**：页面标题
- **head_extra**：额外的头部内容（CSS、Meta等）
- **model_css**：模型特定的CSS
- **model_nav**：模型特定的导航
- **content**：主内容区域
- **model_js**：模型特定的JavaScript
- **scripts_extra**：额外的脚本

基础模板示例：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}量子系统{% endblock %}</title>
    
    <!-- 全局样式 -->
    <link href="/world/static/css/normalize.css" rel="stylesheet">
    <link href="/world/static/css/quantum-theme.css" rel="stylesheet">
    
    <!-- 模型特定样式 -->
    {% block model_css %}{% endblock %}
    
    <!-- 额外头部内容 -->
    {% block head_extra %}{% endblock %}
</head>
<body>
    <!-- 统一导航栏 -->
    {% include "shared/navigation.html" %}
    
    <!-- 模型特定导航 -->
    {% block model_nav %}{% endblock %}
    
    <!-- 主内容区域 -->
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <!-- 统一页脚 -->
    {% include "shared/footer.html" %}
    
    <!-- 全局脚本 -->
    <script src="/world/static/js/quantum_loader.js"></script>
    
    <!-- 模型特定脚本 -->
    {% block model_js %}{% endblock %}
    
    <!-- 额外脚本 -->
    {% block scripts_extra %}{% endblock %}
</body>
</html>
```

## 模型特定模板

### QSM模型模板

QSM模型的基础模板（`base_qsm.html`）定义了QSM特有的样式和脚本：

```html
{% extends "base.html" %}

{% block title %}量子叠加态模型 (QSM){% endblock %}

{% block model_css %}
<link href="/QSM/static/css/qsm.css" rel="stylesheet">
{% endblock %}

{% block model_nav %}
<nav class="model-nav qsm-nav">
    <div class="container">
        <ul>
            <li><a href="/QSM/">QSM首页</a></li>
            <li><a href="/QSM/quantum_test">量子测试</a></li>
            <li><a href="/QSM/quantum_experience">量子体验</a></li>
            <li><a href="/QSM/api_client">API客户端</a></li>
        </ul>
    </div>
</nav>
{% endblock %}

{% block model_js %}
<script src="/QSM/static/js/qsm_core.js"></script>
{% endblock %}
```

QSM页面示例（`index.html`）：

```html
{% extends "base_qsm.html" %}

{% block title %}量子叠加态模型 (QSM) - 首页{% endblock %}

{% block content %}
<div class="hero-section">
    <h1>量子叠加态模型 (QSM)</h1>
    <p class="lead">欢迎使用量子叠加态模型，这是一个基于量子计算的高性能模拟与处理系统。</p>
</div>

<!-- 页面内容 -->
{% endblock %}
```

### 其他模型的模板

其他模型（WeQ、SOM、Ref）的模板结构与QSM类似，各自包含模型特定的样式、导航和脚本。

## 主页模板

系统主页（`world/templates/home.html`）直接包含导航栏和页脚组件：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>量子系统首页</title>
    <!-- 样式和脚本引用 -->
</head>
<body>
    <!-- 统一导航栏 -->
    {% include "QSM/templates/shared/navigation.html" %}
    
    <div class="container">
        <!-- 主页内容 -->
    </div>
    
    <!-- 统一页脚 -->
    {% include "QSM/templates/shared/footer.html" %}
</body>
</html>
```

## 模板加载和渲染

系统使用Flask的模板加载机制，通过Flask蓝图（Blueprint）注册多个模板文件夹：

```python
template_dirs = [
    os.path.join(root_dir, 'world', 'templates'),
    os.path.join(root_dir, 'QSM', 'templates'),
    os.path.join(root_dir, 'WeQ', 'templates'),
    os.path.join(root_dir, 'SOM', 'templates'),
    os.path.join(root_dir, 'Ref', 'templates')
]
app.jinja_env.loader = FileSystemLoader(template_dirs)
```

这样，在渲染模板时，可以使用相对路径引用不同目录下的模板：

```python
@app.route('/QSM/')
def qsm_index():
    return render_template('QSM/templates/index.html')
```

## 模板静态资源

每个模型都有自己的静态资源目录（`static/`），包含CSS、JavaScript和图像等文件。全局的静态资源存放在`world/static/`目录下。

静态资源的URL路径映射如下：

- 全局静态资源：`/world/static/`
- QSM静态资源：`/QSM/static/`
- WeQ静态资源：`/WeQ/static/`
- SOM静态资源：`/SOM/static/`
- Ref静态资源：`/Ref/static/`

## 最佳实践

### 开发新页面

1. 在对应模型的templates目录下创建HTML文件
2. 继承对应的base_{model}.html
3. 只实现需要的块（content、title等）
4. 使用container类包裹内容，确保响应式布局

### 修改导航和页脚

1. 避免直接修改navigation.html和footer.html
2. 如需添加特定链接，使用model_nav块
3. 确保所有链接正确指向各模型的URL

### 共享组件

对于多个页面共用的组件，建议：

1. 创建单独的组件文件，如`templates/shared/components/card.html`
2. 使用Jinja2的include语句引入组件：`{% include "shared/components/card.html" %}`
3. 通过参数传递数据：`{% include "shared/components/card.html" with title="标题" %}`

## 总结

量子系统的模板架构采用了层次清晰的继承关系，通过共享的导航栏和页脚组件，确保了统一的用户体验。开发者可以方便地创建新页面，并使用丰富的模板块来定制内容。这种模块化的设计使得系统易于维护和扩展。 

```
```
量子基因编码: QE-TEM-37E56B727AB0
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
