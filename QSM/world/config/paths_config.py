#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
资源路径配置
为项目中的路径解析提供配置支持
"""

# 支持的模型列表
MODELS = ["QSM", "WeQ", "SOM", "Ref"]

# 资源映射配置
RESOURCE_MAPPING = {
    # 独立运行模式
    "standalone": {
        "world": "./world/static",
        "QSM": "./static",
        "WeQ": "./static",
        "SOM": "./static",
        "Ref": "./static"
    },
    # 集成运行模式
    "integrated": {
        "world": "/world/static",
        "QSM": "/QSM/static",
        "WeQ": "/WeQ/static",
        "SOM": "/SOM/static",
        "Ref": "/Ref/static"
    }
}

# 默认运行模式
DEFAULT_MODE = "integrated"

"""
"""
量子基因编码: QE-PAT-4858A0FB1BAC
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
