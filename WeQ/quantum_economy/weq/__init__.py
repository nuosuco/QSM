"""
松麦经济模型包

这个包包含了松麦经济模型的核心组件，实现了松麦币发行、经济循环、
价值分配和电商平台等功能。

主要组件:
- weq_economy: 松麦经济模型核心实现
- weq_ecommerce: 松麦电商平台实现
"""

from quantum_economy.WeQ.WeQ_economy import (
    SomEconomyModel,
    CycleController,
    ValueDistributor,
    EcosystemDeveloper,
    MarketRegulator
)

from quantum_economy.WeQ.WeQ_ecommerce import SomEcommerce

__all__ = [
    'SomEconomyModel',
    'CycleController',
    'ValueDistributor',
    'EcosystemDeveloper',
    'MarketRegulator',
    'SomEcommerce'
]

__version__ = '0.1.0' 

"""
"""
量子基因编码: QE-INI-59F4570FBD6A
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
