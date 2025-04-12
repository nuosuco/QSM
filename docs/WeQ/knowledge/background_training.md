# background_training

## 模块说明
WeQ(小趣)后台持续训练系统
实现Claude知识教学和爬虫数据训练的后台自动化
支持24小时不间断运行

## 功能概述

### 类

- `SimpleQuantumNetwork`
- `BackgroundTrainer`

### 函数

- `__init__`
- `quantum_simulate`
- `forward`
- `predict`
- `train`
- `generate_knowledge_for_topic`
- `evolve_topics`
- `__init__`
- `load_model`
- `save_model`
- `select_next_topics`
- `generate_training_data`
- `qsm_training_cycle`
- `claude_training_cycle`
- `crawler_training_cycle`
- `simulate_crawler_data_collection`
- `process_crawler_data`
- `text_to_vector`
- `start_background_training`
- `_monitor_training_threads`
- `_log_backup_loop`
- `_clean_old_logs`
- `_claude_training_loop`
- `_crawler_training_loop`
- `_qsm_training_loop`
- `stop_background_training`
- `get_training_status`
- `main`
- `_check_already_running`
- `_watchdog_function`
- `run_as_service`

## 依赖关系

## 使用示例

## 注意事项

*文档最后更新时间：2025-04-12 14:51:58*