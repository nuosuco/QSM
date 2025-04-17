@echo off
chcp 65001 > nul

set TEST_DIR=%~dp0
set SRC_DIR=%~dp0..\src
set BUILD_DIR=%~dp0..\build
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

echo Testing quantum_gene...

set TEST=test_quantum_gene
set TEST_SRC=%TEST_DIR%\%TEST%.c
set TEST_EXE=%BUILD_DIR%\%TEST%.exe

echo Compiling %TEST%.c...

gcc -o "%TEST_EXE%" "%TEST_SRC%" "%SRC_DIR%\quantum_state.c" "%SRC_DIR%\quantum_entanglement.c" "%SRC_DIR%\quantum_gene.c" "%SRC_DIR%\quantum_field.c" -I"%SRC_DIR%"

if %errorlevel% neq 0 (
    echo Compilation failed!
    exit /b 1
)

echo Running %TEST%.exe...
"%TEST_EXE%"

if %errorlevel% neq 0 (
    echo Test failed!
    exit /b 1
)

echo All tests passed!
exit /b 0 
