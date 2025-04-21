# QEntL虚拟机

QEntL虚拟机是一个完全用QEntL语言实现的虚拟机，不依赖任何第三方技术，能够在多个平台上运行，并支持完整的QEntL操作系统。

## 目录结构

```
QEntL/vm/
├── core/                     # 虚拟机核心组件
│   ├── vm_core.qentl         # 虚拟机核心
│   ├── vm_device_manager.qentl # 设备管理器
│   ├── vm_instruction_set.qentl # 指令集
│   ├── vm_memory_manager.qentl # 内存管理器
│   ├── vm_platform_adapter.qentl # 平台适配器
│   ├── vm_process_scheduler.qentl # 进程调度器
│   └── vm_quantum_runtime.qentl # 量子运行时
├── launchers/                # 平台特定启动器
│   ├── windows_launcher.qjs  # Windows启动器
│   ├── linux_launcher.qjs    # Linux启动器
│   └── macos_launcher.qjs    # macOS启动器
├── tests/                    # 测试文件
│   └── qentl_os.qentl        # 测试操作系统
├── vm_launcher.qentl         # 虚拟机启动器
├── qentl_os.qentl            # QEntL操作系统
├── run_vm.qjs                # 运行时启动脚本
├── run.bat                   # Windows批处理启动脚本
└── run.sh                    # Linux/macOS启动脚本
```

## 运行虚拟机

### Windows

```
> run.bat
```

### Linux/macOS

```
$ chmod +x run.sh
$ ./run.sh
```

## 虚拟机架构

QEntL虚拟机采用模块化设计，主要组件包括：

1. **虚拟机核心(VMCore)** - 负责协调其他组件工作，管理虚拟机的生命周期
2. **指令集(InstructionSet)** - 定义虚拟机的指令集和指令解释器
3. **内存管理器(MemoryManager)** - 管理虚拟机的内存分配和访问
4. **进程调度器(ProcessScheduler)** - 管理进程的创建、调度和终止
5. **平台适配器(PlatformAdapter)** - 提供不同平台的兼容层
6. **设备管理器(DeviceManager)** - 管理虚拟和物理设备
7. **量子运行时(QuantumRuntime)** - 提供量子计算功能和量子状态管理

## 扩展虚拟机

要为新平台创建启动器，请按照以下步骤操作：

1. 在`launchers/`目录下创建新的启动器文件，例如`my_platform_launcher.qjs`
2. 修改`run_vm.qjs`添加新平台的检测和支持
3. 创建新平台的启动脚本

## 量子特性

QEntL虚拟机支持以下量子特性：

- 量子比特分配和操作
- 量子门操作(H, X, Y, Z, CNOT等)
- 量子纠缠
- 量子测量
- 量子电路优化 