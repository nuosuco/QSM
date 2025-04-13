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

## 测试构建

```bash
# 运行版本检查
./bin/qentl --version

# 运行测试用例
./bin/qentl ./tests/basic_test.qentl
```

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

## 贡献指南

如果您希望为QEntL环境做出贡献，请参考`CONTRIBUTING.md`文件获取详细信息。 