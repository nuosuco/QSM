# QEntL 全栈量子计算平台 v0.1.0

> 纯QEntL实现，零第三方依赖，自举编译器，QOS平台稳定运行。
> 运行于 https://qsm.som.top (QOS平台)

## 📊 版本统计 (v0.1.0)

| 指标 | 数值 |
|------|------|
| 量子门 | 15种 |
| 算法示例 | 59个 |
| 标准库 | 8个 |
| API端点 | 33个 |
| 验证通过率 | 47/47通过 |
| QVM基准 | 3ms |
| 部署状态 | QOS平台在线 |

## 🚀 QOS平台

- **首页**: https://qsm.som.top
- **IDE**: https://qsm.som.top/ide
- **状态**: https://qsm.som.top/api/status

## 📚 核心架构

```
C种子 (qcl_bootstrap.c)
  ↓ 编译
QCL编译器 (qcl.qentl)
  ↓ 编译
QVM虚拟机 (qvm.qentl)
  ↓ 运行
标准库 (lib/*.qentl)
  ↓ 运行
HTTP服务器 (server_qentl.qentl)
  ↓ 服务
QOS平台 (qsm.som.top)
```

## 🔬 量子算法分类 (59个)

### 基础算法 (25个)
- 量子搜索: Grover (2-5量子位) + 优化版
- 量子变换: QFT (3/4/6量子位)
- 量子估计: PEA, T门相位估计
- 量子分解: Shor (N=15/21/35/77/143)
- 量子协议: 隐形传态、链式隐形传态、BB84、Deutsch-Jozsa
- 量子行走: K3/K4图

### 量子机器学习 (20个)
- QNN: 基础/高级/训练演示
- QSVM: 量子支持向量机
- Q聚类: 纠缠聚类
- Q优化: Grover量子优化
- Q核: 量子核函数
- QRBM: 量子玻尔兹曼机 (单层/深层)
- QML分类器/回归/变分
- QGAN: 量子生成对抗网络
- Q自编码器

### 量子演示 (14个)
- 叠加态、GHZ态、Bell态对
- 量子纠错、密集编码
- Deutsch算法、BV算法
- QSM主模型、QSM经济模型、WeQ社交模型、Ref自反省模型
- 量子稀疏向量

## 🛠️ 技术栈

- **量子门**: h/t/cx/x/z/cz/ccx/ccz/cccz/ccccz/phase/iphase/cphase/icphase/measure
- **编译器**: QCL (纯QEntL自举)
- **虚拟机**: QVM (纯QEntL，3ms基准)
- **文件系统**: QDFS (量子叠加态)
- **神经网络**: QNN/QNS (量子神经网络)
- **服务器**: 纯QEntL HTTP
- **部署**: QOS平台 (qsm.som.top)

## 📝 开发日志

- **v0.1.0**: QFT大规模/T门相位估计/链式隐形传态/量子GAN/量子自编码器/深层QRBM
- **v0.0.9**: QNS训练框架 + 四大模型演示 (QSM/SOM/WeQ/Ref)
- **v0.0.8**: QNN高级模块/Ansatz/分类器/回归分析
- **v0.0.7**: 量子基础算法(隐形传态/纠错/密集编码/Deutsch/BV)
- **v0.0.6**: 量子机器学习系列(QSVM/QNN/Q聚类/优化/RBM)
- **v0.0.5**: QNN/QSV/量子聚类/量子优化等算法
- **v0.0.4**: QDFS完成、Shor分解N=15/21/35/77/143

---

**QEntL — 量子计算，从种子到星空** 🌌