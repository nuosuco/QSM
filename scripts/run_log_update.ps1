#!/usr/bin/env pwsh
#
# 日志路径更新工具启动脚本
# 此脚本用于测试和运行日志路径更新工具

# 确保.logs目录存在
$logsDir = ".logs"
if (-not (Test-Path $logsDir)) {
    New-Item -Path $logsDir -ItemType Directory | Out-Null
    Write-Host "Created .logs directory at $(Resolve-Path $logsDir)" -ForegroundColor Green
}

# 定义颜色函数
function Write-Status {
    param([string]$message)
    Write-Host "[STATUS] $message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$message)
    Write-Host "[WARNING] $message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

function Write-Success {
    param([string]$message)
    Write-Host "[SUCCESS] $message" -ForegroundColor Green
}

# 确保scripts/test_cases目录存在
$testCasesDir = "scripts/test_cases"
if (-not (Test-Path $testCasesDir)) {
    New-Item -Path $testCasesDir -ItemType Directory -Force | Out-Null
    Write-Status "Created test cases directory at $(Resolve-Path $testCasesDir)"
}

# 检查测试用例是否存在
$testCase = "$testCasesDir/test_log_paths.py"
if (-not (Test-Path $testCase)) {
    Write-Warning "Test case file not found at $testCase"
}
else {
    Write-Status "Test case file found at $testCase"
}

# 检查更新脚本是否存在
$updateScript = "scripts/update_log_paths.py"
if (-not (Test-Path $updateScript)) {
    Write-Error "Update script not found at $updateScript"
    exit 1
}

Write-Status "Starting log path update process..."

# 解析命令行参数
$testMode = $false
$dryRun = $false
$restore = $false
$verbose = $false
$addLogConfig = $false
$excludePatterns = @()

foreach ($arg in $args) {
    switch -Regex ($arg) {
        "--test" { $testMode = $true }
        "--dry-run" { $dryRun = $true }
        "--restore" { $restore = $true }
        "--verbose" { $verbose = $true }
        "--add-log-config" { $addLogConfig = $true }
        "--exclude" { 
            # 下一个参数是排除模式，不在这里处理
            # 会在后面根据需要构建完整的参数列表
        }
    }
}

# 构建命令行参数列表
$cmdArgs = @()
if ($dryRun) { $cmdArgs += "--dry-run" }
if ($verbose) { $cmdArgs += "--verbose" }
if ($addLogConfig) { $cmdArgs += "--add-log-config" }

# 处理排除模式
$excludeIndex = [array]::IndexOf($args, "--exclude")
if ($excludeIndex -ge 0 -and $excludeIndex -lt $args.Length - 1) {
    $cmdArgs += "--exclude"
    # 收集所有在--exclude后面且不是以--开头的参数
    for ($i = $excludeIndex + 1; $i -lt $args.Length; $i++) {
        if ($args[$i] -notmatch "^--") {
            $cmdArgs += $args[$i]
        } else {
            break
        }
    }
}

# 如果传入了--test参数，则只运行测试用例
if ($testMode) {
    Write-Status "Running in test mode..."
    
    # 运行更新脚本，只处理测试目录
    $testArgs = $cmdArgs + $testCasesDir
    Write-Status "Command: python $updateScript $($testArgs -join ' ')"
    python $updateScript $testArgs
    
    # 检查测试用例文件更新后的结果
    Write-Status "Test completed. Please check the update results in $testCase"
    
    # 展示更新后的文件内容
    Write-Status "Updated test case content:"
    Get-Content $testCase | ForEach-Object {
        if ($_ -match "os\.path\.join") {
            Write-Host $_ -ForegroundColor Green
        }
        else {
            Write-Host $_
        }
    }
}
else {
    # 如果是干运行模式，不需要确认
    if (-not $dryRun) {
        # 询问用户确认是否运行完整更新
        $confirmation = Read-Host "This will update log paths in all Python files in the project. Continue? (y/n)"
        if ($confirmation -ne 'y') {
            Write-Warning "Operation cancelled by user."
            exit 0
        }
    }
    else {
        Write-Status "Running in dry-run mode - no files will be modified."
    }
    
    # 运行更新脚本，处理整个项目
    $projectArgs = $cmdArgs + "."
    Write-Status "Command: python $updateScript $($projectArgs -join ' ')"
    python $updateScript $projectArgs
    
    if ($dryRun) {
        Write-Success "Dry run completed. Check the log file at .logs/update_log_paths.log for details."
    } else {
        Write-Success "Log path update completed. Check the log file at .logs/update_log_paths.log for details."
    }
}

# 如果传入了--restore参数，则还原测试用例文件
if ($restore) {
    Write-Status "Restoring test case file to original state..."
    
    # 这里可以实现还原测试用例的逻辑，如果需要的话
    # 例如，可以保存一个备份，或者重新生成测试用例文件
    
    Write-Status "Test case file restored."
}

Write-Status "Done!" 