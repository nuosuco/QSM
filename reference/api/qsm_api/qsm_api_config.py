#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QSM API 配置文件

此文件包含QSM API服务的配置信息，包括各子系统的API端口、路径等信息
"""

# API端口配置
QSM_API_PORT = 5000  # QSM主API服务端口
WEQ_API_PORT = 5003  # WeQ API服务端口
SOM_API_PORT = 5001  # SOM API服务端口
REF_API_PORT = 5002  # Ref API服务端口

# API路径前缀
QSM_API_PREFIX = "/api/qsm"
WEQ_API_PREFIX = "/api/weq"
SOM_API_PREFIX = "/api/som"
REF_API_PREFIX = "/api/ref"

# 数据库配置
DATABASE_URI = "sqlite:///qsm_main.db"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "qsm_api.log"

# 跨域配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:5002",
    "http://localhost:5003",
]

# JWT配置
JWT_SECRET_KEY = "quantum_secret_multimodal_key"
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 令牌过期时间（秒）

# 子系统集成配置
INTEGRATE_WEQ = True
INTEGRATE_SOM = True
INTEGRATE_REF = True

# 认证配置
AUTH_REQUIRED = True
AUTH_EXCLUDED_ENDPOINTS = [
    "/api/qsm/health",
    "/api/weq/health",
    "/api/som/health",
    "/api/ref/health",
    "/api/qsm/auth/login",
    "/api/qsm/auth/register",
]

# 量子状态阵API配置
QUANTUM_STATE_ENDPOINT = "/api/qsm/quantum/state"
QUANTUM_INTERACTION_HISTORY_ENDPOINT = "/api/qsm/quantum/history"

# 版本信息
API_VERSION = "1.0.0" 

"""
"""
量子基因编码: QE-QSM-EB864F56D100
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
