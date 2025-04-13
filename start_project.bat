@echo off
chcp 65001 > nul
echo ===================================
echo 量子叠加态模型（QSM）项目启动脚本
echo ===================================

REM 设置环境变量
set QSM_ROOT=%~dp0
set QSM_LOG_DIR=%QSM_ROOT%.logs
set QENTL_PATH=%QSM_ROOT%QEntL-env\bin

REM 创建日志目录
if not exist "%QSM_LOG_DIR%" mkdir "%QSM_LOG_DIR%"

echo 正在启动QSM项目...
echo 日志位置: %QSM_LOG_DIR%
echo 项目根目录: %QSM_ROOT%
echo QEntl路径: %QENTL_PATH%

REM 检查QEntl解释器
if not exist "%QENTL_PATH%\qentl.bat" (
    echo QEntl解释器未找到，正在准备...
    if not exist "%QENTL_PATH%" (
        mkdir "%QENTL_PATH%"
    )
    
    REM 无需构建，我们已经有了批处理版本
    if not exist "%QENTL_PATH%\qentl.bat" (
        echo 错误: QEntl解释器准备失败
        pause
        exit /b 1
    )
)

REM 先确保没有遗留进程
call "%QSM_ROOT%stop_project.bat" > nul 2>&1
timeout /t 2 > nul

REM 检查Python是否可用
python --version > nul 2>&1
if %errorlevel% NEQ 0 (
    echo 错误: Python未安装或未添加到PATH中
    pause
    exit /b 1
)
echo Python环境检查通过

REM 在后台启动QSM主服务
echo 正在启动QSM主控服务...
echo 命令: "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%run.qpy"
start /b cmd /c "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%run.qpy" ^> "%QSM_LOG_DIR%\main_service.log" 2^>^&1
if %errorlevel% NEQ 0 (
    echo 启动QSM主控服务失败，错误码: %errorlevel%
)

REM 等待主服务启动
echo 等待主服务启动...
timeout /t 3 > nul

REM 在后台启动QSM API服务
echo 正在启动QSM API服务...
echo 命令: "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%QSM\api\qsm_api.qpy"
start /b cmd /c "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%QSM\api\qsm_api.qpy" ^> "%QSM_LOG_DIR%\qsm_api.log" 2^>^&1
if %errorlevel% NEQ 0 (
    echo 启动QSM API服务失败，错误码: %errorlevel%
)

REM 等待QSM API服务启动
timeout /t 2 > nul

REM 在后台启动WeQ API服务
echo 正在启动WeQ API服务...
echo 命令: "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%WeQ\api\weq_api.qpy"
start /b cmd /c "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%WeQ\api\weq_api.qpy" ^> "%QSM_LOG_DIR%\weq_api.log" 2^>^&1
if %errorlevel% NEQ 0 (
    echo 启动WeQ API服务失败，错误码: %errorlevel%
)

REM 等待WeQ API服务启动
timeout /t 2 > nul

REM 在后台启动SOM API服务
echo 正在启动SOM API服务...
echo 命令: "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%SOM\api\som_api.qpy"
start /b cmd /c "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%SOM\api\som_api.qpy" ^> "%QSM_LOG_DIR%\som_api.log" 2^>^&1
if %errorlevel% NEQ 0 (
    echo 启动SOM API服务失败，错误码: %errorlevel%
)

REM 等待SOM API服务启动
timeout /t 2 > nul

REM 在后台启动Ref API服务
echo 正在启动Ref API服务...
echo 命令: "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%Ref\api\ref_api.qpy"
start /b cmd /c "%QENTL_PATH%\qentl.bat" "%QSM_ROOT%Ref\api\ref_api.qpy" ^> "%QSM_LOG_DIR%\ref_api.log" 2^>^&1
if %errorlevel% NEQ 0 (
    echo 启动Ref API服务失败，错误码: %errorlevel%
)

REM 等待Ref API服务启动
timeout /t 2 > nul

echo.
echo QSM项目已启动！
echo 所有服务已在后台运行，日志输出到 %QSM_LOG_DIR% 目录
echo 您可以通过访问 http://localhost:3000 查看服务状态
echo.

REM 检查服务状态
echo 服务进程ID信息：
wmic process where "commandline like '%%qentl.bat%%'" get processid,commandline

REM 检查日志文件是否生成
echo.
echo 检查服务日志：
dir "%QSM_LOG_DIR%\*_api.log" /b
if %errorlevel% NEQ 0 (
    echo 警告: 部分服务日志可能未正确生成
)

REM 检查端口是否被监听
echo.
echo 检查服务端口：
netstat -ano | findstr ":3000" | findstr "LISTENING"
if %errorlevel% NEQ 0 (
    echo 警告: 主控服务端口3000未被监听
)

netstat -ano | findstr ":5000" | findstr "LISTENING"
if %errorlevel% NEQ 0 (
    echo 警告: QSM API服务端口5000未被监听
)

netstat -ano | findstr ":5001" | findstr "LISTENING"
if %errorlevel% NEQ 0 (
    echo 警告: WeQ API服务端口5001未被监听
)

echo.
echo 如需查看详细日志，请查看 %QSM_LOG_DIR% 目录下的日志文件
echo 如需停止所有服务，请运行 stop_project.bat
echo. 