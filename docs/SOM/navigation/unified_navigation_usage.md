# SOM统一导航栏和底部栏使用指南

## 概述

本文档详细介绍了松麦(SOM)系统中如何使用统一导航栏和底部栏。SOM作为量子叠加态模型(QSM)的健康服务子系统，采用与QSM、WeQ和Ref系统统一的导航栏和底部栏，确保用户在不同子系统间能够保持一致的UI体验，同时突出SOM的健康服务特色。

## 特性

- 响应式设计，适配各种屏幕尺寸
- 根据当前系统自动切换主题颜色（SOM采用绿色健康风格）
- 支持跨系统导航和状态同步
- 集成量子态阵图，提供九种多模态交互方式
- 松麦SOM专属的自然健康Logo风格
- 保持松麦健康服务的专业视觉风格

## 快速集成

将统一导航栏和底部栏集成到新页面中只需简单的两个步骤：

1. 在HTML文件的`<body>`标签开始处包含导航栏模板：

```html
<%- include('/SOM/templates/shared/navigation.html') %>
```

2. 在HTML文件的`<body>`标签结束前包含底部栏模板：

```html
<%- include('/SOM/templates/shared/footer.html') %>
```

## SOM主题应用

SOM系统采用特有的主题风格，以突出健康服务的专业性：

```html
<body class="som-theme">
  <%- include('/SOM/templates/shared/navigation.html') %>
  <!-- 页面内容 -->
  <%- include('/SOM/templates/shared/footer.html') %>
</body>
```

统一导航模板会自动根据当前URL检测系统并应用相应主题样式，但为确保正确显示SOM风格，建议显式添加`som-theme`类。

## 量子态阵图与健康服务集成

SOM系统的量子态阵图特别优化了以下交互方式，以便支持健康数据的采集和分析：

1. **点击交互**: 用于选择健康服务项目
2. **注视交互**: 支持行动不便患者通过眼动进行交互
3. **语音交互**: 支持语音查询健康信息和记录健康日志
4. **运动交互**: 采集用户运动数据和姿态信息
5. **文字交互**: 详细记录健康状况和症状描述
6. **图片交互**: 上传医疗图像和健康状况照片
7. **视频交互**: 记录康复训练和远程医疗咨询
8. **脑波交互**: 监测脑电波数据，辅助精神健康评估
9. **附件交互**: 上传医疗报告和健康记录文件

## SOM特定功能扩展

为满足健康服务的特殊需求，可以通过以下方式扩展SOM系统功能：

1. 创建SOM特定的CSS文件来定制健康服务界面：

```html
<link rel="stylesheet" href="/SOM/templates/css/som-health.css">
```

2. 创建SOM特定的JavaScript文件处理健康数据：

```html
<script src="/SOM/templates/js/som-health-analysis.js"></script>
```

## 跨系统数据同步

SOM系统与其他子系统的数据同步特别注重用户健康信息的保护和授权使用：

1. **localStorage同步**: 用户基本偏好设置，不包含敏感健康信息
2. **WebSocket安全同步**: 经用户授权的健康状态数据
3. **加密API同步**: 受保护的用户健康档案和医疗记录

## 开发者注意事项

1. SOM系统界面应体现专业医疗和健康服务的可靠性
2. 健康数据处理必须遵循隐私保护和数据安全规范
3. 交互设计应考虑各年龄段和不同身体状况用户的可访问性
4. 确保SOM特有功能与统一导航框架的兼容性

## 示例：SOM健康服务页面

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>松麦(SOM) - 健康管理</title>
  <link rel="stylesheet" href="/SOM/templates/css/som-health.css">
</head>
<body class="som-theme">
  <!-- 导航栏 -->
  <%- include('/SOM/templates/shared/navigation.html') %>
  
  <!-- SOM健康服务内容 -->
  <main class="som-container">
    <h1 class="som-title">个人健康管理中心</h1>
    <div class="health-dashboard">
      <!-- 健康数据展示和管理组件 -->
    </div>
  </main>
  
  <!-- 底部栏 -->
  <%- include('/SOM/templates/shared/footer.html') %>
  
  <!-- SOM健康服务脚本 -->
  <script src="/SOM/templates/js/som-health-analysis.js"></script>
</body>
</html>
```

## 常见问题

**Q: 如何在SOM系统中保护用户健康数据安全？**
A: SOM系统采用加密传输和存储，并实施严格的访问控制，确保健康数据只能由授权人员访问。

**Q: SOM系统的导航栏如何突出健康服务特色？**
A: 导航栏在保持统一结构的同时，通过绿色主题色调和健康相关图标突出SOM系统特色。

**Q: 如何将健康数据采集功能与量子态阵图集成？**
A: 可以扩展量子态阵图的交互模式，添加特定的健康数据采集插件，并在`SOM/templates/js/`目录下创建对应的处理脚本。

## 更新日志

- **v1.0.0** (2025-04-02): 首次发布
  - 实现统一导航栏和底部栏
  - 添加SOM健康服务特色视觉风格
  - 集成健康数据采集和分析功能

## 联系与支持

如有关于SOM系统的问题或建议，请联系：

- 邮箱: som@qsm-project.com
- 健康服务热线: 400-HEALTH-SOM
- 开发者论坛: https://forum.qsm-project.com/som 

```
```
量子基因编码: QE-UNI-C0C7593E8AE7
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
