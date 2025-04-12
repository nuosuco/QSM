#!/usr/bin/env pwsh
<#
.SYNOPSIS
    QSM模型服务启动脚本
.DESCRIPTION
    启动QSM（量子叠加态模型）的各项服务，包括核心服务、推理服务和监控服务
.NOTES
    版本: 1.0.0
    开发团队: 中华 ZhoHo, Claude
    创建日期: 2024-04-11
#>

# 设置错误操作首选项
$ErrorActionPreference = "Stop"

# 获取项目根目录
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$servicesDir = $scriptDir
$scriptsDir = Split-Path -Parent $servicesDir
$qsmDir = Split-Path -Parent $scriptsDir
$projectRoot = Split-Path -Parent $qsmDir

# 切换到项目根目录
Set-Location $projectRoot

# 创建日志目录
$logDir = Join-Path $projectRoot ".logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# 创建日志文件
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $logDir "QSM_services_$timestamp.log"

# 记录日志函数
function Write-Log {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # 输出到控制台
    switch ($Level) {
        "INFO" { Write-Host $logMessage -ForegroundColor Gray }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
    }
    
    # 写入日志文件
    Add-Content -Path $logFile -Value $logMessage
}

# 欢迎信息
Write-Log "=====================================================" "INFO"
Write-Log "              QSM 量子叠加态模型服务                " "INFO"
Write-Log "                  服务启动程序                      " "INFO"
Write-Log "=====================================================" "INFO"
Write-Log "项目根目录: $projectRoot" "INFO"
Write-Log "QSM目录: $qsmDir" "INFO"
Write-Log "启动时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
Write-Log "日志文件: $logFile" "INFO"
Write-Log "=====================================================" "INFO"

# 服务配置
$services = @{
    "QSM主服务" = @{
        ScriptPath = Join-Path $qsmDir "main.py"
        Port = 5331
        Process = $null
        OutputLog = Join-Path $logDir "QSM_main_$timestamp.log"
        ErrorLog = Join-Path $logDir "QSM_main_$timestamp.err"
        SkipIfNotExists = $false
    }
}

# 检查Python环境
Write-Log "检查Python环境..." "INFO"
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Log "未找到Python，请确保Python已安装并添加到PATH环境变量中" "ERROR"
    exit 1
}

# 检查必要的Python包
$requiredPackages = @("flask", "numpy", "pandas", "torch")
foreach ($package in $requiredPackages) {
    $checkPackage = python -c "import $package" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "警告: 未找到必要的Python包: $package" "WARNING"
    }
}

# 启动服务函数
function Start-QsmService {
    param (
        [string]$ServiceName,
        [string]$ScriptPath,
        [int]$Port = 0,
        [string]$OutputLog,
        [string]$ErrorLog,
        [bool]$SkipIfNotExists = $false
    )
    
    Write-Log "正在启动服务: $ServiceName" "INFO"
    
    # 验证脚本是否存在
    if (-not (Test-Path $ScriptPath)) {
        if ($SkipIfNotExists) {
            Write-Log "服务脚本不存在，已配置为跳过: $ScriptPath" "WARNING"
            return $null
        } else {
            Write-Log "服务脚本不存在: $ScriptPath" "ERROR"
            return $null
        }
    }
    
    try {
        # 根据文件扩展名确定如何启动服务
        $extension = [System.IO.Path]::GetExtension($ScriptPath)
        $process = $null
        
        if ($extension -eq ".py") {
            # 创建启动信息
            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = "python"
            $processInfo.Arguments = "`"$ScriptPath`""
            if ($Port -gt 0) {
                $processInfo.Arguments += " --port $Port"
            }
            $processInfo.Arguments += " --daemon"
            $processInfo.UseShellExecute = $false
            $processInfo.RedirectStandardOutput = $true
            $processInfo.RedirectStandardError = $true
            $processInfo.CreateNoWindow = $false
            
            # 启动进程
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $processInfo
            $process.Start() | Out-Null
            
            # 异步读取标准输出和错误
            $outTask = $process.StandardOutput.ReadToEndAsync()
            $errTask = $process.StandardError.ReadToEndAsync()
            
            # 等待一段时间让进程启动
            Start-Sleep -Seconds 2
            
            # 检查进程是否正在运行
            if ($process.HasExited) {
                $exitCode = $process.ExitCode
                $errorOutput = $errTask.Result
                Write-Log "服务启动失败: $ServiceName (错误代码: $exitCode)" "ERROR"
                Write-Log "错误输出: $errorOutput" "ERROR"
                return $null
            }
            
            # 将输出写入日志文件
            try {
                $outTask.Result | Out-File -FilePath $OutputLog -Encoding utf8
                $errTask.Result | Out-File -FilePath $ErrorLog -Encoding utf8
            } catch {
                Write-Log "无法写入日志文件: $($_.Exception.Message)" "ERROR"
            }
            
            Write-Log "已启动Python服务: $ServiceName (PID: $($process.Id))" "SUCCESS"
        }
        else {
            Write-Log "不支持的脚本类型: $extension" "ERROR"
            return $null
        }
        
        return $process
    }
    catch {
        Write-Log "启动服务时出错: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# 停止服务函数
function Stop-QsmService {
    param (
        [string]$ServiceName,
        [System.Diagnostics.Process]$Process
    )
    
    if ($null -eq $Process) {
        Write-Log "服务未运行: $ServiceName" "WARNING"
        return
    }
    
    if (-not $Process.HasExited) {
        Write-Log "正在停止服务: $ServiceName (PID: $($Process.Id))" "INFO"
        
        try {
            $Process.Kill()
            $Process.WaitForExit(5000) | Out-Null
            
            if (-not $Process.HasExited) {
                Write-Log "无法正常停止服务，正在强制终止: $ServiceName" "WARNING"
                $Process.Kill()
            }
            
            Write-Log "服务已停止: $ServiceName" "SUCCESS"
        }
        catch {
            Write-Log "停止服务时出错: $($_.Exception.Message)" "ERROR"
        }
    }
    else {
        Write-Log "服务已停止: $ServiceName" "INFO"
    }
}

# 检查服务是否都在运行
function Test-ServicesRunning {
    $allRunning = $true
    
    foreach ($serviceName in $services.Keys) {
        $serviceInfo = $services[$serviceName]
        $process = $serviceInfo.Process
        
        if ($null -eq $process -or $process.HasExited) {
            $allRunning = $false
            break
        }
    }
    
    return $allRunning
}

# 启动所有服务
Write-Log "开始启动所有QSM服务..." "INFO"

foreach ($serviceName in $services.Keys) {
    $serviceInfo = $services[$serviceName]
    $process = Start-QsmService -ServiceName $serviceName -ScriptPath $serviceInfo.ScriptPath -Port $serviceInfo.Port -OutputLog $serviceInfo.OutputLog -ErrorLog $serviceInfo.ErrorLog -SkipIfNotExists $serviceInfo.SkipIfNotExists
    $services[$serviceName].Process = $process
}

# 检查所有服务是否成功启动
$allRunning = Test-ServicesRunning
if ($allRunning) {
    Write-Log "所有服务已成功启动!" "SUCCESS"
    Write-Host ""
    Write-Host "按任意键停止所有服务..." -ForegroundColor Cyan
    
    # 等待用户按键
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
    
    Write-Log "接收到按键，正在停止服务..." "INFO"
    
    # 停止所有服务
    foreach ($serviceName in $services.Keys) {
        $serviceInfo = $services[$serviceName]
        Stop-QsmService -ServiceName $serviceName -Process $serviceInfo.Process
    }
    
    Write-Log "所有服务已停止" "SUCCESS"
}
else {
    Write-Log "部分服务启动失败，请检查日志文件" "ERROR"
    
    # 停止已启动的服务
    foreach ($serviceName in $services.Keys) {
        $serviceInfo = $services[$serviceName]
        if ($null -ne $serviceInfo.Process -and -not $serviceInfo.Process.HasExited) {
            Stop-QsmService -ServiceName $serviceName -Process $serviceInfo.Process
        }
    }
}

Write-Log "QSM服务管理脚本执行完成" "INFO"

<# 
量子基因编码: QE-SRV-QSM-S5E2R7V1
纠缠状态: 活跃
纠缠对象: ['QSM/core/qsm_core.py', 'QSM/qsm_inference.py', 'QSM/monitor.py']
纠缠强度: 0.99

开发团队：中华 ZhoHo，Claude 
#> 