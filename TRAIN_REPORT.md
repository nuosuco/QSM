# QEntL全栈训练报告 — 21电路 × 3 Epoch

## 总览
| 指标 | 值 |
|------|-----|
| Epochs | 3 |
| 电路数 | 21 |
| QVM执行次数 | 63 |
| 总周期 | 2,835 |
| 总门操作 | 2,835 |
| 失败 | 0 |

## 按模型分类 (3 epoch累计)
| 模型 | 周期 | 门数 | 电路数 | 失败 |
|------|------|------|--------|------|
| QNS | 309 | 309 | 2 | 0 |
| QDFS | 558 | 558 | 4 | 0 |
| QSM | 609 | 609 | 5 | 0 |
| Ref | 540 | 540 | 4 | 0 |
| SOM | 198 | 198 | 2 | 0 |
| WeQ | 357 | 357 | 3 | 0 |
| Other | 264 | 264 | 1 | 0 |

## 每电路详情 (单epoch × 3)
| 电路 | 周期 | 门数 |
|------|------|------|
| qns_training_circuit.qbc | 114 | 114 |
| qns_backprop_circuit.qbc | 195 | 195 |
| qdfs_quantum_circuit.qbc | 123 | 123 |
| grover_search_circuit.qbc | 153 | 153 |
| qsm_consciousness_circuit.qbc | 102 | 102 |
| qsm_entanglement_circuit.qbc | 99 | 99 |
| qsm_entry.qbc | 42 | 42 |
| qsm_yi_training_circuit.qbc | 165 | 165 |
| yi_training_pipeline_circuit.qbc | 201 | 201 |
| ref_entry.qbc | 90 | 90 |
| ref_healing_circuit.qbc | 165 | 165 |
| ref_monitoring_circuit.qbc | 144 | 144 |
| ref_optimization_circuit.qbc | 141 | 141 |
| som_entry.qbc | 66 | 66 |
| som_transaction_circuit.qbc | 132 | 132 |
| weq_entry.qbc | 66 | 66 |
| weq_learning_circuit.qbc | 102 | 102 |
| weq_social_interaction_circuit.qbc | 189 | 189 |
| Models_QNS_Integration_Test.qbc | 264 | 264 |
| qns_qdfs_dataflow.qbc | 114 | 114 |
| qns_qdfs_reverse_flow_circuit.qbc | 168 | 168 |

训练脚本: train_full.sh
