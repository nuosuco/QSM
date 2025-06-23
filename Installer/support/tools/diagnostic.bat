@echo off
:: QEntL System Diagnostic Tool
:: 系统诊断工具

echo ========================================
echo   QEntL 系统诊断工具
echo ========================================
echo.

echo [1/5] 检查系统要求...
systeminfo | findstr /C:"OS Name" /C:"Total Physical Memory" /C:"Processor"

echo.
echo [2/5] 检查 QEntL 安装...
if exist "C:\QEntL\System\VM\bin\qentl.exe" (
    echo   ✓ QEntL 虚拟机已安装
) else (
    echo   ✗ QEntL 虚拟机未找到
)

if exist "C:\QEntL\System\Compiler\bin\qentlc.exe" (
    echo   ✓ QEntL 编译器已安装
) else (
    echo   ✗ QEntL 编译器未找到
)

echo.
echo [3/5] 检查环境变量...
if defined QENTL_HOME (
    echo   ✓ QENTL_HOME = %QENTL_HOME%
) else (
    echo   ✗ QENTL_HOME 未设置
)

echo.
echo [4/5] 检查服务状态...
sc query QEntLService >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ QEntL 服务正在运行
) else (
    echo   ⚠ QEntL 服务未运行
)

echo.
echo [5/5] 检查网络连接...
ping -n 1 quantum.qentl.org >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ 量子网络连接正常
) else (
    echo   ⚠ 量子网络连接异常
)

echo.
echo ========================================
echo   诊断完成
echo ========================================
pause
