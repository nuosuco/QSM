@echo off
REM 编译QEntL Bootstrap解释器
REM 这个脚本会将C源码编译成可执行文件

echo QEntL Bootstrap 编译器
echo =====================

echo 正在编译 qentl_bootstrap.c...

REM 检查是否有GCC编译器
where gcc >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo 使用GCC编译器...
    gcc -o qentl_bootstrap.exe qentl_bootstrap.c
    if %ERRORLEVEL% == 0 (
        echo 编译成功！生成了 qentl_bootstrap.exe
        goto :test
    ) else (
        echo GCC编译失败
        goto :try_msvc
    )
)

:try_msvc
REM 检查是否有MSVC编译器
where cl >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo 使用MSVC编译器...
    cl qentl_bootstrap.c /Fe:qentl_bootstrap.exe
    if %ERRORLEVEL% == 0 (
        echo 编译成功！生成了 qentl_bootstrap.exe
        goto :test
    ) else (
        echo MSVC编译失败
        goto :no_compiler
    )
)

:no_compiler
echo 错误: 未找到C编译器 (GCC 或 MSVC)
echo 请安装以下任一编译器:
echo 1. MinGW-w64 (包含GCC)
echo 2. Microsoft Visual Studio (包含MSVC)
echo 3. TDM-GCC
goto :end

:test
echo.
echo 测试QEntL Bootstrap解释器...
if exist "..\..\tests\test_hello.qentl" (
    echo 运行测试文件: test_hello.qentl
    qentl_bootstrap.exe "..\..\tests\test_hello.qentl"
) else (
    echo 创建简单测试文件...
    echo quantum_class HelloWorld { > test_simple.qentl
    echo     public function main(): Integer { >> test_simple.qentl
    echo         Console.println("Hello from QEntL Bootstrap!"); >> test_simple.qentl
    echo         return 0; >> test_simple.qentl
    echo     } >> test_simple.qentl
    echo } >> test_simple.qentl
    echo.
    echo 运行简单测试:
    qentl_bootstrap.exe test_simple.qentl
)

:end
echo.
echo 编译脚本完成
pause
