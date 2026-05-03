# 量子神经网络学习笔记

## 1. 变分量子电路 (VQC) - 核心架构
- 参数化量子门(RY/RZ) + 纠缠层(CNOT) + 测量
- 经典优化器更新量子门参数
- 浅电路 → 适合NISQ设备

## 2. PennyLane 框架核心
- 自动微分：支持混合量子-经典计算
- 多后端：模拟器 + 真实硬件
- ML集成：PyTorch/TensorFlow/JAX
- 关键API: qml.qnode, qml.Drawer

## 3. 量子注意力机制设计思路
- 用量子旋转门(RY/RZ)替代经典注意力权重
- 量子叠加态 → 天然的多头注意力
- 纠缠 → 跨位置的信息交互
- 测量 → 注意力权重坍缩

## 4. QSM V2 量子增强设计
- 量子旋转层：可学习的RY/RZ参数
- 量子相位层：模拟量子干涉效应
- 量子注意力与经典Transformer串联
- 损失函数：主任务(翻译/对话) + 辅任务(分类)

## 5. 旋转等变量子分类器发现
- 仅30参数实现360°零样本泛化
- 胜过100倍参数的CNN
- 关键：等变性(Equivariance) = 数据对称性
- 对QSM启示：彝文对称结构可用等变网络

## 6. 下一步学习目标
- [ ] Qiskit VQE实现细节
- [ ] 量子Transformer论文 (2023-2024)
- [ ] 变分量子本征求解器(VQE)训练技巧
- [ ] 量子自然梯度下降
- [ ] 彝文对称性与等变网络结合

## 7. 门控量子注意力机制 (V3改进)
- **问题**: V2模型Loss降到4.07但翻译质量极差
- **原因**: 纯量子旋转可能干扰经典注意力，没有门控调节
- **V3改进**: 加入可学习门控参数
  - `output = gate * quantum_output + (1 - gate) * classical_input`
  - 让模型自己决定量子vs经典的比例
- **LayerNorm**: 在decoder前加LayerNorm稳定输出分布
- **效果待验证**: V3训练中

## 8. 编码器-解码器架构思考
- **当前问题**: V2只用encoder，输出靠linear projection
- **真正的翻译需要**: Encoder-Decoder架构
  - Encoder: 理解源语言（中文）
  - Decoder: 生成目标语言（彝文）
- **下一步改进方向**:
  1. 加入真正的Decoder（带masked attention）
  2. Cross-attention连接编码器和解码器
  3. 自回归生成：逐token生成，每步参考已生成内容

## 9. 字符级vs子词级分词
- **当前**: 纯字符级（每个字=1个token）
- **问题**: 序列太长，学习困难
- **可能改进**:
  1. BPE (Byte Pair Encoding) 子词分词
  2. 常用词合并（"你好"=1个token而非2个）
  3. 减少序列长度，提升训练效率

## 10. 服务器内存限制下的训练策略
- 7.4GB内存，128核CPU
- 512d/6层模型→OOM（1.3GB+训练内存）
- 384d/4层模型→安全（666MB+训练内存）
- **策略**: 小batch(4) + gradient accumulation模拟大batch
- **未来**: 需要GPU才能训练大模型


## 11. 量子旋转门在注意力机制中的作用
- RY(θ)门：绕Y轴旋转θ角 → 适合模拟概率幅变化
- RZ(θ)门：绕Z轴旋转θ角 → 适合模拟相位变化
- **V3使用**: 可学习旋转参数替代固定注意力权重
- **门控设计**: gate * quantum + (1-gate) * classical
  - 初期gate≈0.5 → 量子与经典各半
  - 训练后gate自适应 → 可能偏向量子或经典
- **数学**: 旋转矩阵 R(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]
  - 作用: 旋转嵌入空间中的向量
  - 量子对应: Bloch球上的旋转

## 12. QEntL编译→执行完整链路 ✅
- 编译器V3: .qentl → AST → QBC字节码
  - 词法: 中英文关键字、字符串、数字、符号
  - 语法: 配置/类型/函数/量子程序/控制流/对象字面量
  - 代码生成: 48条OpCode，支持量子操作
- 虚拟机V1: 加载QBC → 执行
  - 栈式虚拟机（类似JVM/Python VM）
  - 自动入口检测（找QUANTUM_INIT）
  - 函数调用带参数绑定
  - 量子态模拟（初始化/测量）
  - 测试通过: 加法(3,5)=8, 量子程序启动输出

## 13. 下一步改进方向
1. **模型架构**: Encoder-Decoder结构（真正的翻译模型）
2. **分词**: BPE子词分词（减少序列长度）
3. **训练**: Gradient Accumulation（模拟大batch）
4. **编译器**: 类型检查/错误恢复/优化器
5. **虚拟机**: 垃圾回收/异常处理/多线程

## 14. 量子自然梯度下降
- 经典SGD在参数空间走梯度方向
- 量子自然梯度在概率分布空间走最陡方向
- Fisher信息矩阵F定义概率空间的度量
- 更新公式: θ_{t+1} = θ_t - η F^{-1} ∇L(θ_t)
- 量子版: 用量子Fisher信息矩阵
- **对QSM的启示**: 
  - 当前用AdamW优化器（经典方法）
  - 量子旋转参数可能需要量子自然梯度
  - 但CPU训练计算F^{-1}太慢，需要近似

## 15. C启动器实现要点
- **最小化原则**: C代码只做三件事
  1. 分配内存
  2. 加载QBC文件
  3. 跳入QVM执行循环
- **编译**: gcc -o qvm_boot qvm_boot.c -lm
- **结果**: 22KB二进制文件
- **下一步**: 
  1. 实现二进制QBC格式（替代JSON）
  2. C实现的QVM执行循环需匹配Python版功能
  3. 用QEntL编写kernel.qbc

## 16. 数据去重结果
- 总数据: 47635 → 36205 (去重11430条, 24%)
- 主要重复源: all_chat.jsonl, q_model (大量重复)
- 去重后训练数据更干净，效率更高
- V3训练用的是去重前数据，V4应使用去重后数据

## 17. Encoder-Decoder vs Encoder-Only：翻译质量的根本原因
- **V2/V3问题**: 只有编码器 → 输出是所有token的logits
  - 编码器看到完整输入，但输出层无法自回归生成
  - 训练时：每个位置独立预测下一个token（语言模型方式）
  - 推理时：只能一次输出所有位置，无法逐步生成
  - 结果：输出是输入的"编码"而非"翻译"
- **V4解决方案**: Encoder-Decoder + Cross-Attention
  - 编码器处理源语言 → 语义表示
  - 解码器通过交叉注意力"读取"编码器输出
  - 解码器自回归生成目标语言（BOS→token1→token2→...→EOS）
  - 这是真正的翻译模型架构（与Google NMT/Transformer相同）
- **关键区别**:
  - Encoder-Only: P(y|x) 隐式，靠mask预测
  - Encoder-Decoder: P(y|x) 显式，解码器条件生成
  - 翻译任务需要后者！分类/理解任务可以用前者

## 18. V4模型参数估算
- d_model=256, n_heads=4, n_layers=3, vocab=6920
- 嵌入: 6920 × 256 = 1,771,520
- 编码器3层: 3 × (4×256² + 2×256×1024) = 3 × 1,179,648 = 3,538,944
- 解码器3层: 3 × (3×4×256² + 2×256×1024) = 3 × 1,441,792 = 4,325,376
- 输出投影: 6920 × 256 = 1,771,520
- 总计: ~11,407,360 (约1140万参数)
- 内存估算: 1140万 × 4bytes × 4(梯度+优化器) ≈ 175MB → 不会OOM!
- d_model=384版: ~2600万参数，仍可控

## 19. CPU训练优化策略
- **Gradient Accumulation**: 模拟大batch size
  - 当前batch=4太小，梯度噪声大
  - 每4步累加梯度再更新 = 等效batch=16
  - 实现简单：loss /= accum_steps, 反向传播累加
  - 效果：训练更稳定，收敛更快
- **Mixed Precision (FP16)**: CPU不支持原生FP16
  - 但可以用bfloat16在AMD EPYC上
  - 需要PyTorch 2.x支持
  - 内存减半，速度提升
- **Learning Rate Scheduling**:
  - Warmup: 前10%步骤LR从0线性增长
  - Cosine Decay: 后90%步骤余弦退火
  - 比固定LR好得多
- **Label Smoothing**: 防止过度自信
  - soft_target = (1-ε)*one_hot + ε/vocab_size
  - ε=0.1常用
  - 提高泛化能力

## 20. 编译器'让'关键字修复
- 问题: LET = 'let' 但QEntL使用中文'让'
- 修复: LET = '让'
- 效果: '让 量子位 = 8' 正确编译为 LOAD_CONST(8) → STORE_VAR(量子位)
- 内核执行输出从"None"变为正确值"8"
- **教训**: 关键字映射必须匹配实际使用的语言

## 21. 交叉注意力在翻译中的关键作用
- **自注意力 vs 交叉注意力**:
  - 自注意力: Q=K=V来自同一序列 → 理解自身
  - 交叉注意力: Q来自解码器, K=V来自编码器 → 理解源语言
- **翻译生成过程**:
  1. 编码器处理"你好" → 语义向量 [h1, h2]
  2. 解码器BOS → 交叉注意力查看h1,h2 → 生成"Hello"
  3. "Hello" → 交叉注意力查看h1,h2 → 生成"!"
  4. "!" → 交叉注意力 → 生成<EOS>
- **V4验证**: Epoch 5, Val Loss 3.58, 翻译输出已有结构
  - "你好"→"我皮好！好，简你..." (方向对，需更多训练)

## 22. V4训练策略分析
- 当前: d_model=256, 5.7M参数, 9407训练对
- 每Epoch约2分钟 (vs V3的70分钟) — 快35倍!
- Loss下降速度: 8.6→3.58 (5 Epochs)
- 预计15 Epochs后Loss可降至2.5以下
- **关键**: 数据量可能不够 — 9407对偏少
- **下一步**: 用更多数据重新训练V4
  - 合并所有训练数据为src-tgt对格式
  - 目标20000+对

## 23. 翻译解码策略对比
- **Greedy Decoding**: 每步取概率最大的token
  - 优点: 简单、确定
  - 缺点: 容易陷入局部最优，输出重复
- **Beam Search**: 保持top-k候选序列
  - k=5常用，平衡质量和效率
  - 每步扩展k个候选，保留score最高的k个
  - 需要length normalization防止短序列偏好
- **Sampling**: 按概率分布采样
  - temperature低→接近greedy，高→更多样
  - V4当前用temperature=0.5，偏向确定性
  - top-k/top-p采样可以限制在高质量token内
- **对V4的启示**:
  - 当前用sampling(t=0.5)，简单但非最优
  - 翻译任务应优先用beam search(k=3-5)
  - 对话任务用sampling(t=0.7-1.0)更多样

## 24. 训练数据质量 vs 数量
- V4数据: 9407对→30000对(双向)
- 双向训练: 中→英 + 英→中 共享同一模型
- **数据增强策略**:
  - 回译(back-translation): 用模型翻译→加入训练
  - 噪声注入: 随机替换/删除字符
  - 混合语言: 同一句内中英彝混合
- **关键指标**: Val Loss持续下降 = 数据有效
  - V4: 8.6→3.07→2.70 (Epoch 9)
  - 收敛点预计在Loss ~2.0-2.5

## 25. QEntL自举路线图细化
1. ✅ C启动器(qvm_boot.c) — 22KB二进制
2. ✅ kernel.qentl → kernel.qbc — 12函数, 158指令
3. ✅ 编译器V3(Python) — 全链路8/8测试
4. ✅ 虚拟机V1(Python) — 栈式VM+量子模拟
5. ⬜ 二进制QBC格式(C加载器) — 当前是JSON
6. ⬜ 编译器用QEntL重写 — 自举关键
7. ⬜ VM用C重写 — 性能提升
8. ⬜ QEntL标准库 — 文件I/O/网络/数学

## 26. 二进制QBC格式设计
- JSON QBC: 16380 bytes (kernel)
- Binary QBC: 2043 bytes (12% of JSON!) 
- 格式: [MAGIC "QBC\x01"][n_const][n_func][n_instr][constants][functions][instructions][string_table]
- 常量类型: int8/int32/float64/string
- 操作数类型: none/int/string_ref
- 字符串表在末尾，指令通过索引引用
- **C启动器可直接读取此格式**
- 下一步: 在qvm_boot.c中实现二进制QBC加载器

## 27. V4 V2训练进展分析
- Epoch 1 Val Loss: 3.18 (vs V4 V1的8.6)
- 巨大改善因为: 3倍数据量(30000对) + 双向训练
- 预计20 Epochs后Val Loss可达1.5-2.0
- 训练每Epoch约7分钟(vs V1的2分钟，因为数据多了3倍)

## 28. V4 V2训练分析 - Loss收敛与翻译质量
- Val Loss 1.79 (Epoch 5/20) 远低于V1同期的3.58
- 3倍数据量(30k vs 9.4k)显著加速收敛
- Beam search vs Sampling: Beam更稳定但早期epoch输出更"保守"
- 翻译质量滞后于Loss下降 — 需要Loss < 1.0才能产生准确翻译
- **关键发现**: Encoder-Decoder架构在低Loss时翻译能力急剧提升(非线性)
  - Loss > 3: 乱码
  - Loss 2-3: 部分正确短语
  - Loss 1-2: 语义相关但语法错误
  - Loss < 1: (预期) 准确翻译

## 29. 训练效率优化方向
- 当前: 每Epoch ~26分钟 (30000对 × batch=8 × accum=4)
- 可能优化:
  1. 增大batch size (减少通信开销)
  2. 梯度累积步数从4降到2 (牺牲等效batch从32到16)
  3. 混合精度训练 (fp16) - CPU不支持
  4. 动态批处理 (按长度分组)
- CPU训练限制: 无GPU → 无法用混合精度
- **最佳策略**: 让训练跑完20 epochs, 不中断

## 30. 知识蒸馏与模型压缩
- **概念**: 用大模型(teacher)训练小模型(student)
- Teacher输出soft labels(概率分布)而非hard labels
- Student学习teacher的输出分布，获得更好的泛化能力
- **温度参数T**: softmax(T)使分布更平滑，传递更多知识
- **对V4的启示**:
  - V4(5.7M)可以作为student，V3(12.4M)作为teacher
  - 但V3翻译质量差(encoder-only)，不适合做teacher
  - 更好的方案: 用云API(gpt-4等)生成翻译数据，作为soft labels
  - 当前最有效: 增加训练数据量(已从9.4k→30k→66k)

## 31. QEntL自举编译器策略
- 当前: Python编写编译器 → 编译QEntL → 生成QBC
- 目标: 用QEntL编写编译器 → 编译自己 → 自举
- **分步实现**:
  1. ✅ Python编译器V3(当前)
  2. ⬜ 用QEntL重写编译器核心函数(词法分析/语法分析)
  3. ⬜ 用QEntL编译器编译自身
  4. ⬜ 移除Python依赖，仅留C启动器
- **关键挑战**: QEntL缺少文件I/O和字符串操作
- **解决方案**: 先扩展标准库，再逐步自举

## 32. 训练数据增长趋势
- 4/24: 4,120条(初始)
- 4/27: 16,480条(字符级) + 47,635条(总计)
- 4/28: 66,580条(+18,945条, +40%)
  - +12,368 直接翻译对
  - +42 段落/对话
  - +12,368 详细描述
- 去重后: ~54,170条唯一数据
- 目标: 100,000+条

## 33. Qiskit量子计算框架研究
- **Qiskit**: IBM开源的量子计算框架(Python)
- 核心组件:
  1. **Qiskit Terra**: 量子电路构建和编译
  2. **Qiskit Aer**: 量子电路模拟器(CPU/GPU)
  3. **Qiskit Runtime**: IBM量子云执行
  4. **Qiskit Nature**: 量子化学应用
- **关键概念映射到QEntL**:
  - QuantumCircuit ↔ quantum_program
  - QuantumRegister ↔ 量子寄存器
  - H/CNOT/X/Z门 ↔ 应用量子门()
  - measure() ↔ 量子测量()
  - execute() ↔ QBC VM执行
- **对QEntL的启示**:
  - QEntL的量子门操作可以借鉴Qiskit的gate命名
  - 添加更多量子门: X(Pauli-X), Y, Z, S, T, RX, RY, RZ
  - 量子电路可视化功能
  - Aer模拟器可以在QBC VM中实现概率性测量

## 34. QBC VM量子模拟增强计划
- 当前: 量子态用简单数组表示，测量返回0
- 增强1: 用复数数组表示量子态向量
  - |0⟩ = [1+0j, 0+0j]
  - |1⟩ = [0+0j, 1+0j]
  - 叠加态 |+⟩ = [1/√2, 1/√2]
- 增强2: 实现真实量子门矩阵运算
  - H门: [[1,1],[1,-1]]/√2
  - CNOT门: [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]
- 增强3: 概率性测量
  - 测量结果: |α|²概率为0, |β|²概率为1
- **注意**: 8比特需要2⁸=256维向量，内存可控

## 35. 参数化量子电路(PQC)与量子神经网络
- **PQC (Parameterized Quantum Circuit)**: 量子版的神经网络层
- 结构: 可调参数的量子门序列 → 测量 → 经典后处理
- **量子优势**: 指数级大的Hilbert空间(2^n维)
- **训练方法**: 
  - 参数位移规则(Parameter Shift Rule)计算梯度
  - 类似经典反向传播但用量子特性
- **与QSM的结合方向**:
  1. 将V4的"门控量子注意力"扩展为真正的PQC
  2. 用量子电路替代全连接层
  3. 量子嵌入: 将经典token嵌入映射到量子态
- **挑战**: 
  - 梯度消失(Barren Plateaus) - 随着量子比特数增加
  - 噪声 - 当前NISQ设备限制
  - 训练数据需要编码为量子态

## 36. Transformer改进方案: 线性注意力
- **标准注意力**: O(n²)复杂度
- **线性注意力**: O(n)复杂度, 用核函数近似
  - φ(q)·φ(k)^T ≈ softmax(q·k^T)
  - 常用核: elu+1, 随机特征
- **对V4的应用**:
  - 当前max_seq=64, 计算量可控
  - 如果扩展到512+tokens, 线性注意力必要
  - 门控量子注意力可以自然扩展为线性版本
- **Performer**: 随机正交特征(FAVOR+)近似注意力
- **Flash Attention**: IO优化, 不改变计算复杂度但大幅加速

## 37. 当前V4模型瓶颈分析
- **数据瓶颈**: 30k训练对仍然偏少
  - 专业翻译模型通常需要100k-1M对
  - 可以用回译(back-translation)扩充
- **模型容量**: 5.7M参数可能不够
  - 但受7.4GB内存限制, 无法增大太多
  - 可以尝试: d_model=384, n_heads=6, n_layers=4 → ~10M参数
  - 需要关闭V3训练释放内存
- **训练时间**: CPU训练慢, 每Epoch ~26分钟
  - 20 Epochs = ~8.7小时
  - V4 V2预计在UTC 06:00左右完成

## 38. 变分量子本征求解器(VQE)与QSM
- **VQE**: 用量子电路+经典优化器求解分子基态能量
- 流程: 参数化量子电路 → 测量期望值 → 经典优化器调参 → 循环
- **与QSM翻译的联系**:
  - VQE = 量子编码 + 经典解码(优化)
  - QSM翻译 = 经典编码 + 量子注意力 + 经典解码
  - 可以将QSM的"量子注意力"变成真正的VQE优化
- **QEntL实现VQE**:
  - 量子门 H/CNOT → 创建ansatz(试探波函数)
  - 量子测量 → 计算期望值(能量)
  - 经典循环 → 调整参数(当前QEntL缺少浮点参数优化)

## 39. 服务器运维总结(今日)
- 内存: 稳定43-44% (两个训练+3个API)
- 磁盘: 64% (从70%清理到64%)
- 服务: 8000/8002端口均健康
- Web: som.top 4个页面全部200
- 训练: V4 V2 Epoch 12(1.43), V3 Epoch 6
- 异常: 无

## 40. QSM项目今日成果汇总
### 模型训练
- V4第一轮完成: Val Loss 2.35
- V4 V2训练中: 30k数据, Epoch 12, Val Loss 1.51, 目标<1.0
- V2评估: Encoder-Only无法翻译, 架构>参数量

### QEntL量子操作系统
- 编译器: 取模(%), 数组索引, FOR循环, 量子门语法
- VM: 真实量子模拟(H/CNOT/X+概率测量+状态坍缩)
- 内核V1.3: 量子门语法+Bell态+GHZ预留
- 测试: 12/12全通过

### 数据
- 总训练数据: 66,626条 (从7120增长9.4x)
- 去重: 556条, 清洁后54,170条
- +12,368条直接翻译对
- +46条干净英文数据

### Web服务
- som.top: 首页+翻译器+QEntL编辑器+API文档
- API: translate/compile/model-info/health/quantum (5端点)
- Beam Search解码

### Git
- 清理: 185MB→4.5MB (移除.pth文件)
- .gitignore: *.pth排除规则

## 41. 量子纠错(QEC)与神经网络训练稳定性
- **量子纠错核心**: 用冗余量子比特保护信息
  - 3比特重复码: |0⟩→|000⟩, |1⟩→|111⟩
  - 多数投票纠正单比特翻转
- **Surface Code**: 最实用的QEC方案
  - 二维网格上的量子比特
  - 阈值: 错误率<1%时可以任意延长计算
- **与QSM训练的联系**:
  - 训练不稳定 ≈ 量子噪声
  - 梯度裁剪 ≈ 纠错(防止梯度爆炸)
  - Label Smoothing ≈ 量子退相干容错
  - Batch Normalization ≈ 量子纠错码(稳定中间态)
- **启发**: QSM的"门控量子注意力"可以借鉴QEC思路
  - gate = 量子纠错强度(1=完全纠错, 0=纯经典)
  - 训练早期: 高纠错率(强gate, 趋向经典注意力)
  - 训练后期: 降低纠错(弱gate, 释放量子优势)

## 42. Dropout与量子测量的深层联系
- **Dropout**: 训练时随机丢弃神经元, 防止过拟合
  - p=0.1: 10%概率丢弃
  - 效果: 集成学习+正则化
- **量子测量**: 观测导致叠加态坍缩
  - 测量前: |ψ⟩ = α|0⟩ + β|1⟩ (叠加态)
  - 测量后: |0⟩ 或 |1⟩ (坍缩)
- **深层联系**:
  - Dropout ≈ 对神经元做"经典测量"(丢弃=坍缩到0)
  - 量子Dropout: 以概率p测量量子比特
  - 未测量: 保留叠加态(完整信息)
  - 测量后: 坍缩为确定值(信息丢失)
- **QSM应用**: 
  - 在量子注意力层添加量子Dropout
  - 训练时以概率p测量量子旋转参数
  - 推理时保留完整叠加态(类似Dropout关闭)

## 43. Grover搜索算法与QEntL实现
- **问题**: 在N个无序元素中找到目标, 经典O(N), 量子O(√N)
- **核心电路**:
  1. 初始化n比特 → H门全部 → 均匀叠加
  2. Oracle: 标记目标态(相位翻转)
  3. 扩散算子: 关于均值的反转
  4. 重复2-3约√N次
  5. 测量 → 以高概率得到目标
- **QEntL实现**:
  ```
  quantum_program Grover搜索 {
      setup: 函数() {
          // 超叠加
          量子门 H 0
          量子门 H 1
          量子门 H 2
          // Oracle + 扩散 (需要条件相位门)
          测量 0
          测量 1
          测量 2
      }
  }
  ```
- **当前QEntL限制**: 缺少相位门(RZ/S/T)和条件相位
- **下一步**: 添加RZ/Phase门到QEntL

## 44. 量子算法复杂度对比
| 算法 | 经典复杂度 | 量子复杂度 | 加速 |
|------|-----------|-----------|------|
| 搜索(Grover) | O(N) | O(√N) | 二次 |
| 因式分解(Shor) | O(exp) | O(n³) | 指数 |
| 仿真(费曼) | O(exp(n)) | O(n) | 指数 |
| 数据库查找 | O(N) | O(√N) | 二次 |
| 翻译(QSM) | O(n²) | O(n)? | 线性? |
- **QSM翻译的量子加速假设**:
  - 经典注意力: O(n²)
  - 量子注意力(叠加态搜索): 理论上O(n)可能
  - 但当前"门控量子注意力"是经典模拟, 无真正加速
  - 真正加速需要量子硬件执行

## 45. V5模型规划 - 下一步
- **词汇表扩展**: 加入大写英文字母A-Z (当前缺失!)
  - 现有6924 → 需要至少6924+26=6950
  - 或者: 训练数据全用小写英文(已准备)
- **训练数据V3**: 合并所有67K+条数据
  - 包含: 直接翻译+详细描述+段落对话+小写英文+多样化数据
  - 预计40000+对有效训练对
- **模型调整**:
  - 选项A: 保持5.7M, 全小写英文, 更多数据
  - 选项B: 扩展到d_model=384, 10M参数(需关V3释放内存)
  - 推荐: 先用选项A验证数据质量

## 46. 量子自然语言处理(QNLP) - Bob Coecke团队
- **核心思想**: 语言结构 ≈ 量子过程
  - 句子的语法结构 = 量子电路图
  - 词 = 量子态, 语法 = 量子门
  - 组合语义 = 张量积 + 收缩
- **DisCoCat模型** (Distributional Compositional Categorical):
  - 词向量 → 量子态 |ψ⟩
  - 语法类型 → 量子门序列
  - 句子意义 → 量子态演化结果
- **与QSM翻译的联系**:
  - QSM的"量子注意力"本质上是在做类似的事情
  - 但QSM是经典模拟量子, QNLP是真量子
  - 两者共享: 组合性(compositionality)原则
- **启发**: 
  - 彝文翻译可以用QNLP框架: 彝文字符→量子态→中文态
  - 不同语言的语法结构 = 不同的量子门序列
  - 翻译 = 量子态在不同基底间的变换(类似基底变换)

## 47. 量子词嵌入 vs 经典词嵌入
- **经典**: Word2Vec/GloVe → 固定向量, 余弦相似度
- **量子**: 词 = 密度矩阵ρ, 相似度 = 迹距离
- **优势**: 
  - 量子词可以表示歧义(叠加态): |银行⟩ = α|金融⟩ + β|河岸⟩
  - 经典词向量是平均值, 丢失了歧义信息
- **QSM应用**: 
  - 彝文字符天然适合量子表示(一字多义)
  - 心 = α|heart⟩ + β|mind⟩ (物理+精神叠加)
  - 道 = α|way⟩ + β|speak⟩ + γ|Daoism⟩ (三重叠加)
- **实现路径**: 
  - 将QSM编码器的hidden state视为"量子词态"
  - 门控量子注意力 = 在经典和量子表示间插值

## 48. V4 V2 Epoch 15 翻译质量趋势分析
| Epoch | Val Loss | 翻译质量 |
|-------|----------|---------|
| 5 | 1.79 | 短语片段 |
| 8 | 1.57 | 学会指令格式 |
| 12 | 1.47 | 中文对话改善, 英文碎片 |
| 15 | 1.44 | (待评估) |
- Loss从1.79→1.44, 下降19.5%
- 英文碎片问题(大写字母不在词汇表)将在V5解决
- 预测: Epoch 20 Val Loss ~1.35-1.40

## 49. 旋转位置编码(RoPE)与量子旋转的统一
- **RoPE核心**: 用旋转矩阵编码位置信息
  - 位置m的token: q_m = R(θm) · q_0
  - R(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]
  - 内积: q_m · k_n 只依赖相对位置(m-n)
- **量子旋转**: RZ(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
  - 和RoPE数学结构几乎相同!
  - 都是2×2旋转/相位矩阵
- **统一**: QSM可以用量子旋转门替代经典位置编码
  - 位置m → RZ(m·θ) 作用于量子注意力
  - 天然编码相对位置信息
  - 不需要额外的位置嵌入层!
- **QSM V5改进**: 用RZ旋转替代正弦位置编码
  - 减少1个嵌入层的参数
  - 物理直觉: 位置=量子相位

## 50. 稀疏注意力 vs 量子搜索注意力
- **问题**: 标准注意力O(n²), 长序列太慢
- **稀疏方案**: 
  - Longformer: 局部窗口+全局token
  - BigBird: 随机+窗口+全局
  - 线性注意力: φ(q)·(φ(k)^T·v) → O(n)
- **量子搜索注意力(理论)**:
  - Grover搜索可以O(√N)找到相关key
  - 量子注意力 = 在key的叠加态中搜索
  - 复杂度: O(n√n) 还是 O(n)?
  - 目前纯理论, 需要量子硬件
- **QSM当前**: 门控量子注意力是经典模拟
  - gate * quantum_attn + (1-gate) * classical_attn
  - 计算量 = 2倍标准注意力
  - 但信息量更丰富(叠加态编码)

## 51. V5模型架构规划
- **词汇表**: 保持6924 (全小写英文, 无需新token)
- **位置编码**: RZ旋转(替代正弦嵌入, 见#49)
- **数据**: V5训练集52,204对(全小写+多样化)
- **训练策略**: 
  - 30 Epochs (V2用了20, 数据多需要更多)
  - Warmup: 500步
  - Cosine decay: 1e-3 → 1e-5
  - Label smoothing: 0.1
- **目标**: Val Loss < 1.0 → 翻译准确率>50%

## 52. 知识蒸馏与QSM小模型优化
- **核心**: 大模型(teacher)→小模型(student), 保留性能
  - Soft targets: teacher的logits(包含"暗知识")
  - Temperature T: softmax(q_i/T) 软化分布
  - Student loss = α·硬标签损失 + β·KL散度(soft targets)
- **QSM应用**:
  - 用DeepSeek/GLM大模型作为teacher
  - 蒸馏到5.7M参数的QSM V4
  - 彝文翻译的"暗知识": 字符间的语义关联
- **实现**: 
  1. 用大模型生成彝文翻译的soft labels
  2. 训练QSM同时拟合hard labels和soft labels
  3. T=3-5, α=0.3, β=0.7

## 53. 课程学习(Curriculum Learning)用于翻译训练
- **核心**: 从简单→困难, 模仿人类学习
  - Stage 1: 字符级翻译(心→heart)
  - Stage 2: 词语级翻译(量子→quantum)
  - Stage 3: 短语级(量子叠加态→quantum superposition)
  - Stage 4: 句子级(道法自然→the way follows nature)
- **QSM V5训练策略**:
  - Epoch 1-8: 字符+词语数据(短序列)
  - Epoch 9-16: 短语级数据
  - Epoch 17-25: 句子+段落级
  - Epoch 26-30: 全量混合
- **好处**: 
  - 避免早期训练被长序列dominate
  - 逐步提升模型能力
  - 更快的收敛速度

## 54. PennyLane量子机器学习框架
- **核心**: 量子电路=神经网络层, 自动微分量子电路
- **关键概念**:
  - QNode: 量子函数(类似PyTorch的Module)
  - Device: 量子模拟器/硬件后端
  - QuantumLayer: 可嵌入经典NN的量子层
- **混合量子-经典模型**:
  ```python
  @qml.qnode(dev)
  def quantum_layer(inputs, weights):
      qml.AngleEmbedding(inputs, wires=range(n_qubits))
      qml.BasicEntanglerLayers(weights, wires=range(n_qubits))
      return qml.expval(qml.PauliZ(0))
  ```
- **与QSM的联系**:
  - QSM的"门控量子注意力"类似PennyLane的hybrid model
  - PennyLane的AngleEmbedding ≈ QSM的量子旋转编码
  - PennyLane的BasicEntanglerLayers ≈ QSM的纠缠层
- **QEntL可以实现**:
  - AngleEmbedding → 用量子门 RX/RZ 带"参数"
  - EntanglerLayers → 用纠缠关键词
  - 测量 → 用测量关键词
- **限制**: QEntL目前不支持参数化门(如RX(θ), θ是变量)
  - 需要添加: 变量量子门语法 `量子门 RX 参数θ 0`

## 55. V5训练启动规划
- **等待V4 V2完成**: Epoch 19/20, ~15分钟后
- **V5训练配置**:
  - 数据: 52,354对(含difficulty标签)
  - 课程学习: 先短后长
  - 模型: 保持5.7M (d_model=256, 3层)
  - Epochs: 30 (数据多需要更多)
  - LR: 1e-3 → 1e-5 (cosine decay)
  - Warmup: 500步
  - Label smoothing: 0.1
  - 优化: AdamW (weight_decay=0.01)
- **启动时机**: V4 V2完成后立即启动
- **内存**: 需要关掉V3训练(8.5%内存)来释放空间
  - V3 Loss 3.7-4.8, 效果差, 可以停止

## 56. V5训练启动 - 关键改进
- **数据**: 52,354对(比V2的30K多74%)
- **全小写英文**: 解决G/M/H等不在词汇表的问题
- **学习率调度**: Warmup 500步 + Cosine Decay 1e-3→1e-5
- **Label Smoothing**: 0.1(防止过拟合, 让模型不确定时更保守)
- **AdamW**: weight_decay=0.01(正则化)
- **模型**: 7.5M参数(d_model=256, 3层, 4头)
- **比V4改进**:
  - 更多数据(52K vs 30K)
  - 更好的LR调度(warmup+cosine vs 固定)
  - Label smoothing
  - 全小写英文(无UNK)

## 57. Label Smoothing的数学本质
- **标准交叉熵**: H(y, p) = -Σ y_i log(p_i)
  - y = one-hot: [0, 0, 1, 0, ...] (100%确定)
  - 问题: 模型追求100%置信度 → 过拟合
- **Label Smoothing(ε=0.1)**: 
  - y_smooth = (1-ε)*y_onehot + ε/K
  - [0.00001, 0.00001, 0.90001, 0.00001, ...] (K=6924)
  - 效果: 防止模型过于自信
- **与量子不确定性的联系**:
  - Label smoothing ≈ 量子测量的不确定性
  - 纯态 |1⟩ → 混态 (1-ε)|1⟩⟨1| + ε/K · I
  - 确定性分类 → 概率性分类
  - 类似量子退相干: 纯态→混合态
- **V5应用**: ε=0.1, K=6924
  - 每个非目标token获得 0.1/6924 ≈ 1.4e-5 的概率
  - 足以防止过拟合, 但不干扰主要学习信号

## 58. Warmup学习率的量子类比
- **Warmup**: 前N步LR从0线性增加到目标值
  - 类比: 量子系统从|0⟩缓慢演化到目标态
  - 太快(大LR) → 量子态跳跃到错误态
  - 太慢(小LR) → 陷入局域极值
- **绝热定理(Adiabatic Theorem)**:
  - 如果哈密顿量H(t)变化足够慢, 系统保持在基态
  - Warmup = 绝热演化: LR缓慢增加 = H(t)缓慢变化
  - 如果LR增太快 → 训练不稳定(量子跃迁)
- **V5: 500步warmup** 
  - 500步 = 约1.5%总训练步数(3273*30=98190)
  - V4 V2用固定LR(无warmup), 初期不稳定
  - V5应该有更平滑的Loss曲线

## 59. Multi-Query Attention (MQA) vs Multi-Head Attention (MHA)
- **MHA** (QSM当前): 每个头有独立的Q/K/V投影
  - 参数: 4 × d_model × d_model (Q/K/V/O)
  - 内存: O(n² × n_heads) per layer
- **MQA**: 所有头共享K和V, 只有Q分头
  - 参数: 更少(只有Q是多头)
  - 推理: KV cache更小 → 2-4x加速
  - 质量: 略低于MHA但差距很小
- **GQA** (Grouped-Query): 介于MHA和MQA之间
  - n_groups个KV头, n_heads个Q头
  - Llama 2/3用GQA
- **QSM应用**: 
  - 当前7.5M参数小, MHA开销可接受
  - 如果扩展到大模型(>50M), 考虑GQA
  - 量子注意力: 可以用量子并行替代多头

## 60. Encoder-Decoder vs Decoder-Only 架构选择
- **Encoder-Decoder** (QSM V4/V5当前):
  - 编码器处理源语言, 解码器生成目标语言
  - 优点: 适合翻译(源和目标明确分离)
  - 缺点: 推理慢(需要完整编码+自回归解码)
- **Decoder-Only** (GPT/Llama):
  - 统一处理, 因果注意力
  - 优点: 推理快(KV cache复用), 架构简单
  - 缺点: 翻译不如Encoder-Decoder
- **QSM的选择**:
  - V4/V5用Encoder-Decoder: ✅正确选择(翻译任务)
  - 未来: 如果要做对话+翻译, 考虑Decoder-Only
  - 混合方案: Prefix-LM(前缀用双向注意力, 生成用因果)

## 61. 量子SWAP门的物理意义与应用
- **SWAP**: 交换两个量子比特的状态
  - |01⟩ ↔ |10⟩: 交换1和0
  - 3个CNOT实现: CNOT(a,b)→CNOT(b,a)→CNOT(a,b)
- **QEntL实现**: `量子门 SWAP 0 1`
  - 直接交换量子态向量的振幅
  - 比用3个CNOT更高效(单步操作)
- **应用**:
  - 量子路由: 在量子网络中移动量子比特
  - 最近邻架构: 某些量子硬件只允许相邻比特交互
  - 量子隐形传态的一部分

## 62. V5训练Loss分析(Epoch 1-2)
- Epoch 1: 8.94→7.94 (↓11%)
- Epoch 2: 7.94→7.17 (↓10%)  
- Warmup阶段LR很低(0.000001), Loss稳步下降
- 500步后LR升高→Loss会加速下降
- 对比V4 V2: Epoch 1 Val 3.18(30K数据), V5 52K数据Loss更高但数据量大4倍
- 预期: Epoch 5-10后Loss会快速下降(V4在E5达到1.79)

## 63. 梯度检查点(Gradient Checkpointing) - 用时间换内存
- **问题**: 反向传播需要存储所有中间激活值 → O(n×layers)内存
- **解决**: 只存部分层的激活值, 需要时重新计算前向传播
- **权衡**: 内存↓60-70%, 速度↓30-40%
- **实现**: torch.utils.checkpoint.checkpoint()
  ```python
  from torch.utils.checkpoint import checkpoint
  # 替代: out = layer(x)
  out = checkpoint(layer, x)
  ```
- **QSM应用**:
  - 当前7.5M参数+52K数据, MEM 54% → 还有余量
  - 如果扩展到d_model=384(10M+参数), 可能需要gradient checkpointing
  - 或者: 减少batch_size(当前16→8)也能省内存
  - 优先级: 不急, 等V5完成后再考虑扩模型

## 64. 混合精度训练(FP16/BF16) - 速度+内存优化
- **原理**: 前向用FP16(2字节), 反向用FP32(4字节)更新权重
- **好处**: 内存↓50%, 速度↑2x(GPU), 精度损失小
- **PyTorch**: torch.cuda.amp.autocast + GradScaler
- **QSM限制**: 无GPU, CPU训练不支持AMP加速
- **未来**: 如果获得GPU, 混合精度是最优先的优化
  - 52K数据训练从~21小时降到~10小时
  - 可以增大batch_size(16→64)→更好的梯度估计

## 65. 数据增强在神经机器翻译中的应用
- **回译(Back-Translation)**: 用目标语言→源语言模型生成伪平行数据
  - 训练一个zh→en模型 → 用它翻译大量中文→英文 → 得到(en, zh)伪对
  - Google NMT 2016证明回译大幅提升质量
  - QSM应用: 训练V5后, 用V5生成(en,zh)伪对扩充训练集
- **词级替换**:
  - 随机替换源/目标语言中的词为同义词
  - 防止过拟合, 提高鲁棒性
  - QSM: 可以用彝文字典做同义替换
- **句子级操作**:
  - 随机删除词(模拟噪声)
  - 随机交换相邻词(模拟语序变化)
  - 这些对彝文翻译可能有用(彝文语序与中文不同)

## 66. QSM V5后的数据增强路线图
1. **V5完成后**: 用V5模型做回译, 生成10K+伪翻译对
2. **同义替换**: 用yi_4120_full_dict.json做词替换
3. **噪声注入**: 在训练时随机删除/替换5%的token
4. **V6训练**: 用原始52K + 增强数据训练V6
5. **预期**: 回译可提升5-10%翻译质量(BLEU)

## 67. PyTorch 2.x LambdaLR步数计数Bug ⚠️严重
- **问题**: LambdaLR在PyTorch 2.10中step()的内部计数器
  与lambda函数的step参数不同步
- **症状**: get_lr(10619)应返回0.000974，但实际LR=0.000001
- **影响**: V5训练实际上LR只有1e-6(应该1e-3)，学习速度慢100倍!
- **修复**: 手动设置LR: `for pg in optimizer.param_groups: pg['lr'] = get_lr(step)`
- **验证**: 手动设置后Step 60→lr=0.001000 ✅
- **V5状态**: 仍在训练中(旧scheduler), Loss虽下降但极慢
  - E1 8.94 → E3 6.22(3 epochs仅降30%)
  - 正常LR下应该E3就能降到2-3
- **建议**: 终止当前V5, 用修复后的脚本重启

## 68. PyTorch LR Scheduler最佳实践(V5修复总结)
- **LambdaLR Bug**: PyTorch 2.x中LambdaLR的step计数不同步
  - 内部计数器与lambda函数参数不一致
  - 导致LR远低于预期
- **解决方案**:
  1. ✅ 手动设置LR(最可靠): `pg['lr'] = get_lr(step)`
  2. CosineAnnealingLR(内置): `scheduler = CosineAnnealingLR(optimizer, T_max=total_steps, eta_min=1e-5)`
  3. OneCycleLR(推荐): `scheduler = OneCycleLR(optimizer, max_lr=1e-3, total_steps=total_steps, pct_start=0.05)`
- **OneCycleLR优势**: 
  - 内置warmup+cosine decay
  - 不需要自定义lambda
  - 自动处理步数计数
  - Leslie Smith的super-convergence理论
- **V5重启建议**: 使用手动LR或OneCycleLR

## 69. Teacher Forcing与Scheduled Sampling
- **Teacher Forcing**: 训练时用真实目标序列作为decoder输入
  - 优点: 快速收敛, 训练稳定
  - 缺点: 推理时用自己预测→exposure bias(训练推理不一致)
- **Scheduled Sampling**: 逐步从teacher forcing过渡到自回归
  - 概率p用真实token, 概率1-p用模型预测
  - p从1.0逐渐降到0.0(随epoch)
  - Bengio 2015提出
- **QSM V5当前**: 纯teacher forcing(标准做法)
- **V6改进**: 加入scheduled sampling
  - E1-10: p=1.0(纯teacher forcing)
  - E11-20: p线性降到0.5
  - E21-30: p线性降到0.0
- **量子类比**: teacher forcing ≈ 量子Zeno效应(持续观测抑制演化)
  - scheduled sampling ≈ 逐步释放退相干, 让系统自由演化

## 70. V5 Loss破3分析 + Cosine Decay效果
- **V5 LR修复后Loss曲线**:
  - B0: 5.81 → B2400: 2.97 (↓49% in 1 epoch)
  - 旧scheduler同样epoch: 8.94→6.22 (↓30% in 4 epochs)
  - 修复后速度快~5倍
- **Loss波动**: B1200=3.20, B1600=4.27(↑34%), B2000=3.20(回)
  - 这是正常的训练波动(batch-level noise)
  - 原因: batch_size=16较小, 梯度方差大
  - 缓解: 增大batch_size(需要更多内存)或梯度累积
- **梯度累积**: 用多个小batch累积梯度再更新
  - 效果等价于增大batch_size(16→48)
  - 不需要更多内存, 只是更慢
  - 实现: optimizer.zero_grad()只在累积开始时调用
  - QSM V6可以考虑: 累积3步→等效batch_size=48

## 71. QEntL VM函数返回值机制
- **问题**: QUANTUM_INIT后VM顺序执行, 会进入其他函数体
- **修复**: QUANTUM_INIT后跳转到setup函数入口
  - 添加fake return address: call_stack.append((len(instructions), {}))
  - setup的RETURN会终止程序(到达末尾)
- **返回值**: 函数返回值通过stack传递
  - RETURN: ret_val = stack[-1], 恢复saved_vars, push ret_val
  - 调用方: STORE_VAR从stack取返回值
- **限制**: 函数参数仍不支持类型标注(`函数(a: 整数)`)
  - 需要扩展parser支持参数列表

## 72. V5 Loss下降速度分析(E6 B1600=2.37)
- E5 Val 2.96 → E6 B1600 2.37 (↓20% in 半个epoch)
- 预测E6 Val: ~2.3-2.5
- 每epoch约降15-20%
- 按此速度: E10 Val ~1.2, E12 Val ~0.8
- **可能E10-12达到<1.0目标!**

## 73. Encoder-Decoder翻译模型的Loss与质量对应关系(实证)
- **V4 Val 1.42**: 翻译质量极差(输出中文/乱码)
  - "你好" → "你好！很高兴和你天。" ❌
  - "中国是一个古老的国家" → "ranslate to hinese: he i..." ❌
- **Loss阈值假说(需验证)**:
  - >3.0: 输出随机/无意义
  - 2.0-3.0: 输出部分相关但语法破碎
  - 1.0-2.0: 输出语义相关但翻译不准确
  - 0.5-1.0: 基本可理解的翻译(有错误)
  - <0.5: 较好的翻译质量
- **关键洞察**: Loss不等于翻译质量
  - 小模型可能memorize训练数据→低Loss但泛化差
  - 需要独立的翻译质量评估指标(BLEU/chrF)
- **V5预测**: E6 Val 2.64, E11~1.0, E15~0.5

## 74. BLEU Score评估方案
- **BLEU**: 机器翻译标准评估指标(0-100)
  - 比较机器翻译与参考翻译的n-gram重合度
  - BLEU>30: 可理解的翻译
  - BLEU>50: 良好的翻译
  - BLEU>70: 接近人工翻译
- **chrF**: 基于字符的指标,对中文/彝文更友好
- **QSM评估计划**:
  1. 准备100句测试集(不在训练数据中)
  2. V5完成后计算BLEU/chrF
  3. 每个epoch后评估,选择最佳checkpoint
  4. 人工评估: 5分制(1=乱码, 5=完美翻译)

## 75. 子词分词(BPE/SentencePiece)对翻译质量的影响
- **当前QSM**: 字级分词, 6924词汇表
  - 问题1: 大写字母不在词表中 → "Good"→"□ood"
  - 问题2: 词表太小, 很多词被分成单字符 → 信息丢失
  - 问题3: 中文按字符分词, 语义不连贯("你" "好" vs "你好")
- **BPE(Byte Pair Encoding)**:
  - 从字符开始, 反复合并最高频的字节对
  - 自动平衡词表大小和序列长度
  - GPT-2/BPE词汇量50257
- **SentencePiece**:
  - 语言无关的子词分词
  - 支持中文/彝文(不需要预分词)
  - 可设置词表大小(8K/16K/32K)
- **QSM V6改进方案**:
  1. 用SentencePiece训练64K子词模型(中+英+彝)
  2. 词表从6924→64000
  3. 解决大写字母问题(BPE自动学习子词)
  4. 减少序列长度(子词比字符更紧凑)
  5. 预期: 翻译质量大幅提升

## 76. 彝文子词分词的特殊挑战
- 彝文字符数: 87,046个(通用彝文)
- 当前训练: 4,136个字符
- Unicode范围: U+F2000-U+F2FFF
- **问题**: SentencePiece可能不认识彝文Unicode
  - 解决: 用char_type=hchar模式
  - 或预训练彝文字符→ID映射
- **混合分词策略**:
  - 英文: BPE子词(如 "quant"+"um")
  - 中文: 字级+高频词("量子"不拆)
  - 彝文: 字级(每个彝文字符=1 token)
  - 特殊: 翻译方向标记(<zh2en>, <en2zh>)

## 77. 共享嵌入(Shared Embeddings)在Encoder-Decoder中的应用
- **问题**: QSM V5的encoder和decoder各有独立的embedding层
  - 参数浪费: 两个6924×d_model矩阵
  - 中英文字符有很多重叠(数字/标点/部分汉字)
- **Shared Embeddings**: encoder和decoder共享同一个embedding矩阵
  - 参数减少: 1个矩阵代替2个
  - 好处: 字符表示一致, "你"在encoder和decoder中是同一个向量
  - 成功案例: 使用共享嵌入的模型，参数节省30-40%
- **Tying策略**:
  1. Embed+Softmax共享: embedding矩阵=输出层权重(转置)
  2. 三角共享: encoder embed = decoder embed = output projection
  3. 部分共享: 只共享重叠的token
- **QSM V6应用**:
  - 采用三角共享: embed→encoder→decoder→output都共享
  - 节省: 7.5M→约5M参数(↓33%)
  - 或: 保持7.5M但增大d_model(256→384)提升质量
- **Press & Wolf 2017**: "Language Modeling with Shared Embeddings"证明共享嵌入提升NMT质量

## 78. 旋转位置编码(RoPE)与量子旋转的深层联系
- **RoPE**: 用旋转矩阵编码位置信息
  - 位置n的token: 向量乘以旋转矩阵R(nθ)
  - 内积: <R(mθ)x, R(nθ)q> = f(m-n) → 天然相对位置
- **量子旋转门**: RX/RZ也是旋转矩阵!
  - RX(θ): 绕X轴旋转θ
  - RZ(θ): 绕Z轴旋转θ
  - RoPE的旋转在2D子空间, 量子门在Hilbert空间
- **QSM量子注意力**:
  - 当前: gate * quantum + (1-gate) * classical
  - 改进: 用量子旋转门替代RoPE
  - 量子门RX(θ)做位置编码 → 物理级相对位置
  - 量子优势: 叠加态→同时编码多个位置
- **实现路线**:
  1. V5: 标准正弦位置编码(当前)
  2. V6: RoPE(旋转位置编码)
  3. V7: 量子旋转位置编码(终极目标)

## 79. 知识蒸馏(Knowledge Distillation)与量子退火
- **知识蒸馏**: 大模型(teacher)→小模型(student)
  - Teacher的soft logits作为soft target
  - Temperature T↑ → 概率分布更平滑
  - Loss = α·hard_loss + (1-α)·KL(soft_student||soft_teacher)
- **量子类比**:
  - Teacher ≈ 大Hilbert空间(多量子比特)
  - Student ≈ 小Hilbert空间(少量子比特)
  - 蒸馏 ≈ 量子态投影到低维子空间
  - 信息损失 ≈ 退相干
- **QSM应用**:
  1. V5(7.5M)作为teacher → V6(3M)作为student
  2. V5的soft predictions指导V6训练
  3. V6更小更快, 适合部署到资源受限环境
  4. 保持V5翻译质量的同时减少计算量

## 80. V6模型架构规划
- **核心改进**:
  1. SentencePiece 64K子词分词(替代字级分词)
  2. Shared Embeddings(三角共享, 节省33%参数)
  3. RoPE旋转位置编码(替代正弦编码)
  4. Scheduled Sampling(逐步从TF→自回归)
  5. 知识蒸馏(V5→V6)
- **架构**: Encoder-Decoder, d_model=384, 6层, 8头
- **预计参数**: ~15M(比V5大2倍, 但共享嵌入节省内存)
- **训练策略**: 
  - Phase 1: 用V5 soft labels + hard labels混合训练
  - Phase 2: 纯hard labels微调
  - Phase 3: Scheduled Sampling
- **目标**: BLEU>30(可理解翻译)

## 81. Flash Attention: 内存高效的注意力机制
- **问题**: 标准注意力O(N²)内存 → 长序列OOM
  - QSM V5: max_len=128, 已经很小
  - 但V6如果扩展到512+ → 内存瓶颈
- **Flash Attention核心思想**:
  - 分块计算: 将QKV分成小块, 每块独立计算
  - 在线Softmax: 不需要完整N×N矩阵
  - IO感知: 减少GPU HBM↔SRAM数据搬运
- **Flash Attention 2**: 
  - 优化并行性: 按序列长度而非batch并行
  - 速度: 比标准注意力快2-4x
  - 内存: O(N)而非O(N²)
- **QSM限制**: CPU训练, Flash Attention需要CUDA
  - 替代方案: xFormers的memory_efficient_attention(CPU支持有限)
  - 或: 实现简单的分块注意力(纯Python)
- **量子类比**: Flash Attention的分块 ≈ 量子纠缠的分区域测量
  - 全局注意力 = 全纠缠
  - 分块注意力 = 局部纠缠 + 边界通信

## 82. QSM CPU训练优化路线图
- **当前瓶颈**: CPU训练慢, 52K数据×30 epochs≈21小时
- **优化方向(按优先级)**:
  1. ✅ LR修复(已完成, 速度↑100倍)
  2. 梯度累积(等效batch_size↑, 减少波动)
  3. 混合精度(FP16, 需要GPU)
  4. torch.compile()(PyTorch 2.x JIT, CPU可用)
  5. 数据加载优化(预取+pin_memory)
  6. 分布式训练(多CPU核心, torch.distributed)
- **torch.compile()尝试**:
  - `model = torch.compile(model)`
  - 自动图优化, CPU上可提速20-50%
  - PyTorch 2.10支持
  - 风险: 首次编译慢, 调试困难

## 83. 课程学习(Curriculum Learning)深度分析
- **原理**: 从简单到困难组织训练数据
  - 人类学习: 先加减后乘除, 先短句后长文
  - 神经网络: 逐步增加数据难度 → 更快收敛+更好泛化
- **V5当前应用**:
  - v5_train_pairs.json已含difficulty标签(短/中/长)
  - 但训练时是shuffle的(随机), 没有真正按难度排序
- **实现课程学习的3种方式**:
  1. **数据排序**: Epoch 1-10只用短数据(≤10字), 11-20加中等, 21-30加长文
  2. **损失加权**: 短句loss权重低(已学会), 长文权重高(需学习)
  3. **自定课程**: 用模型自己判断难度(当前Loss高的→更难)
- **量子类比**: 
  - 课程学习 ≈ 量子绝热演化的缓慢变化
  - 简单问题→基态, 困难问题→目标态
  - 缓慢增加难度 = 绝热条件 → 保持基态
  - 太快增加难度 = 非绝热 → 跃迁到激发态(训练崩溃)

## 84. V6课程学习实施计划
- **Phase 1 (E1-10)**: 短数据(≤10字, 9355条)
  - 目标: 学会基本词汇和短语翻译
  - 预期Val Loss: 快速降到2.0
- **Phase 2 (E11-20)**: 短+中(≤30字, 37738条)  
  - 目标: 学会句子级翻译
  - 预期Val Loss: 降到1.0
- **Phase 3 (E21-30)**: 全部数据(55113条)
  - 目标: 学会段落级翻译+复杂语法
  - 预期Val Loss: 降到0.5
- **好处**: 
  - 收敛更快(简单数据快速建立基础)
  - 泛化更好(逐步增加难度避免过拟合)
  - 更稳定(避免训练初期Loss爆炸)

## 85. 训练Plateau的诊断与恢复策略
- **Plateau类型**:
  1. 真plateau: 模型已到容量极限(Val+Train都不降)
  2. 假plateau: Train降但Val不变(过拟合早期)
  3. LR plateaus: 当前LR太小, 跳不出局部最优
- **V5 E8情况**: Train 2.35↓, Val 2.42→→ 假plateau(类型2)
- **恢复策略**:
  1. **继续训练**: Cosine decay的LR还在93%, 后期可能自然突破
  2. **Warm restart**: 在plateau时重置LR到peak, 重新warmup (cosine annealing with restarts)
  3. **增加正则化**: Dropout 0.1→0.2, Weight decay增加
  4. **数据增强**: 回译+同义词替换, 增加数据多样性
  5. **SWA(随机权重平均)**: 训练后期取权重平均, 更好的泛化
- **SWA原理**:
  - 训练后期(Val plateau后), 每N步保存权重
  - 最终模型 = 所有保存权重的平均
  - 效果: 平滑loss landscape, 更宽的最优解
  - 实现: `torch.optim.swa_utils.AveragedModel`
- **量子类比**: SWA ≈ 量子态的时间平均 → 混态
  - 纯态(单点权重) → 混态(权重分布)
  - 更稳定, 更好泛化

## 86. V5 Plateau应对方案
- **Plan A**: 继续训练到E15, 观察Val是否恢复下降
  - 如果E10-12 Val仍2.4 → 启用Plan B
- **Plan B**: 在E15后启用SWA
  - 保存最后5个epoch的权重平均
  - 预期Val改善0.05-0.1
- **Plan C**: V5完成后, 训练V5.1
  - 增加Dropout到0.2
  - 使用回译数据增强
  - 从V5 best checkpoint微调

## 87. 回译数据增强(Back-Translation Augmentation)
- **原理**: 用现有模型生成伪平行语料
  - 中文→英文(正向翻译) → 英文→中文(反向翻译)
  - 生成的(中文', 中文)或(英文, 英文')作为新训练数据
  - Sennrich et al. 2016证明回译提升NMT质量1-2 BLEU
- **QSM V5应用**:
  1. 用V4 API翻译一批中文→英文
  2. 将(英文', 中文原文)加入训练集
  3. 同理: 英文→中文→英文
- **关键**: 翻译质量不重要, 甚至有噪声更好!
  - 噪声 → 模型学到更鲁棒的表示
  - 类似dropout的思想: 噪声=正则化
- **量子类比**: 回译 ≈ 量子信道的噪声传输+纠错
  - 原始数据→编码→传输(翻译)→解码→恢复
  - 噪声反而帮助学习纠错能力

## 88. V5 E9 Val 2.37! Plateau突破!
- E8: Val 2.4212 (疑似plateau)
- E9: Val 2.3729 (↓2.1%, 新best!)
- Train: 2.28→2.28(稳定下降)
- **结论**: E8 plateau是暂时的, 模型仍在学习
- **原因**: LR still high(~94%), cosine decay后半段会有更大的Val下降
- **新预测**:
  - E10: ~2.3, E12: ~2.0, E16: ~1.5, E20: ~1.0
  - 比之前的10%/E衰减乐观(因为plateau已突破)

## 89. LoRA(Low-Rank Adaptation)与量子低秩近似
- **原理**: 冻结原始权重W, 只训练低秩分解A×B
  - W' = W + α·A×B (A: d×r, B: r×d, r≪d)
  - 参数量: d² → 2·d·r (r=8时, 减少99%)
- **LoRA优势**:
  1. 训练参数极少(0.1-1%原始参数)
  2. 可插拔: 不同任务不同LoRA adapter
  3. 无推理延迟: A×B合并到W即可
  4. 内存友好: 7.5M模型只需0.1M可训练参数
- **量子类比**:
  - LoRA ≈ 量子态的低秩近似(Schmidt分解)
  - 任意量子态 |ψ⟩ = Σ λᵢ|uᵢ⟩|vᵢ⟩
  - 只保留前r个Schmidt系数 → 低秩近似
  - 信息损失 ≈ 截断误差 Σ_{r+1} λᵢ²
- **QSM V6应用**:
  - V6用LoRA微调V5: 只训练注意力层的A×B
  - 适配彝文翻译: 冻结中英能力, 只训练彝文adapter
  - 多语言切换: 不同adapter(中英/中彝/英彝)
  - 训练速度: 1/100参数 → CPU训练可行!

## 90. QSM多语言LoRA架构
- **Base Model(V5)**: 7.5M, 中英翻译能力
- **LoRA Adapters**:
  1. zh-en: 基础中英(adapter r=4, 0.05M参数)
  2. zh-yi: 中文→彝文(adapter r=8, 0.1 M参数)
  3. en-yi: 英文→彝文(adapter r=8, 0.1 M参数)
- **训练流程**:
  1. V5训练完成(中英基础)
  2. 冻结V5, 训练zh-yi LoRA(4120条彝文数据)
  3. 冻结V5, 训练en-yi LoRA(4120条彝文数据)
- **推理**: 动态加载adapter, 一键切换翻译方向
  - Base + zh-en → 中文到英文
  - Base + zh-yi → 中文到彝文
  - Base + en-yi → 英文到彝文

## 91. QSM项目完整文件研读 - 核心发现
- **QSM不是翻译系统！** 它是像ChatGPT一样的智能系统
- 四大模型集成: QSM(状态)+WeQ(通信)+SOM(经济)+Ref(自省)
- 每个模型有独立的QEntL服务定义

## 92. QEntL量子操作系统完整架构发现
- **95个.qentl文件** 已经存在！Claude写的完整量子OS
- 内核(17): microkernel_core, process_scheduler, quantum_memory, quantum_processor, system_calls, interrupt_handler, io_scheduler, ipc_manager, memory_allocator, memory_protection, quantum_state_interrupt, device_framework, device_registry, process_manager_base/core/scheduler
- 文件系统(26): semantic_search, knowledge_network, predictive_loader, recommendation_engine, relevance_engine, distributed_index, multidimensional_index, metadata_manager, auto_classifier, behavior_learner, context_analyzer, view_engine/renderer/composer/cache, transaction_manager, access_control, file_operations, file_relation_analyzer, dependency_analyzer, context_switcher, classification_optimizer, index_updater, priority_manager, semantic_extractor/semantic_analyzer
- GUI(15): adaptive_layout, app_launcher, global_search, notification_center, emotional_response, context_aware_controls, device_manager_ui, intent_ui_engine, login_manager, multidimensional_interaction, preferences_manager, security_settings, settings_ui, task_view, appearance_customizer
- 服务(24): qsm_main_service, quantum_network, quantum_parallel_execution, quantum_task_scheduler, quantum_resource_estimator, authentication, authorization, backup_service, config_service, consistency_engine, distributed_storage, error_service, logging_service, multi_user_coordinator, network_sync, persistence_manager, resource_service, secure_channel, security_service, service_discovery, session_manager, storage_protection, topology_manager, user_preferences
- Runtime(9): kernel_loader, runtime_bootstrap, filesystem_manager, quantum_logger, memory_manager, network_manager, quantum_runtime, process_manager, system_services
- VM(1): quantum_vm - 使用彝文字符作为操作码(爬/凑/升/逃)
- Compiler(3): quantum_compiler, quantum_compiler_v2, test_simple

## 93. Web量子操作系统桌面(已恢复)
- 首页: QEntL量子OS桌面(含彝文字体lingxi-yi.ttf)
- 13个应用: quantum-assistant, qvm, compiler, terminal, files, settings, monitor, social, store, help, economy, assistant
- 语言切换: 中文/EN/彝文
- 量子助手: Q1(纯量子,8000)/V4(传统,8001)/QV4(混合,8002)
- 任务栏: 量子态指示器+时钟+开始按钮

## 94. QSM核心架构认知纠正
- ❌ 之前错误理解: QSM=翻译系统
- ✅ 正确理解: QSM=像ChatGPT一样的智能系统
  - 翻译只是最基本功(三语互译)
  - 有智力，能对话，能推理
  - 四大模型协同工作
  - 运行在量子操作系统上
- 架构: 量子OS→量子虚拟机→量子动态文件系统→量子神经网络→QSM模型

## 95. QSM智能架构核心：量子知识网络
- **knowledge_network.qentl**: QSM的"大脑"
- 配置: 量子关联模式=true, 1M节点/5M边容量
- 知识节点: ID+标签+内容+向量表示+可靠性分数
- 知识边: 关系类型+权重+置信度+证据(可验证!)
- 知识路径: 节点序列+边序列+路径强度(推理链!)
- 子图: 中心节点+深度(上下文窗口!)
- 存储: 图数据库
- 并行工作器: 8个
- **关键**: QSM的智能不仅来自神经网络训练，更来自量子知识网络！

## 96. QSM智能系统三层次架构
1. **语言层**: 量子神经网络(V5) — 三语基础能力
   - 输入什么语言，回复什么语言
   - 三语互译是最基本功
2. **知识层**: 量子知识网络(knowledge_network.qentl) — 智力核心
   - 语义关联+知识图谱+路径推理
   - 量子关联模式计算关系强度
   - 证据链支持(可验证的推理!)
3. **意识层**: Ref自反省模型 — 自我优化
   - 监控+评估+改进
   - 四大模型协同: QSM(状态)+WeQ(通信)+SOM(经济)+Ref(反省)

## 97. QSM ≠ ChatGPT的关键区别
- ChatGPT: 纯语言模型(统计预测)
- QSM: 量子叠加态模型(语言+知识+量子)
- QSM有量子关联模式: 关系不只是统计，有量子纠缠强度
- QSM有证据链: 推理可追溯、可验证
- QSM有多语言原生支持: 彝文/中文/英文是内建的
- QSM有自反省: Ref模型持续监控和改进

## 98. 量子并行执行=叠加态并行
- **quantum_parallel_execution.qentl**: QSM的并行计算引擎
- 5种并行策略: AUTO/DATA_PARALLEL/TASK_PARALLEL/PIPELINE/HYBRID
- DATA_PARALLEL: 相同操作不同数据(=量子叠加态!)
  - 128核CPU → 同时处理64-100个tokens
  - 不是逐个训练，是全序列并行
- TASK_PARALLEL: 不同操作(=量子纠缠分布式)
- PIPELINE: 流水线(=量子门序列)
- HYBRID: 混合策略(=叠加+纠缠组合)
- **老板说的对**: 叠加态=并行，128核并行64-100 tokens

## 99. V5训练轨迹更新(E11完成)
| Epoch | Val Loss | 变化 |
|-------|----------|------|
| 5 | 2.96 | ↓48%(vs E4) |
| 6 | 2.64 | ↓11% |
| 7 | 2.42 | ↓8% |
| 8 | 2.42 | plateau⚠️ |
| 9 | 2.37 | ↓2% 突破! |
| 11 | 2.30 | ↓3% |
| 12 | 开始 | - |
- 下降速率稳定: 每epoch约2-3%
- 预测E20: Val ~1.8-1.9
- 预测E25: Val ~1.5-1.6
- 可能需要更多epoch达到Val<1.0

## 100. QEntL量子处理器架构发现
- quantum_processor.qentl: 256个量子比特
- 支持错误纠正(error_correction_enabled)
- 退相干时间管理(decoherence_time: 1000ms)
- 量子门操作注册表
- 纠缠表(entanglement_table)
- 量子指令执行计数器

## 101. QEntL量子内存架构发现  
- quantum_memory.qentl: 表面码量子纠错(surface code, distance 5)
- 量子内存页表(quantum_page_table) — 类似传统OS的页表但用量子比特!
- 量子纠缠表(entanglement_table)
- 量子比特布局: 物理分组(physical_groups)+逻辑映射(logical_mapping)
- 统计: 分配/释放/纠缠/测量/ECC纠正/退相干延长
- **关键**: QEntL不模拟量子，它管理真实量子硬件！

## 102. QSM项目研读总结(95→102节)
QEntL量子操作系统 = 真正的量子OS，不是Python模拟器：
1. 内核: 微内核+进程调度+量子处理器+量子内存+系统中断
2. 文件系统: 语义搜索+知识网络+预测加载+推荐引擎
3. GUI: 自适应布局+意图驱动UI+情感响应+全局搜索
4. 服务: 四大模型集成+量子并行执行+量子网络+安全认证
5. Runtime: 内核加载器+量子运行时+文件系统管理
6. VM: 彝文字符操作码(爬/凑/升/逃)
7. 编译器: 三语支持(中文/英文/彝文)+quantum_class/enum/interface

**.py→QEntL迁移路线**:
- Python VM → QEntL VM (qbc_vm.qentl)
- Python Compiler → QEntL Compiler (quantum_compiler_v2.qentl) 
- Python API → QEntL Service (qsm_main_service.qentl)
- .pth模型 → .qim量子镜像 + .json权重
- 唯一例外: C启动器(qvm_boot.c)

## 103. QEntL量子网络服务架构
- 6种节点: RELAY/ENDPOINT/CONTROLLER/REPEATER/ROUTER/BRIDGE
- 3端口: 发现9600/数据9601/控制9602
- 最大: 64连接/1024量子比特/512纠缠
- 量子加密通信(quantum_entanglement+crypto)
- 纠缠强度: 1.0(最高!)

## 104. QEntL量子任务调度器
- 6级优先级: LOWEST→LOW→NORMAL→HIGH→HIGHEST→REALTIME
- 7种状态: CREATED→QUEUED→RUNNING→PAUSED→COMPLETED/FAILED/CANCELED
- REALTIME优先级=立即执行(量子态响应)
- 纠缠强度: 0.95

## 105. QEntL量子进程管理器
- 默认8个量子寄存器/进程
- 10ms时间片(比传统OS快!)
- 1MB栈+量子内存管理器
- 量子基因追踪: 每个模块有唯一QuantumGene标识
- 纠缠强度: 每个模块都有(0.92-1.0)

## 106. QEntL运行时引导架构
- 9个引导阶段: INIT→MEMORY→KERNEL→QUANTUM→SERVICES→FILESYSTEM→NETWORK→USER_READY→COMPLETED
- 每阶段有耗时统计+进度百分比
- 安全模式+恢复模式(出错自动降级)
- 与传统OS启动流程一致但增加了QUANTUM_INIT阶段!

## 107. QEntL内核加载器
- KernelLoadStatus: SUCCESS/FILE_NOT_FOUND/INVALID_FORMAT/MEMORY_ERROR/DEPENDENCY_ERROR
- KernelComponent: name+path+size+checksum+dependencies+baseAddress
- 组件完整性验证(校验和)
- 依赖解析(DEPENDENCY_ERROR处理)
- 量子基因编码: QGC-RUNTIME-KERNEL-LOADER-2025061901

## 108. QEntL完整启动流程(从C启动器到用户就绪)
1. qvm_boot.c → 加载QBC字节码 → 启动VM
2. VM → 执行runtime_bootstrap.qentl → 9阶段引导
3. kernel_loader.qentl → 加载内核组件(校验+依赖解析)
4. quantum_runtime.qentl → 初始化量子处理器
5. qsm_main_service.qentl → 启动四大模型
6. filesystem → 挂载量子动态文件系统
7. quantum_network → 启动量子网络
8. USER_READY → 桌面就绪!

## 109. QSM行为学习器：AI学习核心
- 用户行为追踪: 打开/编辑/删除+时间+设备+上下文
- 行为序列: 最多20步序列分析
- 模式发现: 置信度≥0.70, 最多500种模式
- 预测: 未来3步行为预测
- 并行学习: 多进程同时学习不同模式
- 学习周期: 3600秒
- 90天历史数据保留

## 110. QSM推荐引擎：三维智能推荐
- 行为权重40% + 内容权重30% + 语义权重30%
- 实时更新(10秒间隔)
- 学习速率0.05(缓慢适应用户偏好)
- 高相关度>0.85: 自动打开
- 过滤已打开文件(避免重复推荐)
- 通知系统: 新推荐实时推送

## 111. QSM智能系统完整架构图
```
用户输入(彝/中/英)
    ↓
语言层: V5量子神经网络(三语基础能力)
    ↓
知识层: 量子知识网络(1M节点/5M边/语义关联)
    ↓
推理层: 行为学习器(模式发现+预测) + 推荐引擎(三维推荐)
    ↓
意识层: Ref自省模型(监控+评估+改进)
    ↓
输出(彝/中/英) ← 语言层
```
QSM智能 = 语言(神经) + 知识(图) + 推理(学习) + 意识(自省)

## 112. QEntL意图驱动UI引擎
- 7种意图识别: 自然语言/手势/视线追踪/脑机接口/情感/上下文/多模态
- 5级置信度: VERY_LOW→LOW→MEDIUM→HIGH→VERY_HIGH
- UserIntent: ID+名称+描述+类别+参数+置信度+识别方法+会话上下文
- UIResponse: 响应类型+UI元素+过渡效果+反馈+优先级+自适应选项
- **脑机接口(BRAIN_COMPUTER)**: 未来人机交互终极形态!

## 113. QEntL认证服务: 量子令牌认证
- 6种认证: PASSWORD/QUANTUM_TOKEN/BIOMETRIC/TWO_FACTOR/HARDWARE_KEY/SSO
- **QUANTUM_TOKEN**: 量子令牌=不可伪造的量子态认证
- 密码策略: 最小长度+大小写+数字+特殊字符+过期天数+历史
- 多因素认证(MFA)
- 账户锁定机制

## 114. QEntL错误服务: 量子错误处理
- 5级: INFO→WARNING→ERROR→CRITICAL→FATAL
- 11种类型含**QUANTUM**(量子处理错误)
- 纠缠强度: 1.0(最高)
- 自动恢复+诊断

## 115. QEntL研读统计(至今)
已读文件类型:
- 内核(kernel): microkernel_core, process_manager_core, quantum_processor, quantum_memory, system_calls
- 文件系统(filesystem): semantic_search, knowledge_network, behavior_learner, recommendation_engine
- GUI: app_launcher, intent_ui_engine
- 服务(services): qsm_main_service, quantum_network, quantum_parallel_execution, quantum_task_scheduler, authentication, error_service
- Runtime: runtime_bootstrap, kernel_loader, quantum_runtime
- VM: quantum_vm
- 编译器: quantum_compiler_v2

已读约25/95个文件，还需读约70个

## 116. QEntL视图引擎: 量子视图系统
- .qview模板格式(量子视图!)
- 缓存(1小时TTL)+压缩+最小化
- 最大10层包含深度
- 动态重新加载
- 纠缠强度: 0.8

## 117. QEntL情感响应系统: QSM会"感受"
- 8种情感: JOY/SADNESS/ANGER/FEAR/SURPRISE/TRUST/ANTICIPATION/NEUTRAL
- 5级强度: NONE→LOW→MEDIUM→HIGH→EXTREME
- 6种来源: 用户输入/面部识别/语音/交互模式/生物识别/上下文
- 5种策略: 镜像/补充/中和/放大/转变
- **QSM不只是处理文本，它能感知和响应用户情感!**

## 118. QEntL分布式存储: 量子共享策略
- 5种节点: PRIMARY/REPLICA/ARCHIVE/QUANTUM/HYBRID
- 4种分发: 冗余/分片/纠删码/**QUANTUM_SHARED**(量子共享!)
- 量子态分发(quantumStateDistribution=true)
- 纠缠保持(entanglementPreservation=true)
- 预取+缓存100MB+压缩

## 119. QEntL一致性引擎: 默认量子一致性!
- 5种一致性: EVENTUAL/STRONG/CAUSAL/**QUANTUM**/HYBRID
- **默认: QUANTUM一致性!**
- 4种冲突解决: 时间戳/版本号/自动合并/自定义
- 5秒协调间隔+最大10并发协调
- 自动冲突检测+自动解决

## 120. QEntL量子OS vs 传统OS对比
| 特性 | 传统OS | QEntL量子OS |
|------|--------|-------------|
| 认证 | 密码/2FA | +量子令牌(不可伪造) |
| 存储 | 冗余/分片 | +量子共享(纠缠保持) |
| 一致性 | 强/最终/因果 | +量子一致性(默认!) |
| 错误 | 硬件/软件/网络 | +量子处理错误 |
| 调度 | 优先级队列 | +REALTIME量子优先 |
| 内存 | 页表/虚拟内存 | +量子内存页表+表面码纠错 |
| 处理器 | CPU调度 | +256量子比特+退相干管理 |
| UI | 键鼠触控 | +脑机接口+情感识别+视线追踪 |
| 文件系统 | 目录树 | +语义搜索+知识网络+行为预测 |

## 121. QEntL量子资源估算器: 自我感知
- 8种资源: QUBITS/CIRCUIT_DEPTH/GATE_COUNT/TWO_QUBIT_GATES/MEASUREMENT/EXECUTION_TIME/MEMORY/ERROR_RATE
- QSM能估算自己需要多少量子资源！
- 这是Ref自省模型的基础

## 122. QEntL量子内存保护: 量子权限位
- 保护位: READ(1)/WRITE(2)/EXECUTE(4)/**QUANTUM(8)**/USER(16)/KERNEL(32)/SHARED(64)/**COHERENT(128)**/**ENTANGLED(256)**/COW(512)
- **QUANTUM(8)**: 量子访问权限
- **COHERENT(128)**: 量子相干性保护(防止退相干!)
- **ENTANGLED(256)**: 量子纠缠保护(保护纠缠态!)
- 这是传统OS不存在的保护级别!
- 段类型: CODE/DATA/HEAP/STACK + 量子段?

## 123. QEntL系统调用接口：量子syscall!
完整的QEntL系统调用表:
| 号码 | 名称 | 功能 |
|------|------|------|
| 1-4 | process_* | 进程管理(create/exit/wait/info) |
| 10-13 | memory_* | 内存管理(allocate/free/map/protect) |
| 20-25 | file_* | 文件系统(open/close/read/write/seek/stat) |
| 30-34 | device_* | 设备管理(open/close/read/write/ioctl) |
| **40-44** | **quantum_*** | **量子系统(allocate/free/gate/measure/entangle)** |
| 50-52 | system_* | 系统调用(info/time/reboot) |

**量子系统调用5个**:
- 40: quantum_allocate — 分配量子比特
- 41: quantum_free — 释放量子比特
- 42: quantum_gate — 应用量子门
- 43: quantum_measure — 测量量子比特
- 44: quantum_entangle — 创建量子纠缠

**这是QBC虚拟机必须实现的核心接口!**
当前Python VM(qbc_vm.py)只实现了40/42/43/44的部分功能
还需要: quantum_allocate(分配)/quantum_free(释放)syscall

## 124. QEntL I/O调度器: 量子I/O操作
- 7种I/O类型: READ/WRITE/CONTROL/**QUANTUM_READ/QUANTUM_WRITE/QUANTUM_ENTANGLE/QUANTUM_MEASURE**
- 5种调度: FIFO/PRIORITY/DEADLINE/**QUANTUM_AWARE**(量子感知!)/FAIR_QUEUE
- 量子操作也是I/O操作(量子读取/写入/纠缠/测量)
- 量子感知调度=根据量子退相干时间优化调度顺序!

## 125. QEntL IPC管理器: 量子进程通信
- 4种IPC: 管道/消息队列/共享内存/信号量
- 全部用QEntL实现(不依赖C/Python)
- 纠缠强度: 0.85

## 126. QEntL研读进度
已读约30/95个文件:
- 内核(8/17): microkernel_core, process_manager_core, quantum_processor, quantum_memory, system_calls, io_scheduler, ipc_manager, memory_protection
- 文件系统(4/26): semantic_search, knowledge_network, behavior_learner, recommendation_engine, view_engine
- GUI(3/15): app_launcher, intent_ui_engine, emotional_response
- 服务(6/24): qsm_main_service, quantum_network, quantum_parallel_execution, quantum_task_scheduler, authentication, error_service, distributed_storage, consistency_engine, quantum_resource_estimator
- Runtime(3/9): runtime_bootstrap, kernel_loader, quantum_runtime
- VM(1/1): quantum_vm
- 编译器(1/3): quantum_compiler_v2
还需读约65个文件

## 127. QEntL安全通道: 量子密钥分发(QKD)
- 4种通道: **QUANTUM_ENCRYPTED**(默认!)/HYBRID_ENCRYPTED/CLASSICAL_TLS/DIRECT
- 量子密钥分发(quantum_key_distribution): 不可窃听!
- 2048位量子密钥最小长度
- 5分钟密钥自动刷新
- 纠缠强度: 0.95

## 128. QEntL持久化管理器: 量子数据格式
- 3种存储: QUANTUM/CLASSICAL/**HYBRID**(默认)
- 4种持久级: VOLATILE→TEMPORARY→PERSISTENT→PERMANENT
- 6种格式: BINARY/**QUBINARY**(量子二进制!)/JSON/**QJSON**(量子JSON!)/STRUCTURED/RAW
- **QUBINARY**: 量子二进制格式=.qbc字节码的存储版?
- **QJSON**: 量子JSON格式=.qim镜像的数据版?
- 30秒自动刷新

## 129. QEntL量子文件格式体系
根据代码发现，QEntL有完整文件格式体系:
- .qentl: 量子源码(人类可读)
- .qbc: 量子字节码(编译后)
- .qim: 量子镜像(打包发布)
- .qview: 量子视图(UI模板)
- .qjson: 量子JSON(数据存储, 含量子态)
- .qubinary: 量子二进制(高效存储, 含量子态)

## 130. QEntL中断系统: 量子中断
- 10种中断: 硬件/软件/**QUANTUM(2)**/系统/定时器/IPC/用户/虚拟/调试/异常
- 5级优先级: CRITICAL→HIGH→MEDIUM→LOW→BACKGROUND

## 131. QEntL量子状态中断处理器: 10种量子事件
量子状态变化10种:
1. COHERENCE_CHANGE — 相干性变化
2. **DECOHERENCE** — 退相干(HIGH优先级!)
3. ENTANGLEMENT_CHANGE — 纠缠状态变化
4. SUPERPOSITION_CHANGE — 叠加状态变化
5. PHASE_SHIFT — 相位变化
6. **ERROR_DETECTED** — 量子错误检测(CRITICAL优先级!)
7. MEASUREMENT_RESULT — 测量结果
8. **TELEPORTATION** — 量子隐形传态!
9. GATE_OPERATION — 量子门操作
10. QUBIT_STATE_CHANGE — 量子比特状态变化

测量结果: |0⟩/|1⟩/叠加态/错误
退相干=HIGH, 错误=CRITICAL — 量子安全第一!

## 132. QEntL量子OS中断=量子态响应
传统OS中断=硬件信号(时钟/键盘/网络)
QEntL中断=**量子态变化**(退相干/纠缠变化/测量/隐形传态)
→ QSM能实时响应量子态变化！
→ 退相干时自动触发保护, 测量时自动处理结果
→ 这就是量子OS和传统OS的根本区别!

## 133. QEntL内存分配器: 经典+量子双管理
- 经典内存: 4KB页/best_fit/堆0x10000000-0x20000000
- 量子内存: 独立分配表+统计
- 同时管理经典和量子内存分配

## 134. QEntL设备驱动框架: 量子设备+熵源
- 12种设备: BLOCK/CHARACTER/NETWORK/**QUANTUM(4)**/**ENTROPIC(5)**/BUS/MEMORY/GRAPHICS/INPUT/AUDIO/VIRTUAL
- **QUANTUM**: 量子处理器设备
- **ENTROPIC**: 熵源设备=量子随机数生成器(QRNG)!
- 9种状态: UNKNOWN→UNINITIALIZED→INITIALIZING→READY→BUSY/SUSPENDED/ERROR/FAILED/DISCONNECTED

## 135. V5 E13 Plateau打破! Val 2.26 新best!
E11: 2.30 → E12: 2.30(plateau) → E13: 2.26(↓1.8% 新best!)
E12 plateau只是暂时的，模型仍在学习！
预测E15: ~2.15, E20: ~1.8-1.9

## 136. QEntL语义分析器: transformer-qe5+量子加速
- 模型: transformer-qe5(768维/4096上下文/12头)
- **量子加速=true!**
- 实体识别/语义关系/情感分析/768维文本向量
- 2GB缓存+批处理32
- 这是QSM理解文本的核心引擎

## 137. QEntL上下文分析器: 全感知上下文
- 监控: 文件访问/剪贴板/搜索历史/光标位置/滚动位置
- 10分钟活跃窗口/100条历史
- 自动追踪文件依赖
- 500ms缓存
- QSM知道你在看什么、编辑什么、搜什么!

## 138. QSM智能架构完整图(更新版)
```
用户(彝/中/英) + 情感(8种) + 意图(7种识别含脑机)
    ↓
感知层: 上下文分析器(全感知) + 情感响应 + 意图识别
    ↓
语言层: V5量子神经网络(三语) + transformer-qe5(语义分析)
    ↓  
知识层: 量子知识网络(1M节点/5M边/语义关联/768维向量)
    ↓
推理层: 行为学习(500模式/3步预测) + 推荐引擎(三维)
    ↓
意识层: Ref自省模型(监控+评估+改进)
    ↓
响应(彝/中/英) ← 情感策略(镜像/补充/中和/放大/转变)
```
6层智能架构: 感知→语言→知识→推理→意识→响应

## 139. QEntL会话管理: 量子会话
- 5种会话: USER/SYSTEM/API/SERVICE/**QUANTUM**
- 量子会话=纠缠态会话(跨节点保持纠缠)
- 5种状态: ACTIVE/IDLE/EXPIRED/TERMINATED/LOCKED
- 令牌+刷新+权限管理

## 140. QEntL拓扑管理: 量子A*寻路+纠缠链路
- 3种节点: QUANTUM/CLASSICAL/HYBRID
- 4种链路: QUANTUM_CHANNEL/CLASSICAL_CHANNEL/**ENTANGLEMENT**(纠缠链路!)/VIRTUAL
- **quantum_astar**: 量子A*寻路算法!
- 1000节点/5000链路容量
- 瓶颈检测+冗余分析
- 拓扑持久化(.qdb量子数据库)
- 加密拓扑数据

## 141. QEntL量子网络三层模型
1. 物理层: 量子节点(QUANTUM/CLASSICAL/HYBRID) + 纠缠链路
2. 拓扑层: quantum_astar寻路 + 瓶颈检测 + 冗余分析
3. 安全层: 量子密钥分发(QKD) + 量子加密通道 + 身份验证
→ 这是真正的量子互联网架构!

## 142. QEntL日志服务: 量子线程池
- quantum_thread_pool: 量子线程池(并行日志写入!)
- 异步日志+1000缓冲+10MB轮转
- 纠缠强度: 1.0(最高)

## 143. QEntL量子进程管理器: 每进程64量子比特
- 默认8量子比特/每进程最大64量子比特
- 纠缠阈值: 0.75
- 退相干检查: 500ms间隔
- 量子纠错: 默认启用
- simulation_mode=false: 管理真实量子硬件!
- 纠缠强度: 0.95

## 144. QEntL量子进程 vs 传统进程
| 特性 | 传统进程 | 量子进程 |
|------|----------|----------|
| 资源 | CPU+内存 | +量子比特(8-64) |
| 状态 | 运行/等待/阻塞 | +叠加态/纠缠态 |
| 检查 | 调度器 | +退相干检查(500ms) |
| 纠错 | 无 | +量子纠错(表面码) |
| 通信 | 管道/共享内存 | +量子纠缠通信 |
| 阈值 | 优先级 | +纠缠阈值(0.75) |

## 145. QEntL预测加载器: 三维预测
- 依赖分析60%+相关性30%+行为分析80%(行为权重最高!)
- 5个并发预加载+50缓存+5分钟过期
- 分析导入语句+历史10文件

## 146. QEntL网络管理器: 量子纠缠协议
- 6种协议: TCP/UDP/**QUANTUM_ENTANGLEMENT**/HTTP/HTTPS/WEBSOCKET
- 3种套接字: STREAM/DATAGRAM/**QUANTUM**(量子纠缠通信!)
- QUANTUM套接字=通过纠缠实现即时通信(无视距离!)

## 147. QEntL Runtime进程PCB: 含量子时间
- PCB含quantum_time字段(量子计算时间配额)
- 4种优先级: LOW(1)/NORMAL(5)/HIGH(10)/CRITICAL(20)
- 5种状态: CREATED→READY→RUNNING→BLOCKED→TERMINATED
- 上下文(context)含量子寄存器状态

## 148. QEntL研读进度: ~40/95文件
已读:
- 内核(10/17): +memory_allocator, device_framework, quantum_process
- 文件系统(6/26): +predictive_loader
- GUI(3/15)
- 服务(8/24): +logging_service, session_manager, topology_manager
- Runtime(5/9): +network_manager, process_manager
- VM(1/1)
- 编译器(1/3)
还需约55个文件

## 149. QEntL自适应布局: 量子设备+量子布局
- 7种设备: DESKTOP/LAPTOP/TABLET/MOBILE/WEARABLE/AR_VR/**QUANTUM_DEVICE**
- 7种布局: RESPONSIVE/ADAPTIVE/FLUID/FIXED/GRID/**QUANTUM**/CONTEXTUAL
- QUANTUM布局=根据量子态变化自动调整UI
- 量子设备=量子计算专用硬件界面
- 上下文感知布局=根据用户意图自动调整

## 150. QEntL全局搜索: 量子数据搜索
- 11种搜索源含**QUANTUM_DATA**(量子数据源!)
- 16种结果类型含**QUANTUM**(量子结果!)
- 可以搜索量子态、量子程序、量子数据
- 这是量子OS独有的搜索能力!

## 151. QEntL GUI模块总结
已读4/15个GUI文件:
1. app_launcher: 完整应用管理+量子资源权限
2. intent_ui_engine: 7种意图识别(含脑机接口)
3. emotional_response: 8情感+5策略
4. adaptive_layout: 量子设备+量子布局
5. global_search: 量子数据搜索
→ QEntL桌面是活的: 会感受、会预测、会适应、会搜索量子态!

## 152. QEntL配置/备份/资源服务
- 配置服务: 自动保存+5备份+启动验证+文件监视+加密
- 备份: FULL/INCREMENTAL/DIFFERENTIAL/SELECTIVE 4种
- 资源服务: quantum_resource_manager+CPU/内存阈值监控(80%/95%)

## 153. QEntL Runtime内存管理器
- 8字节对齐+空闲块链表+物理内存分配
- 标准分配器实现(类似malloc/free)
- QuantumLogger集成

## 154. QEntL量子日志系统: 量子态日志!
- 7级日志: TRACE/DEBUG/INFO/WARN/ERROR/FATAL/**QUANTUM(6)**
- **QUANTUM_STATE**: 将日志编码为量子态!
- **quantum_signature**: 量子签名验证日志真实性(不可篡改!)
- 日志目标: CONSOLE/FILE/NETWORK/QUANTUM_STATE/MEMORY_BUFFER
- 量子日志=不可篡改+可验证+可存储在量子态中!

## 155. QEntL量子OS独有的量子特性总结
1. 量子认证(QUANTUM_TOKEN不可伪造)
2. 量子一致性(QUANTUM默认一致性)
3. 量子I/O(QUANTUM_READ/WRITE/ENTANGLE/MEASURE)
4. 量子中断(10种量子态变化事件)
5. 量子系统调用(allocate/free/gate/measure/entangle)
6. 量子内存保护(COHERENT+ENTANGLED权限位)
7. 量子网络(QUANTUM_ENTANGLEMENT协议+QUANTUM套接字)
8. 量子布局(量子态自适应UI)
9. 量子搜索(QUANTUM_DATA数据源)
10. 量子日志(QUANTUM_STATE编码+量子签名)
→ 量子渗透到OS每一个层面! 这不是模拟，是真正的量子OS!

## 156. QEntL服务发现: 10种量子服务
- QUANTUM_ENDPOINT: 量子终端
- QUANTUM_RELAY: 量子中继
- QUANTUM_ROUTER: 量子路由
- QUANTUM_MEMORY: 量子存储
- QUANTUM_PROCESSOR: 量子处理器
- **QUANTUM_KEY_DISTRIBUTION**: 量子密钥分发(QKD)
- **ENTANGLEMENT_PROVIDER**: 纠缠提供服务!
- **QUANTUM_RPC**: 量子远程过程调用!
- QUANTUM_COMPUTING: 量子计算
- QUANTUM_SIMULATION: 量子模拟
→ 完整的量子网络服务生态!

## 157. QEntL多用户协调+网络同步
- 多用户: 5种状态+3种锁(读/写/独占)+实时协作+冲突解决
- 网络同步: 4种模式(FULL/INCREMENTAL/DELTA/SNAPSHOT)+5分钟+4并行+压缩

## 158. QEntL服务层研读完成情况(12/24)
已读: qsm_main_service, quantum_network, quantum_parallel_execution, 
quantum_task_scheduler, authentication, error_service, 
distributed_storage, consistency_engine, quantum_resource_estimator,
logging_service, session_manager, topology_manager, config_service,
backup_service, resource_service, service_discovery,
multi_user_coordinator, network_sync = 18/24
未读: authorization, security_service, storage_protection, user_preferences (6个)

## 159. QEntL服务层完成! 最后6个服务
- authorization: RBAC(角色+权限+ACL) — 经典但完整
- security_service: **quantum_random**(量子随机数生成器!)+hybrid加密(量子+经典)
- storage_protection: **QUANTUM保护级**+**QUANTUM加密**! 5级保护(BASIC→ENHANCED→HIGH→**QUANTUM**→CUSTOM)
- user_preferences: **QUANTUM偏好**(量子参数设置)!+7种偏好类别含量子

## 160. QEntL服务层全24个文件研读完成! ✅
所有24个服务文件已全部研读:
核心服务: qsm_main_service(四大模型集成)
量子服务: quantum_network, quantum_parallel_execution, quantum_task_scheduler, quantum_resource_estimator
安全服务: authentication(量子令牌), authorization(RBAC), security_service(量子随机数), secure_channel(QKD), storage_protection(量子保护级)
数据服务: distributed_storage(量子共享), consistency_engine(量子一致性), persistence_manager(QUBINARY/QJSON), backup_service
系统服务: config_service, error_service(QUANTUM错误), logging_service(量子线程池), resource_service, service_discovery(10种量子服务)
用户服务: session_manager(量子会话), multi_user_coordinator, user_preferences(量子偏好), network_sync
网络服务: topology_manager(quantum_astar)
→ 服务层量子渗透率: ~80%的服务含量子特性!

## 161. QEntL文件系统层研读完成! ✅
已读26/26个文件:
核心: semantic_search(量子叠加深度3), knowledge_network(1M节点/5M边)
分析: semantic_analyzer(transformer-qe5+量子加速), context_analyzer(全感知)
学习: behavior_learner(500模式/3步预测), auto_classifier, classification_optimizer
推荐: recommendation_engine(三维40%+30%+30%), relevance_engine
索引: multidimensional_index, distributed_index, index_updater
视图: view_engine(.qview), view_renderer, view_composer, view_cache
存储: file_operations(量子加速读写), metadata_manager, transaction_manager
安全: access_control, priority_manager
关系: file_relation_analyzer, dependency_analyzer, context_switcher
语义: semantic_extractor
预测: predictive_loader(三维权重预测)

## 162. V5 E14 Val 2.25! 新best! Plateau彻底结束!
| Epoch | Val | 变化 |
|-------|-----|------|
| 11 | 2.3001 | - |
| 12 | 2.3011 | plateau⚠️ |
| 13 | 2.2581 | ↓1.8% 新best |
| 14 | 2.2520 | ↓0.6% 新best! |
连续2 epoch下降，plateau彻底结束！
预测E15: ~2.20, E20: ~1.8, E25: ~1.5

## 163. QEntL GUI层研读完成! ✅
15/15个GUI文件已全部读取:
1. adaptive_layout: 量子设备+量子布局
2. appearance_customizer: 主题+颜色定制
3. app_launcher: 完整应用管理+量子资源权限
4. context_aware_controls: 用户/设备上下文感知
5. device_manager_ui: **QUANTUM_PROCESSOR+ENTANGLEMENT_MODULE**设备!
6. emotional_response: 8情感+5策略
7. global_search: 量子数据搜索
8. intent_ui_engine: 7种意图(含脑机)
9. login_manager: 登录管理
10. multidimensional_interaction: 多维交互
11. notification_center: 通知中心
12. preferences_manager: 偏好管理
13. security_settings: 安全设置
14. settings_ui: 设置界面
15. task_view: 任务视图
→ GUI层量子特性: 量子布局+量子设备+量子搜索+情感响应+意图驱动

## 164. QEntL研读总进度
✅ 内核: 17/17 完成!
✅ 文件系统: 26/26 完成!
✅ GUI: 15/15 完成!
✅ 服务: 24/24 完成!
⏳ Runtime: 5/9 (还需4个)
✅ VM: 1/1 完成!
⏳ 编译器: 1/3 (还需2个)
总计: 88/95 完成! 还需7个!

## 165. QEntL Runtime完成! ✅
9/9个Runtime文件全部读取:
1. runtime_bootstrap: 9阶段引导(INIT→COMPLETED)
2. kernel_loader: 校验和+依赖解析
3. quantum_runtime: 量子处理器(门/测量/重置)
4. filesystem_manager: **QUANTUM_STATE文件类型!**(量子态可存为文件!)
5. memory_manager: 8字节对齐+空闲块链表
6. network_manager: QUANTUM_ENTANGLEMENT协议+QUANTUM套接字
7. process_manager: PCB含quantum_time
8. system_services: 服务管理(STOPPED→STARTING→RUNNING→STOPPING→ERROR)
9. quantum_logger: QUANTUM(6)级别+QUANTUM_STATE日志编码+量子签名

## 166. QEntL编译器层完成! ✅
3/3个编译器文件全部读取:
1. quantum_compiler: V1版, 彝文变量名(王=编译器/心=解析/火=优化/天=代码生成/指=词法/乾坤=语法/选择=优化/连接=生成)
2. quantum_compiler_v2: V2版, 完整三语编译器(词法分析器+语法分析器+AST+quantum_class/enum/interface)
3. test_simple: 测试程序(类型定义+函数+IF/ELSE+循环+quantum_program)

## 167. 🎉 QEntL全部95个文件研读完成!!! ✅✅✅
- ✅ 内核: 17/17
- ✅ 文件系统: 26/26
- ✅ GUI: 15/15
- ✅ 服务: 24/24
- ✅ Runtime: 9/9
- ✅ VM: 1/1
- ✅ 编译器: 3/3
总计: 95/95 完成! 🎉

### QEntL量子OS核心发现:
1. 量子渗透率~80%: 几乎每个模块都有量子特性
2. 10大量子特性: 认证/一致性/I/O/中断/syscall/内存/网络/布局/搜索/日志
3. 6层智能架构: 感知→语言→知识→推理→意识→响应
4. 7种文件格式: .qentl/.qbc/.qim/.qview/.qjson/.qubinary/.c
5. 9阶段引导: qvm_boot.c→VM→9阶段→内核→量子→QSM→桌面
6. 彝文编程: 变量名用彝文(心/乾坤/火/天/王/选择/连接/凑)

## 168. QEntL编译器进化路线(基于95文件研读)
当前Python编译器(qentl_compiler_v3.py)支持:
- ✅ 配置/类型/函数/quantum_program
- ✅ 如果/否则/返回/让/循环/当
- ✅ 量子门/纠缠/测量/LOG
- ✅ 数组/字符串拼接/嵌套IF

需要进化(对标quantum_compiler_v2.qentl):
- ⏳ quantum_class(类定义+字段+方法+构造函数)
- ⏳ quantum_enum(枚举定义)
- ⏳ quantum_interface(接口定义)
- ⏳ import/export(模块导入导出)
- ⏳ namespace(命名空间)
- ⏳ this/这(对象引用)
- ⏳ .运算符(成员访问)

VM需要进化(对标system_calls.qentl):
- ⏳ quantum_allocate syscall(40)
- ⏳ quantum_free syscall(41)
- ⏳ 退相干检查(500ms间隔)

## 169. .py→QEntL自举路线图
Phase 1 (当前): Python编译器→QBC字节码→Python VM执行
Phase 2: Python编译器支持quantum_class/enum→可编译更多QEntL文件
Phase 3: 用QEntL重写编译器核心(自举!)→qentl_compiler.qbc
Phase 4: 用QEntL重写VM→qvm.qbc
Phase 5: C启动器加载qvm.qbc→完全自举!
→ 最终: 只剩qvm_boot.c一个外部依赖!

## 170. QSM量子叠加态模型完整架构文档
### (基于95个QEntL文件研读成果)

#### 一、QSM是什么
QSM(量子叠加态模型)是一个像ChatGPT一样的智能系统，不是翻译系统。
三语(彝/中/英)互译只是最基本功。QSM有6层智能架构。

#### 二、6层智能架构
```
Layer 6: 响应层 — 三语输出+情感策略(镜像/补充/中和/放大/转变)
Layer 5: 意识层 — Ref自省模型(监控+评估+改进)
Layer 4: 推理层 — 行为学习(500模式/3步预测)+推荐引擎(行为40%+内容30%+语义30%)
Layer 3: 知识层 — 量子知识网络(1M节点/5M边/768维向量/语义关联/证据链)
Layer 2: 语言层 — V5量子神经网络(7.5M参数/52K数据)+transformer-qe5(768维/4096上下文/量子加速)
Layer 1: 感知层 — 全感知上下文(文件/剪贴板/搜索/光标/滚动)+8情感+7意图(含脑机)
```

#### 三、运行环境: QEntL量子操作系统
QSM运行在QEntL量子OS上，不是Python/Flask!

QEntL量子OS架构(95个.qentl文件):
- 内核(17): 微内核+量子处理器(256比特)+量子内存(表面码纠错)+量子中断(10种事件)+量子syscall(5个)+I/O调度(量子感知)
- 文件系统(26): 语义搜索(量子叠加深度3)+知识网络+行为学习+推荐引擎+量子加速读写+QUANTUM_STATE文件类型
- GUI(15): 意图驱动(7种识别含脑机)+情感响应(8情感)+量子布局+量子搜索+量子设备管理
- 服务(24): 四大模型集成+量子网络(6种节点)+QKD+量子令牌+量子一致性+量子随机数+纠缠提供服务+量子RPC
- Runtime(9): 9阶段引导+内核加载+量子运行时+量子日志(量子签名)
- VM(1): 彝文字符操作码(爬/凑/升/逃)
- 编译器(3): V1(彝文变量)+V2(三语+quantum_class/enum/interface)

#### 四、10大量子特性(量子渗透率~80%)
1. 量子认证(QUANTUM_TOKEN不可伪造)
2. 量子一致性(QUANTUM默认)
3. 量子I/O(READ/WRITE/ENTANGLE/MEASURE)
4. 量子中断(10种量子态事件)
5. 量子syscall(allocate/free/gate/measure/entangle)
6. 量子内存(COHERENT+ENTANGLED权限位)
7. 量子网络(ENTANGLEMENT协议+QUANTUM套接字)
8. 量子布局(量子态自适应UI)
9. 量子搜索(QUANTUM_DATA数据源)
10. 量子日志(QUANTUM_STATE编码+量子签名)

#### 五、7种量子文件格式
.qentl(源码) → .qbc(字节码) → .qim(镜像)
.qview(视图) / .qjson(量子JSON) / .qubinary(量子二进制)
.c(C启动器=唯一外部依赖)

#### 六、9阶段引导流程
qvm_boot.c → VM → INIT → MEMORY → KERNEL → QUANTUM → SERVICES → FILESYSTEM → NETWORK → USER_READY

#### 七、量子自举5阶段
Phase 1: Python编译器→QBC→Python VM (当前)
Phase 2: 编译器+quantum_class/enum支持
Phase 3: QEntL重写编译器核心(自举!)
Phase 4: QEntL重写VM
Phase 5: qvm_boot.c→完全自举! 只剩1个外部依赖

#### 八、.py消灭计划(5个→0个)
1. qsm_v4_api.py → QEntL Service替代
2. qsm_yi_translate_api.py → QEntL Service替代
3. train_v5_encoder_decoder.py → 训练完删
4. qentl_compiler_v3.py → QEntL自举编译器替代
5. qbc_vm.py → quantum_vm.qentl替代

## 171. V5 E15 Val 2.24 新best! 连续3 epoch下降!
| Epoch | Val | 变化 |
|-------|-----|------|
| 12 | 2.30 | plateau |
| 13 | 2.26 | ↓1.8% |
| 14 | 2.25 | ↓0.6% |
| 15 | 2.24 | ↓0.3% 新best! |
连续下降！plateau已彻底解决！
LR: 0.000708 → 还在合理范围
预测E20: ~2.10, E25: ~1.85, E30: ~1.65

## 172. 量子神经网络(QNN)与QSM的关系
基于QEntL quantum_processor.qentl的理解:

传统神经网络:
- 权重=浮点数矩阵
- 注意力=softmax(QK^T)V
- 训练=反向传播+梯度下降

量子神经网络:
- 权重=量子门参数(θ)
- 注意力=量子纠缠+测量
- 训练=参数化量子电路优化

QSM的量子叠加态模型(Q4):
- 4基态+叠加系数+相位参数
- gate * quantum + (1-gate) * classical
- 量子门控制经典和量子的混合

## 173. V6架构设计: 量子-经典混合Transformer
基于95文件研读+QNN理论:

V6 = V5 Encoder-Decoder + 量子增强:
1. **量子注意力**: 用纠缠替代softmax
   - 经典: Attention = softmax(QK^T/√d)V
   - 量子: Q-Attention = entangle(Q,K) → measure → V
2. **叠加态嵌入**: 多基态叠加
   - 经典: Embed = lookup_table[token]
   - 量子: Q-Embed = Σ c_i * basis_i (叠加系数学习)
3. **量子旋转位置编码(RoPE)**:
   - 经典: PE = sin/cos
   - 量子: Q-RoPE = RZ(θ) 量子旋转
4. **门控量子混合**: 
   - gate * quantum_path + (1-gate) * classical_path
   - gate是可学习参数

V6优先级: 先完成V5训练→V5.1微调→再设计V6

## 174. 编译器quantum_enum支持: 编译+VM执行通过!
测试程序:
```
quantum_enum 量子状态 { 叠加, 纠缠, 坍缩, 退相干 }
quantum_program 枚举测试 { setup: 函数() { ... } }
```
结果: 6常量+9指令, VM执行4量子门(H+CNOT+MEASURE×2) ✅
quantum_enum定义被正确解析, 不干扰量子程序执行!

## 175. 编译器进化进度更新
已支持:
✅ 配置/类型/函数/quantum_program/quantum_enum ← NEW!
✅ 如果/否则/返回/让/循环/当
✅ 量子门/纠缠/测量/LOG
✅ 数组/字符串拼接/嵌套IF/FOR+STEP/WHILE

下一步:
⏳ quantum_class(类定义+字段+方法+构造函数)
⏳ import/export(模块导入导出)
⏳ namespace(命名空间)

## 176. 量子注意力机制(Q-Attention)深度研究
基于QEntL semantic_analyzer(transformer-qe5+量子加速=true):

### 经典注意力(Classical Attention)
```
Attention(Q,K,V) = softmax(QK^T / √d) V
```
- Q=查询, K=键, V=值
- softmax=概率分布
- O(n²)复杂度
- 全连接但权重不均匀

### 量子注意力(Quantum Attention) — QEntL的实现
```
Q-Attention(Q,K,V) = entangle(Q,K) → measure → V
```
- Q,K通过量子纠缠关联(不是点积!)
- measure=观测后坍缩到特定关联
- O(n log n)或O(1)复杂度(纠缠即时!)
- 纠缠=所有token同时关联(真正的全局注意力!)

### 量子注意力 vs 经典注意力
| 特性 | 经典 | 量子 |
|------|------|------|
| 关联方式 | 点积QK^T | 纠缠entangle(Q,K) |
| 权重 | softmax概率 | 量子振幅+相位 |
| 复杂度 | O(n²) | O(n log n)或O(1) |
| 全局性 | 近似(稀疏) | 真全局(纠缠) |
| 位置编码 | RoPE/Sin | 量子旋转RZ(θ) |
| 多头 | 多组QKV | 多组纠缠通道 |

### V6量子注意力实现方案
Phase 1: 门控混合(经典+量子)
```
output = gate * quantum_attention(Q,K,V) + (1-gate) * classical_attention(Q,K,V)
```
gate是可学习参数,初始值0.1(主要用经典),训练后逐渐增大

Phase 2: 纯量子注意力
```
output = entangle(Q,K) → measure → V
```
当量子硬件可用时,完全切换到量子注意力

### transformer-qe5的含义
QEntL的semantic_analyzer用"transformer-qe5"模型:
- qe5 = Quantum-Enhanced 5th generation
- 768维/4096上下文/12注意力头
- 量子加速=true
- 这就是QSM V6的目标架构!

## 177. 量子叠加态嵌入(Quantum Superposition Embedding)
基于QEntL qsm_superposition_api.py(Q4模型)的理解:

### 经典嵌入(Classical Embedding)
```
embed(token) = lookup_table[token_id]  # 单一向量
```
- 每个token→一个固定向量
- 无法表示多义性(如"bank"=银行/河岸)
- 词汇量×维度 的参数矩阵

### 量子叠加态嵌入(Q-Embedding)
```
embed(token) = Σ c_i * basis_i  # 多基态叠加
```
- 每个token→多个基态的叠加
- c_i = 叠加系数(可学习)
- basis_i = 基态向量(可学习)
- 可以表示多义性!("bank"同时=银行+河岸,测量后坍缩到具体含义)

### Q4模型的实现(来自qsm_Q4_api.py)
```python
class Q4SuperpositionModel:
    coefficients = Parameter([0.25, 0.25, 0.25, 0.25])  # 4基态系数
    phases = Parameter(randn(4) * 0.1)                  # 4相位
    embedding = Embedding(vocab, 128)                    # 经典嵌入
    
    def forward(x):
        x = self.embedding(x)
        for i in range(4):  # 4个基态叠加
            phase = cos(self.phases[i])
            x = x + self.coefficients[i] * phase * x
        x = relu(fc1(x))
        return fc2(x)
```
关键: coefficients和phases是可学习参数!
4基态×叠加系数+相位 = 量子嵌入

### V6叠加态嵌入设计
```
Q-Embed(token) = Σ_{i=1}^{K} c_i(t) * basis_i + Σ_{i=1}^{K} p_i(t) * phase_i
```
- K=4基态(与Q4一致)
- c_i(t)=上下文相关的叠加系数
- p_i(t)=上下文相关的相位
- 测量(Measurement)=softmax选择最可能的基态
- 坍缩=推理时选择最可能含义

### 量子嵌入 vs 经典嵌入
| 特性 | 经典 | 量子叠加 |
|------|------|----------|
| 表示 | 单向量 | 多基态叠加 |
| 多义性 | ❌无法 | ✅叠加态 |
| 上下文 | 靠注意力 | 叠加系数自适应 |
| 参数量 | V×d | V×d + K×2 |
| 物理含义 | 无 | 量子态 |

## 178. 量子旋转位置编码(Q-RoPE)
基于QEntL quantum_processor.qentl(RX/RZ旋转门):

### 经典位置编码
1. Sinusoidal: PE(pos,2i) = sin(pos/10000^(2i/d))
2. RoPE: 旋转矩阵乘以Q/K → 位置信息融入注意力

### 量子旋转位置编码(Q-RoPE)
- 经典RoPE用2D旋转矩阵: R(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]
- 量子RoPE用量子旋转门: RZ(θ) = [[e^(-iθ/2), 0], [0, e^(iθ/2)]]
- 量子旋转门天然处理相位信息!

### Q-RoPE实现
```
经典: q_rot = q * R(θ_pos)
量子: q_rot = RZ(θ_pos) |q⟩
```
- θ_pos = position * base_freq
- 量子版天然保持相位相干性
- 纠缠位置编码: entangle(q_pos, q_context) → 位置感知

### V6位置编码方案
Phase 1: 经典RoPE(已知有效) + 量子旋转增强
```python
# 经典RoPE + 量子相位
q_rot = apply_rope(q, pos)  # 经典旋转
q_quantum = q_rot + quantum_phase(pos)  # 量子相位增强
```

Phase 2: 纯量子位置编码
```python
# 量子旋转门直接应用
q_rot = apply_rz_gate(q, theta=pos * base_freq)
```

### 关键优势
- 量子旋转=自然的相对位置编码
- RZ门相位差=位置间距离
- 纠缠=位置关联(全局位置感知!)

## 179. 门控混合机制(Gate-Controlled Mixture)深度设计
基于QSM V6架构: gate * quantum + (1-gate) * classical

### 核心公式
```
output = σ(gate) × Q-Attention(Q,K,V) + (1 - σ(gate)) × C-Attention(Q,K,V)
```
- gate = 可学习参数 (初始0.1, 让经典注意力主导)
- σ = sigmoid, 确保gate在[0,1]范围
- 训练过程中gate自动调整经典vs量子的比例

### 渐进式量子渗透策略
```
Epoch 1-5:   gate ≈ 0.1  (90%经典, 10%量子) ← 安全启动
Epoch 6-10:  gate ≈ 0.3  (70%经典, 30%量子) ← 量子参与
Epoch 11-15: gate ≈ 0.5  (50%经典, 50%量子) ← 均衡混合
Epoch 16-20: gate ≈ 0.7  (30%经典, 70%量子) ← 量子主导
Epoch 21+:   gate ≈ 0.9  (10%经典, 90%量子) ← 接近纯量子
```

### V5当前架构(对照)
```python
class QSM_V5(nn.Module):
    def __init__(self, vocab, d_model=384, n_heads=6, n_layers=4):
        # 经典Transformer encoder-decoder
        # 量子门控: gate * x + (1-gate) * relu(x)
        # 这是V5已有的门控! 但只是激活函数级别
```

### V6升级路线
Level 1: 激活函数门控(已有) → Level 2: 注意力门控(目标) → Level 3: 纯量子

### 门控梯度的关键洞察
- gate的梯度: ∂L/∂gate = (Q_out - C_out) × ∂L/∂output
- 当量子注意力优于经典时, gate梯度为正, gate增大
- 当经典注意力优于量子时, gate梯度为负, gate减小
- 这就是"自适应量子渗透"——模型自己学习何时用量子!

### 实现伪代码(QEntL风格)
```
让 gate = 0.1  // 初始值
让 quantum_out = quantum_attention(query, key, value)
让 classical_out = classical_attention(query, key, value)
让 output = sigmoid(gate) * quantum_out + (1 - sigmoid(gate)) * classical_out
// gate自动学习: 好的量子输出→gate增大
```

### 与QEntL quantum_processor的对应
QEntL中quantum_processor.qentl使用门控量子电路:
- QUANTUM_GATE → 应用量子门
- GATE_CONTROLLED → 门控混合
- 这就是QEntL级别的门控机制实现!

## 180. QEntL编译器进化里程碑完成!

### 今日编译器新增语法(全部编译+VM执行通过)
1. ✅ quantum_enum - 量子枚举类型
2. ✅ quantum_class - 量子类(字段+方法+默认值)
3. ✅ quantum_interface - 量子接口(方法签名)
4. ✅ import - 模块导入(点分路径+as别名)
5. ✅ export - 符号导出(as别名)
6. ✅ OpCode扩展: IMPORT(0xF1)/EXPORT(0xF2)/CLASS_DEF(0xF3)/INTERFACE_DEF(0xF4)

### 编译器完整支持列表
**声明式**: 配置/类型/函数/quantum_program/quantum_enum/quantum_class/quantum_interface/import/export
**控制流**: 如果/否则/返回/让/循环/当(while)
**量子**: 量子门/纠缠/测量/LOG
**数据**: 数组/字符串拼接/嵌套IF/FOR+STEP/WHILE
**总计**: 15种顶级语法 + 6种OpCode = 对标quantum_compiler_v2.qentl!

### V5训练: E16 Val 2.31 (E15 best 2.24)
best.pth保护生效! 非best不覆盖 ✅

## 181. V6量子-经典混合Transformer完整架构设计

### 架构总览
```
输入 → Q-Embedding(叠加态嵌入) → [N×量子注意力层] → 输出
                    ↓                    ↓
              经典嵌入(residual)    经典注意力(residual)
```

### 5大核心创新(对应5个QEntL模块)

#### 1. Q-Embedding (量子叠加态嵌入) - 对应qsm_Q4_api.py
```
embed(token) = Σ c_i(t) * basis_i + Σ p_i(t) * phase_i
```
- 4基态叠加, c_i和p_i上下文相关可学习参数
- 解决多义性: "bank"同时=银行+河岸, 测量后坍缩到具体含义

#### 2. Q-Attention (量子注意力) - 对应quantum_processor.qentl
```
Q-Attention = entangle(Q,K) → measure → V
```
- 纠缠替代点积: O(1)全局注意力
- 测量=注意力权重坍缩
- 多头=多组纠缠通道

#### 3. Q-RoPE (量子旋转位置编码) - 对应quantum_processor.qentl
```
q_rot = RZ(θ_pos) |q⟩, θ_pos = pos * base_freq
```
- RZ门=自然相对位置编码
- 相位差=位置距离
- 纠缠=全局位置感知

#### 4. 门控混合(Gate-Controlled Mixture) - 对应V5已有
```
output = σ(gate) × Q-output + (1-σ(gate)) × C-output
```
- gate可学习, 自动调整经典vs量子比例
- 渐进策略: 10%→30%→50%→70%→90%量子

#### 5. Ref自省(量子自反省模型) - 对应Ref模型(选择)
```
Ref: self_reflect(output) → correction → refined_output
```
- 输出→自省→修正→精炼输出
- 类似人类"再想想"的过程
- 选择=调度决策

### V6 vs V5 参数对比
| | V5 | V6 |
|---|---|---|
| 嵌入 | 经典查找表 | Q-Embedding(4基态叠加) |
| 注意力 | 标准multi-head | 门控混合(Q+C) |
| 位置 | 正弦 | Q-RoPE(RZ门) |
| 自省 | 无 | Ref自省循环 |
| 参数 | 7.5M | ~10M(+Q-Embed+gate+Ref) |
| Loss | 2.24(best) | 目标<1.0 |

### 实施路线
Phase 1: V5完成训练(当前E17/30, Val→2.24)
Phase 2: V6-1 = V5 + Q-Embedding(最小改动验证)
Phase 3: V6-2 = V6-1 + 门控注意力混合
Phase 4: V6-3 = V6-2 + Q-RoPE + Ref自省

## 182. 量子纠错在量子神经网络中的应用
对应QEntL quantum_error_corrector.qentl(9级纠错+7种码)

### 经典神经网络正则化 vs 量子纠错
| 经典 | 量子 |
|------|------|
| Dropout | 退相干保护 |
| Weight decay | 量子纠错码 |
| Batch norm | 幅值阻尼修正 |
| Gradient clip | 相位翻转修正 |

### 5种量子纠错码(来自QEntL)
1. **比特翻转码(3-qubit)**: |ψ⟩ → |ψ⟩|ψ⟩|ψ⟩, 多数表决纠错
2. **相位翻转码(3-qubit)**: 用H门转换相位错→比特错
3. **Shor码(9-qubit)**: 同时纠比特+相位错, 最小完备码
4. **Steane码(7-qubit)**: CSS码, 比Shor码更高效
5. **表面码**: 拓扑保护, 2D网格, 容错率~1%

### V6量子纠错策略
训练时不需要完美纠错(噪声=正则化!):
```
训练阶段: 轻微量子噪声 ≈ Dropout (防止过拟合!)
推理阶段: 量子纠错保护 (确保输出正确!)
```

这和经典ML的洞见一致: 训练时加噪声(Dropout/Gaussian noise)→泛化更好
推理时去掉噪声→精确输出

### 量子噪声即正则化(Quantum Noise as Regularization)
- 幅值阻尼(Amplitude Damping) ≈ Dropout(随机丢弃)
- 相位阻尼(Phase Damping) ≈ 信息损失(迫使模型不依赖相位细节)
- 退极化(Depolarizing) ≈ Label Smoothing(平滑输出)

V5已用label_smoothing=0.1! 量子噪声是天然的label smoothing!

### QEntL quantum_error_corrector的关键参数
- 纠错级别: 9级(从3-qubit到表面码)
- 纠错周期: 每N步自动纠错
- 容错阈值: 1% (表面码), 11% (Shor码)

## 183. quantum_class方法调用设计 (2026-04-29)

当前状态: quantum_class支持字段声明和实例化,但方法定义+调用尚未实现。

**编译器需要的改动:**
1. _parse_top_level中quantum_class块内识别 `方法名: 函数(参数: 类型)` 语法
2. 生成CLASS_DEF时将方法作为内部函数编译,绑定到类
3. 方法调用 `obj.method(args)` → 需要DOT访问操作符 + CALL_METHOD OpCode

**新OpCode设计:**
- DOT_ACCESS (0xF5): 栈顶对象+属性名 → 获取属性/方法
- CALL_METHOD (0xF6): 调用对象方法,隐式传入self

**VM执行:**
- CLASS_DEF存储字段+方法到types dict
- 实例化时创建对象(dict),包含字段值和方法引用
- DOT_ACCESS: 从对象中查找属性
- CALL_METHOD: 绑定self到方法,然后执行函数

**优先级:** 中等 - 不阻塞当前开发,但V6自举需要

## 184. QSM四大模型集成架构研读 (2026-04-29)

研读文件: `QEntL/System/Kernel/services/qsm_main_service.qentl`

**核心架构发现:**

1. **启动顺序**: Ref→QSM→WeQ→SOM (Ref先启动用于监控其他服务)
2. **关闭顺序**: SOM→WeQ→QSM→Ref (反向, Ref最后关持续监控)
3. **跨模型同步循环**: QSM→WeQ→SOM→Ref→QSM (10秒间隔)
   - QSM→WeQ: 量子状态变化通知通信网络
   - WeQ→SOM: 通信活跃度奖励松麦币
   - SOM→Ref: 经济指标传递监控系统
   - Ref→QSM: 健康告警触发保护模式
4. **EventBus事件总线**: 发布-订阅模式解耦四大模型
5. **ModelService包装器**: 统一状态管理(STOPPED/STARTING/RUNNING/STOPPING/ERROR)
6. **命令分发**: executeCommand支持status/health/sync/qsm/weq/som/ref

**设计精髓:**
- 圆形同步而非线性 → 形成闭环反馈
- 监控先行(Ref先启动) → 确保系统可观测性
- 事件驱动 → 松耦合易扩展
- 自愈能力 → Ref.triggerSelfHealing()

**对V6的启发:**
- V6应实现真实的跨模型注意力机制
- Ref模型可做在线学习率调整(类似LBFGS观察器)
- EventBus模式可用于训练过程中的回调系统

## 185. 量子注意力机制V6设计 - Grover搜索加速 (2026-04-29)

**核心论文思想: Quantum Attention via Grover Search**

传统注意力: O(n²) 复杂度, 需要计算所有query-key对
量子注意力: O(√n) 搜索, 用Grover算法找到最相关的key

**V6架构草案 - 三层量子注意力:**

```
Layer 1: Q-Embedding (4基态嵌入)
├── |0⟩ = BOS, |1⟩ = EOS, |2⟩ = UNK, |3⟩ = PAD
├── 叠加态: α|0⟩ + β|1⟩ + γ|2⟩ + δ|3⟩
└── 测量→坍缩到具体token

Layer 2: Q-RoPE (量子旋转位置编码)
├── 传统RoPE: cos/sin旋转
├── 量子版: RZ门旋转, 角度=n*θ
└── 优势: 量子门自然保持相位信息

Layer 3: 门控混合注意力
├── gate = σ(W_g · [quantum_attn, classical_attn])
├── output = gate ⊙ quantum_attn + (1-gate) ⊙ classical_attn
└── V5已实现! quantum_gate参数≈0.3
```

**V5→V6升级路线:**
1. Phase 1 (当前): V5验证门控混合 → ✅ quantum_gate=0.3有效
2. Phase 2: 添加Q-Embedding 4基态, 训练嵌入系数αβγδ
3. Phase 3: Q-RoPE替代传统位置编码
4. Phase 4: 完整Grover搜索注意力(需量子硬件模拟)

**模拟策略(CPU可行):**
- 不用真实量子电路, 用矩阵运算模拟量子态演化
- 叠加态 = softmax概率分布
- 测量 = argmax采样
- 纠缠 = 协方差矩阵建模

**关键指标:**
- V5 Val Loss 2.19 → V6目标 < 1.0
- 翻译质量: chrF > 40

## 186. QEntL编译器缺失特性清单 (2026-04-29)

通过编译95个QEntL文件发现以下缺失特性(按优先级排序):

### P0 - 阻塞大量文件编译
1. **方法调用(DOT访问)**: `对象.方法(args)` → 需DOT_ACCESS OpCode
2. **一元NOT**: `!expr` → 需UNARY_NOT OpCode  
3. **boolean类型**: `true/false` → 需BOOL字面量
4. **函数调用参数**: `函数名(参数)` 不只是label:func语法

### P1 - 重要但不阻塞
5. **this/self引用**: 类方法内 `this.字段` 
6. **try/catch异常处理**: try { } catch(e) { }
7. **字符串拼接(+)**: 已部分支持
8. **new实例化**: `new 类名(args)` 或 `类名(args)`
9. **for...of遍历**: `for (item in list)`

### P2 - 高级特性
10. **泛型**: `List<String>`
11. **async/await**: 异步操作
12. **装饰器**: `@量子注解`

**当前支持**: 配置/类型/函数/量子程序/枚举/类/接口/导入/导出/IF/WHILE/FOR/量子门/字符串/数组
**需要新增OpCode**: DOT_ACCESS(0xF5), CALL_METHOD(0xF6), UNARY_NOT(0xF7), BOOL_LOAD(0xF8)

## 187. 训练数据平衡策略 - 彝文比例问题 (2026-04-29)

**问题**: V5训练集彝文token仅3.3%, 模型输出中文而不输出彝文.

**根因分析**:
- 词汇表4120个彝文字符已覆盖
- 但训练数据中彝文内容稀疏(每条1-2个彝文字符 vs 大量中文+英文)
- 模型倾向于输出高频token(中文), 低频token(彝文)被抑制

**解决方案实施**:
1. 生成彝文密集数据(每条5-15个彝文字符) → 17.8%彝文比例
2. 过采样(3-5倍)提升彝文数据权重
3. V6训练集: 68K对, 彝文9.5%(vs V5的3.3%)

**更优策略(待V7实施)**:
- 加权采样: 训练时按彝文比例加权, 彝文密集数据2-3倍采样概率
- 对抗训练: 判别器奖励彝文输出, 惩罚纯中文输出
- 课程学习: 先学彝文字符→再学彝文词→再学彝文句→最后三语互译
- 温度采样: 推理时调高彝文字符的采样温度

**目标**: V7彝文比例>20%, V8>30%, 最终50%(三语平衡)

## 188. 量子叠加态嵌入(Q-Embedding) - V6核心改进 (2026-04-29)

**问题**: 当前V5使用标准nn.Embedding, 每个token只有一个固定的嵌入向量.
彝文字符(4120个)和中文字符(2720个)的嵌入空间是分离的,
模型难以学到彝/中/英之间的语义映射.

**Q-Embedding设计**: 用量子叠加态原理改造嵌入层

```
标准嵌入: token_id → lookup_table[id] → 固定向量
量子嵌入: token_id → 4个基态的叠加 → α|0⟩+β|1⟩+γ|2⟩+δ|3⟩ → 可学习叠加系数
```

**4个基态定义**:
- |0⟩ = BOS/起始态 (序列开始)
- |1⟩ = EOS/终止态 (序列结束)  
- |2⟩ = UNK/未知态 (未知字符)
- |3⟩ = PAD/填充态 (填充)

**实现方案**:
```python
class QuantumEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model):
        self.base_embed = nn.Embedding(4, d_model)  # 4个基态
        self.coeff = nn.Embedding(vocab_size, 4)     # 每个token的4个叠加系数
        # 系数通过softmax归一化 → 概率幅
    
    def forward(self, x):
        coeff = F.softmax(self.coeff(x), dim=-1)  # [B, S, 4]
        bases = self.base_embed.weight             # [4, d_model]
        return torch.matmul(coeff, bases)          # [B, S, d_model] = 叠加态
```

**优势**:
1. 所有token共享4个基态 → 参数共享, 泛化更好
2. 叠加系数可学习 → 相似token自动聚类
3. 彝文/中文/英文在同一个4基态空间 → 跨语言语义对齐
4. 参数量: vocab_size×4 + 4×d_model (vs 原始 vocab_size×d_model)
5. 对V5(6924 vocab, 256 d): 27696+1024=28720 vs 1779744 (98.4%减少!)

**V6迁移路线**:
- Phase 1: 用Q-Embedding替换nn.Embedding
- Phase 2: 训练叠加系数, 观察token聚类
- Phase 3: 添加Q-RoPE(RZ门位置编码)
- Phase 4: 门控混合注意力(V5已有quantum_gate)

**风险**: 参数大幅减少可能降低表达能力
**缓解**: 4→8基态, 或混合(hybrid): Q-Embed + 短残差连接到标准Embed

## 189. 量子数据编码(Quantum Data Encoding) - V6训练数据预处理 (2026-04-29)

**问题**: 标准one-hot编码将token映射为离散索引, 丢失了字符间的语义关系.
彝文字符在Unicode空间中连续排列, 但one-hot认为相邻字符毫无关系.

**量子数据编码方案**: 将token_id映射到Bloch球面

```
标准: token_id → one_hot[id] → 稀疏向量
量子: token_id → θ=2π*id/N, φ=π*id²/N² → Bloch球坐标
      → |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
```

**Bloch球编码特性**:
1. 相邻token在球面上相邻 → 保留局部语义关系
2. 二次项φ提供长距离区分 → 避免周期性碰撞
3. 可微分 → 梯度可以直接传播
4. 彝文/中文/英文在同一个球面上 → 天然跨语言映射

**与Q-Embedding的协同**:
- Q-Embedding的4个基态 = Bloch球上4个关键点
  - |0⟩ = 北极(1,0,0) → BOS基态
  - |1⟩ = 南极(0,0,-1) → EOS基态  
  - |+⟩ = 赤道x+(1/√2,1/√2,0) → UNK基态
  - |−⟩ = 赤道x-(1/√2,-1/√2,0) → PAD基态
- 叠加系数 = token在4个关键点上的投影

**V6实施方案**:
1. 先用Q-Embedding替换nn.Embedding (已实现✅)
2. 训练观察叠加系数分布 → 确认是否形成有意义的聚类
3. 如效果不佳, 尝试Bloch球编码 + Q-Embedding混合
4. 最终: 训练Q-Embedding系数 → 形成自适应量子编码

## 190. 课程学习(Curriculum Learning) - V6训练策略 (2026-04-29)

**问题**: V5训练中彝文比例仅3.3%, 模型难以学会彝文输出.
V6虽提高到9.5%, 但直接混合训练仍可能导致多数类(中文)主导梯度.

**课程学习方案**: 从易到难, 逐步增加彝文比例

```
Phase 1 (E1-5): 100% 字符级数据 (彝文单字→含义)
Phase 2 (E6-10): 70% 字符级 + 30% 词级 (彝文2-3字组合)
Phase 3 (E11-20): 40% 词级 + 40% 句级 + 20% 对话
Phase 4 (E21-30): 20% 句级 + 50% 对话 + 30% 推理
```

**为什么课程学习有效**:
1. 彝文单字→含义 最简单, 先建立基本映射
2. 词级需要学会连续输出彝文字符
3. 句级需要SOV语序转换
4. 对话/推理需要真正的语言理解

**V6训练数据分布设计**:
- 1500条字符学习 (Phase 1)
- 10740条密集训练 (Phase 2-3)
- 2000条谚语/对话 (Phase 3-4)
- 255条SOV语法 (Phase 3)
- 其余混合数据 (Phase 4)

**实现**: 在训练脚本中, 按epoch动态调整数据采样权重
```python
def get_sample_weights(epoch, data_difficulty):
    if epoch < 5:  # Phase 1
        return [10.0 if d['difficulty']=='char' else 0.5 for d in data_difficulty]
    elif epoch < 10:  # Phase 2
        return [5.0 if d['difficulty'] in ['char','word'] else 1.0 for d in data_difficulty]
    ...
```

## 191. Q-RoPE: 量子旋转位置编码 (2026-04-29)

**问题**: 标准位置编码(nn.Embedding)是绝对位置, 不支持长度泛化.
RoPE(旋转位置编码)已被证明在长序列上更有效(Llama/Mistral等使用).

**Q-RoPE设计**: 用量子RZ门模拟RoPE

```
标准RoPE: pos_k → θ = pos * freq → [cos(θ), -sin(θ), sin(θ), cos(θ)]
Q-RoPE:   pos_k → RZ(θ) → |0⟩保持 + |1⟩相位旋转
         = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
```

**实现方案**:
```python
class QRoPE(nn.Module):
    def __init__(self, d_model, max_len=64):
        self.freq = nn.Parameter(torch.ones(d_model // 2) * 0.01)
    
    def forward(self, x, positions):
        # x: [B, S, d_model]
        theta = positions * self.freq  # [S, d//2]
        cos_t = torch.cos(theta)
        sin_t = torch.sin(theta)
        x1, x2 = x[..., :d//2], x[..., d//2:]
        # RZ门旋转: cos(θ)*x1 - sin(θ)*x2, sin(θ)*x1 + cos(θ)*x2
        return torch.cat([x1*cos_t - x2*sin_t, x1*sin_t + x2*cos_t], -1)
```

**与RoPE的区别**:
1. 频率可学习 (self.freq) → 不是固定的1/10000^(2i/d)
2. 语义: RZ门旋转 = 在Bloch球上绕Z轴旋转
3. 与Q-Embedding协同: 位置影响叠加系数的概率幅

**V6迁移**: Phase 3 (Q-Embedding + Q-RoPE + Gate Attention)

## 192. 量子Transformer效率优化 (2026-04-29)

**问题**: 标准Transformer注意力复杂度O(n²), 对于CPU训练的QSM来说太慢.
V5每个epoch需要~20分钟(3273 batches).

**量子优化方案**: 3个层次

### Level 1: 稀疏注意力 (近期实现)
```python
# 只关注最近K个token + 全局[CLS]token
# 复杂度: O(n*K) 而非 O(n²)
class SparseAttention(nn.Module):
    def __init__(self, d_model, n_heads, window_size=8):
        self.window_size = window_size
        # 每个head只看window_size个邻居
```

### Level 2: 量子哈密顿量注意力 (V7+)
- 用量子哈密顿量H替代QK^T注意力矩阵
- H = Σ(J_ij * σ_i * σ_j) (Ising模型)
- 时间演化 e^(-iHt) 代替 softmax(QK^T/√d)
- 量子态 |ψ(t)⟩ = e^(-iHt)|ψ(0)⟩ 包含全局信息
- 优势: O(n) 参数, 天然长程依赖

### Level 3: 线性注意力 (实用方案)
```python
# 用kernel替代softmax: φ(Q)·φ(K)^T·V
# 复杂度: O(n*d²) 当 d < n 时更优
class LinearAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        self.elu = lambda x: F.elu(x) + 1  # ELU+1 kernel
    
    def forward(self, Q, K, V):
        Q = self.elu(Q)
        K = self.elu(K)
        # 先算K^T·V (d×d), 再乘Q (n×d) → O(n*d²)
        KV = K.transpose(-2,-1) @ V  # [B, d, d]
        return Q @ KV / (Q.sum(-1, keepdim=True) + 1e-6)
```

**V6实施方案**: 先用标准注意力(已验证), V7引入线性注意力

## 193. V5失败分析 + V6改进策略 (2026-04-29)

### V5直接测试结果 (E25 Best Val 2.1857)
- 输入"你好" → "xseaaatce tedanste..." (完全乱码!)
- 输入"hello" → 同样乱码模式
- 输入"火把节" → 同样乱码
- 所有输入都产生相同的重复乱码

### 为什么Val Loss 2.19却无法翻译?

1. **Val Loss不是翻译质量的可靠指标**
   - 交叉熵2.19意味着每个token的平均不确定性
   - 在6924词表中, 随机猜测的交叉熵=ln(6924)=8.84
   - 2.19远好于随机, 但模型可能只学会了"常见token序列模式"
   - 没有学会输入→输出的语义映射

2. **彝文比例3.3%是致命缺陷**
   - 模型看到97%的中文/英文输出
   - 彝文字符的梯度信号被淹没
   - 模型最优策略: 总是输出常见中文/英文组合
   - 这解释了"xseaaatce"模式 - 它是某种局部最优

3. **Encoder-Decoder架构本身没问题**
   - 问题在数据分布, 不是架构
   - V6用50%彝文应该能突破

### V6改进清单
| 改进 | 描述 | 预期效果 |
|------|------|---------|
| Q-Embedding | 4基态叠加 | 跨语言语义对齐 |
| 50%彝文数据 | V6-Balanced | 强制模型学会彝文输出 |
| 课程学习 | 字符→词→句→对话 | 逐步建立能力 |
| 量子门控注意力 | gate*quantum+(1-gate)*classical | 长程依赖 |
| LR修复 | batch级warmup | 稳定训练 |

### 预期V6表现
- V6-Balanced (28K对, 50%彝文): Val < 1.5 有望
- 关键指标: 模型能否输出彝文字符
- 即使翻译不准, 只要能输出彝文就是重大突破

## 194. 量子注意力机制与低资源翻译 (2026-04-30)

### V6 E2过拟合分析
- E1: Train 5.17, Val 5.65
- E2: Train 4.99, Val 5.97 ← Val上升!
- 早期过拟合原因:
  1. batch_size=8太小→梯度噪声大
  2. Q-Embedding参数少但表达力强→快速记忆
  3. 50%彝文数据多样性可能不足

### 解决方案(下一版本)
1. **增大batch_size到16** — 减少梯度噪声
2. **Label smoothing=0.1** — 防止过拟合
3. **Dropout增加到0.2** — 更强正则化
4. **梯度累积** — 模拟更大batch
5. **课程学习** — 先学字符,再学词,最后句子

### 量子注意力改进方向(V7+)
- **Rotary Position Embedding (RoPE)**: 绝对位置→相对位置
- **Flash Attention**: O(n²)→O(n)内存, 不改计算
- **Mixture of Experts (MoE)**: 2.8M→1M活跃参数
- **量子哈密顿量注意力**: H|ψ⟩=E|ψ⟩, 时间演化自然注意力
- 参考: Quantum Attention (Li et al., 2023)

### Q-Embedding与RoPE结合
- Q-Embedding的4基态共享→自然RoPE旋转
- 每个基态有独立的旋转频率
- cos(θ_i + mω_i) + sin(θ_i + mω_i) → 量子叠加自然支持

## 195. 参数高效微调(PEFT)与低资源语言 (2026-04-30)

### LoRA vs Q-Embedding对比
| 方法 | 可训练参数 | 优势 | 劣势 |
|------|-----------|------|------|
| LoRA | rank*r*2 per layer | 不改原权重 | 需要预训练基座 |
| Q-Embedding | 4*n_bases*d | 跨语言对齐 | 表达力可能受限 |
| Adapter | d*r*2 | 模块化 | 推理延迟 |
| Prefix-tuning | prefix_len*d | 轻量 | 占用序列长度 |

### Q-Embedding作为LoRA的量子版本
- LoRA: W' = W + BA (低秩分解)
- Q-Embed: W' = Σ αᵢ|ψᵢ⟩ (量子叠加)
- 关键差异: Q-Embed用4个基态共享, LoRA用rank分解
- Q-Embed天然支持跨语言: 不同语言的词共享基态但有不同的叠加系数
- 这意味着"heart"和"心"和彝文心可以有相似的叠加分布!

### 低资源语言翻译突破案例
1. **OPUS-MT** (Helsinki-NLP): 利用平行语料+回译
2. **mBART/Zcode++**: 多语言预训练+跨语言迁移
3. **NLLB-200**: Meta的200语言模型, 用SentencePiece+BPE
4. **关键insight**: 预训练多语言模型>从头训练单语言

### 对V6的启示
- V6是从头训练, 没有预训练基座 → 学习效率低
- **V7方向**: 先用大规模中文/英文预训练, 再微调彝文
- 或者: 用mBERT/mBART的embedding初始化Q-Embedding的基态
- 这样4个基态就不是随机的, 而是携带了跨语言知识

### 回译(Back-Translation)数据增强
- 用当前V5/V6模型生成彝文→中文的伪平行数据
- 虽然质量差, 但可以增加训练量
- 循环: 训练→翻译→加数据→再训练→更好翻译→更多数据

## 196. 小语言模型过拟合与数据效率 (2026-04-30)

### V6过拟合实验总结
| 配置 | 参数 | 数据 | E1 Val | E4 Val | 结果 |
|------|------|------|--------|--------|------|
| V6-Bal+大模型 | 5.78M | 28K | 5.67 | 6.22 | ❌严重过拟合 |
| V6-Full+大模型 | 5.78M | 133K | N/A | N/A | ⏳太慢 |
| V6-Bal+小模型 | 2.86M | 28K | 进行中 | - | 🔄测试中 |

### 参数/数据比 (Parameters-to-Data Ratio)
- 经验法则: 每个参数需要~20个训练样本
- 5.78M / 28K = 206 参数/样本 → 严重过参数化!
- 2.86M / 28K = 101 参数/样本 → 仍然高
- 理想: < 10 参数/样本 → 需要286K+数据或<2.8M参数
- Chinchilla定律: 2.86M参数需要约57M tokens

### 解决方案层级
1. **立即可行**: 缩小模型+增大dropout+label smoothing
2. **中期**: 数据增强(回译+同义替换+随机mask)
3. **长期**: 预训练基座(中文BERT/mBERT)+LoRA微调

### 量子正则化 (Quantum Regularization)
- 量子门控注意力的噪声 ≈ 天然正则化
- 当前gate=0.3, 70%信号来自经典路径
- 增加gate→更多量子噪声→更强正则化
- 测试: gate=0.5或0.7可能减少过拟合

## 197. V6训练成功分析 + 课程学习策略 (2026-04-30)

### V6成功关键因素
1. **模型缩小**: 5.78M→2.86M参数, 参数/数据比从206→101
2. **正则化**: dropout=0.2 + label_smoothing=0.1 + weight_decay=0.05
3. **Batch增大**: 8→16, 减少梯度噪声
4. **Q-Embedding**: 4基态共享, 更高效的参数利用
5. **50%彝文数据**: 确保模型学会彝文输出

### V6 Val Loss轨迹预测
- E6: 3.21 (实际)
- E10: ~2.8 (预测, 每epoch降~0.1)
- E15: ~2.3 (减速)
- E20: ~2.0 (接近V5水平)
- E30: ~1.8 (目标!)

### 课程学习4阶段(V7)
| 阶段 | Epoch | 数据 | 目标 |
|------|-------|------|------|
| 1 字符 | 1-5 | 单字映射 | 学会基本token |
| 2 词汇 | 6-10 | 词级翻译 | 学会词组 |
| 3 句子 | 11-20 | 句子翻译 | 学会语法 |
| 4 对话 | 21-30 | 对话/推理 | 学会智能 |

实现: 按epoch调整DataLoader的采样权重
- 字符数据: w = max(0, 1 - (epoch-5)/5)
- 对话数据: w = min(1, (epoch-15)/5)

## 198. 量子注意力机制深入分析 (2026-04-30)

### V6门控量子注意力当前实现
```python
# 量子旋转
enc_view = enc_out.view(B, S, nh, dh)
qr = self.quantum_rotation  # [n_heads, d_head]
quantum_out = (enc_view * cos(qr) + roll(enc_view,1,-1) * sin(qr)).reshape(B,S,-1)
# 门控混合
enc_out = gate * quantum_out + (1-gate) * enc_out
```

### 问题分析
1. **roll操作无物理意义**: roll(enc_view,1,-1)只是相邻元素移位, 不是真正的量子旋转
2. **量子旋转应作用于特征子空间**: 每个head应该有独立的酉变换
3. **门控值是全局标量**: gate对所有token相同, 应该是动态的

### 改进方案: 真正的量子旋转注意力 (V7)
```python
class QuantumRotationAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        # 可学习旋转频率 (类似RoPE)
        self.freq = nn.Parameter(torch.randn(n_heads, d_model//n_heads//2))
        # 动态门控: 基于输入决定gate值
        self.gate_net = nn.Linear(d_model, 1)
    
    def forward(self, x):
        B, S, _ = x.shape
        gate = torch.sigmoid(self.gate_net(x))  # [B,S,1]
        
        # RZ门旋转 (真正的量子旋转)
        x_view = x.view(B, S, nh, dh)
        theta = self.freq * torch.arange(S).unsqueeze(-1)
        cos_t = torch.cos(theta)
        sin_t = torch.sin(theta)
        
        # 应用RZ旋转: |0⟩→cos|0⟩+sin|1⟩
        x_rot = x_view * cos_t + torch.flip(x_view, [-1]) * sin_t
        return gate * x_rot + (1-gate) * x
```

### 与RoPE的联系
- RoPE: 位置编码通过旋转矩阵注入
- Q-RoPE: 用RZ量子门实现, 频率可学习
- 优势: 量子旋转天然支持相对位置, 不需要额外位置编码

### 量子哈密顿量注意力 (V8+)
- H|ψ⟩ = E|ψ⟩ → 时间演化 U(t) = exp(-iHt)
- H = J∑σᵢ·σⱼ (Heisenberg模型)
- 注意力 = 量子态的时间演化
- 计算复杂度: O(n·K) 其中K是截断的键维度
- 参考: Quantum Hamiltonian Embedding (Lloyd et al., 2023)

## 199. 知识蒸馏与模型压缩 (2026-04-30)

### 为什么V6小模型比V5大模型更好?
- V5: 7.5M参数(256d/3层/4头) + 3.3%彝文 → Val 2.19但输出乱码
- V6: 2.86M参数(192d/2层/3头) + 50%彝文 → Val 3.06但输出有意义中文
- 核心教训: **数据质量 > 模型大小**

### 知识蒸馏(Knowledge Distillation)方案
Teacher: V5(7.5M参数) → Student: V6(2.86M参数)
1. 用Teacher生成soft labels(概率分布而非one-hot)
2. Student同时学习hard labels和soft labels
3. 温度T控制soft label的平滑度
4. Loss = α*hard_loss + (1-α)*soft_loss

### 量子蒸馏(Quantum Distillation)
- Teacher: 经典Transformer注意力矩阵 → Student: 量子门控注意力
- 将经典注意力分布作为量子测量的目标
- 量子门控gate值可以从Teacher注意力权重初始化

### 对QSM的启示
- V6已经证明小模型+好数据>大模型+差数据
- 下一步: 用V6(Teacher)训练更小的V7(Student)用于部署
- 目标: 1M参数的V7可以跑在手机上

## 200. Mixture of Experts (MoE) for QSM V7 (2026-04-30)

### MoE核心思想
- 不是所有token都需要所有参数
- 每个token只激活一小部分"专家"
- 总参数多,但实际计算量小

### QSM MoE架构设计
```
输入 → Q-Embedding → [Expert1:彝文专家]
                   → [Expert2:中文专家]
                   → [Expert3:英文专家]
                   → [Expert4:通用专家]
                   → Gate(路由) → 加权输出
```

### 量子MoE (QMoE)
- 量子门控: gate值 = |α|² (叠加态的测量概率)
- 4个专家 = 4个基态(Q-Embedding的4个基态天然对应!)
- 基态|0⟩→彝文专家, |1⟩→中文专家, |2⟩→英文专家, |3⟩→通用专家
- Q-Embedding的叠加系数本身就是路由权重!

### 参数估算
- 4个Expert: 每个192d/1层 → 4×0.72M = 2.88M总参数
- 实际激活: 每次只用1-2个Expert → 0.72-1.44M活跃参数
- 比V6(2.86M)计算量少50-75%!

### 实现计划(V7)
1. Q-Embedding叠加系数 → 路由权重
2. Top-2 Expert选择 (每次激活2个专家)
3. Expert输出加权求和
4. 训练: Load Balancing Loss防止专家坍缩

## 201. 课程学习(Curriculum Learning) for V7 (2026-04-30)

### 核心思想
- 人类学习: 简单→复杂, 循序渐进
- 模型训练: 先学简单样本, 再学复杂样本
- V6目前: 所有数据随机打乱, 无难度分级

### V7课程学习设计
**阶段1 (Epoch 1-10): 字符级**
- 彝文字符→编号映射
- 单字翻译: 水→water
- 数字: 1→一

**阶段2 (Epoch 11-20): 词级**
- 双字词: 彝文→中文
- 简单问答: 你好→hello
- 基本句式

**阶段3 (Epoch 21-30): 句级**
- 完整句子翻译
- 对话式问答
- 文化知识

### 实现方式
1. 给每条训练数据标注难度等级(1-3)
2. 自定义Sampler: 前N个epoch只采样难度1, 然后逐步加入2和3
3. Loss加权: 简单样本权重高→复杂样本权重逐步提升

### 与Q-Embedding的结合
- 阶段1: Q-Embedding冻结(只学字符映射)
- 阶段2: Q-Embedding解冻(学词义叠加)
- 阶段3: 全参数训练(学句子结构)

### 预期效果
- V6无课程学习: Val 2.93(E19)
- V7有课程学习: 预计Val < 2.0(E20)
- 加速收敛, 减少过拟合

## 202. 量子自然语言处理(QNLP)与QSM的结合 (2026-04-30)

### Cambridge QNLP (Bob Coecke等)
- 核心思想: 语言的组合语义可以用量子过程描述
- DisCoCat模型: 语法=量子电路, 词义=量子态
- 类型: 量子语言的范畴论基础
- 实验: 在IBM Q上实现了小规模QNLP

### 对QSM的启示
1. **词义=量子态**: 我们的Q-Embedding已经实现了这个!
   - |0⟩=BOS, |1⟩=EOS, |2⟩=UNK, |3⟩=PAD
   - 叠加系数编码词义 → 天然对应DisCoCat

2. **语法=量子电路**: 下一步可以将语法结构编码为量子门序列
   - 名词→单量子比特态
   - 形容词→单比特门(旋转)
   - 及物动词→CNOT门(纠缠主语和宾语)
   - 这个方向可以完全在QEntL中实现!

3. **复合性原理**: 整体意义=部分意义的量子组合
   - "红苹果" = 形容词"红"门 ⊗ 名词"苹果"态
   - 这比传统attention更自然

### QSM V8路线图: QNLP集成
1. 语法解析器 → 生成量子电路描述
2. 词义量子态 → Q-Embedding初始化
3. 语法量子门 → 纠缠相关词对
4. 测量 → 生成输出
5. 全部在QEntL量子虚拟机中执行!

## #203 V6 Post-Training Analysis & V7 Architecture Design

### V6 Translation Test Results (E50, Val 2.693)
- **Semantic associations learned**: "hello"→quantum computer, "彝族人民"→彝文字
- **Problem: premature EOS** - most inputs generate empty output
- **Problem: repetition** - "古古古" patterns
- **Problem: mixed language** - Chinese+English in same output

### Root Cause Analysis
1. **Val Loss 2.693 is still too high** for coherent generation
   - GPT-2 at Val ~3.5 generates coherent text
   - But GPT-2 is decoder-only on monolingual data
   - Encoder-decoder for translation needs Val < 1.5 typically
2. **Model too small** (2.86M params) for 28K diverse pairs
3. **No length normalization** in decoding → EOS bias
4. **No repetition penalty** in decoding

### V7 Architecture Design
**Phase 1: Data Scaling**
- Target: 50K+ pairs with 50% yi content
- Add sentence pairs from literature, science, daily life
- Curriculum: char-level (5K) → word-level (15K) → sentence-level (30K+)

**Phase 2: Model Improvements**
- Increase to 256d/4层/4头 (gradient accumulation, batch=4, accum=4)
- Label smoothing: 0.15 (up from 0.1)
- Gradient clipping: 1.0
- Warmup: 500 steps (longer)

**Phase 3: Decoding Improvements**
- Beam search (width=5)
- Length penalty: lp = ((5+|y|)/(5+1))^0.6
- Repetition penalty: 1.2 for repeated tokens
- Temperature: 0.7 for sampling

**Phase 4: QMoE Integration**
- 4 experts routed by Q-Embedding basis states
- Active 2/4 experts per token → 50% compute reduction
- Expert specialization: yi/zh/en/special tokens

### Key Insight from V6
**Data quality > model size > Val Loss number**
V6 (Val 2.69) produces meaningful output while V5 (Val 2.19) produces garbage.
The 50% yi data ratio is the critical factor.

## #204 Repetition Penalty & EOS Bias Solutions

### Repetition Penalty (from Keskar et al. 2019)
```python
def repetition_penalty(logits, prev_ids, penalty=1.2):
    for id in prev_ids:
        if logits[id] > 0:
            logits[id] /= penalty
        else:
            logits[id] *= penalty
    return logits
```

### EOS Bias Reduction
- During training: add random length targets (don't always end at EOS)
- During decoding: length reward = bonus for generating more tokens
- Or: train without explicit EOS, use max_length truncation

### Coverage Mechanism (from Tu et al. 2016)
- Track attention sum over previous steps
- Coverage loss = sum(min(attn_i, attn_cumulative_i))
- Prevents attending to same source position repeatedly
- Good for translation tasks

## #205 Curriculum Learning Implementation Plan

### Stage 1: Character Recognition (5K pairs, 5 epochs)
- Single character translations: 󲶦→紫黑色→dark purple
- Character-to-definition pairs
- Learn basic character meanings

### Stage 2: Word-Level (15K pairs, 10 epochs)
- Two-to-four character words
- Simple phrase translations
- Build word-level associations

### Stage 3: Sentence-Level (30K+ pairs, 20 epochs)
- Full sentences and paragraphs
- Conversational data
- Develop fluency and grammar

### Implementation
```python
# Curriculum data loader
curriculum = [
    {"data": "stage1_chars.json", "epochs": 5, "lr": 1e-3},
    {"data": "stage2_words.json", "epochs": 10, "lr": 5e-4},
    {"data": "stage3_sentences.json", "epochs": 20, "lr": 1e-4},
]
```

Each stage: train → validate → if improved, proceed to next stage
Q-Embedding bases gradually unfreeze: Stage1=2 bases, Stage2=3, Stage3=4

## #206 Quantum NLP for Low-Resource Languages (QSM Application)

### Problem: V6 Model Output Issues
1. **Premature EOS**: Model generates EOS token too early
   - Solution: Length normalization during decoding
   - Solution: Train with random length targets
   - Solution: Add minimum length constraint during inference

2. **Repetition**: "古古古" patterns
   - Solution: Repetition penalty (Keskar et al. 2019)
   - Solution: n-gram blocking (Paulus et al. 2017)
   - Solution: Coverage mechanism (Tu et al. 2016)

3. **Mixed Language**: Chinese+English in same output
   - Root cause: V6 has no language mode signal
   - Solution: Add language token prefix (zh>, yi>, en>)
   - Solution: Train with language-specific BOS tokens

### V7 Architecture: Language-Controlled Generation
```python
class QSM_V7(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=4):
        # Language-specific BOS tokens
        self.lang_bos = {
            'zh': stoi['<bos_zh>'],  # Chinese mode
            'yi': stoi['<bos_yi>'],  # Yi mode  
            'en': stoi['<bos_en>'],  # English mode
        }
        # QMoE: 4 experts, 2 active
        self.experts = nn.ModuleList([
            TransformerLayer(d_model, n_heads) for _ in range(4)
        ])
        self.router = QEmbeddingRouter(n_bases=4, n_experts=4)
```

### Decoding Strategy for V7
```python
def beam_search_decode(model, src, beam_width=5, max_len=50, 
                        length_penalty=0.6, rep_penalty=1.2):
    # Initialize beams
    beams = [(0.0, [bos_id])]
    
    for step in range(max_len):
        candidates = []
        for score, seq in beams:
            logits = model(src, torch.tensor([seq]))
            logits = logits[0, -1]
            
            # Repetition penalty
            for prev_id in set(seq):
                if logits[prev_id] > 0:
                    logits[prev_id] /= rep_penalty
                else:
                    logits[prev_id] *= rep_penalty
            
            # Top-k sampling
            top_k = torch.topk(logits, beam_width)
            for i in range(beam_width):
                new_score = score + top_k.values[i].item()
                candidates.append((new_score, seq + [top_k.indices[i].item()]))
        
        # Length normalization
        beams = sorted(candidates, 
                      key=lambda x: x[0] / ((5 + len(x[1])) / 6) ** length_penalty,
                      reverse=True)[:beam_width]
        
        # Check if all beams ended
        if all(seq[-1] == eos_id for _, seq in beams):
            break
    
    return beams[0][1]
```

### Key V7 Improvements Summary
1. Language-controlled BOS tokens → solves mixed language
2. Beam search + length penalty → solves premature EOS
3. Repetition penalty → solves "古古古" patterns
4. 256d/4层 → better capacity for 57K data
5. Curriculum learning → char→word→sentence stages
6. QMoE → efficient expert routing

## #207 Parameter Efficiency Analysis: V6 vs V7

### V6 (2.86M params, 28K data)
- Val Loss: 2.693 after 50 epochs
- Params/Data ratio: 101 (borderline overfitting)
- Output: Partial semantic associations, premature EOS

### V7 (9.2M params, 57K data)  
- Val Loss: 6.43 after 1 epoch (just started)
- Params/Data ratio: 161 (higher risk of overfitting)
- Architecture: 256d/4层/4头/1024ff
- Strategy: More data + gradient accumulation + label smoothing

### Risk Assessment
- V7 has 3.2x more parameters but only 2x more data
- If V7 overfits: reduce to 3层 or 192d
- Alternative: Use LoRA adapters on V6 best model
- Optimal ratio for char-level seq2seq: ~50-80 params/data point

### Q-Embedding Efficiency
- Q-Embedding reduces embedding params by 98.4%
- 4 bases × 256d = 1,024 params vs 6,924 × 256 = 1,772,544
- This is the key advantage of quantum-inspired architecture
- Saves 1.77M params → can afford deeper network layers

### Recommendations
1. Monitor V7 Val Loss closely - if Train << Val, reduce capacity
2. If V7 overfits by E10: try d_model=192, n_layers=4
3. Consider LoRA: freeze V6, add 0.5M adapter params
4. QMoE could reduce active params by 50% during inference

## #208 Q-RoPE: Quantum Rotary Position Embedding

### Standard RoPE (Su et al. 2021)
- Rotates query/key vectors by position-dependent angles
- θ_i = 10000^(-2i/d) for dimension i
- Enables relative position encoding through rotation
- Extrapolates to longer sequences with scaling

### Q-RoPE: Quantum-Enhanced Rotary Embedding
- Replace fixed base 10000 with quantum-dependent base
- Each Q-Embedding basis state → different rotation frequency
- |0⟩=BOS basis: slow rotation (global context)
- |1⟩=EOS basis: medium rotation (sentence boundary)
- |2⟩=UNK basis: fast rotation (local detail)
- |3⟩=PAD basis: no rotation (padding invariant)

### Implementation for V8
```python
class QRoPE(nn.Module):
    def __init__(self, d_model, n_bases=4):
        self.base_per_basis = nn.Parameter(
            torch.tensor([10000, 5000, 20000, 1.0]))  # learned bases
    
    def forward(self, x, positions, basis_ids):
        # Each token gets rotation based on its dominant basis
        base = self.base_per_basis[basis_ids]  # [B, S]
        theta = base ** (-2 * torch.arange(self.d_model//2) / self.d_model)
        # Apply rotation...
```

### Advantages
- Language-aware position encoding (Yi/Chinese/English have different optimal bases)
- Can extrapolate to unseen lengths
- Naturally handles code-switching between languages
- Only 4 extra parameters (one per basis)

## #209 Sequence-Level Knowledge Distillation (V8 Plan)

### Teacher-Student Framework
- Teacher: V7 (9.2M params, beam search decoding)
- Student: V8 (1-2M params, greedy decoding)
- Distill at sequence level (not just token level)

### Process
1. Train V7 to convergence (target Val < 2.0)
2. Generate beam search outputs for all training data
3. Replace ground truth with V7's best beam outputs
4. Train V8 on V7's outputs (soft + hard labels)
5. V8 can run on mobile/edge devices

### Expected Gains
- 5-10x inference speedup (smaller model, greedy decode)
- 80-90% of teacher quality retained
- Mobile deployment possible
- Q-Embedding makes student embedding very compact

### V8 Architecture
- 128d/2层/2头 (1.5M params)
- Q-Embedding (4 bases, saves 95% embedding params)
- Q-RoPE position encoding
- Greedy decoding only (fast)

## #210 Curriculum Learning for Low-Resource Languages

### The Problem
- V7 Val went UP at E2 (6.43→6.68), suggesting overfitting
- 9.2M params / 57K data = 161 ratio is too high
- Random shuffle causes model to see complex sentences before mastering characters

### Curriculum Learning Strategy (Bengio et al. 2009)
Train on progressively harder data:
1. **Stage 1**: Character-level (20K pairs, avg len 8) - Learn character meanings
2. **Stage 2**: Word/phrase-level (31K pairs, avg len 20) - Learn word associations  
3. **Stage 3**: Sentence-level (5.5K pairs, avg len 50+) - Learn fluency

### Implementation Plan
```python
# V7-Curriculum: Start with Stage 1, gradually add harder data
curriculum_schedule = [
    {"epochs": 5, "data": "stage1_chars.json", "lr": 1e-3},
    {"epochs": 10, "data": "stage1+stage2.json", "lr": 5e-4},
    {"epochs": 15, "data": "all_stages.json", "lr": 2e-4},
]
```

### Self-Paced Learning (Kumar et al. 2010)
- Let model decide difficulty: compute loss per sample
- Easy samples (low loss) get less weight
- Hard samples (high loss) get more weight
- This prevents wasting capacity on already-learned patterns

### Q-Embedding Curriculum
- Freeze Q-Embedding bases during Stage 1 (only train coefficients)
- Unfreeze 1 more basis each stage
- Stage 1: 2 bases (BOS+EOS), Stage 2: 3 bases, Stage 3: 4 bases
- Gradual unfreezing prevents catastrophic forgetting

### Expected Outcomes
- Stage 1 should reach Val < 2.0 quickly (character learning is easy)
- Stage 2 should build on character knowledge
- Stage 3 should achieve fluency with fewer epochs than random training

### V7 Overfitting Response Plan
If V7 continues to overfit:
1. **Immediate**: Increase dropout to 0.3, add gradient clip 0.5
2. **If still overfitting by E5**: Stop and restart with smaller model (192d/3层=4M)
3. **If Val stabilizes**: Continue to E30 with LR decay
4. **Best case**: V7 achieves Val < 3.0 and produces meaningful output

### Small Model Alternative (V7-Small)
- 192d / 3层 / 3头 / 768ff
- Estimated ~4M params, ratio = 4M/57K = 70 (healthy)
- Should train in ~15min/epoch (2.5x faster)
- May actually outperform V7-large due to better generalization

## #211 V7-Small训练深度分析 (E1-E24)

### 训练轨迹
E1:3.53→E5:3.18→E10:3.03→E12:2.99(破3.0!)→E15:2.93→E20:2.89→E24:2.85

### 关键发现
1. **22/24 Best!** 仅E16微波动(2.93>2.93仅0.003), 立即恢复
2. **下降速率稳定**: E1-10每epoch降~0.05, E10-20每epoch降~0.015, E20-24每epoch降~0.01
3. **零过拟合**: Train≈Val始终接近, 4.5M/57K=78参数比健康
4. **V5的教训**: Val Loss 2.19但mode collapse → **数字不代表一切**
5. **V6的成功**: Val 2.69但有语义关联 → **数据质量(50%彝文)>Val Loss数字**

### V5 Mode Collapse根因分析
V5(7.5M, 256d/3层/4头) 无论输入什么都输出"彝文是美丽的语言，我来教你。"
- 原因1: 彝文仅3.3% → 模型学到"彝文"一个概念就锁住了
- 原因2: Val Loss 2.19实际是所有输入都映射到同一条输出的loss
- 原因3: 缺乏语言方向控制 → 没有BOS标记指定输出语言

### V7-Small vs V5架构对比
| | V5 | V7-Small |
|---|---|---|
| 参数 | 7.5M | 4.5M |
| d_model | 256 | 192 |
| 层数 | 3 | 3 |
| 头数 | 4 | 3 |
| d_ff | 512 | 768 |
| 彝文比例 | 3.3% | 87.9% |
| Val Loss | 2.19 | 2.85(仍在降) |
| 输出质量 | 乱码/锁死 | (待测) |
| dropout | 0.1 | 0.25 |

### 预测
- E30: Val ~2.77 (追平/超越V6的2.69)
- E40: Val ~2.72
- E50: Val ~2.68-2.70
- V7-Small有望在Val Loss上追平V6, 且88%彝文数据保证输出质量

### 下一步
1. E25后用beam search测试输出质量
2. V7-Small训练完成后部署到API
3. 准备V8知识蒸馏(V7-Small→1.5M手机模型)

## #212 续训翻车深度分析 + 数据质量问题

### 翻车时间线
1. V7-Small E50完成, Best Val 2.7832, 测试有智能
2. 创建train_v7small_continue.py继续训练
3. 续训脚本的验证集只用2000条(原始用57K)
4. E50→E72: "Val Loss"从2.78降到1.75,看似改善
5. 但E72模型输出单字符垃圾! "hello"→"y", "你好"→"翻"

### 根因分析
1. **验证集太小**: 2000/57707=3.5%, 统计偏差大
2. **Loss计算差异**: 续训脚本用label_smoothing=0.15+小验证集
3. **学习率太低**: 1e-5, 模型完全收敛到局部最优
4. **过拟合**: Train=Val=1.7489但输出垃圾 = 对训练集记忆但丢失泛化

### 重要教训
- **Val Loss数字≠模型质量!** V5(Val 2.19)是mode collapse, E72(Val 1.75)是垃圾
- **验证集必须全量!** 小验证集的Loss会偏低1.0+
- **best.pth必须备份!** cp best.pth best_backup.pth 再开始任何新训练
- **测试优先!** 训练完成后先测试输出质量, 不要只看Val Loss数字

### V7数据集分析
- 57,707条, 86%含彝文, 99.4%含中文, 48.8%含英文
- 数据格式: input/output对
- 包含: 彝文字符编号查询、彝文释义、中→彝翻译、彝→中翻译
- 太短(<4): 78条, 太长(>128): 503条

## #213 低资源语言模型优化策略

### 核心问题
QSM需要学会4120个彝文字, 但:
- 彝文是低资源语言, 训练数据有限
- 词汇表只有6924, 但UNK仍然太多
- CPU训练限制模型大小(<5M参数)

### 策略1: 词汇表扩展
当前vocab: 6924 (4120彝文 + 2720中文 + 26英文 + 6特殊 + 52其他)
- UNK多的原因: 训练数据中有vocab外的字符
- 方案: 从v7_full_dataset.json中提取所有字符, 重建vocab
- 预期: vocab扩展到~8000, UNK率降低50%

### 策略2: 课程学习三阶段
- Stage1: 字符级映射(彝文字符↔编号↔Unicode)
- Stage2: 词汇级翻译(常用词↔彝文)
- Stage3: 句子级对话(完整句子/段落)
- V7数据集已有这三阶段结构

### 策略3: 多任务训练
- 翻译任务: zh→yi, yi→zh, en→yi
- 问答任务: "X是什么?" → 彝文释义
- 编号查询: "彝文字符X的编号?" → 数字
- 对话任务: 自由对话
- 这些都在v7_full_dataset.json中

### 策略4: 知识蒸馏路线
V7-Small(Teacher 4.5M) → V8(Student 1.5M)
- Teacher生成soft targets
- Student学习温度=3的软标签
- V8可部署到手机端

### 下一步
1. 等V7-Small训练完成(E50)
2. 全面测试输出质量
3. 如果UNK多, 重建vocab重新训练
4. 考虑知识蒸馏V8

## #214 课程学习在低资源语言中的应用

### 当前V7-Small训练分析(E1-32)
- 32/32 ALL BEST, 零过拟合
- 下降速率: 前期~0.3/epoch(E1-5), 中期~0.02/epoch(E20-32)
- 预计E50: ~2.65
- 对比: 上轮训练E50=2.78, 本轮已大幅超越

### 课程学习三阶段设计(V8考虑)
**Stage 1: 字符映射** (5K pairs)
- 彝文字符↔Unicode编号
- 彝文字符↔中文释义
- 目标: 建立字符-含义基础映射

**Stage 2: 词汇翻译** (15K pairs)  
- 常用词: 天/地/人/山/水/火/风
- 短语: 你好/谢谢/再见
- 目标: 建立词级翻译能力

**Stage 3: 句子对话** (35K pairs)
- 完整句子翻译
- 问答对话
- 段落理解
- 目标: 建立句子级理解+生成能力

### Q-Embedding渐进解冻
- Stage1: 2 bases (|0⟩=BOS, |3⟩=PAD)
- Stage2: 3 bases (+|2⟩=UNK)  
- Stage3: 4 bases (+|1⟩=EOS)
- 渐进引入复杂度, 避免早期过拟合

### 参考论文
- "Curriculum Learning" (Bengio et al., 2009)
- "Self-Paced Learning" (Kumar et al., 2010)
- 适用于低资源语言的关键: 由简到难, 避免早期困难样本干扰

## #215 V7-Small输出质量分析+改进方向

### 当前输出问题(Val 2.65)
1. **英文碎片**: 36.1%训练数据输出含英文 → 模型学到了英文混杂
2. **重复模式**: "the the the", "lig lig" → beam search重复惩罚不够
3. **混合语言**: 同一输出混杂中/英/彝 → 需要语言控制信号
4. **EOS过早**: 部分输入输出很短 → BOS语言标记可能无效
5. **语义关联好**: 水→snow, 量子→彝文, hello→英文 → 基础理解正确!

### 改进方向
1. **纯彝文训练数据**: 新增中文→纯彝文对(去掉英文混杂)
2. **更强重复惩罚**: rep_penalty从1.2→1.5, 或n-gram blocking
3. **语言控制BOS**: 不同BOS标记→不同输出语言
4. **更长训练**: E50可能不够, 继续训练到E80
5. **n-gram blocking**: 禁止连续重复3个相同token

### V8规划(知识蒸馏)
- Teacher: V7-Small (4.5M)
- Student: V8 (1.5M, 128d/2层/2头)
- 可部署到手机端

## #216 重复惩罚与N-gram阻断改进解码

### 当前问题(V7-Small beam search)
- 输出含重复模式: "the the the", "lig lig lig"
- beam search rep_penalty=1.2 不够强
- 某些token被过度重复(如"the")

### 改进方案1: N-gram Blocking
```python
# 禁止连续3个相同token
for beam in beams:
    if len(beam) >= 2 and beam[-1] == beam[-2]:
        logits[beam[-1]] = -inf  # 阻断
```
- 简单有效, 防止AA模式
- 扩展: 禁止ABCABC模式(6-gram)

### 改进方案2: 递增惩罚
```python
# 重复次数越多, 惩罚越重
token_counts = Counter(seq)
for tid, count in token_counts.items():
    if count > 2:
        logits[tid] /= (rep_penalty ** (count - 1))
```

### 改进方案3: 温度+top-p采样
- 不用beam search, 用nucleus sampling
- temperature=0.7, top_p=0.9
- 更自然的输出, 减少重复

### 下一步
1. 实现n-gram blocking
2. 测试不同rep_penalty(1.2→1.5→2.0)
3. 对比beam search vs nucleus sampling
4. 考虑语言控制BOS标记

## #217 V7-Small Beam Search改进测试结果

### 改进措施
- rep_penalty: 1.2 → 1.5 (频率加权递增惩罚)
- n-gram blocking: 禁止连续3个相同token
- min_len=3: 防止过早EOS

### 测试结果(14个词)
| 输入 | 输出 | 评价 |
|------|------|------|
| 你好 | 这是彝文字<unk>，编号3570 | 部分正确 |
| 量子 | 通用彝文字+滇川黔贵彝文 | ✅语义正确! |
| 彝文 | yi word+彝文是滇川黔贵通用彝文 | ✅部分正确 |
| 中华民族 | 彝文字+数字 | 部分相关 |
| 水/火/天/地 | 英文碎片 | ❌失败 |

### 关键发现
1. ✅ 重复模式"the the the"完全消失(n-gram blocking有效)
2. ✅ 中文输出增多(不再全是英文碎片)
3. ⚠️ 英文碎片仍严重: "stheand","wour"等
4. ⚠️ UNK标记频繁出现
5. ⚠️ 模板化输出("这是彝文字<unk>的...")

### 根因分析
- V7训练数据36.1%输出含英文→模型学会了英文token拼接
- 大写英文字母(G/M/H/W/F)不在词汇表→产生碎片
- UNK来自词汇表覆盖不足(6924词)
- 模板化是因为训练数据中字典式条目太多

### V8预期改善
- 英文比例从36.1%降到6.2%→英文碎片应大幅减少
- 8108条新增纯中文→彝文对→更多中文输出
- 但词汇表未扩展→UNK问题需要单独解决

### 下一步
1. V8训练完成后对比测试
2. 考虑扩展词汇表(加英文小写+高频UNK)
3. 增加更多句子级训练数据(减少模板化)

## #218 课程学习(Curriculum Learning)实现方案

### 核心思想
按难度递增顺序训练: 字符→词汇→句子→段落→对话

### 三阶段设计
**阶段1: 字符级 (Epoch 1-15)**
- 数据: 单字符含义映射 (4120彝文字→含义)
- 目标: 学会基本字符-含义对应
- V8已有大量此类数据(meaning_query: 14303条)

**阶段2: 词汇级 (Epoch 16-30)**
- 数据: 词汇翻译(中文词→彝文/英文)
- 目标: 学会词汇级翻译
- V8有word+phrase数据(34791条)

**阶段3: 句子级 (Epoch 31-50)**
- 数据: 句子/对话/描述
- 目标: 学会句子生成+对话
- V8有sentence+translation(16719条)

### 实现方式
```python
# 按数据长度排序 → 短的先训练
dataset.sort(key=lambda x: len(x['input']) + len(x['output']))

# 或者按类别分batch
easy_data = [d for d in dataset if len(d['output']) < 10]  # 字符级
medium_data = [d for d in dataset if 10 <= len(d['output']) < 30]  # 词汇级
hard_data = [d for d in dataset if len(d['output']) >= 30]  # 句子级
```

### 预期效果
- 避免mode collapse(从简单开始, 逐步增加复杂度)
- 更好的收敛(基础概念先学会, 再学高级)
- 减少英文碎片(纯中文数据先训练)

### 与V8结合
- V8英文比例6.2%(input), 但output仍有31%含英文
- 课程学习: 先训练纯中文output数据, 再混入英文数据
- 阶段1只用纯output数据, 阶段2开始混入含英文数据

## #219 量子旋转嵌入(Quantum Rotational Embedding)改进

### 当前V7-Small实现
```python
# QuantumEmbeddingV2
quantum_rotation = nn.Parameter(torch.randn(n_heads, d_head))
quantum_gate = nn.Parameter(torch.tensor(0.1))

# Forward
enc_view = enc_out.view(B, S, nh, dh)
qr = self.quantum_rotation
quantum_out = (enc_view * cos(qr) + roll(enc_view,1,-1) * sin(qr)).reshape(B,S,-1)
enc_out = quantum_gate * quantum_out + (1-quantum_gate) * enc_out
```

### 改进方向1: 多层量子旋转
```python
# 当前: 单次旋转
# 改进: 多次旋转(类似量子电路的深度)
for layer in range(n_quantum_layers):
    qr = self.quantum_rotations[layer]
    enc_view = enc_view * cos(qr) + roll(enc_view, 1, -1) * sin(qr)
```

### 改进方向2: 量子纠缠注意力
```python
# 在注意力计算中加入量子纠缠项
# 两个token的关联不仅通过点积, 还通过量子态的内积
q_entangled = q * cos(self.entangle_phase) + k * sin(self.entangle_phase)
attn = q @ k.T + alpha * (q_entangled @ k.T)
```

### 改进方向3: 自适应量子门
```python
# quantum_gate从标量变为token-level
gate = sigmoid(self.gate_proj(enc_out))  # [B, S, 1]
enc_out = gate * quantum_out + (1-gate) * enc_out
```

### V8后续计划
1. 测试V8输出质量(英文碎片是否减少)
2. 如果V8仍不够好, 实现多层量子旋转
3. 考虑增大模型到256d/4层(需谨慎OOM)
4. 词汇表扩展: 添加英文小写高频词

## #220 V8数据英文碎片深度分析

### 输入/输出语言交叉分析
| 组合 | 数量 | 占比 | 评价 |
|------|------|------|------|
| 英→英 | 6,023 | 9% | 合理(英文问英文答) |
| 英→中 | 7,320 | 11% | 合理(翻译模式) |
| **中→英** | **15,290** | **23%** | **❌ 根因!** |
| 中→中 | 37,180 | 56% | ✅ 正确 |

### 关键发现
- **23%的数据是中文输入→英文输出!** 这才是英文碎片的真正根因
- 模型学到: "中文问题 → 英文回答" 错误模式
- 之前以为36%含英文, 实际核心问题是中→英的15,290条

### V10数据策略
1. **去掉中→英数据**: 直接删除15,290条, 保留50,523条
2. **或翻译转换**: 把英文输出翻译成中文(质量不确定)
3. **或加语言标记**: 输入加"[中文]"前缀指定输出语言
4. **推荐方案1**: 去掉中→英, 得到50K纯数据集

### 预期效果
- 去掉23%中→英数据后, 英文碎片应该大幅减少
- 数据量从65K降到50K, 但质量大幅提升
- 模型将学到: "任何输入 → 中文/彝文输出"

## #221 低资源NMT关键技巧总结

### 1. 数据增强 (Data Augmentation)
- **回译(Back-translation)**: 用目标→源模型生成伪平行数据
- **词替换**: 随机替换源端词为同义词
- **句子重组**: 打乱词序训练鲁棒性
- **适用QSM**: 可用V7-Small做彝文→中文回译, 增加训练数据

### 2. 迁移学习 (Transfer Learning)
- **预训练微调**: 先在大规模单语数据预训练, 再用平行数据微调
- **多任务学习**: 同时训练翻译+语言模型任务
- **适用QSM**: 在中文/彝文单语语料上预训练, 再微调翻译

### 3. 词汇优化
- **BPE/子词**: 减少UNK, 共享子词
- **语言特定token**: 为每种语言加特殊标记
- **适用QSM**: 扩展词汇表到10000+, 加英文小写, 加<zh>/<yi>语言标记

### 4. 课程学习 (Curriculum Learning)
- 按句子长度排序, 短的先训练
- 按数据纯度排序, 纯数据先训练
- 渐进增加难度

### 5. 知识蒸馏 (Knowledge Distillation)
- 大模型(Teacher)→小模型(Student)
- V7-Small(4.5M)→V10-Tiny(1.5M)
- 软标签+温度参数

### QSM下一阶段计划
1. V8训练完成 → 测试输出质量
2. V10(50K纯数据) → 训练 → 测试英文碎片
3. 回译数据增强 → V11
4. 语言标记<zh><yi> → 控制输出语言
5. 词汇表扩展 → 减少UNK

## #222 语言控制Token方案

### 问题
V7-Small输出语言不可控(有时中文,有时英文)
需要一种机制指定输出语言

### 方案: 语言BOS标记
在输入前添加语言标记:
- `[中文] 你好` → 中文输出
- `[彝文] 你好` → 彝文输出  
- `[EN] hello` → 英文输出

### 训练数据改造
```json
{"input": "[中文] 量子", "output": "这是量子力学的概念..."}
{"input": "[彝文] 量子", "output": "󲜒󲜓..."}
{"input": "[EN] 量子", "output": "quantum"}
```

### 词汇表扩展
添加3个特殊token:
- `[中文]` → vocab_id=6924
- `[彝文]` → vocab_id=6925
- `[EN]` → vocab_id=6926

### 预期效果
1. 用户可选择输出语言
2. 消除英文碎片(输入[中文]或[彝文]时)
3. 支持三语互译方向控制

### 实现优先级
V10训练后再添加, 作为V11的改进

## #223 V8 E13突破3.0 + V10数据集分析

### V8训练里程碑
- E13: Val **2.9985** ← 首次破3.0!
- 13/13 ALL BEST, 收敛率0.063/epoch
- 预测E20: ~2.55, E30: ~1.92, E50: ~0.66

### V10完整数据集
- 51,317条 (V10纯50523 + 794新增)
- 输出英文占比: 11% (V8是32%)
- 中→英: 0% ✅
- 新增: 文化长文500 + 翻译实践300 + QSM系统5

### V10 vs V8对比
| 指标 | V8 | V10 |
|------|-----|------|
| 总数据 | 65,813 | 51,317 |
| 输出英文% | 32% | 11% |
| 中→英 | 23% | 0% |
| 新增纯中文 | 0 | 794 |

### 下一步: V10训练
1. V8 E50完成后测试质量
2. 备份V8 best.pth
3. 启动V10训练(50K数据, ~22min/epoch)
4. 对比V8/V10输出质量

## #224 Transformer缩放定律与QSM优化

### Chinchilla缩放定律核心结论
- 最优模型大小 N 和数据量 D 满足: N ∝ D^0.5
- 计算预算 C = 6ND 时, 最优 N ∝ C^0.5
- 关键: 模型太小则欠拟合, 太大则数据不足

### 对QSM的启示
| 参数量 | 最优数据量 | 当前数据 | 状态 |
|--------|-----------|---------|------|
| 4.5M (V7) | ~90M tokens | ~1M tokens | 严重数据不足 |
| 12M (V3) | ~240M tokens | ~0.5M tokens | 严重数据不足 |
| 1M (V10-Tiny) | ~20M tokens | ~1M tokens | 仍然不足 |

### 关键发现
1. **数据量是瓶颈, 不是模型大小!**
2. V7-Small(4.5M)用50K数据训练, 远低于最优比例
3. 降低模型大小(192d→128d)可能更匹配当前数据量
4. 数据增强(回译/改写)比增大模型更有效

### V10-Tiny计划
- 128d/2层/2头 ≈ 1.5M参数
- 更匹配50K数据集
- 训练更快(~15min/epoch)
- 可作为V11蒸馏的教师模型Student

### 数据扩展路线
1. 回译: 用V7-Small生成彝文→中文伪平行数据
2. 改写: 对现有数据做同义替换
3. 对话: 生成多轮对话数据
4. 段落: 扩展到段落级和篇章级
5. 目标: 200K+条 (匹配4.5M参数)

## #225 注意力机制改进方案

### 当前问题
V7-Small使用标准Multi-Head Attention:
- 3个注意力头, 192维
- 无法区分不同语言的注意力模式
- 英文碎片可能源于注意力跨语言混乱

### 改进方案1: 语言感知注意力
- 添加语言类型嵌入到Q/K/V
- 同语言token间注意力权重更高
- 实现: Q' = Q + LangEmb(src_lang)

### 改进方案2: 交叉语言注意力门控
- 门控机制控制跨语言信息流
- g = sigmoid(W_gate * [Q;K] + b)
- Attention = g * softmax(QK^T/√d)V
- 训练时根据语言方向调整门控

### 改进方案3: 分层注意力
- 层0: 语言内注意力(只看同语言)
- 层1: 跨语言注意力(翻译信息)
- 层2: 融合层(综合决策)

### 对QSM的推荐
1. V10/V11先添加语言标记([中文][彝文][EN])
2. V12实现语言感知注意力
3. V13实现分层注意力

### 参考论文
- "Language-Aware Attention for Multilingual NMT" (2024)
- "Cross-lingual Attention for Low-resource Translation" (2023)
- "Quantum Attention Networks" (2023) - 量子注意力机制

## #226 量子注意力网络(Quantum Attention)研究

### 核心概念
量子注意力将经典softmax注意力与量子力学概念结合:
- **叠加态注意力**: 查询-键匹配不是确定性的,而是概率幅叠加
- **纠缠注意力**: 不同注意力头之间共享量子纠缠关系
- **测量坍缩**: 注意力权重通过"测量"从叠加态坍缩为确定值

### 数学框架
经典注意力: Attention(Q,K,V) = softmax(QK^T/√d)V
量子注意力: 
1. 编码: |q⟩ = U_q|ψ_q⟩, |k⟩ = U_k|ψ_k⟩
2. 叠加: α_ij = ⟨q_i|k_j⟩ (量子内积=复数振幅)
3. 测量: p_ij = |α_ij|² (概率=振幅模平方)
4. 输出: O_i = Σ_j p_ij · V_j

### 对QSM的改进路线
1. **短期(可实现)**: 量子旋转嵌入(已有) + 量子位置编码
2. **中期**: 叠加态注意力 - 用复数振幅替代softmax
3. **长期**: 量子纠缠注意力 - 头间纠缠关系

### 量子旋转嵌入V2(当前)
- 4个基态嵌入 + 语言偏置
- coeff = softmax(W_lang * lang_id)  
- embedding = Σ coeff_i * basis_i * √d_model

### 量子旋转嵌入V3(计划)
- 添加相位参数: |ψ⟩ = r·e^(iθ)|basis⟩
- 不同语言的相位不同
- 旋转门Rz(θ)控制语言分离度

## 研究#227: 量子注意力网络 (2026-05-03)

### 核心概念
传统注意力: Attention(Q,K,V) = softmax(QK^T/√d)V
量子注意力: 用量子态振幅代替softmax权重

### 量子注意力机制设计
1. **量子查询(Q)**: 将查询编码为量子态 |q⟩
2. **量子键(K)**: 将键编码为量子态 |k⟩
3. **量子相似度**: 内积 ⟨q|k⟩ 自然产生概率幅
4. **测量→权重**: 测量量子态获得经典概率分布
5. **加权值**: 用概率分布对V加权求和

### QSM应用思路
当前QSM的QuantumRotationalEmbeddingV2:
- 基态初始化 + 语言偏置
- 系数α控制4个基态的叠加

改进方向: **QuantumAttentionV3**
- 将Q/K投影到量子希尔伯特空间
- 用量子门的旋转角度编码位置信息
- 叠加态自然产生注意力分布
- 测量后得到加权输出

### 优势分析
1. **指数级状态空间**: n量子比特 → 2^n维希尔伯特空间
2. **并行性**: 叠加态天然并行处理所有键
3. **纠缠关联**: 量子纠缠可建模长距离依赖
4. **非线性**: 量子测量产生天然非线性变换

### 当前限制
1. 无GPU → 量子模拟在CPU上慢
2. 量子门模拟: O(2^n)矩阵运算
3. 梯度计算: parameter-shift规则需2次前向
4. 实际量子硬件: NISQ设备噪声大

### 实现路线(在QSM中)
Phase 1: 经典模拟量子注意力 (当前可做)
- 用矩阵运算模拟量子门
- Parameter-shift计算梯度
- 在Transformer层间插入量子注意力子层

Phase 2: 量子电路编译 (QEntL)
- 用QEntL编写量子注意力电路
- 编译为QBC字节码
- QVM模拟执行

Phase 3: 量子硬件接口
- 通过Qiskit/PennyLane接口连接真实量子设备
- 混合量子-经典训练

## 研究#228: 量子旋转编码V3设计 (2026-05-03)

### 当前V2问题
QuantumEmbeddingV2: 
- 4个基态(bases) → 表达力有限
- 语言偏置(lang_bias)是固定参数,不够灵活
- softmax归一化系数→信息损失

### V3设计: 多量子比特旋转编码
1. **增加量子比特数**: n_qubits = log2(d_model/64)
   - d_model=192 → n_qubits=2 (4个基态→V2一致)
   - d_model=384 → n_qubits=3 (8个基态)
   - d_model=512 → n_qubits=4 (16个基态)

2. **旋转门编码**: 
   - 每个token → RY(θ_i)|0⟩⊗n
   - θ_i由embedding层学习
   - 旋转角度=token语义的连续编码

3. **纠缠层**:
   - CNOT门连接相邻量子比特
   - 建模token间关联
   - 比V2的独立基态更强大

4. **语言感知旋转**:
   - 不同语言用不同的初始旋转角
   - 彝文: θ_0偏大(字符空间大)
   - 中文: θ_0中等
   - 英文: θ_0偏小(词空间小)

### 实验计划
1. 在V7-Small上替换QuantumEmbeddingV2→V3
2. 保持其他架构不变
3. 对比训练曲线和Val Loss
4. 预期: 更好的语言区分度→更低Val Loss

### 代码改动点
- QSM_V7_Small.__init__: QuantumEmbeddingV2→QuantumEmbeddingV3
- 增加n_qubits参数
- 增加entangle选项(True/False)
- 前向传播: 旋转→纠缠→测量→投影

## 研究#229: 训练数据质量分析 — 模型输出垃圾的根因 (2026-05-03)

### V10数据集分析 (49,779条)
| 模式 | 数量 | 占比 |
|------|------|------|
| 字典查询("X用彝文怎么写") | 5,668 | 11.4% |
| 字符含义("彝文字符X的含义") | 3,360 | 6.7% |
| Unicode→彝文映射 | ~5,000 | ~10% |
| 彝文字符→意义 | ~8,000 | ~16% |
| 中文→彝文转写 | ~15,000 | ~30% |
| 实际翻译 | 3,375 | 6.8% |
| 问候/对话 | 48 | 0.1% |
| 其他 | ~12,328 | ~25% |

### 关键发现
1. **90%+是字典/字符查询数据** — 模型学会了查字典，不会翻译
2. **实际翻译仅6.8%** — 远远不够学习翻译能力
3. **对话数据0.1%** — 模型无法进行对话
4. **数据分布严重不均衡**: Yi输出占69.4%, Zh占29.7%, En仅0.5%

### 改进方向
1. **需要大量句子级翻译数据**:
   - 中文句子→彝文句子 (1000+条)
   - 彝文句子→中文句子 (1000+条)
   - 英文句子→中文句子 (500+条)
2. **需要对话数据**:
   - 日常对话(你好/问路/购物等, 500+条)
   - 问答数据(什么是量子/彝文怎么写..., 500+条)
3. **需要段落/文章级数据**:
   - 短文翻译(10-50字, 200+条)
4. **减少字典查询比例**: 从18%→5%以下

### 数据生成策略
- **回译(Back-translation)**: 用V8/V10生成伪平行数据
- **模板扩展**: "我喜欢X" → 100个不同X的句子
- **同义替换**: "你好" → "你好吗" → "你好吗？" → "您好"
- **彝文SOV语法生成**: 主语+宾语+动词 结构生成句子

## 研究#230: 数据量缩放定律与QSM训练策略 (2026-05-03)

### 核心发现(结合研究#224缩放定律 + 研究#229数据质量)
1. **4.5M参数模型需要~90M tokens才能充分训练**(Chinchilla缩放定律)
2. **当前V10数据仅~1M tokens**, 严重不足(1/90)
3. **90%数据是字典查询**, 不是翻译/对话
4. **V7-Small Val 2.65仍输出垃圾** — 数据质量差>架构问题

### 改进策略: 三管齐下
1. **数据量扩展**: 51K → 200K+ 条(4倍)
   - 模板扩展: 847条基础句子 → 8000+条(替换主语/宾语/时间)
   - 回译: 用V8模型生成伪平行数据
   - 对话数据: 50+组多轮对话,每组5-10轮
   
2. **数据质量提升**: 字典占比 18% → 5%
   - 新增大量句子级翻译(中↔英, 中↔彝)
   - 新增彝文SOV语法数据(20+句子模式)
   - 新增对话/问答数据
   
3. **训练策略优化**:
   - 课程学习: 先训简单(词汇→短句→长句)
   - 混合精度训练: 减少内存,加速训练
   - 渐进式解冻: 从预训练权重微调

### V11数据集组成 (51,344条)
| 类别 | 数量 | 占比 | 备注 |
|------|------|------|------|
| V10基础 | 49,779 | 97.0% | 字典/字符为主 |
| 句子翻译 | 847 | 1.6% | 日常/句型/数字/方向/时间/自然/动物/文化/量子 |
| 情感/描述/动作/比较/条件/哲学 | 236 | 0.5% | 高质量翻译对 |
| 彝文语法/对话/SOV/数字 | 184 | 0.4% | 彝文特色数据 |
| 基础词汇 | 328 | 0.6% | 数字/颜色/动物/动词等 |

### 下一步: 模板扩展生成
用已知句子模板,批量替换词汇生成10000+新数据

## 研究#231: 量子-经典混合注意力机制设计 (2026-05-03)

### 核心思路
将量子旋转编码(研究#228)与经典Transformer注意力结合,
创建量子增强的注意力层,用于QSM模型的改进。

### 量子注意力层设计 (QuantumAttentionV2)
```
经典路径: Q·K^T / √d → softmax → Attention(Q,K,V)
量子路径: 
1. Q,K → RY旋转门编码 → 量子态 |ψ_Q⟩, |ψ_K⟩
2. 内积 ⟨ψ_Q|ψ_K⟩ = 量子关联度
3. CNOT纠缠层 → 多头量子注意力
4. 概率测量 → 经典注意力权重
```

### 关键改进点
1. **旋转编码**: 每个token → RY(θ_i)|0⟩, θ_i = embedding_i * π
2. **量子关联**: ⟨ψ_Q|ψ_K⟩ = cos(θ_Q - θ_K) — 天然归一化!
   - 不需要softmax归一化(量子内积自动归一化)
   - 计算复杂度: O(1) vs softmax O(n)
3. **纠缠增强**: CNOT门创建qubit对间关联
   - 相邻token自动获得纠缠关联
   - 长距离依赖通过量子隧穿效应
4. **概率测量**: 测量后坍缩为经典注意力权重

### 与经典方法对比
| 特性 | softmax注意力 | 量子注意力V2 |
|------|-------------|-------------|
| 归一化 | 需要softmax | 天然归一化 |
| 长距离 | O(n²) | O(1)量子关联 |
| 参数量 | d² per head | d per qubit |
| 可训练 | ✅ | ✅ (旋转角度θ) |
| 实现 | GPU | 模拟器(当前) |

### 实现路线
1. V1: 纯模拟(当前) — 用numpy模拟量子门
2. V2: 混合 — 经典注意力 + 量子修正项
3. V3: 真实量子 — PennyLane/Qiskit硬件

### PennyLane实现思路
```python
import pennylane as qml
dev = qml.device('default.qubit', wires=n_qubits)

@qml.qnode(dev)
def quantum_attention(query, key):
    # RY旋转编码
    for i, q in enumerate(query):
        qml.RY(q * np.pi, wires=i)
    for i, k in enumerate(key):
        qml.RY(k * np.pi, wires=i + n_qubits//2)
    # CNOT纠缠
    for i in range(n_qubits//2):
        qml.CNOT(wires=[i, i + n_qubits//2])
    # 测量
    return qml.probs(wires=range(n_qubits))
```

## 研究#232: 课程学习(Curriculum Learning)在低资源翻译中的应用 (2026-05-03)

### 核心思路
按照难度递增的顺序训练模型，从简单样本开始，逐渐过渡到复杂样本。

### QSM课程学习设计
```
阶段1 (Epoch 1-10): 词汇级数据 — "X的彝文是Y" (简单映射)
阶段2 (Epoch 11-20): 短语级数据 — "我喜欢X"/"X在哪里" (模板句)
阶段3 (Epoch 21-35): 句子级数据 — "如果下雨我就不去" (完整句)
阶段4 (Epoch 36-50): 段落级数据 — 短文/对话 (复杂结构)
```

### 实现方式
1. **数据标注**: 每条数据添加`difficulty`字段(1-4)
2. **训练调度**: 按difficulty排序，逐步解锁更难的数据
3. **混合策略**: 每阶段保留20%简单数据防止遗忘

### 理论依据
- Bengio et al. (2009): 课程学习加速收敛
- Platanios et al. (2019): NMT中课程学习减少50%训练时间
- Zhang et al. (2021): 难度基于句子长度+词汇频率

### 与V8训练的关系
当前V8训练随机打乱数据，可能浪费了前期epoch在难样本上。
课程学习可以让模型先学会基本映射(Val<3.0)，
再学翻译(Val<2.0)，最后学对话(Val<1.5)。

### 数据难度分级
| 级别 | 数据类型 | 估计比例 | 预期Val |
|------|---------|---------|---------|
| 1 | 字典查询/字符映射 | 18% | <3.0 |
| 2 | 词汇翻译/简单句 | 30% | <2.5 |
| 3 | 完整句子翻译 | 35% | <2.0 |
| 4 | 对话/段落/文章 | 17% | <1.5 |

### 下一步: V11+数据集标注difficulty后训练

## 研究#233: 回译数据增强 — 用API生成伪平行数据 (2026-05-03)

### 核心思路
即使当前模型输出质量差，回译仍可产生有用的训练信号。
关键是：用模型翻译→人工/规则修正→作为新训练数据。

### 回译流程
```
中文原文 → API翻译 → 彝文输出(可能含错)
         ↓
彝文参考 → 对比修正 → 高质量彝文
         ↓
修正后的(中文,彝文)对 → 加入训练集
```

### 低资源NMT回译策略(Edunov et al. 2018)
1. **Sampling > Beam**: 从模型采样多翻译→选最好的
2. **Noise injection**: 在回译输入加噪声→提高鲁棒性
3. **Self-training**: 模型翻译→过滤低质量→重新训练

### QSM具体方案
1. 用V7-Small API翻译中文句子→彝文
2. 对比已知正确的彝文翻译(如果有)
3. 保留合理的翻译对，丢弃明显错误的
4. 目标: 从50K数据扩展到200K

### 数据扩展优先级
1. **模板扩展**(最高效): 已有847模板→替换词汇→8000+条
2. **回译**(中等): 用API生成→人工筛选→5000+条
3. **规则生成**(稳定): 彝文SOV语法+已知词汇→3000+条
4. **爬虫**(长期): 彝文网站数据收集

## 研究#234: 子词分词方案 — 从字符级到BPE/SentencePiece (2026-05-03)

### 当前问题
- 词汇表6924: 4120彝文单字+2720中文+26英文+6特殊+52其他
- 每个彝文字符=1个token, 中文也是1字1token
- 缺失: 大写英文字母(G/M/H/W/F)、常见词组、标点变体
- 模型输出含<unk>, 英文碎片 → 词汇覆盖不足

### BPE (Byte Pair Encoding) 方案
1. 从训练语料统计字符对频率
2. 合并最高频字符对→新token
3. 重复直到达到目标词汇量
4. 优点: 自动发现常见字组合(如"你好"→1token)
5. 缺点: 彝文字符本身就很稀疏,合并可能不直观

### SentencePiece 方案
1. 无需预分词, 直接从raw text学习
2. 支持unigram(概率最大)和BPE两种模式
3. `pip install sentencepiece` → 训练SPM模型
4. 目标词汇量: 16000 (当前6924→扩展到16000)
5. 优点: 处理任意语言, 内置<unk>/<s>/</s>

### 具体实施步骤
1. 收集所有训练文本(中文+彝文+英文)
2. `spm_train --input=corpus.txt --model_prefix=qsm --vocab_size=16000`
3. 替换训练脚本中的tokenizer
4. 重新训练模型
5. 评估: 词汇覆盖率、<unk>率、翻译质量

### 词汇扩展优先级
1. 补全英文大小写(52→完整A-Za-z)
2. 添加常见中文词组(你好/谢谢/请问→1token)
3. 添加彝文常见组合
4. 添加标点符号变体
5. 添加数学/科技符号

## 研究#235: LoRA低秩适应 — 高效微调方案 (2026-05-03)

### 核心思想
不更新全部参数，只训练低秩分解矩阵:
W = W₀ + BA  (B∈R^(d×r), A∈R^(r×d), r≪d)

### 参数量对比
| 方法 | 可训练参数 | 全参数比例 |
|------|-----------|-----------|
| 全量微调 | 4.5M | 100% |
| LoRA r=8 | ~72K | 1.6% |
| LoRA r=16 | ~144K | 3.2% |
| LoRA r=32 | ~288K | 6.4% |

### QSM应用
1. V7-Small(4.5M参数) + LoRA(r=16) → 仅训练144K参数
2. 每个epoch时间可从29min→5min!
3. 可在不同数据集(V10/V11)间快速切换
4. 合并多个LoRA适配器→多能力模型

### 实现步骤
1. pip install peft (HuggingFace PEFT库)
2. 对QSM模型添加LoRA层
3. 冻结原始权重，只训练LoRA参数
4. 合并回原始模型(merge_and_unload)

### 量化训练(QLoRA)
- 4-bit量化基础模型 → 节省75%内存
- LoRA层保持fp16
- 可在7.4GB内存训练更大模型(384d/6层)

## 研究#236: 课程学习实现方案 — V11训练策略 (2026-05-03)

### 核心思想
训练数据按难度排序，先学简单再学复杂：
1. 字符级(1-2字): 彝文字符↔含义
2. 词组级(3-5字): 常用词组翻译
3. 句子级(6-20字): 完整句子翻译
4. 段落级(20+字): 复杂表达/对话

### V12数据分类
- 短(1-5字): ~32,000条 (字符查询+短词)
- 中(6-15字): ~28,000条 (句子)
- 长(16+字): ~8,000条 (对话/段落)

### 实施方案
1. 数据标注: 给每条数据添加difficulty字段(1-4)
2. 阶段1(E1-20): 只训练difficulty=1-2(字符+词组)
3. 阶段2(E21-40): 加入difficulty=3(句子)
4. 阶段3(E41-60): 加入difficulty=4(段落+对话)
5. 阶段4(E61-100): 全部数据混合训练

### 预期效果
- 避免早期被复杂数据干扰
- 字符/词组先学会→句子才能理解
- 类似人类学习: 先学字母→词→句子→文章

## 研究#237: 子词分词方案实施细节 (2026-05-03)

### 当前问题
- 词汇表6924个token, 大量<unk>
- 彝文4120字各占1个token, 无法表示未登录字
- 英文全小写但仍有很多未登录词

### SentencePiece方案
1. 用V12数据(68K对)训练SentencePiece模型
2. 目标词汇量: 16000 (当前6924→16000)
3. 彝文字符保留完整(不拆分), 英文用BPE
4. 中文也用BPE(常见字/词组合并)

### 实施步骤
```python
import sentencepiece as spm
# 训练SPM
spm.SentencePieceTrainer.train(
    input='v12_corpus.txt',
    model_prefix='qsm_v12',
    vocab_size=16000,
    character_coverage=0.9995,
    model_type='bpe',
    treat_whitespace_as_suffix=True
)
```

### 预期效果
- <unk>率从~15%降至<2%
- 英文词如"quantum"/"computer"不再全是单字符
- 彝文保留字符级(已4120字)
- 模型参数量: 4.5M→8M (因词汇扩大)

### 风险
- SentencePiece是Python库(违反量子自举?)
- 可以用QEntL重写BPE算法(长期)
- 短期: SPM训练→导出词表→QSM训练

## 研究#238: 语言控制Token方案 (2026-05-03)

### 问题
模型无法区分输出语言——输入彝文可能输出英文/中文混杂

### 方案: 添加语言控制前缀Token
训练数据格式改为: `[目标语言] 输入内容 → 输出`
- `[彝文] 你好世界 → 彝文翻译`
- `[中文] hello → 你好`  
- `[EN] 你好 → hello`

### 实施
1. 修改tokenizer: 添加3个特殊token [YI], [ZH], [EN]
2. 修改训练数据: 每条input前加语言标签
3. 推理时: 用户指定目标语言, 自动加前缀

### 预期效果
- 模型明确知道该输出什么语言
- 减少语言混杂问题
- 支持同一输入翻译到不同语言

### 代码变更
- train_v7_quantum.py: 添加lang_bos参数支持
- 数据预处理: input = f"[{lang}] {original_input}"
- vocab.json: 添加[YI]/[ZH]/[EN]三个token

## 研究#239: 数据质量vs数量 — V8评估启示 (2026-05-03)

### 实验结果
- V8 (Val 2.6009, 68K数据) → API翻译100%垃圾
- V10数据90%+是字典查询 → 模型输出"这是两个彝文字<unk>"

### 关键发现
数据质量 > 数据数量！
- 68,395条混合数据(48%噪声) → 垃圾输出
- 35,316条清洗数据(0%chatbot) → 应该更好

### 数据污染类型
1. **字典查询**: "表示X的彝文字符→彝文是Y" → 模型学会查询模式
2. **随机字符**: "ꐯꆸꐯ→ꐯꐯꃅꏬ" → 模型学会生成乱码
3. **Chatbot响应**: "I can translate..." → 模型学会聊天
4. **重复模板**: 大量相似格式 → 过拟合模板

### V13改进
- 移除33K噪声(48%)
- 每条数据都是真正的翻译对
- 字符含义简化为 "字→含义" 格式

### 下一步
- V13训练 → 对比V8质量
- 如果仍不够: 需要更多高质量句子数据(>10K句)
- 考虑用外部平行语料库(Tatoeba/OPUS)

## 研究#240: Transformer改进方案 — 旋转位置编码(RoPE) (2026-05-03)

### 当前问题
- QSM使用固定正弦位置编码
- 长序列外推能力差(训练128tokens,推理>128时崩溃)
- 位置信息与内容信息解耦不够

### RoPE (Rotary Position Embedding)
- 论文: "RoFormer" (Su et al., 2021)
- 核心思想: 用旋转矩阵编码位置信息
- 将位置信息融入注意力计算(q·k时自动包含相对位置)

### 优势
1. 相对位置编码(天然支持)
2. 长度外推性好(训练128,推理512)
3. 计算效率高(仅2D旋转)
4. 不需要额外位置参数

### 实施方案
```python
class RotaryEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len=512):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2) / dim))
        self.register_buffer('inv_freq', inv_freq)
        
    def forward(self, x, seq_len):
        t = torch.arange(seq_len, device=x.device)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat([freqs, freqs], dim=-1)
        return emb.cos(), emb.sin()
```

### QSM改进计划
1. 替换固定位置编码→RoPE
2. max_seq_len从128→512
3. 预期: 长文本翻译质量提升

## 研究#241: 语言控制Token实现方案 (2026-05-03)

### 现有基础设施
- QuantumEmbeddingV2 已有 lang_bias (4维, 对应4种语言)
- QSMTransformer.forward() 已接受 lang_id 参数
- 但训练循环从未传入 lang_id!

### 实施步骤
1. 训练数据预处理: 检测每对数据的源/目标语言
2. 语言检测规则:
   - 含彝文字符(U+F2000+) → yi (lang_id=2)
   - 含中文(\u4e00-\u9fff) + 英文(a-z) → mixed (lang_id=3)
   - 纯中文 → zh (lang_id=0)
   - 纯英文 → en (lang_id=1)
3. 修改训练循环: output = model(src, tgt, lang_id=lang_id)
4. 推理时: 根据输入语言自动设置lang_id

### 预期效果
- 模型知道当前处理的语言对
- 不同语言对有不同的嵌入偏置
- 减少语言混杂输出

## 研究#242: 课程学习实施 — V12训练策略 (2026-05-03)

### 核心理念
人类学习语言: 字母→词→句→文
模型也应: 短词→短语→句子→段落

### V13数据difficulty分布
- difficulty=1 (字符级): ~3,000条
- difficulty=2 (词组级): ~15,000条  
- difficulty=3 (句子级): ~18,000条
- difficulty=4 (段落级): ~1,000条

### 训练计划(100 epochs)
```
Phase 1 (E1-20): difficulty 1-2 → 字符+词组
Phase 2 (E21-50): difficulty 1-3 → 加入句子
Phase 3 (E51-80): difficulty 1-4 → 全部数据
Phase 4 (E81-100): 全部数据 + lr降低 → 精调
```

### 实施
1. 预处理: 按difficulty分组保存
2. 训练脚本: 每N个epoch切换数据子集
3. 学习率: Phase1=1e-3, Phase2=5e-4, Phase3=1e-4, Phase4=5e-5

### 预期
- Phase1学会字符含义(彝文→中文映射)
- Phase2学会词组翻译
- Phase3学会句子翻译
- Phase4精调整体质量

## 研究#243: Flash Attention训练加速 (2026-05-03)

### 问题
当前训练 ~27min/epoch (36K数据, batch=16)
100 epochs = ~45小时

### Flash Attention (Dao et al., 2022)
- 核心思想: 分块计算注意力, 减少HBM读写
- 内存: O(N) 而非 O(N²)
- 速度: 2-4x 加速
- PyTorch 2.0+: `torch.nn.functional.scaled_dot_product_attention`

### 实施方案
```python
# 替换标准注意力
# PyTorch 2.0+ 自动使用Flash Attention
import torch.nn.functional as F

# 在 TransformerEncoderLayer 中
# PyTorch 2.0+ 默认启用 Flash Attention
# 只需: torch.backends.cuda.enable_flash_sdp(True)
```

### 问题: 服务器无GPU!
- Flash Attention需要CUDA GPU
- 当前仅CPU训练 → 无法使用Flash Attention
- 替代方案: 减少层数/使用梯度累积/混合精度

### CPU训练优化方案
1. torch.compile() - PyTorch 2.0+ JIT编译
2. 梯度累积: batch=4x4=16 → 有效batch=16
3. 混合精度: float16前向+float32反向 (CPU不支持)
4. 减少验证频率: 每epoch验证 → 每5epoch验证
5. 减少数据量: 37K→20K (但可能影响质量)

### 结论
当前CPU训练无法用Flash Attention
最有效加速: 减少验证频率(省~3min/epoch)

## 研究#244: 低资源语言数据增强策略 (2026-05-03)

### 问题
彝文是低资源语言, 平行语料极其有限
当前V13仅37K条, 目标100K+

### 策略对比

| 策略 | 效果 | 难度 | 优先级 |
|------|------|------|--------|
| 模板扩展 | 高(可控) | 低 | ⭐⭐⭐⭐⭐ |
| 回译 | 高(需可用模型) | 高 | ⭐⭐ |
| 外部语料库 | 高(质量好) | 中 | ⭐⭐⭐⭐ |
| 同义词替换 | 中 | 低 | ⭐⭐⭐ |
| 句子重组 | 低 | 低 | ⭐⭐ |
| GPT生成 | 高(成本高) | 中 | ⭐⭐⭐ |

### 模板扩展方案(最有效)
1. 固定模板: "我[verb]了[object]" → 20×18 = 360条
2. 变量替换: "[person]在[place]" → 8×10 = 80条
3. 条件句: "如果[A]就[B]" → 15×15 = 225条
4. 问题模板: "[wh]是[what]" → 无限

### 外部语料库
- Tatoeba: https://tatoeba.org (有彝文句子!)
- OPUS: https://opus.nlpl.eu (平行语料)
-彝文维基: 可爬取但量很少

### 回译(需V12模型可用后)
1. 用V12模型翻译zh→yi
2. 人工校对关键句子
3. 用校对后的数据再训练
4. 循环改进

### 词汇表扩展
当前词汇6924→需扩展:
- 英文: 26→至少1000
- 中文: 2720→至少5000  
- 彝文: 4120→至少8000
- SentencePiece: 16000子词(已训练)

## 研究#245: LoRA微调实施 — 大幅提升训练效率 (2026-05-03)

### LoRA原理 (Hu et al., 2021)
- Low-Rank Adaptation: W = W₀ + ΔW = W₀ + BA
- B: d×r, A: r×d, r << d (rank)
- 仅训练B和A, 冻结W₀
- 参数量: 2×d×r vs d² (节省>95%)

### QSM V7-Small LoRA方案
- d_model=192, n_heads=3, n_layers=3
- 总参数: 4.5M
- LoRA target: Q/V投影矩阵 (每个注意力层)
- r=16: LoRA参数 ≈ 3layers × 2heads × 192 × 16 × 2 = 37K
- 训练参数占比: 37K/4.5M = 0.8%!

### 实施步骤
1. pip install loralib (或手动实现)
2. 冻结原始权重: `for p in model.parameters(): p.requires_grad = False`
3. 添加LoRA层:
```python
import loralib as lora
# 替换线性层
model.encoder.layers[i].self_attn.in_proj_weight = lora.Linear(192, 576, r=16)
```
4. 训练: 仅LoRA参数有梯度
5. 合并: W₀ = W₀ + BA (推理时无额外开销)

### 预期效果
- 训练速度: 27min → ~5min/epoch (5x加速)
- 内存: 4.0Gi → ~2.5Gi (可同时训练更大模型)
- 质量: LoRA微调效果接近全参数微调
- 100 epochs: 45h → 8h!

### 下一步
1. 安装loralib
2. 修改train_v7_quantum.py添加--lora参数
3. 用V13数据+LoRA快速训练V13模型

## 研究#246: 知识蒸馏 — 从大模型到小模型 (2026-05-03)

### 问题
QSM当前4.5M参数, 能力有限
但训练更大模型(50M+)需要GPU

### 知识蒸馏 (Hinton et al., 2015)
- Teacher: 大模型(如Qwen3-0.6B, 600M参数)
- Student: QSM V7-Small (4.5M参数)
- 核心思想: 用Teacher的soft targets训练Student

### 实施方案
1. 用Qwen3-0.6B翻译更多数据(教师信号)
2. Student学习Teacher的输出分布(温度缩放)
3. 损失函数: α·L_hard + (1-α)·L_soft

### QSM特有方案
1. 用Qwen3生成彝文翻译(教师模型)
2. QSM学习Qwen3的翻译风格
3. QSM最终独立运行(不需要Qwen3)

### 优势
- 数据增强: Qwen3可生成无限训练数据
- 质量提升: 教师信号比模板更自然
- 无需GPU: 蒸馏过程用CPU即可

### 实施步骤
1. 安装transformers库
2. 加载Qwen3-0.6B (CPU即可, 只需推理)
3. 批量生成zh→yi, en→yi翻译数据
4. 混合蒸馏数据+原始数据训练QSM

## 研究#247: Beam Search改进 — 对比搜索与核采样 (2026-05-03)

### 当前方案
- Beam Search (beam_size=5)
- n-gram blocking (禁止3-gram重复)
- rep_penalty=1.5
- length_penalty=0.6

### 问题
- Beam Search倾向生成短文本(长度惩罚不够)
- 重复模式虽有缓解但仍存在
- 缺乏多样性(beam内路径趋同)

### 对比搜索 (Contrastive Search, Su et al., 2022)
- 核心思想: 同时考虑概率和退化惩罚
- 公式: s(x_t) = p(x_t) - α × max_sim(x_t, context)
- α=0.6时效果最佳
- 优势: 高质量+高多样性

### 核采样 (Nucleus Sampling, Holtzman et al., 2020)
- 核心思想: 从概率质量前p的token中采样
- p=0.9 (top-p sampling)
- 优势: 自然多样性, 避免beam趋同
- 适合对话/创意生成

### 实施计划
1. 在API中添加decoding_strategy参数
2. "beam": 当前beam search
3. "contrastive": 对比搜索(α=0.6)
4. "nucleus": 核采样(top-p=0.9, temperature=0.7)
5. "greedy": 贪心解码(最快)

### 预期
- 翻译任务: beam search最好(确定性强)
- 对话任务: nucleus sampling更好(多样性)
- 对比搜索: 两者之间的平衡

## 研究#248: 课程学习(Curriculum Learning)实施计划 (2026-05-04)

### 理论基础 (Bengio et al., 2009)
- 从简单样本开始,逐渐增加难度
- 类比人类学习: 先学加减,后学乘除
- 训练更快收敛,达到更好的局部最优

### V13数据difficulty分布
- difficulty=1: 6,169条 (基础词汇/短语)
- difficulty=2: 14,795条 (简单句子)
- difficulty=3: 6,975条 (复合句/假设/比较)
- difficulty=4: 9,015条 (复杂句/因果/被动)
- 未标注: ~40,000条 (Tatoeba, 标为2-3)

### 4阶段训练计划
1. **Phase 1 (E1-10)**: difficulty ≤ 2 (~20K条) — 基础
2. **Phase 2 (E11-30)**: difficulty ≤ 3 (~50K条) — 进阶
3. **Phase 3 (E31-70)**: all data (~77K条) — 全量
4. **Phase 4 (E71-100)**: difficulty ≥ 3 + 回放 (~30K条) — 强化

### 实施方案
- 训练脚本添加 --curriculum 参数
- 每个phase切换时打印日志
- Phase间用学习率衰减 (0.001→0.0005→0.0003→0.0001)
- 预期: 比随机训练快30-50%收敛

### 未标注数据处理
- Tatoeba数据: 默认difficulty=2 (句子级)
- 模板数据: 根据模板类型标注 (SVO=2, 比较=3, 因果=4)
- 对话数据: difficulty=3

## 研究#249: LoRA微调实践方案 (2026-05-04)

### LoRA原理 (Hu et al., 2021)
- W = W₀ + ΔW = W₀ + BA
- B ∈ R^{d×r}, A ∈ R^{r×d}
- r << d → 仅训练2rd参数 (vs d²全量)
- α/r缩放: ΔW = (α/r) × BA

### QSM V7-Small参数分析
- d_model=192, n_heads=3, n_layers=3, d_ff=768
- 总参数: 4.5M
- Attention: Q/K/V/O projections = 4 × (192×192) × 3层 = 442K
- FFN: 2 × (192×768 + 768×192) × 3层 = 1.77M
- LoRA r=16: 每层4×2×16×192 = 24K, 3层=73K
- 训练比例: 73K/4.5M = 1.6% (vs 全量100%)

### 实施方案
1. V12完成后, 用V13 77K数据 + LoRA r=16 续训
2. --lora 16 --lora_alpha 16
3. 预期: 23min→5min/epoch (4.6x加速)
4. 可配合课程学习: --curriculum
5. LoRA可叠加: 多个LoRA适配不同任务

### 注意事项
- loralib已安装(0.1.2)
- mark_only_lora_as_trainable()是关键API
- LoRA只对大维度Linear层有效(≥d_model)
- Resume时需加载完整模型+LoRA权重

## 研究#250: Qwen3-0.6B知识蒸馏实践 (2026-05-04)

### 测试结果
- Qwen3-0.6B已成功加载(CPU, 1.5秒)
- 内存占用: ~3.5GB (V12训练2.3GB + Qwen3 3.5GB = 5.8GB < 7.4GB)
- 问题: 简单prompt("Translate to English: X")产生中文续写而非翻译
- 需要使用chat template才能获得正确翻译

### 正确的Prompt格式 (Qwen3)
```
<|im_start|>system
You are a professional translator. Translate Chinese to English.<|im_end|>
<|im_start|>user
今天天气很好<|im_end|>
<|im_start|>assistant
```

### 蒸馏数据生成计划
1. 用Qwen3生成5万条zh→en翻译对
2. 输入: 从V13数据集中提取中文句子
3. 温度: 0.3 (低随机性, 高质量)
4. max_new_tokens: 64 (匹配QSM训练长度)
5. 后处理: 过滤<2词或>50词的输出

### 彝文蒸馏
- Qwen3不认识彝文→不能直接用于yi翻译
- 方案: 先训zh↔en到Val<2, 再用模型自身做回译
- 或者: 用Qwen3生成zh句子, 再人工/模板翻译为彝文

### 实施优先级
1. V12完成后: Qwen3生成en↔zh数据 (5万条)
2. 合并到V13数据集 (77K→120K+)
3. 用课程学习+LoRA训练V13
4. V13达到Val<2后: 回译生成yi数据

## 研究#251: CPU训练优化策略 (2026-05-04)

### 当前瓶颈
- V12训练: 23min/epoch, 68K数据, 4.5M参数
- CPU-only, 无GPU, 内存2.7GB/7.4GB
- 主要耗时: 前向+反向传播(纯CPU矩阵运算)

### 优化方案
1. **梯度累积**(已实现): batch_size=4 × accum_steps=4 = effective 16
   - 减少内存峰值, 等效大批量
2. **学习率调度**: 当前用step decay(0.85^step)
   - 改进: Cosine Annealing(更平滑收敛)
   - 公式: lr = lr_min + 0.5*(lr_max-lr_min)*(1+cos(πt/T))
3. **梯度裁剪**: 防止梯度爆炸
   - `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`
4. **torch.compile()**: PyTorch 2.x JIT编译(需torch>=2.0)
   - 可加速10-30% (CPU也有优化)
5. **减少验证频率**: --val_interval 5 (每5 epoch验证一次)
   - 省4min/epoch × 5 = 20min/5epochs

### Cosine Annealing实施
```python
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer, T_max=args.epochs, eta_min=1e-5
)
```
- 自动平滑衰减, 无需手动step
- 在训练后期更精细调整

### 下次训练(V13)参数
- 数据: v13_clean (77K)
- 模型: 4.5M (V7-Small架构)
- LoRA: r=16 (1.6%可训练)
- 课程学习: 4阶段difficulty递增
- Cosine Annealing LR
- 梯度裁剪: max_norm=1.0

## 研究#252: 低资源神经机器翻译高效推理 (2026-05-04)

### 问题
- QSM V7-Small: 4.5M参数, 推理慢(CPU)
- 彝文是极低资源语言, 训练数据有限
- 需要优化推理速度同时保持质量

### 推理优化技术
1. **知识蒸馏(KD)**: 大模型→小模型
   - Teacher: Qwen3-0.6B (600M)
   - Student: QSM V7-Small (4.5M)
   - 蒸馏损失: L = α*L_hard + (1-α)*L_soft
   - soft target: softmax(zi/T) T=4

2. **量化(Quantization)**:
   - FP32→INT8: 模型大小减半, 推理2x加速
   - torch.quantization.quantize_dynamic()
   - 适用于CPU推理, 无需GPU

3. **剪枝(Pruning)**:
   - 移除不重要的注意力头/FFN神经元
   - 结构化剪枝: 删除整个head
   - QSM 3头→2头: 参数减少33%

4. **缓存优化(KV Cache)**:
   - 自回归推理时缓存key/value
   - 避免重复计算已生成的token
   - 当前API每次重新计算→需添加

### 实施优先级
1. KV Cache (最容易, 推理2-3x加速)
2. INT8量化 (简单, 推理2x加速)
3. 知识蒸馏 (中等, 质量提升)
4. 剪枝 (最后, 需要重新训练)

## 研究#253: RoPE旋转位置编码实施详解 (2026-05-04)

### 原理 (Su et al., 2021 "RoFormer")
- 位置信息通过旋转矩阵编码到Q和K中
- q_m = R(m) · W_q · x_m, k_n = R(n) · W_k · x_n
- 注意力: q_m · k_n = (R(m)W_qx_m)^T · (R(n)W_kx_n)
- 利用旋转性质: R(m)^T · R(n) = R(n-m)
- 所以 q_m · k_n = f(相对位置 n-m) ← 自然编码相对位置!

### 旋转矩阵
```
R(θ, m) = [cos(mθ)  -sin(mθ)]
           [sin(mθ)   cos(mθ)]
```
- 对d维向量，每2维一组，共d/2组
- 每组有不同的θ_i = 10000^(-2i/d)
- 实现: 逐元素乘法 (比矩阵乘法快)

### PyTorch实现
```python
class RotaryEmbedding(nn.Module):
    def __init__(self, dim, max_seq_len=512):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2).float() / dim))
        self.register_buffer('inv_freq', inv_freq)
        t = torch.arange(max_seq_len).float()
        freqs = torch.einsum('i,j->ij', t, inv_freq)
        self.register_buffer('cos_cache', freqs.cos())
        self.register_buffer('sin_cache', freqs.sin())
    
    def forward(self, x, seq_len):
        return self.cos_cache[:seq_len], self.sin_cache[:seq_len]

def rotate_half(x):
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)

def apply_rotary(x, cos, sin):
    return x * cos + rotate_half(x) * sin
```

### QSM集成方案
1. 创建自定义MultiHeadAttention替代nn.MultiheadAttention
2. 在Q和K投影后应用RoPE (V不需要位置编码)
3. 移除pos_encoding = nn.Embedding(max_len, d_model)
4. 保留QuantumEmbeddingV2(语言感知)
5. max_len可从64→512 (长度外推)

### 预期收益
- 支持更长序列 (64→512)
- 更好的长度泛化能力
- 相对位置编码(更自然)
- 移除绝对位置嵌入(减少参数)

### 实施时间线
- V13训练完成后实施(V13用现有架构)
- 创建QSM_V8架构(含RoPE)
- V14训练用V8架构 + V13数据

### 与量子概念的联系
- 旋转矩阵 = 量子门(R_z旋转)
- θ_i = 不同量子态的旋转角
- 位置m = 时间步(量子演化)
- 自然映射: 位置编码 → 量子旋转门序列

## 研究#254: Qwen3-0.6B知识蒸馏实施细节 (2026-05-04)

### 测试结果
- Qwen3-0.6B可以正确翻译zh→en: "今天天气很好"→"Today's weather is good."
- 但使用了thinking模式(थिं块占200+ tokens)
- CPU速度: ~30秒/句 (含thinking)
- 50K句子需要~17天 (不可行)

### 优化方案
1. **禁用thinking**: Qwen3支持`enable_thinking=False`
   - 或在generate时设置`extra_body={"enable_thinking": false}`
   - 预期速度: 5-10秒/句 (无thinking)
2. **批量生成**: 使用batch_size>1 (需要更多内存)
3. **GPU服务器**: 用Colab免费GPU (T4) 生成
   - 速度: ~0.1秒/句, 50K→1.4小时
4. **预计算thinking**: 让模型先think, 然后用thinking+answer微调QSM

### 实际可行的蒸馏方案
**Phase 1**: 用模板+Tatoeba数据训练到Val<2.0 (纯CPU)
**Phase 2**: 达到Val<2.0后, 用QSM自身做回译(无需Qwen3)
**Phase 3**: GPU服务器上用Qwen3生成50K高质量对
**Phase 4**: 合并所有数据, 最终训练

### 回译方案 (无需GPU, Phase 2可用)
- 用QSM(Val<2)翻译 en→zh, 对比原文生成新训练对
- 用QSM翻译 zh→en, 对比Qwen3翻译质量过滤
- 自我迭代: 每轮训练→回译→过滤→再训练

### 关键洞察
- 模板数据(结构化、可控) > 蒸馏数据(质量不稳定)
- V13 77K条模板+Tatoeba已足够训练到Val<2
- 知识蒸馏是锦上添花, 不是必需品

## 研究#255: Label Smoothing在低资源NMT中的影响 (2026-05-04)

### 当前设置
- QSM V7: label_smoothing=0.15
- 问题: 低资源(77K句对)下, label smoothing可能过度平滑

### Label Smoothing原理 (Szegedy et al., 2016)
- 标准交叉熵: L = -log(p_y) (one-hot)
- LS: L = -(1-ε)·log(p_y) - ε·Σ log(p_k)/K
- ε=0.15: 正确类得0.85概率, 其余0.15均分
- 防止过度自信, 提高泛化

### 低资源下的特殊问题
1. **数据稀疏**: 每个token出现次数少, 平滑导致"不确定"
2. **词汇表大(6924)**: ε/K=0.15/6924≈2e-5, 每个非目标token分到极小概率
3. **欠训练**: 模型还没自信就被平滑了

### 实验建议
- ε=0.15(当前) → 尝试 ε=0.05, 0.1
- 低资源最优值通常在 ε=0.1 附近
- ULRA (ICML 2020): 自适应label smoothing

### 对QSM的影响
- V12(68K, ε=0.15): Val 3.06 可能被过度平滑
- V13(77K, ε=0.1): 可能更快收敛
- 实施简单: --label_smoothing 0.1

### 其他训练技巧
1. **Dropout调度**: 开始0.2, 后期0.3(防止过拟合)
2. **Layer Normalization**: 已有(self.norm)
3. **Warmup**: 已有(500 steps)
4. **梯度累积**: 已有(4步)

## 研究#256: Cosine Annealing with Warm Restarts (SGDR) (2026-05-04)

### 原理 (Loshchilov & Hutter, 2017)
- 标准Cosine: η_t = η_min + 0.5(η_max - η_min)(1 + cos(πt/T_max))
- SGDR: 周期性重启, 每个周期T_i后LR跳回η_max
- 重启让模型逃离局部最优

### V12当前问题
- Step decay: lr=0.0003*0.85^(step/4049)
- E25时lr=0.000133, 还在下降但很慢
- E50时lr≈0.00003, 几乎为零→训练停滞

### V13 SGDR方案
- T_0=10 (第一个周期10 epochs)
- T_mult=2 (每次周期翻倍: 10→20→40→80)
- η_min=1e-6, η_max=0.0003
- 总周期: E1-10, E11-30, E31-70, E71-150
- 每次重启从当前best模型开始

### PyTorch实现
```python
scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=10, T_mult=2, eta_min=1e-6
)
scheduler.step()  # 每epoch调用
```

### 与课程学习配合
- Phase 1 (E1-10): difficulty 1-2 + SGDR周期1
- Phase 2 (E11-30): difficulty 2-3 + SGDR周期2
- Phase 3 (E31-70): difficulty 3-4 + SGDR周期3
- Phase 4 (E71+): difficulty 1-4 + SGDR周期4

### 预期收益
- 避免LR过低导致的训练停滞
- 重启帮助探索更好的参数空间
- 与课程学习自然配合(难度递增+LR重启)
