# QSM (QEntL) 项目结构分析报告

> 生成日期: 2026-06-28
> 项目路径: /root/QSM
> 总非Git文件数: 611
> Git仓库大小: 5.9GB (含40个临时pack文件)
> 数据目录大小: 325MB

---

## 一、目录结构树

```
QSM/                              # 项目根目录 (QEntL量子操作系统)
├── .git/                         # Git元数据 (5.9GB, 含40个临时pack文件)
├── .gitignore                    # Git忽略规则
├── Makefile                      # 顶层构建脚本
│
├── api/                          # Python API层 (64KB, 12文件)
│   ├── README.md                 # API文档
│   ├── start_api.sh              # API启动脚本
│   ├── qsm_Q2_api.py             # Q2量子API
│   ├── qsm_Q4_api.py             # Q4量子API
│   ├── qsm_quantum_api.py        # 量子API核心
│   ├── qsm_superposition_api.py  # 叠加态API
│   ├── qsm_yi_api.py             # Yi语言API
│   ├── qsm_yi_api_v3.py          # Yi API v3
│   ├── qsm_yi_api_v4.py          # Yi API v4
│   ├── qsm_yi_translate_api.py   # Yi翻译API
│   └── v2/                       # API v2版本 (3文件, 与上层部分重叠)
│       ├── q1_api.py
│       ├── qv4_api.py
│       └── v4_api.py
│
├── aurora/                       # Aurora引擎QEntL版 (36KB, 5文件)
│   ├── aurora_engine.qentl       # 引擎核心
│   ├── config.qentl              # 配置文件
│   ├── memory_loader.qentl       # 内存加载器
│   ├── start_aurora.sh           # 启动脚本
│   └── wechat_push.qentl         # 微信推送模块
│
├── bin/                          # 编译产物 (84KB, 5文件)
│   ├── bell.qbc                  # Bell状态字节码
│   ├── qentl_compiler            # QEntL编译器二进制
│   ├── qnn_runner                # QNN运行器二进制
│   ├── qvm_boot                  # QVM引导程序二进制
│   └── yi_pipeline               # Yi流水线二进制
│
├── data/                         # 训练数据 (325MB, 103文件) ★最大目录
│   ├── *.jsonl                   # 91个训练数据文件 (JSON Lines格式)
│   ├── docs/index.html           # 数据文档
│   ├── 《通用彝文字典》.pdf      # 113MB - 主字典
│   ├── 《通用彝文字典》_上册.pdf  # 74MB
│   ├── 《通用彝文字典》_下册.pdf  # 81MB
│   ├── 滇川黔桂彝文字典_*.pdf    # 35MB
│   ├── ywly2通用彝文4120注释*.pdf # 3.1MB
│   ├── 彝文三语对照表_4120字.{csv,docx}
│   ├── 通用彝文彝汉对照表.xlsx   # 250KB
│   ├── 通用彝文彝汉对照训练表.{jsonl,xlsx}
│   ├── 通用彝文汉彝对照训练表.{jsonl,xlsx}
│   ├── 测试.xlsx
│   └── ... (大量yi_*系列训练文件)
│
├── docs/                         # 开发文档 (2.4MB, 57文件)
│   ├── MASTER_PLAN_COMPLETE.md   # 主计划 v4.0
│   ├── PROJECT_STRUCTURE.md      # 项目结构说明
│   ├── QEntL_RUNTIME_GUIDE.md    # 运行时指南
│   ├── change_history.qentl      # 变更历史
│   ├── project_construction_plan.qentl
│   ├── architecture/             # 架构设计 (14文件)
│   │   ├── QEntL_docs/           # QEntL详细文档 (9文件)
│   │   │   ├── compiler_implementation_plan.md
│   │   │   ├── installation_guide.md
│   │   │   ├── QEntL_BUILD_PLAN.md
│   │   │   ├── qentl_ecosystem_plan.md
│   │   │   ├── qentl_environment_design.md
│   │   │   ├── quantum_ecosystem_integration.md
│   │   │   ├── README.md
│   │   │   ├── syntax.md
│   │   │   └── vm_implementation_plan.md
│   │   ├── QEntL_Compiler.qentl
│   │   ├── QEntL_OS_Components.qentl
│   │   ├── QEntL_OS_Core.qentl
│   │   ├── QEntL_QNN_Engine.qentl
│   │   ├── QEntL_System_Calls.qentl
│   │   ├── QEntL_Yi_Data_Pipeline.qentl
│   │   ├── 中华之语于Claude.txt
│   │   ├── 华经_ANSI.txt
│   │   ├── 服务人类生态基金.txt
│   │   ├── 松麦文化.txt
│   │   └── 框架设计决策_量子叠加态模型.txt
│   ├── core/                     # 核心文档 (2文件)
│   │   ├── QSM核心基础文档库.txt
│   │   └── 三大圣律与伦理实践宣章.txt
│   ├── ecosystem/                # 生态系统 (3文件)
│   ├── examples/                 # 量子示例 (11文件, 全部.qentl)
│   │   ├── hello.qentl
│   │   ├── bb84_protocol.qentl
│   │   ├── teleportation.qentl
│   │   └── ... (Grover, GHZ, QFT等)
│   ├── integration/              # 集成文档 (3文件)
│   ├── learning/                 # 学习资源 (4文件)
│   ├── philosophy/               # 哲学/实现 (5文件)
│   └── project_state/            # 项目状态 (6文件)
│
├── Installer/                    # 安装器 (44KB, 6文件)
│   ├── autorun.inf
│   ├── setup.bat
│   ├── docs/installation_guide.md   # ← 与docs/architecture/QEntL_docs/完全重复
│   ├── qentl_bootmgr.c
│   ├── qentl_installer.qentl
│   └── sources/IMAGE_README.md
│   └── support/                     # 空目录
│
├── memory_bank/                  # AI记忆库 (320KB, 74文件)
│   ├── context_snapshot.json     # 上下文快照
│   ├── cycle_summary.json        # 周期摘要
│   ├── architecture_*.md         # 10个架构快照 (每2小时一次)
│   ├── improvement_*.md          # 10个改进记录
│   ├── learning_*.md             # 10个学习记录
│   ├── memory_update_*.md        # 10个记忆更新
│   ├── summary_*.md              # 10个摘要
│   ├── testing_*.md              # 10个测试记录
│   └── training_*.md             # 10个训练记录
│
├── QEntL/                        # QEntL系统源码 (4.5MB, 212文件) ★最大源码目录
│   ├── docs/                     # 系统文档 (10文件)
│   │   ├── README.md             # ← 与docs/architecture/QEntL_docs/README.md重复
│   │   ├── QEntL_BUILD_PLAN.md   # ← 与docs/architecture/QEntL_docs/重复
│   │   ├── compiler_implementation_plan.md  # ← 重复
│   │   ├── qentl_ecosystem_plan.md          # ← 重复
│   │   ├── qentl_environment_design.md      # ← 重复
│   │   ├── quantum_ecosystem_integration.md # ← 重复
│   │   ├── syntax.md                    # ← 重复
│   │   ├── vm_implementation_plan.md    # ← 重复
│   │   ├── deployment/README.md
│   │   ├── development/README.md
│   │   └── architecture/README.md
│   ├── scripts/                  # 构建脚本 (7文件)
│   │   ├── Makefile              # ← 与根目录Makefile重复
│   │   ├── build_qentl.qentl
│   │   ├── build_bootstrap.bat
│   │   ├── install.qentl
│   │   ├── uninstall.qentl
│   │   ├── start_qentl.bat
│   │   └── qentl_bootstrap.c
│   ├── Models/                   # 模型定义 (10文件)
│   │   ├── QSM/                  # QSM模型
│   │   │   ├── docs/qsm_implementation.qentl   # ← 与docs/philosophy/重复
│   │   │   └── docs/project_plan/
│   │   │       ├── qsm_construction_plan.qentl
│   │   │       ├── som_construction_plan.qentl # ← 与SOM/重复
│   │   │       └── weq_construction_plan.qentl # ← 与WeQ/重复
│   │   ├── Ref/                  # Ref模型
│   │   │   ├── docs/ref_implementation.qentl   # ← 与docs/philosophy/重复
│   │   │   └── docs/project_plan/ref_construction_plan.qentl
│   │   ├── SOM/                  # SOM模型
│   │   │   ├── docs/som_implementation.qentl   # ← 与docs/philosophy/重复
│   │   │   └── docs/project_plan/som_construction_plan.qentl
│   │   └── WeQ/                  # WeQ模型
│   │       ├── docs/weq_implementation.qentl   # ← 与docs/philosophy/重复
│   │       └── docs/project_plan/weq_construction_plan.qentl
│   └── System/                   # 系统组件 (185文件)
│       ├── Compiler/             # 编译器 (65文件)
│       │   ├── bin/
│       │   │   ├── qentl.qentl
│       │   │   ├── cli/          # 命令行工具 (7文件)
│       │   │   │   ├── compiler_cli.qentl
│       │   │   │   ├── bytecode_generator_cli.qentl
│       │   │   │   ├── bytecode_optimizer_cli.qentl
│       │   │   │   ├── linker_cli.qentl
│       │   │   │   ├── option_parser.qentl
│       │   │   │   ├── auto_compiler.qentl
│       │   │   │   └── qentl_cli.qentl
│       │   │   └── platform/     # 平台安装 (3文件)
│       │   └── src/
│       │       ├── compiler.qentl
│       │       ├── backend/
│       │       │   ├── build/       # 构建系统 (6文件)
│       │       │   │   ├── incremental_builder.qentl
│       │       │   │   ├── incremental_build_manager.qentl
│       │       │   │   ├── parallel_builder.qentl
│       │       │   │   ├── parallel_build_manager.qentl
│       │       │   │   ├── parallel_build_scheduler.qentl
│       │       │   │   └── build/optimizer.qentl
│       │       │   ├── bytecode/    # 字节码 (5文件)
│       │       │   │   ├── generator/
│       │       │   │   │   ├── quantum_bytecode_generator.qentl
│       │       │   │   │   ├── qobj_generator.qentl
│       │       │   │   │   ├── qexe_generator.qentl
│       │       │   │   │   └── optimizer.qentl
│       │       │   │   └── optimizer/
│       │       │   │       ├── bytecode_optimizer.qentl
│       │       │   │       ├── entanglement_optimizer.qentl
│       │       │   │       └── quantum_gate_fusion.qentl
│       │       │   ├── debug/       # 调试 (2文件)
│       │       │   │   ├── debug_info_generator.qentl
│       │       │   │   └── source_mapping.qentl
│       │       │   ├── debug_info/  # ← 与debug/重复
│       │       │   │   └── debug_info_generator.qentl
│       │       │   ├── ir/          # IR中间表示 (3文件)
│       │       │   ├── linker/      # 链接器 (3文件)
│       │       │   └── optimizer/   # ← 与bytecode/optimizer/部分重复
│       │       │       └── quantum_gate_fusion.qentl
│       │       ├── diagnostic/    # 诊断 (2文件)
│       │       ├── frontend/      # 前端 (8文件)
│       │       │   ├── lexer/     # 词法分析 (2文件)
│       │       │   ├── parser/    # 语法分析 (2文件)
│       │       │   └── semantic/  # 语义分析 (3文件)
│       │       ├── testing/       # 测试 (2文件)
│       │       │   ├── test_framework.qentl
│       │       │   └── unit_test_framework.qentl
│       │       └── utils/         # 工具 (5文件)
│       ├── Kernel/              # 内核 (115文件)
│       │   ├── filesystem/      # 文件系统 (23文件)
│       │   ├── gui/             # GUI (15文件)
│       │   ├── kernel/          # 核心 (17文件)
│       │   │   ├── microkernel_core.qentl
│       │   │   ├── quantum_processor.qentl
│       │   │   ├── quantum_memory.qentl
│       │   │   ├── quantum_process.qentl
│       │   │   ├── quantum_state_interrupt.qentl
│       │   │   ├── process_manager_*.qentl (3文件)
│       │   │   ├── memory_allocator.qentl
│       │   │   ├── memory_protection.qentl
│       │   │   ├── system_calls.qentl
│       │   │   ├── io_scheduler.qentl
│       │   │   ├── interrupt_handler.qentl
│       │   │   ├── ipc_manager.qentl
│       │   │   ├── device_framework.qentl
│       │   │   └── device_registry.qentl
│       │   └── services/        # 服务 (19文件)
│       └── VM/                  # 虚拟机 (15文件)
│           ├── bin/cli/         # CLI工具 (4文件)
│           └── src/core/        # 核心 (11文件)
│               ├── debug/       # 调试 (5文件)
│               ├── interpreter/ # 解释器 (2文件)
│               ├── memory/      # 内存管理 (1文件)
│               ├── os_interface/ # OS接口 (3文件)
│               └── quantum/     # 量子处理 (5文件)
│
├── src/                          # C源码 (72KB, 3文件)
│   ├── qnn_runner.c
│   ├── qvm_boot.c
│   └── yi_pipeline.c
│
├── tests/                        # 测试 (4KB, 1文件)
│   └── test_qbc.sh
│
├── tools/                        # 工具集 (132KB, 17文件)
│   ├── *.c                       # 11个C源文件
│   ├── analyze_jsonl             # 编译后的ELF二进制
│   ├── check_vocab               # 编译后的ELF二进制
│   ├── check_vocab2              # 编译后的ELF二进制
│   ├── count_yi_chars            # 编译后的ELF二进制
│   ├── debug_pipeline            # 编译后的ELF二进制
│   ├── test_extract              # 编译后的ELF二进制
│   ├── check_vocab.c             # 与check_vocab2.c功能重叠
│   ├── check_vocab2.c
│   ├── yi_dict_to_csv.py
│   └── yi_dict_to_word.py
│
└── web/                          # Web量子操作系统 (5.4MB, ~180文件)
    ├── index.html                # 主页
    ├── index.html.bak            # 备份文件
    ├── index-new.html            # 新版本
    ├── index-old.html            # 旧版本
    ├── styles.css                # 样式表
    ├── app.js                    # 主应用脚本
    ├── qsm-core.js               # 核心JS
    ├── quantum-*.js              # 量子相关JS (6文件)
    ├── desktop.html              # 桌面界面
    ├── quantum.html              # 量子界面
    ├── qvm.html                  # QVM界面
    ├── compiler.html             # 编译器界面
    ├── training.html             # 训练界面
    ├── translate.html            # 翻译界面
    ├── status.html               # 状态页面
    ├── api-docs*.html            # API文档 (2文件)
    ├── font-installer.html       # 字体安装器
    ├── v7_status.json            # 状态JSON
    ├── algorithm-stats-tracker.js
    ├── service-modes.js
    ├── trilingual-display.js
    ├── apps/                     # Web应用 (13个子应用)
    │   ├── assistant/
    │   ├── compiler/
    │   ├── economy/
    │   ├── files/
    │   ├── help/
    │   ├── monitor/
    │   ├── qentl-playground/
    │   ├── quantum-assistant/
    │   ├── qvm/
    │   ├── settings/
    │   ├── social/
    │   ├── store/
    │   └── terminal/
    ├── assets/
    │   ├── css/                  # 样式 (1文件)
    │   ├── fonts/                # 空目录
    │   ├── icons/                # 空目录
    │   └── js/                   # JS (4文件)
    ├── data/                     # 数据 (3文件)
    ├── docs/                     # 文档HTML (53文件) ★与docs/大量重复
    ├── downloads/                # 下载目录 (含8个空子目录)
    ├── fonts/                    # 字体 (3文件)
    ├── update/                   # 更新配置 (1文件)
    ├── yi-images/                # 彝文字形图片 (15文件)
    └── api/                      # Web API (4文件)
        ├── api_daemon.sh
        ├── quantum-api.html
        ├── quantum_yi_model.json
        └── __pycache__/          # Python缓存
```

---

## 二、各目录用途说明

| 目录 | 大小 | 文件数 | 用途 |
|------|------|--------|------|
| **api/** | 64KB | 12 | Python API层，提供量子计算和语言处理的RESTful接口 |
| **aurora/** | 36KB | 5 | Aurora引擎QEntL版，包含引擎核心、配置、内存加载器和微信推送 |
| **bin/** | 84KB | 5 | 编译产物目录，存放已编译的二进制文件和字节码 |
| **data/** | 325MB | 103 | 训练数据集，包含彝文词典PDF、91个JSONL训练文件、对照表等 |
| **docs/** | 2.4MB | 57 | 主开发文档库，含架构设计、示例、哲学、学习资源、项目状态等 |
| **Installer/** | 44KB | 6 | 安装器，包含引导程序C源码、安装脚本、批处理文件 |
| **memory_bank/** | 320KB | 74 | AI记忆库，按时间戳自动生成的架构/改进/学习/测试/训练快照 |
| **QEntL/** | 4.5MB | 212 | QEntL系统核心源码，含编译器、内核、虚拟机、模型定义 |
| **src/** | 72KB | 3 | C语言源码，对应bin/中的三个可执行文件 |
| **tests/** | 4KB | 1 | 测试脚本 |
| **tools/** | 132KB | 17 | 数据处理工具，含C源码和已编译的二进制 |
| **web/** | 5.4MB | ~180 | Web量子操作系统前端，含应用、文档HTML、样式、脚本 |

---

## 三、冗余文件清单

### 3.1 完全重复的文件 (MD5相同)

#### A. docs/ 与 QEntL/docs/ 之间的重复 (9个)
| 文件名 | docs/位置 | QEntL/docs/位置 |
|--------|-----------|-----------------|
| compiler_implementation_plan.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| vm_implementation_plan.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| installation_guide.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| qentl_ecosystem_plan.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| README.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| quantum_ecosystem_integration.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| QEntL_BUILD_PLAN.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| qentl_environment_design.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |
| syntax.md | docs/architecture/QEntL_docs/ | QEntL/docs/ |

#### B. docs/philosophy/ 与 QEntL/Models/*/docs/ 之间的重复 (4个)
| 文件名 | docs/位置 | QEntL/Models/位置 |
|--------|-----------|-------------------|
| qsm_implementation.qentl | docs/philosophy/ | QEntL/Models/QSM/docs/ |
| ref_implementation.qentl | docs/philosophy/ | QEntL/Models/Ref/docs/ |
| som_implementation.qentl | docs/philosophy/ | QEntL/Models/SOM/docs/ |
| weq_implementation.qentl | docs/philosophy/ | QEntL/Models/WeQ/docs/ |

#### C. Installer/ 与 docs/ 之间的重复 (1个)
| 文件名 | docs/位置 | Installer/位置 |
|--------|-----------|---------------|
| installation_guide.md | docs/architecture/QEntL_docs/ | Installer/docs/ |

#### D. QEntL/Models/QSM/docs/project_plan/ 内的重复
| 文件名 | QSM/位置 | SOM/或WeQ/位置 |
|--------|----------|----------------|
| som_construction_plan.qentl | QEntL/Models/QSM/docs/project_plan/ | QEntL/Models/SOM/docs/project_plan/ |
| weq_construction_plan.qentl | QEntL/Models/QSM/docs/project_plan/ | QEntL/Models/WeQ/docs/project_plan/ |

#### E. 编译器源码内部的部分重复
| 文件名 | 位置1 | 位置2 | 说明 |
|--------|-------|-------|------|
| quantum_gate_fusion.qentl | Compiler/src/backend/bytecode/optimizer/ | Compiler/src/backend/optimizer/ | 同名不同MD5，需检查内容差异 |
| debug_info_generator.qentl | Compiler/src/backend/debug/ | Compiler/src/backend/debug_info/ | 同名不同MD5，需检查内容差异 |
| dependency_analyzer.qentl | Compiler/src/utils/ | Kernel/filesystem/ | 同名不同MD5，跨模块复用 |
| incremental_builder.qentl | Compiler/src/backend/build/ | (无直接重复) | 与incremental_build_manager.qentl功能相近 |
| parallel_builder.qentl | Compiler/src/backend/build/ | (无直接重复) | 与parallel_build_manager.qentl/parallel_build_scheduler.qentl功能相近 |
| test_framework.qentl | Compiler/src/testing/ | (无直接重复) | 与unit_test_framework.qentl功能相近 |

### 3.2 文档→HTML转换重复 (53个)
docs/目录下的所有`.md`和`.qentl`文件都在`web/docs/`中有对应的`.html`副本。这些是自动生成的网页版本，保留一个来源即可。

### 3.3 备份/临时文件
| 文件 | 说明 |
|------|------|
| web/index.html.bak | 主页备份 |
| web/index-new.html | 新版本占位 |
| web/index-old.html | 旧版本占位 |
| web/tests/ 下18个文件 | 测试页面，与主web/功能重叠 |

### 3.4 空目录 (浪费inode)
| 目录 | 说明 |
|------|------|
| web/assets/fonts/ | 空 |
| web/assets/icons/ | 空 |
| Installer/support/ | 空 |
| web/downloads/os/iot/ | 空 |
| web/downloads/os/mobile/ | 空 |
| web/downloads/os/pc/ | 空 |
| web/downloads/updates/os/ | 空 |
| web/downloads/updates/vm/ | 空 |
| web/downloads/vm/linux/ | 空 |
| web/downloads/vm/macos/ | 空 |
| web/downloads/vm/windows/ | 空 |

### 3.5 工具重复
| 文件 | 说明 |
|------|------|
| tools/check_vocab / tools/check_vocab2 | 功能高度重叠 |
| tools/ 中6个ELF二进制 + 对应.c源码 | 二进制应通过构建产生，不应提交 |
| QEntL/scripts/Makefile | 与根目录Makefile重复 |

### 3.6 Git仓库冗余
| 项 | 说明 |
|----|------|
| 40个 tmp_pack_* 文件 | git gc未运行，占用大量空间 |
| .git/refs/original/refs/heads/master | filter-branch遗留 |
| 2个stash条目 | 旧stash未清理 |
| 分支: master, main, dev + 对应origin | 分支管理混乱 |

---

## 四、建议的清理方案

### Phase 1: 立即执行 (安全, 无损)

```bash
# 1. 清理空目录
find /root/QSM -not -path '*/.git/*' -type d -empty -delete

# 2. 删除备份/临时文件
rm /root/QSM/web/index.html.bak
rm /root/QSM/web/index-new.html
rm /root/QSM/web/index-old.html
rm -rf /root/QSM/web/tests/   # 与主web目录功能重叠

# 3. 清理Python缓存
rm -rf /root/QSM/web/api/__pycache__/

# 4. 删除工具编译产物 (保留.c源码, 按需重新编译)
rm /root/QSM/tools/analyze_jsonl /root/QSM/tools/check_vocab \
   /root/QSM/tools/check_vocab2 /root/QSM/tools/count_yi_chars \
   /root/QSM/tools/debug_pipeline /root/QSM/tools/test_extract

# 5. 删除重复的Makefile
rm /root/QSM/QEntL/scripts/Makefile
```

### Phase 2: 文档去重

**策略**: 以 `docs/` 为唯一权威来源，`QEntL/docs/` 中的重复文件改为符号链接或删除。

```bash
# 方案A: 删除QEntL/docs/中9个重复文件
# 方案B: 将QEntL/docs/下的重复文件替换为指向docs/的符号链接
# 方案C: 将docs/architecture/QEntL_docs/合并到QEntL/docs/，删除前者
```

**推荐方案C** — 统一文档结构：
```
docs/                    # 保留
├── architecture/        # 保留 (含QEntL_docs/)
├── core/                # 保留
├── ecosystem/           # 保留
├── examples/            # 保留
├── integration/         # 保留
├── learning/            # 保留
├── philosophy/          # 保留
├── project_state/       # 保留
├── MASTER_PLAN_COMPLETE.md
└── PROJECT_STRUCTURE.md

QEntL/docs/              # 简化后仅保留独有文件
├── deployment/README.md
├── development/README.md
└── architecture/README.md
```

### Phase 3: 哲学/模型实现去重

```bash
# 删除 QEntL/Models/*/docs/ 中的实现文件 (与docs/philosophy/重复)
rm /root/QSM/QEntL/Models/QSM/docs/qsm_implementation.qentl
rm /root/QSM/QEntL/Models/Ref/docs/ref_implementation.qentl
rm /root/QSM/QEntL/Models/SOM/docs/som_implementation.qentl
rm /root/QSM/QEntL/Models/WeQ/docs/weq_implementation.qentl
```

### Phase 4: 编译器源码整理

```bash
# 检查以下疑似重复文件的内容差异
diff /root/QSM/QEntL/System/Compiler/src/backend/bytecode/optimizer/quantum_gate_fusion.qentl \
     /root/QSM/QEntL/System/Compiler/src/backend/optimizer/quantum_gate_fusion.qentl

diff /root/QSM/QSM/QEntL/System/Compiler/src/backend/debug/debug_info_generator.qentl \
     /root/QSM/QEntL/System/Compiler/src/backend/debug_info/debug_info_generator.qentl

# 建议: 删除冗余子目录，统一结构
# - 删除 backend/optimizer/ (内容已在 bytecode/optimizer/)
# - 删除 backend/debug_info/ (内容已在 backend/debug/)
# - 合并 test_framework 与 unit_test_framework
# - 合并 incremental_builder 与 incremental_build_manager
# - 合并 parallel_builder 与 parallel_build_manager 与 parallel_build_scheduler
```

### Phase 5: API 版本合并

```bash
# api/v2/ 与 api/ 根目录存在功能重叠
# 建议: 评估 v2/ 下的3个文件是否仍在使用
# - 如果已弃用: rm -rf api/v2/
# - 如果仍需支持: 在api/下添加版本路由
```

### Phase 6: Git 仓库瘦身

```bash
cd /root/QSM

# 1. 运行垃圾回收
git gc --aggressive --prune=now

# 2. 清理未引用的pack文件
rm -f .git/objects/pack/tmp_pack_*

# 3. 清理filter-branch遗留
rm -rf .git/refs/original/

# 4. 清理stashes
git stash drop stash@{0}   # filter-branch产生的旧stash
git stash drop stash@{1}   # 旧WIP stash

# 5. 统一分支 (选择保留一个主分支)
# git branch -D master    # 如果main是主力
# git checkout main
# git push origin --delete master

# 预期结果: .git/ 从 5.9GB 降至 ~50-200MB
```

### Phase 7: 数据目录整理

```bash
# 彝文训练数据91个.jsonl文件建议按类别归档:
data/
├── dictionaries/           # 词典类
│   ├── 通用彝文字典_上册.pdf
│   ├── 通用彝文字典_下册.pdf
│   ├── 通用彝文字典.pdf
│   ├── 滇川黔桂彝文字典.pdf
│   └── ywly2通用彝文4120注释.pdf
├── corpora/                # 语料库
│   ├── yi_chat/            # 对话数据
│   ├── yi_grammar/         # 语法数据
│   ├── yi_translation/     # 翻译数据
│   └── yi_specialized/     # 专业领域数据
├── training/               # 训练集
│   ├── merged/             # 合并后的训练文件
│   └── raw/                # 原始数据
└── references/             # 参考材料
    ├── 彝文三语对照表.csv
    ├── 通用彝文对照表.xlsx
    └── 测试.xlsx

# 注意: 合并训练文件可减少91个文件为3-5个，节省大量inode
```

### 预期清理效果汇总

| 类别 | 可释放空间 | 可删除文件数 |
|------|-----------|-------------|
| 空目录+备份文件 | ~50KB | ~25 |
| Git临时pack+stashes | ~2-4GB | 40+pack |
| 工具ELF二进制 | ~200KB | 6 |
| 重复文档 (Phase 2-3) | ~1MB | 14 |
| 重复模型实现 | ~1MB | 4 |
| 重复Makefile | ~4KB | 1 |
| 编译器源码重复 | ~500KB | 6-10 |
| Python缓存 | ~10KB | 2 |
| **总计可释放** | **~2-4GB** | **~70+** |

---

## 五、建议的目录重构目标

```
QSM/                           # 项目根目录
├── .git/                      # 瘦身后 ~50-200MB
├── .gitignore
├── Makefile                   # 唯一构建入口
├── docs/                      # 唯一文档来源 (57文件)
│   ├── architecture/
│   ├── core/
│   ├── ecosystem/
│   ├── examples/
│   ├── integration/
│   ├── learning/
│   ├── philosophy/
│   └── project_state/
├── src/                       # C源码 (3文件)
├── api/                       # Python API (9文件, 删除v2/)
├── aurora/                    # Aurora引擎 (5文件)
├── bin/                       # 编译产物 (5文件)
├── tools/                     # 工具 (仅保留.c/.py源码)
├── tests/                     # 测试 (1文件)
├── data/                      # 训练数据 (325MB, 重新组织)
├── web/                       # Web前端 (~5MB)
│   ├── docs/                  # 由docs/自动生成
│   └── apps/                  # 13个子应用
├── QEntL/                     # 系统源码 (精简后)
│   ├── docs/                  # 仅保留独有文档
│   ├── scripts/               # 构建脚本 (删除重复Makefile)
│   ├── Models/                # 模型定义 (删除重复实现)
│   └── System/                # 编译器+内核+VM (去重后)
└── memory_bank/               # AI记忆库 (保留, 定期清理旧快照)
```
