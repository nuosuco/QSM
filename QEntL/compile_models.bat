@echo off
setlocal enabledelayedexpansion

echo [Model Builder] Starting QEntL Models build...

set "COMPILER_PATH=System/Compiler/bin/qentl_Compiler.bat"
set "SOURCE_ROOT=Models"
set "OUTPUT_ROOT=dist/models"

REM Define the model source directories  
set "MODEL_DIRS=QSM/src Ref/src SOM/src WeQ/src QEntL/src neural_networks"

if not exist "%COMPILER_PATH%" (
    echo [Model Builder] Error: Compiler not found at "%COMPILER_PATH%".
    echo Please ensure the toolchain is built first.
    exit /b 1
)

echo [Model Builder] Cleaning output directory: %OUTPUT_ROOT%
if exist "%OUTPUT_ROOT%" (
    del /q "%OUTPUT_ROOT%/*.qbc"
) else (
    mkdir "%OUTPUT_ROOT%"
)

echo [Model Builder] Compiling Models and Neural Networks...
echo =================================================

set "compile_count=0"
set "error_count=0"

for %%d in (%MODEL_DIRS%) do (
    set "source_dir=%SOURCE_ROOT%/%%d"
    echo.
    echo [Model Builder] Compiling components in: !source_dir!
    
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
        echo   [Model Builder] Warning: Source directory !source_dir! not found.
    )
)

echo.
echo =================================================
echo [Model Builder] Build process finished.
echo.
echo Successfully compiled: %compile_count% files.
echo Failed: %error_count% files.

if %error_count% gtr 0 (
    echo [Model Builder] Models build failed with errors.
    exit /b 1
) else (
    echo [Model Builder] QEntL Models successfully built into "%OUTPUT_ROOT%".
    exit /b 0
) 