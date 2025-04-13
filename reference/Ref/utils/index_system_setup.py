#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
索引系统初始化脚本 - 创建必要的目录结构和配置文件
"""

import os
import sys
import json
import shutil
import logging
import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("IndexSystemSetup")

# 确保路径正确
script_dir = os.path.dirname(os.path.abspath(__file__))
ref_dir = os.path.dirname(script_dir)
project_root = os.path.dirname(ref_dir)

# 需要创建的目录结构
DIRECTORIES = [
    os.path.join(ref_dir, "data"),
    os.path.join(ref_dir, "backup", "index_backups"),
    os.path.join(ref_dir, "logs"),
    os.path.join(ref_dir, "monitor"),
    os.path.join(ref_dir, "utils"),
    os.path.join(project_root, "docs", "world"),
    os.path.join(project_root, "docs", "QSM", "world"),
    os.path.join(project_root, "docs", "SOM", "world"),
    os.path.join(project_root, "docs", "WeQ", "world"),
    os.path.join(project_root, "docs", "Ref", "world"),
]

# 配置文件路径
CONFIG_PATH = os.path.join(ref_dir, "data", "index_management.json")

def create_directories():
    """创建必要的目录结构"""
    for dir_path in DIRECTORIES:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"创建目录: {dir_path}")
        else:
            logger.info(f"目录已存在: {dir_path}")

def create_default_config():
    """创建默认配置文件"""
    if os.path.exists(CONFIG_PATH):
        logger.info(f"配置文件已存在: {CONFIG_PATH}")
        return
    
    config = {
        "last_update": datetime.datetime.now().isoformat(),
        "index_files": {
            "project": "docs/world/qsm_project_index.md",
            "qsm": "docs/QSM/world/qsm_index.md",
            "som": "docs/SOM/world/som_index.md",
            "weq": "docs/WeQ/world/weq_index.md",
            "ref": "docs/Ref/world/ref_index.md",
            "world": "docs/world/world_modules.md",
            "detailed": "docs/world/detailed_index.md",
            "files": "docs/world/files_index.md",
            "navigation": "docs/world/navigation_index.md"
        },
        "backup_directory": "Ref/backup/index_backups",
        "optimization_level": 3,
        "auto_update": True,
        "update_interval": 86400,  # 默认1天
        "monitor_changes": True,
        "optimization_rules": {
            "path_standardization": True,
            "description_updating": True,
            "metadata_enhancement": True,
            "structure_improvement": True
        },
        "file_classification": {
            "core_files": [
                "app.py",
                "quantum_blockchain_core.py",
                "qsm_main_chain.py",
                "ref_blockchain.py",
                "weq_blockchain.py",
                "som_coin_system.py"
            ],
            "config_files": [
                "*.json",
                "*.config",
                "*.yml",
                "*.yaml"
            ],
            "document_files": [
                "*.md",
                "*.txt",
                "*.html"
            ],
            "script_files": [
                "*.py",
                "*.js"
            ],
            "template_files": [
                "*.html",
                "*.htm",
                "*.template"
            ],
            "style_files": [
                "*.css",
                "*.scss",
                "*.less"
            ]
        },
        "directory_classification": {
            "core_dirs": [
                "quantum_core",
                "quantum_blockchain"
            ],
            "api_dirs": [
                "api"
            ],
            "docs_dirs": [
                "docs"
            ],
            "frontend_dirs": [
                "frontend",
                "templates",
                "static"
            ],
            "model_dirs": [
                "models",
                "checkpoints"
            ]
        },
        "description_mappings": {
            "directory": {
                "api": "API接口定义和实现",
                "docs": "项目文档",
                "frontend": "前端共享组件和工具",
                "world": "全局配置、模板和工具",
                "models": "模型定义和检查点",
                "quantum_core": "量子核心功能实现",
                "quantum_data": "量子数据存储",
                "quantum_economy": "量子经济系统",
                "quantum_shared": "共享的量子工具和存储",
                "QSM": "主模型实现",
                "Ref": "量子纠错子系统",
                "SOM": "量子经济子系统",
                "src": "源代码通用组件",
                "static": "静态资源",
                "WeQ": "小趣子系统",
                "quantum_blockchain": "量子区块链实现",
                "templates": "模板文件",
                "js": "JavaScript文件",
                "css": "CSS样式文件",
                "images": "图片资源",
                "config": "配置文件",
                "tools": "工具脚本",
                "shared": "共享组件",
                "knowledge": "知识库",
                "neural": "神经网络实现",
                "backup": "备份功能",
                "repair": "修复功能",
                "monitor": "监控功能",
                "utils": "工具函数",
                "gene": "基因实现",
                "data": "数据文件",
                "logs": "日志文件",
                "checkpoints": "模型检查点",
                "training_data": "训练数据",
                "crawler_data": "爬虫数据",
                "multimodal": "多模态交互"
            },
            "file": {
                "app.py": "应用入口点",
                "__init__.py": "包初始化文件",
                "qsm_main_chain.py": "QSM主链实现",
                "quantum_blockchain_core.py": "量子区块链核心",
                "weq_blockchain.py": "WeQ区块链实现",
                "ref_blockchain.py": "Ref区块链实现",
                "som_coin_system.py": "SOM代币系统",
                "base.html": "基础模板",
                "base_qsm.html": "QSM基础模板",
                "base_som.html": "SOM基础模板",
                "base_weq.html": "WeQ基础模板",
                "base_ref.html": "Ref基础模板",
                "quantum_loader.js": "量子加载器",
                "quantum_entanglement.js": "量子纠缠实现",
                "quantum_entanglement_client.js": "量子纠缠客户端",
                "weq_multimodal_interactions.js": "WeQ多模态交互",
                "som_entanglement_client.js": "SOM量子纠缠客户端",
                "weq_entanglement_client.js": "WeQ量子纠缠客户端",
                "ref_entanglement_client.js": "Ref量子纠缠客户端",
                "background_training.py": "背景知识训练",
                "quantum_blockchain_learning.py": "量子区块链学习",
                "paths_config.py": "路径配置",
                "path_resolver.py": "路径解析工具",
                "auto_template_watcher.py": "模板自动监视",
                "create_page.py": "页面创建工具",
                "install_auto_template.py": "自动模板安装",
                "start_template_watcher.py": "启动模板监视",
                "update_project_index.py": "项目索引更新工具",
                "index_monitor.py": "索引监控脚本",
                "index_system_setup.py": "索引系统初始化脚本",
                "multimodal_entanglement.py": "多模态纠缠",
                "simplified_core.py": "简化核心",
                "index_management.json": "索引管理配置",
                "detailed_index.md": "详细目录索引",
                "files_index.md": "文件索引",
                "world_modules.md": "全局模块概要",
                "navigation_index.md": "导航索引",
                "qsm_project_index.md": "项目总体索引",
                "qsm_index.md": "QSM主模型索引",
                "som_index.md": "SOM子系统索引",
                "weq_index.md": "WeQ子系统索引",
                "ref_index.md": "Ref子系统索引"
            }
        },
        "optimization_history": [
            {
                "date": datetime.datetime.now().isoformat(),
                "action": "initial_setup",
                "description": "初始化索引管理系统"
            }
        ]
    }
    
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"创建默认配置文件: {CONFIG_PATH}")

def copy_monitor_script():
    """复制监控脚本到适当的位置"""
    source = os.path.join(ref_dir, "monitor", "index_monitor.py")
    if not os.path.exists(source):
        logger.warning(f"索引监控脚本不存在: {source}")
        return False
    
    target = os.path.join(ref_dir, "monitor", "index_monitor.py")
    if os.path.exists(target):
        logger.info(f"监控脚本已存在: {target}")
        return True
    
    shutil.copy2(source, target)
    logger.info(f"复制监控脚本: {source} -> {target}")
    return True

def create_readme():
    """创建README文件"""
    readme_path = os.path.join(ref_dir, "README.md")
    if os.path.exists(readme_path):
        logger.info(f"README文件已存在: {readme_path}")
        return
    
    content = """# Ref 索引管理系统

Ref量子纠错子系统的索引管理模块，用于自动维护和优化QSM项目的目录和文件索引。

## 功能

- 自动扫描项目结构并更新目录索引
- 维护完整的文件索引
- 定期备份索引文件
- 监控项目文件变化并触发更新
- 优化索引结构和描述

## 目录结构

- `data/`: 配置和数据文件
- `backup/`: 索引文件备份
- `logs/`: 日志文件
- `monitor/`: 监控脚本
- `utils/`: 工具脚本

## 使用方法

### 初始化索引系统

```bash
python Ref/utils/index_system_setup.py
```

### 手动更新索引

```bash
python frontend/tools/update_project_index.py
```

### 启动监控服务

```bash
python Ref/monitor/index_monitor.py
```

### 强制更新索引

```bash
python Ref/monitor/index_monitor.py --force-update
```

## 配置文件

索引系统的配置文件位于 `Ref/data/index_management.json`，你可以修改此文件来调整索引系统的行为。
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"创建README文件: {readme_path}")

def setup_system():
    """设置索引系统"""
    try:
        # 创建目录结构
        create_directories()
        
        # 创建默认配置
        create_default_config()
        
        # 复制监控脚本
        copy_monitor_script()
        
        # 创建README
        create_readme()
        
        logger.info("索引系统初始化完成")
        return True
    except Exception as e:
        logger.error(f"索引系统初始化失败: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QSM项目索引系统初始化工具")
    parser.add_argument('--force', action='store_true', help="强制重新初始化")
    args = parser.parse_args()
    
    if args.force:
        # 强制重新初始化
        logger.info("强制重新初始化索引系统")
    
    if setup_system():
        logger.info("索引系统设置成功")
        return 0
    else:
        logger.error("索引系统设置失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 

"""

"""
量子基因编码: QE-IND-D0665ED482B9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
