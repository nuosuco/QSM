@echo off
echo 正在启动world目录同步工具...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保已安装Python并添加到PATH环境变量中
    pause
    exit /b 1
)

REM 运行同步脚本
if "%1"=="--watch" (
    echo 启动监视模式，将自动同步world目录的变化...
    python sync_world.py --watch
) else (
    echo 执行单次同步...
    python sync_world.py
)

if errorlevel 1 (
    echo 同步过程中出现错误，请查看world_sync.log文件了解详细信息
    pause
    exit /b 1
) else (
    echo 同步完成
    pause
) 