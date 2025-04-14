@echo off
REM 设置代码页为UTF-8
chcp 65001 > nul

echo ===== QSM Services Stopper =====

REM 设置必要的环境变量和目录
set ROOT_DIR=%~dp0..\..
set LOG_DIR=%ROOT_DIR%\.logs
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\services_stop_%TIMESTAMP%.log

REM 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Start time: %DATE% %TIME% > "%LOG_FILE%"
echo ===== Stopping QSM Services ===== >> "%LOG_FILE%"

echo Stopping all Python processes...
echo Stopping all Python processes... >> "%LOG_FILE%"

REM 列出当前运行的Python进程
echo Current Python processes:
echo Current Python processes: >> "%LOG_FILE%"
tasklist /FI "IMAGENAME eq python.exe" /V
tasklist /FI "IMAGENAME eq python.exe" /V >> "%LOG_FILE%"

REM 使用Python脚本停止所有服务
echo Running Python service stopper...
echo Running Python service stopper... >> "%LOG_FILE%"
py -u "%ROOT_DIR%\scripts\services\stop_all_services.py"
if %ERRORLEVEL% NEQ 0 (
    echo Python service stopper failed with error code %ERRORLEVEL%
    echo Python service stopper failed with error code %ERRORLEVEL% >> "%LOG_FILE%"
    
    REM 如果Python脚本失败，尝试直接终止所有Python进程
    echo Forcibly terminating all Python processes...
    echo Forcibly terminating all Python processes... >> "%LOG_FILE%"
    taskkill /F /IM python.exe 2>nul
)

echo All Python processes terminated
echo All Python processes terminated >> "%LOG_FILE%"

echo.
echo All services stopped
echo All services stopped >> "%LOG_FILE%"
echo End time: %DATE% %TIME% >> "%LOG_FILE%"

pause 