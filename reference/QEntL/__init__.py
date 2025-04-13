# 
"""
"""
量子基因编码: Q-BCE3-2944-ABFE
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
# 开发团队：中华 ZhoHo ，Claude

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QEntL - 量子纠缠模板语言
用于描述量子纠缠系统的配置语言
"""

from .parser import QEntLParser, QEntLValidator
from .compiler import QEntLCompiler

__version__ = "2.0.0"
__all__ = ['QEntLParser', 'QEntLValidator', 'QEntLCompiler']

# 让导入发生在实际使用时，避免循环导入
def get_version():
    """获取QEntL版本号"""
    return __version__

def get_info():
    """获取QEntL信息"""
    return {
        "name": "QEntL - 量子纠缠语言",
        "version": __version__,
        "author": __author__,
        "description": "一种基于量子纠缠原理的编程语言框架",
        "repository": "https://github.com/zhohov/qentl"
    } 