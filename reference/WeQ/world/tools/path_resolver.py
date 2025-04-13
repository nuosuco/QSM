#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
资源路径解析器
用于处理全局资源和模型特定资源的路径问题，
支持独立运行模式和集成运行模式
"""

import os
import sys
import logging
from flask import request, current_app

# 添加项目根目录到sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PathResolver")

# 导入配置
try:
    from world.config.paths_config import MODELS, RESOURCE_MAPPING, DEFAULT_MODE
except ImportError as e:
    # 默认配置
    logger.warning(f"无法导入路径配置，使用默认配置: {e}")
    MODELS = ["QSM", "WeQ", "SOM", "Ref"]
    RESOURCE_MAPPING = {
        "standalone": {
            "world": "./world/static",
            "QSM": "./static",
            "WeQ": "./static",
            "SOM": "./static",
            "Ref": "./static"
        },
        "integrated": {
            "world": "/world/static",
            "QSM": "/QSM/static",
            "WeQ": "/WeQ/static",
            "SOM": "/SOM/static",
            "Ref": "/Ref/static"
        }
    }
    DEFAULT_MODE = "integrated"

class PathResolver:
    """资源路径解析器"""
    
    def __init__(self, app=None):
        self.app = app
        self.config = {
            "models": MODELS,
            "resource_mapping": RESOURCE_MAPPING,
            "mode": DEFAULT_MODE
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """在Flask应用中初始化路径解析器"""
        self.app = app
        
        # 注册模板函数
        app.jinja_env.globals.update(resource_url=self.resource_url)
        
        # 添加路径解析中间件
        @app.before_request
        def before_request():
            # 如有需要，在请求前进行路径处理
            pass
    
    def detect_mode(self):
        """检测当前运行模式（独立或集成）"""
        # 可以通过环境变量、配置文件或当前运行目录来检测
        if self.app and hasattr(self.app, 'config') and 'RUN_MODE' in self.app.config:
            return self.app.config['RUN_MODE']
        
        return self.config.get('mode', DEFAULT_MODE)
    
    def get_model_name(self):
        """获取当前模型名称"""
        if self.app and hasattr(self.app, 'config') and 'MODEL_NAME' in self.app.config:
            return self.app.config['MODEL_NAME']
        
        # 尝试从请求路径判断
        if request and request.path:
            for model in MODELS:
                if request.path.startswith(f'/{model}/'):
                    return model
        
        # 默认返回QSM
        return "QSM"
    
    def resource_url(self, path, model=None):
        """
        生成资源URL
        
        参数:
            path: 资源路径
            model: 模型名称，如果为None则使用全局资源
        
        返回:
            完整的资源URL
        """
        mode = self.detect_mode()
        
        if model is None or model == 'world':
            # 全局资源
            base_path = self.config['resource_mapping'][mode]['world']
            return f"{base_path}/{path.lstrip('/')}"
        else:
            # 模型特定资源
            if model in self.config['resource_mapping'][mode]:
                base_path = self.config['resource_mapping'][mode][model]
                return f"{base_path}/{path.lstrip('/')}"
            else:
                # 默认回退到全局资源
                base_path = self.config['resource_mapping'][mode]['world']
                return f"{base_path}/{path.lstrip('/')}"

# 创建单例实例
path_resolver = PathResolver()

def init_app(app):
    """初始化应用的快捷方法"""
    path_resolver.init_app(app)

def resource_url(path, model=None):
    """资源URL生成的快捷方法"""
    return path_resolver.resource_url(path, model) 

"""
"""
量子基因编码: QE-PAT-ED6E59E0D78C
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
