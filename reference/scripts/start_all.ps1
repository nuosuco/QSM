
# # 量子基因编码: QE-STA-B96947093657
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# 启动所有服务脚本
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

# 主函数
function Start-AllServices {
    Print-Status "开始启动所有服务..."
    
    # 激活虚拟环境
    $venvPath = ".\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvPath) {
        try {
            Print-Status "激活虚拟环境..."
            & $venvPath
            Print-Status "虚拟环境激活成功"
        }
        catch {
            Print-Error "虚拟环境激活失败: $_"
            return
        }
    }
    else {
        Print-Warning "未找到虚拟环境，跳过激活步骤"
    }
    
    # 创建备份目录，用于修复已知的缩进问题
    $backupDir = ".\.indentation_backups"
    if (-not (Test-Path $backupDir)) {
        New-Item -Path $backupDir -ItemType Directory | Out-Null
        Print-Status "创建备份目录: $backupDir"
    }
    
    # 检查并修复Ref/ref_core.py的缩进问题
    $refCorePath = ".\Ref\ref_core.py"
    if (Test-Path $refCorePath) {
        # 备份文件
        $backupPath = Join-Path $backupDir "ref_core.py.bak"
        Copy-Item -Path $refCorePath -Destination $backupPath -Force
        Print-Status "已备份 $refCorePath 到 $backupPath"
        
        # 修复文件中的已知问题
        try {
            $content = Get-Content -Path $refCorePath -Raw
            
            # 修复缩进问题
            $content = $content -replace '""".*?"""', '' -replace "'''.*?'''", ''
            
            # 将修复后的内容写回文件
            Set-Content -Path $refCorePath -Value $content
            Print-Status "已修复 $refCorePath 中的缩进问题"
        }
        catch {
            Print-Error "修复 $refCorePath 时出错: $_"
        }
    }
    
    # 定义启动服务的函数
    function Start-Service {
        param(
            [string]$serviceName,
            [string]$command
        )
        
        Print-Status "正在启动 $serviceName..."
        try {
            Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"$command`"" -WindowStyle Minimized
            Print-Status "$serviceName 已成功启动"
            return $true
        }
        catch {
            Print-Error "$serviceName 启动失败: $_"
            return $false
        }
    }
    
    # 启动服务计数
    $successCount = 0
    
    # 启动Ref核心
    if (Start-Service -serviceName "Ref核心" -command "python .\Ref\ref_core.py") {
        $successCount++
    }
    
    # 等待2秒
    Start-Sleep -Seconds 2
    
    # 启动文件监控系统
    if (Start-Service -serviceName "文件监控系统" -command "python .\Ref\utils\file_monitor.py") {
        $successCount++
    }
    
    # 等待2秒
    Start-Sleep -Seconds 2
    
    # 启动QSM API服务
    if (Start-Service -serviceName "QSM API服务" -command "python .\app.py") {
        $successCount++
    }
    
    # 输出总结
    Print-Status "总共成功启动了 $successCount 个服务"
    Print-Status "所有服务启动完成！"
}

# 运行主函数
Start-AllServices 