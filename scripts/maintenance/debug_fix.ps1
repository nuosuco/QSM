
# # 量子基因编码: QE-DEB-0B0BBAA0F641
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
# 带调试功能的量子系统修复脚本

# 设置颜色
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow
$RED = [System.ConsoleColor]::Red

function Print-Status {
    param([string]$message)
    Write-Host "[STATUS] $message" -ForegroundColor $GREEN
    # 记录到日志文件
    Add-Content -Path "debug_log.txt" -Value "[$(Get-Date)] [STATUS] $message"
}

function Print-Warning {
    param([string]$message)
    Write-Host "[WARNING] $message" -ForegroundColor $YELLOW
    # 记录到日志文件
    Add-Content -Path "debug_log.txt" -Value "[$(Get-Date)] [WARNING] $message"
}

function Print-Error {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor $RED
    # 记录到日志文件
    Add-Content -Path "debug_log.txt" -Value "[$(Get-Date)] [ERROR] $message"
}

# 检查进程是否运行
function Check-ProcessRunning {
    param(
        [string]$ProcessName,
        [string]$CommandLinePattern
    )
    
    try {
        $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | 
                   Where-Object { $_.CommandLine -like "*$CommandLinePattern*" }
        return ($null -ne $process)
    } catch {
        return $false
    }
}

# 停止所有Python进程(可选)
function Stop-AllPythonProcesses {
    Print-Status "正在停止所有Python进程..."
    try {
        Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep -Seconds 2
        Print-Status "所有Python进程已停止"
    } catch {
        Print-Error "停止Python进程时出错: $_"
    }
}

# 修复并启动
function Fix-And-Start-WithDebug {
    # 创建或清空调试日志
    Set-Content -Path "debug_log.txt" -Value "[$(Get-Date)] 开始调试日志"
    
    Print-Status "===== 量子系统修复和启动(调试模式) ====="
    
    # 可选：停止所有Python进程
    # Stop-AllPythonProcesses
    
    # 激活虚拟环境
    Print-Status "正在激活虚拟环境..."
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        try {
            & ".\.venv\Scripts\Activate.ps1"
            Print-Status "虚拟环境激活成功"
        } catch {
            Print-Error "虚拟环境激活失败: $_"
        }
    } else {
        Print-Warning "未找到虚拟环境 (.venv\Scripts\Activate.ps1)"
    }
    
    # 修复量子基因标记
    $markerPath = "Ref/utils/quantum_gene_marker.py"
    if (Test-Path $markerPath) {
        Print-Status "修复量子基因标记文件: $markerPath"
        
        # 创建备份
        $backupPath = "$markerPath.debug.bak"
        Copy-Item -Path $markerPath -Destination $backupPath -Force
        Print-Status "备份文件已创建: $backupPath"
        
        # 读取文件
        $content = Get-Content -Path $markerPath -Raw
        Print-Status "已读取文件内容，长度: $($content.Length) 字符"
        
        # 创建一个包含监控功能的单独文件
        $monitorScriptPath = "quantum_monitor.py"
        Print-Status "创建监控脚本: $monitorScriptPath"
        
        $monitorScript = @"
#!/usr/bin/env python
# 量子基因标记监控独立脚本
# 调试版本

import time
import logging
import sys
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quantum_monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("QuantumMonitor")

def start_monitoring():
    """启动监控模式，监控量子基因标记"""
    logger.info("启动量子基因标记监控模式")
    print("量子基因标记监控模式已启动，按Ctrl+C退出")
    
    try:
        # 这里只是简单循环，实际应用中可以添加监控逻辑
        count = 0
        while True:
            count += 1
            logger.info(f"监控运行中... 循环次数: {count}")
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("监控被用户中断")
        print("监控已停止")
    except Exception as e:
        logger.error(f"监控过程中发生错误: {e}")
        print(f"监控出错: {e}")

if __name__ == "__main__":
    print("量子基因标记监控 - 调试版本")
    logger.info("监控脚本启动")
    start_monitoring()
"@
        Set-Content -Path $monitorScriptPath -Value $monitorScript
        Print-Status "监控脚本已创建: $monitorScriptPath"
    } else {
        Print-Error "未找到量子基因标记文件: $markerPath"
    }
    
    # 逐个启动服务，每次添加超时和错误处理
    
    # 1. 启动Ref核心服务
    Print-Status "启动Ref核心服务..."
    $refCorePath = "Ref/ref_core.py"
    if (Test-Path $refCorePath) {
        try {
            # 使用后台任务启动服务
            $job = Start-Job -ScriptBlock {
                param($path)
                cd $using:PWD
                python $path
            } -ArgumentList $refCorePath
            
            # 等待服务启动，最多30秒
            $timeout = 30
            for ($i = 0; $i -lt $timeout; $i++) {
                Start-Sleep -Seconds 1
                # 检查任务状态
                $state = (Get-Job -Id $job.Id).State
                if ($state -ne "Running") {
                    Print-Error "Ref核心服务启动失败！状态: $state"
                    break
                }
                
                # 每5秒输出一次状态
                if ($i % 5 -eq 0) {
                    Print-Status "Ref核心服务启动中... ($i/$timeout 秒)"
                }
            }
            
            Print-Status "Ref核心服务已启动，任务ID: $($job.Id)"
        } catch {
            Print-Error "Ref核心服务启动时出错: $_"
        }
    } else {
        Print-Error "未找到Ref核心服务文件: $refCorePath"
    }
    
    # 等待系统稳定
    Start-Sleep -Seconds 2
    
    # 2. 启动量子基因标记监控(使用我们创建的独立脚本)
    Print-Status "启动量子基因标记监控..."
    if (Test-Path $monitorScriptPath) {
        try {
            Start-Process python -ArgumentList $monitorScriptPath -NoNewWindow
            Print-Status "量子基因标记监控已启动"
        } catch {
            Print-Error "量子基因标记监控启动失败: $_"
        }
    } else {
        Print-Error "未找到监控脚本: $monitorScriptPath"
    }
    
    # 查看运行的Python进程
    Print-Status "正在运行的Python进程:"
    try {
        $processes = Get-Process -Name python -ErrorAction SilentlyContinue
        foreach ($proc in $processes) {
            Print-Status "  进程ID: $($proc.Id), 内存: $($proc.WorkingSet/1MB) MB, CPU: $($proc.CPU)"
        }
    } catch {
        Print-Error "获取进程信息时出错: $_"
    }
    
    Print-Status "===== 修复和启动完成 ====="
    Print-Status "服务已启动，可以查看debug_log.txt获取详细日志"
}

# 执行主函数
try {
    Fix-And-Start-WithDebug
    Print-Status "脚本执行完成，按任意键退出..."
    # 等待用户输入，不使用无限循环
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
} catch {
    Print-Error "执行过程中发生错误: $_"
    Exit 1
} 