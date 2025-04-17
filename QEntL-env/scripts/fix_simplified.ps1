# 简化版修复脚本
# 专注修复以下问题：
# 1. QuantumField和QField类型混用的问题
# 2. quantum_field_merge函数中MergeStrategy类型的使用

Write-Host "开始修复QEntL代码库中的关键问题..." -ForegroundColor Green

# 设置基础路径
$basePath = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Host "基础路径: $basePath" -ForegroundColor Yellow

# 1. 修复类型名称问题 - 将QuantumField替换为QField
Write-Host "修复类型名称问题..." -ForegroundColor Cyan
$sourceFiles = Get-ChildItem -Path "$basePath\src" -Recurse -Include "*.c", "*.h"
$headerFiles = Get-ChildItem -Path "$basePath\include" -Recurse -Include "*.h" -ErrorAction SilentlyContinue

$allFiles = @()
$allFiles += $sourceFiles
if ($headerFiles) { $allFiles += $headerFiles }

foreach ($file in $allFiles) {
    Write-Host "处理文件: $($file.FullName)" -ForegroundColor Gray
    
    # 读取文件内容
    $content = Get-Content -Path $file.FullName -Raw
    
    # 替换类型名称
    $newContent = $content -replace "QuantumField\s*\*", "QField*" `
                          -replace "struct\s+QuantumField\s*\*", "struct QField*" `
                          -replace "\bQuantumField\b(?!\s*\{)", "QField"
    
    # 如果内容有变化，写回文件
    if ($content -ne $newContent) {
        Write-Host "  修复了类型名称问题" -ForegroundColor Green
        Set-Content -Path $file.FullName -Value $newContent
    }
}

# 2. 修复字段名称不一致问题
Write-Host "修复字段名称不一致问题..." -ForegroundColor Cyan
foreach ($file in $allFiles) {
    # 读取文件内容
    $content = Get-Content -Path $file.FullName -Raw
    
    # 替换字段名称
    $newContent = $content -replace "field->strength", "field->intensity" `
                          -replace "node1->next", "node1 = field1->nodes[++i]" `
                          -replace "node2->next", "node2 = field2->nodes[++j]"
    
    # 如果内容有变化，写回文件
    if ($content -ne $newContent) {
        Write-Host "  修复了字段名称不一致问题: $($file.FullName)" -ForegroundColor Green
        Set-Content -Path $file.FullName -Value $newContent
    }
}

# 3. 修复quantum_field_merge函数
Write-Host "修复量子场合并函数参数类型..." -ForegroundColor Cyan
$sourceFiles = Get-ChildItem -Path "$basePath\src" -Include "quantum_field.c" -Recurse

foreach ($file in $sourceFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 修复quantum_field_merge函数的参数
    $oldSignature = 'QField\* quantum_field_merge\(QField\* field1, QField\* field2, const char\* name\)'
    $newSignature = 'QField* quantum_field_merge(QField* field1, QField* field2, MergeStrategy strategy)'
    $newContent = $content -replace $oldSignature, $newSignature
    
    # 修复函数内部的name参数使用
    if ($content -ne $newContent) {
        # 修改函数内部代码，根据strategy参数替代原来的name参数
        $newContent = $newContent -replace 'strcmp\(field1->name, ""\) != 0.+?strdup\(field1->name\).+?field2->name.+?:.*?"merged_field"', '(field1->name && strlen(field1->name) > 0 && field2->name && strlen(field2->name) > 0) ? strcat(strcat(strdup(field1->name), "_"), field2->name) : "merged_field"'
        
        Write-Host "  修复了quantum_field_merge函数签名: $($file.FullName)" -ForegroundColor Green
        Set-Content -Path $file.FullName -Value $newContent
    }
}

# 4. 确保在头文件中正确定义MergeStrategy枚举
Write-Host "确保MergeStrategy枚举定义存在..." -ForegroundColor Cyan
$headerFiles = Get-ChildItem -Path "$basePath\src" -Include "quantum_field.h" -Recurse

foreach ($file in $headerFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查是否已有MergeStrategy枚举
    if ($content -notmatch "typedef\s+enum\s+\{.*?MERGE_ADD") {
        # 在合适的位置添加MergeStrategy枚举定义
        $addPoint = "typedef enum \{"
        $mergeEnum = @"
typedef enum {
    MERGE_ADD,                   // 相加
    MERGE_MULTIPLY,              // 相乘
    MERGE_MAX,                   // 取最大值
    MERGE_MIN,                   // 取最小值
    MERGE_AVERAGE,               // 取平均值
    MERGE_CUSTOM                 // 自定义策略
} MergeStrategy;

"@
        
        # 在适当位置添加枚举定义
        if ($content -match "typedef\s+enum\s+\{.*?FieldType;") {
            $newContent = $content -replace "(typedef\s+enum\s+\{.*?FieldType;)", "`$1`r`n`r`n/**`r`n * 场合并策略`r`n */`r`n$mergeEnum"
            
            if ($content -ne $newContent) {
                Write-Host "  添加了MergeStrategy枚举定义: $($file.FullName)" -ForegroundColor Green
                Set-Content -Path $file.FullName -Value $newContent
            }
        }
    }

    # 修改quantum_field_merge函数声明
    $content = Get-Content -Path $file.FullName -Raw
    $oldDeclaration = 'QField\* quantum_field_merge\(QField\* field1, QField\* field2, const char\* name\);'
    $newDeclaration = 'QField* quantum_field_merge(QField* field1, QField* field2, MergeStrategy strategy);'
    $newContent = $content -replace $oldDeclaration, $newDeclaration
    
    if ($content -ne $newContent) {
        Write-Host "  修复了quantum_field_merge函数声明: $($file.FullName)" -ForegroundColor Green
        Set-Content -Path $file.FullName -Value $newContent
    }
}

Write-Host "简化修复完成！" -ForegroundColor Green 