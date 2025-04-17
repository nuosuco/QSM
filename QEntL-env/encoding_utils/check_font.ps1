# PowerShell脚本：检查并配置控制台字体和编码以支持中文字符

# 获取当前控制台字体信息
$currentFont = $Host.UI.RawUI.FontFamily
$currentFontSize = $Host.UI.RawUI.FontSize
$currentCodePage = [System.Console]::OutputEncoding.CodePage

Write-Host "控制台字体检查工具" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "当前控制台设置:" -ForegroundColor Yellow
Write-Host "字体家族: $currentFont"
Write-Host "字体大小: $($currentFontSize.Width)x$($currentFontSize.Height)"
Write-Host "当前代码页: $currentCodePage"
Write-Host ""

# 检查是否支持中文
$supportsChinese = $false
$recommendedFonts = @("NSimSun", "SimSun-ExtB", "Microsoft YaHei", "Microsoft YaHei UI", "SimSun", "MS Gothic", "MingLiU")

if ($recommendedFonts -contains $currentFont) {
    $supportsChinese = $true
    Write-Host "✓ 当前字体 '$currentFont' 支持中文字符" -ForegroundColor Green
} 
else {
    Write-Host "✗ 当前字体 '$currentFont' 可能不支持中文字符" -ForegroundColor Red
}

if ($currentCodePage -eq 65001) {
    Write-Host "✓ 当前使用UTF-8编码 (代码页65001)" -ForegroundColor Green
} 
else {
    Write-Host "✗ 当前未使用UTF-8编码，中文显示可能会有问题" -ForegroundColor Red
    Write-Host "  建议使用 'chcp 65001' 设置UTF-8编码" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "建议字体设置:" -ForegroundColor Yellow
foreach ($font in $recommendedFonts) {
    Write-Host " - $font"
}

Write-Host ""
Write-Host "是否要将控制台设置为最佳中文支持配置? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    try {
        # 尝试更改当前控制台字体
        if ("Microsoft YaHei" -ne $currentFont) {
            $Host.UI.RawUI.FontFamily = "Microsoft YaHei"
            Write-Host "字体已更改为 'Microsoft YaHei'" -ForegroundColor Green
        }
        
        # 设置控制台为UTF-8
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        # 同时使用命令行更改代码页
        cmd /c "chcp 65001 >nul"
        
        Write-Host "控制台已设置为UTF-8编码" -ForegroundColor Green
        Write-Host "中文测试: 量子纠缠 量子场 量子基因" -ForegroundColor Magenta
    }
    catch {
        Write-Host "无法更改字体设置: $_" -ForegroundColor Red
        Write-Host "请手动更改控制台属性中的字体设置" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "提示: 要在批处理文件中设置UTF-8编码，请添加 'chcp 65001 >nul'" -ForegroundColor Cyan
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 