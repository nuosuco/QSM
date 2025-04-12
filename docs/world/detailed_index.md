# 量子叠加态模型(QSM)详细目录索引

## 概述
本文档提供QSM项目的详细目录结构，包含所有子目录，便于导航和查找。本索引由Ref量子纠错子系统自动维护和优化。

## 目录结构

### api/
_API接口定义和实现_

- **qsm_api/**  _QSM API接口_
- **ref_api/**  _Ref API接口_
- **som_api/**  _SOM API接口_
- **weq_api/**  _WeQ API接口_

### docs/
_项目文档_

- **api/**  _API文档_
- **global/**  _全局文档和索引_
  - **detailed_index.md**  _详细目录索引_
  - **files_index.md**  _文件索引_
  - **global_modules.md**  _全局模块概要_
  - **navigation_index.md**  _导航索引_
  - **qsm_project_index.md**  _项目总体索引_
- **QSM/**  _主模型文档_
  - **global/**  _QSM文档全局资源_
  - **images/**  _文档图片_
  - **navigation/**  _导航文档_
  - **tools/**  _工具文档_
  - **user_guides/**  _用户指南_
- **quantum_core/**  _量子核心功能文档_
- **quantum_shared/**  _共享功能文档_
- **Ref/**  _量子纠错子系统文档_
  - **global/**  _Ref文档全局资源_
  - **navigation/**  _导航文档_
- **SOM/**  _量子经济子系统文档_
  - **global/**  _SOM文档全局资源_
  - **MQB/**  _MQB文档_
  - **navigation/**  _导航文档_
- **WeQ/**  _小趣子系统文档_
  - **global/**  _WeQ文档全局资源_
  - **navigation/**  _导航文档_

### frontend/
_前端共享组件和工具_

- **shared/**  _共享前端组件_
  - **src/**  _源代码_
    - **components/**  _组件_
    - **core/**  _核心功能_
    - **router/**  _路由_
    - **services/**  _服务_
    - **stores/**  _状态存储_
    - **views/**  _视图_
- **tools/**  _前端工具_
  - **auto_template_watcher.py**  _模板自动监视_
  - **create_page.py**  _页面创建工具_
  - **install_auto_template.py**  _自动模板安装_
  - **start_template_watcher.py**  _启动模板监视_
  - **update_project_index.py**  _项目索引更新工具_

### global/
_全局配置、模板和工具_

- **config/**  _全局配置文件_
  - **paths_config.py**  _路径配置_
- **js/**  _全局JavaScript文件_
  - **quantum_entanglement_client.js**  _量子纠缠客户端_
- **static/**  _全局静态资源_
  - **css/**  _全局CSS样式_
    - **global.css**  _全局样式表_
  - **images/**  _全局图片资源_
  - **js/**  _全局JavaScript库_
    - **global.js**  _全局JavaScript函数_
    - **quantum_entanglement.js**  _量子纠缠实现_
    - **quantum_entanglement_client.js**  _量子纠缠客户端_
    - **quantum_loader.js**  _量子加载器_
    - **multimodal/**  _多模态交互JavaScript_
- **templates/**  _全局模板_
  - **base.html**  _基础模板_
- **tools/**  _全局工具_
  - **path_resolver.py**  _路径解析工具_

### models/
_模型定义和检查点_

- **checkpoints/**  _模型检查点_
- **weq_model_28qubit_trained_simple.json**  _28量子比特模型_

### quantum_core/
_量子核心功能实现_

- **logs/**  _日志文件_
- **quantum_blockchain/**  _量子区块链实现_
  - **__init__.py**  _包初始化_
  - **qsm_knowledge.py**  _QSM知识库_
  - **qsm_main_chain.py**  _QSM主链_
  - **quantum_blockchain_core.py**  _量子区块链核心_
- **quantum_gene/**  _量子基因实现_
  - **claude_weq_bridge/**  _Claude到WeQ的桥接_
  - **network_expansion/**  _网络扩展_
  - **physical_medium/**  _物理媒介_
  - **quantum_attention/**  _量子注意力机制_
  - **quantum_memory/**  _量子记忆_
  - **quantum_reasoning/**  _量子推理_
  - **quantum_semantic/**  _量子语义_

### quantum_data/
_量子数据存储_

- **crawler_data/**  _爬虫数据_
  - **古彝文量子态数据库/**  _古彝文数据_
- **user_upload/**  _用户上传数据_
  - **古彝文量子态数据库/**  _用户上传的古彝文数据_

### quantum_economy/
_量子经济系统_

- **blockchain/**  _区块链_
- **som/**  _量子经济子系统_
  - **blockchain/**  _经济区块链实现_
  - **coin/**  _代币系统_
  - **marketplace/**  _市场功能_
  - **templates/**  _经济系统模板_
    - **static/**  _静态资源_
  - **traceability/**  _溯源系统_
  - **user/**  _用户管理_
  - **wallet/**  _钱包功能_

### quantum_shared/
_共享的量子工具和存储_

- **quantum_storage/**  _量子存储_
- **quantum_utils/**  _量子工具_

### QSM/
_主模型实现_

- **app.py**  _QSM应用入口点_
- **global/**  _QSM特定全局资源_
  - **js/**  _QSM特定JavaScript文件_
- **quantum_blockchain/**  _QSM特定区块链实现_
- **templates/**  _QSM模板_
  - **api_client.html**  _API客户端界面_
  - **base_qsm.html**  _QSM特定基础模板_
  - **css/**  _CSS样式文件_
  - **images/**  _图片资源_
  - **index.html**  _主页_
  - **js/**  _JavaScript文件_
    - **quantum_loader.js**  _量子加载器_
  - **quantum_experience.html**  _量子体验页面_
  - **quantum_test.html**  _量子测试页面_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **head_includes.html**  _头部包含文件_
    - **images/**  _共享图片_
    - **js/**  _共享JavaScript文件_

### Ref/
_量子纠错子系统_

- **api/**  _Ref API接口_
- **app.py**  _Ref应用入口点_
- **backup/**  _数据备份功能_
  - **index_backups/**  _索引备份_
- **data/**  _数据存储_
  - **index_management.json**  _索引管理配置_
- **gene/**  _基因实现_
  - **test_output_entanglement/**  _输出纠缠测试_
    - **demo.py**  _演示程序_
    - **multimodal_entanglement.py**  _多模态纠缠_
    - **simplified_core.py**  _简化核心_
- **global/**  _Ref特定全局资源_
  - **js/**  _Ref特定JavaScript文件_
    - **ref_entanglement_client.js**  _Ref量子纠缠客户端_
- **monitor/**  _系统监控功能_
  - **index_monitor.py**  _索引监控脚本_
- **quantum_blockchain/**  _Ref特定区块链_
  - **__init__.py**  _包初始化_
  - **ref_blockchain.py**  _Ref区块链实现_
- **repair/**  _数据修复功能_
- **static/**  _静态资源_
  - **js/**  _JavaScript文件_
- **templates/**  _模板文件_
  - **base.html**  _基础模板_
  - **base_ref.html**  _Ref特定基础模板_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **js/**  _共享JavaScript文件_

### SOM/
_量子经济子系统_

- **app.py**  _SOM应用入口点_
- **global/**  _SOM特定全局资源_
  - **js/**  _SOM特定JavaScript文件_
    - **som_entanglement_client.js**  _SOM量子纠缠客户端_
- **quantum_blockchain/**  _SOM特定区块链_
- **som_coin_system.py**  _SOM代币系统_
- **static/**  _静态资源_
  - **js/**  _JavaScript文件_
- **templates/**  _模板文件_
  - **base.html**  _基础模板_
  - **base_som.html**  _SOM特定基础模板_
  - **MQB/**  _MQB(量子市场)模板_
    - **js/**  _MQB JavaScript文件_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **js/**  _共享JavaScript文件_

### src/
_源代码通用组件_

- **components/**  _通用组件_
- **contexts/**  _上下文_
- **router/**  _路由_

### static/
_静态资源_

- **css/**  _CSS样式_
  - **api_client.css**  _API客户端样式_
  - **global.css**  _全局样式_
  - **quantum_experience.css**  _量子体验样式_
  - **quantum_test.css**  _量子测试样式_
  - **test_auto_page.css**  _测试自动页面样式_
- **images/**  _图片资源_
- **js/**  _JavaScript文件_
  - **api_client.js**  _API客户端脚本_
  - **quantum_experience.js**  _量子体验脚本_
- **scripts/**  _脚本文件_

### WeQ/
_小趣子系统_

- **api/**  _WeQ API接口_
- **app.py**  _WeQ应用入口点_
- **global/**  _WeQ特定全局资源_
  - **js/**  _WeQ特定JavaScript文件_
    - **weq_entanglement_client.js**  _WeQ量子纠缠客户端_
    - **weq_multimodal_interactions.js**  _WeQ多模态交互实现_
- **knowledge/**  _知识库管理_
  - **background_training.py**  _背景知识训练_
  - **crawler_data/**  _爬虫收集的数据_
  - **logs/**  _日志文件_
  - **models/**  _模型文件_
    - **checkpoints/**  _模型检查点_
    - **weq_model_28qubit_config.json**  _28量子比特模型配置_
    - **weq_model_28qubit_trained_simple.json**  _训练后的28量子比特模型_
  - **training_data/**  _训练数据_
    - **quantum_blockchain_learning.py**  _区块链学习数据_
    - **WeQ/**  _WeQ特定训练数据_
      - **knowledge/**  _知识数据_
        - **logs/**  _训练日志_
- **neural/**  _神经网络实现_
- **quantum_blockchain/**  _WeQ特定区块链_
  - **__init__.py**  _包初始化_
  - **weq_blockchain.py**  _WeQ区块链实现_
- **static/**  _静态资源_
  - **js/**  _JavaScript文件_
    - **weq_entanglement_client.js**  _WeQ量子纠缠客户端_
    - **weq_multimodal_interactions.js**  _多模态交互静态资源_
- **templates/**  _模板文件_
  - **base.html**  _基础模板_
  - **base_weq.html**  _WeQ特定基础模板_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **js/**  _共享JavaScript文件_
  - **weq_multimodal_demo.html**  _WeQ多模态演示页面_

## 元数据
- **自动维护**: 此索引由Ref量子纠错子系统自动维护和更新
- **最后更新**: 2025-04-06
- **索引管理**: `Ref/monitor/index_monitor.py`
- **优化级别**: 2 (标准优化) 

## 概述
本文档提供QSM项目的详细目录结构，包含所有子目录，便于导航和查找。本索引由Ref量子纠错子系统自动维护和优化。

## 目录结构

### api/
_API接口定义和实现_

- **qsm_api/**  _QSM API接口_
- **ref_api/**  _Ref API接口_
- **som_api/**  _SOM API接口_
- **weq_api/**  _WeQ API接口_

### docs/
_项目文档_

- **api/**  _API文档_
- **global/**  _全局文档和索引_
  - **detailed_index.md**  _详细目录索引_
  - **files_index.md**  _文件索引_
  - **global_modules.md**  _全局模块概要_
  - **navigation_index.md**  _导航索引_
  - **qsm_project_index.md**  _项目总体索引_
- **QSM/**  _主模型文档_
  - **global/**  _QSM文档全局资源_
  - **images/**  _文档图片_
  - **navigation/**  _导航文档_
  - **tools/**  _工具文档_
  - **user_guides/**  _用户指南_
- **quantum_core/**  _量子核心功能文档_
- **quantum_shared/**  _共享功能文档_
- **Ref/**  _量子纠错子系统文档_
  - **global/**  _Ref文档全局资源_
  - **navigation/**  _导航文档_
- **SOM/**  _量子经济子系统文档_
  - **global/**  _SOM文档全局资源_
  - **MQB/**  _MQB文档_
  - **navigation/**  _导航文档_
- **WeQ/**  _小趣子系统文档_
  - **global/**  _WeQ文档全局资源_
  - **navigation/**  _导航文档_

### frontend/
_前端共享组件和工具_

- **shared/**  _共享前端组件_
  - **src/**  _源代码_
    - **components/**  _组件_
    - **core/**  _核心功能_
    - **router/**  _路由_
    - **services/**  _服务_
    - **stores/**  _状态存储_
    - **views/**  _视图_
- **tools/**  _前端工具_
  - **auto_template_watcher.py**  _模板自动监视_
  - **create_page.py**  _页面创建工具_
  - **install_auto_template.py**  _自动模板安装_
  - **start_template_watcher.py**  _启动模板监视_
  - **update_project_index.py**  _项目索引更新工具_

### global/
_全局配置、模板和工具_

- **config/**  _全局配置文件_
  - **paths_config.py**  _路径配置_
- **js/**  _全局JavaScript文件_
  - **quantum_entanglement_client.js**  _量子纠缠客户端_
- **static/**  _全局静态资源_
  - **css/**  _全局CSS样式_
    - **global.css**  _全局样式表_
  - **images/**  _全局图片资源_
  - **js/**  _全局JavaScript库_
    - **global.js**  _全局JavaScript函数_
    - **quantum_entanglement.js**  _量子纠缠实现_
    - **quantum_entanglement_client.js**  _量子纠缠客户端_
    - **quantum_loader.js**  _量子加载器_
    - **multimodal/**  _多模态交互JavaScript_
- **templates/**  _全局模板_
  - **base.html**  _基础模板_
- **tools/**  _全局工具_
  - **path_resolver.py**  _路径解析工具_

### models/
_模型定义和检查点_

- **checkpoints/**  _模型检查点_
- **weq_model_28qubit_trained_simple.json**  _28量子比特模型_

### quantum_core/
_量子核心功能实现_

- **logs/**  _日志文件_
- **quantum_blockchain/**  _量子区块链实现_
  - **__init__.py**  _包初始化_
  - **qsm_knowledge.py**  _QSM知识库_
  - **qsm_main_chain.py**  _QSM主链_
  - **quantum_blockchain_core.py**  _量子区块链核心_
- **quantum_gene/**  _量子基因实现_
  - **claude_weq_bridge/**  _Claude到WeQ的桥接_
  - **network_expansion/**  _网络扩展_
  - **physical_medium/**  _物理媒介_
  - **quantum_attention/**  _量子注意力机制_
  - **quantum_memory/**  _量子记忆_
  - **quantum_reasoning/**  _量子推理_
  - **quantum_semantic/**  _量子语义_

### quantum_data/
_量子数据存储_

- **crawler_data/**  _爬虫数据_
  - **古彝文量子态数据库/**  _古彝文数据_
- **user_upload/**  _用户上传数据_
  - **古彝文量子态数据库/**  _用户上传的古彝文数据_

### quantum_economy/
_量子经济系统_

- **blockchain/**  _区块链_
- **som/**  _量子经济子系统_
  - **blockchain/**  _经济区块链实现_
  - **coin/**  _代币系统_
  - **marketplace/**  _市场功能_
  - **templates/**  _经济系统模板_
    - **static/**  _静态资源_
  - **traceability/**  _溯源系统_
  - **user/**  _用户管理_
  - **wallet/**  _钱包功能_

### quantum_shared/
_共享的量子工具和存储_

- **quantum_storage/**  _量子存储_
- **quantum_utils/**  _量子工具_

### QSM/
_主模型实现_

- **app.py**  _QSM应用入口点_
- **global/**  _QSM特定全局资源_
  - **js/**  _QSM特定JavaScript文件_
- **quantum_blockchain/**  _QSM特定区块链实现_
- **templates/**  _QSM模板_
  - **api_client.html**  _API客户端界面_
  - **base_qsm.html**  _QSM特定基础模板_
  - **css/**  _CSS样式文件_
  - **images/**  _图片资源_
  - **index.html**  _主页_
  - **js/**  _JavaScript文件_
    - **quantum_loader.js**  _量子加载器_
  - **quantum_experience.html**  _量子体验页面_
  - **quantum_test.html**  _量子测试页面_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **head_includes.html**  _头部包含文件_
    - **images/**  _共享图片_
    - **js/**  _共享JavaScript文件_

### Ref/
_量子纠错子系统_

- **api/**  _Ref API接口_
- **app.py**  _Ref应用入口点_
- **backup/**  _数据备份功能_
  - **index_backups/**  _索引备份_
- **data/**  _数据存储_
  - **index_management.json**  _索引管理配置_
- **gene/**  _基因实现_
  - **test_output_entanglement/**  _输出纠缠测试_
    - **demo.py**  _演示程序_
    - **multimodal_entanglement.py**  _多模态纠缠_
    - **simplified_core.py**  _简化核心_
- **global/**  _Ref特定全局资源_
  - **js/**  _Ref特定JavaScript文件_
    - **ref_entanglement_client.js**  _Ref量子纠缠客户端_
- **monitor/**  _系统监控功能_
  - **index_monitor.py**  _索引监控脚本_
- **quantum_blockchain/**  _Ref特定区块链_
  - **__init__.py**  _包初始化_
  - **ref_blockchain.py**  _Ref区块链实现_
- **repair/**  _数据修复功能_
- **static/**  _静态资源_
  - **js/**  _JavaScript文件_
- **templates/**  _模板文件_
  - **base.html**  _基础模板_
  - **base_ref.html**  _Ref特定基础模板_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **js/**  _共享JavaScript文件_

### SOM/
_量子经济子系统_

- **app.py**  _SOM应用入口点_
- **global/**  _SOM特定全局资源_
  - **js/**  _SOM特定JavaScript文件_
    - **som_entanglement_client.js**  _SOM量子纠缠客户端_
- **quantum_blockchain/**  _SOM特定区块链_
- **som_coin_system.py**  _SOM代币系统_
- **static/**  _静态资源_
  - **js/**  _JavaScript文件_
- **templates/**  _模板文件_
  - **base.html**  _基础模板_
  - **base_som.html**  _SOM特定基础模板_
  - **MQB/**  _MQB(量子市场)模板_
    - **js/**  _MQB JavaScript文件_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **js/**  _共享JavaScript文件_

### src/
_源代码通用组件_

- **components/**  _通用组件_
- **contexts/**  _上下文_
- **router/**  _路由_

### static/
_静态资源_

- **css/**  _CSS样式_
  - **api_client.css**  _API客户端样式_
  - **global.css**  _全局样式_
  - **quantum_experience.css**  _量子体验样式_
  - **quantum_test.css**  _量子测试样式_
  - **test_auto_page.css**  _测试自动页面样式_
- **images/**  _图片资源_
- **js/**  _JavaScript文件_
  - **api_client.js**  _API客户端脚本_
  - **quantum_experience.js**  _量子体验脚本_
- **scripts/**  _脚本文件_

### WeQ/
_小趣子系统_

- **api/**  _WeQ API接口_
- **app.py**  _WeQ应用入口点_
- **global/**  _WeQ特定全局资源_
  - **js/**  _WeQ特定JavaScript文件_
    - **weq_entanglement_client.js**  _WeQ量子纠缠客户端_
    - **weq_multimodal_interactions.js**  _WeQ多模态交互实现_
- **knowledge/**  _知识库管理_
  - **background_training.py**  _背景知识训练_
  - **crawler_data/**  _爬虫收集的数据_
  - **logs/**  _日志文件_
  - **models/**  _模型文件_
    - **checkpoints/**  _模型检查点_
    - **weq_model_28qubit_config.json**  _28量子比特模型配置_
    - **weq_model_28qubit_trained_simple.json**  _训练后的28量子比特模型_
  - **training_data/**  _训练数据_
    - **quantum_blockchain_learning.py**  _区块链学习数据_
    - **WeQ/**  _WeQ特定训练数据_
      - **knowledge/**  _知识数据_
        - **logs/**  _训练日志_
- **neural/**  _神经网络实现_
- **quantum_blockchain/**  _WeQ特定区块链_
  - **__init__.py**  _包初始化_
  - **weq_blockchain.py**  _WeQ区块链实现_
- **static/**  _静态资源_
  - **js/**  _JavaScript文件_
    - **weq_entanglement_client.js**  _WeQ量子纠缠客户端_
    - **weq_multimodal_interactions.js**  _多模态交互静态资源_
- **templates/**  _模板文件_
  - **base.html**  _基础模板_
  - **base_weq.html**  _WeQ特定基础模板_
  - **shared/**  _共享模板组件_
    - **css/**  _共享CSS样式_
    - **js/**  _共享JavaScript文件_
  - **weq_multimodal_demo.html**  _WeQ多模态演示页面_

## 元数据
- **自动维护**: 此索引由Ref量子纠错子系统自动维护和更新
- **最后更新**: 2025-04-06
- **索引管理**: `Ref/monitor/index_monitor.py`
- **优化级别**: 2 (标准优化) 

```
```
量子基因编码: QE-DET-37B4D6D49B76
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
