# QSM量子叠加态模型项目 - 部署指南

**量子基因编码**: `QGC-DEPLOYMENT-GUIDE-2025061801`  
**量子纠缠信道**: `QEC-DEPLOYMENT-GUIDE-01`  
**文档版本**: v1.0.0  
**更新日期**: 2025年6月18日

## 🎯 项目概述

QSM量子叠加态模型项目是一个完整的量子编程生态系统，基于自主研发的QEntL编程语言，集成了四大核心模型：
- **QSM**: 量子状态模型
- **WeQ**: 量子通信模型  
- **SOM**: 松麦经济模型
- **Ref**: 自省监控模型

## 🛠️ 系统要求

### 硬件要求
- **CPU**: Intel i5或AMD Ryzen 5以上
- **内存**: 8GB RAM (推荐16GB)
- **硬盘**: 至少2GB可用空间
- **网络**: 互联网连接(用于扩展功能)

### 软件要求
- **操作系统**: Windows 10/11 (64位)
- **编译工具**: Microsoft Visual Studio (任一版本)
  - 支持路径: `D:\Program\Microsoft Visual Studio`
  - 支持路径: `D:\files\Microsoft Visual Studio`  
  - 支持路径: `C:\Program Files\Microsoft Visual Studio`
- **PowerShell**: Windows PowerShell 5.0+

## 📁 项目结构

```
QSM/
├── 🏗️ build/                          # 构建输出目录
│   ├── compiler/                      # 编译器可执行文件
│   ├── vm/                           # 虚拟机可执行文件
│   ├── models/                       # 四大模型服务
│   └── tests/                        # 测试程序
├── 📦 dist/                           # 发布目录
├── 📚 QEntL/                          # QEntL核心系统
│   ├── System/                       # 系统核心
│   │   ├── Compiler/                 # 编译器
│   │   ├── VM/                       # 虚拟机
│   │   ├── Kernel/                   # 系统内核
│   │   └── Runtime/                  # 运行时环境
│   ├── Models/                       # 四大模型
│   │   ├── QSM/                      # 量子状态模型
│   │   ├── WeQ/                      # 量子通信模型
│   │   ├── SOM/                      # 松麦经济模型
│   │   └── Ref/                      # 自省监控模型
│   └── docs/                         # 文档系统
├── 🧪 tests/                          # 测试文件
├── 📋 complete_project_build.bat      # 完整项目构建脚本
└── 🚀 run_qsm_system.bat             # 系统运行器
```

## 🚀 快速开始

### 1. 下载项目
确保项目已下载到本地目录，例如 `f:\QSM\`

### 2. 检查构建工具
确认您的系统已安装Microsoft Visual Studio，支持的安装路径：
- `D:\Program\Microsoft Visual Studio`
- `D:\files\Microsoft Visual Studio`
- `C:\Program Files\Microsoft Visual Studio`

### 3. 构建项目
双击运行 `build_qsm_project.bat` 脚本：

```batch
# 右键点击 build_qsm_project.bat
# 选择 "以管理员身份运行"
```

构建过程包括：
1. 🔧 检测构建环境
2. 🏗️ 创建构建目录
3. ⚡ 构建QEntL编译器
4. 🎮 构建QEntL虚拟机
5. 🌟 构建四大模型服务
6. 🧪 创建测试程序
7. 📝 生成启动脚本
8. ✅ 运行集成测试

### 4. 启动系统
构建完成后，双击运行 `run_qsm_system.bat`：

```batch
# 双击 run_qsm_system.bat
# 选择菜单选项使用系统
```

## 📖 使用指南

### 编译器使用

#### 基本编译
```batch
# 编译单个QEntL文件
build\compiler\qentl_compiler.exe hello.qentl

# 指定输出目录
build\compiler\qentl_compiler.exe hello.qentl -o ./output

# 启用优化
build\compiler\qentl_compiler.exe hello.qentl -O2

# 生成调试信息
build\compiler\qentl_compiler.exe hello.qentl -g
```

#### 编译选项
- `-o <目录>`: 指定输出目录
- `-O0`: 无优化 (默认)
- `-O1`: 基本优化
- `-O2`: 标准优化  
- `-O3`: 最大优化
- `-g`: 生成调试信息
- `-v`: 详细输出
- `-h`: 显示帮助

### 虚拟机使用

#### 基本执行
```batch
# 执行字节码文件
build\vm\qentl_vm.exe program.qbc

# 启用调试模式
build\vm\qentl_vm.exe program.qbc -d

# 显示性能统计
build\vm\qentl_vm.exe program.qbc -p

# 设置内存大小
build\vm\qentl_vm.exe program.qbc -h 128MB -s 16MB
```

#### 虚拟机选项
- `-h <大小>`: 设置堆大小 (默认: 64MB)
- `-s <大小>`: 设置栈大小 (默认: 8MB)
- `-d`: 启用调试模式
- `-p`: 显示性能统计
- `-q <数量>`: 设置最大量子状态数 (默认: 1024)

### 四大模型服务

#### 启动服务
```batch
# 启动所有模型服务
build\models\qsm_models_manager.exe
```

服务包括：
- **QSM服务**: 量子状态管理和叠加态处理
- **WeQ服务**: 量子通信和纠缠管理
- **SOM服务**: 松麦经济模型和激励机制
- **Ref服务**: 自省监控和系统反馈

## 📝 QEntL编程示例

### Hello World程序
```qentl
// hello_world.qentl
import "QEntL/core/console.qentl";

quantum_function main(): Integer {
    Console.println("🌟 Hello, QSM Quantum World!");
    Console.println("量子基因编码: QGC-HELLO-WORLD-2025061801");
    return 0;
}
```

### 量子状态程序
```qentl
// quantum_example.qentl
import "QEntL/core/console.qentl";
import "QEntL/quantum/state.qentl";

quantum_function main(): Integer {
    // 创建量子叠加态
    qstate = QuantumState.createSuperposition([0, 1]);
    
    Console.println("🔬 量子叠加态创建成功");
    Console.println("状态概率: " + qstate.getProbabilities());
    
    // 执行量子测量
    result = qstate.measure();
    Console.println("📊 测量结果: " + result);
    
    return 0;
}
```

### 四大模型集成程序
```qentl
// models_integration.qentl
import "QEntL/core/console.qentl";
import "Models/QSM/api/qsm_api.qentl";
import "Models/WeQ/api/weq_api.qentl";
import "Models/SOM/api/som_api.qentl";
import "Models/Ref/api/ref_api.qentl";

quantum_function main(): Integer {
    Console.println("🌟 四大模型集成演示");
    
    // QSM量子状态处理
    qsmResult = QSM.processQuantumState("superposition");
    Console.println("QSM处理结果: " + qsmResult);
    
    // WeQ量子通信
    weqChannel = WeQ.createQuantumChannel("channel1");
    WeQ.sendQuantumMessage(weqChannel, "Hello Quantum!");
    
    // SOM经济激励
    reward = SOM.calculateReward("task_completion", 100);
    Console.println("SOM奖励计算: " + reward);
    
    // Ref系统监控
    systemHealth = Ref.getSystemHealth();
    Console.println("系统健康状态: " + systemHealth);
    
    return 0;
}
```

## 🧪 测试与验证

### 运行测试套件
```batch
# 运行集成测试
build\tests\integration_test.exe

# 编译并运行示例程序
build\compiler\qentl_compiler.exe examples\hello_world.qentl
build\vm\qentl_vm.exe examples\hello_world.qbc
```

### 测试检查清单
- [ ] ✅ QEntL编译器正常工作
- [ ] ✅ QEntL虚拟机正常执行
- [ ] ✅ 四大模型服务启动成功
- [ ] ✅ 示例程序编译执行成功
- [ ] ✅ 量子状态操作正常
- [ ] ✅ 系统集成功能正常

## 🔧 故障排除

### 常见问题

#### 1. 构建失败
**问题**: Visual Studio未找到
**解决**: 确认VS安装路径，支持的路径：
- `D:\Program\Microsoft Visual Studio`
- `D:\files\Microsoft Visual Studio`
- `C:\Program Files\Microsoft Visual Studio`

#### 2. 编译器错误
**问题**: 编译器无法运行
**解决**: 
1. 检查build目录是否存在
2. 重新运行构建脚本
3. 以管理员权限运行

#### 3. 虚拟机异常
**问题**: 虚拟机执行失败
**解决**:
1. 检查字节码文件是否存在
2. 启用调试模式 `-d` 查看详细信息
3. 检查内存设置是否合理

#### 4. 模型服务启动失败
**问题**: 四大模型服务无法启动
**解决**:
1. 确认build\models目录完整
2. 检查端口占用情况
3. 查看系统资源使用情况

### 日志文件位置
- 编译器日志: `build\compiler\compiler.log`
- 虚拟机日志: `build\vm\vm.log`
- 模型服务日志: `build\models\services.log`

## 📊 性能优化

### 编译优化
- 使用 `-O2` 或 `-O3` 优化级别
- 启用调试信息 `-g` 便于调试
- 指定合适的输出目录 `-o`

### 运行时优化
- 根据程序需要调整堆大小 `-h`
- 合理设置栈大小 `-s`
- 量子状态数量适配 `-q`

### 系统调优
- 确保足够的系统内存
- 关闭不必要的后台程序
- 使用SSD硬盘提升I/O性能

## 🔄 系统升级

### 版本更新
1. 备份当前配置和数据
2. 下载新版本项目文件
3. 重新运行构建脚本
4. 验证系统功能完整性

### 配置迁移
- 复制用户程序和数据
- 保留自定义配置文件
- 更新环境变量设置

## 📞 技术支持

### 文档资源
- 架构文档: `QEntL\docs\architecture\README.md`
- 构建计划: `QEntL\docs\QEntL_BUILD_PLAN.md`  
- 项目完成计划: `PROJECT_COMPLETION_PLAN.md`

### 开发者信息
- **项目名称**: QSM量子叠加态模型
- **量子基因编码**: QGC-QSM-PROJECT-2025061801
- **技术栈**: QEntL, C++, Windows
- **开发模式**: 敏捷开发, 量子计算

## 🎉 成功部署确认

部署成功的标志：
1. 🟢 构建脚本执行无错误
2. 🟢 系统启动器正常工作
3. 🟢 编译器可以编译QEntL程序
4. 🟢 虚拟机可以执行字节码
5. 🟢 四大模型服务正常运行
6. 🟢 集成测试全部通过

**🌟 恭喜！QSM量子叠加态模型系统部署成功！**

---

*本部署指南涵盖了QSM项目的完整部署流程，如遇问题请参考故障排除章节或查阅相关技术文档。*
