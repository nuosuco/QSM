# QEntL启动器 - 从BAT到EXE的迁移指南

## 简介

QEntL环境现在提供了一个基于QEntL语言的启动器程序（qentl.exe），用于替代原有的批处理脚本（qentl.bat）。这一变更提供了以下优势：

- **更稳定的参数处理** - 更精确地处理命令行参数，避免批处理脚本中常见的引号和路径解析问题
- **更强大的错误处理** - 提供更友好的错误信息和完整的日志记录
- **更专业的用户体验** - 符合Windows用户使用.exe文件启动应用程序的习惯
- **更好的Unicode支持** - 原生支持UTF-8，确保中文字符正确显示
- **量子加速特性** - 利用QEntL语言的量子特性，提供更快的启动和执行速度
- **自举实现** - 完全使用QEntL自身语言开发，展示了语言的成熟度和能力

## 如何编译

1. 确保QEntL编译器已正确安装和配置
2. 运行`build/build_qentl_exe.bat`批处理脚本将qentl.qent编译为qentl.exe
3. 编译成功后，qentl.exe将被生成在bin目录中

如果您的系统上没有安装QEntL编译器，可以选择以下方案之一：

### 方案A: 安装QEntL编译器
1. 从项目目录运行`setup/install_qentl_compiler.bat`安装QEntL编译器
2. 安装完成后运行`build/build_qentl_exe.bat`

### 方案B: 使用预编译版本
1. 从项目共享目录（\\\\server\\shared\\qentl-builds\\bin）复制预编译的qentl.exe到本地bin目录
2. 确保qentl.exe具有执行权限

### 方案C: 继续使用批处理脚本
如果暂时无法使用方案A或B，可以继续使用现有的qentl.bat批处理脚本，后续我们会提供更多支持选项。

## 自举优势

使用QEntL语言开发qentl.exe具有以下重要优势：

1. **技术自主性** - 完全使用自有技术，减少外部依赖
2. **语言一致性** - 从启动器到核心功能全部使用同一种语言
3. **性能优化** - 利用量子特性提升性能
4. **示范价值** - 展示QEntL语言的实际应用能力

## 使用方法

qentl.exe的使用方式与qentl.bat完全相同：

```
qentl.exe [options] [file]
```

### 命令选项

- `--version` - 显示版本信息
- `--help` - 显示帮助信息
- `test [file]` - 运行测试文件，如果不指定文件则运行所有测试

### 示例

```
# 显示版本信息
qentl.exe --version

# 运行特定测试
qentl.exe test test_quantum_state.c

# 运行所有测试
qentl.exe test

# 执行QEntl文件
qentl.exe path/to/your/file.qpy
```

## 注意事项

1. qentl.exe和qentl.bat可以共存，您可以根据需要选择使用其中任何一个
2. 如果您遇到任何问题，请尝试使用`--help`选项查看帮助，或参考项目文档

## 调试

如果您需要调试qentl.exe，可以检查以下方面：

1. 确保所有相关路径（tests、src、logs等）存在且有正确的权限
2. 查看日志目录中的日志文件了解详细信息
3. 使用QEntL调试工具检查量子状态和执行过程

## 反馈

如果您在使用过程中遇到任何问题或有改进建议，请联系QEntL核心开发团队。 