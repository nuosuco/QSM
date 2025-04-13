@echo off
echo 正在启动QEntL UI服务...

:: 设置必要的环境变量
set QENTL_ROOT=%~dp0
set QENTL_ENGINE=%QENTL_ROOT%QEntL-env\bin\qentl.exe
set TEMPLATES_DIR=%QENTL_ROOT%world\templates

:: 检查QEntL引擎是否存在
if not exist "%QENTL_ENGINE%" (
    echo 错误: 未找到QEntL引擎 - %QENTL_ENGINE%
    echo 请先运行 QEntL-env\build.bat 编译QEntL引擎
    pause
    exit /b 1
)

:: 启动API服务
start cmd /k "cd %QENTL_ROOT%QSM\api && python qsm_api.qpy"
echo QSM API 服务已启动 (端口: 5000)
timeout /t 2 > nul

start cmd /k "cd %QENTL_ROOT%WeQ\api && python weq_api.qpy"
echo WeQ API 服务已启动 (端口: 5001)
timeout /t 2 > nul

start cmd /k "cd %QENTL_ROOT%SOM\api && python som_api.qpy"
echo SOM API 服务已启动 (端口: 5002)
timeout /t 2 > nul

:: 启动QEntL UI服务
echo 正在启动QEntL UI渲染引擎...
start cmd /k "cd %TEMPLATES_DIR% && %QENTL_ENGINE% serve --port 8080 --templates ."

echo.
echo QEntL UI已启动！请访问: http://localhost:8080
echo.
echo 按任意键结束所有服务...
pause > nul

:: 结束所有启动的服务
taskkill /f /im python.exe > nul 2>&1
taskkill /f /im qentl.exe > nul 2>&1

echo 所有服务已停止。
