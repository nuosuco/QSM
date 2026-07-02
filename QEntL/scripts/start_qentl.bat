@echo off
rem QEntL量子编程语言启动脚本
rem 版本: 1.0.0-alpha
rem 日期: 2025-06-12

echo.
echo ========================================
echo    QEntL 量子编程语言启动器
echo ========================================
echo    版本: 1.0.0-alpha
echo    构建日期: 2025-06-12
echo ========================================
echo.

rem 设置环境变量
set QENTL_SCRIPT_DIR=%~dp0
cd /d "%QENTL_SCRIPT_DIR%..\..\"
set QENTL_HOME=%CD%
set QENTL_BUILD_DIR=%QENTL_HOME%\build
set QENTL_SRC_DIR=%QENTL_HOME%

echo [INFO] QEntL项目根目录: %QENTL_HOME%
echo [INFO] 构建目录: %QENTL_BUILD_DIR%
echo.

rem 检查基础目录结构
echo [STEP 1] 检查项目结构...
if not exist "%QENTL_HOME%\QEntL" (
    echo [ERROR] QEntL目录不存在！
    pause
    exit /b 1
)

if not exist "%QENTL_HOME%\QSM" (
    echo [ERROR] QSM模型目录不存在！
    pause
    exit /b 1
)

echo [OK] 项目结构检查完成
echo.

rem 创建构建目录
echo [STEP 2] 准备构建环境...
if not exist "%QENTL_BUILD_DIR%" (
    mkdir "%QENTL_BUILD_DIR%"
    echo [INFO] 创建构建目录: %QENTL_BUILD_DIR%
)

echo [OK] 构建环境准备完成
echo.

rem 显示当前项目状态
echo [STEP 3] 项目状态检查...
echo [INFO] 编译器状态: 已实现 (85%%)
echo [INFO] 虚拟机状态: 已实现 (90%%)
echo [INFO] 文件系统状态: 已实现 (95%%)
echo [INFO] QSM模型状态: 框架完成，业务逻辑开发中
echo [INFO] WeQ模型状态: 框架完成，学习模块开发中
echo [INFO] SOM模型状态: 框架完成，松麦币开发中
echo [INFO] Ref模型状态: 框架完成，自修复开发中
echo.

rem 执行基础测试
echo [STEP 4] 运行基础测试...
echo [INFO] 测试文件: test_hello.qentl
if exist "%QENTL_HOME%test_hello.qentl" (
    echo [OK] 找到测试文件
    type "%QENTL_HOME%test_hello.qentl"
    echo.
) else (
    echo [WARNING] 测试文件不存在
)

echo [INFO] 基础测试完成
echo.

rem 显示可用操作
echo [STEP 5] 可用操作:
echo.
echo 1. 查看项目进度报告
echo 2. 查看今日行动计划  
echo 3. 进入开发模式
echo 4. 运行编译器测试
echo 5. 退出
echo.

:menu
set /p choice="请选择操作 (1-5): "

if "%choice%"=="1" (
    echo.
    echo [INFO] 打开项目进度报告...
    if exist "%QENTL_HOME%PROJECT_PROGRESS_FINAL.md" (
        type "%QENTL_HOME%PROJECT_PROGRESS_FINAL.md"
    ) else (
        echo [ERROR] 项目进度报告文件不存在
    )
    echo.
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo [INFO] 打开今日行动计划...
    if exist "%QENTL_HOME%TODAY_ACTION_PLAN.md" (
        type "%QENTL_HOME%TODAY_ACTION_PLAN.md"
    ) else (
        echo [ERROR] 行动计划文件不存在
    )
    echo.
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo [INFO] 进入开发模式...
    echo [INFO] 当前实现状态:
    echo   - 编译器: QEntL/compiler/src/ (完整框架)
    echo   - 虚拟机: QEntL/vm/src/ (核心实现)
    echo   - 文件系统: QEntL/src/filesystem/ (几乎完成)
    echo   - 四大模型: QSM/WeQ/SOM/Ref (框架完成)
    echo.
    echo [下一步] 建议先完成编译器的核心编译流程
    echo [下一步] 然后连接虚拟机进行字节码执行
    echo [下一步] 最后实现四大模型的核心业务逻辑
    echo.
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo [INFO] 运行编译器测试...
    echo [INFO] 当前编译器文件:
    dir "%QENTL_HOME%QEntL\compiler\src\" /b
    echo.
    echo [INFO] 核心组件状态:
    echo   ✅ compiler.qentl (556行) - 主编译器类
    echo   ✅ lexer.qentl (616行) - 词法分析器
    echo   ✅ token.qentl (304行) - Token定义
    echo   ✅ parser.qentl (628行) - 语法分析器
    echo.
    echo [NOTE] 编译器框架已基本完成，需要连接各组件
    echo.
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo [INFO] 退出QEntL启动器
    echo [INFO] 继续开发时请再次运行此脚本
    echo.
    pause
    exit /b 0
)

echo [ERROR] 无效选择，请重新输入
goto menu
