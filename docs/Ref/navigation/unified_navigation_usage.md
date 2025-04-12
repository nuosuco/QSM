# Ref统一导航栏和底部栏使用指南

## 概述

本文档详细介绍了量子基因参考系统(Ref)中如何使用统一导航栏和底部栏。Ref作为量子叠加态模型(QSM)的知识库子系统，采用与QSM、WeQ和SOM系统统一的导航栏和底部栏，确保用户在不同子系统间能够保持一致的UI体验，同时突出Ref的知识库和参考资料特色。

## 特性

- 响应式设计，适配各种屏幕尺寸
- 根据当前系统自动切换主题颜色（Ref采用紫色学术风格）
- 支持跨系统导航和状态同步
- 集成量子态阵图，提供九种多模态交互方式
- Ref专属的学术Logo风格
- 针对参考资料与知识库的优化UI元素

## 快速集成

将统一导航栏和底部栏集成到新页面中只需简单的两个步骤：

1. 在HTML文件的`<body>`标签开始处包含导航栏模板：

```html
<%- include('/Ref/templates/shared/navigation.html') %>
```

2. 在HTML文件的`<body>`标签结束前包含底部栏模板：

```html
<%- include('/Ref/templates/shared/footer.html') %>
```

## Ref主题应用

Ref系统采用特有的主题风格，以突出知识库的学术性：

```html
<body class="ref-theme">
  <%- include('/Ref/templates/shared/navigation.html') %>
  <!-- 页面内容 -->
  <%- include('/Ref/templates/shared/footer.html') %>
</body>
```

统一导航模板会自动根据当前URL检测系统并应用相应主题样式，但为确保正确显示Ref风格，建议显式添加`ref-theme`类。

## 量子态阵图与知识库集成

Ref系统的量子态阵图特别优化了以下交互方式，以便支持知识检索和学习：

1. **点击交互**: 导航至特定知识条目
2. **注视交互**: 基于用户阅读行为推荐相关参考资料
3. **语音交互**: 支持语音查询量子基因知识库
4. **运动交互**: 基于交互姿态进行知识空间探索
5. **文字交互**: 高级语义搜索和知识问答
6. **图片交互**: 图像识别与知识匹配
7. **视频交互**: 视频知识讲解与教学内容
8. **脑波交互**: 基于认知活动推荐学习内容
9. **附件交互**: 支持上传论文与研究资料进行分析

## Ref特定功能扩展

为满足知识库系统的特殊需求，可以通过以下方式扩展Ref系统功能：

1. 创建Ref特定的CSS文件来定制知识库界面：

```html
<link rel="stylesheet" href="/Ref/templates/css/ref-knowledge.css">
```

2. 创建Ref特定的JavaScript文件处理知识检索：

```html
<script src="/Ref/templates/js/ref-knowledge-search.js"></script>
```

## 跨系统数据同步

Ref系统与其他子系统的数据同步特别关注学术引用和知识共享：

1. **localStorage同步**: 用户阅读历史和偏好设置
2. **WebSocket同步**: 知识库检索记录和阅读进度
3. **API同步**: 量子基因知识图谱和专业词汇表

## 开发者注意事项

1. Ref系统界面应体现学术严谨和专业参考的特质
2. 知识条目展示应注重结构化和可引用性
3. 交互设计应支持高效的知识检索和深度学习
4. 确保Ref特有的学术功能与统一导航框架的兼容性

## 示例：Ref知识库页面

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>量子基因参考系统(Ref) - 知识库</title>
  <link rel="stylesheet" href="/Ref/templates/css/ref-knowledge.css">
</head>
<body class="ref-theme">
  <!-- 导航栏 -->
  <%- include('/Ref/templates/shared/navigation.html') %>
  
  <!-- Ref知识库内容 -->
  <main class="ref-container">
    <h1 class="ref-title">量子基因知识索引</h1>
    <div class="knowledge-browser">
      <!-- 知识条目浏览与检索组件 -->
    </div>
  </main>
  
  <!-- 底部栏 -->
  <%- include('/Ref/templates/shared/footer.html') %>
  
  <!-- Ref知识库脚本 -->
  <script src="/Ref/templates/js/ref-knowledge-search.js"></script>
</body>
</html>
```

## 常见问题

**Q: 如何在Ref系统中实现知识条目的引用功能？**
A: Ref系统提供了`ref-citation.js`工具，可以生成任何知识条目的引用链接和引用格式。

**Q: Ref系统的导航栏如何突出知识库特色？**
A: 导航栏在保持统一结构的同时，通过紫色学术主题和知识分类菜单突出Ref系统特色。

**Q: 如何将新的知识条目添加到量子态阵图交互中？**
A: 可以通过`Ref/templates/js/quantum-knowledge-matrix.js`注册新的知识节点，并设置其与九种交互模式的关联。

## 更新日志

- **v1.0.0** (2025-04-02): 首次发布
  - 实现统一导航栏和底部栏
  - 添加Ref知识库特色视觉风格
  - 集成知识检索和引用功能

## 联系与支持

如有关于Ref系统的问题或建议，请联系：

- 邮箱: ref@qsm-project.com
- 学术合作: academic@qsm-project.com
- 开发者论坛: https://forum.qsm-project.com/ref 

```
```
量子基因编码: QE-UNI-35DD2083DE61
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
