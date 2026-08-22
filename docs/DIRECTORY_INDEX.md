# QEntL QLife 目录索引 (更新 2026-08-22 小趣WeQ)
# 核心规划: docs/QYI_TRAIN_PLAN.md (彝文训练三步走)

## 根 /root/QSM/QLife/
- qcl.qentl — QCL编译器
- qvm.qentl — QVM虚拟机
- bin/qvm_boot — 唯一启动器(compile+run)
- bin/q_bootstrap.bak — C种子备份(绝不再用)

## build/ 构建产物
- server_v14.qentl / server_v14.qbc — HTTP服务器(9802) 小趣聊天+QSCL识别 已部署
- yi_infer.sh — QSCL字形推理(纯bash)
- yi_recog_cp.sh — 码点→QSCL识别(cp2d查表+权重)
- corpus_gen.qentl — 语料生成器(纯QEntL骨架)

## qdfs/ns/data/ 数据
- yi_flat_b{0-7}.bin — 字形8×16像素(4120字 128维)
- yi_glyph_4120.data — 原始字形+码点
- cp2d.txt — 码点↔d映射(小趣聊天任意字识别用)
- yi_train_4120.data — 训练集

## qdfs/ns/models/ 权重
- qscl_b{0-7}_s{0-3}.w — QSCL识别器32份(8批×4态)
- (待) qscl_lm_s{0-3}.w — 语言生成模型4份(阶段C)

## qdfs/ns/corpus/ 语料库
- yi_seq.txt — SOV彝语句9600条(9000肯定+600过去+600否定)
- vocab_map.txt — 81索引↔码点映射

## web/ 桌面
- qdesktop.html — 量子桌面(17应用 已删字形识别app)

## docs/ 文档
- QYI_TRAIN_PLAN.md — 彝文训练三步走完整规划 ★★★
- PROJECT_STATUS.md / MASTER_PLAN.md / QSM_MASTER_PLAN.md

## skill
- qyi-model-training — 彝文训练规划(小趣专用记忆)