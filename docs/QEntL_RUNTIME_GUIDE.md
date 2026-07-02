# QEntL语言运行指南

**日期**: 2025年6月12日  
**系统**: QEntL量子编程语言生态系统

## 🎯 QEntL文件运行流程

### 完整的工具链

```
源代码(.qentl) → 编译器 → 字节码(.qobj) → 虚拟机 → 执行结果
```

## 🔧 运行QEntL文件的方法

### 方法1: 一键编译并运行（推荐）

```powershell
# 使用QEntL主CLI工具，自动编译并运行
.\QEntL\compiler\bin\cli\qentl_cli.qentl run test_hello.qentl

# 或者使用完整路径
.\QEntL\compiler\bin\qentl.qentl run .\tests\test_hello.qentl
```

### 方法2: 分步编译和运行

#### 步骤1: 编译QEntL源文件
```powershell
# 编译单个文件
.\QEntL\compiler\bin\cli\compiler_cli.qentl .\tests\test_hello.qentl -o .\build\

# 编译后生成: .\build\test_hello.qobj
```

#### 步骤2: 运行字节码文件
```powershell
# 使用虚拟机运行字节码
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\test_hello.qobj

# 或者使用虚拟机启动器
.\QEntL\vm\bin\cli\vm_launcher.qentl .\build\test_hello.qobj
```

### 方法3: 开发环境自动编译

```powershell
# 启动自动编译器，监控文件变化
.\QEntL\compiler\bin\cli\auto_compiler.qentl --watch .\tests --output .\build --verbose

# 在另一个终端运行编译好的文件
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\test_hello.qobj
```

## 📁 文件类型说明

### 源文件格式
- **`.qentl`** - QEntL源代码文件
- **`.qent`** - QEntL模块文件
- **`.qjs`** - QEntL JavaScript扩展文件

### 编译产物
- **`.qobj`** - QEntL字节码对象文件
- **`.qexe`** - QEntL可执行文件（链接后）
- **`.qlib`** - QEntL库文件

## 🚀 运行QEntL操作系统源文件

### 运行文件系统组件
```powershell
# 编译文件系统组件
.\QEntL\compiler\bin\cli\compiler_cli.qentl .\QEntL\src\filesystem\auto_classifier.qentl -o .\build\

# 运行文件系统组件
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\auto_classifier.qobj
```

### 运行内核组件
```powershell
# 编译内核组件
.\QEntL\compiler\bin\cli\compiler_cli.qentl .\QEntL\src\kernel\scheduler.qentl -o .\build\

# 运行内核组件
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\scheduler.qobj
```

### 运行服务组件
```powershell
# 编译服务组件
.\QEntL\compiler\bin\cli\compiler_cli.qentl .\QEntL\src\services\quantum_network.qentl -o .\build\

# 运行服务组件
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\quantum_network.qobj
```

## 🎮 虚拟机运行模式

### 1. 直接执行模式
```powershell
# 直接运行字节码文件
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj
```

### 2. 调试模式
```powershell
# 以调试模式运行
.\QEntL\vm\bin\cli\debug_cli.qentl program.qobj
```

### 3. 量子可视化模式
```powershell
# 以量子状态可视化模式运行
.\QEntL\vm\bin\cli\quantum_visualizer.qentl program.qobj
```

## ⚙️ 虚拟机参数配置

### 内存配置
```powershell
# 设置内存限制为512MB
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj --memory 512
```

### 调试选项
```powershell
# 启用详细调试输出
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj --debug --verbose
```

### 性能优化
```powershell
# 设置优化级别
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj --optimize 2
```

## 🔄 完整的开发工作流

### 1. 开发阶段
```powershell
# 启动自动编译器
.\QEntL\compiler\bin\cli\auto_compiler.qentl --watch .\QEntL\src --output .\build

# 编辑源文件 (在另一个终端/编辑器中)
# 文件保存后自动编译
```

### 2. 测试阶段
```powershell
# 运行编译好的程序
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\your_program.qobj

# 或者运行测试套件
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\test_suite.qobj
```

### 3. 部署阶段
```powershell
# 生成可执行文件
.\QEntL\compiler\bin\cli\linker_cli.qentl --input .\build\ --output .\dist\app.qexe

# 运行可执行文件
.\QEntL\vm\bin\cli\vm_cli.qentl run .\dist\app.qexe
```

## 🌟 QEntL操作系统的特殊运行方式

### 启动QEntL操作系统
```powershell
# 编译整个操作系统内核
.\QEntL\scripts\build_qentl.qentl --target os

# 启动QEntL操作系统
.\QEntL\vm\bin\cli\vm_launcher.qentl --os-mode .\build\qentl_os.qexe
```

### 双模式执行
QEntL的创新特性：同一套代码可以：
1. **在宿主系统上运行** - 作为普通应用程序
2. **作为独立操作系统运行** - 直接在硬件上

```powershell
# 应用程序模式
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj

# 操作系统模式
.\QEntL\vm\bin\cli\vm_launcher.qentl --boot program.qobj
```

## 🔧 故障排除

### 常见问题

1. **找不到导入模块**
```powershell
# 设置模块搜索路径
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj --module-path .\QEntL\src
```

2. **内存不足**
```powershell
# 增加内存限制
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj --memory 1024
```

3. **性能问题**
```powershell
# 启用优化
.\QEntL\vm\bin\cli\vm_cli.qentl run program.qobj --optimize 3
```

## 📝 示例命令

### 运行Hello World
```powershell
# 编译
.\QEntL\compiler\bin\cli\compiler_cli.qentl .\tests\test_hello.qentl -o .\build\

# 运行
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\test_hello.qobj
```

### 运行编译器测试
```powershell
# 编译编译器测试
.\QEntL\compiler\bin\cli\compiler_cli.qentl .\tests\test_compiler.qentl -o .\build\

# 运行编译器测试
.\QEntL\vm\bin\cli\vm_cli.qentl run .\build\test_compiler.qobj
```

这就是QEntL语言完整的运行机制！🚀
