# QEntL环境构建指南

本文档详细说明了如何从源代码构建QEntL语言环境。

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

## 手动构建（推荐）

### Linux/macOS

```bash
# 进入源代码目录
cd QEntL-env/src

# 编译解释器
gcc -o ../bin/qentl interpreter/qentl_interpreter.c -I. -std=c99 -Wall -O2

# 添加可执行权限
chmod +x ../bin/qentl
```

### Windows

```batch
REM 进入源代码目录
cd QEntL-env\src

REM 使用Visual Studio编译（命令行版本）
cl /Fe..\bin\qentl.exe interpreter\qentl_interpreter.c /I. /W4 /O2

REM 或使用MinGW/gcc
gcc -o ..\bin\qentl.exe interpreter\qentl_interpreter.c -I. -std=c99 -Wall -O2
```

## 使用CMake构建

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

## 测试构建

```bash
# 运行版本检查
./bin/qentl --version

# 运行测试用例
./bin/qentl ./tests/basic_test.qentl
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
```

### Windows

```batch
REM 临时设置
set PATH=%PATH%;C:\path\to\QEntL-env\bin

REM 永久设置（通过系统设置）
setx PATH "%PATH%;C:\path\to\QEntL-env\bin"
```

## 常见问题

### 编译错误

如果遇到编译错误，请确保：

1. 使用的C编译器支持C99标准
2. 所有必需的头文件都能被找到
3. 系统中有足够的内存进行编译

### 运行时错误

如果解释器可以编译但无法正常运行，请检查：

1. 动态链接库是否可用（如果有使用）
2. 是否有足够的权限执行文件
3. 文件路径是否正确

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
   ```

## 贡献指南

如果您希望为QEntL环境做出贡献，请参考`CONTRIBUTING.md`文件获取详细信息。 