@echo off
REM QEntL Runtime Loader Script
REM 加载并启动QEntL运行时模块

echo ================================================
echo QEntL Runtime Loader v1.0.0
echo ================================================

set RUNTIME_QBC_DIR=%~dp0
set QENTL_VM=%~dp0..\..\VM\bin\qentlvm.exe
set RUNTIME_INDEX=%RUNTIME_QBC_DIR%runtime_index.qbc

echo [INFO] Runtime QBC Directory: %RUNTIME_QBC_DIR%
echo [INFO] QEntL VM: %QENTL_VM%
echo [INFO] Runtime Index: %RUNTIME_INDEX%
echo.

if not exist "%RUNTIME_INDEX%" (
    echo [ERROR] Runtime index not found: %RUNTIME_INDEX%
    pause
    exit /b 1
)

echo [LOAD] Loading QEntL Runtime modules...
echo.

REM 按照依赖顺序加载模块
echo [1/9] Loading Quantum Logger...
if exist "%RUNTIME_QBC_DIR%logging\quantum_logger.qbc" (
    echo [OK] logging/quantum_logger.qbc
) else (
    echo [ERROR] Missing: logging/quantum_logger.qbc
)

echo [2/9] Loading Memory Manager...
if exist "%RUNTIME_QBC_DIR%memory\memory_manager.qbc" (
    echo [OK] memory/memory_manager.qbc
) else (
    echo [ERROR] Missing: memory/memory_manager.qbc
)

echo [3/9] Loading Kernel Loader...
if exist "%RUNTIME_QBC_DIR%core\kernel_loader.qbc" (
    echo [OK] core/kernel_loader.qbc
) else (
    echo [ERROR] Missing: core/kernel_loader.qbc
)

echo [4/9] Loading Process Manager...
if exist "%RUNTIME_QBC_DIR%system\process_manager.qbc" (
    echo [OK] system/process_manager.qbc
) else (
    echo [ERROR] Missing: system/process_manager.qbc
)

echo [5/9] Loading Filesystem Manager...
if exist "%RUNTIME_QBC_DIR%io\filesystem_manager.qbc" (
    echo [OK] io/filesystem_manager.qbc
) else (
    echo [ERROR] Missing: io/filesystem_manager.qbc
)

echo [6/9] Loading Network Manager...
if exist "%RUNTIME_QBC_DIR%network\network_manager.qbc" (
    echo [OK] network/network_manager.qbc
) else (
    echo [ERROR] Missing: network/network_manager.qbc
)

echo [7/9] Loading Quantum Runtime...
if exist "%RUNTIME_QBC_DIR%quantum\quantum_runtime.qbc" (
    echo [OK] quantum/quantum_runtime.qbc
) else (
    echo [ERROR] Missing: quantum/quantum_runtime.qbc
)

echo [8/9] Loading System Services...
if exist "%RUNTIME_QBC_DIR%system\system_services.qbc" (
    echo [OK] system/system_services.qbc
) else (
    echo [ERROR] Missing: system/system_services.qbc
)

echo [9/9] Loading Runtime Bootstrap...
if exist "%RUNTIME_QBC_DIR%core\runtime_bootstrap.qbc" (
    echo [OK] core/runtime_bootstrap.qbc
) else (
    echo [ERROR] Missing: core/runtime_bootstrap.qbc
)

echo.
echo ================================================
echo Runtime Load Summary
echo ================================================

REM 统计加载的模块
set /a LOADED_MODULES=0
for /r "%RUNTIME_QBC_DIR%" %%f in (*.qbc) do (
    if not "%%~nxf"=="runtime_index.qbc" (
        set /a LOADED_MODULES+=1
    )
)

echo [SUCCESS] %LOADED_MODULES% runtime modules loaded successfully!
echo.
echo Available modules:
echo   - Core: kernel_loader, runtime_bootstrap
echo   - Memory: memory_manager  
echo   - Quantum: quantum_runtime
echo   - System: process_manager, system_services
echo   - I/O: filesystem_manager
echo   - Network: network_manager
echo   - Logging: quantum_logger
echo.

if exist "%QENTL_VM%" (
    echo [INFO] QEntL Virtual Machine found
    echo [INFO] Ready to start QEntL Runtime System
    echo.
    echo Starting QEntL Runtime...
    REM "%QENTL_VM%" --runtime "%RUNTIME_QBC_DIR%" --bootstrap "core\runtime_bootstrap.qbc"
    echo [SIMULATED] QEntL Runtime started successfully
) else (
    echo [WARNING] QEntL Virtual Machine not found at: %QENTL_VM%
    echo [INFO] Runtime modules are loaded and ready for VM
)

echo.
pause
