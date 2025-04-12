# QSM项目自动备份脚本
# 版本：1.0
# 日期：2023-04-09
# 功能：每小时备份QSM项目到指定位置，保留最近72个备份

# 颜色定义，用于输出信息
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$RED = [ConsoleColor]::Red

# 输出函数
function Print-Status {
    param (
        [string]$Message
    )
    Write-Host "[状态] $Message" -ForegroundColor $GREEN
}

function Print-Warning {
    param (
        [string]$Message
    )
    Write-Host "[警告] $Message" -ForegroundColor $YELLOW
}

function Print-Error {
    param (
        [string]$Message
    )
    Write-Host "[错误] $Message" -ForegroundColor $RED
}

# 配置部分
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$projectRoot = "E:\model\QSM"
$backupRoot = "E:\QSM_Backups"
$backupDir = Join-Path -Path $backupRoot -ChildPath "backup_$timestamp"
$logDir = Join-Path -Path $backupRoot -ChildPath "logs"
$logFile = Join-Path -Path $logDir -ChildPath "backup_$timestamp.log"
$maxBackups = 72 # 保留的最大备份数量

# 初始化
function Initialize-Backup {
    # 创建日志目录
    if (-not (Test-Path -Path $logDir)) {
        try {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
            Print-Status "创建日志目录: $logDir"
        } catch {
            Print-Error "创建日志目录失败: $_"
            exit 1
        }
    }

    # 创建备份根目录
    if (-not (Test-Path -Path $backupRoot)) {
        try {
            New-Item -Path $backupRoot -ItemType Directory -Force | Out-Null
            Print-Status "创建备份根目录: $backupRoot"
        } catch {
            Print-Error "创建备份根目录失败: $_"
            exit 1
        }
    }

    # 初始化日志
    try {
        $startTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$startTime] 开始QSM项目备份" | Out-File -FilePath $logFile -Encoding utf8
        "[$startTime] 项目路径: $projectRoot" | Out-File -FilePath $logFile -Append -Encoding utf8
        "[$startTime] 备份路径: $backupDir" | Out-File -FilePath $logFile -Append -Encoding utf8
    } catch {
        Print-Error "初始化日志失败: $_"
        exit 1
    }
}

# 执行备份
function Perform-Backup {
    Print-Status "开始备份QSM项目到 $backupDir"
    
    # 创建备份目录
    try {
        New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    } catch {
        Print-Error "创建备份目录失败: $_"
        $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$errorTime] 错误: 创建备份目录失败: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
        exit 1
    }
    
    # 要排除的目录和文件
    $excludeDirs = @(
        "__pycache__",
        ".pytest_cache",
        ".venv",
        "venv",
        "node_modules",
        ".git"
    )
    
    $excludeParams = $excludeDirs | ForEach-Object { "/xd `"$_`"" }
    $excludeParamsString = $excludeParams -join " "
    
    # 使用Robocopy进行备份
    try {
        $backupTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$backupTime] 开始使用Robocopy备份文件" | Out-File -FilePath $logFile -Append -Encoding utf8
        
        $robocopyArgs = @(
            "`"$projectRoot`"",
            "`"$backupDir`"",
            "/E",
            "/NP",
            "/R:3",
            "/W:3",
            "/MT:16",
            "/NFL",
            "/NDL"
        )
        
        # 添加排除参数
        foreach ($exclude in $excludeDirs) {
            $robocopyArgs += "/XD"
            $robocopyArgs += "`"$exclude`""
        }
        
        # 执行Robocopy
        $robocopyOutput = & robocopy $robocopyArgs
        $robocopyExitCode = $LASTEXITCODE
        
        # Robocopy退出码：0-7表示成功（不同级别的信息），8表示有错误
        if ($robocopyExitCode -lt 8) {
            $completeTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$completeTime] 备份完成，退出码: $robocopyExitCode" | Out-File -FilePath $logFile -Append -Encoding utf8
            Print-Status "QSM项目备份完成，退出码: $robocopyExitCode"
        } else {
            $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$errorTime] 备份失败，退出码: $robocopyExitCode" | Out-File -FilePath $logFile -Append -Encoding utf8
            Print-Error "备份失败，退出码: $robocopyExitCode"
        }
    } catch {
        Print-Error "备份过程中发生错误: $_"
        $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$errorTime] 错误: 备份过程中发生错误: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
        exit 1
    }
    
    # 验证备份
    try {
        $verifyTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$verifyTime] 开始验证备份" | Out-File -FilePath $logFile -Append -Encoding utf8
        
        # 检查几个关键文件是否存在
        $keyFiles = @(
            "Ref\ref_core.py",
            "Ref\utils\quantum_gene_marker.py",
            "world\static\js\world.js"
        )
        
        $allFilesExist = $true
        foreach ($file in $keyFiles) {
            $filePath = Join-Path -Path $backupDir -ChildPath $file
            if (-not (Test-Path -Path $filePath)) {
                $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                "[$errorTime] 警告: 关键文件未备份: $file" | Out-File -FilePath $logFile -Append -Encoding utf8
                Print-Warning "关键文件未备份: $file"
                $allFilesExist = $false
            }
        }
        
        if ($allFilesExist) {
            $verifyCompleteTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$verifyCompleteTime] 备份验证通过" | Out-File -FilePath $logFile -Append -Encoding utf8
            Print-Status "备份验证通过"
        } else {
            $verifyFailTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$verifyFailTime] 备份验证失败: 部分关键文件未备份" | Out-File -FilePath $logFile -Append -Encoding utf8
            Print-Warning "备份验证失败: 部分关键文件未备份"
        }
    } catch {
        Print-Error "验证备份时发生错误: $_"
        $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$errorTime] 错误: 验证备份时发生错误: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
    }
}

# 清理旧备份
function Clean-OldBackups {
    try {
        $backupDirs = Get-ChildItem -Path $backupRoot -Directory | Where-Object { $_.Name -like "backup_*" } | Sort-Object CreationTime
        $backupCount = $backupDirs.Count
        
        if ($backupCount -gt $maxBackups) {
            $toRemove = $backupCount - $maxBackups
            $dirsToRemove = $backupDirs | Select-Object -First $toRemove
            
            $cleanTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$cleanTime] 开始清理旧备份，将删除 $toRemove 个备份" | Out-File -FilePath $logFile -Append -Encoding utf8
            
            foreach ($dir in $dirsToRemove) {
                $dirPath = $dir.FullName
                "[$cleanTime] 删除旧备份: $dirPath" | Out-File -FilePath $logFile -Append -Encoding utf8
                Remove-Item -Path $dirPath -Recurse -Force
                Print-Status "已删除旧备份: $dirPath"
            }
            
            $cleanCompleteTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$cleanCompleteTime] 清理旧备份完成，已删除 $toRemove 个备份" | Out-File -FilePath $logFile -Append -Encoding utf8
            Print-Status "清理旧备份完成，已删除 $toRemove 个备份"
        } else {
            $cleanTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            "[$cleanTime] 当前备份数量 ($backupCount) 未超过最大限制 ($maxBackups)，无需清理" | Out-File -FilePath $logFile -Append -Encoding utf8
            Print-Status "当前备份数量 ($backupCount) 未超过最大限制 ($maxBackups)，无需清理"
        }
    } catch {
        Print-Error "清理旧备份时发生错误: $_"
        $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$errorTime] 错误: 清理旧备份时发生错误: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
    }
}

# 统计备份大小
function Get-BackupSize {
    try {
        $size = Get-ChildItem -Path $backupDir -Recurse -File | Measure-Object -Property Length -Sum
        $sizeInMB = [Math]::Round($size.Sum / 1MB, 2)
        
        $sizeTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$sizeTime] 备份大小: $sizeInMB MB" | Out-File -FilePath $logFile -Append -Encoding utf8
        Print-Status "备份大小: $sizeInMB MB"
        
        return $sizeInMB
    } catch {
        Print-Error "计算备份大小时发生错误: $_"
        $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$errorTime] 错误: 计算备份大小时发生错误: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
        return 0
    }
}

# 主函数
function Main {
    $startTime = Get-Date
    Print-Status "开始QSM项目自动备份 (时间: $startTime)"
    
    try {
        # 初始化
        Initialize-Backup
        
        # 执行备份
        Perform-Backup
        
        # 清理旧备份
        Clean-OldBackups
        
        # 获取备份大小
        $backupSize = Get-BackupSize
        
        # 计算耗时
        $endTime = Get-Date
        $duration = $endTime - $startTime
        $durationMinutes = [Math]::Round($duration.TotalMinutes, 2)
        
        $completeTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$completeTime] 备份完成，耗时: $durationMinutes 分钟，备份大小: $backupSize MB" | Out-File -FilePath $logFile -Append -Encoding utf8
        Print-Status "备份完成，耗时: $durationMinutes 分钟，备份大小: $backupSize MB"
        
        # 返回成功
        return 0
    } catch {
        $errorTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "[$errorTime] 严重错误: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
        Print-Error "严重错误: $_"
        
        # 返回失败
        return 1
    }
}

# 执行主函数
$exitCode = Main
exit $exitCode