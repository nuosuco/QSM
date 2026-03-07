@echo off
setlocal enabledelayedexpansion

:main
echo [Compiler] QEntL Compiler Initialized.
if "%~1"=="" (
    echo [Compiler] Error: No source file provided.
    echo Usage: qentl_Compiler.bat [source_file.qentl] [optional_output_file.qbc]
    exit /b 1
)

set "source_file=%~1"
set "base_name=%~n1"
set "output_file=%~2"

REM If output file is not provided, generate it from source name
if "%output_file%"=="" (
    set "output_file=%base_name%.qbc"
)

echo [Compiler] Compiling source file: "%source_file%"
call :compile_qentl_file "%source_file%" "%output_file%"

if %errorlevel% equ 0 (
    echo [Compiler] Compilation successful. Output: "%output_file%"
) else (
    echo [Compiler] Compilation failed.
)

exit /b %errorlevel%

:compile_qentl_file
set "source=%~1"
set "output=%~2"

echo [Compiler] Stage 1: Parsing QEntL source...
echo [Compiler] Stage 2: Generating QBC bytecode...
echo [Compiler] Stage 3: Embedding Quantum Gene Code and Magic Number (QENT)...
echo [Compiler] Stage 4: Compressing bytecode (Target ~90%%)...

REM Simulate file creation at the specified output path
echo QENT > "%output%"
echo Quantum Gene: QGC-GENERIC-COMP-20240703 >> "%output%"
echo Source: %source% >> "%output%"
echo Bytecode: [...] >> "%output%"

echo [Compiler] Mock compilation complete.
exit /b 0

cd F:\QSM\QEntL\qbc\system\runtime 