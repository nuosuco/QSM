@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo 请指定要测试的模块:
    echo   quantum_state
    echo   quantum_entanglement
    echo   quantum_gene
    echo   quantum_field
    exit /b 1
)

set TEST_NAME=%~1
if not "!TEST_NAME:~0,5!"=="test_" set TEST_NAME=test_!TEST_NAME!
if not "!TEST_NAME:~-4!"==".exe" (
    if not "!TEST_NAME:~-2!"==".c" set TEST_NAME=!TEST_NAME!.exe
    REM 如果还是.c，转为.exe
    set TEST_NAME=!TEST_NAME:.c=.exe!
)

set TEST_DIR=%~dp0..\tests

echo 运行测试: !TEST_NAME!
if exist "%TEST_DIR%\!TEST_NAME!" (
    echo 执行: %TEST_DIR%\!TEST_NAME!
    pushd "%TEST_DIR%" && !TEST_NAME!
    if !errorlevel! EQU 0 (
        echo 测试通过!
    ) else (
        echo 测试失败!
    )
    popd
) else (
    echo 错误: 测试文件不存在 - %TEST_DIR%\!TEST_NAME!
)

exit /b %errorlevel% 