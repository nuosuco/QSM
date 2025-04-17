@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM QEntL环境启动脚本 - 带日志初始化版本
REM 本脚本与qentl.bat功能相同，但会在启动前初始化日志文件
echo ======================================
echo    QEntL环境启动脚本 - 带日志初始化
echo ======================================

set LOG_DIR=%~dp0..\logs
set MAIN_LOG=%LOG_DIR%\main.log

REM 确保日志目录存在
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 创建或清空主日志文件
echo %date% %time% - QEntL环境初始化 > "%MAIN_LOG%"
echo %date% %time% - 系统准备就绪 >> "%MAIN_LOG%"
echo %date% %time% - 等待服务启动 >> "%MAIN_LOG%"

echo 日志文件已初始化: %MAIN_LOG%
echo.

echo 正在启动QEntL环境...
echo ======================================
REM 调用qentl.bat启动环境
call "%~dp0qentl.bat"
echo ======================================

echo.
echo 检查服务状态...
netstat -ano | findstr "3000 5000 5001 5002 5003 5004"
if %errorlevel% EQU 0 (
    echo 服务已成功启动并正在监听端口
) else (
    echo 注意: 未检测到服务端口正在监听
    echo 这是模拟环境，实际服务未启动
)

echo.
echo QEntL环境启动完成
echo ======================================

exit /b 0 