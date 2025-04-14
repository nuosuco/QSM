@echo off
REM 设置代码页为UTF-8
chcp 65001 > nul

echo ===== QSM DLL Issues Fixer =====

REM 设置必要的环境变量和目录
set ROOT_DIR=%~dp0
set LOG_DIR=%ROOT_DIR%.logs
set TIMESTAMP=%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\dll_fix_%TIMESTAMP%.log

REM 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo Start time: %DATE% %TIME% > "%LOG_FILE%"
echo ===== Fixing DLL Issues ===== >> "%LOG_FILE%"

REM 停止现有的Python进程
echo Stopping existing Python processes...
echo Stopping existing Python processes... >> "%LOG_FILE%"
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak > nul

REM 修复kiwisolver问题
echo Fixing kiwisolver DLL issues...
echo Fixing kiwisolver DLL issues... >> "%LOG_FILE%"
py -m pip uninstall -y kiwisolver >> "%LOG_FILE%" 2>&1
py -m pip install --no-cache-dir kiwisolver==1.3.2 >> "%LOG_FILE%" 2>&1

REM 修复matplotlib问题
echo Fixing matplotlib issues...
echo Fixing matplotlib issues... >> "%LOG_FILE%"
py -m pip uninstall -y matplotlib >> "%LOG_FILE%" 2>&1
py -m pip install --no-cache-dir matplotlib==3.5.3 >> "%LOG_FILE%" 2>&1

REM 确保安装了所有必要的依赖
echo Installing required dependencies...
echo Installing required dependencies... >> "%LOG_FILE%"
py -m pip install --no-cache-dir cirq numpy flask pandas >> "%LOG_FILE%" 2>&1

echo.
echo DLL issues fixed
echo DLL issues fixed >> "%LOG_FILE%"
echo.
echo End time: %DATE% %TIME% >> "%LOG_FILE%"
echo Now you can run start_all_services_fixed.bat to start all services

pause 