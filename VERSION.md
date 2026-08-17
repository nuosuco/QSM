# QLife v0.0.3 - 当前生长版本

## 状态
- 🟢 活跃开发中
- 🟢 QSCL叠加态并行训练已实现
- 🟢 QNS框架已恢复
- 🟢 QVM已添加QSCL builtin

## 核心功能
1. **QSCL训练**: 4态×1030字×5轮，叠加态并行不同起步
2. **QNS框架**: 神经叠加态网络，支持自举生长
3. **彝文识别**: 4120通用彝文字，权重内化
4. **Web桌面**: qdesktop.html (9802端口)

## 目录结构
```
QLife/v0.0.3/
├── components/     # QNS、QDFS、四大模型
├── lib/           # 核心库 (qns_framework.qentl)
├── build/         # 编译产物
├── qdfs/          # 量子文件系统
├── web/           # Web桌面
└── docs/          # 本地文档
```

## QSCL实现
- embedding: 码点→向量
- mat_mul: 矩阵运算
- softmax: 概率分布
- argmax: 取最大值
- backprop: 反向传播

## 下一步
- [ ] 完成QSCL训练验证
- [ ] 合成服务器API
- [ ] 归档到QSM
