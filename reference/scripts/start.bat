@echo off
REM QSM系统启动脚本 - Windows版

echo 正在启动QSM系统...

REM 创建必要的目录
if not exist "QSM\logs" mkdir "QSM\logs"
if not exist "Ref\logs" mkdir "Ref\logs"
if not exist "Ref\data" mkdir "Ref\data"
if not exist "Ref\backup\files" mkdir "Ref\backup\files"

REM 检查是否安装了watchdog库
python -c "import watchdog" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 正在安装必要的依赖...
    pip install watchdog
)

REM 启动QSM系统
python QSM/main.py %*

echo QSM系统已停止 