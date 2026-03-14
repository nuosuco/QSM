# QEntL 用户目录系统

## 📁 用户目录结构

QEntL操作系统提供完整的用户目录管理系统，为每个用户提供独立的工作环境。

### 🏠 默认用户目录: `/Users/Default/`

```
Users/
├── Default/                    # 默认用户目录
│   ├── Documents/              # 用户文档
│   │   ├── QEntL_Projects/     # QEntL项目文件
│   │   ├── Scripts/            # 用户脚本
│   │   └── Templates/          # 文档模板
│   ├── Programs/               # 用户安装的程序
│   │   ├── Custom/             # 自定义程序
│   │   └── Extensions/         # QEntL扩展
│   ├── Settings/               # 用户设置
│   │   ├── preferences.qentl   # 用户偏好设置
│   │   ├── environment.qentl   # 环境变量
│   │   └── quantum_config.qentl # 量子计算配置
│   ├── Data/                   # 用户数据
│   │   ├── Cache/              # 缓存文件
│   │   ├── Temp/               # 临时文件
│   │   └── Quantum/            # 量子数据存储
│   └── Desktop/                # 桌面环境
│       ├── Shortcuts/          # 快捷方式
│       └── Widgets/            # 桌面小部件
└── Templates/                  # 用户模板目录
    ├── NewUser/                # 新用户模板
    └── UserProfile/            # 用户配置文件模板
```

## 🎯 功能特性

### 1. 多用户支持
- **独立环境**: 每个用户拥有完全独立的工作环境
- **权限管理**: 基于量子安全的权限控制系统
- **资源隔离**: 用户间的量子态和计算资源完全隔离

### 2. 用户配置
- **个性化设置**: 支持完全自定义的用户界面
- **量子偏好**: 用户特定的量子计算偏好设置
- **环境变量**: 用户级别的环境配置

### 3. 数据管理
- **智能存储**: 自动分类和管理用户数据
- **量子加密**: 用户数据采用量子加密保护
- **备份同步**: 支持用户数据的自动备份和同步

## 🔧 用户管理命令

### 创建新用户
```qentl
user create <username> [--template=default|advanced|minimal]
```

### 切换用户
```qentl
user switch <username>
```

### 用户设置
```qentl
user config set <key> <value>
user config get <key>
user config list
```

### 权限管理
```qentl
user permissions grant <username> <permission>
user permissions revoke <username> <permission>
user permissions list <username>
```

## 🌟 默认用户配置

### 环境变量
```qentl
QENTL_USER_HOME=/Users/Default
QENTL_USER_DOCS=/Users/Default/Documents
QENTL_USER_PROGRAMS=/Users/Default/Programs
QENTL_USER_SETTINGS=/Users/Default/Settings
QENTL_USER_DATA=/Users/Default/Data
QENTL_USER_DESKTOP=/Users/Default/Desktop
```

### 量子计算配置
```qentl
QUANTUM_MEMORY_POOL=64MB
QUANTUM_ENTANGLEMENT_LIMIT=1024
QUANTUM_SUPERPOSITION_STATES=16
QUANTUM_COHERENCE_TIME=1000ms
```

## 🚀 快速开始

### 1. 初始化用户环境
```bash
cd /Users/Default
qentl user init
```

### 2. 创建第一个QEntL项目
```bash
cd Documents/QEntL_Projects
qentl project create hello_quantum
```

### 3. 配置个人设置
```bash
qentl user config set theme quantum_dark
qentl user config set quantum_cores 4
```

## 🔒 安全特性

### 量子安全
- **量子密钥**: 每个用户拥有独特的量子密钥
- **纠缠认证**: 基于量子纠缠的身份认证
- **态坍塌保护**: 防止量子态被恶意观测

### 数据保护
- **加密存储**: 所有用户数据自动加密
- **访问控制**: 细粒度的文件访问权限
- **审计日志**: 完整的用户操作审计记录

## 📚 相关文档

- [用户管理指南](../docs/System/User_Management_Guide.md)
- [权限系统说明](../docs/System/Permission_System.md)
- [量子安全架构](../docs/System/Quantum_Security.md)
- [多用户环境配置](../docs/System/Multi_User_Setup.md)

---
**创建时间**: 2025年6月19日  
**QEntL版本**: v1.0.0  
**用户系统版本**: v1.0.0
