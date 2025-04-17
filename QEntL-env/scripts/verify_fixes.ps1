# 验证修复脚本
# 检查以下内容：
# 1. QuantumField类型是否已全部替换为QField
# 2. quantum_field_merge函数是否使用MergeStrategy参数

Write-Host "开始验证QEntL代码库修复..." -ForegroundColor Green

# 设置基础路径
$basePath = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "基础路径: $basePath" -ForegroundColor Yellow

# 1. 检查是否仍有QuantumField类型
Write-Host "检查QuantumField类型..." -ForegroundColor Cyan
$sourceFiles = Get-ChildItem -Path "$basePath\src" -Recurse -Include "*.c", "*.h"
$headerFiles = Get-ChildItem -Path "$basePath\include" -Recurse -Include "*.h" -ErrorAction SilentlyContinue

$allFiles = @()
$allFiles += $sourceFiles
if ($headerFiles) { $allFiles += $headerFiles }

$quantumFieldCount = 0
$problematicFiles = @()

foreach ($file in $allFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查是否有QuantumField出现在代码中（除了注释、字符串常量和QField前置）
    if ($content -match "(?<!Q)QuantumField") {
        $quantumFieldCount++
        $problematicFiles += $file.FullName
        Write-Host "  发现QuantumField类型: $($file.FullName)" -ForegroundColor Red
    }
}

if ($quantumFieldCount -eq 0) {
    Write-Host "  没有发现QuantumField类型, 类型替换完成!" -ForegroundColor Green
}
else {
    Write-Host "  发现 $quantumFieldCount 个文件中仍有QuantumField类型" -ForegroundColor Red
    Write-Host "  问题文件:" -ForegroundColor Red
    foreach ($file in $problematicFiles) {
        Write-Host "    - $file" -ForegroundColor Red
    }
}

# 2. 检查quantum_field_merge函数签名
Write-Host "检查quantum_field_merge函数签名..." -ForegroundColor Cyan
$fieldHeaderFiles = Get-ChildItem -Path "$basePath\src" -Include "quantum_field.h" -Recurse
$fieldSourceFiles = Get-ChildItem -Path "$basePath\src" -Include "quantum_field.c" -Recurse

$mergeSignatureCorrect = $true

foreach ($file in $fieldHeaderFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查函数声明
    if ($content -match "QField\*\s+quantum_field_merge\s*\(\s*QField\*\s+field1\s*,\s*QField\*\s+field2\s*,\s*const\s+char\*") {
        $mergeSignatureCorrect = $false
        Write-Host "  函数声明使用错误参数类型: $($file.FullName)" -ForegroundColor Red
    }
    elseif ($content -match "QField\*\s+quantum_field_merge\s*\(\s*QField\*\s+field1\s*,\s*QField\*\s+field2\s*,\s*MergeStrategy") {
        Write-Host "  函数声明使用正确参数类型: $($file.FullName)" -ForegroundColor Green
    }
}

foreach ($file in $fieldSourceFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查函数定义
    if ($content -match "QField\*\s+quantum_field_merge\s*\(\s*QField\*\s+field1\s*,\s*QField\*\s+field2\s*,\s*const\s+char\*") {
        $mergeSignatureCorrect = $false
        Write-Host "  函数定义使用错误参数类型: $($file.FullName)" -ForegroundColor Red
    }
    elseif ($content -match "QField\*\s+quantum_field_merge\s*\(\s*QField\*\s+field1\s*,\s*QField\*\s+field2\s*,\s*MergeStrategy") {
        Write-Host "  函数定义使用正确参数类型: $($file.FullName)" -ForegroundColor Green
    }
}

if ($mergeSignatureCorrect) {
    Write-Host "  quantum_field_merge函数签名检查通过!" -ForegroundColor Green
}
else {
    Write-Host "  quantum_field_merge函数签名检查失败，需要进一步修改!" -ForegroundColor Red
}

# 3. 检查field->strength是否已替换为field->intensity
Write-Host "检查field->strength使用情况..." -ForegroundColor Cyan
$strengthCount = 0
$problematicStrengthFiles = @()

foreach ($file in $allFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查是否有field->strength出现在代码中
    if ($content -match "field->strength") {
        $strengthCount++
        $problematicStrengthFiles += $file.FullName
        Write-Host "  发现field->strength用法: $($file.FullName)" -ForegroundColor Red
    }
}

if ($strengthCount -eq 0) {
    Write-Host "  没有发现field->strength用法, 字段名称统一完成!" -ForegroundColor Green
}
else {
    Write-Host "  发现 $strengthCount 个文件中仍有field->strength用法" -ForegroundColor Red
    Write-Host "  问题文件:" -ForegroundColor Red
    foreach ($file in $problematicStrengthFiles) {
        Write-Host "    - $file" -ForegroundColor Red
    }
}

Write-Host "验证完成!" -ForegroundColor Green 