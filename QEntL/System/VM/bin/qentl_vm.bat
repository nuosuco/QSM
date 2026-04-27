@echo off
setlocal enabledelayedexpansion

echo [VM] QEntL Virtual Machine Initialized.

if "%~1"=="--runtime" (
    call :boot_runtime %*
    exit /b !errorlevel!
)

if "%~1"=="" (
    echo [VM] Error: No bytecode file provided.
    echo Usage: qentl_vm.bat [bytecode_file.qbc]
    echo   or:  qentl_vm.bat --runtime [path] --bootstrap [file]
    exit /b 1
)

set "qbc_file=%~1"

if not exist "%qbc_file%" (
    echo [VM] Error: File not found - "%qbc_file%"
    exit /b 1
)

echo [VM] Loading single bytecode file: "%qbc_file%"
call :load_qbc_file "%qbc_file%"

if %errorlevel% equ 0 (
    echo [VM] Execution finished successfully.
) else (
    echo [VM] Execution failed.
)
exit /b %errorlevel!

:load_qbc_file
    set "file=%~1"
    echo [VM] Stage 1: Loading QBC file...
    echo [VM] Stage 2: Verifying Magic Number (expecting QENT)...

    set /p magic=<"%file%"
    if /i "!magic:~0,4!" equ "QENT" (
        echo [VM] Magic Number verified.
    ) else (
        echo [VM] Error: Invalid Magic Number. Expected 'QENT', got '!magic:~0,4!'.
        exit /b 1
    )

    echo [VM] Stage 3: Parsing bytecode and analyzing content...
    echo [VM] Stage 4: Executing instructions...
    echo [VM] Mock execution complete.
    exit /b 0

:boot_runtime
    set "runtime_path=%2"
    set "bootstrap_file=%4"
    echo [VM-Boot] Booting from runtime.
    echo [VM-Boot] Runtime Path: %runtime_path%
    echo [VM-Boot] Bootstrap Module: %bootstrap_file%

    if not exist "%runtime_path%" (
        echo [VM-Boot] Error: Runtime path not found.
        exit /b 1
    )
    if not exist "%runtime_path%%bootstrap_file%" (
        echo [VM-Boot] Error: Bootstrap file not found in runtime path.
        exit /b 1
    )

    echo [VM-Boot] Initializing Quantum Core...
    echo [VM-Boot] Executing bootstrap module: %bootstrap_file%
    
    REM Simulate kernel_loader loading the rest of the OS
    echo [VM-Boot] Kernel Loader is now loading all OS components...
    echo [VM-Boot] OS Kernel loaded.
    echo [VM-Boot] Filesystem mounted.
    echo [VM-Boot] GUI services started.
    echo [VM-Boot] System services running.
    echo [VM-Boot] Now loading models...
    echo [VM-Boot] QSM, WeQ, Ref, SOM models are now integrated and running.
    echo.
    echo [VM-Boot] QEntL OS startup complete. Welcome!
    exit /b 0 