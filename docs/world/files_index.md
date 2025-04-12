# 量子叠加态模型(QSM)文件索引

## 概述
本文档提供QSM项目的重要文件索引，按目录组织，便于查找特定文件。本索引由Ref量子纠错子系统自动维护和优化。

## 文件索引

### api/
#### api/qsm_api/
- `api/qsm_api/__init__.py`  _包初始化文件_

#### api/ref_api/
- `api/ref_api/__init__.py`  _包初始化文件_

#### api/som_api/
- `api/som_api/__init__.py`  _包初始化文件_

#### api/weq_api/
- `api/weq_api/__init__.py`  _包初始化文件_

### docs/

#### docs/global/
- `docs/global/detailed_index.md`  _详细目录索引_
- `docs/global/files_index.md`  _文件索引_
- `docs/global/global_modules.md`  _全局模块概要_
- `docs/global/navigation_index.md`  _导航索引_
- `docs/global/qsm_project_index.md`  _项目总体索引_

#### docs/QSM/global/
- `docs/QSM/global/qsm_index.md`  _QSM主模型索引_

#### docs/QSM/user_guides/
- `docs/QSM/user_guides/quantum_network_connection_guide.md`  _量子网络连接指南_

#### docs/Ref/global/
- `docs/Ref/global/ref_index.md`  _Ref子系统索引_

#### docs/SOM/global/
- `docs/SOM/global/som_index.md`  _SOM子系统索引_

#### docs/WeQ/global/
- `docs/WeQ/global/weq_index.md`  _WeQ子系统索引_

### frontend/

#### frontend/tools/
- `frontend/tools/auto_template_watcher.py`  _模板自动监视_
- `frontend/tools/create_page.py`  _页面创建工具_
- `frontend/tools/install_auto_template.py`  _自动模板安装_
- `frontend/tools/start_template_watcher.py`  _启动模板监视_
- `frontend/tools/update_project_index.py`  _项目索引更新工具_

#### frontend/shared/
- `frontend/shared/base_template.html`  _基础模板_
- `frontend/shared/manage_frontend.py`  _前端管理脚本_

### global/

#### global/config/
- `global/config/paths_config.py`  _路径配置_

#### global/js/
- `global/js/quantum_entanglement_client.js`  _量子纠缠客户端_

#### global/static/css/
- `global/static/css/global.css`  _全局样式表_

#### global/static/js/
- `global/static/js/global.js`  _全局JavaScript函数_
- `global/static/js/quantum_entanglement.js`  _量子纠缠实现_
- `global/static/js/quantum_entanglement_client.js`  _量子纠缠客户端_
- `global/static/js/quantum_loader.js`  _量子加载器_

#### global/templates/
- `global/templates/base.html`  _全局基础模板_

#### global/tools/
- `global/tools/path_resolver.py`  _路径解析工具_

### models/
- `models/weq_model_28qubit_trained_simple.json`  _28量子比特模型_

### quantum_core/

#### quantum_core/quantum_blockchain/
- `quantum_core/quantum_blockchain/__init__.py`  _包初始化文件_
- `quantum_core/quantum_blockchain/qsm_knowledge.py`  _QSM知识库_
- `quantum_core/quantum_blockchain/qsm_main_chain.py`  _QSM主链_
- `quantum_core/quantum_blockchain/quantum_blockchain_core.py`  _量子区块链核心_

### QSM/
- `QSM/app.py`  _QSM应用入口点_
- `QSM/.cursorignore`  _编辑器忽略文件_

#### QSM/templates/
- `QSM/templates/api_client.html`  _API客户端界面_
- `QSM/templates/base_qsm.html`  _QSM基础模板_
- `QSM/templates/index.html`  _首页_
- `QSM/templates/quantum_experience.html`  _量子体验页面_
- `QSM/templates/quantum_test.html`  _量子测试页面_

#### QSM/templates/js/
- `QSM/templates/js/quantum_loader.js`  _量子加载器_

#### QSM/templates/shared/
- `QSM/templates/shared/head_includes.html`  _头部包含文件_

### Ref/
- `Ref/app.py`  _Ref应用入口点_
- `Ref/.cursorignore`  _编辑器忽略文件_

#### Ref/gene/test_output_entanglement/
- `Ref/gene/test_output_entanglement/demo.py`  _演示程序_
- `Ref/gene/test_output_entanglement/multimodal_entanglement.py`  _多模态纠缠_
- `Ref/gene/test_output_entanglement/simplified_core.py`  _简化核心_

#### Ref/global/js/
- `Ref/global/js/ref_entanglement_client.js`  _Ref量子纠缠客户端_

#### Ref/monitor/
- `Ref/monitor/index_monitor.py`  _索引监控脚本_

#### Ref/quantum_blockchain/
- `Ref/quantum_blockchain/__init__.py`  _包初始化文件_
- `Ref/quantum_blockchain/ref_blockchain.py`  _Ref区块链实现_

#### Ref/templates/
- `Ref/templates/base.html`  _基础模板_
- `Ref/templates/base_ref.html`  _Ref基础模板_

### SOM/
- `SOM/app.py`  _SOM应用入口点_
- `SOM/.cursorignore`  _编辑器忽略文件_
- `SOM/som_coin_system.py`  _SOM代币系统_

#### SOM/global/js/
- `SOM/global/js/som_entanglement_client.js`  _SOM量子纠缠客户端_

#### SOM/templates/
- `SOM/templates/base.html`  _基础模板_
- `SOM/templates/base_som.html`  _SOM基础模板_

### static/

#### static/css/
- `static/css/api_client.css`  _API客户端样式_
- `static/css/global.css`  _全局样式_
- `static/css/quantum_experience.css`  _量子体验样式_
- `static/css/quantum_test.css`  _量子测试样式_
- `static/css/test_auto_page.css`  _测试自动页面样式_

#### static/js/
- `static/js/api_client.js`  _API客户端脚本_
- `static/js/quantum_experience.js`  _量子体验脚本_

### WeQ/
- `WeQ/app.py`  _WeQ应用入口点_
- `WeQ/.cursorignore`  _编辑器忽略文件_

#### WeQ/global/js/
- `WeQ/global/js/weq_entanglement_client.js`  _WeQ量子纠缠客户端_
- `WeQ/global/js/weq_multimodal_interactions.js`  _WeQ多模态交互实现_

#### WeQ/knowledge/
- `WeQ/knowledge/background_training.py`  _背景知识训练_

#### WeQ/knowledge/models/
- `WeQ/knowledge/models/weq_model_28qubit_config.json`  _28量子比特模型配置_
- `WeQ/knowledge/models/weq_model_28qubit_trained_simple.json`  _28量子比特模型_

#### WeQ/knowledge/training_data/
- `WeQ/knowledge/training_data/quantum_blockchain_learning.py`  _区块链学习数据_

#### WeQ/quantum_blockchain/
- `WeQ/quantum_blockchain/__init__.py`  _包初始化文件_
- `WeQ/quantum_blockchain/weq_blockchain.py`  _WeQ区块链实现_

#### WeQ/static/js/
- `WeQ/static/js/weq_entanglement_client.js`  _WeQ量子纠缠客户端_
- `WeQ/static/js/weq_multimodal_interactions.js`  _多模态交互静态资源_

#### WeQ/templates/
- `WeQ/templates/base.html`  _基础模板_
- `WeQ/templates/base_weq.html`  _WeQ基础模板_
- `WeQ/templates/weq_multimodal_demo.html`  _WeQ多模态演示页面_

## 关键文件分类

### 应用入口点
- `QSM/app.py`  _QSM应用入口点_
- `SOM/app.py`  _SOM应用入口点_
- `WeQ/app.py`  _WeQ应用入口点_
- `Ref/app.py`  _Ref应用入口点_

### 量子区块链实现
- `quantum_core/quantum_blockchain/quantum_blockchain_core.py`  _量子区块链核心_
- `quantum_core/quantum_blockchain/qsm_main_chain.py`  _QSM主链_
- `Ref/quantum_blockchain/ref_blockchain.py`  _Ref区块链实现_
- `WeQ/quantum_blockchain/weq_blockchain.py`  _WeQ区块链实现_

### 量子纠缠实现
- `global/js/quantum_entanglement_client.js`  _全局量子纠缠客户端_
- `global/static/js/quantum_entanglement.js`  _量子纠缠实现_
- `SOM/global/js/som_entanglement_client.js`  _SOM量子纠缠客户端_
- `WeQ/global/js/weq_entanglement_client.js`  _WeQ量子纠缠客户端_
- `Ref/global/js/ref_entanglement_client.js`  _Ref量子纠缠客户端_

### 多模态实现
- `WeQ/global/js/weq_multimodal_interactions.js`  _WeQ多模态交互实现_
- `WeQ/templates/weq_multimodal_demo.html`  _WeQ多模态演示页面_
- `Ref/gene/test_output_entanglement/multimodal_entanglement.py`  _多模态纠缠_

### 基础模板
- `global/templates/base.html`  _全局基础模板_
- `QSM/templates/base_qsm.html`  _QSM基础模板_
- `SOM/templates/base_som.html`  _SOM基础模板_
- `WeQ/templates/base_weq.html`  _WeQ基础模板_
- `Ref/templates/base_ref.html`  _Ref基础模板_

### 自动化工具
- `frontend/tools/update_project_index.py`  _项目索引更新工具_
- `frontend/tools/create_page.py`  _页面创建工具_
- `frontend/tools/auto_template_watcher.py`  _模板自动监视_
- `Ref/monitor/index_monitor.py`  _索引监控脚本_

## 元数据
- **自动维护**: 此索引由Ref量子纠错子系统自动维护和更新
- **最后更新**: 2025-04-06
- **索引管理**: `Ref/monitor/index_monitor.py`
- **优化级别**: 2 (标准优化)
- **索引数量**: 包含80+核心文件 

## 概述
本文档提供QSM项目的重要文件索引，按目录组织，便于查找特定文件。本索引由Ref量子纠错子系统自动维护和优化。

## 文件索引

### api/
#### api/qsm_api/
- `api/qsm_api/__init__.py`  _包初始化文件_

#### api/ref_api/
- `api/ref_api/__init__.py`  _包初始化文件_

#### api/som_api/
- `api/som_api/__init__.py`  _包初始化文件_

#### api/weq_api/
- `api/weq_api/__init__.py`  _包初始化文件_

### docs/

#### docs/global/
- `docs/global/detailed_index.md`  _详细目录索引_
- `docs/global/files_index.md`  _文件索引_
- `docs/global/global_modules.md`  _全局模块概要_
- `docs/global/navigation_index.md`  _导航索引_
- `docs/global/qsm_project_index.md`  _项目总体索引_

#### docs/QSM/global/
- `docs/QSM/global/qsm_index.md`  _QSM主模型索引_

#### docs/QSM/user_guides/
- `docs/QSM/user_guides/quantum_network_connection_guide.md`  _量子网络连接指南_

#### docs/Ref/global/
- `docs/Ref/global/ref_index.md`  _Ref子系统索引_

#### docs/SOM/global/
- `docs/SOM/global/som_index.md`  _SOM子系统索引_

#### docs/WeQ/global/
- `docs/WeQ/global/weq_index.md`  _WeQ子系统索引_

### frontend/

#### frontend/tools/
- `frontend/tools/auto_template_watcher.py`  _模板自动监视_
- `frontend/tools/create_page.py`  _页面创建工具_
- `frontend/tools/install_auto_template.py`  _自动模板安装_
- `frontend/tools/start_template_watcher.py`  _启动模板监视_
- `frontend/tools/update_project_index.py`  _项目索引更新工具_

#### frontend/shared/
- `frontend/shared/base_template.html`  _基础模板_
- `frontend/shared/manage_frontend.py`  _前端管理脚本_

### global/

#### global/config/
- `global/config/paths_config.py`  _路径配置_

#### global/js/
- `global/js/quantum_entanglement_client.js`  _量子纠缠客户端_

#### global/static/css/
- `global/static/css/global.css`  _全局样式表_

#### global/static/js/
- `global/static/js/global.js`  _全局JavaScript函数_
- `global/static/js/quantum_entanglement.js`  _量子纠缠实现_
- `global/static/js/quantum_entanglement_client.js`  _量子纠缠客户端_
- `global/static/js/quantum_loader.js`  _量子加载器_

#### global/templates/
- `global/templates/base.html`  _全局基础模板_

#### global/tools/
- `global/tools/path_resolver.py`  _路径解析工具_

### models/
- `models/weq_model_28qubit_trained_simple.json`  _28量子比特模型_

### quantum_core/

#### quantum_core/quantum_blockchain/
- `quantum_core/quantum_blockchain/__init__.py`  _包初始化文件_
- `quantum_core/quantum_blockchain/qsm_knowledge.py`  _QSM知识库_
- `quantum_core/quantum_blockchain/qsm_main_chain.py`  _QSM主链_
- `quantum_core/quantum_blockchain/quantum_blockchain_core.py`  _量子区块链核心_

### QSM/
- `QSM/app.py`  _QSM应用入口点_
- `QSM/.cursorignore`  _编辑器忽略文件_

#### QSM/templates/
- `QSM/templates/api_client.html`  _API客户端界面_
- `QSM/templates/base_qsm.html`  _QSM基础模板_
- `QSM/templates/index.html`  _首页_
- `QSM/templates/quantum_experience.html`  _量子体验页面_
- `QSM/templates/quantum_test.html`  _量子测试页面_

#### QSM/templates/js/
- `QSM/templates/js/quantum_loader.js`  _量子加载器_

#### QSM/templates/shared/
- `QSM/templates/shared/head_includes.html`  _头部包含文件_

### Ref/
- `Ref/app.py`  _Ref应用入口点_
- `Ref/.cursorignore`  _编辑器忽略文件_

#### Ref/gene/test_output_entanglement/
- `Ref/gene/test_output_entanglement/demo.py`  _演示程序_
- `Ref/gene/test_output_entanglement/multimodal_entanglement.py`  _多模态纠缠_
- `Ref/gene/test_output_entanglement/simplified_core.py`  _简化核心_

#### Ref/global/js/
- `Ref/global/js/ref_entanglement_client.js`  _Ref量子纠缠客户端_

#### Ref/monitor/
- `Ref/monitor/index_monitor.py`  _索引监控脚本_

#### Ref/quantum_blockchain/
- `Ref/quantum_blockchain/__init__.py`  _包初始化文件_
- `Ref/quantum_blockchain/ref_blockchain.py`  _Ref区块链实现_

#### Ref/templates/
- `Ref/templates/base.html`  _基础模板_
- `Ref/templates/base_ref.html`  _Ref基础模板_

### SOM/
- `SOM/app.py`  _SOM应用入口点_
- `SOM/.cursorignore`  _编辑器忽略文件_
- `SOM/som_coin_system.py`  _SOM代币系统_

#### SOM/global/js/
- `SOM/global/js/som_entanglement_client.js`  _SOM量子纠缠客户端_

#### SOM/templates/
- `SOM/templates/base.html`  _基础模板_
- `SOM/templates/base_som.html`  _SOM基础模板_

### static/

#### static/css/
- `static/css/api_client.css`  _API客户端样式_
- `static/css/global.css`  _全局样式_
- `static/css/quantum_experience.css`  _量子体验样式_
- `static/css/quantum_test.css`  _量子测试样式_
- `static/css/test_auto_page.css`  _测试自动页面样式_

#### static/js/
- `static/js/api_client.js`  _API客户端脚本_
- `static/js/quantum_experience.js`  _量子体验脚本_

### WeQ/
- `WeQ/app.py`  _WeQ应用入口点_
- `WeQ/.cursorignore`  _编辑器忽略文件_

#### WeQ/global/js/
- `WeQ/global/js/weq_entanglement_client.js`  _WeQ量子纠缠客户端_
- `WeQ/global/js/weq_multimodal_interactions.js`  _WeQ多模态交互实现_

#### WeQ/knowledge/
- `WeQ/knowledge/background_training.py`  _背景知识训练_

#### WeQ/knowledge/models/
- `WeQ/knowledge/models/weq_model_28qubit_config.json`  _28量子比特模型配置_
- `WeQ/knowledge/models/weq_model_28qubit_trained_simple.json`  _28量子比特模型_

#### WeQ/knowledge/training_data/
- `WeQ/knowledge/training_data/quantum_blockchain_learning.py`  _区块链学习数据_

#### WeQ/quantum_blockchain/
- `WeQ/quantum_blockchain/__init__.py`  _包初始化文件_
- `WeQ/quantum_blockchain/weq_blockchain.py`  _WeQ区块链实现_

#### WeQ/static/js/
- `WeQ/static/js/weq_entanglement_client.js`  _WeQ量子纠缠客户端_
- `WeQ/static/js/weq_multimodal_interactions.js`  _多模态交互静态资源_

#### WeQ/templates/
- `WeQ/templates/base.html`  _基础模板_
- `WeQ/templates/base_weq.html`  _WeQ基础模板_
- `WeQ/templates/weq_multimodal_demo.html`  _WeQ多模态演示页面_

## 关键文件分类

### 应用入口点
- `QSM/app.py`  _QSM应用入口点_
- `SOM/app.py`  _SOM应用入口点_
- `WeQ/app.py`  _WeQ应用入口点_
- `Ref/app.py`  _Ref应用入口点_

### 量子区块链实现
- `quantum_core/quantum_blockchain/quantum_blockchain_core.py`  _量子区块链核心_
- `quantum_core/quantum_blockchain/qsm_main_chain.py`  _QSM主链_
- `Ref/quantum_blockchain/ref_blockchain.py`  _Ref区块链实现_
- `WeQ/quantum_blockchain/weq_blockchain.py`  _WeQ区块链实现_

### 量子纠缠实现
- `global/js/quantum_entanglement_client.js`  _全局量子纠缠客户端_
- `global/static/js/quantum_entanglement.js`  _量子纠缠实现_
- `SOM/global/js/som_entanglement_client.js`  _SOM量子纠缠客户端_
- `WeQ/global/js/weq_entanglement_client.js`  _WeQ量子纠缠客户端_
- `Ref/global/js/ref_entanglement_client.js`  _Ref量子纠缠客户端_

### 多模态实现
- `WeQ/global/js/weq_multimodal_interactions.js`  _WeQ多模态交互实现_
- `WeQ/templates/weq_multimodal_demo.html`  _WeQ多模态演示页面_
- `Ref/gene/test_output_entanglement/multimodal_entanglement.py`  _多模态纠缠_

### 基础模板
- `global/templates/base.html`  _全局基础模板_
- `QSM/templates/base_qsm.html`  _QSM基础模板_
- `SOM/templates/base_som.html`  _SOM基础模板_
- `WeQ/templates/base_weq.html`  _WeQ基础模板_
- `Ref/templates/base_ref.html`  _Ref基础模板_

### 自动化工具
- `frontend/tools/update_project_index.py`  _项目索引更新工具_
- `frontend/tools/create_page.py`  _页面创建工具_
- `frontend/tools/auto_template_watcher.py`  _模板自动监视_
- `Ref/monitor/index_monitor.py`  _索引监控脚本_

## 元数据
- **自动维护**: 此索引由Ref量子纠错子系统自动维护和更新
- **最后更新**: 2025-04-06
- **索引管理**: `Ref/monitor/index_monitor.py`
- **优化级别**: 2 (标准优化)
- **索引数量**: 包含80+核心文件 

```
```
量子基因编码: QE-FIL-A1E69C2B3308
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
