@echo off
setlocal enabledelayedexpansion

echo [OS Builder] Starting QEntL Operating System build...

set "COMPILER_PATH=Compiler/bin/qentl_Compiler.bat"
set "SOURCE_ROOT=Kernel"
set "OUTPUT_ROOT=dist/os"

REM Define the subdirectories of the OS kernel to be compiled
set "CORE_DIRS=kernel filesystem gui services"

if not exist "%COMPILER_PATH%" (
    echo [OS Builder] Error: Compiler not found at "%COMPILER_PATH%".
    echo Please ensure the toolchain is built first.
    exit /b 1
)

echo [OS Builder] Cleaning output directory: %OUTPUT_ROOT%
if exist "%OUTPUT_ROOT%" (
    del /q "%OUTPUT_ROOT%/*.qbc"
) else (
    mkdir "%OUTPUT_ROOT%"
)

echo [OS Builder] Compiling OS components...
echo =================================================

set "compile_count=0"
set "error_count=0"

for %%d in (%CORE_DIRS%) do (
    set "source_dir=%SOURCE_ROOT%/%%d"
    echo.
    echo [OS Builder] Compiling components in: !source_dir!
    
    if exist "!source_dir!" (
        for %%f in ("!source_dir!/*.qentl") do (
            echo   -> Compiling %%~nxf ...
            call %COMPILER_PATH% "%%f"
            if !errorlevel! equ 0 (
                move "%%~nf.qbc" "%OUTPUT_ROOT%/" > nul
                set /a compile_count+=1
            ) else (
                echo      Error compiling %%~nxf
                set /a error_count+=1
            )
        )
    ) else (
        echo   [OS Builder] Warning: Source directory !source_dir! not found.
    )
)

echo.
echo =================================================
echo [OS Builder] Build process finished.
echo.
echo Successfully compiled: %compile_count% files.
echo Failed: %error_count% files.

if %error_count% gtr 0 (
    echo [OS Builder] OS Build failed with errors.
    exit /b 1
) else (
    echo [OS Builder] QEntL OS core components successfully built into "%OUTPUT_ROOT%".
    exit /b 0
) 