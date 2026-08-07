# QEntL 全栈量子计算平台 v0.0.8

> 纯QEntL实现，零第三方依赖，自举编译器，在线IDE，HTTP服务器全栈完成。
> 运行于 https://qsm.som.top (QOS平台)

## 📊 版本统计

| 指标 | v0.0.8 |
|------|--------|
| 量子门 | 15种 |
| 算法示例 | 40+个 |
| 标准库 | 7个 |
| API端点 | 30+个 |
| 验证通过率 | 35/35通过 |
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

## 🔬 量子算法分类

### 基础算法
- 量子搜索: Grover (2-5量子位)
- 量子变换: QFT (3/6量子位)
- 量子估计: PEA
- 量子分解: Shor (N=15/21/35/77/143)
- 量子协议: 隐形传态、BB84、Deutsch-Jozsa

### 量子机器学习
- 量子神经网络: QNN基础/高级
- 量子SVM: 二分类
- 量子聚类: 纠缠聚类
- 量子优化: Grover优化
- 量子RBM: 玻尔兹曼机
- 量子核函数: 核方法
- 量子分类器: 多分类
- 量子回归: 函数拟合
- 量子变分: Ansatz/VQE

### 量子演示
- 叠加态测量
- GHZ态
- Bell态对
- 量子行走K3
- 量子纠错
- 量子密集编码
- Deutsch算法
- BV算法

## 🛠️ 技术栈

- **量子门**: h/t/cx/x/z/cz/ccx/ccz/cccz/ccccz/phase/iphase/cphase/icphase/measure
- **编译器**: QCL (纯QEntL)
- **虚拟机**: QVM (纯QEntL)
- **文件系统**: QDFS (量子叠加态)
- **服务器**: 纯QEntL HTTP
- **部署**: QOS平台 (qsm.som.top)

## 📝 开发日志

- **v0.0.8**: 新增QNN高级模块/Ansatz/分类器/回归分析
- **v0.0.7**: 新增量子基础算法(隐形传态/纠错/密集编码/Deutsch/BV)
- **v0.0.6**: 新增量子机器学习算法(QSVM/密度矩阵/QNN分类器/VQA)
- **v0.0.5**: 新增QNN/QSV/量子聚类/量子优化等算法
- **v0.0.4**: QDFS完成、Shor分解N=15/21/35/77/143、18个API端点

---

**QEntL — 量子计算，从种子到星空** 🌌