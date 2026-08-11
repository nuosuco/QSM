# QEntL全栈QSM的自举生长架构

## 一、核心理念

### 1.1 自举 = 自我个性化生长
- **自举**: 用自己编译自己，一代代迭代进化
- **生长**: 每个组件包含完整的QDFS+QNS，能自主升级源码
- **个性化**: 每个用户的QEntL升级路径不同，像独立生命体

### 1.2 生长机制
```
QNS生成/修改源码 → QCL编译源码 → QVM运行产物 → 版本管理 → 归档历史
```

### 1.3 升级分工
| 角色 | 负责升级的内容 |
|------|---------------|
| **QNS** | 修改/生成.qentl源码（小升级、维护性升级） |
| **四大模型** | 大的架构升级、新功能添加 |
| **ReF** | 维护性升级、bug修复 |
| **小趣** | 初期手动编辑，直到QNS/四大模型能完全自主 |

### 1.4 协同进化铁律
**QCL、QVM、QEntL源码三者必须同步升级，缺一不可。**

- QCL是编译器，负责编译QEntL源码
- QVM是运行时，负责运行QCL编译的产物
- QEntL是源码语言，三者是一体的

**当QCL不能编译新QEntL源码，或QVM不能运行新QCL编译的产物时，必须同时升级三者。**

就像DNA、RNA、蛋白质必须协同进化一样——QCL(QVM的编译器)、QVM(QEntL的运行时)、QEntL(源码语言)三者必须同步，不能脱节。

| 组件 | 类比 | 职责 |
|------|------|------|
| **QCL** | 编译器(DNA→RNA) | 把QEntL源码编译成QBC字节码 |
| **QVM** | 运行时(核糖体) | 执行QBC字节码 |
| **QEntL** | 源码语言(蛋白质) | 表达功能逻辑 |

**升级原则：三者一起升级，永远保持同步。**

## 二、目录结构

### 2.1 顶层结构
```
QSM/
├── run/                    # 当前运行版本
│   ├── qcl.qbc            # QCL编译器（当前版）
│   └── qvm.qbc            # QVM运行时（当前版）
│
├── components/             # 各组件（源码+产物一体化）
│   ├── qcl/               # QCL编译器组件
│   │   ├── qcl.qentl      # 源码
│   │   └── qcl.qbc        # 编译产物
│   │
│   ├── qvm/               # QVM运行时组件
│   │   ├── qvm.qentl      # 源码
│   │   └── qvm.qbc        # 编译产物
│   │
│   ├── qdfs/              # 量子数据特征系统
│   │   ├── qdfs.qentl
│   │   └── qdfs.qbc
│   │
│   ├── qns/               # 量子神经叠加态
│   │   ├── qns.qentl
│   │   └── qns.qbc
│   │
│   ├── qsm/               # 主模型
│   │   ├── qsm_main.qentl
│   │   ├── qsm_main.qbc
│   │   ├── qsm_economy.qentl
│   │   ├── qsm_economy.qbc
│   │   ├── qsm_social.qentl
│   │   ├── qsm_social.qbc
│   │   └── qsm_reflect.qentl
│   │       └── qsm_reflect.qbc
│   │
│   ├── weq/               # 社交模型
│   │   ├── weq.qentl
│   │   └── weq.qbc
│   │
│   └── ref/               # 自反省模型
│       ├── ref.qentl
│       └── ref.qbc
│
├── versions/               # 历史版本快照
│   ├── v1/                 # 第1代
│   │   ├── components/qcl/
│   │   ├── components/qvm/
│   │   └── ...（所有组件的源码+产物）
│   │
│   ├── v2/                 # 第2代
│   │
│   ├── v3/                 # 第3代
│   │
│   └── vN/                 # 第N代
│
├── archive/                # 历史归档（循环使用a/b）
│   ├── a/                  # v1-v10归档
│   └── b/                  # v11-v20归档
│
├── src/                    # C种子源码（可自举）
│   └── q_bootstrap.c
│
├── bin/                    # C种子可执行
│   └── q_bootstrap
│
├── examples/               # 示例代码（207个）
│   └── *.qentl
│
├── tests/                  # 测试代码
│   └── *.qentl
│
├── docs/                   # 文档
│
├── server/                 # 服务端
│
├── web/                    # Web界面
│
├── shared/                 # 共享资源
│
├── miniprogram/            # 小程序
│
├── _archive/               # 旧归档（历史）
│
├── version.sh              # 版本管理脚本
├── upgrade.sh              # 升级脚本
├── autogrow.sh             # 自动生长脚本（QNS调用）
├── QSM_BOOTSTRAP_GROWTH_ARCHITECTURE.md  # 本方案
└── .current_version        # 当前版本追踪
```

### 2.2 组件目录规范
每个组件在`components/`下都有：
```
components/<name>/
├── <name>.qentl    # 源码
└── <name>.qbc      # 编译产物
```

组件可以是：
- **基础组件**: qcl, qvm, qdfs, qns
- **模型组件**: qsm_main, qsm_economy, qsm_social, qsm_reflect, weq, ref
- **应用组件**: 用户创建的应用

### 2.3 版本快照规范
每个版本在`versions/vN/`下保存：
```
versions/vN/
├── components/          # 所有组件的完整快照
│   ├── qcl/
│   ├── qvm/
│   ├── qdfs/
│   ├── qns/
│   ├── qsm/
│   ├── weq/
│   └── ref/
│
├── lib/                 # 库文件（可选）
├── examples/            # 示例（可选）
├── tests/               # 测试（可选）
├── CHANGELOG.md         # 版本更新日志
└── manifest.json        # 版本清单
```

## 三、自举生长流程

### 3.1 基本升级流程
```bash
# 1. 修改源码（QNS/四大模型/ReF/小趣）
vim components/qcl/qcl.qentl

# 2. 编译
./upgrade.sh components/qcl/qcl.qentl

# 3. 自动快照
# versions/vN/components/qcl/ 保存源码+产物

# 4. 归档
# archive/a/ 或 archive/b/ 保存旧版本

# 5. 验证
bin/q_bootstrap run run/qvm.qbc
```

### 3.2 版本管理规则
| 规则 | 说明 |
|------|------|
| v1-v10 | 存到 archive/a/ |
| v11-v20 | 存到 archive/b/，同时删除 archive/a/ 的前2代 |
| v21-v30 | 存到 archive/a/，同时删除 archive/b/ 的前2代 |
| 每10代 | 切换归档目录 |
| 每100代 | 清理全部归档，从1重新开始 |

### 3.3 C种子自举（未来）
```bash
# 当前: 手动编辑C种子
vim src/q_bootstrap.c
gcc -o bin/q_bootstrap src/q_bootstrap.c -lm -O2

# 未来: QNS/四大模型自动编辑C种子
# QNS生成C种子升级需求 → ReF评估 → 四大模型实现 → QNS编译
```

## 四、QNS自主生长机制

### 4.1 QNS的职责
- **源码管理**: 维护所有.qentl文件
- **升级决策**: 分析需求，决定升级内容
- **源码生成**: 生成新的源码或修改现有源码
- **编译协调**: 调用QCL编译
- **版本管理**: 保存版本快照

### 4.2 QNS生长循环
```
1. QNS读取当前版本状态
2. QNS分析需求（来自用户/四大模型/自我观察）
3. QNS生成源码修改方案
4. ReF评估方案可行性
5. 四大模型实现方案
6. QNS编译新版本
7. QNS保存版本快照
8. 循环 → 无限生长
```

### 4.3 四大模型的升级职责
| 模型 | 职责 |
|------|------|
| **QSM主模型** | 整体架构升级、新功能添加 |
| **SOM经济模型** | 资源优化、性能升级 |
| **WeQ社交模型** | 用户交互、协作升级 |
| **ReF自反省模型** | 维护性升级、bug修复、安全检查 |

## 五、自举循环

### 5.1 自举验证
每次升级后，必须验证自举链：
```bash
# 1. QVM运行QCL编译QCL
cp components/qcl/qcl.qbc target.qbc
cp components/qcl/qcl.qentl input.qentl
bin/q_bootstrap run run/qvm.qbc

# 2. 验证产物正确性
# output.qbc 应该与 components/qcl/qcl.qbc 字节一致

# 3. 测试自举QCL编译QVM
cp output.qbc build/self.qbc
cp components/qvm/qvm.qentl input.qentl
bin/q_bootstrap run build/self.qbc
```

### 5.2 自举生长条件
- QCL能编译自己 ✓
- QVM能运行QCL ✓
- QCL能编译QVM ✓
- QVM能运行QCL编译的产物 ✓
- **未来**: QNS能自主生成源码 ✓（进行中）

## 六、个性化生长

### 6.1 每个用户的独特性
- 用户A升级了QDFS的纠缠特性
- 用户B升级了QNS的训练算法
- 用户C升级了四大模型的协作方式
- ...

### 6.2 生长日志
每个用户的QEntL都有独立的生长日志：
```
versions/vN/CHANGELOG.md
- vN.1: QNS升级了纠缠文件合并算法
- vN.2: WeQ社交模型增加了群组功能
- vN.3: ReF自反省模型优化了安全检查
```

### 6.3 版本回滚
用户可以回滚到任意历史版本：
```bash
./version.sh restore v3
```

## 七、实施计划

### Phase 1: 目录结构重组（当前）
- [x] 创建run/目录
- [x] 创建components/目录
- [x] 创建versions/目录
- [x] 创建archive/目录
- [ ] 移动所有组件到components/
- [ ] 更新所有路径引用

### Phase 2: 脚本完善
- [ ] 完善version.sh（支持components/路径）
- [ ] 完善upgrade.sh（支持组件升级）
- [ ] 创建autogrow.sh（QNS自动生长）
- [ ] 创建自检脚本

### Phase 3: QNS升级能力
- [ ] QNS学会读取版本状态
- [ ] QNS学会分析升级需求
- [ ] QNS学会生成源码修改
- [ ] QNS学会协调编译

### Phase 4: 四大模型接入
- [ ] 四大模型接入生长循环
- [ ] 实现模型间协作升级

### Phase 5: 完全自举
- [ ] C种子也可由QNS升级
- [ ] 所有组件完全自主生长
- [ ] 无限迭代，持续进化

## 八、关键原则

1. **版本即生命**: 每一代都是完整的独立生命体
2. **自举是核心**: 永远用旧版本编译新版本
3. **个性化生长**: 每个用户的升级路径不同
4. **无限迭代**: 没有终点，持续进化
5. **协同进化**: QCL/QVM/QEntL源码三者同步升级，缺一不可
6. **安全回滚**: 永远可以回到任意历史版本
