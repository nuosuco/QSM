# 修复中文编码问题
# 这个脚本将自动检测文件编码并转换为UTF-8

Write-Host "开始修复中文编码问题..." -ForegroundColor Green

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$testDir = Join-Path $scriptPath "..\tests"
$srcDir = Join-Path $scriptPath "..\src"
$binDir = Join-Path $scriptPath "..\bin"

# 转换文件编码的函数
function Convert-FileEncoding {
    param (
        [string]$filePath
    )
    
    try {
        # 读取文件
        $content = Get-Content -Path $filePath -Raw
        
        # 如果文件包含中文字符但显示乱码
        if ($content -match "閲忓瓙|鐘舵€乗") {
            Write-Host "修复文件编码: $filePath" -ForegroundColor Yellow
            
            # 检测当前编码，尝试不同的编码方式读取
            $encodings = @("Default", "UTF8", "Unicode", "BigEndianUnicode", "ASCII")
            
            foreach ($encoding in $encodings) {
                try {
                    $testContent = Get-Content -Path $filePath -Encoding $encoding -Raw
                    
                    # 如果可以正确读取中文
                    if ($testContent -match "量子|状态|测试" -and $testContent -notmatch "閲忓瓙|鐘舵€乗") {
                        Write-Host "  检测到有效编码: $encoding" -ForegroundColor Cyan
                        # 以UTF-8保存
                        $testContent | Out-File -FilePath $filePath -Encoding utf8
                        Write-Host "  已转换为UTF-8" -ForegroundColor Green
                        return
                    }
                }
                catch {
                    # 忽略编码错误继续尝试
                }
            }
            
            # 如果无法自动检测，尝试以GB2312/GBK读取
            Write-Host "  尝试使用GBK/GB2312编码..." -ForegroundColor Yellow
            
            try {
                $bytes = [System.IO.File]::ReadAllBytes($filePath)
                $gbkEncoding = [System.Text.Encoding]::GetEncoding("GBK")
                $text = $gbkEncoding.GetString($bytes)
                
                # 验证是否成功解码
                if ($text -match "量子|状态|测试" -and $text -notmatch "閲忓瓙|鐘舵€乗") {
                    $utf8Encoding = [System.Text.Encoding]::UTF8
                    $utf8Bytes = $utf8Encoding.GetBytes($text)
                    [System.IO.File]::WriteAllBytes($filePath, $utf8Bytes)
                    Write-Host "  已从GBK转换为UTF-8" -ForegroundColor Green
                }
                else {
                    Write-Host "  无法自动修复编码: $filePath" -ForegroundColor Red
                }
            }
            catch {
                Write-Host "  编码转换错误: $_" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "处理文件错误: $_" -ForegroundColor Red
    }
}

# 处理各目录下的文件
Write-Host "处理测试文件..." -ForegroundColor Cyan
Get-ChildItem -Path $testDir -Filter "*.c" | ForEach-Object {
    Convert-FileEncoding -filePath $_.FullName
}

Write-Host "处理源代码文件..." -ForegroundColor Cyan
Get-ChildItem -Path $srcDir -Filter "*.c" | ForEach-Object {
    Convert-FileEncoding -filePath $_.FullName
}
Get-ChildItem -Path $srcDir -Filter "*.h" | ForEach-Object {
    Convert-FileEncoding -filePath $_.FullName
}

Write-Host "处理批处理文件..." -ForegroundColor Cyan
Get-ChildItem -Path $binDir -Filter "*.bat" | ForEach-Object {
    Convert-FileEncoding -filePath $_.FullName
}
Get-ChildItem -Path $testDir -Filter "*.bat" | ForEach-Object {
    Convert-FileEncoding -filePath $_.FullName
}

Write-Host "编码修复完成！" -ForegroundColor Green
Write-Host "如果问题仍然存在，请重新编译测试文件。" -ForegroundColor Yellow 