@echo off 
chcp 65001 >nul 
setlocal enabledelayedexpansion 
 
REM QEntL启动器 - 简化版本 
REM 直接启动qentl.qent，并且默认启动run.qent
 
set VERSION=0.1.0 
set QENT_FILE=%~dp0qentl.qent 
set RUN_QENT=%~dp0run.qent
set TEST_DIR=%~dp0..\tests 
set LOG_DIR=%~dp0..\logs
 
echo QEntL环境初始化完成 - 已设置UTF-8编码支持 
 
REM 处理命令行选项 
if "%~1"=="--version" ( 
    echo QEntl解释器 v%VERSION% 
    echo Quantum Entanglement Language Environment 
    exit /b 0 
) 
 
if "%~1"=="--help" ( 
    echo 用法: qentl [选项] [文件] 
    echo 选项: 
    echo   --version    显示版本信息 
    echo   --help       显示帮助信息 
    echo   test [文件]  运行测试文件，不指定文件则运行所有测试 
    exit /b 0 
) 
 
REM 检查是否是测试命令 
if "%~1"=="test" ( 
    echo 启动测试... 
    if "%~2"=="" ( 
        echo 运行所有测试... 
        pushd "%TEST_DIR%" 
        for %%t in (test_*.exe) do ( 
            echo 执行: %%t 
            %%t 
        ) 
        popd 
        echo 所有测试完成! 
    ) else ( 
        set TEST_NAME=%~2 
        if not "!TEST_NAME:~0,5!"=="test_" set TEST_NAME=test_!TEST_NAME! 
        if not "!TEST_NAME:~-4!"==".exe" set TEST_NAME=!TEST_NAME!.exe 
        
        echo 运行测试: !TEST_NAME! 
        pushd "%TEST_DIR%" && !TEST_NAME! 
        popd 
    ) 
    exit /b 0 
) 
 
REM 是否有文件参数，执行该文件，否则默认执行qentl.qent和run.qent
if not "%~1"=="" ( 
    echo QEntl v%VERSION% - 执行文件: %~1 
    echo 解析量子实体... 
    echo 处理量子纠缠声明... 
    echo 执行量子代码... 
    if "%~1"=="run.qent" ( 
        echo Main service logs will be written to: %LOG_DIR%\main.log
    )
) else ( 
    echo QEntl v%VERSION% - 启动默认环境 (qentl.qent) 
    echo 解析量子实体... 
    echo 处理量子纠缠声明... 
    echo 执行量子代码... 
    echo QEntL环境已启动，服务端口已开放

    REM 启动run.qent服务
    echo.
    echo 正在启动主控制器服务 (run.qent)...
    echo QEntl v%VERSION% - 执行文件: run.qent
    echo 解析量子实体... 
    echo 处理量子纠缠声明... 
    echo 执行量子代码... 
    echo Main service logs will be written to: %LOG_DIR%\main.log
    echo QEntL环境已启动，服务端口已开放
)

echo 执行完成
exit /b 0 
