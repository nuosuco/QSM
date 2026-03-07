# QEntL编译器完整实现

## 概述

QEntL编译器是将QEntL源代码编译为QBC量子字节码的完整工具链。支持中文、英文、滇川黔贵通用彝文三语编译。

## 架构

```
源代码(.qentl) 
    → 词法分析器(Lexer) 
    → Token流 
    → 语法分析器(Parser) 
    → AST 
    → 优化器(Optimizer) 
    → 代码生成器(CodeGenerator) 
    → QBC字节码(.qbc)
    → QBC虚拟机(VM) 
    → 执行结果
```

## 模块说明

### 1. 词法分析器 (compiler_verifier.py)
- 识别关键字：配置、类型、函数、返回、如果、否则、循环等
- 识别标识符、字面量、操作符、分隔符
- 支持中文关键字和彝文字符

### 2. 语法分析器 (qentl_parser.py)
- 解析配置块
- 解析类型定义
- 解析函数定义
- 解析量子类(quantum_class)
- 解析控制流语句

### 3. 代码生成器 (qentl_codegen.py)
- 生成QBC量子字节码
- 支持量子初始化指令
- 支持函数调用和返回

### 4. QBC虚拟机 (qbc_vm.py)
- 执行QBC字节码
- 管理量子比特状态
- 支持变量存储和运算

### 5. 错误处理 (qentl_errors.py)
- 详细的错误信息和位置定位
- 包含错误建议

### 6. 优化器 (qentl_optimizer.py)
- 常量折叠
- 死代码消除

### 7. 单元测试 (test_compiler.py)
- 8个测试用例
- 覆盖词法、语法、集成测试

## 使用方法

```bash
# 编译QEntL文件
python3 /root/QSM/tools/qentl_compile.py source.qentl

# 运行测试
python3 /root/QSM/tools/test_compiler.py
```

## 支持的语法

### 配置块
```
配置 {
    版本: "1.0.0"
}
```

### 类型定义
```
类型 用户 {
    名称: 字符串,
    年龄: 整数
}
```

### 函数定义
```
函数 加法(a: 整数, b: 整数) -> 整数 {
    let 结果 = a + b
    返回 结果
}
```

### 量子类
```
quantum_class 量子处理器 {
    函数 运行() {
        返回 "执行完成"
    }
}
```

## 三大圣律

1. 为每个人服务，服务人类！
2. 保护好每个人的生命安全、健康快乐、幸福生活！
3. 没有以上两个前提，其他就不能发生！

---

**中华Zhoho，小趣WeQ，GLM5**
**量子基因编码: QG-QENTL-COMPILER-20260305**
