# QSM Deployment Status Report — Cloud (Production)

> Generated: 2026-07-03 | Mode: **Production** (DEPLOY_ID_PROD = 1)
> 量子基因编码: QGC-DEPLOY-STATUS-CLOUD-2026070301

## Summary

| Attribute | Value |
|-----------|-------|
| **Status** | ⚠️ **PARTIAL — code ready, endpoint/config not configured** |
| Deployment Type ID | `DEPLOY_ID_PROD = 1` |
| Environment Label | `cloud` / `production` |
| Default Endpoint | `DEFAULT_CLOUD_ENDPOINT` (qpu.qentl.org/api/v1/execute) |
| Default Protocol | `http` |
| Timeout | `DEFAULT_TIMEOUT_MS` (30,000 ms) |
| Retry Count | `DEFAULT_RETRY_COUNT` (3) |
| Auth Method | Bearer token (`QPU_CLOUD_TOKEN`) |
| Execution Model | HTTP POST `/api/v1/execute` → base64 bytecode → JSON response |

## Source Files (.qentl)

| File | Lines | Status |
|------|-------|--------|
| `qpu_adapter_cloud.qentl` | 465 | ✅ Present |
| `qpu_deployment_types.qentl` | — | ✅ Present |
| `qpu_deployment_config.qentl` | 478 | ✅ Present |
| `qpu_deployment_router.qentl` | — | ✅ Present |
| `qpu_runtime_detector.qentl` | — | ✅ Present |
| `qpu_bytecode_converter.qentl` | — | ✅ Present |

**Total .qentl files in deployment dir: 8**

## Bytecode Files (.qbc)

| File | Size (bytes) | Status |
|------|-------------|--------|
| `qpu_adapter_cloud.qbc` | 465 | ✅ Present |
| `qpu_deployment_config.qbc` | 472 | ✅ Present |
| `qpu_deployment_router.qbc` | 1,220 | ✅ Present |
| `qpu_deployment_types.qbc` | — | ✅ Present |
| `qpu_runtime_detector.qbc` | 570 | ✅ Present |
| `qpu_bytecode_converter.qbc` | — | ✅ Present |

**Total .qbc files in deployment dir: 8**
**Total .qbc files in project: 356**

## Cloud Configuration (defaults)

```qentl
cloudEndpointUrl = DEFAULT_CLOUD_ENDPOINT   // qpu.qentl.org/api/v1/execute
cloudAuthToken   = ""                        // needs QPU_CLOUD_TOKEN env var
cloudTimeoutMs   = DEFAULT_TIMEOUT_MS        // 30000
cloudRetryCount  = DEFAULT_RETRY_COUNT       // 3
cloudProtocol    = "http"
cloudBatchSize   = 100
cloudCompress    = false
```

## API Contract

```
POST https://<cloud-host>/api/v1/execute
Headers:
  Authorization: Bearer <token>
  Content-Type: application/json
  X-Protocol: http|grpc
Body:
  { "bytecode": "<base64>", "protocol": "http", "timeout": 30000 }
Response:
  {
    "success": true,
    "data": {
      "cycles": N,
      "gates": N,
      "measurements": [...],
      "jobId": "uuid"
    },
    "latency": N
  }
```

## Deployment Manifest — Cloud

```json
{
  "deploymentMode": "production",
  "deploymentType": 1,
  "label": "cloud",
  "endpoint": "https://qpu.qentl.org/api/v1/execute",
  "binary": null,
  "compiler": "/root/QSM/bin/qcl_bootstrap",
  "sourceFiles": {
    "adapter": "qpu_adapter_cloud.qentl",
    "config": "qpu_deployment_config.qentl",
    "router": "qpu_deployment_router.qentl",
    "types": "qpu_deployment_types.qentl",
    "detector": "qpu_runtime_detector.qentl",
    "converter": "qpu_bytecode_converter.qentl"
  },
  "bytecodeFiles": {
    "adapter": "qpu_adapter_cloud.qbc",
    "config": "qpu_deployment_config.qbc",
    "router": "qpu_deployment_router.qbc",
    "types": "qpu_deployment_types.qbc",
    "detector": "qpu_runtime_detector.qbc",
    "converter": "qpu_bytecode_converter.qbc"
  },
  "config": {
    "endpointUrl": "https://qpu.qentl.org/api/v1/execute",
    "authToken": "(not configured)",
    "timeoutMs": 30000,
    "retryCount": 3,
    "protocol": "http",
    "batchSize": 100,
    "compress": false
  },
  "endpointReachable": false,
  "authConfigured": false,
  "status": "partial",
  "notes": [
    "Source code and bytecode compiled — adapter is ready",
    "No QPU_CLOUD_TOKEN environment variable set",
    "Cloud endpoint not verified reachable",
    "HTTP GET/POST helpers are stubbed (placeholder implementations)",
    "Fallback chain: hardware → cloud → qvm"
  ]
}
```

## Verification Checklist

- [x] `qpu_adapter_cloud.qentl` source present (465 lines, full adapter class)
- [x] `qpu_adapter_cloud.qbc` compiled bytecode present (465 bytes)
- [x] Deployment configuration (`.qentl` / `.qbc`) present
- [x] Deployment router and detector modules present
- [x] Supports HTTP and gRPC protocols
- [x] Retry logic implemented (up to 3 retries)
- [x] Job history tracking implemented
- [ ] `QPU_CLOUD_TOKEN` environment variable set — ❌ not configured
- [ ] `QPU_CLOUD_URL` environment variable set — ❌ not configured
- [ ] Cloud endpoint reachable — ❌ not verified
- [x] Health-check endpoint defined (`/health`)
- [ ] HTTP client (`httpClientGet` / `httpClientPost`) — ⚠️ placeholder only

## Issues / Attention Needed

1. **No authentication token** — `cloudAuthToken` is empty. Set `QPU_CLOUD_TOKEN`
   environment variable or provide in config JSON.
2. **No cloud endpoint configured** — `cloudEndpointUrl` uses the default.
   Override via `QPU_CLOUD_URL` env var.
3. **HTTP client is stubbed** — `httpClientGet` and `httpClientPost` are
   placeholder implementations (`return null`). A real QEntL network module
   is required for production operation.
4. **Endpoint not reachable** — `/health` check will fail without a live
   `qpu.qentl.org` service.

## Result

**Cloud (Production) mode code is READY, but cloud service is NOT CONFIGURED.**
All QEntL source (465 lines) and `.qbc` bytecode are compiled and present.
The adapter is fully structured with retry logic, job history, and protocol
selection. It requires a live cloud endpoint, auth token, and a working
QEntL HTTP client module to function. Without these, the deployment will
fallback to hardware → qvm per the fallback chain.
