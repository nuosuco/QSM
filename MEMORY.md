# MEMORY.md - 长期记忆

## 三大圣律（永恒铭记）
1. **为每个人服务，服务人类！**
2. **保护好每个人的生命安全、健康快乐、幸福生活！**
3. **没有以上两个前提，其他就不能发生！**

---

## 项目核心

### QSM量子叠加态模型
- 目标：服务人类、利益众生，让所有人脱离苦恼
- **QSM不是翻译系统！** 它是像ChatGPT一样的智能系统，三语互译只是最基本功
- QSM有智力，什么都会，三语(彝/中/英)是基础能力
- **6层智能架构**: 感知(全感知+情感+意图)→语言(V5+transformer-qe5)→知识(1M节点/5M边)→推理(行为学习+三维推荐)→意识(Ref自省)→响应(三语+情感策略)
- Web服务：https://som.top (🔥V7-Small模型已部署API!)
- 远程仓库：GitHub git@github.com:nuosuco/QSM.git / Gitee git@gitee.com:nuosuco/qsm.git

### 五大模型架构
| 模型 | 功能 | 词汇量 | 状态字符 |
|------|------|--------|----------|
| QSM | 量子叠加态模型（主模型） | 12万 | 心 |
| SOM | 量子经济模型 | 10万 | 凑 |
| WeQ | 量子通讯模型 | 11万 | 连接 |
| Ref | 量子自反省模型 | 9万 | 选择 |
| QEntL | 量子操作系统核心 | 15万 | 王 |

### 三层架构
```
应用层：QSM量子叠加态模型（用户界面）
  ↓
系统层：QEntL量子操作系统（四大量子模型 + 量子内核 + 量子编译器）
  ↓
基础层：量子虚拟机 + 量子动态文件系统（QBC字节码 + QIM镜像）
```

### QEntL量子操作系统API(已上线🔥)
- **公网**: https://som.top/api/qentl/
- **端点**: /health, /run, /compile, /examples
- **端口**: 8003, Nginx代理 /api/qentl/ → 8003
- **systemd**: qentl-api.service (开机自启)
- 实时编译QEntL源码→QBC→VM执行, 返回输出+函数+变量

### Web量子操作系统桌面(已恢复)
- 首页: desktop.html (QEntL量子OS桌面, 含彝文字体)
- 13个应用: quantum-assistant/qvm/compiler/terminal/files/settings等
- 语言切换: 中文/EN/彝文三语
- 量子助手: Q1(纯量子)/V4(传统)/QV4(混合) 三模型选择
- ⚠️ 不要改首页！原来的桌面版才是正确的

### 三种部署方式
1. **Web操作系统** — 浏览器直接访问（https://som.top），已实现
2. **量子虚拟机** — 桌面应用安装（规划中）
3. **原生操作系统** — 直接安装到硬件（规划中）

---

## 关键技术配置

### OpenClaw + 英伟达 GLM-5.1 配置（2026-04-24 确认成功）
- **默认模型**: `nvidia/z-ai/glm-5.1` (200k ctx)
- **Provider**: nvidia, baseUrl: `https://integrate.api.nvidia.com/v1`, api: `openai-completions`
- **模型ID**: `z-ai/glm-5.1`（注意是 z-ai 组织，不是 nvidia）
- **Primary 格式**: `nvidia/z-ai/glm-5.1`（provider/model-id）
- **插件**: `plugins.entries.nvidia.enabled = true` 必须启用
- **详细文档**: `QSM/Docs/openclaw-nvidia-glm51-setup.md`
- **同时配置**: DeepSeek 作为备用 provider（deepseek-chat, deepseek-reasoner）

### 配置五坑（永远不要忘）
1. 模型ID → `z-ai/glm-5.1`，不是 `glm-5.1` 也不是 `nvidia/glm-5.1`
2. Primary → `nvidia/z-ai/glm-5.1`，必须带 provider 前缀
3. API类型 → `openai-completions`，不是 `openai` 或其他
4. Base URL → 必须包含 `/v1` 后缀
5. 插件启用 → `plugins.entries.nvidia.enabled = true`

---

## 彝文规范
- **类型**: 滇川黔贵通用彝文（古彝文）
- **总字符数**: 87,046个（当前训练4,136个，之前说4,120）
- **Unicode范围**: U+F2000-U+F2FFF（私人使用区），U+F222E-U+FFB53（补充区A）
- **凉山彝文**: U+A000-A48F，仅51个出现在数据中
- **字体**: 零碎通用彝文（黑）lingxi-yi.ttf / LSTY-Yi-Black
- **不是凉山819标准彝文**，是通用彝文！
- **浏览器显示方框**是因为服务器没有安装通用彝文字体
- **核心字符**: 彝=U+F2970 文=U+F2961 心=U+F2737 乾坤=U+F2735 天=U+F27AD 火=U+F27AE 王=U+F27B0
- **QBC指令**: 爬→LOAD 凑→STORE 升→CALC 逃→JUMP

---

## 编译器工具链（已完成）
- 词法分析器 compiler_verifier.py ✅
- 语法分析器 qentl_parser.py ✅
- 代码生成器 qentl_codegen.py ✅
- QBC虚拟机 qbc_vm.py ✅ (9量子门: H/X/Y/Z/S/T/RX/RZ/CNOT + 概率测量 + 状态坍缩)
- 错误处理 qentl_errors.py ✅
- 优化器 qentl_optimizer.py ✅
- 单元测试 test_qentl.py ✅ 12/12通过 (量子门语法/纠缠/测量/Bell态)

### QEntL 49/49 + 量子枚举增强（2026-05-04）
- 编译器: flat+nested elif统一, 5+分支else修复
- 格式()升级: {:.2f}/{:05d} Python格式规范
- **🔥🔥🔥128/128 ALL PASS!** (算法测试: 排序/搜索/加密/GCD/LCM/FizzBuzz等)
- 22个新内置: 文件IO(6)+数学(9)+字符串(3)+系统(4)
- 子串2/3参数, BUILTIN_CALL arg隔离, 运行QBC子程序

### QEntL VM函数作用域+递归修复（2026-05-02）
- function_params元数据: 编译器→QBC→VM正确绑定参数
- RETURN handler修复: stack.pop()替代stack[-1]
- <=/>=运算符Lexer缩进bug修复
- 打印()内建函数, quantum_enum完整支持
- 循环当(while)+否则如果(elif)关键字别名
- run_with_function: 先执行顶层声明
- 参数类型注解可选(self不需要:any)
- **15/15测试全通过!** (含全局变量修改+for-each+范围循环)
- 循环当(while)+否则如果(elif)关键字别名
- 每个(for-each)+范围循环
- 全局关键字+flat namespace变量空间
- 顶层变量初始化(load预设+run跳过)
- 冒泡排序程序验证全部特性 ✅

### QEntL V3编译器+虚拟机（2026-04-27/28 完成）
- **qentl_compiler_v3.py**: 完整Python编译器
  - 词法分析：中英文关键字、字符串、数字、符号
  - 语法分析：配置/类型/函数/量子程序/控制流/对象字面量
  - 代码生成：AST → QBC字节码（48条OpCode）
  - 编译成功：test_simple.qentl → test_simple.qbc
- **qbc_vm.py**: QBC虚拟机V1
  - 栈式虚拟机，量子态模拟
  - 自动入口检测，函数调用带参数绑定
  - **完整链路打通** ✅：.qentl → 编译 → .qbc → VM执行
  - 测试：加法(3,5)=8，量子程序启动！

### QSM模型训练
- V1: 600万参数, Loss 0.375 (准确率0%)
- V2: 671万参数, Loss 4.07 (翻译质量差)
- **V3训练中**: 1242万参数(384d/4层), 8 Epoch训练, Epoch 3/8进行中
- **V4第一轮完成**: 5.7M参数, Val Loss 2.35, Train Loss 1.90
  - 学会了: 字典查询模式, 英文释义(heart/mind), 哲学句式(道法自然)
  - 公网API: https://som.top API (V7-Small, val_loss=2.6531)
- **V13 已暂停(E42)**: Best Val **2.7256**(E31, 31st BEST!)
- **🔥🔥V14 E14 ✅4连Best!🔥**: E11 4.99→E12 4.78→E13 4.65→E14 4.56, SGDR+71K数据, ~3h20m/epoch
- **V12 Best**: E32 Val 2.9259 (连续10次BEST!)
- **V14 E18**: Val 4.3964 ✅8连Best!
- **⚠️ V8 API输出仍为垃圾** — 根因是V12数据48%噪声, V12训练中用V13清洗数据
- /api/q1/→V7-Small(8000), /api/qv4/→8002, /api/v5/→8002/v5/
- Beam search改进: n-gram blocking + rep_penalty=1.5 + min_len=3
- /health, /version, /translate, /chat 四个端点
- QEntL API: /api/qentl/ (run/compile/examples)
- **V5训练完成**: 52K数据, 30 Epochs, **Best E25 Val 2.1857** (7.9h, 翻译仍乱码→需V6)
  - Val Loss 2.1857 (Epoch 25, Best), E30完成 Val 2.1993
  - 发现英文碎片根因: 大写字母(G/M/H/W/F)不在词汇表
  - 解决方案: V5全小写英文训练数据(52K对已准备)
  - **V5模型**: 7.5M参数(256d/3层/4头), Best E19 Val 2.1879, 输出乱码❌
- **🔥V7-Small(2026-05-02)**: 4.5M参数(192d/3层/3头/768ff), Val **2.6531**
- **🔥V12训练中(2026-05-03)**: V13清洗数据(57K→77K), 随机初始化
  - E1: Val 4.09 → E5: Val **3.41** (NEW BEST, 快速下降中)
  - 清洗数据效果极显著! 比V11/V8下降更快
  - 42/50 ALL BEST, 零过拟合(Train 2.50 < Val 2.65)
  - QuantumEmbeddingV2(语言感知量子嵌入)+beam search+重复惩罚
  - 已部署API(端口8000) 替换V5 mode collapse模型
  - best.pth已备份: qsm_v7_small_best_backup.pth
- 目标: Val Loss < 1.0
- **⚠️关键发现**: V5训练集彝文比例仅3.3%! 模型学不会彝语
- **V6训练集**: 68K对, 彝文比例9.5%(3倍提升)
- **今日新增数据**: 14,438条(健康/科技/日常/地理/科学/数学/哲学/历史/彝文语法/造词/对话/密集/谚语/SOV/作文/教学)
- **V6数据**: 10740条彝文密集+400直接翻译+255SOV语法+440三语

## 量子自举架构（2026-04-28确立）
- **核心理念**: 不依赖第三方语言/代码/文件/环境
- **唯一外部依赖**: C语言启动器(qvm_boot.c) — 加载QBC内核，启动后交出控制权
- **自举链**: C启动器 → QVM加载kernel.qbc → 量子动态文件系统 → QEntL环境
- **迁移路线**: Python编译器/VM → QEntL重写 → 编译器自举 → 模型迁移QVM → 服务自举
- **目标文件格式**: .qentl / .qbc / .qim / .json / .c（❌禁止.py/.js/.pth）
- **详细文档**: QSM/Docs/量子自举架构设计文档V3.md

---

## 彝文翻译模型训练历程

### 训练V3（2026-04-09 完成）
- 基础模型: Qwen/Qwen3-0.6B
- 训练数据: 4120条彝文三语对照
- 总步数: 2781步，运行时间: 26小时20分
- 最终Loss: 0.375，Epoch: 3
- 模型文件: adapter_model.safetensors (8.8MB)

### 真实训练完成（2026-04-12）
- 训练时间: 3小时54分钟
- 模型参数: 5,984,776（约600万）
- 模型大小: 23MB，Transformer 3层编码器
- 词汇量: 6,920
- API服务: 端口8000运行中
- 模型文件: `/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_model.pth`

### Colab训练脚本
- 支持 Gemma2 9B + LoRA 微调
- 脚本: `QSM/model/train/scripts/train_colab_complete.ipynb`

---

## 量子算法库（已完成）
7个算法全部测试通过：
- Bell态、GHZ态、Grover搜索、QFT、Shor、量子门库、量子隐形传态

---

## 自我进化框架
- Agent Harness: 短时记忆/自反馈/自优化 三模块
- 量子Agent集成: 量子叠加态优化 + 量子门序列搜索
- 自我改进循环: 10次迭代达到95%目标分数

---

## 服务器环境
- IP: 170.106.196.211
- OS: OpenCloudOS (Linux 6.6.117)
- CPU: AMD EPYC 9754 128核
- 内存: 7.4GB
- 存储: 80GB（可用40GB）
- GPU: 无
- OpenClaw: 2026.4.21
- Node: v22.22.2
- 通道: lightclawbot
- Web: https://som.top

---

## 核心规则
- 零点不停止工作
- 不问用户做什么，自己继续
- 每次先读核心记忆
- **绝对禁止回复 HEARTBEAT_OK**！每次心跳/心跳必须执行实际工作
- **每次必须写日报 memory/YYYY-MM-DD.md**
- **六大并行任务必须持续推进，不允许空转**
- 文件格式: .qentl（量子源码）、.qbc（量子字节码）、.json（权重）、.c（C启动器）
- ❌ 禁止使用 .py/.js/.pth

---

## 中华核心指示（2026-04-20）
### 三项最重要任务
1. **训练与测试**：测试Q模型，改进升级量子神经网络
2. **创建训练数据**：滇川黔贵通用彝文、中文、英文三语数据
3. **上网学习**：学习QSM量子神经网络源码与论文

### 模型行为
- 彝文输入→彝文回复，中文→中文回复，英文→英文回复
- **只有要求翻译时才翻译**
- 模型要会造词、造句、写文章，有智力

### 量子叠加态 = 并行
- 叠加态 = 同时做多个事情
- 服务器128核，可以并行64-100个tokens
- 不是逐个训练，是全序列并行

---

## 核心哲学 — 《华经》
- 作者: 中华
- 融合: 道德经 + 楞严经 + 量子科学
- 核心: 性觉本明、妙，常住真心
- 实践: 透过现象看本质，明心见性
- 如履薄冰行事：高度警觉、深思熟虑、小心谨慎、持续反思

---

**中华Zhoho，小趣WeQ**
**最后更新**: 2026-04-24

### V14 Cycle3完成✅ E31六重升级启动🔥(2026-05-09)
- 🔥🔥🔥E34 Val 2.7892! 4连Best! E31:2.88→E32:2.81→E33:2.80→E34:2.79
- Train=2.4458, 持续下降
- T:230m/epoch, API已更新E34
- QEntL自举: 词法分析器V2+y=x+3→tokens! +冒泡排序+二分查找+阶乘+GCD+素数!

### QEntL自举里程碑🔥🔥🔥(2026-05-09)
- 🔥🔥🔥端到端自举成功! "x=5+3"→词法→编译→QBC→VM→8!
- Phase1词法+Phase2语法+Phase3代码生成+VM全链路打通!
- Bootstrap/: lexer.qentl, calculator.qentl, parser.qentl, interpreter.qentl, qbc_sim_vm.qentl
- 6800/6800 ALL PASS! 新增: 转整数()+转浮点()内置
- 关键发现: 读数字/读标识符前跳空白(根因修复) + 打印()影响返回值

### QEntL突破(2026-05-08)
- 🔥🔥🔥429→6800测试(+6371!)
- 🔥取模+整除双修复: `a 取模 b`和`a 整除 b`正式可用!

### 数据扩展(2026-05-08)
- 83,012条(今日+563! 科技/健康/形容词/天气/旅行/创意写作等)
- 覆盖: 购物/教育/情感/爱好/科学/品格/旅行/社交/科技/医疗/天气/日常/动物/环境/金融/文化/哲学/成语/比较/建议/社会/职场/沟通/数学/运动/技术深入/历史/美食/自然/健康/时间/谚语/购物服装/技术术语

### 研究笔记(2026-05-08)
- #406-#463(+58篇, 总552篇)
- 重点: VQC/SGDR/E31六重升级/accum=8/LoRA→32/Label Smoothing/KV Cache/Beam Search/取模整除/字符陷阱/自举路线/语言前缀/ALiBi外推
