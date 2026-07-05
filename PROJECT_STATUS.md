# QSM 项目状态报告

> 生成时间：2026-07-06  
> 项目根目录：`/root/QSM`  
> 验证方式：递归文件系统扫描 + 文件头部字节检查

---

## 一、总体文件统计

| 指标 | 数量 |
|---|---|
| `.qentl` 文件总数 | **341** |
| `.qbc` 文件总数 | **552** |
| 有效 `.qbc`（首字节 0x14） | **548** |
| 无效 `.qbc`（首字节非 0x14） | **4** |
| 小体积 `.qbc`（大小 < 50 字节） | **212** |
| 完全空 `.qbc`（0 字节） | **0** |

> 说明：212 个小体积文件中，208 个首字节为 0x14（有效但体积过小），4 个首字节非 0x14（无效）。

---

## 二、无效 `.qbc` 明细（首字节 ≠ 0x14）

| 文件路径 | 大小(字节) | 首字节 |
|---|---|---|
| `./build/compiled/instruction_set.qbc` | 2 | 0x0b |
| `./QEntL/System/Compiler/bin/platform/linux_install.qbc` | 1 | 0x0c |
| `./QEntL/System/Compiler/src/backend/debug_info/debug_info_generator.qbc` | 1 | 0x0c |
| `./QEntL/System/VM/src/core/debug/debugger.qbc` | 1 | 0x0c |

---

## 三、`.qentl` 按目录分布（Top 20）

| 目录 | 文件数 |
|---|---|
| `QEntL/System/Kernel/filesystem` | 32 |
| `test` | 29 |
| `QEntL/System/Kernel/services` | 23 |
| `QEntL/System/Kernel/kernel` | 17 |
| `QEntL/System/Kernel/neural` | 15 |
| `QEntL/System/Kernel/gui` | 15 |
| `docs/examples` | 14 |
| `QEntL/Models/QSM` | 10 |
| `tests/qcl_phase2_boundary` | 8 |
| `QEntL/System/VM/src/deployment` | 8 |
| `docs/architecture` | 8 |
| `QEntL/System/Compiler/bin/cli` | 7 |
| `QEntL/Models/Ref` | 7 |
| `QCL模块` | 7 |
| `QEntL/Models/WeQ` | 6 |
| `QEntL/Models/SOM` | 6 |
| `docs` | 6 |
| `QEntL/System/VM/src/core/quantum` | 5 |
| `QEntL/System/VM/src/core/debug` | 5 |
| `QEntL/System/Compiler/bin/cli` | 5 |

> `.qentl` 文件共分布在 **70** 个目录中。

---

## 四、`.qbc` 按目录分布（Top 20）

| 目录 | 文件数 |
|---|---|
| `build/compiled` | 60 |
| `QEntL/System/Kernel/filesystem` | 32 |
| `dist/QDFS` | 32 |
| `build` | 30 |
| `test` | 29 |
| `build_report/logs` | 29 |
| `QEntl/System/Kernel/services` | 23 |
| `QEntl/Models/Ref` | 23 |
| `QEntl/Models/QSM` | 23 |
| `QEntl/System/Kernel/kernel` | 17 |
| `QEntl/System/Kernel/neural` | 15 |
| `QEntl/System/Kernel/gui` | 15 |
| `docs/examples` | 14 |
| `build/qbc/deployment` | 11 |
| `tests/qcl_phase2_boundary` | 8 |
| `QEntl/System/VM/src/deployment` | 8 |
| `QCL模块` | 8 |
| `docs/architecture` | 8 |
| `build/platform` | 8 |
| `build_output/QEntl/System/VM/src/deployment` | 8 |

> `.qbc` 文件共分布在 **78** 个目录中。

---

## 五、红线验证：`src/qcl_bootstrap.c`

| 检查项 | 结果 |
|---|---|
| 文件存在 | ✅ 是（247 行，7768 字节） |
| 含 `parse_import` 函数定义 | ✅ **无**（仅在注释红线声明中出现） |
| 含 `parse_type` 函数定义 | ✅ **无** |
| 含 `parse_function` 函数定义 | ✅ **无** |
| 含任意 `parse_xxx` 函数定义 | ✅ **无** |
| 红线是否违反 | ✅ **未违反** |

**结论：** `src/qcl_bootstrap.c` 不包含任何 `parse_import`、`parse_type`、`parse_function` 或其他 `parse_xxx` 函数定义，严格遵守"只允许解析量子指令子集"的红线约束。

---

## 六、总结

| 维度 | 状态 |
|---|---|
| 文件规模 | 341 个 `.qentl`，552 个 `.qbc`，代码规模较大 |
| 编译产出 | 548/552 个 `.qbc` 有效（99.3% 有效率） |
| 待清理项 | 4 个无效 `.qbc`（首字节非 0x14，极小体积）建议复查 |
| 红线合规 | ✅ 完全合规，未添加任何高级语法解析函数 |
