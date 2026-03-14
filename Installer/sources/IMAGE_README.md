# QEntL 安装镜像文件说明

## install.qim (QEntL安装镜像)
**大小**: 约 4.2GB  
**格式**: QEntL压缩镜像格式  
**描述**: 包含完整的QEntL系统文件

### 镜像内容结构
```
install.qim 内容:
├── System/                   # 系统核心 (2.8GB)
│   ├── Compiler/             # 编译器组件 (800MB)
│   ├── VM/                   # 虚拟机组件 (600MB) 
│   ├── Kernel/               # 系统内核 (1.2GB)
│   └── Runtime/              # 运行时环境 (200MB)
├── Models/                   # 四大模型 (1.0GB)
│   ├── QSM/                  # 量子状态模型 (300MB)
│   ├── WeQ/                  # 微量子模型 (250MB)
│   ├── SOM/                  # 同步组织模型 (250MB)
│   └── Ref/                  # 引用模型 (200MB)
├── Programs/                 # 预装程序 (200MB)
├── Users/                    # 用户目录系统 (50MB)
│   ├── Default/              # 默认用户目录
│   └── Templates/            # 用户模板
├── Templates/                # 项目模板 (100MB)
└── docs/                     # 文档文件 (100MB)
```

## boot.qim (引导镜像)
**大小**: 约 500MB  
**格式**: QEntL引导镜像格式  
**描述**: 系统引导和恢复工具

### 引导镜像内容
```
boot.qim 内容:
├── bootmgr/                  # 引导管理器
├── recovery/                 # 系统恢复工具
├── diagnostics/              # 诊断工具
├── drivers/                  # 基础驱动程序
└── firmware/                 # 固件更新
```

## 镜像特性

### 压缩技术
- **算法**: QEntL量子压缩算法
- **压缩比**: 平均 65%
- **解压速度**: 支持并行解压
- **完整性检查**: SHA-256 + 量子校验和

### 安全特性
- **数字签名**: 使用QEntL量子签名
- **防篡改**: 量子纠缠完整性保护
- **加密**: AES-256 + 量子密钥分发

### 安装优化
- **增量安装**: 支持差分更新
- **并行安装**: 多线程文件复制
- **智能检测**: 自动硬件兼容性检查
- **回滚支持**: 安装失败自动回滚
- **用户环境**: 自动创建用户目录和配置文件

## 创建安装镜像

### 工具命令
```bash
# 创建完整安装镜像
qentl-image-builder create --type full --source "C:\QEntL" --output install.qim

# 创建引导镜像  
qentl-image-builder create --type boot --source "C:\QEntL\System\Boot" --output boot.qim

# 验证镜像完整性
qentl-image-verifier verify install.qim boot.qim

# 镜像信息查看
qentl-image-info install.qim
```

### 构建脚本
```powershell
# build-installer-images.ps1
param(
    [string]$SourcePath = "C:\QEntL-Build",
    [string]$OutputPath = "C:\QEntL-Installer\sources"
)

Write-Host "构建QEntL安装镜像..." -ForegroundColor Green

# 创建安装镜像
Write-Host "正在创建install.qim..." -ForegroundColor Yellow
& qentl-image-builder create `
    --type full `
    --source "$SourcePath" `
    --output "$OutputPath\install.qim" `
    --compression quantum `
    --verify-integrity

# 创建引导镜像
Write-Host "正在创建boot.qim..." -ForegroundColor Yellow  
& qentl-image-builder create `
    --type boot `
    --source "$SourcePath\System\Boot" `
    --output "$OutputPath\boot.qim" `
    --compression standard `
    --sign-image

Write-Host "镜像构建完成！" -ForegroundColor Green
```

## 镜像使用

### 安装程序集成
```qentl
// 在安装程序中使用镜像
function extractInstallImage(imagePath: String, targetPath: String) -> Result {
    let extractor = QImageExtractor.new();
    
    // 验证镜像签名
    if (!extractor.verifySignature(imagePath)) {
        return Error("镜像签名验证失败");
    }
    
    // 检查磁盘空间
    let requiredSpace = extractor.getRequiredSpace(imagePath);
    if (!checkDiskSpace(targetPath, requiredSpace)) {
        return Error("磁盘空间不足");
    }
    
    // 并行解压安装
    let result = extractor.extractParallel(
        source: imagePath,
        destination: targetPath,
        progressCallback: updateProgress
    );
    
    return result;
}
```

### 系统恢复使用
```bash
# 从引导镜像恢复系统
qentl-recovery restore --boot-image boot.qim --target "C:\QEntL"

# 部分系统修复
qentl-recovery repair --component kernel --boot-image boot.qim
```

---

*注意: 实际的.qim文件需要使用qentl-image-builder工具创建*
