# QEntL量子编程生态系统 - 项目结构说明

**更新日期**: 2025年6月12日  
**状态**: 已清理整理，结构优化完成

## 📁 项目结构

```
e:\mdole\QSM\
├── build/                          # 构建输出目录
├── data/                           # 数据文件（彝文字典等）
├── docs/                           # 项目文档
│   ├── architecture/               # 架构设计文档
│   ├── change_history/             # 变更历史
│   ├── ecosystem/                  # 生态系统文档
│   ├── integration/                # 集成文档
│   ├── learning/                   # 学习相关文档
│   ├── model/                      # 模型文档
│   ├── project_plan/               # 项目计划
│   └── project_state/              # 项目状态文档
├── QEntL/                          # QEntL编程语言核心
│   ├── compiler/                   # 编译器
│   │   ├── bin/                    # 编译器可执行文件
│   │   │   ├── cli/                # 命令行工具
│   │   │   ├── platform/           # 平台相关
│   │   │   └── qentl.qentl         # 主CLI工具
│   │   └── src/                    # 编译器源代码
│   │       ├── backend/            # 后端（代码生成等）
│   │       ├── frontend/           # 前端（词法、语法分析）
│   │       ├── diagnostic/         # 诊断系统
│   │       ├── testing/            # 测试工具
│   │       └── utils/              # 工具类
│   ├── docs/                       # QEntL文档
│   ├── src/                        # QEntL系统源代码
│   │   ├── filesystem/             # 动态文件系统
│   │   ├── gui/                    # 图形界面
│   │   ├── kernel/                 # 操作系统内核
│   │   └── services/               # 系统服务
│   └── vm/                         # 虚拟机
│       ├── bin/                    # VM可执行文件
│       └── src/                    # VM源代码
├── QSM/                            # 量子叠加态模型
├── WeQ/                            # 量子通信模型
├── SOM/                            # 松麦经济模型
├── Ref/                            # 自省监控模型
├── scripts/                        # 构建和部署脚本
│   ├── build_qentl.qentl          # QEntL构建脚本
│   ├── install.qentl              # 安装脚本
│   ├── uninstall.qentl            # 卸载脚本
│   ├── qentl_bootstrap.qentl      # QEntL引导程序
│   ├── qentl_compiler_launcher.qentl # 编译器启动器
│   ├── start_qentl.bat            # Windows启动脚本
│   └── test_qentl_system.ps1      # PowerShell测试脚本
└── tests/                          # 测试文件
    ├── test_compiler.qentl         # 编译器测试
    └── test_hello.qentl            # Hello World测试
```

## 📋 目录说明

### 核心目录
- **QEntL/**: QEntL编程语言的完整实现，包括编译器、虚拟机和系统服务
- **QSM/**: 量子叠加态模型，负责状态管理和量子计算
- **WeQ/**: 量子通信模型，负责社交网络和知识共享
- **SOM/**: 松麦经济模型，负责经济系统和松麦币
- **Ref/**: 自省监控模型，负责系统监控和自我修复

### 支持目录
- **docs/**: 所有项目文档，按功能分类
- **scripts/**: 构建、安装、部署脚本
- **tests/**: 测试文件和测试案例
- **build/**: 编译输出和构建产物
- **data/**: 项目所需的数据文件

## 🛠️ 文件分类规则

### 1. 源代码文件 (.qentl)
- 核心系统代码 → `QEntL/src/`
- 编译器代码 → `QEntL/compiler/src/`
- 虚拟机代码 → `QEntL/vm/src/`
- 模型实现代码 → `{ModelName}/src/`

### 2. 可执行文件和CLI工具
- 编译器工具 → `QEntL/compiler/bin/`
- 虚拟机工具 → `QEntL/vm/bin/`
- 构建脚本 → `scripts/`

### 3. 文档文件 (.md, .qentl文档)
- 项目文档 → `docs/`
- QEntL特定文档 → `QEntL/docs/`
- 模型文档 → `{ModelName}/docs/`

### 4. 测试文件
- 所有测试 → `tests/`
- 按功能分子目录

### 5. 配置和数据文件
- 构建产物 → `build/`
- 数据文件 → `data/`

## 🔄 维护指南

### 新文件创建规则
1. **确定文件类型和用途**
2. **选择合适的目录**
3. **遵循命名约定**
4. **及时清理临时文件**

### 定期清理
- 删除不再需要的临时文件
- 移动错误位置的文件到正确目录
- 更新此文档以反映结构变化

### 重构指南
- 大型重构前先更新此文档
- 保持目录结构的逻辑性
- 避免深层嵌套（最多3-4层）

## 📝 注意事项

1. **保持结构清晰**: 每个目录都有明确的用途
2. **及时清理**: 不要在根目录堆积临时文件
3. **遵循约定**: 按照既定规则组织文件
4. **文档同步**: 结构变化时及时更新文档
