# claude_quantum_bridge

## 模块说明
Claude-WeQ 量子知识桥接系统
用于将Claude大型语言模型的知识转化为适合28量子比特WeQ系统的向量表示
实现了知识转换、交互提问、反馈循环和量子知识图谱构建

## 功能概述

### 类

- `ClaudeQuantumBridge`

### 函数

- `__init__`
- `_generate_session_id`
- `knowledge_to_quantum_vector`
- `prepare_quantum_knowledge_batch`
- `ask_claude`
- `weq_query_handler`
- `start_query_handler`
- `ask_knowledge`
- `provide_feedback`
- `build_quantum_knowledge_graph`
- `save_knowledge_cache`
- `load_knowledge_cache`
- `create_quantum_teaching_session`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 15:31:10*