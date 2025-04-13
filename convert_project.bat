@echo off
REM =========================================================
REM 项目量子化转换脚本
REM 将项目中的所有文件转换为量子格式（QEntl, QPy, QJS等）
REM =========================================================

echo 开始量子化转换项目...
echo 时间: %date% %time%
echo.

REM 设置路径
set SCRIPT_PATH=scripts\utils\quantum_converter.qpy
set BASE_DIR=%~dp0
cd %BASE_DIR%

REM 检查转换脚本是否存在
if not exist "%SCRIPT_PATH%" (
    echo 错误: 转换脚本 %SCRIPT_PATH% 不存在!
    exit /b 1
)

echo 第1步: 转换核心模块...
python %SCRIPT_PATH% --module QSM --verbose
echo.

echo 第2步: 转换 WeQ 模块...
python %SCRIPT_PATH% --module WeQ --verbose
echo.

echo 第3步: 转换 SOM 模块...
python %SCRIPT_PATH% --module SOM --verbose
echo.

echo 第4步: 转换 Ref 模块...
python %SCRIPT_PATH% --module Ref --verbose
echo.

echo 第5步: 转换 world 模块...
python %SCRIPT_PATH% --module world --verbose
echo.

echo 第6步: 转换 scripts 模块...
python %SCRIPT_PATH% --module scripts --verbose
echo.

echo 第7步: 转换 tests 模块...
python %SCRIPT_PATH% --module tests --verbose
echo.

echo 第8步: 转换 docs 模块...
python %SCRIPT_PATH% --module docs --verbose
echo.

echo 转换完成时间: %date% %time%
echo 所有模块已完成量子化转换!
echo 请检查转换日志确认结果。

pause 