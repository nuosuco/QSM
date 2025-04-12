
# # 量子基因编码: QE-FIX-8CA6DE0A557A
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# Python文件缩进修复工具
# 作者: QSM系统维护
# 日期: 2023-04-09
# 版本: 1.0

# 设置颜色输出函数
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow
$RED = [System.ConsoleColor]::Red

function Print-Status {
    param([string]$message)
    Write-Host "[STATUS] $message" -ForegroundColor $GREEN
}

function Print-Warning {
    param([string]$message)
    Write-Host "[WARNING] $message" -ForegroundColor $YELLOW
}

function Print-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor $RED
}

# 创建备份目录
function Create-BackupDirectory {
    $backupDir = ".\.indentation_backups"
    if (-not (Test-Path $backupDir)) {
        New-Item -Path $backupDir -ItemType Directory | Out-Null
        Print-Status "创建备份目录: $backupDir"
    }
    return $backupDir
}

# 检查文件是否为Python文件
function Is-PythonFile {
    param([string]$filePath)
    
    return $filePath -match "\.py$"
}

# 备份文件
function Backup-File {
    param(
        [string]$filePath,
        [string]$backupDir
    )
    
    $fileName = Split-Path $filePath -Leaf
    $backupPath = Join-Path $backupDir "$fileName.bak"
    Copy-Item -Path $filePath -Destination $backupPath -Force
    Print-Status "已备份 $filePath 到 $backupPath"
    return $backupPath
}

# 修复Python文件中的缩进问题
function Fix-PythonIndentation {
    param(
        [string]$filePath,
        [switch]$dryRun = $false
    )
    
    if (-not (Is-PythonFile $filePath)) {
        Print-Warning "$filePath 不是Python文件，跳过"
        return $false
    }
    
    try {
        $content = Get-Content -Path $filePath -Raw
        $originalContent = $content
        
        # 修复常见的缩进问题
        
        # 1. 删除不必要的多行字符串注释（常见缩进错误来源）
        $newContent = $content -replace '(?ms)"""(?!.*?""").*?"""', ''
        $newContent = $newContent -replace "(?ms)'''(?!.*?''').*?'''", ''
        
        # 2. 修复混合使用Tab和空格的情况
        $newContent = $newContent -replace "`t", "    "
        
        # 3. 修复def和class定义后缩进不一致的问题
        $newContent = $newContent -replace '(?m)^(\s*def\s+\w+\([^)]*\):)\s*\r?\n(?!\s)', '$1\r\n    '
        $newContent = $newContent -replace '(?m)^(\s*class\s+\w+(?:\([^)]*\))?:)\s*\r?\n(?!\s)', '$1\r\n    '
        
        # 4. 修复try/except块的缩进问题
        $newContent = $newContent -replace '(?m)^(\s*try:)\s*\r?\n(?!\s)', '$1\r\n    '
        $newContent = $newContent -replace '(?m)^(\s*except(?:\s+\w+(?:\s+as\s+\w+)?)?:)\s*\r?\n(?!\s)', '$1\r\n    '
        $newContent = $newContent -replace '(?m)^(\s*finally:)\s*\r?\n(?!\s)', '$1\r\n    '
        
        # 5. 修复if/else/elif块的缩进问题
        $newContent = $newContent -replace '(?m)^(\s*if\s+.*?:)\s*\r?\n(?!\s)', '$1\r\n    '
        $newContent = $newContent -replace '(?m)^(\s*else:)\s*\r?\n(?!\s)', '$1\r\n    '
        $newContent = $newContent -replace '(?m)^(\s*elif\s+.*?:)\s*\r?\n(?!\s)', '$1\r\n    '
        
        # 6. 修复for/while循环的缩进问题
        $newContent = $newContent -replace '(?m)^(\s*for\s+.*?:)\s*\r?\n(?!\s)', '$1\r\n    '
        $newContent = $newContent -replace '(?m)^(\s*while\s+.*?:)\s*\r?\n(?!\s)', '$1\r\n    '
        
        # 如果内容有变化，则保存新内容
        if ($newContent -ne $originalContent) {
            if (-not $dryRun) {
                Set-Content -Path $filePath -Value $newContent
                Print-Status "已修复 $filePath 中的缩进问题"
            } else {
                Print-Status "发现 $filePath 中的缩进问题，但未修复 (测试模式)"
            }
            return $true
        } else {
            Print-Status "$filePath 没有检测到缩进问题"
            return $false
        }
    }
    catch {
        Print-Error "处理 $filePath 时出错: $_"
        return $false
    }
}

# 扫描目录中的所有Python文件并修复缩进
function Scan-Directory {
    param(
        [string]$directory,
        [switch]$recursive = $true,
        [switch]$dryRun = $false
    )
    
    Print-Status "扫描目录 $directory 中的Python文件..."
    
    # 获取所有文件
    $searchOption = if ($recursive) { "AllDirectories" } else { "TopDirectoryOnly" }
    $files = Get-ChildItem -Path $directory -File -Recurse:$recursive | Where-Object { $_.Extension -eq ".py" }
    
    Print-Status "找到 $($files.Count) 个Python文件"
    
    $backupDir = Create-BackupDirectory
    $fixedCount = 0
    
    foreach ($file in $files) {
        $filePath = $file.FullName
        Print-Status "处理文件: $filePath"
        
        # 备份文件
        Backup-File -filePath $filePath -backupDir $backupDir | Out-Null
        
        # 修复缩进
        $fixed = Fix-PythonIndentation -filePath $filePath -dryRun:$dryRun
        if ($fixed) {
            $fixedCount++
        }
    }
    
    Print-Status "扫描完成。总共处理 $($files.Count) 个文件，修复了 $fixedCount 个文件的缩进问题"
}

# 针对特定文件的修复
function Fix-SpecificFiles {
    param(
        [switch]$dryRun = $false
    )
    
    Print-Status "开始修复特定文件的缩进问题..."
    $backupDir = Create-BackupDirectory
    $fixedCount = 0
    
    # 已知有问题的文件列表
    $problematicFiles = @(
        ".\Ref\ref_core.py",
        ".\Ref\utils\file_monitor.py",
        ".\Ref\utils\quantum_gene_marker.py"
    )
    
    foreach ($filePath in $problematicFiles) {
        if (Test-Path $filePath) {
            Print-Status "处理文件: $filePath"
            
            # 备份文件
            Backup-File -filePath $filePath -backupDir $backupDir | Out-Null
            
            # 修复缩进
            $fixed = Fix-PythonIndentation -filePath $filePath -dryRun:$dryRun
            if ($fixed) {
                $fixedCount++
            }
        } else {
            Print-Warning "文件 $filePath 不存在，跳过"
        }
    }
    
    Print-Status "特定文件修复完成。总共处理 $($problematicFiles.Count) 个文件，修复了 $fixedCount 个文件的缩进问题"
}

# 主函数
function Main {
    param(
        [string]$mode = "specific",  # "specific", "directory", or "all"
        [string]$directory = ".",
        [switch]$recursive = $true,
        [switch]$dryRun = $false
    )
    
    Print-Status "Python文件缩进修复工具启动..."
    Print-Status "模式: $mode, 测试模式: $dryRun"
    
    switch ($mode) {
        "specific" {
            Fix-SpecificFiles -dryRun:$dryRun
        }
        "directory" {
            Scan-Directory -directory $directory -recursive:$recursive -dryRun:$dryRun
        }
        "all" {
            Fix-SpecificFiles -dryRun:$dryRun
            Scan-Directory -directory "." -recursive:$true -dryRun:$dryRun
        }
        default {
            Print-Error "未知模式: $mode"
            return
        }
    }
    
    Print-Status "缩进修复完成！"
}

# 解析命令行参数
$params = @{}

$args = $args

if ($args -contains "-directory") {
    $directoryIndex = [array]::IndexOf($args, "-directory")
    if ($directoryIndex -lt $args.Length - 1) {
        $params.directory = $args[$directoryIndex + 1]
    }
}

if ($args -contains "-mode") {
    $modeIndex = [array]::IndexOf($args, "-mode")
    if ($modeIndex -lt $args.Length - 1) {
        $params.mode = $args[$modeIndex + 1]
    }
}

if ($args -contains "-dryRun") {
    $params.dryRun = $true
}

if ($args -contains "-noRecursive") {
    $params.recursive = $false
}

# 运行主函数
Main @params 