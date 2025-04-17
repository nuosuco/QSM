# 修复代码库中的常见问题
# 此脚本将处理以下问题：
# 1. QuantumField和QField类型混用的问题
# 2. 数据结构定义中字段名称不一致的问题
# 3. 结构体初始化方式的问题

Write-Host "开始修复QEntL代码库中的常见问题..." -ForegroundColor Green

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

# 3. 修复结构体定义中position字段缺失问题
Write-Host "修复结构体定义中position字段缺失问题..." -ForegroundColor Cyan
$headerFiles = Get-ChildItem -Path "$basePath\src" -Include "quantum_field.h" -Recurse

foreach ($file in $headerFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查是否已有position字段
    if ($content -notmatch "position\s*;") {
        # 在结构体中添加position字段
        $pattern = 'double z;'
        $replacement = 'double z;`r`n    double* position;            // 通用位置数组，支持任意维度'
        $newContent = $content -replace [regex]::Escape($pattern), $replacement
        
        # 如果内容有变化，写回文件
        if ($content -ne $newContent) {
            Write-Host "  添加了position字段到QFieldNode结构体: $($file.FullName)" -ForegroundColor Green
            Set-Content -Path $file.FullName -Value $newContent
        }
    }
    
    # 检查是否已有FieldNode别名
    if ($content -notmatch "typedef\s+QFieldNode\s+FieldNode\s*;") {
        # 添加FieldNode类型定义
        $pattern = '} QFieldNode;'
        $replacement = '} QFieldNode;`r`n`r`n/**`r`n * 场节点（向后兼容）`r`n */`r`ntypedef QFieldNode FieldNode;'
        $newContent = $content -replace [regex]::Escape($pattern), $replacement
        
        # 如果内容有变化，写回文件
        if ($content -ne $newContent) {
            Write-Host "  添加了FieldNode类型定义: $($file.FullName)" -ForegroundColor Green
            Set-Content -Path $file.FullName -Value $newContent
        }
    }
    
    # 检查是否已有FIELD_TYPE_STRUCTURAL枚举值
    if ($content -notmatch "FIELD_TYPE_STRUCTURAL\s*,") {
        # 添加FIELD_TYPE_STRUCTURAL枚举值
        $pattern = 'FIELD_TYPE_DYNAMIC,'
        $replacement = 'FIELD_TYPE_DYNAMIC,`r`n    FIELD_TYPE_STRUCTURAL,       // 结构型量子场'
        $newContent = $content -replace [regex]::Escape($pattern), $replacement
        
        # 如果内容有变化，写回文件
        if ($content -ne $newContent) {
            Write-Host "  添加了FIELD_TYPE_STRUCTURAL枚举值: $($file.FullName)" -ForegroundColor Green
            Set-Content -Path $file.FullName -Value $newContent
        }
    }
    
    # 检查是否已有MergeStrategy枚举
    if ($content -notmatch "typedef\s+enum\s+\{\s*MERGE_") {
        # 添加MergeStrategy枚举定义
        $pattern = '} FieldBoundaryType;'
        $replacement = '} FieldBoundaryType;`r`n`r`n/**`r`n * 场合并策略`r`n */`r`ntypedef enum {`r`n    MERGE_ADD,                   // 相加`r`n    MERGE_MULTIPLY,              // 相乘`r`n    MERGE_MAX,                   // 取最大值`r`n    MERGE_MIN,                   // 取最小值`r`n    MERGE_AVERAGE,               // 取平均值`r`n    MERGE_CUSTOM                 // 自定义策略`r`n} MergeStrategy;'
        $newContent = $content -replace [regex]::Escape($pattern), $replacement
        
        # 如果内容有变化，写回文件
        if ($content -ne $newContent) {
            Write-Host "  添加了MergeStrategy枚举定义: $($file.FullName)" -ForegroundColor Green
            Set-Content -Path $file.FullName -Value $newContent
        }
    }
}

# 4. 修复测试文件中的结构体初始化问题
Write-Host "修复测试文件中的结构体初始化问题..." -ForegroundColor Cyan
$testFiles = Get-ChildItem -Path "$basePath\tests" -Include "*.c" -Recurse

foreach ($file in $testFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 替换结构体初始化方式
    $pattern = 'QFieldNode\s+node\s*=\s*\{([^}]+)\};'
    $replacement = 'QFieldNode node;`r`nnode.x = $1;`r`nnode.y = $1;`r`nnode.z = $1;`r`nnode.intensity = $1;`r`nnode.state = NULL;`r`nnode.position = NULL;  // 临时测试，实际应指向有效内存'
    $newContent = [regex]::Replace($content, $pattern, $replacement)
    
    # 如果内容有变化，写回文件
    if ($content -ne $newContent) {
        Write-Host "  修复了结构体初始化方式: $($file.FullName)" -ForegroundColor Green
        Set-Content -Path $file.FullName -Value $newContent
    }
}

# 5. 修复量子场合并函数
Write-Host "修复量子场合并函数..." -ForegroundColor Cyan
$sourceFiles = Get-ChildItem -Path "$basePath\src" -Include "quantum_field.c" -Recurse

foreach ($file in $sourceFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查是否包含合并函数
    if ($content -match "quantum_field_merge\s*\(") {
        # 查找是否使用了链表式遍历
        if ($content -match "node1\s*=\s*field1->nodes;.*?while\s*\(\s*node1\s*\)") {
            Write-Host "  需要修复quantum_field_merge函数，使用数组式遍历替代链表式: $($file.FullName)" -ForegroundColor Yellow
            
            # 这个替换比较复杂，可能需要手动处理
            # 创建一个标记文件提示需要手动检查
            $markFile = "$basePath\needs_manual_fix.txt"
            if (-not (Test-Path $markFile)) {
                "以下文件需要手动检查合并函数：" | Set-Content -Path $markFile
            }
            $file.FullName | Add-Content -Path $markFile
        }
    }
}

Write-Host "修复完成！" -ForegroundColor Green
Write-Host "请注意：某些复杂问题可能需要手动检查和修复，详见needs_manual_fix.txt（如果存在）" -ForegroundColor Yellow
Write-Host "按任意键退出..." -ForegroundColor Cyan 