# 递归处理Ref目录下所有文件的PowerShell脚本
# 包括第一级到第三级子目录
# 功能：
# 1. 检查Python文件语法
# 2. 修复导入路径问题
# 3. 处理未闭合的三引号
# 4. 创建备份

# 创建备份目录
$backupDir = ".\Ref\.backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "备份目录已创建: $backupDir" -ForegroundColor Green

# 定义要处理的目录类型
$dirTypes = @("utils", "core", "api", "tests", "examples", "data", "models", "train")

# 处理目录的函数
function Process-Directory {
    param (
        [string]$dirPath,
        [int]$currentLevel = 1,
        [int]$maxLevel = 3
    )

    Write-Host "处理目录: $dirPath (级别 $currentLevel)" -ForegroundColor Cyan
    
    # 处理当前目录中的所有Python文件
    Get-ChildItem -Path $dirPath -Filter "*.py" | ForEach-Object {
        $filePath = $_.FullName
        $fileName = $_.Name
        
        # 创建备份
        $relativePath = $filePath.Replace("$PWD\", "")
        $backupPath = Join-Path -Path $backupDir -ChildPath $relativePath
        $backupFolder = Split-Path -Path $backupPath -Parent
        
        if (-not (Test-Path -Path $backupFolder)) {
            New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null
        }
        
        Copy-Item -Path $filePath -Destination $backupPath -Force
        
        Write-Host "处理文件: $fileName" -ForegroundColor Yellow
        
        # 检查Python文件是否有语法错误
        $syntaxCheck = python -m py_compile $filePath 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "文件 $fileName 存在语法错误:" -ForegroundColor Red
            Write-Host $syntaxCheck -ForegroundColor Red
            
            # 检查是否存在未闭合的三引号问题
            $content = Get-Content -Path $filePath -Raw
            $openQuotes = ([regex]::Matches($content, '"""')).Count
            
            if ($openQuotes % 2 -ne 0) {
                Write-Host "检测到未闭合的三引号，尝试修复..." -ForegroundColor Yellow
                
                # 检查是否包含量子纠缠相关标记
                if ($content -match "量子基因编码|纠缠状态|纠缠对象|纠缠强度") {
                    Write-Host "检测到量子纠缠相关标记，确认修复三引号问题" -ForegroundColor Green
                    
                    # 修复未闭合的三引号
                    if ($content.TrimEnd().EndsWith('"""')) {
                        $newContent = $content.TrimEnd()
                    } else {
                        $newContent = $content.TrimEnd() + "`n`n"
                    }
                    
                    Set-Content -Path $filePath -Value $newContent -NoNewline
                    
                    # 再次检查语法
                    $syntaxCheck = python -m py_compile $filePath 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "成功修复 $fileName 的三引号问题" -ForegroundColor Green
                    } else {
                        Write-Host "修复后仍存在语法错误，可能需要手动检查" -ForegroundColor Red
                    }
                }
            }
        } else {
            Write-Host "文件 $fileName 语法正确" -ForegroundColor Green
            
            # 检查并更新导入路径
            $content = Get-Content -Path $filePath -Raw
            $updatedContent = $content
            
            # 检查导入路径
            if ($filePath -match "Ref") {
                # 如果是Ref模块文件，处理相对导入
                $matches = [regex]::Matches($content, "import\s+([^\s;]+)|from\s+([^\s;]+)\s+import")
                
                foreach ($match in $matches) {
                    $importPath = if ($match.Groups[1].Success) { $match.Groups[1].Value } else { $match.Groups[2].Value }
                    
                    # 检查是否是相对路径但没有使用正确的相对导入语法
                    if ($importPath -match "^Ref" -and $filePath -match "Ref") {
                        $relativePath = $importPath -replace "^Ref\.", ""
                        $correctPath = ""
                        
                        # 根据文件在Ref中的位置确定正确的相对导入路径
                        $fileInRefPath = $filePath -replace ".*Ref\\", ""
                        $depth = ($fileInRefPath.Split("\")).Count - 1
                        
                        if ($depth -eq 0) {
                            # 在Ref根目录，使用直接导入
                            $correctPath = $relativePath
                        } else {
                            # 在子目录中，使用相对导入
                            $prefix = "../" * $depth
                            $correctPath = "$prefix$relativePath"
                        }
                        
                        # 替换导入路径
                        if ($match.Groups[1].Success) {
                            $updatedContent = $updatedContent -replace "import\s+$importPath", "import $correctPath"
                        } else {
                            $updatedContent = $updatedContent -replace "from\s+$importPath\s+import", "from $correctPath import"
                        }
                    }
                }
                
                # 如果内容有变化，更新文件
                if ($updatedContent -ne $content) {
                    Set-Content -Path $filePath -Value $updatedContent -NoNewline
                    Write-Host "已更新 $fileName 的导入路径" -ForegroundColor Green
                }
            }
        }
    }
    
    # 如果未达到最大级别，递归处理子目录
    if ($currentLevel -lt $maxLevel) {
        # 只处理指定类型的子目录
        Get-ChildItem -Path $dirPath -Directory | Where-Object { 
            $_.Name -in $dirTypes -or $currentLevel -eq 1 
        } | ForEach-Object {
            Process-Directory -dirPath $_.FullName -currentLevel ($currentLevel + 1) -maxLevel $maxLevel
        }
    }
}

# 开始处理Ref目录
$refPath = ".\Ref"
Process-Directory -dirPath $refPath -currentLevel 1 -maxLevel 3

Write-Host "`n脚本执行完成" -ForegroundColor Green
Write-Host "备份已保存至: $backupDir" -ForegroundColor Green
Write-Host "共处理了以下目录类型: $($dirTypes -join ', ')" -ForegroundColor Green 