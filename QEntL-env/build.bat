@echo off
chcp 65001 > nul

echo ===================================
echo QEntl解释器构建脚本 (Windows)
echo ===================================

REM 检查是否安装了gcc
gcc --version > nul 2>&1
if errorlevel 1 (
    echo 需要安装gcc编译器
    echo 可以使用MinGW或MSYS2安装gcc
    exit /b 1
)

REM 获取当前目录
set CURRENT_DIR=%~dp0
set BIN_DIR=%CURRENT_DIR%bin

REM 创建bin目录
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

REM 编译QEntl解释器
echo 正在编译QEntl解释器...
gcc -o "%BIN_DIR%\qentl.exe" "%BIN_DIR%\qentl.c" -Wall -O2

if errorlevel 1 (
    echo 编译失败
    exit /b 1
)

echo 编译成功！
echo QEntl解释器已构建: %BIN_DIR%\qentl.exe

REM 添加到PATH (可选)
echo.
set /p add_to_path="是否将QEntl添加到系统PATH? (y/n): "
if /i "%add_to_path%"=="y" (
    setx PATH "%PATH%;%BIN_DIR%"
    echo QEntl已添加到系统PATH
)

echo.
echo 可以通过以下命令测试QEntl解释器:
echo %BIN_DIR%\qentl.exe --version
echo. 