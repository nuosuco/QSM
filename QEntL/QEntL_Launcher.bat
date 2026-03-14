@echo off
chcp 936 >nul
title QEntL 量子编程环境启动器
color 0B

:MAIN_MENU
cls
echo ========================================
echo   QEntL 量子编程环境启动器
echo ========================================
echo.
echo 可用选项:
echo   1. 启动QEntL虚拟机
echo   2. 启动QEntL编译器
echo   3. 打开开发环境
echo   4. 系统诊断工具
echo   5. 退出
echo.
set /p choice=请选择 (1-5): 

if "%choice%"=="1" goto START_VM
if "%choice%"=="2" goto START_COMPILER
if "%choice%"=="3" goto START_DEV_ENV
if "%choice%"=="4" goto DIAGNOSTICS
if "%choice%"=="5" goto EXIT
echo 无效选择，请重新输入！
pause
goto MAIN_MENU

:START_VM
cls
echo ========================================
echo 启动QEntL虚拟机...
echo ========================================
echo.

if exist "%~dp0System\VM\bin\qentl_vm.exe" (
    echo 正在启动量子虚拟机...
    cd /d "%~dp0System\VM\bin"
    start "" qentl_vm.exe
    echo 虚拟机已启动！
) else if exist "%~dp0System\VM\bin\start_vm.bat" (
    echo 正在启动虚拟机...
    call "%~dp0System\VM\bin\start_vm.bat"
) else (
    echo 错误: 未找到虚拟机可执行文件
    echo 路径: %~dp0System\VM\bin\
    echo 请检查QEntL是否正确安装
)

echo.
pause
goto MAIN_MENU

:START_COMPILER
cls
echo ========================================
echo 启动QEntL编译器...
echo ========================================
echo.

if exist "%~dp0System\Compiler\bin\qentl_compiler.exe" (
    echo 正在启动量子编译器...
    cd /d "%~dp0System\Compiler\bin"
    start "" qentl_compiler.exe
    echo 编译器已启动！
) else if exist "%~dp0System\Compiler\bin\start_compiler.bat" (
    echo 正在启动编译器...
    call "%~dp0System\Compiler\bin\start_compiler.bat"
) else (
    echo 错误: 未找到编译器可执行文件
    echo 路径: %~dp0System\Compiler\bin\
    echo 请检查QEntL是否正确安装
)

echo.
pause
goto MAIN_MENU

:START_DEV_ENV
cls
echo ========================================
echo 打开QEntL开发环境...
echo ========================================
echo.

echo 正在初始化开发环境...

REM 设置环境变量
set QENTL_HOME=%~dp0
set QENTL_USER_HOME=%~dp0Users\Default
set QENTL_SYSTEM=%~dp0System
set PATH=%QENTL_SYSTEM%\Compiler\bin;%QENTL_SYSTEM%\VM\bin;%PATH%

echo 环境变量已设置：
echo   QENTL_HOME=%QENTL_HOME%
echo   QENTL_USER_HOME=%QENTL_USER_HOME%
echo   QENTL_SYSTEM=%QENTL_SYSTEM%
echo.

REM 创建用户目录（如果不存在）
if not exist "%QENTL_USER_HOME%" (
    echo 创建用户目录...
    mkdir "%QENTL_USER_HOME%\Documents\QEntL_Projects" 2>nul
    mkdir "%QENTL_USER_HOME%\Programs\Custom" 2>nul
    mkdir "%QENTL_USER_HOME%\Settings" 2>nul
    mkdir "%QENTL_USER_HOME%\Data\Cache" 2>nul
    mkdir "%QENTL_USER_HOME%\Desktop\Shortcuts" 2>nul
    echo 用户目录已创建
)

REM 启动开发环境
if exist "%~dp0System\dev_environment.bat" (
    call "%~dp0System\dev_environment.bat"
) else (
    echo 打开QEntL开发目录...
    explorer "%QENTL_USER_HOME%\Documents\QEntL_Projects"
    
    echo 打开QEntL系统终端...
    cmd /k "echo QEntL开发环境已就绪！ && echo 当前用户目录: %QENTL_USER_HOME% && echo 输入 'qentl --help' 查看可用命令"
)

pause
goto MAIN_MENU

:DIAGNOSTICS
cls
echo ========================================
echo QEntL系统诊断工具
echo ========================================
echo.

echo 正在检查系统状态...
echo.

REM 检查核心目录
echo [1/5] 检查核心目录...
if exist "%~dp0System" (
    echo   ✓ System目录存在
) else (
    echo   ✗ System目录缺失
)

if exist "%~dp0Users" (
    echo   ✓ Users目录存在
) else (
    echo   ✗ Users目录缺失
)

if exist "%~dp0Models" (
    echo   ✓ Models目录存在
) else (
    echo   ✗ Models目录缺失
)

echo.

REM 检查关键文件
echo [2/5] 检查关键组件...
if exist "%~dp0System\Compiler" (
    echo   ✓ 编译器组件存在
) else (
    echo   ✗ 编译器组件缺失
)

if exist "%~dp0System\VM" (
    echo   ✓ 虚拟机组件存在
) else (
    echo   ✗ 虚拟机组件缺失
)

if exist "%~dp0System\Runtime" (
    echo   ✓ 运行时组件存在
) else (
    echo   ✗ 运行时组件缺失
)

echo.

REM 检查用户环境
echo [3/5] 检查用户环境...
if exist "%~dp0Users\Default" (
    echo   ✓ 默认用户目录存在
) else (
    echo   ✗ 默认用户目录缺失
)

if exist "%~dp0Users\Default\Settings\preferences.qentl" (
    echo   ✓ 用户配置文件存在
) else (
    echo   ✗ 用户配置文件缺失
)

echo.

REM 检查模型
echo [4/5] 检查四大模型...
for %%m in (QSM WeQ SOM Ref) do (
    if exist "%~dp0Models\%%m" (
        echo   ✓ %%m模型存在
    ) else (
        echo   ✗ %%m模型缺失
    )
)

echo.

REM 系统信息
echo [5/5] 系统信息...
echo   安装路径: %~dp0
echo   系统时间: %date% %time%
echo   用户名: %USERNAME%
echo   计算机名: %COMPUTERNAME%

echo.
echo 诊断完成！
echo.
pause
goto MAIN_MENU

:EXIT
cls
echo 感谢使用QEntL量子编程环境！
echo 再见！
timeout /t 2 >nul
exit

REM 错误处理
:ERROR
echo 发生错误，请检查QEntL安装是否完整
pause
goto MAIN_MENU
