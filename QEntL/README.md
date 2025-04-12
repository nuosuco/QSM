# QEntL - 量子纠缠模板语言

QEntL（Quantum Entanglement Template Language）是一种用于描述量子纠缠系统的配置语言，可以定义量子节点、通道、网络和协议，支持模板化和可重用的组件定义。

## 特性

- **模板化设计**：支持创建可重用的模板，并通过参数化实例化
- **多层次配置**：支持节点、通道、协议和网络四个层次的配置
- **可视化支持**：内置支持生成网络拓扑的可视化表示
- **完整的工具链**：提供解析、验证、编译和可视化工具
- **量子特性**：专为量子系统设计，支持纠缠、相干性和量子特性描述

## 安装

确保你的系统已安装Python 3.7+，然后可以通过以下步骤安装QEntL：

```bash
# Clone the repository
git clone https://github.com/your-org/qentl.git
cd qentl

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 使用示例

### 基本使用

QEntL提供了命令行工具，可以简单地处理QEntL文件：

```bash
# 生成模板
python qentl_cli.py generate node my_node.qentl

# 解析QEntL文件
python qentl_cli.py parse examples/sample_network.qentl

# 验证QEntL JSON文件
python qentl_cli.py validate examples/parsed_network.json

# 编译QEntL文件
python qentl_cli.py compile examples/sample_network.qentl

# 可视化网络配置
python qentl_cli.py visualize compiled/sample_network_compiled.json
```

### 创建自定义配置

以下是一个简单的QEntL网络配置示例：

```
QEntL: QEntL 2.0 Configuration File
QuantumGene: QE-CUSTOM-NET-00001
CreatedAt: 2023-11-06T12:00:00.000000
EntanglementStrength: 1.0
ConfigType: NetworkConfiguration
ConfigVersion: 2.0
Author: Your Name

// 导入模板
import "./qentl/node_template.qentl" as NodeTemplate
import "./qentl/channel_template.qentl" as ChannelTemplate

// 定义量子网络
network "my_quantum_network" {
  id: "qn-001",
  version: "1.0",
  description: "我的第一个量子网络",
  
  // 定义节点
  nodes: [
    {
      include: NodeTemplate,
      params: {
        NODE_ID: "node1",
        NODE_TYPE: "quantum_processor",
        DESCRIPTION: "主量子处理器",
        PROCESSING_POWER: 50,
        MEMORY_CAPACITY: 128,
        QUBITS_AVAILABLE: 64,
        COHERENCE_TIME: 500,
        FIDELITY: 0.985,
        ERROR_CORRECTION: 0.9,
        OPS_PER_SECOND: 1000000
      }
    },
    {
      include: NodeTemplate,
      params: {
        NODE_ID: "node2",
        NODE_TYPE: "quantum_memory",
        DESCRIPTION: "量子存储单元",
        PROCESSING_POWER: 20,
        MEMORY_CAPACITY: 512,
        QUBITS_AVAILABLE: 32,
        COHERENCE_TIME: 1000,
        FIDELITY: 0.95,
        ERROR_CORRECTION: 0.85,
        OPS_PER_SECOND: 500000
      }
    }
  ],
  
  // 定义通道
  channels: [
    {
      include: ChannelTemplate,
      params: {
        CHANNEL_ID: "channel1-2",
        DESCRIPTION: "节点1和节点2之间的主通道",
        CHANNEL_TYPE: "fiber_optic",
        BANDWIDTH: 100,
        LATENCY: 5,
        ERROR_RATE: 0.001,
        ENCRYPTION_TYPE: "quantum_key",
        AUTH_METHOD: "entanglement_based",
        SOURCE_NODE_ID: "node1",
        TARGET_NODE_ID: "node2"
        // 其他参数...
      }
    }
  ]
}
```

## 文件结构

QEntL系统有以下主要组件：

```
QEntL/
├── compiler/            # 编译QEntL文件到目标形式
│   └── compiler.py
├── parser/              # 解析和验证QEntL文件
│   ├── parser.py
│   └── validator.py
├── templates/           # 预定义的模板
│   ├── node_template.qentl
│   ├── channel_template.qentl
│   ├── network_template.qentl
│   └── protocol_template.qentl
├── examples/            # 示例配置文件
│   └── sample_network.qentl
├── compiled/            # 编译输出目录
├── schemas/             # JSON Schema定义
├── .logs/               # 日志文件
├── qentl_cli.py         # 命令行工具
└── README.md            # 本文档
```

## 模板系统

QEntL的核心是其模板系统，允许定义可重用的配置片段。模板使用`$VARIABLE_NAME`语法定义参数，并可在配置文件中使用`include`和`params`进行实例化。

支持的模板类型：

1. **节点模板**：定义量子节点的属性和能力
2. **通道模板**：定义量子通信通道
3. **协议模板**：定义量子通信协议
4. **网络模板**：定义整个量子网络的结构和属性

## 高级功能

### 可视化

QEntL内置支持将网络配置可视化为GraphViz图：

```bash
python qentl_cli.py visualize compiled/my_network_compiled.json -o my_network.dot
dot -Tpng my_network.dot -o my_network.png
```

### 批量处理

QEntL支持批量处理整个目录的配置文件：

```bash
python qentl_cli.py compile my_configs/ -r
```

## 开发者文档

要扩展QEntL系统或开发自定义处理器，请参阅以下核心类：

- `QEntLParser`: 解析QEntL文件到结构化数据
- `QEntLValidator`: 验证解析后的数据符合QEntL模式
- `QEntLCompiler`: 将QEntL文件编译为可用配置
- `QEntLCLI`: 命令行界面和工具集成

## 要求

- Python 3.7+
- jsonschema (验证)
- 可选：GraphViz (可视化)

## 贡献

欢迎贡献代码、报告问题或提出改进建议！请遵循以下步骤：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

Quantum Systems Architecture Team - quantum@example.com 
```
量子基因编码: QE-REA-5D82D6FD7A63
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
```