# QSM项目备份计划任务设置脚本
# 版本：1.0
# 日期：2025-04-09
# 功能：创建Windows计划任务，每小时执行一次QSM项目备份

# 需要以管理员权限运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "此脚本需要管理员权限运行。请以管理员身份重新运行此脚本。" -ForegroundColor Red
    exit
}

# 备份脚本路径
$scriptPath = "E:\model\QSM\Ref\backup\hourly_backup.ps1"
$scriptDirectory = Split-Path -Parent $scriptPath

# 检查备份脚本是否存在
if (-not (Test-Path $scriptPath)) {
    Write-Host "错误: 备份脚本不存在: $scriptPath" -ForegroundColor Red
    exit
}

# 任务名称和描述
$taskName = "QSM项目自动备份"
$taskDescription = "每小时备份QSM项目到指定位置，并保留最近72个备份"

# 检查任务是否已存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "计划任务 '$taskName' 已存在，正在移除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建任务动作 - 运行PowerShell脚本
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" `
    -WorkingDirectory $scriptDirectory

# 创建任务触发器 - 每小时运行一次
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries `
    -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# 获取当前用户
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# 注册计划任务
try {
    Register-ScheduledTask -TaskName $taskName -Description $taskDescription `
        -Action $action -Trigger $trigger -Settings $settings `
        -User $currentUser -RunLevel Highest -Force | Out-Null
    
    Write-Host "成功创建计划任务 '$taskName'" -ForegroundColor Green
    Write-Host "任务将每小时运行一次，备份QSM项目" -ForegroundColor Green
    Write-Host "备份脚本路径: $scriptPath" -ForegroundColor Green
    Write-Host "首次运行时间: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Green
}
catch {
    Write-Host "创建计划任务失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 显示任务信息
Write-Host "`n计划任务详细信息:" -ForegroundColor Cyan
Get-ScheduledTask -TaskName $taskName | Format-List *
Write-Host "`n"
Get-ScheduledTaskInfo -TaskName $taskName | Format-List * 