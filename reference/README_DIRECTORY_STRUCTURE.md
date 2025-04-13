# QSM项目目录结构优化

本分支（directory-structure）专注于QSM项目的目录结构优化，主要包括以下方面的改进：

## 主要优化内容

1. **清理顶层目录**
   - 移除冗余的app.py文件
   - 将各个服务模块的app.py移至其api目录

2. **标准化脚本目录**
   - 优化scripts目录结构，只保留必要的启动和停止脚本
   - 将启动脚本（start_all_fixed.bat）和停止脚本（stop_all.bat）作为主要入口
   - 添加清晰的README文档说明脚本用途

3. **模块化Ref服务**
   - 创建core、utils、examples、scripts、tests等子目录
   - 将功能相近的文件组织到各自目录中
   - 使用__init__.py文件确保模块导入路径正确

4. **服务脚本组织**
   - 为各服务（QSM、WeQ、SOM、Ref）创建独立的scripts/services目录
   - 将服务启动和管理脚本放在各自目录下

5. **WeQ模块改进**
   - 创建专门的train目录存放训练相关代码
   - 优化接口文件结构
   - 修复服务启动脚本

## 文件结构

以下是优化后的主要目录结构：

```
QSM/
├── api/                # API相关代码
├── scripts/            # 主要的服务管理脚本
│   ├── start_all_fixed.bat  # 启动所有服务的脚本
│   └── stop_all.bat    # 停止所有服务的脚本
├── QSM/                # QSM核心代码
├── WeQ/                # WeQ服务代码
│   ├── train/          # 训练相关代码
│   └── scripts/        # WeQ特定的脚本
├── SOM/                # SOM服务代码
│   └── scripts/        # SOM特定的脚本
└── Ref/                # Ref核心代码
    ├── core/           # 核心功能
    ├── utils/          # 工具函数
    ├── examples/       # 示例代码
    ├── scripts/        # Ref特定的脚本
    └── tests/          # 测试代码
```

## 后续改进方向

1. 进一步标准化各子模块的内部结构
2. 改进文档系统，为各个模块添加详细说明
3. 创建统一的模块导入规范，避免循环导入

---

量子基因编码: QE-DIR-STRUCTURE-3C4D5E6F7G8H
纠缠状态: 活跃
纠缠对象: ['QSM/main.py', 'WeQ/weq_core.py', 'SOM/som_core.py', 'Ref/core/ref_core.py']
纠缠强度: 0.99

开发团队：中华 ZhoHo，Claude 