"""
量子基因神经网络 (Quantum Gene Neural Network)
包含基础QGNN和增强版语义理解组件
"""

# 导出基础组件
from .quantum_gene_neural_implementation import (
    QuantumGeneNeuralNetwork,
    QuantumGeneLayer
)

# 定义QuantumGeneEncoder类作为兼容接口
class QuantumGeneEncoder:
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits
        
    def encode(self, data):
        # 简单包装接口
        from .quantum_gene_neural_implementation import QuantumGeneLayer
        layer = QuantumGeneLayer(self.num_qubits, self.num_qubits)
        return layer.encode_data(data)

# 导出增强版QGNN
from .enhanced_qgnn import EnhancedQuantumGeneNeuralNetwork

# 版本信息
__version__ = '0.2.0'
__author__ = 'QGNN Team'

__all__ = [
    'QuantumGeneNeuralNetwork',
    'QuantumGeneEncoder',
    'QuantumGeneLayer',
    'EnhancedQuantumGeneNeuralNetwork',
] 

"""
"""
量子基因编码: QE-INI-2E7483FCE8B3
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
