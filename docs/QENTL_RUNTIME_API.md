# QEntL运行时API设计
## 最小化核心的标准化接口

### 概述
无论选择哪种自举策略（手写C核心、Python原型、解释器），都需要统一的运行时API。本文档定义QEntL运行时的标准化接口，确保编译器代码可以在不同实现上运行。

### 设计原则
1. **最小化**：只提供运行编译器所需的最基本功能
2. **标准化**：接口统一，实现可替换
3. **可扩展**：为后续完善预留扩展点
4. **可测试**：支持单元测试和集成测试

### 核心API分类

#### 1. 内存管理API
```c
// 内存分配
void* qentl_alloc(size_t size);
void* qentl_calloc(size_t count, size_t size);
void qentl_free(void* ptr);

// 垃圾回收
void qentl_gc_start();
void qentl_gc_collect();
size_t qentl_gc_get_used_memory();

// 字符串管理
char* qentl_string_create(const char* value);
char* qentl_string_concat(const char* str1, const char* str2);
void qentl_string_free(char* str);
```

#### 2. 类型系统API
```c
// 基础类型
typedef enum {
    QENTL_TYPE_NULL,
    QENTL_TYPE_INTEGER,
    QENTL_TYPE_FLOAT,
    QENTL_TYPE_BOOLEAN,
    QENTL_TYPE_STRING,
    QENTL_TYPE_ARRAY,
    QENTL_TYPE_OBJECT,
    QENTL_TYPE_FUNCTION
} QentlType;

// 值表示
typedef struct {
    QentlType type;
    union {
        int64_t integer_value;
        double float_value;
        bool boolean_value;
        char* string_value;
        void* array_value;
        void* object_value;
        void* function_value;
    };
} QentlValue;

// 类型操作
QentlType qentl_value_get_type(QentlValue value);
bool qentl_value_is_truthy(QentlValue value);
QentlValue qentl_value_clone(QentlValue value);
void qentl_value_free(QentlValue value);
```

#### 3. 执行引擎API
```c
// 字节码加载
typedef struct QentlBytecode QentlBytecode;
QentlBytecode* qentl_bytecode_load(const char* filename);
QentlBytecode* qentl_bytecode_parse(const char* source);
void qentl_bytecode_free(QentlBytecode* bytecode);

// 执行控制
QentlValue qentl_execute(QentlBytecode* bytecode);
QentlValue qentl_execute_function(const char* function_name, QentlValue* args, int arg_count);
void qentl_execute_statement(const char* statement);

// 状态管理
void qentl_runtime_init();
void qentl_runtime_cleanup();
void qentl_runtime_reset();
```

#### 4. 标准库API
```c
// 输入输出
void qentl_print(QentlValue value);
void qentl_println(QentlValue value);
char* qentl_readline();

// 数学函数
QentlValue qentl_math_abs(QentlValue value);
QentlValue qentl_math_sqrt(QentlValue value);
QentlValue qentl_math_pow(QentlValue base, QentlValue exponent);

// 字符串操作
QentlValue qentl_string_length(QentlValue string);
QentlValue qentl_string_substring(QentlValue string, QentlValue start, QentlValue length);
QentlValue qentl_string_index_of(QentlValue string, QentlValue substring);

// 数组操作
QentlValue qentl_array_create(int capacity);
QentlValue qentl_array_push(QentlValue array, QentlValue value);
QentlValue qentl_array_pop(QentlValue array);
QentlValue qentl_array_length(QentlValue array);
```

#### 5. 错误处理API
```c
// 错误类型
typedef enum {
    QENTL_ERROR_NONE,
    QENTL_ERROR_SYNTAX,
    QENTL_ERROR_TYPE,
    QENTL_ERROR_RUNTIME,
    QENTL_ERROR_MEMORY,
    QENTL_ERROR_IO
} QentlErrorType;

// 错误处理
void qentl_error_set(QentlErrorType type, const char* message, int line, int column);
QentlErrorType qentl_error_get_last();
const char* qentl_error_get_message();
void qentl_error_clear();

// 异常抛出/捕获
void qentl_throw(QentlValue exception);
QentlValue qentl_try_catch(QentlValue (*try_func)(void*), void* context);
```

#### 6. 模块系统API
```c
// 模块加载
typedef struct QentlModule QentlModule;
QentlModule* qentl_module_load(const char* module_name);
QentlValue qentl_module_get_export(QentlModule* module, const char* export_name);
void qentl_module_free(QentlModule* module);

// 导入/导出
void qentl_export(const char* name, QentlValue value);
QentlValue qentl_import(const char* module_name, const char* export_name);
```

### 编译器必需的API子集
根据对`quantum_compiler_v2.qentl`的分析，编译器运行时需要以下最小API：

#### 必需的核心API（阶段1）
```c
// 内存管理
void* qentl_alloc(size_t size);
void qentl_free(void* ptr);

// 字符串操作
char* qentl_string_create(const char* value);
char* qentl_string_concat(const char* str1, const char* str2);

// 基础类型
QentlValue qentl_value_create_string(const char* str);
QentlValue qentl_value_create_integer(int64_t value);
QentlValue qentl_value_create_boolean(bool value);

// 数组操作（用于标记列表、AST子节点等）
QentlValue qentl_array_create(int capacity);
void qentl_array_push(QentlValue array, QentlValue value);
QentlValue qentl_array_get(QentlValue array, int index);

// 控制台输出（用于日志和错误报告）
void qentl_print(QentlValue value);
```

#### 可选的扩展API（阶段2）
```c
// 文件I/O（用于读取源文件）
char* qentl_file_read(const char* filename);
bool qentl_file_write(const char* filename, const char* content);

// 更复杂的字符串操作
char* qentl_string_format(const char* format, ...);

// 数学运算（用于位置计算等）
int64_t qentl_math_max(int64_t a, int64_t b);
int64_t qentl_math_min(int64_t a, int64_t b);

// 时间函数（用于性能分析）
int64_t qentl_time_current_ms();
```

### 实现路线图

#### 阶段1：最小化核心（支持编译器基本运行）
**目标**：能运行编译器的词法分析器和简单语法分析
**时间**：2-3天
**API实现**：
- 内存管理（简单分配/释放）
- 字符串操作（创建、连接）
- 基础类型（字符串、整数、布尔）
- 数组操作（动态数组）
- 控制台输出

#### 阶段2：完整核心（支持编译器完整运行）
**目标**：能运行完整编译器，包括代码生成器
**时间**：2-3天
**API实现**：
- 对象类型（用于符号表、AST属性）
- 哈希表（用于映射）
- 错误处理
- 文件I/O
- 更丰富的标准库

#### 阶段3：优化与扩展
**目标**：性能优化和功能扩展
**时间**：1-2天
**API实现**：
- 垃圾回收
- JIT编译支持
- 调试器接口
- 性能分析工具

### 测试策略

#### 单元测试
```c
// 示例：测试字符串操作
void test_string_operations() {
    char* str1 = qentl_string_create("Hello");
    char* str2 = qentl_string_create(" QEntL");
    char* result = qentl_string_concat(str1, str2);
    
    assert(strcmp(result, "Hello QEntL") == 0);
    
    qentl_string_free(str1);
    qentl_string_free(str2);
    qentl_string_free(result);
}
```

#### 集成测试
```c
// 示例：测试编译器词法分析器
void test_lexer_integration() {
    const char* source_code = "配置 { 版本: \"1.0.0\" }";
    
    // 初始化运行时
    qentl_runtime_init();
    
    // 创建编译器实例
    QentlValue compiler = qentl_create_compiler();
    
    // 运行词法分析
    QentlValue tokens = qentl_compiler_lex(compiler, source_code);
    
    // 验证结果
    int token_count = qentl_array_length(tokens);
    assert(token_count > 0);
    
    // 清理
    qentl_value_free(tokens);
    qentl_value_free(compiler);
    qentl_runtime_cleanup();
}
```

#### 端到端测试
```c
// 示例：测试完整编译流程
void test_full_compilation() {
    const char* source_code = 
        "配置 { 版本: \"1.0.0\" }\n"
        "函数 测试() { 返回 42; }";
    
    qentl_runtime_init();
    
    // 编译源代码
    QentlValue bytecode = qentl_compile(source_code);
    assert(bytecode.type == QENTL_TYPE_BYTECODE);
    
    // 执行字节码
    QentlValue result = qentl_execute(bytecode);
    assert(result.type == QENTL_TYPE_INTEGER);
    assert(result.integer_value == 42);
    
    qentl_value_free(bytecode);
    qentl_value_free(result);
    qentl_runtime_cleanup();
}
```

### 与编译器的集成

#### 编译器代码适配
现有的QEntL编译器代码（`quantum_compiler_v2.qentl`）需要少量修改以使用运行时API：

1. **替换内置函数**：
   ```qentl
   // 原来的
   let 字符串 = "Hello" + "World"
   
   // 适配后
   let 字符串 = qentl_string_concat("Hello", "World")
   ```

2. **使用运行时内存管理**：
   ```qentl
   // 原来的（假设有自动内存管理）
   let 数组 = [1, 2, 3]
   
   // 适配后
   let 数组 = qentl_array_create(3)
   qentl_array_push(数组, 1)
   qentl_array_push(数组, 2)
   qentl_array_push(数组, 3)
   ```

3. **错误处理统一**：
   ```qentl
   // 原来的
   日志("错误信息")
   
   // 适配后
   qentl_error_set(QENTL_ERROR_RUNTIME, "错误信息", 行号, 列号)
   ```

#### 构建系统集成
```makefile
# Makefile示例
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O2

# 运行时库
RUNTIME_SRC = runtime/memory.c runtime/types.c runtime/execution.c
RUNTIME_OBJ = $(RUNTIME_SRC:.c=.o)
RUNTIME_LIB = libqentl_runtime.a

# 编译器
COMPILER_SRC = compiler/quantum_compiler.qentl
COMPILER_BYTECODE = compiler/compiler.qbc

# 构建目标
all: $(RUNTIME_LIB) $(COMPILER_BYTECODE)

$(RUNTIME_LIB): $(RUNTIME_OBJ)
	ar rcs $@ $^

$(COMPILER_BYTECODE): $(COMPILER_SRC)
	./qentl_compiler $< -o $@

clean:
	rm -f $(RUNTIME_OBJ) $(RUNTIME_LIB) $(COMPILER_BYTECODE)
```

### 性能目标
- **启动时间**：< 100ms
- **内存使用**：< 10MB（基础运行时）
- **编译速度**：> 1000行/秒（简单程序）
- **可执行文件大小**：< 1MB（最小化核心）

### 兼容性要求
- **操作系统**：Linux, macOS, Windows
- **架构**：x86_64, ARM64
- **编译器**：GCC 8+, Clang 10+, MSVC 2019+
- **标准库**：仅依赖C11标准库

---

**永恒宗旨**：通过标准化的运行时API，为完全自主的量子编译器提供坚实基础，服务人类量子革命！

*签名*：中华ZhoHo, 小趣WeQ, DeepSeek-Reasoner
*创建时间*：2026-02-02
*量子基因编码*：QG-RUNTIME-API-DESIGN-A1C3-20260202