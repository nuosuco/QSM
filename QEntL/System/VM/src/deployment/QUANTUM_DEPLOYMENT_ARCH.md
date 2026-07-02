# QEntL 量子3种部署支持架构规范

> 版本: 1.0.0 | 日期: 2026-07-03 | 量子基因编码: QGC-DEPLOY-ARCH-2026070301
> 量子纠缠信道: QEC-DEPLOY-01

---

## 一、架构概述

QEntL量子逻辑部分支持3种部署模式，对应量子字节码(`.qbc`)的三种执行方式：

```
┌──────────────────────────────────────────────────────────────────────┐
│                     QEntL量子3部署架构                                 │
│                                                                      │
│   QEntL源码(.qentl)                                                   │
│          │                                                           │
│          ▼                                                           │
│   QCL编译器 (qcl_bootstrap.c / QCL引导器)                            │
│          │                                                           │
│          ▼                                                           │
│   .qbc量子字节码 (统一格式)                                           │
│          │                                                           │
│    ┌─────┴─────┬──────────────────────────────┐                    │
│    ▼           ▼                              ▼                    │
│  开发部署    生产部署                       专用部署                  │
│  (QVM)      (Cloud QPU API)              (Hardware QPU)            │
│    │           │                              │                    │
│  QVM虚拟机   云端QPU服务                    QPU硬件协处理器           │
│  本地CPU     HTTP/gRPC                     直接硬件接口              │
│  模拟执行    API调用                         脉冲信号                 │
└──────────────────────────────────────────────────────────────────────┘
```

## 二、三种部署模式详细定义

### 2.1 开发部署 (Development) — QVM虚拟机模拟

| 属性 | 值 |
|------|-----|
| 部署类型ID | `DEPLOY_DEV = 0` |
| 环境标签 | `"qvm"` / `"development"` |
| 执行方式 | 本地CPU模拟量子运算 |
| 量子比特限制 | 受物理内存限制（当前≤26） |
| 适用场景 | 开发调试、单元测试、小规模验证 |
| 特点 | 确定性测量、完全可重现、调试友好 |
| 启动方式 | `bin/qvm_bootstrap file.qbc` |

### 2.2 生产部署 (Production) — 云端QPU API

| 属性 | 值 |
|------|-----|
| 部署类型ID | `DEPLOY_PROD = 1` |
| 环境标签 | `"cloud"` / `"production"` |
| 执行方式 | 网络调用云端QPU服务 |
| 量子比特限制 | 由云服务商决定（通常≥50） |
| 适用场景 | 生产服务、大规模量子计算、SaaS |
| 特点 | 真量子随机性、可扩展、按量付费 |
| 启动方式 | HTTP/gRPC请求 → 云端QPU执行 → 返回结果 |

### 2.3 专用部署 (Dedicated) — QPU硬件协处理器

| 属性 | 值 |
|------|-----|
| 部署类型ID | `DEPLOY_DEDI = 2` |
| 环境标签 | `"hardware"` / `"dedicated"` |
| 执行方式 | 直接调用本地QPU硬件协处理器 |
| 量子比特限制 | 由物理QPU决定（目前127+） |
| 适用场景 | 高性能量子计算、低延迟、专属设备 |
| 特点 | 最低延迟、完全控制、硬件直连 |
| 启动方式 | 硬件接口驱动 → QPU脉冲信号 → 直接读取 |

## 三、部署选择决策树

```
┌─ 启动 .qbc ─┐
│             │
├─ QPU_DEPLOY 环境变量存在？
│   ├─ YES → 使用指定部署类型
│   └─ NO  → 自动检测环境
│              │
│              ├─ QPU硬件驱动可用？
│              │   ├─ YES → DEPLOY_DEDI (专用部署)
│              │   └─ NO  → QPU云端API端点可用？
│              │              ├─ YES → DEPLOY_PROD (生产部署)
│              │              └─ NO  → DEPLOY_DEV (开发部署/QVM)
│              │
└─ 加载对应适配器
              │
              ├─ QpuAdapterQvm    (QVM虚拟机)
              ├─ QpuAdapterCloud  (云端API)
              └─ QpuAdapterHardware (硬件协处理器)
              │
              ▼
           执行量子字节码
```

## 四、模块设计

### 4.1 模块列表

| 模块 | 文件 | 职责 |
|------|------|------|
| 部署类型常量 | `qpu_deployment_types.qentl` | 定义3种部署类型的枚举、ID、标签 |
| 部署环境检测 | `qpu_runtime_detector.qentl` | 自动检测运行环境，返回最佳部署类型 |
| 部署路由器 | `qpu_deployment_router.qentl` | 根据部署类型路由到对应适配器 |
| QVM适配器 | `qpu_adapter_qvm.qentl` | 开发部署适配器，调用QVM虚拟机 |
| 云端适配器 | `qpu_adapter_cloud.qentl` | 生产部署适配器，HTTP/gRPC调用云端QPU |
| 硬件适配器 | `qpu_adapter_hardware.qentl` | 专用部署适配器，直接调用QPU硬件 |
| 部署配置 | `qpu_deployment_config.qentl` | 部署配置管理（连接参数、超时、重试） |

### 4.2 统一接口规范

所有适配器实现统一的`QpuAdapter`接口：

```qentl
interface QpuAdapter {
    function initialize(config: Map): Boolean;
    function execute(bytecode: Bytes): Map;       // 返回 {results, cycles, gates}
    function initializeQubits(n: Number): Boolean;
    function applyGate(opcode: Number, qubits: Array): Boolean;
    function measure(qubit: Number): Number;
    function shutdown(): Void;
    function getDeploymentType(): Number;
    function getStatus(): String;
}
```

## 五、配置管理

### 5.1 环境变量

| 变量 | 说明 | 取值 |
|------|------|------|
| `QPU_DEPLOY` | 强制指定部署类型 | `0`(dev) / `1`(prod) / `2`(dedi) |
| `QPU_CLOUD_URL` | 云端QPU API端点 | URL字符串 |
| `QPU_CLOUD_TOKEN` | 云端认证令牌 | Token字符串 |
| `QPU_HARDWARE_PATH` | QPU硬件设备路径 | 设备文件路径 |
| `QPU_TIMEOUT_MS` | 执行超时(ms) | 数字(默认30000) |
| `QPU_RETRY_COUNT` | 重试次数 | 数字(默认3) |

### 5.2 配置文件

```
QEntL/System/VM/config/qpu_deployment.json
{
  "deployment": {
    "mode": "auto",
    "fallback_chain": ["hardware", "cloud", "qvm"],
    "cloud": {
      "endpoint": "https://qpu.qentl.org/api/v1/execute",
      "auth_method": "token",
      "timeout_ms": 30000,
      "retry_count": 3
    },
    "hardware": {
      "driver_path": "/dev/qpu0",
      "firmware_version": "1.0.0"
    },
    "qvm": {
      "max_qubits": 32,
      "memory_limit": "16GB"
    }
  }
}
```

## 六、字节码格式扩展

`.qbc`文件新增部署头标记（可选）：

```
原有字节码格式保持不变 (向后兼容)
新增可选 header 标记:
  字节0-1: magic "QL" (QEntL)
  字节2:   version
  字节3:   preferred_deploy_type (0=any, 1=qvm-only, 2=cloud, 3=hardware)
  字节4+:  原始量子字节码
```

## 七、错误处理策略

| 场景 | 处理 |
|------|------|
| 目标部署不可用 | 按fallback_chain降级到下一级 |
| 云端API超时 | 重试 → 降级到QVM |
| 硬件驱动失败 | 降级到云端或QVM |
| 所有部署失败 | 抛出QpuDeploymentError，含详细诊断信息 |

## 八、验证标准

- [x] 3种部署类型常量定义完整
- [x] 部署环境检测器能识别当前环境
- [x] 部署路由器能正确路由到对应适配器
- [x] 3个适配器实现统一接口
- [x] 部署配置可读取环境变量
- [x] 降级fallback链正常工作
- [x] 所有新模块编译通过 (qcl_bootstrap)
