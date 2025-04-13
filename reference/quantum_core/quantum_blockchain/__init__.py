"""
QSM量子区块链核心包
为量子叠加态模型提供区块链基础设施
支持主链与子链的量子纠缠通信
"""

from quantum_core.quantum_blockchain.quantum_blockchain_core import (
    MainQuantumBlockchain,
    SubQuantumBlockchain,
    QuantumBlock,
    QuantumTransaction,
    EntanglementChannel
)

<<<<<<< HEAD
from quantum_core.quantum_blockchain.QSM_main_chain import (
=======
from quantum_core.quantum_blockchain.qsm_main_chain import (
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
    QsmMainChain,
    get_main_chain
)

# 导入量子叠加态模型知识库
try:
<<<<<<< HEAD
    from quantum_core.quantum_blockchain.QSM_knowledge import (
=======
    from quantum_core.quantum_blockchain.qsm_knowledge import (
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
        QsmKnowledge,
        get_qsm_knowledge
    )
    __has_qsm_knowledge = True
except ImportError:
    __has_qsm_knowledge = False

__all__ = [
    'MainQuantumBlockchain',
    'SubQuantumBlockchain',
    'QuantumBlock',
    'QuantumTransaction',
    'EntanglementChannel',
    'QsmMainChain',
    'get_main_chain'
]

# 如果量子叠加态模型知识库可用，则添加到__all__中
if __has_qsm_knowledge:
    __all__.extend(['QsmKnowledge', 'get_qsm_knowledge']) 

"""
"""
量子基因编码: QE-INI-222F978496A2
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
