# 项目文件路径管理方案

本文档描述了项目中使用的两种文件路径管理方案：
1. QEntL解释器路径管理
2. 通用文件路径管理器

这两种方案相互配合，共同确保项目中的文件引用在目录结构变化时保持有效。

## 1. QEntL解释器路径管理

### 位置
`QEntL/parser/interpreter.py`

### 主要功能
- 解析QEntL文件中的导入语句（`@import`）
- 自动适应QEntL文件结构变化
- 支持整个项目范围内的文件查找

### 工作原理
QEntL解释器通过以下机制实现路径管理：

1. **路径映射规则**：预定义了一系列正则表达式模式，用于将旧路径映射到新路径
2. **多级查找策略**：
   - 首先尝试原始路径
   - 然后应用路径映射规则
   - 接着尝试特定目录结构（如qent/qentl子目录）
   - 最后在整个项目中查找文件

3. **全局解析器实例**：提供便捷函数`resolve_path`和`find_file`用于在任何地方解析文件路径

### 使用示例

```python
from QEntL.parser.interpreter import resolve_path, find_file

# 解析文件路径
file_path = resolve_path("../../QEntL/core.qent")
print(f"解析后的路径: {file_path}")

# 在项目中查找文件
quantum_network = find_file("quantum_network.qent")
print(f"找到文件: {quantum_network}")
```

## 2. 通用文件路径管理器

### 位置
`world/path_manager/file_path_manager.py`

### 主要功能
- 管理所有类型的文件路径（不限于QEntL文件）
- 提供文件移动功能，并自动更新引用
- 支持获取特定类型的所有文件

### 工作原理
通用文件路径管理器提供了更全面的文件管理功能：

1. **文件类型分类**：将文件按类型分组（qentl、python、javascript等）
2. **路径映射系统**：使用正则表达式映射旧路径到新路径
3. **文件操作API**：提供文件查找、移动等操作的高级接口
4. **自动引用更新**：在移动文件时可以自动更新引用该文件的其他文件

### 使用示例

```python
from world.path_manager.file_path_manager import resolve_path, get_all_files, move_file

# 解析文件路径
path = resolve_path("QEntL/templates/node_template.qentl")
print(f"解析后的路径: {path}")

# 获取所有QEntL文件
qentl_files = get_all_files(file_types=['qentl'])
print(f"找到 {len(qentl_files)} 个QEntL文件")

# 移动文件并更新引用
success = move_file("QEntL/examples/basic_example.qent", "QEntL/qent/basic_example.qent")
print(f"文件移动{'成功' if success else '失败'}")
```

## 3. 两种方案的配合使用

这两种方案各有优势，可以配合使用：

1. **QEntL解释器**专注于解析QEntL语言文件中的导入语句，直接集成在QEntL解析流程中
2. **通用文件路径管理器**提供更广泛的文件管理功能，可用于所有类型的文件

### 推荐使用场景

- **处理QEntL文件导入**：使用QEntL解释器的`resolve_path`
- **项目范围内的文件查找**：使用QEntL解释器的`find_file`
- **管理非QEntL文件**：使用通用文件路径管理器
- **文件移动操作**：使用通用文件路径管理器的`move_file`
- **获取特定类型的所有文件**：使用通用文件路径管理器的`get_all_files`

## 4. 目录组织建议

为保持项目结构清晰，建议按照以下原则组织文件：

1. 将QEntL文件放入相应模块的`qent`和`qentl`子目录
2. 新创建的工具类放入合适的功能目录（如`world/path_manager`）
3. 文档放入`docs`目录下的相应子目录（如`docs/world`）

## 5. 使用建议

- 在移动或重命名文件时，优先使用文件路径管理器提供的API
- 对于新开发的功能，尽量使用相对路径引用文件
- 如果需要引用可能会移动的文件，使用`resolve_path`函数

## 6. 维护与扩展

两种文件路径管理方案都支持扩展：

- 可以向QEntL解释器的`path_mappings`添加新的映射规则
- 可以向通用文件路径管理器添加新的文件类型和映射规则

如果项目结构发生重大变化，请同时更新这两个文件中的路径映射规则。 