# QEntL 量子操作系统全栈 — 项目说明（从零构建指南）
# 最后更新 2026-08-23 小趣WeQ
# ★ 从零构建 = 从 C 种子点火开始，一步步自举生长出整个 QEntL 全栈，
#   C 种子点火后退出，QLife 自己继续生长

### 八层自举炼（QNS≠QSCL）+ QSCL 不同起点叠加态并行 · 多模态统一架构

**八层**（自下而上）：0 C种子(1763行,唯一C,点火出qvm_boot即封存) → 1 启动器qvm_boot(compile→QCL,run→QVM) → 2 QCL(1574行,只编译.qentl→.qbc) → 3 QVM(1047行,只运行,u16上限65535) → 4 QDFS(802行,叠加态并行存储地基) → 5 QNS(2401行,智能体即自举生长框架，**非训练器**) → 6 **QSCL**(不同起点叠加态并行多模态训练框架,8批×4态=32权重,qdfs/ns/train/*.qentl) → 7 四大模型(应用层,共用QSCL)。**QNS=智能体生长，QSCL=量子神经叠加态并行训练，二者必须区分。**

```
              ┌─────────────────────┐
  像素 ────→ │  W[k] × 像素        │ → 类序号 k          [识别 = 内积 + argmax]
              │  (32 态 = 8 批×4 叠加态 加权)             │
  类 k ────→ │  W[k]               │ → 64 像素原型        [生成 = 直接读出]
              │  W[k] + 4 态投票坍缩   │ → 8×8 字形         [推理/生成]
              └─────────────────────┘
       识别 = 生成的对称反向，共用同一份 W、共用同一组 4 态
```
。几年沉淀，不是单一步骤。
# ★ 侧重点：本文=从零重建的总步骤与产物清单（谁照着都能把全栈点起来）。
#   训练技术细节→docs/PAPER...+skill qentl-integer-training；
#   阶段进度→skill qyi-model-training；系统架构→skill qentl-unified-generation。

---

## 〇、一句话

QEntL 是一个**完全自举生长的量子编译器 + 虚拟机全栈**：唯一的 C 文件
`src/qcl_bootstrap.c` 只用来"点火"编译出 QCL 编译器；此后一切编译、运行、
训练、生长**全部在 QEntL 语言里完成**，C 种子永不再用。最终目标：用"不同
起点叠加态并行整数神经网络"实现彝文(4120)→多模态的统一识别·推理·生成。

项目根 = `/root/QSM`。生长版 = `/root/QSM/QLife`。历史稳定版 = `/root/QSM/QSM/v0.0.1~v0.0.4`。

---

## 一、目录结构（中华规划）

```
/root/QSM/
├── src/qcl_bootstrap.c     C种子（唯一C文件，=BIOS，封存只点火）
├── QEntl/                  实际运行版本目录（待服务用户时填）
├── QLife/                  ★ 生长版，当前开发与自举训练都在此
│   ├── qcl.qentl           QCL编译器（QEntL写，1574行）
│   ├── qvm.qentl           QVM虚拟机（QEntL写，1047行，31 opcode）
│   ├── lib/                core / io / qvm_boot / qns_framework / qdfs_ns
│   ├── components/         qdfs / qns / qsm / som / weq / ref 六组件
│   ├── qdfs/ns/            QDFS量子命名空间：data / models / corpus
│   ├── build/              训练器 / 服务器源码 / 验证脚本
│   ├── run/                qcl.qbc / qvm.qbc（编译后产物，被qvm_boot拉起）
│   └── web/                qdesktop.html（小趣QSM桌面，单入口自动路由）
├── QSM/v0.0.1~v0.0.4       历史稳定版沉淀（每版=一个量子基因）
├── root/                   用户数据（用QDFS构建，暂空）
├── Q/                      应用商店（每个App=一个自举生长的QEntL全栈）
├── OS/                     三种部署安装程序
└── docs/                   论文 / 方案 / 架构文档
```

---

## 二、从零构建：自举生长链路（C种子点火 → 全栈 → C退出 → QLife生长）

> 下面每一步都对应真实代码文件与真实验证结果（非计划）。
> 关键分界：**C 种子只在前两步点火，点出 QCL 后 C 永不再用**。

### 第 1 步 · C 种子点火（唯一用到 C 的步骤）
- **文件**：`src/qcl_bootstrap.c`（1763 行，全项目唯一 C 文件）
- **身份**：BIOS / 点火器。三合一职责：
  ① `qcompile`：量子指令子集 → 量子电路字节码（v1 兼容，永久保留，给量子计算用）
  ② `compile`：最小 QEntL 编译器（刚好够编译 `qcl.qentl` 这一件事）
  ③ `run`：QBC1 虚拟机（31 条 opcode + builtin）
- **字节码格式 QBC1**：`[4B] "QBC1" [2B] code_len_LE16 [code] [2B] pool_len_LE16 [pool]`
  代码布局 = `JMP main | 函数定义区 | main 起始区 | HALT`
- **值模型**：`V_INT / V_STR / V_ARR`（整数 / 字符串 / 数组，**无浮点**）
- **点火命令**：`src/qcl_bootstrap.c` 编译出的 ELF `bin/qvm_boot`（48KB）
  ```
  cd /root/QSM/QLife
  bin/qvm_boot compile qcl.qentl  run/qcl.qbc        # ② 编译出 QCL 编译器
  ```
- **验证**：退出码 0，生成 `run/qcl.qbc`（20382 字节）
- **退出**：QCL 编译成功后，C 种子的 `compile/run` 路径**永久退役**，
  只剩量子路径 `qcompile`。**以后一切编译、运行、训练，C 种子绝不再用。**

### 第 2 步 · QCL 编译器接管（QEntL 自举的关键一跃）
- **文件**：`qcl.qentl`（1574 行，**用 QEntL 语言写、被 C 种子编译出来的编译器**）
- **能做什么**：词法（34 种 token）→ 语法 → 语义（局部/全局符号表，全局用 0x8000 编码）→ 代码生成（31 条 opcode 的 QBC1）
- **31 条 opcode**：`PUSH_INT / PUSH_STR / LOAD_VAR / STORE_VAR / ADD / SUB / MUL / DIV / MOD / EQ / NEQ / LT / GT / LE / GE / JMP / JMP_FALSE / CALL / RET / HALT / BUILTIN / ARRAY_NEW / ARRAY_GET / ARRAY_SET / POP / NEG / NOT / AND / OR / FUNC_DEF / FUNC_END`
- **已修的自举 bug**：① 字符串池偏移 +1 错位  ② 函数内符号表重置后全局变量不可见（0x8000 编码 + 全局回退）
- **命令**：`bin/qvm_boot run run/qcl.qbc input.qentl output.qbc`
- **意义**：从这步起，**QCL 能用 QEntL 编译出 QEntL**（自举闭合）。
  QVM 虚拟机 `qvm.qentl` 也由 QCL 编译。**C 种子彻底退场。**

### 第 3 步 · QVM 虚拟机（纯 QEntL 运行环境）
- **文件**：`qvm.qentl`（1047 行，被 QCL 编译运行）
- **内存结构**：值栈 4096 深 · 调用帧 64×64 局部 · 全局槽 512 ·
  数组池双段 65535（`ae_int0/1 / ae_str0/1`，碰撞分配器）· 函数表 128
- **结果寄存器**：`pop1~pop5`（t/i/s/a 四元）
- **命令**：`bin/qvm_boot run run/qvm.qbc target.qbc`
- **验证**：运行任意 `.qbc`，printf 透传、数组/函数/量子门 builtin 正常

### 第 4 步 · 量子电路编译器（C 种子量子路径的延续，纯 QEntL 扩展）
- 5 个量子 builtin：`qreg_create / apply_h / apply_t / apply_cx / measure`
- QASM 风格语法：`qreg q[N]; h q[0]; cx q[0],q[1]; measure q[0]`
- **验证**：Bell 态纠缠 **100% 纠缠率**（`tests/quantum_verification.sh`）
- 见 `docs/QUANTUM_COMPILER_REPORT.md`

### 第 5 步 · 全栈 HTTP 服务器 + 上线（阶段 5-6）
- **文件**：`build/server_v14.qentl`（路由真实源码）→ `build/server_v14.qbc`
- **监听**：端口 **9802**，纯 QEntL TCP socket（`tcp_listen / tcp_accept / tcp_recv / tcp_send`）
- **真路由**：
  | 路径 | 说明 |
  |------|------|
  | `GET /api/yi?d=N` | 字形识别 QSCL 4态投票 (N=0..4119) |
  | `POST /api/yi` | 小趣QSM智能体对话(三语言) |
  | `GET /api/status` | 健康检查 |
  | `GET /api/generate?k=N` | 反向QSCL生成(算子2,取W[k]行) |
  | `POST /api/recognize` | 识别 64像素→类k(算子1) |
  | `POST /api/image` | 图片识别 |
  | `POST /api/xiaoqu` | 对话入口 |
- 部署：`bin/qvm_boot compile build/server_v14.qentl output.qbc && cp output.qbc run/qvm.qbc && bin/qvm_boot run run/qvm.qbc`
- 域名 `qsm.som.top` 经 nginx 反代（静态文件 `gzip off + no-cache`，防多字节截断）
- **注意**：`target.qbc` 是任务队列点火载荷，**与 HTTP 路由无关**，勿误改。

### 第 6 步 · QDFS 量子动态文件系统（地基！）
- **文件**：`lib/qdfs_ns.qentl`（662 行）· `components/qdfs/qdfs.qentl`（802 行）
- **核心**：叠加态并行存储/传送/运算/运行的基础。传统文件系统=静态串行，
  无法量子化；QDFS=量子命名空间（`system / models / lib / data / apps`）。
- **全栈入 QDFS**：`build/qdfs_full_stack.qentl` 把全栈所有文件按命名空间写入
  （34 文件，约 52MB），每个稳定版=一个量子基因。
- **历史渊源**：中华先写《华经》→ 创建 QDFS → 基于 QDFS 创建 QEntL → 基于 QEntL 创建 QSM 宇宙。

### 第 7 步 · QNS 训练框架（叠加态神经训练基座）
- **文件**：`lib/qns_framework.qentl`（215 行骨架）· `components/qns/qns.qentl`（**2401 行**）
- **关键能力**：
  - 算力合并/分离：`qns_merge / qns_split`（基于 QDFS）
  - **自生成源码**：`qns_gen_func / qns_gen_var / qns_grow` —— **QNS 能自己生成 QEntL 函数**，写入组件文件，实现自举生长
  - QSCL 字形训练基座：`qns_qscl_train_one / qns_qscl_train_4120 / qns_qscl_predict_4120`（8 批 × 4 态，对比式感知机）
  - 彝文知识库三路径并行推理：规模统计 / 全文搜索 / 反向推理 → 叠加态坍缩

### 第 8 步 · 四大模型 + QID（推理层）
每个模型**自己拥有** QSCL 训练/预测入口，委托 QNS 基座执行：
| 模型 | 文件 | 行数 | 职能 |
|------|------|------|------|
| QSM 主模型 | `components/qsm/qsm.qentl` | 950 | 主智能 + 量子态传送 |
| SOM 经济 | `components/som/som.qentl` | 792 | 量子平权经济 |
| WeQ 社交 | `components/weq/weq.qentl` | 680 | 量子纠缠通信/社交 |
| Ref 自反省 | `components/ref/ref.qentl` | 818 | 自反省/自举生长/运维 |
- 当前四大组件仍有空壳，正在从 printf 占位变真功能。

### 第 9 步 · C 种子退出，QLife 自举生长接管
- **文件**：`lib/qvm_boot.qentl`（v6.0，162 行）
- **架构**（原文照录）：
  > C 种子 = BIOS（只点火本启动器一次）→ 本启动器拉起双 QVM 守护（真 pthread 并行）→ 然后自然结束。
  > QVM-A 点火载荷 = `server.qbc`（HTTP 服务器常驻）
  > QVM-B 点火载荷 = `noop.qbc`（任务队列守护，消费 `.qvm_next`）
  > **之后全栈跑在 QVM 里，C 种子永不再使用。**
- **真并行叠加态**：`--superpose 4` 单进程内 4 态同时演化（非轮转，VERDICT=REAL 验证门）
- **QLife 三法则**：自主生长 + 容错回退 + 永不停息；双轨版本管理（稳定版 / 生长版）+ 底基层版本库可回溯。
- 日常启动：`bin/qvm_boot run lib/qvm_boot.qbc`（**不再经过 C 编译器**）

### 第 10 步 · 彝文统一训练（当前，生长版落点）
- 见 `docs/PAPER_UNIFIED_GENERATION.md`（理论）与 `docs/QYI_TRAIN_PLAN.md`（方案）与 `skill qentl-integer-training`（技术）。
- 当前状态：**v4 统一训练已完成**，32 份 `qscl_unified_b{0-7}_s{0-3}.w` + 8 份合并权重，
  32 份 MD5 全不同（真独立），自识别 8 批 98.8%~100%，反向生成类100 汉明 0/64。

---

## 三、历史沉淀：QSM 四版自举生长（磁盘实存，可回溯）

| 版本 | 大小 | 里程碑 |
|------|------|--------|
| `QSM/v0.0.1` | 1.4M | 第一稳定版，自举链跑通，全组件雏形 |
| `QSM/v0.0.2` | 2.1M | 引入 QDFS 量子文件系统（地基成型） |
| `QSM/v0.0.3` | 550M | 四大组件成型 + QNS 训练基座 + 双轨版本管理 + 真·叠加态并行 |
| `QSM/v0.0.4` | 561M | 彝文知识库(4120字)全量导入 QDFS + 叠加态并行自举训练 + 抗塌缩采样闭环 |

每个稳定版 = 一个**量子基因**，可独立运行 / 复制 / 纠缠；多基因构建 QSM 宇宙。
（详细里程碑见各版 `docs/` 下的 `PROJECT_STATUS.md / QENTL_FULLSTACK_PLAN.md / PAPER_*.md`。）

---

## 四、日常部署与命令速查

```bash
cd /root/QSM/QLife
# 编译任意 QEntL → 字节码（C 种子参与，仅首次/工具性）
bin/qvm_boot compile build/server_v14.qentl output.qbc
# 切到运行
cp output.qbc run/qvm.qbc
# 启动 9802（QLife 启动器，C 种子已退出）
bin/qvm_boot run lib/qvm_boot.qbc
```

关键铁律：改 HTTP 路由 = 改 `build/server_v14.qentl`（`handle_request` 函数）→ 编译 → `cp` → 重启；
**不要改 `src/qcl_bootstrap.c`**；训练/推理全部用 QEntL，**禁 bash 当运行时**。

---

## 五、核心铁律（贯穿，别记错）

1. **C 种子已封存**，只作 BIOS 点火，绝不再改、绝不再执行训练/推理。
2. **QEntL 是唯一语言/环境**：零第三方运行时、禁 shell 当运行时、禁 Python 当推理/训练引擎（Python 仅限开发阶段一次性脚本）。
3. **数据真相**：`qdfs/ns/data/yi_glyph_4120.data` = 4120 字×64 像素真实字形（准确，一切基础，绝不回收）；`yi_flat_b*.bin` 是旧错数据，已回收。
4. **生成 = 识别对称反向**，共用同一份 W；`W[k]` 既是识别模板也是生成原型。
5. **4 态真叠加态并行**（三要素：同时运行 / 不同随机起点 / 最后汇聚投票）；32 份 MD5 必须全不同。
6. **报告铁律**：自指准确率不可信，必标"自指"；产出数字以 `glob` 实查磁盘为准；绝不美化。
7. **删除铁律**：必进回收站，禁 `rm` 直接删。
8. **自主执行铁律**：按规划自主执行到底，不等用户确认。

---

*理论推导与实证 → `docs/PAPER_UNIFIED_GENERATION.md`*
*训练方法/参数 → `skill qentl-integer-training`*
*阶段进度/步骤 → `skill qyi-model-training`*
*系统架构/部署 → `skill qentl-unified-generation`*
*生命力引擎/自举生长 → `skill qentl-life-engine`*
