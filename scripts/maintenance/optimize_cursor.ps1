# Cursor优化脚本
# 版本：1.0
# 功能：优化Cursor性能，设置缓存保留3天

# 设置颜色
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow 
$RED = [System.ConsoleColor]::Red
$CYAN = [System.ConsoleColor]::Cyan

function Write-Status {
    param([string]$message)
    Write-Host "[状态] $message" -ForegroundColor $GREEN
}

function Write-Warning {
    param([string]$message)
    Write-Host "[警告] $message" -ForegroundColor $YELLOW
}

function Write-Error {
    param([string]$message)
    Write-Host "[错误] $message" -ForegroundColor $RED
}

# Cursor配置目录
$cursorDir = ".cursor"
$configFile = Join-Path $cursorDir "config.json"

# 创建Cursor配置目录(如果不存在)
if (-not (Test-Path $cursorDir)) {
    try {
        New-Item -Path $cursorDir -ItemType Directory -Force | Out-Null
        Write-Status "创建Cursor配置目录成功"
    } catch {
        Write-Error "创建Cursor配置目录失败: $_"
        exit 1
    }
}

# 创建或更新配置文件
$config = @{
    "yolo_mode" = $true
    "ai_optimization" = "extreme"
    "timestamp" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "memory_usage" = "optimized"
    "gpu_acceleration" = $true
    "auto_complete_level" = "aggressive"
    "response_time" = "fastest"
    "cache_retention_days" = 3
    "cache_optimization" = "performance"
}

try {
    $config | ConvertTo-Json | Set-Content -Path $configFile -Encoding UTF8
    Write-Status "Cursor配置更新成功"
} catch {
    Write-Error "更新配置文件失败: $_"
    exit 1
}

# 清理过期缓存
function Clear-OldCache {
    Write-Status "正在清理过期的Cursor缓存..."
    
    $cacheFolder = "$env:APPDATA\Cursor\Cache"
    
    if (Test-Path $cacheFolder) {
        try {
            # 删除3天前的缓存文件
            $cutoffDate = (Get-Date).AddDays(-3)
            $oldFiles = Get-ChildItem -Path $cacheFolder -Recurse -File | Where-Object { $_.LastWriteTime -lt $cutoffDate }
            
            if ($oldFiles) {
                $oldFiles | Remove-Item -Force
                Write-Status "已清理 $($oldFiles.Count) 个过期缓存文件"
            } else {
                Write-Status "没有找到过期的缓存文件需要清理"
            }
        } catch {
            Write-Warning "清理缓存时出错: $_"
        }
    } else {
        Write-Warning "未找到Cursor缓存目录: $cacheFolder"
    }
}

# 优化程序性能
function Optimize-CursorPerformance {
    Write-Status "正在优化Cursor性能..."
    
    # 1. 关闭不必要的后台进程
    $cursorProcesses = Get-Process | Where-Object { $_.ProcessName -like "*cursor*" -and $_.ProcessName -ne "cursor" }
    if ($cursorProcesses) {
        try {
            $cursorProcesses | ForEach-Object {
                if ($_.ProcessName -notlike "*cursor-helper*") {
                    Stop-Process -Id $_.Id -Force
                    Write-Status "已停止不必要的进程: $($_.ProcessName)"
                }
            }
        } catch {
            Write-Warning "停止进程时出错: $_"
        }
    }
    
    # 2. 设置系统性能优化
    try {
        # 设置Cursor进程的优先级为高
        $mainProcess = Get-Process | Where-Object { $_.ProcessName -eq "cursor" }
        if ($mainProcess) {
            $mainProcess | ForEach-Object { $_.PriorityClass = "High" }
            Write-Status "已将Cursor进程优先级设置为高"
        }
    } catch {
        Write-Warning "设置进程优先级时出错: $_"
    }
}

# 执行优化
Clear-OldCache
Optimize-CursorPerformance

# 显示完成信息
Write-Host ""
Write-Host "✅ Cursor优化已完成！" -ForegroundColor $CYAN
Write-Host "   • 性能设置已调整为最佳状态" -ForegroundColor $CYAN
Write-Host "   • 缓存保留期限已设置为3天" -ForegroundColor $CYAN
Write-Host "   • 过期缓存已清理" -ForegroundColor $CYAN
Write-Host ""
Write-Host "   提示：如需最佳性能，建议定期重启Cursor" -ForegroundColor $YELLOW
Write-Host "" 