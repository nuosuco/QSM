# QEntL环境

这是QEntL（Quantum Entanglement Language）语言环境的实现代码。QEntL是一种专为量子计算和量子纠缠概念设计的特殊编程语言，旨在提供完全独立、自主可控的量子编程体验。

## 目录结构

```
QEntL-env/
├── bin/              # 可执行文件目录
├── docs/             # 内部文档
├── gcc编译器/        # GCC环境安装程序
├── src/              # 源代码
│   ├── compiler/     # 编译器实现
│   ├── interpreter/  # 解释器实现
│   ├── runtime/      # 运行时实现
│   ├── stdlib/       # 标准库
│   └── tools/        # 开发工具
├── tests/            # 测试用例和框架
└── examples/         # 示例程序
```

## 快速开始

### 1. 安装GCC编译环境

在Windows系统上，需要安装MSYS2提供GCC环境支持：

1. 运行 `QEntL-env\gcc编译器\msys2-installer.exe`
2. 按照安装向导完成安装
3. 安装完成后，更新MSYS2系统：
   ```
   pacman -Syu
   ```
4. 安装GCC工具链：
   ```
   pacman -S mingw-w64-x86_64-toolchain
   pacman -S make
   pacman -S mingw-w64-x86_64-cmake
   ```
5. 将GCC添加到系统PATH：
   ```
   设置环境变量，添加 C:\msys64\mingw64\bin
   ```

更多详细步骤，请参考 `docs/BUILDING.md` 文档。

### 2. 编译QEntL引擎

```
cd QEntL-env/src
mkdir build
cd build
cmake ..
cmake --build .
cmake --install .
```

### 3. 启动QEntL服务

完成编译后，可以通过以下方式启动QEntL环境：

#### 方式一：使用启动脚本

在项目根目录中运行启动脚本：
```
start_qentl_ui.bat
```

该脚本将启动所有必要的服务，包括：
- QSM服务 (端口5000)
- WeQ服务 (端口5001)
- SOM服务 (端口5002)
- Ref服务 (端口5003)
- World UI服务 (端口3000)

#### 方式二：手动启动各服务

您也可以手动启动各个服务：

```
cd QEntL-env/bin
qentl --service=qsm --port=5000
qentl --service=weq --port=5001
qentl --service=som --port=5002
qentl --service=ref --port=5003
qentl --service=world --port=3000
```

启动后，访问 http://localhost:3000 使用QEntL环境。

## 详细文档

更多详细信息，请参考以下文档：
- 构建指南：`docs/BUILDING.md`
- 语言规范：`docs/LANGUAGE.md`
- API参考：`docs/API.md`
- 示例教程：`examples/README.md`

## 许可证

遵循项目整体许可协议。 