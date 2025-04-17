@echo off
chcp 65001 > nul

set SRC_DIR=%~dp0..\src
set TEST_DIR=%~dp0
set BUILD_DIR=%~dp0..\build
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

echo ===== 缂栬瘧閲忓瓙鍩哄洜娴嬭瘯 =====

gcc -o "%BUILD_DIR%\test_quantum_gene.exe" ^
    "%TEST_DIR%\test_quantum_gene.c" ^
    "%SRC_DIR%\quantum_gene.c" ^
    "%SRC_DIR%\quantum_state.c" ^
    -I"%SRC_DIR%" -Wall

if %errorlevel% neq 0 (
    echo 缂栬瘧澶辫触锛?
    exit /b 1
)

echo ===== 杩愯閲忓瓙鍩哄洜娴嬭瘯 =====

"%BUILD_DIR%\test_quantum_gene.exe"

if %errorlevel% neq 0 (
    echo 娴嬭瘯澶辫触锛?
    exit /b 1
)

echo ===== 娴嬭瘯瀹屾垚 ===== 
