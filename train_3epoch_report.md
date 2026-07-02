# QEntL全栈训练循环报告
## 执行时间: 2026-07-03
## 工作目录: /root/QSM
## 训练工具: bin/qvm_bootstrap (QVM量子虚拟机)

---

## 一、训练概况

| 指标 | 数值 |
|------|------|
| 有效量子电路数 | **21个** (首字节0x14) |
| Epoch数 | **3** |
| 总运行次数 | **63次** (21×3) |
| 总周期数 | **2835** |
| 总门操作数 | **2835** |
| 失败数 | **0** (全部成功) |

---

## 二、Per-Circuit 详情 (每电路单epoch周期/门数，3 epoch均值一致)

### QSM模型 (5个电路)
| 电路 | 周期 | 门数 |
|------|------|------|
| qsm_consciousness_circuit | 34 | 34 |
| qsm_entanglement_circuit | 33 | 33 |
| qsm_entry | 14 | 14 |
| qsm_yi_training_circuit | 55 | 55 |
| yi_training_pipeline_circuit | 67 | 67 |

### Ref模型 (4个电路)
| 电路 | 周期 | 门数 |
|------|------|------|
| ref_entry | 30 | 30 |
| ref_healing_circuit | 55 | 55 |
| ref_monitoring_circuit | 48 | 48 |
| ref_optimization_circuit | 47 | 47 |

### SOM模型 (2个电路)
| 电路 | 周期 | 门数 |
|------|------|------|
| som_transaction_circuit | 44 | 44 |
| som_entry | 22 | 22 |

### WeQ模型 (3个电路)
| 电路 | 周期 | 门数 |
|------|------|------|
| weq_entry | 22 | 22 |
| weq_learning_circuit | 34 | 34 |
| weq_social_interaction_circuit | 63 | 63 |

### QNS (3个电路)
| 电路 | 周期 | 门数 |
|------|------|------|
| Models_QNS_Integration_Test | 88 | 88 |
| qns_backprop_circuit | 65 | 65 |
| qns_training_circuit | 38 | 38 |

### QDFS (4个电路)
| 电路 | 周期 | 门数 |
|------|------|------|
| grover_search_circuit | 51 | 51 |
| qdfs_quantum_circuit | 41 | 41 |
| qns_qdfs_dataflow | 38 | 38 |
| qns_qdfs_reverse_flow_circuit | 56 | 56 |

---

## 三、按模型分类统计 (3 epoch汇总)

| 模型 | 电路数 | 总周期 | 总门数 | 失败 |
|------|--------|--------|--------|------|
| **QSM** | 5 | 609 | 609 | 0 |
| **Ref** | 4 | 540 | 540 | 0 |
| **QNS** | 3 | 573 | 573 | 0 |
| **QDFS** | 4 | 558 | 558 | 0 |
| **WeQ** | 3 | 357 | 357 | 0 |
| **SOM** | 2 | 198 | 198 | 0 |

---

## 四、关键发现

1. **21/21电路全部通过** — 3 epoch共63次QVM执行，0失败，成功率100%
2. **QNS集成测试电路最重** — Models_QNS_Integration_Test达88周期/88门，是全栈验证的核心
3. **QSM意识训练链最重** — yi_training_pipeline_circuit(67)、qsm_yi_training_circuit(55)
4. **QDFS Grover搜索** — grover_search_circuit(51周期)体现量子搜索算法特征
5. 各epoch结果完全一致（确定性执行），符合QVM确定性格点

## 五、生成文件

- `/root/QSM/run_training_3epoch.py` — 训练脚本
- `/root/QSM/train_3epoch_report.md` — 本报告

---
*执行方式: 纯QVM量子虚拟机运行，未使用Python/PyTorch等经典训练框架*
