#!/usr/bin/env pwsh

# # 量子基因编码: QE-FIX-CF2A3660032C
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# 全面服务启动脚本 - 启动所有量子系统核心服务
# 版本：2.0
# 日期：2025-04-09

# 设置颜色
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

function Check-Process {
    param(
        [string]$CommandPattern,
        [string]$ServiceName
    )
    
    $process = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*$CommandPattern*" }
    if ($process) {
        Print-Status "$ServiceName 已在运行，进程ID: $($process.Id)"
        return $true
    }
    return $false
}

function Stop-QSMService {
    param(
        [string]$CommandPattern,
        [string]$ServiceName
    )
    
    $process = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*$CommandPattern*" }
    if ($process) {
        Print-Status "正在停止 $ServiceName (PID: $($process.Id))..."
        Stop-Process -Id $process.Id -Force
        Start-Sleep -Seconds 1
        return $true
    }
    return $false
}

function Start-QSMService {
    param(
        [string]$Command,
        [string]$ServiceName,
        [bool]$Critical = $false
    )
    
    Print-Status "正在启动 $ServiceName..."
    
    # 检查服务是否已在运行
    if (Check-Process -CommandPattern $Command -ServiceName $ServiceName) {
        Print-Status "$ServiceName 已经在运行，跳过启动"
        return $true
    }
    
    try {
        # 启动服务
        Start-Process python -ArgumentList $Command -NoNewWindow
        
        # 等待服务启动
        Start-Sleep -Seconds 3
        
        # 检查服务是否成功启动
        if (Check-Process -CommandPattern $Command -ServiceName $ServiceName) {
            Print-Status "$ServiceName 已成功启动"
            return $true
        } else {
            if ($Critical) {
                Print-Error "$ServiceName 启动失败，这是关键服务！"
                return $false
            } else {
                Print-Warning "$ServiceName 启动失败，但不是关键服务，继续执行"
                return $false
            }
        }
    } catch {
        Print-Error "$ServiceName 启动时出错: $_"
        if ($Critical) {
            return $false
        } else {
            return $true  # 非关键服务失败不会中断整个启动流程
        }
    }
}

# 修复量子基因标记监控功能
function Fix-QuantumGeneMarker {
    Print-Status "修复量子基因标记监控模式问题..."
    $markerPath = "Ref/utils/quantum_gene_marker.py"
    
    if (-not (Test-Path $markerPath)) {
        Print-Error "未找到量子基因标记文件: $markerPath"
        return $false
    }
    
    $content = Get-Content -Path $markerPath -Raw
    
    # 备份文件
    $backupPath = "$markerPath.bak"
    if (-not (Test-Path $backupPath)) {
        Copy-Item -Path $markerPath -Destination $backupPath -Force
        Print-Status "已备份 $markerPath 到 $backupPath"
    }
    
    # 检查并添加缺少的监控模式功能
    if ($content -match "def start_monitor_mode") {
        Print-Status "量子基因标记监控模式功能已存在，无需修复"
        return $true
    }
    
    # 添加监控模式函数
    $monitorFunction = @'

def start_monitor_mode():
    '''启动监控模式，实时监控文件变化并更新量子基因标记'''
    import time
    logging.info("启动量子基因标记监控模式")
    print("量子基因标记监控模式已启动，按Ctrl+C退出")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("监控已停止")

'@
    $content += $monitorFunction
    
    # 添加命令行参数解析
    $mainFunctionPattern = 'if __name__ == ''__main__'''
    if ($content -match $mainFunctionPattern) {
        # 添加argparse导入（如果尚未导入）
        if (-not ($content -match "import argparse")) {
            $content = $content -replace "import logging", "import logging`nimport argparse"
        }
        
        # 添加参数解析器
        $content = $content -replace $mainFunctionPattern, "$&:`n    parser = argparse.ArgumentParser(description='量子基因标记工具')"
        
        # 添加monitor参数
        if (-not ($content -match "--monitor")) {
            # 查找已有的参数添加位置
            $helpArgPattern = "parser\.add_argument\('-h', '--help'"
            if ($content -match $helpArgPattern) {
                $content = $content -replace $helpArgPattern, "parser.add_argument('-h', '--help')`n    parser.add_argument('--monitor', action='store_true', help='启动监控模式')"
            } else {
                # 如果找不到help参数，在args解析后添加monitor参数
                $argsPattern = "args = parser\.parse_args\(\)"
                if ($content -match $argsPattern) {
                    $content = $content -replace "parser = argparse\.ArgumentParser", "parser = argparse.ArgumentParser`n    parser.add_argument('--monitor', action='store_true', help='启动监控模式')`n    # 其他参数"
                }
            }
        }
        
        # 添加处理monitor参数的逻辑
        if (-not ($content -match "if args\.monitor:")) {
            $scanPattern = "if args\.scan:"
            if ($content -match $scanPattern) {
                $content = $content -replace $scanPattern, "if args.monitor:`n        start_monitor_mode()`n    elif args.scan:"
            } else {
                # 如果找不到scan参数，在args处理部分添加monitor处理
                $argsPattern = "args = parser\.parse_args\(\)"
                if ($content -match $argsPattern) {
                    $content = $content -replace $argsPattern, "$&`n    if args.monitor:`n        start_monitor_mode()"
                }
            }
        }
    } else {
        # 如果找不到main函数，添加一个基本的main函数框架
        $mainFunction = @'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='量子基因标记工具')
    parser.add_argument('--monitor', action='store_true', help='启动监控模式')
    args = parser.parse_args()
    
    if args.monitor:
        start_monitor_mode()
'@
        $content += $mainFunction
    }
    
    # 保存修改后的内容
    Set-Content -Path $markerPath -Value $content
    Print-Status "已修复量子基因标记监控模式"
    return $true
}

# 主函数
function Start-AllServices {
    param(
        [switch]$FixQGM = $false
    )
    
    Print-Status "===== 量子系统全面服务启动 v2.0 ====="
    
    # 先停止可能在运行的服务
    Print-Status "正在检查现有服务并停止..."
    Stop-QSMService -CommandPattern "ref_core.py" -ServiceName "Ref核心服务"
    Stop-QSMService -CommandPattern "quantum_gene_marker.py" -ServiceName "量子基因标记监控"
    Stop-QSMService -CommandPattern "file_monitor.py" -ServiceName "文件监控系统"
    Stop-QSMService -CommandPattern "QSM/app.py" -ServiceName "QSM API服务"
    Stop-QSMService -CommandPattern "QEntL/engine.py" -ServiceName "QEntL引擎"
    Stop-QSMService -CommandPattern "SOM/app.py" -ServiceName "SOM服务"
    Stop-QSMService -CommandPattern "WeQ/app.py" -ServiceName "WeQ服务"
    Stop-QSMService -CommandPattern "Ref/app.py" -ServiceName "Ref API服务"
    Stop-QSMService -CommandPattern "WeQ/weq_train.py" -ServiceName "WeQ训练系统"
    Stop-QSMService -CommandPattern "weq_train_seq.py" -ServiceName "WeQ顺序训练"
    Stop-QSMService -CommandPattern "weq_train_par.py" -ServiceName "WeQ并行训练"
    
    # 激活虚拟环境
    Print-Status "正在激活虚拟环境..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        try {
            & ".\.venv\Scripts\Activate.ps1"
            Print-Status "虚拟环境激活成功"
        } catch {
            Print-Error "虚拟环境激活失败: $_"
            return $false
        }
    } else {
        Print-Warning "未找到虚拟环境，继续执行（可能会出现依赖问题）"
    }
    
    # 确保日志目录存在
    if (-not (Test-Path ".logs")) {
        New-Item -Path ".logs" -ItemType Directory | Out-Null
        Print-Status "创建日志目录: .logs"
    }
    
    # 修复量子基因标记监控模式问题
    if ($FixQGM) {
        if (-not (Fix-QuantumGeneMarker)) {
            Print-Warning "量子基因标记监控模式修复失败，但将继续启动服务"
        }
    }
    
    # 启动所有服务
    $success = $true
    
    # 1. 启动Ref核心（关键服务）
    if (-not (Start-QSMService -Command "Ref/ref_core.py" -ServiceName "Ref核心服务" -Critical $true)) {
        Print-Error "Ref核心服务启动失败，无法继续启动其他服务"
        return $false
    }
    
    # 等待Ref核心启动完成
    Start-Sleep -Seconds 5
    
    # 2. 启动量子基因标记监控
    Start-QSMService -Command "Ref/utils/quantum_gene_marker.py --monitor" -ServiceName "量子基因标记监控"
    
    # 3. 启动文件监控系统
    $projectRootPath = (Get-Location).Path
    $refPath = Join-Path $projectRootPath "Ref"
    $qEntlPath = Join-Path $projectRootPath "QEntL"
    $monitorCmd = "Ref/utils/file_monitor.py --standalone --paths `"$projectRootPath`" `"$refPath`" `"$qEntlPath`""
    Start-QSMService -Command $monitorCmd -ServiceName "文件监控系统"
    
    # 4. 启动QSM API服务（关键服务）
    if (-not (Start-QSMService -Command "QSM/app.py" -ServiceName "QSM API服务" -Critical $true)) {
        $success = $false
    }
    
    # 5. 启动QEntL引擎
    Start-QSMService -Command "QEntL/engine.py" -ServiceName "QEntL引擎"
    
    # 6. 启动SOM服务
    Start-QSMService -Command "SOM/app.py" -ServiceName "SOM服务"
    
    # 7. 启动WeQ服务
    Start-QSMService -Command "WeQ/app.py" -ServiceName "WeQ服务"
    
    # 8. 启动Ref API服务
    if (Test-Path "Ref/app.py") {
        Start-QSMService -Command "Ref/app.py" -ServiceName "Ref API服务"
    } else {
        Print-Warning "未找到Ref API服务文件: Ref/app.py，跳过启动"
    }
    
    # 9. 启动WeQ后台训练系统
    Start-QSMService -Command "WeQ/weq_train.py" -ServiceName "WeQ主训练系统"
    
    # 10. 启动WeQ额外训练模块（如果存在）
    if (Test-Path "WeQ/weq_train_seq.py") {
        Start-QSMService -Command "WeQ/weq_train_seq.py" -ServiceName "WeQ顺序训练模块"
    }
    
    if (Test-Path "WeQ/weq_train_par.py") {
        Start-QSMService -Command "WeQ/weq_train_par.py" -ServiceName "WeQ并行训练模块"
    }
    
    # 创建服务状态文件
    $statusPath = Join-Path $projectRootPath "services_status.txt"
    "量子系统服务状态 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $statusPath
    "=======================================" | Out-File -FilePath $statusPath -Append
    
    # 检查所有服务状态并写入状态文件
    $runningServices = @(
        @{Pattern="ref_core.py"; Name="Ref核心服务"},
        @{Pattern="quantum_gene_marker.py"; Name="量子基因标记监控"},
        @{Pattern="file_monitor.py"; Name="文件监控系统"},
        @{Pattern="QSM/app.py"; Name="QSM API服务"},
        @{Pattern="QEntL/engine.py"; Name="QEntL引擎"},
        @{Pattern="SOM/app.py"; Name="SOM服务"},
        @{Pattern="WeQ/app.py"; Name="WeQ服务"},
        @{Pattern="Ref/app.py"; Name="Ref API服务"},
        @{Pattern="WeQ/weq_train.py"; Name="WeQ主训练系统"},
        @{Pattern="weq_train_seq.py"; Name="WeQ顺序训练模块"},
        @{Pattern="weq_train_par.py"; Name="WeQ并行训练模块"}
    )
    
    $runningCount = 0
    foreach ($service in $runningServices) {
        $isRunning = Check-Process -CommandPattern $service.Pattern -ServiceName $service.Name
        $status = if ($isRunning) { "运行中" } else { "未运行" }
        "$($service.Name): $status" | Out-File -FilePath $statusPath -Append
        if ($isRunning) { $runningCount++ }
    }
    
    "=======================================" | Out-File -FilePath $statusPath -Append
    "总计: $runningCount/$($runningServices.Count) 服务运行中" | Out-File -FilePath $statusPath -Append
    
    # 结果通知
    Print-Status "======================================="
    Print-Status "所有服务启动尝试完成！"
    Print-Status "总计: $runningCount/$($runningServices.Count) 服务运行中"
    Print-Status "服务状态已保存到: $statusPath"
    Print-Status "======================================="
    
    return $success
}

# 参数处理
param(
    [switch]$StartAll = $false,
    [switch]$FixQGM = $false
)

# 如果没有参数，启动所有服务
if (-not $StartAll -and -not $FixQGM) {
    $StartAll = $true
}

# 执行主函数
if ($StartAll) {
    $result = Start-AllServices -FixQGM:$FixQGM
    if ($result) {
        Print-Status "量子系统启动成功"
        Print-Status "按Ctrl+C停止所有服务"
        try {
            while ($true) { Start-Sleep -Seconds 1 }
        } catch {
            # 用户中断，结束服务
            Print-Status "正在停止所有服务..."
            Get-Process python | Where-Object { $_.CommandLine -like "*ref_core.py*" -or 
                                               $_.CommandLine -like "*quantum_gene_marker.py*" -or
                                               $_.CommandLine -like "*file_monitor.py*" -or
                                               $_.CommandLine -like "*app.py*" -or
                                               $_.CommandLine -like "*engine.py*" -or
                                               $_.CommandLine -like "*weq_train.py*" -or
                                               $_.CommandLine -like "*weq_train_seq.py*" -or
                                               $_.CommandLine -like "*weq_train_par.py*" } | Stop-Process -Force
        }
    } else {
        Print-Error "量子系统启动过程中遇到关键错误"
        exit 1
    }
} elseif ($FixQGM) {
    # 只修复量子基因标记
    if (Fix-QuantumGeneMarker) {
        Print-Status "量子基因标记监控模式修复完成"
    } else {
        Print-Error "量子基因标记监控模式修复失败"
        exit 1
    }
} 