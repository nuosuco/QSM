# QSM项目管理工具使用指南

## 概述

> 量子基因编码: QG-QSM01-DOC-20250401213356-887F94-ENT2777


QSM项目管理工具是一套用于管理量子叠加态模型(QSM)项目的实用工具集。这些工具帮助您：

1. 自动备份项目中的所有文件，防止意外修改或丢失
2. 统一所有前端页面的导航栏，确保用户体验一致性
3. 在修改前后安全地管理项目文件
4. 创建整个项目的完整备份

## 可用工具

### 1. 文件备份工具 (backup_files.py)

自动为项目文件创建带时间戳的备份副本，或创建完整项目备份。

**使用方法:**
```bash
# 备份所有项目文件
python backup_files.py

# 备份特定文件
python backup_files.py path/to/file1.py path/to/file2.html

# 只备份前端文件
python backup_files.py --frontend

# 只备份Python文件
python backup_files.py --python

# 备份所有项目文件（明确指定）
python backup_files.py --all

# 创建完整项目备份（创建备份目录）
python backup_files.py --full

# 备份特定类型的文件
python backup_files.py --extensions .py,.html,.js
```

### 2. 导航栏统一工具 (unify_nav.py)

从首页提取导航栏并应用到其他页面，确保统一的用户界面。

**使用方法:**
```bash
# 统一所有页面的导航栏
python unify_nav.py

# 将导航栏应用到特定页面
python unify_nav.py static/api_client.html templates/dashboard.html
```

### 3. 项目管理界面 (manage_project.py)

提供交互式管理界面，集成所有项目管理功能。

**使用方法:**
```bash
# 启动交互式管理界面
python manage_project.py

# 直接备份所有项目文件
python manage_project.py --backup-all

# 直接备份所有Python文件
python manage_project.py --backup-py

# 直接备份所有前端文件
python manage_project.py --backup-frontend

# 创建完整项目备份
python manage_project.py --full-backup

# 统一所有导航栏
python manage_project.py --unify-nav
```

## 备份功能详解

### 单文件备份
为单个文件创建带时间戳的备份副本。例如：`file.py` → `file.20250331_120000.py`

### 特定类型文件备份
可以备份特定类型的文件：
- Python文件 (.py)
- HTML文件 (.html)
- JavaScript文件 (.js)
- CSS文件 (.css)
- JSON文件 (.json)
- 其他自定义类型

### 完整项目备份
创建一个包含整个项目的备份目录，排除不必要的文件和目录（如 .git、node_modules、env 等）。

## 最佳实践

1. **在修改前备份**：任何时候修改项目文件前，先运行备份工具
   ```bash
   python backup_files.py path/to/file.py
   ```

2. **定期全量备份**：每周或重大更新前对项目进行完整备份
   ```bash
   python manage_project.py --full-backup
   ```

3. **保持导航栏一致**：修改首页导航栏后，运行统一工具应用到其他页面
   ```bash
   python unify_nav.py
   ```

4. **使用管理界面**：不确定操作时，使用交互式界面安全地管理文件
   ```bash
   python manage_project.py
   ```

5. **定期清理旧备份**：使用管理界面的清理功能删除不需要的旧备份文件
   ```bash
   # 在交互式界面中选择选项 9
   python manage_project.py
   ```

## 注意事项

- 备份文件使用原文件名加时间戳保存，不会覆盖原文件
- 完整项目备份会创建一个新目录，包含项目的所有重要文件
- 导航栏统一工具会先备份目标文件，再应用修改
- 首次运行时会自动安装所需依赖（beautifulsoup4）

## 技术支持

如有问题或建议，请联系项目维护团队或在项目仓库提交issue。 