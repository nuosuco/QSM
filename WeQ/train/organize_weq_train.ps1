# PowerShell脚本：组织WeQ训练目录下的文件
# 将训练相关文件移动到对应的子目录中

# 进入WeQ/train目录
cd E:\model\QSM\WeQ\train

# 定义文件映射规则
$file_mappings = @{
    # 帮助文件
    ".*helper.*\.py$" = "helpers"
    
    # 模型文件
    ".*model.*\.py$" = "models"
    
    # 数据处理文件
    ".*data.*\.py$" = "data"
}

# 需要保留在根目录的主要文件
$main_files = @(
    "weq_train.py",
    "weq_train_seq.py",
    "weq_train_par.py"
)

# 创建一个备份目录
$backup_dir = "..\backup\train_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -Path $backup_dir -ItemType Directory -Force | Out-Null
Write-Host "创建备份目录: $backup_dir" -ForegroundColor Green

# 确保子目录存在
@("helpers", "models", "data") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -Path $_ -ItemType Directory -Force | Out-Null
        Write-Host "创建目录: $_" -ForegroundColor Yellow
    }
}

# 获取当前目录下的所有Python文件
$py_files = Get-ChildItem -Path "." -Filter "*.py" -File

foreach ($file in $py_files) {
    # 检查是否是主要文件（不需要移动）
    if ($main_files -contains $file.Name) {
        Write-Host "保留主文件: $($file.Name)" -ForegroundColor Cyan
        continue
    }
    
    # 确定目标目录
    $target_dir = $null
    foreach ($pattern in $file_mappings.Keys) {
        if ($file.Name -match $pattern) {
            $target_dir = $file_mappings[$pattern]
            break
        }
    }
    
    # 如果没有匹配的目标目录，默认为helpers
    if (-not $target_dir) {
        $target_dir = "helpers"
    }
    
    $target_path = Join-Path -Path $target_dir -ChildPath $file.Name
    
    # 检查目标文件是否已存在
    if (Test-Path $target_path) {
        Write-Host "目标文件已存在，跳过: $target_path" -ForegroundColor Yellow
        continue
    }
    
    # 备份文件
    Copy-Item -Path $file.FullName -Destination (Join-Path -Path $backup_dir -ChildPath $file.Name)
    Write-Host "备份文件: $($file.Name) -> $backup_dir\$($file.Name)" -ForegroundColor Cyan
    
    # 移动文件
    try {
        # 读取文件内容
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        
        # 创建新文件
        Set-Content -Path $target_path -Value $content -Encoding UTF8
        
        # 删除原文件
        Remove-Item -Path $file.FullName
        
        Write-Host "移动文件: $($file.Name) -> $target_dir\$($file.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "移动文件失败: $($file.Name) -> $target_dir\$($file.Name)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host "`nWeQ训练文件组织完成!" -ForegroundColor Green 