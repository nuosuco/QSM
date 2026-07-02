# QEntL 安装介质完整指南

## 📦 安装包结构

QEntL安装包采用类似Windows安装介质的标准结构，确保用户熟悉的安装体验：

```
QEntL-Installer/
├── autorun.inf               # 自动运行配置
├── setup.bat                 # 安装向导 (图形界面入口)
├── qentl_installer.qentl     # 主安装程序
├── qentl_bootmgr.c          # 引导管理器源码
├── sources/                  # 核心安装文件
│   ├── install.qim          # QEntL安装镜像 (4.2GB)
│   ├── boot.qim             # 引导镜像 (500MB)
│   ├── IMAGE_README.md      # 镜像说明文档
│   └── lang/                # 多语言支持
│       ├── zh-CN/           # 简体中文
│       ├── zh-TW/           # 繁体中文
│       ├── en-US/           # 英文
│       └── ja-JP/           # 日文
├── support/                  # 支持工具
│   ├── drivers/             # 硬件驱动
│   │   ├── quantum/         # 量子硬件驱动
│   │   ├── network/         # 网络驱动
│   │   └── storage/         # 存储驱动
│   └── tools/               # 部署工具
│       ├── diagnostic.exe   # 系统诊断工具
│       ├── recovery.exe     # 恢复工具
│       └── migration.exe    # 迁移工具
└── docs/                    # 安装文档
    ├── installation_guide.md
    ├── system_requirements.md
    └── troubleshooting.md
```

## 🚀 安装方式

### 方式1: 图形界面安装 (推荐)
```bash
# 双击运行安装向导
setup.bat

# 或者从命令行启动
.\setup.bat
```

### 方式2: 命令行安装
```bash
# 静默安装到默认位置
.\qentl_installer.exe /S

# 自定义安装位置
.\qentl_installer.exe /S /D=C:\MyQEntL

# 完整安装
.\qentl_installer.exe /FULL /D=C:\QEntL

# 开发环境安装
.\qentl_installer.exe /DEV /D=C:\QEntL

# 服务器安装
.\qentl_installer.exe /SERVER /D=C:\QEntL

# 集群主节点安装
.\qentl_installer.exe /CLUSTER /MASTER /D=C:\QEntL

# 集群工作节点安装
.\qentl_installer.exe /CLUSTER /WORKER /MASTER=192.168.1.10 /D=C:\QEntL
```

### 方式3: 网络安装
```bash
# 从网络位置安装
.\qentl_installer.exe /NETWORK /SOURCE=\\server\qentl-share

# 从HTTP源安装
.\qentl_installer.exe /NETWORK /SOURCE=https://releases.qentl.org/v1.2.0/
```

## 🔧 安装选项详解

### 基本安装类型
- `/FULL` - 完整安装 (默认，包含所有组件)
- `/MINIMAL` - 最小安装 (仅核心组件)
- `/CUSTOM` - 自定义安装 (需要GUI界面)
- `/DEV` - 开发环境 (包含开发工具和调试器)
- `/SERVER` - 服务器安装 (无GUI，优化性能)
- `/CLUSTER` - 集群安装 (分布式部署)

### 系统配置选项
- `/SERVICE` - 安装系统服务
- `/DESKTOP` - 创建桌面快捷方式
- `/STARTMENU` - 创建开始菜单项
- `/PATH` - 添加到系统环境变量
- `/QUANTUM` - 启用量子加速功能
- `/DEBUG` - 安装调试组件

### 集群配置选项
- `/MASTER` - 配置为主节点
- `/WORKER` - 配置为工作节点
- `/MASTER=<IP>` - 指定主节点IP地址
- `/CLUSTER=<name>` - 指定集群名称
- `/REPLICAS=<n>` - 设置副本数量

### 网络安装选项
- `/NETWORK` - 启用网络安装模式
- `/SOURCE=<path>` - 指定安装源路径
- `/CACHE=<path>` - 设置本地缓存路径
- `/OFFLINE` - 离线安装模式

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 10 (1909+), Windows Server 2019+
- **处理器**: Intel Core i5 或 AMD Ryzen 5
- **内存**: 8GB RAM
- **存储**: 10GB 可用空间 (SSD推荐)
- **网络**: 千兆以太网 (集群部署需要)

### 推荐配置
- **操作系统**: Windows 11, Windows Server 2022
- **处理器**: Intel Core i7 或 AMD Ryzen 7
- **内存**: 16GB+ RAM
- **存储**: 50GB+ 可用空间 (NVMe SSD)
- **显卡**: 支持量子计算加速的GPU
- **网络**: 10Gb以太网 (大规模集群)

### 量子硬件要求 (可选)
- **量子处理器**: IBM Quantum, Google Quantum AI, IonQ
- **量子比特数**: 最少32个量子比特
- **相干时间**: >100μs
- **门保真度**: >99%

## 🛠️ 安装后配置

### 验证安装
```bash
# 检查版本
qentl --version

# 系统诊断
qentl-diagnostic --all

# 硬件检测
qentl-diagnostic --hardware

# 量子功能测试
qentl-diagnostic --quantum
```

### 首次配置
```bash
# 初始化用户环境
qentl-init --user

# 配置开发环境
qentl-config --dev-env

# 生成量子密钥
qentl-keygen --quantum

# 创建示例项目
qentl-create-project --template hello-quantum
```

### 服务管理
```bash
# 启动服务
net start QEntLKernel
net start QEntLCompiler

# 停止服务
net stop QEntLKernel
net stop QEntLCompiler

# 服务状态
sc query QEntLKernel
sc query QEntLCompiler
```

## 🔄 升级和迁移

### 版本升级
```bash
# 检查更新
qentl-updater check

# 下载并安装更新
qentl-updater install

# 回滚到上一版本
qentl-updater rollback
```

### 系统迁移
```bash
# 导出当前配置
qentl-export --config --output config-backup.qentl

# 导出用户数据
qentl-export --userdata --output userdata-backup.qentl

# 导出项目
qentl-export --projects --output projects-backup.qentl

# 在新系统上导入
qentl-import --config config-backup.qentl
qentl-import --userdata userdata-backup.qentl
qentl-import --projects projects-backup.qentl
```

## 🗑️ 卸载

### 图形界面卸载
1. 控制面板 → 程序和功能
2. 选择"QEntL Quantum Programming System"
3. 点击"卸载"

### 命令行卸载
```bash
# 标准卸载
"C:\QEntL\uninstall.exe"

# 完全卸载 (删除所有数据)
"C:\QEntL\uninstall.exe" /FULL

# 静默卸载
"C:\QEntL\uninstall.exe" /S

# 保留用户数据
"C:\QEntL\uninstall.exe" /KEEP-USERDATA
```

## 🚨 故障排除

### 常见安装问题

#### 权限不足
```bash
# 解决方案：以管理员身份运行
runas /user:Administrator "setup.bat"
```

#### 磁盘空间不足
```bash
# 检查磁盘空间
dir C:\ /-c
# 清理临时文件
cleanmgr /sageset:1
```

#### 网络问题
```bash
# 检查网络连接
ping releases.qentl.org
# 配置代理
qentl-installer.exe /PROXY=http://proxy.company.com:8080
```

#### 兼容性问题
```bash
# 兼容性检查
qentl-compatibility-check.exe
# 强制兼容模式
qentl-installer.exe /FORCE-COMPATIBILITY
```

### 安装日志
```bash
# 查看安装日志
type "%TEMP%\QEntL-Install.log"

# 详细调试日志
qentl-installer.exe /DEBUG-LOG
```

### 技术支持
- **官方文档**: https://docs.qentl.org
- **技术支持**: https://support.qentl.org
- **社区论坛**: https://community.qentl.org
- **GitHub Issues**: https://github.com/qentl/qentl/issues

---

*安装完成后，请参考[用户手册](../docs/user/README.md)开始使用QEntL*
