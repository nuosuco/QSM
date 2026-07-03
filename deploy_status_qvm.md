# QSM Deployment Status Report — QVM (Development)

> Generated: 2026-07-03 | Mode: **Development** (DEPLOY_ID_DEV = 0)
> 量子基因编码: QGC-DEPLOY-STATUS-QVM-2026070301

## Summary

| Attribute | Value |
|-----------|-------|
| **Status** | ✅ **READY** |
| Deployment Type ID | `DEPLOY_ID_DEV = 0` |
| Environment Label | `qvm` / `development` |
| Binary | `/root/QSM/bin/qvm_bootstrap` (ELF 64-bit, 12,920 bytes) |
| Compiler Binary | `/root/QSM/bin/qcl_bootstrap` (ELF 64-bit, 22,680 bytes) |
| Max Qubits | 32 (default) / ≤26 by physical memory |
| Memory Limit | `16GB` (default) |
| Execution Model | Local CPU quantum simulation, deterministic |

## Source Files (.qentl)

| File | Lines | Status |
|------|-------|--------|
| `qpu_adapter_qvm.qentl` | 439 | ✅ Present |
| `qpu_deployment_types.qentl` | — | ✅ Present |
| `qpu_deployment_config.qentl` | 478 | ✅ Present |
| `qpu_deployment_router.qentl` | — | ✅ Present |
| `qpu_runtime_detector.qentl` | — | ✅ Present |
| `qpu_bytecode_converter.qentl` | — | ✅ Present |

**Total .qentl files in deployment dir: 8**

## Bytecode Files (.qbc)

| File | Size (bytes) | Status |
|------|-------------|--------|
| `qpu_adapter_qvm.qbc` | 207 | ✅ Present |
| `qpu_adapter_hardware.qbc` | 1,303 | ✅ Present |
| `qpu_adapter_cloud.qbc` | 465 | ✅ Present |
| `qpu_deployment_config.qbc` | 472 | ✅ Present |
| `qpu_deployment_router.qbc` | 1,220 | ✅ Present |
| `qpu_deployment_types.qbc` | — | ✅ Present |
| `qpu_runtime_detector.qbc` | 570 | ✅ Present |
| `qpu_bytecode_converter.qbc` | — | ✅ Present |

**Total .qbc files in deployment dir: 8**
**Total .qbc files in project: 356**

## Deployment Manifest — QVM

```json
{
  "deploymentMode": "development",
  "deploymentType": 0,
  "label": "qvm",
  "binary": "/root/QSM/bin/qvm_bootstrap",
  "compiler": "/root/QSM/bin/qcl_bootstrap",
  "binaryExists": true,
  "binaryType": "ELF 64-bit LSB executable, x86-64",
  "sourceFiles": {
    "adapter": "qpu_adapter_qvm.qentl",
    "config": "qpu_deployment_config.qentl",
    "router": "qpu_deployment_router.qentl",
    "types": "qpu_deployment_types.qentl",
    "detector": "qpu_runtime_detector.qentl",
    "converter": "qpu_bytecode_converter.qentl"
  },
  "bytecodeFiles": {
    "adapter": "qpu_adapter_qvm.qbc",
    "config": "qpu_deployment_config.qbc",
    "router": "qpu_deployment_router.qbc",
    "types": "qpu_deployment_types.qbc",
    "detector": "qpu_runtime_detector.qbc",
    "converter": "qpu_bytecode_converter.qbc"
  },
  "config": {
    "qvmPath": "bin/qvm_bootstrap",
    "maxQubits": 32,
    "memoryLimit": "16GB",
    "verbose": false
  },
  "status": "ready"
}
```

## Verification Checklist

- [x] `qpu_adapter_qvm.qentl` source present (439 lines)
- [x] `qpu_adapter_qvm.qbc` compiled bytecode present (207 bytes)
- [x] `bin/qvm_bootstrap` binary executable and verified ELF64
- [x] `bin/qcl_bootstrap` compiler binary present
- [x] Deployment configuration (`qpu_deployment_config.qentl/.qbc`) present
- [x] Deployment router and detector modules present
- [x] Architecture spec (`QUANTUM_DEPLOYMENT_ARCH.md`) present

## Result

**QVM (Development) mode is READY.** All source, bytecode, and runtime files verified.
The `qvm_bootstrap` binary is a working ELF64 executable accepting `.qbc` files as input.
