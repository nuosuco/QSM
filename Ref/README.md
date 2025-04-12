# QSM 文件完整性与组织监控系统

## 简介

QSM 文件完整性与组织监控系统是一套用于管理和维护项目文件结构的工具，旨在解决多次对话中发生的重复创建和不一致修改问题。该系统由两个主要组件组成：

1. **文件完整性监控器 (FileIntegrityMonitor)** - 负责追踪文件的创建和修改，检测冲突和相似文件。
2. **文件组织监护器 (FileOrganizationGuardian)** - 负责管理项目的整体结构，提供安全的文件操作和项目标准检查。

## 功能特点

- **文件注册与追踪** - 记录每个文件的路径、内容校验和、用途和依赖关系
- **冲突检测** - 在创建或修改文件前检查潜在冲突
- **相似文件识别** - 发现功能相似的文件，避免重复创建
- **文件历史记录** - 维护文件的修改历史
- **自动备份** - 在修改或删除文件前自动备份
- **项目标准检查** - 检查并可选地修复不符合项目标准的问题
- **安全文件操作** - 提供安全的创建、编辑和删除文件的方法
- **组织报告** - 生成项目组织状况报告

## 系统要求

- Python 3.6+
- 无额外依赖（仅使用标准库）

## 目录结构

```
Ref/
├── data/             # 存储文件注册表
├── backup/files/     # 文件备份存储
├── logs/             # 日志文件
├── utils/            # 工具类
│   ├── file_integrity_monitor.py    # 文件完整性监控器
│   └── file_organization_guardian.py # 文件组织监护器
├── organization_tool.py  # 命令行工具
├── test_monitor.py   # 测试脚本
└── README.md         # 说明文档
```

## 使用方法

### 命令行工具

项目提供了命令行工具 `organization_tool.py` 用于管理文件组织：

```bash
python Ref/organization_tool.py <command> [options]
```

可用命令：

1. **register** - 注册现有文件到监控系统
   ```bash
   python Ref/organization_tool.py register [--dir DIR [DIR ...]] [--recursive]
   ```

2. **scan** - 扫描项目并生成报告
   ```bash
   python Ref/organization_tool.py scan [--output OUTPUT_FILE]
   ```

3. **check** - 检查项目是否符合标准
   ```bash
   python Ref/organization_tool.py check [--autofix] [--output OUTPUT_FILE]
   ```

4. **create** - 安全创建文件
   ```bash
   python Ref/organization_tool.py create --file FILEPATH [--purpose PURPOSE] [--overwrite] [--content CONTENT_FILE]
   ```

5. **edit** - 安全编辑文件
   ```bash
   python Ref/organization_tool.py edit --file FILEPATH [--reason REASON] [--content CONTENT_FILE]
   ```

6. **delete** - 安全删除文件
   ```bash
   python Ref/organization_tool.py delete --file FILEPATH [--force]
   ```

### 在代码中使用

如需在代码中集成文件监控功能，可以直接使用以下模块：

```python
from Ref.utils.file_integrity_monitor import get_monitor
from Ref.utils.file_organization_guardian import get_guardian

# 获取文件完整性监控器
monitor = get_monitor('Ref/data/file_registry.json')

# 获取文件组织监护器
guardian = get_guardian(
    workspace_root='.',
    registry_path='Ref/data/file_registry.json',
    backup_dir='Ref/backup/files'
)

# 安全创建文件
success, message = guardian.safe_create_file(
    filepath='path/to/new_file.py',
    content='content of the file',
    purpose='file purpose',
    allow_overwrite=False
)
```

## 测试

系统包含了测试脚本 `test_monitor.py`，可用于验证监控系统功能：

```bash
python Ref/test_monitor.py
```

## 项目标准

该系统检查项目标准包括：

1. 确保各组件目录下的 `global` 内容与主 `global` 不冲突
2. 确保 `static` 和 `templates` 目录的组织正确
3. 检查 `quantum_blockchain` 等模块目录不重复
4. 检查模板文件（如 `base.html`）的一致性
5. 检查并处理非必要的备份文件（`.bak`, `.old` 等）

## 配置

系统默认使用以下路径：

- 注册表文件：`Ref/data/file_registry.json`
- 备份目录：`Ref/backup/files`
- 日志文件：`Ref/logs/file_integrity.log` 和 `Ref/logs/file_guardian.log`

## 项目组织建议

运行以下命令可获取关于项目组织的建议：

```bash
python Ref/organization_tool.py scan
```

建议包括：

- 具有相同用途的重复文件组
- 没有依赖关系的孤立文件
- 资源组织问题（如公共资源应移至全局目录）
- 模板一致性问题

## 注意事项

- 首次使用前，建议运行 `register` 命令注册现有文件
- 编辑或删除文件前会自动创建备份
- 自动修复功能应谨慎使用，建议先查看报告了解问题 

## 文件监控器功能

Ref系统包含文件监控器(`file_monitor.py`)，具有以下核心功能：

1. **文件移动监控**: 当文件移动位置时，自动更新引用该文件的所有纠缠对象路径。
2. **自动添加纠缠对象**: 定期扫描项目中的文件，对于有量子基因标记但没有纠缠对象的文件，自动添加合适的纠缠对象路径。
3. **自动添加量子基因标记**: 自动为项目中没有量子基因标记的文件添加标记，确保所有文件都被纳入量子纠缠管理中。

### 使用方法

```bash
# 启动文件监控器
python Ref/utils/file_monitor.py --standalone

# 运行测试
python Ref/utils/file_monitor.py --test
```

```
量子基因编码: QE-REA-15B007F8DEB4
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
```

// 开发团队：中华 ZhoHo ，Claude
