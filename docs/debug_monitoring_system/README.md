# QEntL调试监控系统 Debug Monitoring System

## 🎯 快速开始

### 启动监控界面
```bash
# 进入项目根目录
cd F:\QSM

# 启动HTML监控界面
start quantum_monitor.html
```

### 监控界面功能
- **📁 文件状态监控**：实时查看所有QEntL文件的运行状态
- **🧠 训练状态监控**：监控四大量子模型训练进度
- **💬 对话测试**：测试量子模型响应（Enter发送，Shift+Enter换行）
- **📊 系统日志**：查看详细系统运行日志

## 📚 文档结构

```
docs/debug_monitoring_system/
├── README.md                           # 本文件 - 快速开始指南
├── QENTL_DEBUG_MONITORING_GUIDE.md     # 完整调试监控指南
├── mpc_interface_spec.md               # MPC接口技术规范
├── component_status_tracker.md         # 组件状态追踪器
└── scripts/                            # 监控脚本
    ├── auto_health_check.ps1           # 自动健康检查
    ├── start_monitoring.ps1            # 启动监控系统
    └── repair_unused_files.ps1         # 修复未使用文件
```

## 🔍 核心监控内容

### QEntL系统组件状态
- ✅ 量子叠加态神经网络引擎
- ✅ 量子模型融合引擎  
- 🔄 QEntL编译器
- 🔄 量子虚拟机
- 🔄 运行时环境

### 四大量子模型状态
- **QSM量子叠加态模型**：五阴破除训练
- **SOM自组织映射模型**：神经元网格优化
- **WeQ量子通讯模型**：量子纠缠信道建立
- **Ref自反省模型**：自我超越训练

### 量子数据文件状态
- ✅ 24h_continuous_learning.qentl
- ✅ quantum_gene_data.qentl
- ✅ neural_pattern_data.qentl
- ❌ unused_test_file.qentl（需要修复）

## 🛠️ 问题修复指南

### 未被调用文件修复
当发现 `🔴 unused_test_file.qentl [测试文件] 未使用 ❌未被调用` 时：

1. **分析文件用途**
2. **查找调用点**
3. **集成到工具链**
4. **验证修复结果**

详细修复步骤请参考：[QENTL_DEBUG_MONITORING_GUIDE.md](./QENTL_DEBUG_MONITORING_GUIDE.md)

## 🔗 Claude MPC接口

为Claude提供实时监控能力：
- **状态查询**：`GET /api/qentl/status`
- **文件监控**：`GET /api/qentl/files`
- **训练控制**：`POST /api/qentl/training/{action}`
- **系统修复**：`POST /api/qentl/repair`

## 📞 技术支持

- **主文档**：[QENTL_DEBUG_MONITORING_GUIDE.md](./QENTL_DEBUG_MONITORING_GUIDE.md)
- **MPC接口**：[mpc_interface_spec.md](./mpc_interface_spec.md)  
- **组件追踪**：[component_status_tracker.md](./component_status_tracker.md)

---

**通过这个监控系统，我们可以一目了然地看到哪些文件真正在使用，哪些需要修复！** 🌟 