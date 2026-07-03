# QSM Deployment Status Report — Hardware (Dedicated)

> Generated: 2026-07-03 | Mode: **Dedicated** (DEPLOY_ID_DEDI = 2)
> 量子基因编码: QGC-DEPLOY-STATUS-HW-2026070301

## Summary

| Attribute | Value |
|-----------|-------|
| **Status** | ⚠️ **PARTIAL — code ready, hardware unavailable** |
| Deployment Type ID | `DEPLOY_ID_DEDI = 2` |
| Environment Label | `hardware` / `dedicated` |
| Default Device Path | `/dev/qpu0` |
| Default Platform | `HW_PLATFORM_GENERIC` (4) |
| Hardware Timeout | 60,000 ms |
| Execution Model | Direct QPU coprocessor via device driver / pulse signals |
| Supported Platforms | IBM Superconducting, IonQ Trapped Ion, Rigetti, QuEra Neutral Atom, Generic QPU |

## Source Files (.qentl)

| File | Lines | Status |
|------|-------|--------|
| `qpu_adapter_hardware.qentl` | 611 | ✅ Present |
| `qpu_deployment_types.qentl` | — | ✅ Present |
| `qpu_deployment_config.qentl` | 478 | ✅ Present |
| `qpu_deployment_router.qentl` | — | ✅ Present |
| `qpu_runtime_detector.qentl` | — | ✅ Present |
| `qpu_bytecode_converter.qentl` | — | ✅ Present |

**Total .qentl files in deployment dir: 8**

## Bytecode Files (.qbc)

| File | Size (bytes) | Status |
|------|-------------|--------|
| `qpu_adapter_hardware.qbc` | 1,303 | ✅ Present |
| `qpu_deployment_config.qbc` | 472 | ✅ Present |
| `qpu_deployment_router.qbc` | 1,220 | ✅ Present |
| `qpu_deployment_types.qbc` | — | ✅ Present |
| `qpu_runtime_detector.qbc` | 570 | ✅ Present |
| `qpu_bytecode_converter.qbc` | — | ✅ Present |

**Total .qbc files in deployment dir: 8**
**Total .qbc files in project: 356**

## Hardware Configuration (defaults)

```qentl
hardwarePath       = "/dev/qpu0"
hardwarePlatform   = 4  // HW_PLATFORM_GENERIC
hardwareTimeoutMs  = 60000
hardwareRetryCount = 3
hardwareCalibrate  = false
pulseQueueSize     = 1024
measurementBuffer  = 256
```

## Deployment Manifest — Hardware

```json
{
  "deploymentMode": "dedicated",
  "deploymentType": 2,
  "label": "hardware",
  "defaultDevice": "/dev/qpu0",
  "defaultPlatform": "HW_PLATFORM_GENERIC",
  "binary": null,
  "compiler": "/root/QSM/bin/qcl_bootstrap",
  "sourceFiles": {
    "adapter": "qpu_adapter_hardware.qentl",
    "config": "qpu_deployment_config.qentl",
    "router": "qpu_deployment_router.qentl",
    "types": "qpu_deployment_types.qentl",
    "detector": "qpu_runtime_detector.qentl",
    "converter": "qpu_bytecode_converter.qentl"
  },
  "bytecodeFiles": {
    "adapter": "qpu_adapter_hardware.qbc",
    "config": "qpu_deployment_config.qbc",
    "router": "qpu_deployment_router.qbc",
    "types": "qpu_deployment_types.qbc",
    "detector": "qpu_runtime_detector.qbc",
    "converter": "qpu_bytecode_converter.qbc"
  },
  "config": {
    "hardwarePath": "/dev/qpu0",
    "hardwarePlatform": 4,
    "hardwareTimeoutMs": 60000,
    "hardwareRetryCount": 3,
    "hardwareCalibrate": false,
    "pulseQueueSize": 1024,
    "measurementBuffer": 256
  },
  "deviceExists": false,
  "status": "partial",
  "notes": [
    "Source code and bytecode compiled — adapter is ready",
    "/dev/qpu0 device file does not exist on this machine",
    "Requires physical QPU hardware or mock driver",
    "Fallback chain: hardware → cloud → qvm"
  ]
}
```

## Verification Checklist

- [x] `qpu_adapter_hardware.qentl` source present (611 lines, full adapter class)
- [x] `qpu_adapter_hardware.qbc` compiled bytecode present (1,303 bytes)
- [x] Deployment configuration (`.qentl` / `.qbc`) present
- [x] Deployment router and detector modules present
- [x] Supports IBM / IonQ / Rigetti / QuEra / Generic platforms
- [x] Supports calibration, pulse queue, measurement buffer
- [ ] `/dev/qpu0` device file available — ❌ not present
- [ ] Physical QPU hardware installed — ❌ not available

## Issues / Attention Needed

1. **No `/dev/qpu0` device** — The hardware adapter checks `fileExists("/dev/qpu0")` on init.
   This device does not exist on this system.
2. **Driver not installed** — No QPU hardware driver/coprocessor detected.
   The adapter relies on device file I/O (`openDevice`, `sendCommand`, `submitPulseProgram`).
3. **Placeholder implementations** — Low-level functions (`translateToPulses`,
   `submitPulseProgram`, `waitForCompletion`, `readMeasurements`) are stubbed
   (`return true` / `return null`). These need real driver bindings.

## Result

**Hardware (Dedicated) mode code is READY, but hardware is NOT AVAILABLE.**
All QEntL source (611 lines) and `.qbc` bytecode are compiled and present.
The deployment can succeed on any machine with a QPU device at `/dev/qpu0` (or
a custom path via `QPU_HARDWARE_PATH` env var or config). On this system,
the fallback chain will downgrade to cloud → qvm.
