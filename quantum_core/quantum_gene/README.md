# 量子基因神经网络 (Quantum Gene Neural Network)

基于量子计算的神经网络模型，专为处理基因和语义数据而设计。

## 组件结构

量子基因神经网络包含以下核心组件：

- **基础QGNN**: 原始量子基因神经网络实现
  - `QuantumGeneNeuralNetwork`: 主网络类
  - `QuantumGeneEncoder`: 数据编码器
  - `QuantumGeneLayer`: 量子神经网络层

- **语义增强组件**: 新增的语义理解能力
  - `quantum_semantic`: 量子语义理解层
    - `SemanticConcept`: 语义概念表示
    - `SemanticConceptStore`: 语义概念存储
    - `QuantumSemanticLayer`: 量子语义理解层
  
  - `quantum_attention`: 量子注意力机制
    - `QuantumSemanticAttention`: 注意力基类
    - `QuantumSelfAttention`: 自注意力机制
    - `QuantumCrossAttention`: 交叉注意力机制
    - `QuantumMultiModalAttention`: 多模态注意力
    - `QuantumHierarchicalAttention`: 层次注意力
  
  - `quantum_memory`: 量子语义记忆
    - `MemoryItem`: 记忆项
    - `QuantumMemoryRegion`: 记忆区域
    - `QuantumSemanticMemory`: 语义记忆管理
  
  - `quantum_reasoning`: 量子语义推理
    - `KnowledgeNode`: 知识图谱节点
    - `KnowledgeRelation`: 知识图谱关系
    - `QuantumKnowledgeGraph`: 量子知识图谱

- **增强版QGNN**: 整合了上述所有组件
  - `EnhancedQuantumGeneNeuralNetwork`: 增强版网络类

## 功能特点

1. **多模态处理**: 可处理文本、图像、音频等多种模态数据
2. **语义理解**: 具备基础语义映射和解释能力
3. **注意力机制**: 实现了多种量子注意力机制
4. **记忆存储**: 可存储和检索语义知识
5. **知识推理**: 基于量子行走算法的图谱推理

## 使用方法

### 基础QGNN

```python
from quantum_gene_network import QuantumGeneNeuralNetwork

# 创建QGNN实例
qgnn = QuantumGeneNeuralNetwork(num_qubits=8, num_layers=2)

# 处理输入数据
result = qgnn.forward(input_data)
```

### 增强版QGNN

```python
from quantum_gene_network import EnhancedQuantumGeneNeuralNetwork

# 创建增强版QGNN实例
enhanced_qgnn = EnhancedQuantumGeneNeuralNetwork()

# 处理查询
response = enhanced_qgnn.process_query("这是一个测试查询")

# 训练模型
training_data = [
    {
        'text': '示例文本1',
        'labels': ['类别1', '类别2'],
        'content': {'id': 1, 'text': '示例文本1'}
    },
    # 更多训练数据...
]
enhanced_qgnn.train(training_data, epochs=5)

# 保存模型
enhanced_qgnn.save("saved_model")

# 加载模型
loaded_model = EnhancedQuantumGeneNeuralNetwork.load("saved_model")
```

## 依赖

- Python 3.7+
- NumPy
- Cirq
- NetworkX (用于知识图谱)
- Matplotlib (可选，用于可视化)

## 安装

```bash
pip install -r requirements.txt
```

```
```
量子基因编码: QE-REA-D2185713C3B8
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
``````

// 开发团队：中华 ZhoHo ，Claude 
