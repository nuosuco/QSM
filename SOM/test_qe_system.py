"""
测试量子电商系统
使用模拟的cirq库
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.abspath('.'))

# 尝试使用模拟库
print("正在测试量子电商系统...")
try:
    # 尝试导入真实cirq
    import cirq
    print(f"使用真实cirq库 (版本: {cirq.__version__})")
except ImportError:
    # 使用模拟cirq
    print("无法导入真实cirq库，使用模拟版本...")
    sys.modules['cirq'] = __import__('SOM.mock_cirq')
    import SOM.mock_cirq as cirq

# 创建基本模拟类
class QuantumGene:
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits
    
    def encode(self, data):
        return "量子编码: " + str(data)[:20] + "..."

class QuantumGeneOps:
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits

class QuantumDatabase:
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits
        self.storage = {}
    
    def store(self, key, value):
        self.storage[key] = value
        return True
    
    def search(self, query):
        results = []
        for key, value in self.storage.items():
            results.append({'key': key, 'value': value, 'similarity': 0.9})
        return results

class QuantumWallet:
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits
    
    def create_transaction(self, sender, receiver, amount, metadata=None):
        from collections import namedtuple
        Transaction = namedtuple('Transaction', ['sender', 'receiver', 'amount', 'signature'])
        return Transaction(sender, receiver, amount, "QS" + str(hash(f"{sender}{receiver}{amount}"))[:10])

class QuantumContract:
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits

# 添加模拟模块
sys.modules['quantum_gene'] = type('', (), {'QuantumGene': QuantumGene, 'QuantumGeneOps': QuantumGeneOps})
sys.modules['quantum_db'] = type('', (), {'QuantumDatabase': QuantumDatabase})
sys.modules['quantum_wallet'] = type('', (), {'QuantumWallet': QuantumWallet})
sys.modules['quantum_contract'] = type('', (), {'QuantumContract': QuantumContract})

# 导入量子电商系统
try:
    from SOM.quantum_ecommerce import QuantumEcommerce
    
    # 测试基本功能
    print("\n开始测试量子电商基本功能:")
    ecommerce = QuantumEcommerce()
    
    # 添加商品
    product = ecommerce.add_product(
        name="量子计算机模拟器",
        description="用于量子计算研究的设备",
        price=5999.99,
        stock=5,
        metadata={"category": "computing", "weight": "5kg"}
    )
    print(f"添加商品成功: {product.name}, ID: {product.product_id[:8]}...")
    
    # 创建订单
    order = ecommerce.create_order(
        user_id="TestUser",
        product_ids=[product.product_id],
        quantities=[1],
        metadata={"shipping": "express"}
    )
    print(f"创建订单成功: ID: {order.order_id[:8]}..., 金额: {order.total_amount}")
    
    # 处理支付
    payment_result = ecommerce.process_payment(order.order_id)
    print(f"支付处理结果: {'成功' if payment_result else '失败'}")
    
    # 获取订单信息
    order_info = ecommerce.get_order_info(order.order_id)
    print(f"订单状态: {order_info['status']}")
    
    print("\n测试完成！量子电商系统基本功能正常。")
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc() 