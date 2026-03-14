@echo off
setlocal enabledelayedexpansion

echo [Runtime Builder] Starting QEntL Runtime build...

set "COMPILER_PATH=../Compiler/bin/qentl_Compiler.bat"
set "SOURCE_ROOT=src"
set "OUTPUT_ROOT=../../qbc/system/runtime"

REM Define the subdirectories of the runtime to be compiled
set "CORE_DIRS=core memory quantum system io network logging"

if not exist "%COMPILER_PATH%" (
    echo [Runtime Builder] Error: Compiler not found at "%COMPILER_PATH%".
    exit /b 1
)

echo [Runtime Builder] Compiling Runtime components...
echo =================================================

set "compile_count=0"
set "error_count=0"

for %%d in (%CORE_DIRS%) do (
    set "source_dir=%SOURCE_ROOT%/%%d"
    set "output_dir=%OUTPUT_ROOT%/%%d"
    echo.
    echo [Runtime Builder] Compiling components in: !source_dir! to !output_dir!
    
    if not exist "!output_dir!" (
        mkdir "!output_dir!"
    )

    if exist "!source_dir!" (
        for %%f in ("!source_dir!/*.qentl") do (
            echo   -> Compiling %%~nxf ...
            set "source_file=%%f"
            set "output_file=!output_dir!/%%~nf.qbc"
            
            call %COMPILER_PATH% "!source_file!" "!output_file!"
            
            if !errorlevel! equ 0 (
                set /a compile_count+=1
            ) else (
                echo      Error compiling %%~nxf
                set /a error_count+=1
            )
        )
    ) else (
        echo   [Runtime Builder] Warning: Source directory !source_dir! not found.
    )
)

echo.
echo =================================================
echo [Runtime Builder] Build process finished.
echo.
echo Successfully compiled: %compile_count% files.
echo Failed: %error_count% files.

if %error_count% gtr 0 (
    echo [Runtime Builder] Runtime build failed with errors.
    exit /b 1
) else (
    echo [Runtime Builder] QEntL Runtime components successfully built.
    exit /b 0
) 