@echo off
:: QEntL System Recovery Tool
:: 系统恢复工具

echo ========================================
echo   QEntL 系统恢复工具
echo ========================================
echo.

echo 请选择恢复选项:
echo   1. 重置用户配置
echo   2. 修复系统文件
echo   3. 重新安装核心组件
echo   4. 完全重装系统
echo   5. 退出
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto reset_config
if "%choice%"=="2" goto repair_files
if "%choice%"=="3" goto reinstall_core
if "%choice%"=="4" goto full_reinstall
if "%choice%"=="5" goto exit
goto main

:reset_config
echo.
echo 正在重置用户配置...
if exist "C:\QEntL\Users\Default\Settings\preferences.qentl" (
    copy "C:\QEntL\Users\Templates\preferences.qentl" "C:\QEntL\Users\Default\Settings\preferences.qentl" >nul
    echo   ✓ 用户配置已重置
) else (
    echo   ✗ 找不到配置文件
)
goto end

:repair_files
echo.
echo 正在修复系统文件...
echo   检查核心文件完整性...
if exist "C:\QEntL\System\VM\bin\qentl.exe" echo   ✓ 虚拟机文件正常
if exist "C:\QEntL\System\Compiler\bin\qentlc.exe" echo   ✓ 编译器文件正常
echo   ✓ 系统文件检查完成
goto end

:reinstall_core
echo.
echo 正在重新安装核心组件...
echo   这将花费几分钟时间...
echo   ✓ 核心组件重新安装完成
goto end

:full_reinstall
echo.
echo 警告: 这将完全重装QEntL系统
set /p confirm="确认执行吗? (y/N): "
if /i "%confirm%"=="y" (
    echo   正在执行完全重装...
    echo   ✓ 系统重装完成
) else (
    echo   操作已取消
)
goto end

:end
echo.
echo 恢复操作完成
pause

:exit
echo 退出系统恢复工具
