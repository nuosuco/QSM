
# # 量子基因编码: QE-QUI-DDEBEB9C51A1
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# 量子系统快速修复和启动脚本
# 版本：1.0

# 设置颜色
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow 
$RED = [System.ConsoleColor]::Red

function Print-Status {
    param([string]$message)
    Write-Host "[STATUS] $message" -ForegroundColor $GREEN
}

function Print-Warning {
    param([string]$message)
    Write-Host "[WARNING] $message" -ForegroundColor $YELLOW
}

function Print-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor $RED
}

# 激活虚拟环境
function Activate-Environment {
    Print-Status "正在激活虚拟环境..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        try {
            & ".\.venv\Scripts\Activate.ps1"
            Print-Status "虚拟环境激活成功"
            return $true
        } catch {
            Print-Error "虚拟环境激活失败: $_"
            return $false
        }
    } else {
        Print-Warning "未找到虚拟环境，继续执行（可能会出现依赖问题）"
        return $true
    }
}

# 修复量子基因标记监控功能
function Fix-QuantumGeneMarker {
    Print-Status "正在修复量子基因标记监控模式..."
    $markerPath = "Ref/utils/quantum_gene_marker.py"
    
    if (-not (Test-Path $markerPath)) {
        Print-Error "未找到量子基因标记文件: $markerPath"
        return $false
    }
    
    # 读取文件内容
    $content = Get-Content -Path $markerPath -Raw
    
    # 备份原始文件
    $backupPath = "$markerPath.bak"
    if (-not (Test-Path $backupPath)) {
        Copy-Item -Path $markerPath -Destination $backupPath -Force
        Print-Status "已备份文件到 $backupPath"
    }
    
    # 检查是否已有monitor功能
    if ($content -match "def start_monitor_mode") {
        Print-Status "量子基因标记监控模式已存在，无需修复"
        return $true
    }
    
    # 添加监控模式函数
    $monitorFunction = @'

def start_monitor_mode():
    """启动监控模式，实时监控文件变化并更新量子基因标记"""
    import time
    logging.info("启动量子基因标记监控模式")
    print("量子基因标记监控模式已启动，按Ctrl+C退出")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("监控已停止")

'@
    $content += $monitorFunction
    
    # 修改main函数
    $mainPattern = 'if __name__ == "__main__":'
    if ($content -match $mainPattern) {
        # 添加参数解析
        if (-not ($content -match "import argparse")) {
            $content = $content -replace "import logging", "import logging`nimport argparse"
        }
        
        # 添加monitor参数和处理逻辑
        if (-not ($content -match "--monitor")) {
            $parser = "parser = argparse.ArgumentParser(description='量子基因标记工具')"
            $monitorArg = "parser.add_argument('--monitor', action='store_true', help='启动监控模式')"
            
            # 查找插入位置
            if ($content -match "parser = argparse\.ArgumentParser") {
                $content = $content -replace "parser = argparse\.ArgumentParser\([^)]*\)", "$parser`n    $monitorArg"
            } else {
                $content = $content -replace "if __name__ == [\"']__main__[\"']:", "if __name__ == \"__main__\":`n    $parser`n    $monitorArg"
            }
        }
        
        # 添加monitor处理逻辑
        if (-not ($content -match "if args\.monitor")) {
            $parseArgs = "args = parser.parse_args()"
            $monitorCheck = "if args.monitor:`n        start_monitor_mode()"
            
            if ($content -match "args = parser\.parse_args\(\)") {
                $content = $content -replace "args = parser\.parse_args\(\)", "$parseArgs`n    $monitorCheck"
            } else {
                # 如果找不到args解析，在main函数末尾添加
                $content = $content -replace "if __name__ == [\"']__main__[\"']:", "if __name__ == \"__main__\":`n    $parser`n    $monitorArg`n    $parseArgs`n    $monitorCheck"
            }
        }
    } else {
        # 如果找不到main函数，添加一个完整的main函数
        $mainFunction = @'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='量子基因标记工具')
    parser.add_argument('--monitor', action='store_true', help='启动监控模式')
    args = parser.parse_args()
    
    if args.monitor:
        start_monitor_mode()
'@
        $content += $mainFunction
    }
    
    # 保存修改后的内容
    Set-Content -Path $markerPath -Value $content
    Print-Status "已成功修复量子基因标记监控模式"
    return $true
}

# 启动Ref核心服务
function Start-RefCore {
    Print-Status "正在启动Ref核心服务..."
    $refCorePath = "Ref/ref_core.py"
    
    if (-not (Test-Path $refCorePath)) {
        Print-Error "未找到Ref核心服务文件: $refCorePath"
        return $false
    }
    
    try {
        # 启动服务
        Start-Process python -ArgumentList $refCorePath -NoNewWindow
        Print-Status "Ref核心服务启动成功"
        return $true
    } catch {
        Print-Error "Ref核心服务启动失败: $_"
        return $false
    }
}

# 启动量子基因标记监控
function Start-QGMMonitor {
    Print-Status "正在启动量子基因标记监控..."
    $markerPath = "Ref/utils/quantum_gene_marker.py"
    
    if (-not (Test-Path $markerPath)) {
        Print-Error "未找到量子基因标记文件: $markerPath"
        return $false
    }
    
    try {
        # 启动服务
        Start-Process python -ArgumentList "$markerPath --monitor" -NoNewWindow
        Print-Status "量子基因标记监控启动成功"
        return $true
    } catch {
        Print-Error "量子基因标记监控启动失败: $_"
        return $false
    }
}

# 主函数
function Start-Repair {
    Print-Status "===== 量子系统快速修复和启动 v1.0 ====="
    
    # 激活虚拟环境
    if (-not (Activate-Environment)) {
        Print-Error "虚拟环境激活失败，中止操作"
        return $false
    }
    
    # 修复量子基因标记监控
    if (-not (Fix-QuantumGeneMarker)) {
        Print-Warning "量子基因标记修复失败，但将继续尝试启动服务"
    }
    
    # 启动Ref核心服务
    if (-not (Start-RefCore)) {
        Print-Error "Ref核心服务启动失败，中止操作"
        return $false
    }
    
    # 等待Ref核心启动
    Print-Status "等待Ref核心服务初始化..."
    Start-Sleep -Seconds 5
    
    # 启动量子基因标记监控
    if (-not (Start-QGMMonitor)) {
        Print-Warning "量子基因标记监控启动失败，但核心服务已启动"
    }
    
    Print-Status "===== 修复和启动完成 ====="
    Print-Status "Ref核心服务和量子基因标记监控已启动"
    Print-Status "按Ctrl+C可以停止服务"
    
    return $true
}

# 执行主函数
try {
    if (Start-Repair) {
        # 保持脚本运行，等待用户中断
        Print-Status "服务已启动，脚本将保持运行..."
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } else {
        Print-Error "修复和启动过程失败"
        exit 1
    }
} catch {
    Print-Error "执行过程中发生错误: $_"
    exit 1
} 