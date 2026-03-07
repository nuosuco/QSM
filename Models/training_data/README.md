# QEntL模型训练数据目录

## 📖 目录说明

本目录包含QEntL量子操作系统的所有训练数据、配置和结果文件，为五大量子模型的训练提供完整的数据支持。

## 📁 目录结构

```
Models/training_data/
├── README.md                               # 本说明文档
├── datasets/                               # 训练数据集
│   ├── training_data.json                 # 229个.qentl文件训练样本 (4.5MB)
│   └── yi_wen/                            # 彝文训练数据
│       ├── 滇川黔贵通用彝文词汇表摘要.json          # 彝文词汇表摘要 (6.2KB)
│       ├── 滇川黔贵通用彝文三语对照表.jsonl         # 三语对照表 (1.3MB)
│       ├── 通用彝文彝汉对照训练表(2.0.4.22).jsonl  # 彝汉对照表 (697KB)
│       └── 通用彝文汉彝对照训练表(2.0.4.22).jsonl  # 汉彝对照表 (697KB)
├── configs/                                # 训练配置
│   └── training_environment_config.json   # 训练环境配置
└── results/                                # 训练结果
    ├── training_results.json              # 五大模型训练结果
    └── QENTL_SYSTEM_COMPLETION_REPORT.json # 系统完成报告
```

## 📊 数据集详情

### 📁 datasets/training_data.json
- **文件大小**: 4.5MB
- **训练样本数**: 229个.qentl文件
- **数据来源**: 整个QEntL项目的程序文件
- **数据分类**: 
  - 按模型类型分类 (QSM, SOM, WeQ, Ref, QEntL)
  - 按硬件目标分类 (CPU, Memory, Storage, Network, Quantum)
  - 按语言类型分类 (中文, English, 滇川黔贵通用彝文)
  - 按量子状态分类 (量子叠加态字符)

### 📁 datasets/yi_wen/ (彝文训练数据)
- **滇川黔贵通用彝文词汇表摘要.json** (6.2KB)
  - 彝文词汇统计摘要
  - 字符分类统计
  - 翻译质量评估
  - 示例字符展示

- **滇川黔贵通用彝文三语对照表.jsonl** (1.3MB)
  - 4,120个彝文字符的三语对照
  - 彝文-中文-英文完整映射
  - 用于多语言模型训练

- **通用彝文彝汉对照训练表(2.0.4.22).jsonl** (697KB)
  - 彝文到中文的对照训练数据
  - 4,121条训练记录

- **通用彝文汉彝对照训练表(2.0.4.22).jsonl** (697KB)
  - 中文到彝文的对照训练数据
  - 4,121条训练记录

### 📊 样本分布
| 模型 | 样本数 | 功能类型 |
|------|--------|----------|
| QSM | 10 | 量子叠加态主模型 |
| SOM | 4 | 量子平权经济模型 |
| WeQ | 4 | 量子通讯协调模型 |
| Ref | 9 | 量子自反省模型 |
| QEntL | 202 | 量子操作系统核心 |

## ⚙️ 配置详情

### 📁 configs/training_environment_config.json
- **量子处理器**: 64量子比特
- **经典处理器**: 8核CPU + GPU加速
- **神经网络**: 5层量子叠加态架构
- **训练参数**: 
  - batch_size: 32
  - learning_rate: 2e-05
  - num_epochs: 100
  - max_seq_length: 512

## 📈 训练结果

### 📁 results/training_results.json
五大量子模型的训练结果详情：

| 模型 | 训练数据 | 量子相干性 | 准确率 | 量子保真度 | 多语言集成 |
|------|----------|------------|---------|------------|------------|
| QSM | 10样本 | 0.98 | 0.98 | 0.94 | 0.94 |
| SOM | 4样本 | 0.92 | 0.97 | 0.97 | 0.88 |
| WeQ | 4样本 | 0.98 | 0.98 | 0.96 | 0.90 |
| Ref | 9样本 | 0.96 | 0.96 | 0.98 | 0.88 |
| QEntL | 202样本 | 0.93 | 0.98 | 0.99 | 0.91 |

### 📊 性能指标
- **平均量子相干性**: 0.954
- **平均准确率**: 0.974
- **平均量子保真度**: 0.968
- **平均多语言集成**: 0.902

### 📁 results/QENTL_SYSTEM_COMPLETION_REPORT.json
系统完成报告包含：
- 完成时间: 2025-07-03T15:09:45
- 系统状态: fully_operational
- 训练摘要: 229个样本，5个模型
- 指令表摘要: 5条指令
- 执行引擎: 文件路径信息
- 下一步计划: 启动、测试、验证、部署

## 🔄 训练流程

### 第一阶段：准备训练数据
1. 收集所有.qentl文件
2. 智能分类和标注
3. 生成训练数据集

### 第二阶段：搭建训练环境
1. 配置量子处理器
2. 设置神经网络架构
3. 优化训练参数

### 第三阶段：开始模型训练
1. 五大模型并行训练
2. 24小时持续学习
3. 性能监控和优化

### 第四阶段：生成指令表
1. 训练完成后自动生成
2. 操作系统和应用程序指令
3. 量子特性支持

### 第五阶段：构建执行引擎
1. 量子执行引擎
2. 硬件控制接口
3. 系统启动器

## 🌐 多语言支持

### 中文 (50%权重)
- 量子哲学概念
- 东方智慧思想
- 传统计算思维

### English (40%权重)
- 技术精确性
- 国际标准
- 现代计算概念

### 滇川黔贵通用彝文 (10%权重)
- 总字符数: 87,046个
- 训练字符数: 4,120个
- 独特计算思维
- 古彝文量子概念

## 📋 使用方法

### 🔍 查看训练数据
```bash
# 查看数据集统计
python -c "
import json
with open('Models/training_data/datasets/training_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'训练样本数: {len(data)}')
    print(f'文件大小: {len(str(data))} 字符')
"
```

### ⚙️ 查看配置
```bash
# 查看训练环境配置
python -c "
import json
with open('Models/training_data/configs/training_environment_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    print('训练环境配置:')
    print(json.dumps(config, indent=2, ensure_ascii=False))
"
```

### 📊 查看结果
```bash
# 查看训练结果
python -c "
import json
with open('Models/training_data/results/training_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)
    print('训练结果摘要:')
    for model, result in results.items():
        print(f'{model}: 准确率 {result['performance_metrics']['accuracy']:.3f}')
"
```

## 🚀 相关脚本

训练脚本位于：
- `Models/training_scripts/unified_training_system.py` - 统一训练系统
- `Models/training_scripts/start_quantum_training.py` - 量子模型训练启动脚本

## 🔧 维护说明

### 📝 更新数据集
1. 修改训练脚本中的数据收集逻辑
2. 重新运行训练系统
3. 更新本README文档

### 🔄 重新训练
1. 备份当前结果
2. 清理旧的训练结果
3. 运行统一训练系统
4. 验证新的训练结果

### 📊 性能监控
定期检查训练结果的性能指标，确保：
- 量子相干性 > 0.90
- 准确率 > 0.95
- 量子保真度 > 0.93
- 多语言集成 > 0.88

---

**创建时间**: 2025年7月3日  
**最后更新**: 2025年7月3日  
**维护者**: QEntL开发团队  
**版本**: 1.0.0 