# QSM 训练数据质量报告
## 生成时间: 2026-06-28
## 数据目录: /root/QSM/data/

---

## 1. 数据概览

| 指标 | 数值 |
|------|------|
| `.jsonl` 文件总数 | **92 个** |
| 彝文相关 (`yi_*`) 文件 | 79 个 |
| 非彝文文件 | 13 个 |
| 总行数 | **122,521 行** |
| 目录总大小 | **325 MB** (含子目录) |
| `.jsonl` 文件总大小 | ~19.1 MB |
| 彝文字符覆盖 | **4120 / 4120 (100%)** |

### 主要数据文件（按行数排序）

| 文件名 | 行数 | 大小 | 格式 |
|--------|------|------|------|
| yi_gemma_training_merged.jsonl | 51,540 | 7.6 MB | messages |
| yi_detailed_descriptions_v3.jsonl | 12,368 | 2.0 MB | messages |
| yi_dense_training_v3.jsonl | 10,740 | 1.5 MB | messages |
| yi_char_trilingual_v3.jsonl | 7,711 | 1.1 MB | messages |
| yi_structured_v3.jsonl | 6,044 | 1.2 MB | messages |
| yi_direct_translation_v3.jsonl | 4,735 | 610 KB | messages |
| 滇川黔贵通用彝文三语对照表.jsonl | 4,120 | 1.4 MB | messages |
| 通用彝文彝汉对照训练表.jsonl | 4,120 | 700 KB | messages |
| 通用彝文汉彝对照训练表.jsonl | 4,120 | 700 KB | messages |
| yi_extended_training_v3.jsonl | 3,439 | 516 KB | messages |

---

## 2. 数据格式分析

### 2.1 字段格式分布

| 格式 | 记录数 | 占比 |
|------|--------|------|
| `messages` (role/content) | 121,627 | 99.3% |
| `input,output` | 468 | 0.4% |
| `input,output,zh` | 181 | 0.1% |
| `input,target` | 100 | 0.1% |
| 其他变体 | ~165 | 0.1% |

### 2.2 格式不统一问题

**严重问题**: 数据存在 3 种不同的 JSON 结构：
1. **`messages` 格式** (主流): `[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]`
2. **`user/assistant` 格式** (少数): `{user: "...", assistant: "..."}`
3. **结构化变体**: `{input, output, zh}` 等多字段格式

Pipeline 文档 `QEntL_Yi_Data_Pipeline.qentl` 假设使用 `json_obj["user"]` 和 `json_obj["assistant"]` 键名，但 **99.3% 的数据使用 `messages` 格式**。这意味着 pipeline 代码无法直接处理主流数据格式。

---

## 3. 重复性分析

### 3.1 跨文件重复（严重程度：🔴 高）

`yi_gemma_training_merged.jsonl` 是一个**聚合文件**，包含了绝大多数其他 `yi_*.jsonl` 文件的全部或部分数据：

| 文件 | 与 gemma 共享行数 | 占原文件比例 | 关系 |
|------|-------------------|-------------|------|
| yi_dense_training_v3.jsonl | 10,740 (100%) | **完全子集** | 冗余 |
| yi_dialog_expanded_v3.jsonl | 2,010 (100%) | **完全子集** | 冗余 |
| yi_extended_training_v3.jsonl | 3,236 (94%) | **几乎完全子集** | 冗余 |
| yi_grammar_formation_v3.jsonl | 518 (100%) | **完全子集** | 冗余 |
| yi_paragraph_v3.jsonl | 1,422 (100%) | **完全子集** | 冗余 |
| yi_proverbs_dialogue_v3.jsonl | 2,040 (100%) | **完全子集** | 冗余 |
| yi_direct_translation_v3.jsonl | 4,734 (100%) | **几乎完全子集** | 冗余 |
| yi_detailed_descriptions_v3.jsonl | 12,088 (98%) | **几乎完全子集** | 冗余 |
| yi_structured_v3.jsonl | 4,578 (76%) | **大部分重复** | 部分冗余 |
| yi_char_trilingual_v3.jsonl | 7,422 (96%) | **几乎完全子集** | 冗余 |
| yi_char_learning_v4.jsonl | 1,462 (97%) | **几乎完全子集** | 冗余 |
| yi_culture_science_v3.jsonl | 360 (71%) | **大部分重复** | 部分冗余 |
| yi_sentence_dialogue_expanded.jsonl | 930 (100%) | **几乎完全子集** | 冗余 |

**结论**: 总计约 **47,426 行** (占总数的 38.7%) 是跨文件重复数据。

### 3.2 文件内重复

| 文件 | 重复行数 | 重复率 |
|------|---------|--------|
| training_batch.jsonl | 83/100 | **83%** |
| yi_extended_training_v3.jsonl | 203/3,439 | 5.9% |
| yi_culture_science_v3.jsonl | 27/532 | 5.1% |

### 3.3 跨文件重复哈希统计

- 出现在多个文件中的唯一内容哈希：**51,895 个**
- 总唯一内容哈希：**~100,000 个**
- 重复率：**~52% 的内容在多个文件中出现**

---

## 4. 数据质量问题

### 4.1 内容过短/低质量

| 文件 | 平均内容长度 | 极短内容(<10字符) | 极短占比 |
|------|------------|-------------------|---------|
| yi_dialog_expanded_v3.jsonl | 7 chars | 2,006/2,010 | **99.8%** |
| yi_char_learning_v4.jsonl | 6 chars | 2,458/1,500* | **164%** (多message) |
| yi_dense_training_v3.jsonl | 12 chars | 14,988/10,740* | **139%** |
| yi_direct_translation_v3.jsonl | 13 chars | 4,774/4,735* | **101%** |
| yi_char_trilingual_v3.jsonl | 11 chars | 7,253/7,711* | **94%** |
| yi_gemma_training_merged.jsonl | 15 chars | 46,544/51,540* | **90%** |

*注：由于每条记录有 user+assistant 两条消息，内容计数可能超过行数。

**核心问题**: yi_gemma_training_merged.jsonl 中 **90% 的记录内容少于 10 个字符**，绝大多数是单字符问答（如"这个彝文是什么意思？"->"陷害"），缺乏上下文和多样性。

### 4.2 彝文字符分布不均

- **高频字符** (≥40次): 26 个字符出现 40-45 次
- **低频字符** (≤10次): 112 个字符仅出现 6-10 次
- **中频字符** (15-30次): 最多的一类 (~2,000+ 个字符)
- **覆盖率**: 4120 个字符全部出现在数据中 ✅
- **分布形态**: 右偏分布，大量字符出现次数极少

### 4.3 非彝文数据混杂

以下文件与彝文训练无关，属于噪音数据：
- `en_chat.jsonl` (155行): 纯英文对话
- `clean_english_v3.jsonl` (38行): 英文翻译
- `zh_chat_training.jsonl` (10行): 中文对话
- `all_chat.jsonl` (41行): 中英文混合闲聊
- `q_model_all_in_one.jsonl` (402行): 模型自我介绍
- `yi_general_chat.jsonl` (41行): 闲聊，含非标准彝文字符 (U+F222E, U+F2256)

### 4.4 彝文字符范围异常

- `yi_general_chat.jsonl`: 76 个字符超出标准 U+F2710-F3FFD 范围 (U+F222E, U+F2256, U+F2282)
- `q_model_all_in_one.jsonl`: 3 个全角 ASCII 字符 (U+FF71A, U+FFB53, U+FF71F)

### 4.5 解析错误

- `yi_grammar_extended.jsonl`: 1 条 JSON 解析错误

---

## 5. 三语对照表文件分析

三个中文命名的文件内容互补，无重复：

| 文件 | 行数 | 特点 |
|------|------|------|
| 滇川黔贵通用彝文三语对照表.jsonl | 4,120 | 彝文→中英对照，含metadata字段 |
| 通用彝文彝汉对照训练表.jsonl | 4,120 | 彝文→中文对照 |
| 通用彝文汉彝对照训练表.jsonl | 4,120 | 中文→彝文对照 |

三者各有 4,120 行，覆盖全部 4120 个字符，**相互无重复**，是高质量的基础数据。

---

## 6. 预处理建议

### 🔴 P0 - 必须处理（影响训练效果）

1. **去重 yi_gemma_training_merged.jsonl**
   - 该文件已包含 12 个其他文件的全部或大部分数据
   - 建议：删除 yi_gemma_training_merged.jsonl，改用去重后的合并方案
   - 预计减少 ~30,000 行重复数据

2. **统一数据格式**
   - Pipeline 期望 `user/assistant` 键，但 99.3% 数据使用 `messages` 格式
   - 建议：修改 pipeline 或编写格式转换脚本，将所有数据统一为 `messages` 格式

3. **过滤极短/低信息量记录**
   - yi_gemma_training_merged.jsonl 中 90% 记录内容 <10 字符
   - 建议：设置最小内容长度阈值（如 user+assistant 合计 ≥20 字符），或至少对单字符问答做抽样降权

### 🟡 P1 - 应该处理（提升数据质量）

4. **清理小文件噪音**
   - 以下文件内容过少（<100行），信息密度低，建议合并或删除：
     - yi_conversation.jsonl (2行), yi_grammar_extended.jsonl (16行), yi_health_v3.jsonl (8行)
     - 所有 10 行/18 行/20 行的 v3 文件

5. **移除非彝文训练文件**
   - en_chat.jsonl, clean_english_v3.jsonl, zh_chat_training.jsonl, all_chat.jsonl, q_model_all_in_one.jsonl
   - 这些文件不包含彝文字符，对彝文训练无贡献

6. **修复字符范围异常**
   - yi_general_chat.jsonl 中的 U+F222E/U+F2256 等非常规字符应检查是否为编码错误

7. **处理内部重复文件**
   - training_batch.jsonl 83% 的行是重复的
   - yi_extended_training_v3.jsonl 有 203 行内部重复

### 🟢 P2 - 可选优化

8. **平衡低频字符覆盖**
   - 112 个字符仅出现 6-10 次
   - 建议：对这些字符补充更多上下文示例，或在训练中对低频字符提高采样权重

9. **合并三语对照表**
   - 三个 4120 行的对照表可以合并为一个统一的三语数据集，便于 pipeline 处理

10. **数据分层策略**
    - 将数据分为：基础字符学习层（4120对照表）、词汇扩展层（结构化翻译）、对话应用层（长对话数据）
    - 不同层使用不同的采样比例进行训练

---

## 7. 推荐的数据清洗流程

```
原始数据 (92 files, 122,521 lines)
    │
    ├─ 1. 格式统一 → 全部转为 messages 格式
    │
    ├─ 2. 移除非彝文文件 → 删除 en_*, zh_*, all_chat, q_model 等
    │
    ├─ 3. 跨文件去重 → 基于内容哈希去重
    │         ├─ yi_gemma_training_merged 包含 12 个文件的子集
    │         └─ 保留唯一行，标记来源文件
    │
    ├─ 4. 文件内去重 → 删除 training_batch.jsonl 等内部重复
    │
    ├─ 5. 内容过滤 → 移除 <5 字符的无效记录
    │
    ├─ 6. 字符验证 → 过滤非标准彝文字符 (U+F2710-F3FFD)
    │
    └─ 7. 分层合并 → 基础层(4120对照) + 扩展层 + 对话层
```

预期结果：从 122,521 行 → 约 55,000-65,000 行唯一高质量彝文训练数据。
