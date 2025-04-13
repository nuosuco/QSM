"""
量子基因编码模块 - 为QSM系统中的所有元素提供量子基因编码
"""

from Ref.gene.quantum_gene_encoder import get_encoder

# 导出核心功能
encoder = get_encoder()

# 便于导入的函数
def generate_quantum_gene(element_type, element_id, metadata=None):
    """生成量子基因编码"""
    return encoder.generate_quantum_gene(element_type, element_id, metadata)

def check_entanglement(gene1, gene2):
    """检查两个量子基因之间的纠缠度"""
    return encoder.check_entanglement(gene1, gene2)

def detect_entanglement_network(threshold=0.5):
    """检测整个系统中的量子纠缠网络"""
    return encoder.detect_entanglement_network(threshold) 

"""

"""
量子基因编码: QE-INI-C53B1FED426F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
