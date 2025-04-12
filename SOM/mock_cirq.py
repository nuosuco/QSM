"""
Mock Cirq Module
用于在无法加载正式cirq库时提供基本功能
"""

import numpy as np

class GridQubit:
    """模拟GridQubit"""
    def __init__(self, row, col):
        self.row = row
        self.col = col
    
    def __str__(self):
        return f"q({self.row}, {self.col})"
    
    def __repr__(self):
        return f"GridQubit({self.row}, {self.col})"
    
    @classmethod
    def rect(cls, rows, cols):
        """创建网格量子比特"""
        return [cls(r, c) for r in range(rows) for c in range(cols)]

class Gate:
    """基础门类"""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __call__(self, *qubits):
        return Operation(self, qubits)

class Ry(Gate):
    """Ry旋转门"""
    def __init__(self, rads):
        super().__init__(f"Ry({rads})")
        self.rads = rads

class H(Gate):
    """Hadamard门"""
    def __init__(self):
        super().__init__("H")

class X(Gate):
    """X门"""
    def __init__(self):
        super().__init__("X")

class Y(Gate):
    """Y门"""
    def __init__(self):
        super().__init__("Y")

class Z(Gate):
    """Z门"""
    def __init__(self):
        super().__init__("Z")

class Operation:
    """门操作"""
    def __init__(self, gate, qubits):
        self.gate = gate
        self.qubits = qubits
    
    def __str__(self):
        qubit_str = ", ".join(str(q) for q in self.qubits)
        return f"{self.gate}({qubit_str})"

class Circuit:
    """量子电路"""
    def __init__(self):
        self.operations = []
    
    def append(self, operation):
        """添加操作到电路"""
        self.operations.append(operation)
        return self
    
    def __str__(self):
        return "\n".join(str(op) for op in self.operations)

# 常用门
h = H()
x = X()
y = Y()
z = Z()

# 版本信息
__version__ = "mock.1.0.0"

print("警告: 使用了模拟版cirq库，功能有限") 