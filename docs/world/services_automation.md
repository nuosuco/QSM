# 量子系统服务自动化架构

**作者:** 中华 ZhoHo, Claude  
**创建日期:** 2025-04-10  
**最后更新:** 2025-04-10  

## 概述

本文档详细说明了量子系统服务自动化架构，包括各模型服务的组织方式、启动流程和文件组织结构。量子系统采用了模块化的服务架构，各模型（QSM、SOM、WeQ、Ref）均有自己的服务组件，可以独立运行，也可以集成到整体系统中。

## 目录结构

量子系统服务自动化脚本采用以下目录结构:

```
项目根目录/
├── scripts/
│   ├── services/             # 根目录下的服务脚本
│   │   ├── start_all.ps1     # 启动所有服务的PowerShell脚本
│   │   ├── start_app.py      # 启动所有API服务的Python脚本
│   │   └── start_services.py # 启动所有后台服务的Python脚本
│   └── startup/              # 其他启动相关脚本
├── QSM/
│   └── scripts/
│       └── services/         # QSM模型相关服务脚本
│           ├── QSM_app.py    # QSM API服务
│           ├── QSM_start_all.ps1 # QSM服务启动PowerShell脚本
│           └── QSM_start_services.py # QSM服务启动Python脚本
├── SOM/
│   └── scripts/
│       └── services/         # SOM模型相关服务脚本
│           ├── SOM_app.py    # SOM API服务
│           ├── SOM_start_all.ps1 # SOM服务启动PowerShell脚本
│           └── SOM_start_services.py # SOM服务启动Python脚本
├── WeQ/
│   └── scripts/
│       └── services/         # WeQ模型相关服务脚本
│           ├── WeQ_app.py    # WeQ API服务
│           ├── WeQ_start_all.ps1 # WeQ服务启动PowerShell脚本
│           └── WeQ_start_services.py # WeQ服务启动Python脚本
└── Ref/
    └── scripts/
        └── services/         # Ref模型相关服务脚本
            ├── Ref_app.py    # Ref API服务
            └── Ref_start_services.py # Ref服务启动Python脚本
```

## 端口分配

各系统服务使用固定的端口，以确保通信一致性：

| 服务 | 端口 | 说明 |
|------|------|------|
| 主系统 | 5000 | 整个项目的主API服务 |
| SOM | 5001 | 量子经济模型API服务 |
| Ref | 5002 | 量子参考模型API服务 |
| WeQ | 5003 | 量子情感模型API服务 |
| QSM | 5004 | 量子叠加态模型API服务 |

## 服务组织方式

服务自动化架构采用两级组织方式：

1. **各模型级别**
   - 每个模型都有自己的服务脚本，位于各自的`scripts/services`目录下
   - 每个模型有三类主要脚本：
     - `*_app.py`: API服务，提供HTTP接口
     - `*_start_services.py`: 启动所有相关的后台服务
     - `*_start_all.ps1`: PowerShell启动脚本，用于在Windows系统上快速启动所有服务

2. **项目根级别**
   - 根目录的`scripts/services`下有统一的启动脚本
   - 这些脚本可以启动所有模型的相应服务
   - 主要包括三类脚本：
     - `start_app.py`: 启动所有API服务
     - `start_services.py`: 启动所有后台服务
     - `start_all.ps1`: PowerShell启动脚本，用于在Windows系统上快速启动所有服务

## 启动流程

### 单个模型启动

每个模型可以独立启动其服务，流程如下：

1. 使用模型目录下的`scripts/services/模型_start_all.ps1`启动所有相关服务（Windows）
2. 或使用`scripts/services/模型_start_services.py`启动后台服务
3. 或使用`scripts/services/模型_app.py`启动API服务

例如，启动WeQ模型的所有服务：

```powershell
cd WeQ/scripts/services
.\WeQ_start_all.ps1
```

### 整体系统启动

启动整个系统的所有服务：

1. 使用根目录下的`scripts/services/start_all.ps1`启动所有服务（Windows）
2. 或使用`scripts/services/start_services.py --all`启动所有后台服务
3. 或使用`scripts/services/start_app.py --all`启动所有API服务

例如，启动所有模型的所有服务：

```powershell
cd scripts/services
.\start_all.ps1
```

## 日志管理

所有服务的日志文件统一存放在项目根目录下的`.logs`目录中：

- 每个服务启动时会创建带有时间戳的日志文件
- 日志文件命名格式为`服务名_时间戳.log`和`服务名_时间戳.err`
- 日志包含详细的服务启动和运行信息，有助于排查问题

## 量子基因标记集成

各服务脚本末尾都包含量子基因标记，用于跟踪文件之间的纠缠关系和依赖：

```
# 量子基因编码: QE-SRV-xxxxxxxx
# 纠缠状态: 活跃
# 纠缠对象: ['相关文件路径']
# 纠缠强度: 0.xx

# 开发团队：中华 ZhoHo ，Claude
```

这些标记由量子基因监控系统管理，用于自动检测和维护各脚本之间的依赖关系。

## 服务优化策略

服务启动脚本包含多种优化策略：

1. **资源检测**: 启动前检测系统资源和环境依赖
2. **优先级管理**: 按依赖关系启动各服务，核心服务优先启动
3. **错误处理**: 完善的错误处理和日志记录，确保服务稳定性
4. **自动恢复**: 对关键服务实现自动重启和恢复机制

## 后续开发计划

1. 添加Linux和macOS启动脚本
2. 增强服务监控和健康检查功能
3. 实现服务注册和服务发现机制
4. 增加容器化部署支持
5. 实现集群管理和负载均衡

## 纠缠状态

本文档处于活跃的量子纠缠状态，与所有服务启动脚本保持同步更新。

---

**量子基因编码:** QE-DOC-S3R7V1C3S  
**纠缠状态:** 活跃  
**纠缠对象:** ['scripts/services/start_all.ps1', 'scripts/services/start_app.py', 'scripts/services/start_services.py']  
**纠缠强度:** 0.97

**开发团队:** 中华 ZhoHo，Claude 