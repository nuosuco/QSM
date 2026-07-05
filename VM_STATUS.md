# VM 模块状态报告

**生成时间：** 2026-07-06
**项目路径：** /root/QSM
**检查范围：** QEntL/System/VM/ + src/

---

## 1. QEntL 源文件清单（30 个 .qentl）

### bin/cli/（5 个）
- debug_cli.qentl
- quantum_visualizer.qentl
- vm_cli.qentl
- vm_launcher.qentl
- vm_main.qentl

### 根目录（1 个）
- qvm_extensions.qentl

### src/core/debug/（5 个）
- debug_config.qentl
- debugger.qentl
- debug_protocol.qentl
- debug_session.qentl
- debug_visualizer.qentl

### src/core/interpreter/（2 个）
- instruction_set.qentl
- interpreter.qentl

### src/core/memory/（1 个）
- memory_manager.qentl

### src/core/os_interface/（3 个）
- file_system.qentl
- network.qentl
- process.qentl

### src/core/quantum/（5 个）
- complex.qentl
- entanglement_engine.qentl
- entanglement_manager.qentl
- quantum_state_processor.qentl
- random.qentl

### src/deployment/（8 个）
- qpu_adapter_cloud.qentl
- qpu_adapter_hardware.qentl
- qpu_adapter_qvm.qentl
- qpu_bytecode_converter.qentl
- qpu_deployment_config.qentl
- qpu_deployment_router.qentl
- qpu_deployment_types.qentl
- qpu_runtime_detector.qentl

---

## 2. C 源码清单（3 个）
- src/qvm_bootstrap.c
- src/qcl_bootstrap.c
- src/qcl_phase2.c

---

## 3. .qentl 编译状态

| 结果 | 数量 | 说明 |
|------|------|------|
| ✅ 已编译且最新 | 30 | 所有 .qentl 对应 .qbc 均存在，且源文件未更新 |
| ⚠️ 需要重新编译 | 0 | — |
| ❌ 缺少 .qbc | 0 | — |

**结论：无需重新编译。** 全部 30 个 .qentl 对应的 .qbc 字节码文件均为最新。

---

## 4. C 源码编译状态

| 源文件 | 目标二进制 | 状态 |
|--------|-----------|------|
| src/qvm_bootstrap.c | bin/qvm_bootstrap | ✅ 二进制最新 |
| src/qcl_bootstrap.c | bin/qcl_bootstrap | ✅ 二进制最新 |
| src/qcl_phase2.c | bin/qcl_phase2 | ✅ 二进制最新 |

**结论：三个核心 C 源文件均无需重新编译，二进制与源文件时间戳一致。**

---

## 5. 文件统计

| 类别 | 数量 |
|------|------|
| QEntL 源文件 (.qentl) | 30 |
| QBC 字节码文件 (.qbc) | 30 |
| C 源文件 (.c) | 3 |
| 编译好的二进制 | 4 |
| 文档 (Markdown) | 1 |
| **合计** | **68** |

---

## 6. 总体结论

✅ **VM 模块状态：健康（All Clear）**

- QEntL/System/VM/ 下全部 30 个 .qentl 文件均已编译，对应 30 个 .qbc 字节码文件全部最新
- src/ 下 3 个 C 核心源文件（qvm_bootstrap.c、qcl_bootstrap.c、qcl_phase2.c）均无需重编译
- 二进制 bin/ 下有 qvm_bootstrap、qcl_bootstrap、qcl_phase2、qentl_compiler 共 4 个可执行文件
- 未发现缺失、过期或损坏的编译产物
