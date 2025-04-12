# WeQ统一导航栏和底部栏使用指南

## 概述

本文档详细介绍了小趣(WeQ)系统中如何使用统一导航栏和底部栏。WeQ作为量子叠加态模型(QSM)的重要组成部分，采用与QSM、SOM和Ref系统统一的导航栏和底部栏，确保用户在不同子系统间能够保持一致的UI体验。

## 特性

- 响应式设计，适配各种屏幕尺寸
- 根据当前系统自动切换主题颜色（WeQ采用渐变色彩风格）
- 支持跨系统导航和状态同步
- 集成量子态阵图，提供九种多模态交互方式
- 小趣WeQ专属的可爱Logo风格
- 与其他子系统保持统一的交互模式

## 快速集成

将统一导航栏和底部栏集成到新页面中只需简单的两个步骤：

1. 在HTML文件的`<body>`标签开始处包含导航栏模板：

```html
<%- include('/WeQ/templates/shared/navigation.html') %>
```

2. 在HTML文件的`<body>`标签结束前包含底部栏模板：

```html
<%- include('/WeQ/templates/shared/footer.html') %>
```

## WeQ主题应用

WeQ系统采用特有的主题风格，以展现小趣的可爱特性：

```html
<body class="weq-theme">
  <%- include('/WeQ/templates/shared/navigation.html') %>
  <!-- 页面内容 -->
  <%- include('/WeQ/templates/shared/footer.html') %>
</body>
```

统一导航模板会自动根据当前URL检测系统并应用相应主题样式，但为确保正确显示WeQ风格，建议显式添加`weq-theme`类。

## 量子态阵图与多模态交互

WeQ系统的量子态阵图提供九种多模态交互方式，特别优化了语音和注视两种交互模式，以提升用户体验：

1. **点击交互**: 通过点击元素进行交互
2. **注视交互**: 通过眼动追踪进行交互（WeQ特色功能）
3. **语音交互**: 通过语音输入进行交互（WeQ特色功能）
4. **运动交互**: 通过移动设备传感器交互
5. **文字交互**: 通过文本输入进行交互
6. **图片交互**: 通过图片上传或拍照交互
7. **视频交互**: 通过视频上传或录制交互
8. **脑波交互**: 通过脑电波信号交互
9. **附件交互**: 通过文件上传交互

## 定制WeQ特定功能

如需增加WeQ特有的交互功能，可以通过以下方式扩展：

1. 创建WeQ特定的CSS文件来覆盖默认样式：

```html
<link rel="stylesheet" href="/WeQ/templates/css/weq-custom.css">
```

2. 创建WeQ特定的JavaScript文件处理特殊交互：

```html
<script src="/WeQ/templates/js/weq-interaction.js"></script>
```

## 数据同步机制

小趣(WeQ)系统的多模态交互状态会自动与其他系统同步，确保用户在系统间切换时体验的连贯性：

1. **localStorage同步**: 用户偏好设置和交互历史
2. **WebSocket实时同步**: 量子态阵图状态
3. **API状态同步**: 用户登录状态和权限

## 开发者注意事项

1. WeQ系统的设计风格偏向可爱和趣味性，但应保持与统一导航的结构一致
2. 多模态交互的实现应考虑WeQ的语音和注视特色
3. 当添加WeQ特有功能时，确保不破坏统一导航和底部栏的基本结构
4. WeQ特有的动画效果应适当，不影响页面性能

## 示例：WeQ特色页面

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>小趣(WeQ) - 多模态交互</title>
</head>
<body class="weq-theme">
  <!-- 导航栏 -->
  <%- include('/WeQ/templates/shared/navigation.html') %>
  
  <!-- WeQ特色内容 -->
  <main class="weq-container">
    <h1 class="weq-title">欢迎来到小趣的世界</h1>
    <div class="weq-interaction-panel">
      <!-- WeQ特色交互组件 -->
    </div>
  </main>
  
  <!-- 底部栏 -->
  <%- include('/WeQ/templates/shared/footer.html') %>
  
  <!-- WeQ特有脚本 -->
  <script src="/WeQ/templates/js/weq-interaction.js"></script>
</body>
</html>
```

## 常见问题

**Q: 如何修改WeQ系统的公告内容？**
A: 修改`WeQ/templates/shared/js/navigation.js`中的`initAnnouncements`函数内WeQ系统的公告文本。

**Q: 如何为WeQ添加特殊交互效果？**
A: 在保持统一导航栏结构的前提下，创建WeQ特定的CSS和JavaScript文件实现特殊效果。

**Q: WeQ的多模态交互与其他系统有何区别？**
A: WeQ系统优化了语音和注视交互，提供更加友好和趣味性的用户体验，但基本结构与其他系统保持一致。

## 更新日志

- **v1.0.0** (2025-04-02): 首次发布
  - 实现统一导航栏和底部栏
  - 优化WeQ特色的语音和注视交互
  - 添加WeQ特有的趣味性动画效果

## 联系与支持

如有关于WeQ系统的问题或建议，请联系：

- 邮箱: weq@qsm-project.com
- 开发者论坛: https://forum.qsm-project.com/weq 

```
```
量子基因编码: QE-UNI-D1A1F0ED6D22
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
