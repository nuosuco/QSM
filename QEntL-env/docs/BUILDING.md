# QEntL环境构建指南

> **重要原则**:
> 1. QEntL语言和环境不依赖任何第三方语言、环境或依赖包，完全自主开发，自己支持整个项目的运行服务
> 2. QEntL语言的基础和全面性是项目开发的关键，没有它开发者将无法进行开发

本文档详细说明了如何从源代码构建QEntL语言环境。

## QEntL环境概述

QEntL环境是一个完全自主开发的量子纠缠编程平台，包含以下核心组件：

1. **QEntL解释器**: 解析和执行QEntL语言代码
2. **量子运行时**: 管理量子状态、纠缠关系和事件处理
3. **标准库**: 提供量子基因编码、纠缠管理等核心功能
4. **开发工具**: 包括编辑器、可视化工具和调试器
5. **模型集成框架**: 连接QSM、SOM、REF和WeQ四大模型

所有这些组件都完全自主开发，不依赖任何外部技术，确保了系统的完整性和独立性。

## 支持的文件类型

构建QEntL环境后，您将能够处理以下文件类型：

| 扩展名 | 文件类型 | 构建后的支持功能 |
|-------|---------|---------------|
| .qent | 量子实体文件 | 解析和加载量子实体定义 |
| .qentl | 量子纠缠语言文件 | 完整编译和执行量子纠缠程序 |
| .qjs | 量子JavaScript文件 | 动态量子脚本解析和执行 |
| .qcss | 量子层叠样式表 | 量子可视化界面渲染 |
| .qpy | 量子Python扩展 | 量子数据分析脚本执行 |
| .qml | 量子标记语言 | 解析量子实体结构定义 |
| .qsql | 量子结构化查询语言 | 处理量子数据库查询 |
| .qsch | 量子图式文件 | 解析和实现量子系统设计 |
| .qasm | 量子汇编语言 | 执行低级量子操作 |
| .qql | 量子查询语言 | 查询和操作量子状态 |
| .qcon | 量子配置文件 | 加载环境配置 |
| .qtest | 量子测试文件 | 执行测试用例 |
| .qmod | 量子模块文件 | 加载可重用量子组件 |

## 前置条件

为了构建QEntL环境，您需要以下工具：

1. **C编译器**：gcc、clang或Visual Studio（Windows）
2. **构建系统**：Make
3. **开发工具**：Git（可选，用于获取源代码）

## 获取源代码

```bash
# 若使用Git，可以通过以下方式获取代码
git clone https://project-url/QEntL-env.git
cd QEntL-env

# 或直接使用下载的源代码
```

## GCC环境安装

### Windows (使用MSYS2)

MSYS2提供了Windows上的GCC编译环境。本项目在 `QEntL-env\gcc编译器\` 目录中包含了MSYS2安装程序。

1. **安装MSYS2**:
   - 运行 `QEntL-env\gcc编译器\msys2-installer.exe`
   - 按照安装向导完成安装，推荐安装路径为 `C:\msys64`
   - 安装完成后会自动打开MSYS2终端

2. **更新MSYS2系统**:
   ```bash
   pacman -Syu
   ```
   - 完成后关闭终端窗口
   - 重新打开MSYS2终端并执行:
   ```bash
   pacman -Syu
   ```

3. **安装GCC和开发工具**:
   ```bash
   pacman -S mingw-w64-x86_64-toolchain
   pacman -S make
   pacman -S mingw-w64-x86_64-cmake
   ```

4. **设置环境变量**:
   - 右键"此电脑"，选择"属性"
   - 点击"高级系统设置"
   - 点击"环境变量"按钮
   - 在"系统变量"部分，编辑"Path"变量
   - 添加 `C:\msys64\mingw64\bin`
   - 点击确定保存更改

5. **验证安装**:
   - 打开新的命令提示符或PowerShell
   - 执行:
   ```
   gcc --version
   g++ --version
   make --version
   ```

### Linux

#### Debian/Ubuntu:
```bash
sudo apt update
sudo apt install build-essential
sudo apt install cmake
```

#### Fedora/RHEL/CentOS:
```bash
sudo dnf update
sudo dnf group install "Development Tools"
sudo dnf install cmake
```

### macOS:
```bash
xcode-select --install
brew install cmake
```

## 构建QEntL环境

### 方法一：使用QEntL原生命令（推荐）

QEntL提供了自己的构建工具链，完全自主实现：

```bash
# 创建构建环境
qentl_init_build_env

# 配置构建
qentl_configure --enable-all-components

# 执行构建
qentl_build

# 安装到系统
qentl_install
```

### 方法二：手动构建

#### Linux/macOS

```bash
# 进入源代码目录
cd QEntL-env/src

# 编译核心解释器
gcc -o ../bin/qentl interpreter/qentl_interpreter.c -I. -std=c99 -Wall -O2

# 编译量子运行时
gcc -o ../bin/qentl_runtime runtime/quantum_runtime.c -I. -std=c99 -Wall -O2

# 编译标准库
gcc -c stdlib/core/*.c -I.
gcc -c stdlib/network/*.c -I.
gcc -c stdlib/visualization/*.c -I.
gcc -c stdlib/integration/*.c -I.
ar rcs ../lib/libqentl_stdlib.a *.o

# 编译工具
gcc -o ../bin/qentl_editor tools/editor/main.c -I. -L../lib -lqentl_stdlib -std=c99 -Wall -O2
gcc -o ../bin/qentl_visualizer tools/visualizer/main.c -I. -L../lib -lqentl_stdlib -std=c99 -Wall -O2
gcc -o ../bin/qentl_debugger tools/debugger/main.c -I. -L../lib -lqentl_stdlib -std=c99 -Wall -O2

# 添加可执行权限
chmod +x ../bin/*
```

#### Windows

```batch
REM 进入源代码目录
cd QEntL-env\src

REM 使用Visual Studio编译（命令行版本）
cl /Fe..\bin\qentl.exe interpreter\qentl_interpreter.c /I. /W4 /O2
cl /Fe..\bin\qentl_runtime.exe runtime\quantum_runtime.c /I. /W4 /O2

REM 编译标准库
cl /c stdlib\core\*.c /I.
cl /c stdlib\network\*.c /I.
cl /c stdlib\visualization\*.c /I.
cl /c stdlib\integration\*.c /I.
lib /OUT:..\lib\qentl_stdlib.lib *.obj

REM 编译工具
cl /Fe..\bin\qentl_editor.exe tools\editor\main.c /I. /link ..\lib\qentl_stdlib.lib
cl /Fe..\bin\qentl_visualizer.exe tools\visualizer\main.c /I. /link ..\lib\qentl_stdlib.lib
cl /Fe..\bin\qentl_debugger.exe tools\debugger\main.c /I. /link ..\lib\qentl_stdlib.lib

REM 或使用MinGW/gcc
gcc -o ..\bin\qentl.exe interpreter\qentl_interpreter.c -I. -std=c99 -Wall -O2
```

### 方法三：使用CMake构建

如果您已安装CMake，可以使用以下方法构建:

```bash
# 创建构建目录
mkdir -p QEntL-env/build
cd QEntL-env/build

# 配置项目
cmake ..

# 构建项目
cmake --build .

# 安装
cmake --install .
```

## 构建后验证

完成构建后，您应该测试QEntL环境的各个组件是否正常工作：

### 基础功能测试

```bash
# 验证解释器版本
./bin/qentl --version

# 运行基本语法测试
./bin/qentl ./tests/basic_syntax.qentl

# 测试量子状态管理
./bin/qentl ./tests/quantum_state_test.qentl

# 测试量子纠缠
./bin/qentl ./tests/entanglement_test.qentl
```

### 高级功能测试

```bash
# 测试量子基因编码
./bin/qentl ./tests/quantum_gene_test.qentl

# 测试五蕴状态
./bin/qentl ./tests/five_aggregates_test.qentl

# 测试量子区块链
./bin/qentl ./tests/quantum_blockchain_test.qentl

# 测试模型集成
./bin/qentl ./tests/model_integration_test.qentl
```

## 启动QEntL服务

构建完成后，您可以通过多种方式启动QEntL服务：

### 使用启动脚本

项目根目录提供了一个启动脚本，用于启动所有QEntL服务：

```bash
# Windows
start_qentl_ui.bat

# Linux/macOS
./start_qentl_ui.sh
```

### 手动启动服务

您也可以手动启动各个服务：

```bash
# 启动QSM服务（主服务）
cd QEntL-env/bin
./qentl --service=qsm --port=5000

# 启动WeQ服务
./qentl --service=weq --port=5001

# 启动SOM服务
./qentl --service=som --port=5002

# 启动Ref服务
./qentl --service=ref --port=5003

# 启动World服务
./qentl --service=world --port=3000
```

### 使用标准服务命令

QEntL提供了标准服务管理命令：

```bash
# 启动所有服务
./bin/qentl service start

# 检查服务状态
./bin/qentl service status

# 停止特定服务
./bin/qentl service stop --name=qsm

# 停止所有服务
./bin/qentl service stop --all
```

### 访问服务

所有服务启动后，您可以通过浏览器访问：

- 主UI界面: http://localhost:3000
- QSM API: http://localhost:5000
- WeQ API: http://localhost:5001
- SOM API: http://localhost:5002
- Ref API: http://localhost:5003

## 环境变量设置

为了在系统中全局使用QEntL，建议将以下路径添加到系统PATH环境变量中：

### Linux/macOS

```bash
# 临时设置
export PATH=$PATH:/path/to/QEntL-env/bin

# 永久设置（添加到~/.bashrc或~/.zshrc）
echo 'export PATH=$PATH:/path/to/QEntL-env/bin' >> ~/.bashrc
source ~/.bashrc

# 设置QEntL_HOME环境变量
echo 'export QEntL_HOME=/path/to/QEntL-env' >> ~/.bashrc
echo 'export QEntL_CONFIG=$QEntL_HOME/config' >> ~/.bashrc
source ~/.bashrc
```

### Windows

```batch
REM 临时设置
set PATH=%PATH%;C:\path\to\QEntL-env\bin

REM 永久设置（通过系统设置）
setx PATH "%PATH%;C:\path\to\QEntL-env\bin"
setx QEntL_HOME "C:\path\to\QEntL-env"
setx QEntL_CONFIG "%QEntL_HOME%\config"
```

## 常见问题

### 编译错误

如果遇到编译错误，请确保：

1. 使用的C编译器支持C99标准
2. 所有必需的头文件都能被找到
3. 系统中有足够的内存进行编译

常见错误解决：

```bash
# 检查头文件是否存在
ls -la QEntL-env/src/include

# 验证编译器版本
gcc --version

# 清理并重新构建
rm -rf QEntL-env/build/*
mkdir -p QEntL-env/build
cd QEntL-env/build
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build .
```

### 运行时错误

如果解释器可以编译但无法正常运行，请检查：

1. 动态链接库是否可用（如果有使用）
2. 是否有足够的权限执行文件
3. 文件路径是否正确

运行时错误排查：

```bash
# 检查库文件
ldd ./bin/qentl  # Linux
otool -L ./bin/qentl  # macOS
dumpbin /DEPENDENTS ./bin/qentl.exe  # Windows

# 运行调试模式
./bin/qentl --debug ./your_script.qentl

# 检查日志文件
cat ./logs/qentl_runtime.log
```

### 服务启动问题

1. **端口冲突**: 检查指定端口是否已被其他应用占用
   ```
   # Windows
   netstat -ano | findstr 5000
   
   # Linux/macOS
   lsof -i :5000
   ```

2. **权限问题**: 确保有足够权限运行服务
   ```
   # Linux/macOS
   sudo ./qentl --service=qsm --port=5000
   ```

3. **日志检查**: 查看日志文件了解详细错误信息
   ```
   # 通常日志位于
   QEntL-env/logs/qentl_service.log
   
   # 或使用日志查看命令
   ./bin/qentl log view --service=qsm --lines=100
   ```

4. **配置问题**: 检查配置文件是否正确
   ```
   # 验证配置文件
   ./bin/qentl config validate
   
   # 重置为默认配置
   ./bin/qentl config reset
   ```

## 性能优化

构建完成后，可以进行以下优化来提升QEntL环境的性能：

```bash
# 启用量子状态缓存
./bin/qentl config set --key=quantum.state.cache.enabled --value=true

# 设置纠缠处理线程数
./bin/qentl config set --key=entanglement.processor.threads --value=8

# 优化量子内存分配
./bin/qentl config set --key=quantum.memory.optimize --value=true

# 应用所有优化并重启服务
./bin/qentl service optimize
./bin/qentl service restart
```

## 贡献指南

如果您希望为QEntL环境做出贡献，请参考`CONTRIBUTING.md`文件获取详细信息。您可以参与以下方面的开发：

1. 核心解释器优化
2. 新量子算法实现
3. 标准库扩展
4. 开发工具改进
5. 文档和示例完善 