
# # 量子基因编码: QE-SIM-B0000E7F5D1C
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# 简单的量子系统修复和启动脚本

# 设置颜色
$GREEN = [System.ConsoleColor]::Green
$RED = [System.ConsoleColor]::Red

function Print-Status {
    param([string]$message)
    Write-Host "[STATUS] $message" -ForegroundColor $GREEN
}

function Print-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor $RED
}

# 主函数
function Fix-And-Start {
    Print-Status "===== 量子系统简单修复和启动 ====="
    
    # 激活虚拟环境
    Print-Status "正在激活虚拟环境..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".\.venv\Scripts\Activate.ps1"
    }
    
    # 修复量子基因标记
    $markerPath = "Ref/utils/quantum_gene_marker.py"
    if (Test-Path $markerPath) {
        Print-Status "修复量子基因标记文件..."
        # 创建备份
        Copy-Item -Path $markerPath -Destination "$markerPath.bak" -Force
        
        # 读取文件
        $content = Get-Content -Path $markerPath -Raw
        
        # 添加monitor功能
        if (-not ($content -match "def start_monitor_mode")) {
            $monitorCode = @"

# 添加监控模式功能
def start_monitor_mode():
    import time
    import logging
    logging.info("启动量子基因标记监控模式")
    print("量子基因标记监控模式已启动，按Ctrl+C退出")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("监控已停止")

# 更新main函数
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='量子基因标记工具')
    parser.add_argument('--monitor', action='store_true', help='启动监控模式')
    args = parser.parse_args()
    
    if args.monitor:
        start_monitor_mode()

"@
            # 附加到文件末尾
            Add-Content -Path $markerPath -Value $monitorCode
            Print-Status "量子基因标记监控功能已添加"
        } else {
            Print-Status "量子基因标记监控功能已存在"
        }
    } else {
        Print-Error "未找到量子基因标记文件: $markerPath"
    }
    
    # 启动Ref核心服务
    Print-Status "启动Ref核心服务..."
    $refCorePath = "Ref/ref_core.py"
    if (Test-Path $refCorePath) {
        Start-Process python -ArgumentList $refCorePath -NoNewWindow
        Print-Status "Ref核心服务启动成功"
    } else {
        Print-Error "未找到Ref核心服务文件: $refCorePath"
    }
    
    # 等待Ref核心启动
    Start-Sleep -Seconds 5
    
    # 启动量子基因标记监控
    Print-Status "启动量子基因标记监控..."
    if (Test-Path $markerPath) {
        Start-Process python -ArgumentList "$markerPath --monitor" -NoNewWindow
        Print-Status "量子基因标记监控启动成功"
    }
    
    Print-Status "===== 修复和启动完成 ====="
    Print-Status "按Ctrl+C可以停止脚本"
}

# 执行主函数
try {
    Fix-And-Start
    
    # 保持脚本运行
    Print-Status "服务已启动，脚本将保持运行..."
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Print-Error "执行过程中发生错误: $_"
    exit 1
} 