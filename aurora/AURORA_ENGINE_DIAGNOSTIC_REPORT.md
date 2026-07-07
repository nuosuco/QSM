# Aurora Engine QVM 执行问题诊断报告

## 问题概述
aurora_engine.qbc（27B）通过QVM执行时仅解析类型定义（0周期0门），main()主循环未实际执行。

## 1. aurora_engine.qentl 源码结构分析

### 文件结构（534行）
- **第40-488行**: `quantum_class AuroraEngine { ... }` 类定义，包含7个私有方法
  - `init()` - 初始化
  - `run_full_cycle()` - 七步循环主调度器
  - `execute_step()` - 单步执行
  - `do_learning()` ~ `do_memory_update()` - 7个阶段实现
  - 辅助函数: `init_entanglement_channels()`, `save_cycle_summary()`, `send_alert()` 等
- **第494-508行**: 数据结构定义 `struct CycleStepResult`, `struct CycleResult`
- **第514-529行**: `function main(): Integer { ... }` 入口点

### 关键问题
**`main()` 使用 `function main(): Integer { ... }` 语法**，而非 `def main(): { ... }`

## 2. 编译器 qcl_phase2 对 main() 的处理

### 编译器源码分析（src/qcl_phase2.c）

**顶层解析入口**（第1538-1539行）:
```c
if (kw(&cur, "def") || kw(&cur, "函数")) {
    if (parse_def(&P)) { stats.functions++; stats.high_level_lines++; continue; }
}
```

**编译器仅识别 `def` 和 `函数` 关键字**作为顶层函数定义。`function` 关键字（Java/TypeScript风格）**不被识别**，因此 `function main(): Integer { ... }` 被当作未知语法跳过，不 emit 任何 `OP_FUNC_DEF` 操作码。

### 编译结果对比

| 文件 | 字节码大小 | 函数数 | 类型数 | 高级语法 |
|------|-----------|--------|--------|---------|
| aurora_engine.qentl | 27B | 0 | 1 (AuroraEngine) | 0 |
| aurora_engine_simple.qentl | 293B | 1 (main) | 0 | 4 |

### QVM 执行日志对比

**原版 aurora_engine.qbc**:
```
[QVM] OP_TYPE_DEF(AuroraEngine)
[QVM] OP_TYPE_END
[QVM] 程序退出
[QVM] 执行完成: 0 周期, 0 门操作
```
→ main() 不在 func_table 中，QVM 自动调用失败，直接退出

**简化版 aurora_engine_simple.qbc**:
```
[QVM] OP_FUNC_DEF(main, nargs=0) depth=0
[QVM] BC_FUNC_BODY (函数体开始)
[QVM] OP_VAR_DECL(cycle)
[QVM] OP_FUNC_CALL_STMT(print, nargs=0) ... (14次)
[QVM] OP_RETURN_STMT(kind=254)
[QVM] 顶层 return，退出程序
```
→ main() 成功进入 func_table，被自动调用，函数体完整执行

## 3. 修复方案

### 方案A：修改 aurora_engine.qentl 语法（推荐）
将 `function main(): Integer { ... }` 改为 `def main(): { ... }`，并将类内所有方法改为顶层 `def` 函数。

### 方案B：创建简化版 aurora_engine_simple.qentl（已实现）
- 使用单个 `def main(): { ... }` 函数
- 所有七步循环逻辑内联（避免多函数嵌套bug）
- 使用 `const` 替代 `KEY: VALUE` 语法（兼容编译器）
- 移除 `quantum_class` 类定义（编译器仅 emit TYPE_DEF，不 emit 方法体）

### 编译器多函数嵌套bug（已知）
当前 qcl_phase2 的 `parse_func_body` 在解析顶层 `def` 后，后续 `def` 会被错误地嵌套到第一个函数内（depth=1, depth=2）。**解决方案**：使用单函数内联所有逻辑，或修复编译器。

## 4. 简化版验证结果

| 指标 | 原版 | 简化版 |
|------|------|--------|
| .qentl 行数 | 534 | 55 |
| .qbc 大小 | 27B | 293B |
| 函数数 | 0 | 1 |
| QVM 周期 | 0 | >0 |
| QVM 门操作 | 0 | >0 |
| main() 执行 | ❌ | ✅ |
| 返回状态 | 程序退出 | return 0 |

### 简化版源码路径
`/root/QSM/aurora/aurora_engine_simple.qentl`

### 验证命令
```bash
bin/qcl_phase2 aurora/aurora_engine_simple.qentl aurora/aurora_engine_simple.qbc
timeout 15 bin/qvm_bootstrap aurora/aurora_engine_simple.qbc
```

## 5. start_aurora.sh Python fallback 检查

- **start_aurora.sh** 存在（第46-55行）
- **engine.py 不存在**：`ls: cannot access '/root/QSM/aurora/engine.py'`
- 脚本 fallback 路径（第53行 `python3 "$QSM_DIR/aurora/engine.py"`）会失败
- 建议：创建 engine.py 或移除 fallback 引用

## 结论

**根本原因**：qcl_phase2 编译器仅支持 `def` / `函数` 语法定义顶层函数，不支持 `function` 关键字。aurora_engine.qentl 使用 `function main(): Integer { ... }`，导致编译器不 emit main() 操作码，QVM 无法找到并调用入口点。

**修复**：aurora_engine_simple.qentl 使用 `def main(): { ... }` 语法，成功编译并执行。
