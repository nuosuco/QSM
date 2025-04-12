# quantum_adapter

## 模块说明
量子适配器模块 - 负责将Claude生成的知识向量转换为WeQ可训练的格式
实现Claude和WeQ神经网络之间的双向交互和知识转换

## 功能概述

### 类

- `QuantumKnowledgeAdapter`

### 函数

- `__init__`
- `vector_to_quantum_state`
- `quantum_state_to_vector`
- `add_to_batch`
- `prepare_training_batch`
- `create_training_samples`
- `save_quantum_ready_data`
- `load_quantum_ready_data`
- `prepare_knowledge_for_weq`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 15:31:10*