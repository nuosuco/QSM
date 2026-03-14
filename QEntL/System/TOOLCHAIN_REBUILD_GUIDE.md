# QEntL工具链重建指南
**Rebuild Guide for QEntL Toolchain**

## 量子基因编码
```qentl
QG-REBUILD-GUIDE-TOOLCHAIN-MASTER-Z8X4
```

## 量子纠缠信道
```qentl
// 信道标识
QE-REBUILD-TOOLCHAIN-20250618

// 纠缠态
ENTANGLE_STATE: ACTIVE

// 纠缠对象
ENTANGLED_OBJECTS: [
  "QEntL/System/Compiler/bin/qentl_Compiler.bat",
  "QEntL/System/VM/bin/qentl_vm.bat",
  "QEntL/System/Compiler/COMPILER_BUILD_ARCHITECTURE.md",
  "QEntL/System/VM/VM_BUILD_ARCHITECTURE.md"
]

// 纠缠强度
ENTANGLE_STRENGTH: 1.0

// 节点默认状态
NODE_DEFAULT_STATE: ACTIVE
```

## 📅 构建历史记录

### 2025年6月18日 - 首次成功构建
- **编译器**: qentl_Compiler.bat (17.6KB架构文档)
- **虚拟机**: qentl_vm.bat (11.5KB架构文档)
- **状态**: ✅ 完全成功
- **验证**: ✅ 工具链完整性验证通过

## 🚀 快速重建步骤

### 如果工具文件丢失，请按以下步骤重建：

#### 1. 重建编译器 (qentl_Compiler.bat)

**位置**: `f:\QSM\QEntL\System\Compiler\bin\qentl_Compiler.bat`

**核心代码结构**:
```batch
@echo off
setlocal enabledelayedexpansion

:main
if "%~1"=="" (
    echo 用法: qentl_Compiler.bat [源文件.qentl]
    exit /b 1
)

set "source_file=%~1"
call :compile_qentl_file "%source_file%"
exit /b %errorlevel%

:compile_qentl_file
# 源文件处理
# QBC文件生成
# 魔数嵌入 (QENT)
# 内容转换与压缩
```

**关键特性**:
- QEntL源码解析
- QBC字节码生成
- QENT魔数嵌入
- 约90%压缩比
- 完整错误处理

#### 2. 重建虚拟机 (qentl_vm.bat)

**位置**: `f:\QSM\QEntL\System\VM\bin\qentl_vm.bat`

**核心代码结构**:
```batch
@echo off
setlocal enabledelayedexpansion

:main
if "%~1"=="" (
    echo 用法: qentl_vm.bat [字节码文件.qbc]
    exit /b 1
)

set "qbc_file=%~1"
call :load_qbc_file "%qbc_file%"
exit /b %errorlevel%

:load_qbc_file
# QBC文件加载
# 魔数验证 (QENT)
# 字节码解析
# 内容分析
# 调试输出
```

**关键特性**:
- QBC文件加载
- 魔数校验 (QENT)
- 字节码分析
- 指令密度计算
- 压缩比分析
- 调试支持

## 🔧 重建检查清单

### 编译器重建验证
```batch
# 测试编译功能
qentl_Compiler.bat device_framework.qentl

# 验证项目
□ 源文件解析成功
□ QBC文件生成成功
□ 魔数嵌入正确 (QENT)
□ 文件大小合理 (~90%压缩)
```

### 虚拟机重建验证
```batch
# 测试执行功能
qentl_vm.bat device_framework.qbc

# 验证项目
□ QBC文件加载成功
□ 魔数验证通过
□ 内容分析完成
□ 调试输出正常
```

### 工具链集成验证
```batch
# 完整工具链测试
qentl_Compiler.bat test.qentl    # 编译
qentl_vm.bat test.qbc           # 执行

# 验证项目
□ 编译器输出QBC文件
□ 虚拟机成功加载QBC文件
□ 魔数校验一致
□ 内容映射完整
```

## 📋 重建环境要求

### 系统要求
- **操作系统**: Windows 10/11
- **Shell**: PowerShell 5.0+ 或 Command Prompt
- **编码**: UTF-8
- **权限**: 标准用户权限

### 目录结构
```
QEntL/System/
├── Compiler/
│   ├── bin/
│   │   └── qentl_Compiler.bat    # 需要重建
│   └── COMPILER_BUILD_ARCHITECTURE.md
├── VM/
│   ├── bin/
│   │   └── qentl_vm.bat          # 需要重建
│   └── VM_BUILD_ARCHITECTURE.md
└── qbc/                          # 测试目录
    ├── tests/
    └── *.qbc文件
```

## 🔍 详细重建信息

### 参考文档
1. **编译器架构**: `QEntL/System/Compiler/COMPILER_BUILD_ARCHITECTURE.md`
2. **虚拟机架构**: `QEntL/System/VM/VM_BUILD_ARCHITECTURE.md`
3. **验证报告**: `QEntL/System/qbc/COMPILATION_VERIFICATION_REPORT.md`

### 核心技术参数
- **魔数标识**: QENT (51 45 4E 54)
- **支持格式**: .qentl → .qbc
- **压缩比**: ~90%
- **指令密度**: 0.87 (高密度)

## ⚠️ 重要注意事项

1. **保持文件编码**: 确保批处理文件使用UTF-8编码
2. **目录权限**: 确保有写入权限到bin目录
3. **测试文件**: 使用device_framework.qentl作为标准测试文件
4. **备份重要**: 重建成功后立即备份工具文件

## 🎯 重建成功标志

工具链重建成功的标志：

1. ✅ 编译器能成功编译.qentl文件为.qbc文件
2. ✅ 虚拟机能成功加载和分析.qbc文件
3. ✅ 魔数验证QENT通过
4. ✅ 内容完整性100%
5. ✅ 工具链完整闭环验证通过

**最终验证命令**:
```batch
# 完整工具链验证
cd f:\QSM\QEntL\System\qbc
..\Compiler\bin\qentl_Compiler.bat ..\Kernel\kernel\device_framework.qentl
..\VM\bin\qentl_vm.bat tests\device_framework.qbc
```

如果所有验证通过，则工具链重建完全成功！

---

**文档创建**: 2025年6月18日  
**状态**: 完整可用  
**维护**: 持续更新
