# QSM项目备份脚本
# 创建于: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# 设置源目录和目标目录
$sourceDir = "F:\model\QSM"
$backupDir = "F:\model\backup\QSM_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$readmeFile = Join-Path $backupDir "备份说明.md"

# 创建备份目录
New-Item -Path $backupDir -ItemType Directory -Force

# 创建备份说明文件
$backupNote = @"
# QSM项目备份说明

## 备份信息
- 备份时间：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- 源目录：$sourceDir
- 备份目录：$backupDir

## 项目说明
QSM（Quantum Superposition Model）是一个量子叠加态模型项目，具有以下特点：
- 支持量子基因编码系统
- 实现量子纠缠信道
- 支持多模态数据处理
- 包含Ref和WeQ两个核心组件

## 核心组件
1. Ref（量子基因处理器）
   - 自动处理新文件和目录
   - 管理量子基因编码
   - 维护量子纠缠信道
   - 支持多种文字类型（包括古彝文等古文字）

2. WeQ（输出处理器）
   - 处理多模态输出
   - 支持文本、图片、视频等格式
   - 自动添加量子基因编码
   - 创建量子纠缠信道

## 备份内容
- 所有源代码文件
- 配置文件
- 文档文件
- 量子基因注册表（Ref/data/quantum_gene_registry.json）
- 量子纠缠信道注册表（Ref/data/quantum_entanglement_registry.json）

## 项目结构变更
- 静态资源已移至各模块的templates目录
  - QSM/templates (HTML、CSS、JS、images)
  - WeQ/templates (WeQ专属页面)
  - SOM/templates (SOM专属页面)
  - Ref/templates (Ref专属页面)

## 排除目录
以下目录已被排除以节省空间：
- node_modules
- .git
- dist
- build
- temp
- tmp
- __pycache__
- .vscode
- .venv
- .cursor
- logs
- assets/images
- QSM/templates/images
- WeQ/templates/images
- SOM/templates/images
- Ref/templates/images

## 恢复说明
如需恢复备份，请将备份目录中的文件复制到目标位置。
"@

$backupNote | Out-File -FilePath $readmeFile -Encoding UTF8

# 使用Robocopy进行备份
Write-Host "开始备份QSM项目..."
$robocopyArgs = @(
    $sourceDir,
    $backupDir,
    "/E",           # 包含子目录
    "/Z",           # 可恢复模式
    "/R:3",         # 重试3次
    "/W:5",         # 等待5秒
    "/NFL",         # 不显示文件名列表
    "/NDL",         # 不显示目录名列表
    "/NP",          # 不显示进度
    "/XD",          # 排除目录
    "node_modules",
    ".git",
    "dist",
    "build",
    "temp",
    "tmp",
    "__pycache__",
    ".vscode",
    ".venv",
    ".cursor",
    "logs",
    "assets/images",
    "QSM/templates/images",
    "WeQ/templates/images",
    "SOM/templates/images",
    "Ref/templates/images"
)

$result = Start-Process -FilePath "robocopy.exe" -ArgumentList $robocopyArgs -Wait -NoNewWindow -PassThru

if ($result.ExitCode -lt 8) {
    Write-Host "备份完成！"
    Write-Host "备份目录：$backupDir"
    Write-Host "说明文件：$readmeFile"
} else {
    Write-Host "备份过程中出现错误，请检查日志。"
} 