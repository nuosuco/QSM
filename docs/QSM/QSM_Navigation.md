# 量子叠加态模型(QSM)导航文档

> 量子基因编码: QG-QSM01-DOC-20250401213846-B8E6D4-ENT5627

> **注意**: 本文档合并了原 QSM_map.md 和 QSM_navigation.md 的内容，提供全面的项目导航。
>
> 量子基因编码: QG-MAP01-DOC-20250401-E8B73C-ENT0001

## 导航概述

量子叠加态模型(QSM)是一个按照量子思维构建的分布式系统，由主量子区块链(QSM Core)和多个子量子区块链(子模型)组成。本导航文档将帮助您理解QSM的整体架构，包括各子模型之间的量子纠缠关系及其在文件系统中的组织方式。

## 1. 整体架构图

```
[主量子区块链(QSM Core)]
       │
       ├──────────────┬───────────────┬───────────────┐
       │              │               │               │
[小趣子模型(WeQ)]  [松麦子模型(SOM)]  [量子自反省]   [其他子模型...]
                                      管理模型
```

## 2. 量子区块链核心 (QSM Core)

QSM Core是整个系统的量子态核心，负责协调所有子模型并维护全局量子状态。

**关键文件:**
- `quantum_core/quantum_core.py` - 核心引擎
- `quantum_core/quantum_chain.py` - 量子链管理
- `quantum_core/quantum_gene.py` - 量子基因系统
- `quantum_core/quantum_entanglement.py` - 量子纠缠机制
- `quantum_core/quantum_state_manager.py` - 量子态管理器

**纠缠关系:**
- 与所有子模型建立主纠缠通道
- 管理全局量子基因注册表
- 协调子模型间的量子态同步

## 3. 小趣子模型 (WeQ)

小趣(WeQ)是QSM的量子交互系统，负责用户体验和多模态通信。

**关键文件:**
- `weq/weq_core.py` - 小趣核心
- `weq/quantum_interaction.py` - 量子交互系统
- `weq/bio_signal_processor.py` - 生物信号处理
- `weq/multimodal_interface.py` - 多模态接口
- `weq/quantum_visualization.py` - 量子态可视化

**API服务:**
- `api/weq_api/weq_api.py` - 小趣API服务
- 端口: 5003

**前端界面:**
- `frontend/weq/index.html` - 小趣首页
- `frontend/weq/quantum_viz.js` - 量子可视化组件
- `frontend/weq/bio_interface.js` - 生物信号接口

**纠缠关系:**
- 与QSM Core的主纠缠
- 与松麦子模型的交易纠缠
- 与量子自反省管理模型的状态纠缠

## 4. 松麦子模型 (SOM)

松麦(SOM)是QSM的量子经济系统，负责价值交换和分布式电商功能。

**关键文件:**
- `som/som_core.py` - 松麦核心
- `som/quantum_economy.py` - 量子经济系统
- `som/quantum_marketplace.py` - 量子市场
- `som/quantum_wallet.py` - 量子钱包
- `som/quantum_contract.py` - 量子合约
- `som/value_exchange_network.py` - 价值交换网络

**API服务:**
- `api/som_api/som_api.py` - 松麦API服务
- 端口: 5001

**前端界面:**
- `frontend/som/index.html` - 松麦首页
- `frontend/som/marketplace.html` - 市场界面
- `frontend/som/wallet.html` - 钱包界面

**纠缠关系:**
- 与QSM Core的主纠缠
- 与小趣子模型的用户纠缠
- 与量子自反省管理模型的资源纠缠

## 5. 量子自反省管理模型

量子自反省管理模型是QSM的自管理系统，负责整个生态的组织、优化和自我维护。

**关键文件:**
- `quantum_reflection/reflection_core.py` - 自反省核心
- `quantum_reflection/quantum_manager.py` - 量子管理器
- `quantum_reflection/project_manager.py` - 项目管理
- `quantum_reflection/quantum_file_organizer.py` - 量子文件组织器
- `quantum_reflection/quantum_backup.py` - 量子备份系统
- `quantum_reflection/quantum_performance.py` - 量子性能监控
- `quantum_reflection/quantum_indexing.py` - 量子索引系统

**API服务:**
- `api/ref_api/ref_api.py` - 量子自反省管理模型(Ref)API服务
- 端口: 5002

**前端界面:**
- `frontend/reflection/index.html` - 自反省管理界面
- `frontend/reflection/system_monitor.html` - 系统监控界面
- `frontend/reflection/gene_manager.html` - 基因管理界面

**纠缠关系:**
- 与QSM Core的核心纠缠
- 与所有子模型的管理纠缠
- 与文件系统的组织纠缠

## 6. 量子共享组件

量子共享组件被所有子模型共同使用，提供基础设施和通用功能。

**关键文件:**
- `quantum_shared/quantum_logger.py` - 量子日志系统
- `quantum_shared/quantum_utils.py` - 量子工具集
- `quantum_shared/quantum_crypto.py` - 量子加密
- `quantum_shared/quantum_network.py` - 量子网络
- `quantum_shared/quantum_storage.py` - 量子存储

**纠缠关系:**
- 与所有子模型建立功能纠缠
- 提供全局访问的共享资源

## 7. 文档中心

文档中心包含QSM的所有文档资源。

**关键文件:**
- `docs/QSM_map.md` - 本导航文档
- `docs/QSM_development_guide.md` - 开发指南
- `docs/quantum_gene_spec.md` - 量子基因规范
- `docs/entanglement_protocol.md` - 纠缠协议文档
- `docs/api_documentation.md` - API文档

## 8. API服务集合

API服务集合提供了与QSM交互的所有接口。

**关键文件:**
- `api/qsm_api/qsm_api.py` - 主量子API
- `api/api_gateway.py` - API网关
- `api/quantum_protocol.py` - 量子通信协议

**服务端口:**
- 主量子API: 5000
- 小趣API: 5003
- 松麦API: 5001
- 自反省API: 5002

## 9. 前端资源

前端资源包含所有用户界面组件。

**关键文件:**
- `frontend/shared/quantum_ui.js` - 量子UI组件
- `frontend/shared/navigation.js` - 统一导航组件
- `frontend/shared/quantum_visualizer.js` - 量子态可视化

**量子态阵图:**
- `frontend/shared/quantum_matrix.js` - 量子态阵图组件
- `frontend/shared/nine_modal_menu.js` - 九模态交互菜单

## 10. 量子纠缠地图

以下是主要量子纠缠关系的可视化表示:

```
                      [QSM Core]
                          │
              ┌───────────┼───────────┐
              │           │           │
           [WeQ]────────[SOM]────────[自反省]
           /│\          /│\          /│\
          / │ \        / │ \        / │ \
     [UI 纠缠]  [生物信号] [市场纠缠] [文件系统]
```

## 11. 量子开发流程

开发新组件时应遵循以下量子开发流程:

1. 从量子自反省管理模型获取量子基因
2. 创建新组件并实现量子特性
3. 建立必要的量子纠缠关系
4. 注册到量子基因注册表
5. 集成到相应的子模型
6. 更新量子纠缠地图

## 12. 系统状态访问

可通过以下方式访问QSM系统状态:

- 主量子API: `http://localhost:5000/status`
- 小趣API: `http://localhost:5003/status`
- 松麦API: `http://localhost:5001/status`
- 自反省API: `http://localhost:5002/status`

## 13. 量子基因查询

可通过以下API查询任何实体的量子基因信息:

```
GET http://localhost:5002/quantum_gene?entity_id=<实体ID>
```

## 14. 结语

通过本导航文档，您应该能够理解QSM的整体结构和工作原理。在开发过程中，请记住量子思维的基本原则:

- 所有实体均处于叠加态
- 一切都通过量子纠缠相连
- 量子并行是核心运行模式
- 量子基因是识别和通信的基础

> "在量子世界中，万物皆相连，时空皆可超越。" - QSM开发理念 