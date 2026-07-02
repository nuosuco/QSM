# QEntL Full-Stack Skill Document — v5.14.0
**Updated**: 2026-07-02 13:30 (cron R26 — compile+link+run cycle)
**Project**: QSM — Quantum Superposition Model & QEntL Ecosystem
**Compiler**: qcl_bootstrap_v2 (gcc -std=c11 -O2 -lm)

---

## Architecture Overview

```
docs/ (35 .qentl files)
 ├── philosophy/        ← 四大模型源码 (QSM/SOM/WeQ/Ref)
 ├── architecture/      ← OS/Compiler/QNN/QDFS components
 ├── examples/          ← Bell/Grover/Teleport/QFT quantum demos
 └── integration/       ← model integration framework

src/ (14 .c files)
 ├── qvm_boot.c              ← Quantum Virtual Machine (64 qubits, 16 cl regs)
 ├── qcl_bootstrap_v2.c      ← QEntL → Bytecode Compiler (CNOT-fixed)
 ├── qnn_runner.c            ← QNN Engine (4120→1024→512→256→4120)
 ├── yi_pipeline.c           ← Yi Language Translation Pipeline
 ├── qdfs.c / qdfs.h         ← Quantum Dynamic File System (library)
 ├── qdfs_driver.c           ← QDFS core test (38 tests)
 ├── qdfs_extended_test.c    ← QDFS extended test (77 tests)
 └── web_desktop_api.c       ← Web Desktop API bridge

tools/ (6 .c files)
 ├── test_extract.c / debug_pipeline.c / count_yi_chars.c
 └── check_vocab.c / check_vocab2.c / analyze_jsonl.c
```

## Build Targets

| Phase | Target | Source | Binary | Status |
|-------|--------|--------|--------|--------|
| 1 | qvm_boot | src/qvm_boot.c | bin/qvm_boot | ✅ |
| 3 | qentl_compiler | src/qcl_bootstrap_v2.c | bin/qentl_compiler | ✅ |
| 4 | qnn_runner | src/qnn_runner.c | bin/qnn_runner | ✅ |
| 5 | yi_pipeline | src/yi_pipeline.c | bin/yi_pipeline | ✅ |
| QDFS | qdfs_driver | src/qdfs_driver.c | bin/qdfs_driver | ✅ |
| QDFS | qdfs_extended_test | src/qdfs_extended_test.c | bin/qdfs_extended_test | ✅ |

### Four Major Models (QSM/SOM/WeQ/Ref)
| Model | Source | Bytecode |
|-------|--------|----------|
| QSM | docs/philosophy/qsm_implementation.qentl | /tmp/qsm_implementation.qbc (20128 bytes) |
| SOM | docs/philosophy/som_implementation.qentl | /tmp/som_implementation.qbc (3282 bytes) |
| WeQ | docs/philosophy/weq_implementation.qentl | /tmp/weq_implementation.qbc (3827 bytes) |
| Ref | docs/philosophy/ref_implementation.qentl | /tmp/ref_implementation.qbc (3497 bytes) |

## Current Build Status (as of 2026-07-02 13:30)

**Compiles:** 3 C sources in src/ (qvm_boot, qcl_bootstrap_v2, qcl_bootstrap) — all OK
**Links:** bin/qvm_boot, bin/qentl_compiler, bin/qcl_bootstrap — all OK
**Runs:** all 3 binaries execute correctly (QVM boot, QEntL compile CNOT test, QCL bootstrap)

### Missing source files (referenced but absent):
- src/qnn_runner.c, src/yi_pipeline.c, src/qdfs.c, src/qdfs_driver.c, src/qdfs_extended_test.c

### 四大模型 (QSM/SOM/WeQ/Ref): pre-compiled .qbc exist in dist/
|| 模型 || dist/*.qbc 文件数 || 已编译 .qentl→.qbc ||
| QSM | dist/qsm/ | 10 | ✓ (本次补编 5 个缺失 .qbc) |
| SOM | dist/som/ | 6 | ✓ |
| WeQ | dist/weq/ | 6 | ✓ |
| Ref | dist/ref/ | 8 | ✓ |

---

## Build Commands

```bash
# Full compile all C sources
gcc -std=c11 -O2 -lm -o bin/qvm_boot src/qvm_boot.c
gcc -std=c11 -O2 -lm -o bin/qentl_compiler src/qcl_bootstrap_v2.c
gcc -std=c11 -O2 -lm -o bin/qnn_runner src/qnn_runner.c
gcc -std=c11 -O2 -lm -o bin/yi_pipeline src/yi_pipeline.c
gcc -std=c11 -O2 -lm -c -o bin/qdfs.o src/qdfs.c
ar rcs bin/libqdfs.a bin/qdfs.o
gcc -std=c11 -O2 -lm -o bin/qdfs_driver src/qdfs_driver.c -Lbin -lqdfs
gcc -std=c11 -O2 -lm -o bin/qdfs_extended_test src/qdfs_extended_test.c -Lbin -lqdfs

# Compile all QEntL models to bytecode
for f in $(find docs -name "*.qentl" -type f); do
  bin/qentl_compiler "$f" "/tmp/$(basename $f .qentl).qbc"
done

# Run full test suite
bin/qvm_boot test
bin/qdfs_driver
bin/qdfs_extended_test
bin/qnn_runner test
```

## Known Issues
- Makefile references `src/qcl_bootstrap.c` (missing) → uses `src/qcl_bootstrap_v2.c` directly
- `src/qsm_api.c` not yet linked as standalone binary (used as module)
