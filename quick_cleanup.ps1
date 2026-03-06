# 快速清理Cursor和系统缓存
Write-Host " QSM量子系统快速清理工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查内存使用情况
$Memory = Get-WmiObject -Class Win32_ComputerSystem
$TotalRAM = [math]::Round($Memory.TotalPhysicalMemory / 1GB, 2)
$AvailableRAM = [math]::Round((Get-Counter '\Memory\Available MBytes').CounterSamples[0].CookedValue / 1024, 2)
$UsedRAM = $TotalRAM - $AvailableRAM

Write-Host " 内存状态:" -ForegroundColor Green
Write-Host "   总内存: $TotalRAM GB" -ForegroundColor White
Write-Host "   已用内存: $UsedRAM GB" -ForegroundColor Yellow
Write-Host "   可用内存: $AvailableRAM GB" -ForegroundColor Green

Write-Host ""
Write-Host " 开始清理..." -ForegroundColor Green

# 清理项目空文件
$EmptyFiles = Get-ChildItem -Path "." -Recurse -File | Where-Object { $_.Length -eq 0 -and $_.Name -match "\.(html|md|txt)$" }
if ($EmptyFiles) {
    $EmptyFiles | Remove-Item -Force
    Write-Host " 已清理 $($EmptyFiles.Count) 个空文件" -ForegroundColor Green
}

Write-Host " 清理完成！建议重启Cursor" -ForegroundColor Green
