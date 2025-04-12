# 量子叠加模型系统资源组织

本文档整理了量子叠加模型系统(QSM)项目中的所有全局及各模型特定的资源文件，包括JavaScript、CSS和HTML模板等。

## 目录结构

项目主要包含以下模块:

1. `world` - 全局共享模块
2. `QSM` - 量子叠加态模型
3. `WeQ` - 量子情感模型
4. `SOM` - 量子经济模型
5. `Ref` - 量子自反省模型

## 全局资源文件 (world模块)

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/world/static/js/quantum_entanglement.js` | 量子纠缠通信核心JS，提供跨模块的量子纠缠通信功能 | 已创建 |
| `/world/static/js/quantum_entanglement_client.js` | 量子纠缠客户端JS | 已创建 |
| `/world/static/js/quantum_loader.js` | 量子加载器，处理资源加载 | 已创建 | 
| `/world/static/js/global.js` | 全局通用功能JS | 已创建 |

### CSS文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/world/static/css/normalize.css` | CSS标准化样式 | 已创建 |
| `/world/static/css/quantum-theme.css` | 量子主题样式 | 已创建 |
| `/world/static/css/global.css` | 全局通用样式 | 已创建 |

### HTML模板

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/world/templates/base.html` | 全局基础模板，包含共享导航栏和页脚 | 已创建 |

## QSM模块资源

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/QSM/static/js/qsm_core.js` | QSM核心功能JS | 已创建 |

### CSS文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/QSM/static/css/qsm.css` | QSM模块样式 | 已创建 |

### HTML模板

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/QSM/templates/base_qsm.html` | QSM基础模板，扩展自全局base.html | 已创建 |
| `/QSM/templates/index.html` | QSM首页 | 已创建 |
| `/QSM/templates/api_client.html` | API客户端页面 | 已创建 |
| `/QSM/templates/quantum_test.html` | 量子测试页面 | 已创建 |
| `/QSM/templates/quantum_experience.html` | 量子体验页面 | 已创建 |

## WeQ模块资源

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/WeQ/static/js/multimodal_interaction.js` | 多模态交互JS | 已创建 |
| `/WeQ/static/js/weq_multimodal.js` | WeQ多模态功能JS | 已创建 |
| `/WeQ/static/js/weq_ref_integration.js` | WeQ和Ref模块集成JS | 已创建 |
| `/WeQ/static/js/weq_entanglement_client.js` | WeQ量子纠缠客户端JS | 已创建 |
| `/WeQ/static/js/weq_multimodal_interactions.js` | 多模态交互扩展JS | 已创建 |

### CSS文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/WeQ/static/css/weq.css` | WeQ模块样式 | 已创建 |
| `/WeQ/static/css/weq_multimodal.css` | WeQ多模态界面样式 | 已创建 |

### HTML模板

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/WeQ/templates/base_weq.html` | WeQ基础模板 | 已创建 |
| `/WeQ/templates/index.html` | WeQ首页 | 已创建 |
| `/WeQ/templates/weq_multimodal_demo.html` | WeQ多模态演示页面 | 已创建 |

## SOM模块资源

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/SOM/static/js/som_entanglement_client.js` | SOM量子纠缠客户端JS | 已创建 |

### CSS文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/SOM/static/css/som.css` | SOM模块样式 | 已创建 |

### HTML模板

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/SOM/templates/base_som.html` | SOM基础模板 | 已创建 |
| `/SOM/templates/index.html` | SOM首页 | 已创建 |

## Ref模块资源

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/Ref/static/js/quantum_entanglement_client.js` | 量子纠缠客户端JS | 已创建 |
| `/Ref/static/js/ref_entanglement_client.js` | 量子自反省模型专用量子纠缠客户端JS | 已创建 |

### CSS文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/Ref/static/css/ref.css` | 量子自反省模型样式 | 已创建 |
| `/Ref/static/css/ref_dashboard.css` | 量子自反省模型仪表盘样式 | 已创建 |

### HTML模板

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/Ref/templates/base_ref.html` | 量子自反省模型基础模板 | 已创建 |
| `/Ref/templates/index.html` | 量子自反省模型首页 | 已创建 |
| `/Ref/templates/quantum_entanglement_comm.html` | 量子纠缠通信页面 | 已创建 |
| `/Ref/templates/dashboard.html` | 量子自反省模型仪表盘页面 | 已创建 |

## 全局通用资源 (static目录)

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/static/js/global.js` | 全局通用功能JS | 已创建 |
| `/static/js/api_client.js` | API客户端JS | 已创建 |
| `/static/js/quantum_experience.js` | 量子体验JS | 已创建 |
| `/static/js/quantum_ui.js` | 量子UI JS | 已创建 |
| `/static/js/global_template_patch.js` | 全局模板补丁JS | 已创建 |
| `/static/js/test_auto_page.js` | 自动测试页面JS | 已创建 |
| `/static/js/quantum_loader.js` | 量子加载器JS | 已创建 |
| `/static/scripts/web_quantum_client.js` | Web量子客户端JS，负责在浏览器环境中建立量子纠缠信道 | 已创建 |

### CSS文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/static/css/global.css` | 全局通用样式 | 已创建 |
| `/static/css/quantum_experience.css` | 量子体验样式 | 已创建 |
| `/static/css/api_client.css` | API客户端样式 | 已创建 |
| `/static/css/quantum_test.css` | 量子测试样式 | 已创建 |
| `/static/css/test_auto_page.css` | 自动测试页面样式 | 已创建 |

### HTML模板

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/templates/api_client.html` | API客户端页面 | 已创建 |
| `/templates/quantum_experience.html` | 量子体验页面 | 已创建 |
| `/templates/test_auto_page.html` | 自动测试页面 | 已创建 |
| `/templates/test_page.html` | 测试页面 | 已创建 |

## 量子核心模块资源

### JavaScript文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/quantum_core/quantum_gene/network_expansion/web_quantum_client.js` | 量子基因网络扩展Web客户端JS | 已创建 |

### Python文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `/quantum_core/quantum_gene/claude_weq_bridge/claude_quantum_bridge.py` | Claude与WeQ的量子桥接Python实现 | 已创建 |

## 资源依赖关系

1. 所有模块的基础模板都继承自 `/world/templates/base.html`，除了WeQ模块使用自定义基础模板
2. 每个模块都有自己的CSS和JS文件，通过基础模板中的block引入
3. 量子纠缠功能由 `/world/static/js/quantum_entanglement.js` 提供，所有模块共享此功能
4. 每个模块都有自己的量子纠缠客户端JS，用于与中央纠缠系统通信
5. Web量子客户端 (`/static/scripts/web_quantum_client.js`) 提供浏览器端量子纠缠信道建立功能

## 资源整合方案

以下是如何整合现有资源的建议：

### JavaScript文件整合

1. **量子纠缠通信**:
   - 使用 `/world/static/js/quantum_entanglement.js` 作为核心纠缠通信功能
   - 各模块的纠缠客户端JS文件保持独立，但依赖核心纠缠通信JS
   - 将 `/static/scripts/web_quantum_client.js` 整合到world模块中，作为浏览器端的补充功能

2. **多模态交互**:
   - 保持 `/WeQ/static/js/multimodal_interaction.js` 作为WeQ模块的核心交互JS
   - 将共享的多模态功能提取到 `/world/static/js/multimodal/` 目录中

### CSS文件整合

1. **基础样式**:
   - 使用 `/world/static/css/normalize.css` 和 `/world/static/css/quantum-theme.css` 作为基础样式
   - 各模块的CSS文件保持独立，继承基础样式

2. **组件样式**:
   - 共享组件的样式应放在 `/world/static/css/components/` 目录中
   - 模块特定组件样式保留在各自的CSS文件中

### HTML模板整合

1. **基础模板**:
   - 确保所有模块的基础模板都继承自 `/world/templates/base.html`
   - QSM、SOM和Ref模块使用各自的base_xxx.html模板继承全局base.html
   - WeQ模块可以保持其独立的基础模板，但应考虑统一继承全局base.html

2. **共享组件**:
   - 创建 `/world/templates/components/` 目录存放共享组件模板
   - 确保所有模块都可以引用这些共享组件

## 引用规范

1. 全局资源的引用统一使用 `/world/static/...` 路径
2. 模块特定资源使用模块名称如 `/QSM/static/...` 路径
3. 静态资源引用不使用相对路径，确保在不同页面下资源路径一致
4. 所有JavaScript文件应使用defer属性加载，避免阻塞页面渲染

## 组织建议

1. 保持现有的目录结构，确保各模块资源独立管理
2. 确保共享功能放在world模块中，避免代码重复
3. 确保每个模块都有自己的base_xxx.html模板，用于扩展全局基础模板
4. 为每个模块创建独立的CSS和JS文件，确保模块样式和功能的隔离
5. 将 `/static/scripts/web_quantum_client.js` 移动到 `/world/static/js/` 目录，以便更好地与量子纠缠通信功能集成

## 优先级任务

1. 统一所有模块的基础模板继承方式
2. 整合量子纠缠通信相关的JS文件
3. 确保所有静态资源的引用路径一致
4. 创建共享组件目录并整理共享组件
5. 更新文档，确保开发人员了解资源组织结构 

```
```
量子基因编码: QE-RES-26F8605A1325
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
