# 量子系统主启动脚本 - 编码兼容版
# 通过此脚本启动所有服务，避免中文乱码问题

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==== 量子系统服务启动器 ====" -ForegroundColor Cyan
Write-Host "正在启动所有服务，请稍候..." -ForegroundColor Green

# 使用Python启动脚本
& python scripts\services\start_services.py --all --optimize

# 确保文件监控器已启动
$processInfo = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*file_monitor.py*" }
if (-not $processInfo) {
    Write-Host "未检测到文件监控器，正在启动..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "Ref/utils/file_monitor.py --standalone" -WindowStyle Hidden
    Write-Host "文件监控器已启动" -ForegroundColor Green
} else {
    Write-Host "文件监控器已在运行中" -ForegroundColor Green
}

Write-Host ""
Write-Host "==== 启动完成 ====" -ForegroundColor Cyan
Write-Host "所有服务已在后台运行，您可以继续使用控制台" -ForegroundColor Green
Write-Host "系统将自动进行量子叠加态优化和资源管理" -ForegroundColor Yellow 