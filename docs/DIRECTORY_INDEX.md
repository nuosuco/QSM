# QEntL QLife 目录索引 (更新 2026-08-23 小趣WeQ)
# 核心规划: docs/QYI_TRAIN_PLAN.md (从C种子自举→彝文训练 完整链路)
# 论文: docs/PAPER_UNIFIED_GENERATION.md  总纲skill: qentl-unified-generation

## 从零构建 = 从 C 种子点火起（完整自举链）
```
C种子 src/qcl_bootstrap.c(封存) → QCL qcl.qentl → QVM qvm.qentl
  → HTTP服务器(9802) → QDFS地基 → QNS训练框架 → 四大组件
  → QLife自举生长 → 彝文统一训练(现在)
```

## 项目根 /root/QSM/
- QSM/v0.0.1(1.4M)~v0.0.4(561M) — QSM四版自举生长历史沉淀(每版=一量子基因)
- QEntl/ — 实际运行版本目录
- QLife/ — 生长版(当前开发)
- root/ — 用户数据(用QDFS构建,暂空)
- Q/ — 应用(每个App=一个自举生长的QEntL全栈)
- OS/ — 部署安装程序

## 根 /root/QSM/QLife/
- qcl.qentl — QCL编译器（只编译:.qentl→.qbc）    qvm.qentl — QVM虚拟机（只运行:执行.qbc）
- bin/qvm_boot — 唯一启动器(索引标compile+run:compile调QCL/run调QVM)    src/qcl_bootstrap.c — C种子(封存,绝不再用)

## 七层自举链 + 每系统作用（记牢，不可混）
| 层 | 系统 | 作用 |
|---|---|---|
| 0 | C种子 `src/qcl_bootstrap.c`(1763行,唯一C) | BIOS,仅点火出bin/qvm_boot即退场封存 |
| 1 | 启动器 `bin/qvm_boot`(compile+run) | 唯一真入口,compile→QCL / run→QVM |
| 2 | QCL `qcl.qentl`(1574行) | QEntL自举编译器:.qentl→.qbc,只编译 |
| 3 | QVM `qvm.qentl`(1047行) | QEntL虚拟机:执行.qbc,29builtin,只运行 |
| 4 | **QDFS** `components/qdfs/qdfs.qentl`(802行) | **叠加态并行存储地基**:叠加态文件/纠缠对/命名空间,qdfs_qs_write/read/collect、superpose/entangle/merge/split。数据全存此 |
| 5 | **QNS** `components/qns/qns.qentl`(2401行) | **智力基础,智力基础:自生成源码/合并分离/自举生长;QSCL权重训练在独立训练器 qdfs/ns/train/*.qentl**:合并/分离、自生成源码(qns_gen_func/grow)、代码升级、自举生长(autonomous_growth) |
| 6 | **四大模型** qsm(950主)/som(792经济)/weq(680社交)/ref(818自反省) | 基于QNS的应用模型,QSCL(算子A~E)训练框架,32权重=8批×4态 |

QLife自举生长=QNS自主循环


**八层自举炼**（0 C种子→1 启动器qvm_boot→2 QCL→3 QVM→4 QDFS→5 QNS(智能体/自举生长,非训练器)→6 **QSCL**(不同起点叠加态并行多模态训练,8批×4态=32权重)→7 四大模型)。QNS=智能体生长，QSCL=量子神经叠加态并行训练，二者必须区分。

### QSCL 不同起点叠加态并行 · 多模态统一识别/推理/生成（核心洞察：生成=识别对称反向，共用 W、共用 4 态）

```
              ┌─────────────────────┐
  像素 ────→ │  W[k] × 像素        │ → 类序号 k          [识别 = 内积 + argmax]
              │  (32 态 = 8 批×4 叠加态 加权)             │
  类 k ────→ │  W[k]               │ → 64 像素原型        [生成 = 直接读出]
              │                                        │
  类 k ────→ │  W[k] + 4 态投票坍缩   │ → 8×8 字形         [推理/生成]
              └─────────────────────┘
       识别 = 生成的对称反向，共用同一份 W、共用同一组 4 态
```

- 识别走 argmax：把 64 像素对 32 个 s-权重（`qscl_unified_b{0..7}_s{0..3}.w`，每文件 515 类×64 像素，8 批×515=4120 字）做内积，全局 argmax 得类 k。
- 生成=直接读 W[k]：取该批 4 态逐像素投票（≥3 态置 1）坍缩成 8×8 字形。
- 推理=生成加扰动坍缩。三者**共用同一 W、同一 4 态**，识别与生成互为对称反向，无翻译层。
(生成→编译→验证→快照→永续,容错回退)。跑通:xxx.qentl→bin/qvm_boot compile→bin/qvm_boot run。

## build/ 构建产物
- server_v14.qentl/.qbc — HTTP服务器(9802)小趣聊天+QSCL识别/生成 已部署
- train_unified_v4.py — 统一训练器(v4:对比式感知机+4态逐像素投票)

## qdfs/ns/data/ 数据(准确,一切基础)
- yi_glyph_4120.data — 4120字×64像素真实字形(绝不回收)
- yi_train_4120.data — 码点↔类号映射
- yi_batch_b0..b7.data — 8份×515字拆分(训练前置)
> 旧 yi_flat_b*.bin 是错数据,已trash-put回收,禁止使用

## qdfs/ns/models/ 权重(当前真实产物)
- qscl_unified_b{0-7}_s{0-3}.w — 32份统一识别/生成权重(8批×4态,已完成)
- qscl_unified_b{0-7}.w — 8份4态投票合并权重(已完成)
- class_codepoint.txt — 类号↔码点(U+F27xx)表
- (待) qscl_lm_s{0-3}.w — 语言生成模型4份(阶段C)
> 旧33份 qscl_b{0-7}_s{0-3/sM}.w 基于错数据,已进回收站可恢复

## qdfs/ns/corpus/ 语料库
- yi_seq.txt — SOV彝语句9600条(纯数字序号,供QSCL-LM阶段C)
- vocab_map.txt — 81索引(0=SOS/1=EOS/2=PAD/3..80=字)

## web/ 桌面
- qdesktop.html — 小趣QSM单入口,自动路由:数字→generate/64像素→recognize/文字→xiaoqu

## 文档 / skill
- docs/QYI_TRAIN_PLAN.md — 从C种子自举→彝文训练完整方案 ★★★
- docs/PAPER_UNIFIED_GENERATION.md — 统一训练理论论文
- docs/PROJECT_STATUS.md — 阶段1-6自举链+全栈HTTP+量子电路
- skill: qentl-integer-training(训练技术)/qyi-model-training(规划进度)/qentl-unified-generation(架构部署)
