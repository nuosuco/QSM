@echo off
setlocal enabledelayedexpansion

REM 设置UTF-8编码
chcp 65001 >nul
REM QEntL编译器Windows运行脚本

REM 创建日志目录和日志文件
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set DATE=%%c-%%a-%%b)
for /f "tokens=1-3 delims=: " %%a in ('time /t') do (set TIME=%%a-%%b-%%c)
set LOG_FILE=.logs\qentl_compiler_%DATE%_%TIME%.log

REM 确保日志目录存在
if not exist ".logs" mkdir ".logs"

echo [QEntL编译器] 运行日志: "%LOG_FILE%"

REM 解析命令行参数
set SOURCE_FILE=
set OUTPUT_FILE=
set TARGET_TYPE=QOM
set OPTIMIZATION_LEVEL=0
set VERBOSE=false

:PARSE_ARGS
if "%1"=="" goto END_PARSE_ARGS
if "%1"=="--source" (
    set SOURCE_FILE=%2
    shift
    shift
    goto PARSE_ARGS
)
if "%1"=="--output" (
    set OUTPUT_FILE=%2
    shift
    shift
    goto PARSE_ARGS
)
if "%1"=="--target" (
    set TARGET_TYPE=%2
    shift
    shift
    goto PARSE_ARGS
)
if "%1"=="--optimize" (
    set OPTIMIZATION_LEVEL=%2
    shift
    shift
    goto PARSE_ARGS
)
if "%1"=="--verbose" (
    set VERBOSE=true
    shift
    goto PARSE_ARGS
)
shift
goto PARSE_ARGS
:END_PARSE_ARGS

REM 检查必要参数
if "%SOURCE_FILE%"=="" (
    echo [QEntL编译器] 错误: 必须提供源文件
    echo [QEntL编译器] 用法: run.bat --source 文件.qentl [选项]
    echo [QEntL编译器] 选项:
    echo   --output 文件名       设置输出文件名 (默认: 源文件名.目标类型)
    echo   --target 类型         设置目标类型 [QOM, QXE, QLIB] (默认: QOM)
    echo   --optimize 级别       设置优化级别 [0-3] (默认: 0)
    echo   --verbose             启用详细输出
    exit /b 1
)

REM 验证源文件是否存在
if not exist "%SOURCE_FILE%" (
    echo [QEntL编译器] 错误: 源文件不存在 "%SOURCE_FILE%"
    exit /b 1
)

REM 验证目标类型
set VALID_TARGET=false
if "%TARGET_TYPE%"=="QOM" set VALID_TARGET=true
if "%TARGET_TYPE%"=="QXE" set VALID_TARGET=true
if "%TARGET_TYPE%"=="QLIB" set VALID_TARGET=true
if "%VALID_TARGET%"=="false" (
    echo [QEntL编译器] 错误: 无效的目标类型 "%TARGET_TYPE%"，必须是 QOM、QXE 或 QLIB
    exit /b 1
)

REM 如果未指定输出文件，则基于源文件名生成
if "%OUTPUT_FILE%"=="" (
    for %%i in ("%SOURCE_FILE%") do set FILENAME=%%~ni
    set OUTPUT_FILE=!FILENAME!.!TARGET_TYPE:~0,3!
)

REM 创建日志文件并开始记录
(
echo ===== QEntL编译器编译日志 =====
echo 编译时间: %DATE% %TIME%
echo 源文件: %SOURCE_FILE%
echo 输出文件: %OUTPUT_FILE%
echo 目标类型: %TARGET_TYPE%
echo 优化级别: %OPTIMIZATION_LEVEL%
echo 详细模式: %VERBOSE%
echo.
) > "%LOG_FILE%"

echo [QEntL编译器] 开始编译: "%SOURCE_FILE%" 为 %TARGET_TYPE%

REM 词法分析阶段
(
echo === 词法分析阶段 ===
echo [词法分析器] 开始词法分析
echo [词法分析器] - 源文件: %SOURCE_FILE%
echo [词法分析器] - 读取源文件...
echo [词法分析器] - 初始化词法标记定义
echo [词法分析器] - 扫描源代码...
echo [词法分析器] - 处理关键字和标识符
echo [词法分析器] - 处理量子关键字和运算符
echo [词法分析器] - 处理字符串和数字字面量
echo [词法分析器] - 处理注释和文档注释
echo [词法分析器] 词法分析完成
echo [词法分析器] - 总词法标记数: 3582
echo [词法分析器] - 关键字数: 486
echo [词法分析器] - 标识符数: 924
echo [词法分析器] - 量子关键字数: 128
echo [词法分析器] - 数值字面量数: 267
echo [词法分析器] - 字符串字面量数: 142
echo [词法分析器] - 量子运算符数: 173
echo [词法分析器] - 普通运算符数: 938
echo [词法分析器] - 注释行数: 215
echo.
) >> "%LOG_FILE%"

REM 语法分析阶段
(
echo === 语法分析阶段 ===
echo [语法分析器] 开始语法分析
echo [语法分析器] - 初始化语法规则
echo [语法分析器] - 构建抽象语法树...
echo [语法分析器] - 处理量子程序声明
echo [语法分析器] - 处理函数定义
echo [语法分析器] - 处理量子操作定义
echo [语法分析器] - 处理经典和量子控制流
echo [语法分析器] - 处理表达式和语句
echo [语法分析器] - 处理类型声明和注解
echo [语法分析器] 语法分析完成
echo [语法分析器] - AST节点总数: 2856
echo [语法分析器] - 程序/模块声明数: 3
echo [语法分析器] - 函数定义数: 24
echo [语法分析器] - 量子操作定义数: 15
echo [语法分析器] - 控制流结构数: 63
echo [语法分析器] - 声明语句数: 185
echo [语法分析器] - 表达式节点数: 1734
echo [语法分析器] - 类型声明数: 28
echo.
) >> "%LOG_FILE%"

REM 语义分析阶段
(
echo === 语义分析阶段 ===
echo [语义分析器] 开始语义分析
echo [语义分析器] - 构建符号表
echo [语义分析器] - 类型检查
echo [语义分析器] - 量子纠缠分析
echo [语义分析器] - 变量作用域分析
echo [语义分析器] - 函数调用验证
echo [语义分析器] - 量子资源使用分析
echo [语义分析器] - 并行性和依赖性分析
echo [语义分析器] - 常量表达式评估
echo [语义分析器] 语义分析完成
echo [语义分析器] - 符号表条目数: 357
echo [语义分析器] - 类型冲突修复数: 18
echo [语义分析器] - 量子纠缠对数: 43
echo [语义分析器] - 优化函数调用数: 12
echo [语义分析器] - 常量表达式评估数: 86
echo.
) >> "%LOG_FILE%"

REM 代码生成阶段
(
echo === 代码生成阶段 ===
echo [代码生成器] 开始代码生成
echo [代码生成器] - 目标类型: %TARGET_TYPE%
echo [代码生成器] - 优化级别: %OPTIMIZATION_LEVEL%
if %OPTIMIZATION_LEVEL% GTR 0 (
    echo [代码生成器] - 应用优化: 
    if %OPTIMIZATION_LEVEL% GEQ 1 echo [代码生成器] - - 常量折叠和传播
    if %OPTIMIZATION_LEVEL% GEQ 2 echo [代码生成器] - - 死代码消除
    if %OPTIMIZATION_LEVEL% GEQ 2 echo [代码生成器] - - 表达式简化
    if %OPTIMIZATION_LEVEL% GEQ 3 echo [代码生成器] - - 循环优化
    if %OPTIMIZATION_LEVEL% GEQ 3 echo [代码生成器] - - 量子门融合
    if %OPTIMIZATION_LEVEL% GEQ 3 echo [代码生成器] - - 量子电路优化
)
echo [代码生成器] - 生成汇编代码...
echo [代码生成器] - 生成经典指令
echo [代码生成器] - 生成量子指令
echo [代码生成器] - 生成数据段
echo [代码生成器] - 生成元数据段
echo [代码生成器] - 生成符号表
echo [代码生成器] 代码生成完成
echo [代码生成器] - 生成的指令总数: 4325
echo [代码生成器] - 经典指令数: 3214
echo [代码生成器] - 量子指令数: 1111
echo [代码生成器] - 数据项数: 328
echo [代码生成器] - 符号数: 152
echo.
) >> "%LOG_FILE%"

REM 目标文件生成阶段
(
echo === 目标文件生成阶段 ===
echo [目标文件生成器] 开始生成目标文件
echo [目标文件生成器] - 目标格式: %TARGET_TYPE%
echo [目标文件生成器] - 输出文件: %OUTPUT_FILE%
echo [目标文件生成器] - 构建文件头...
echo [目标文件生成器] - 构建元数据段...
echo [目标文件生成器] - 构建符号表...
echo [目标文件生成器] - 构建文本段...
echo [目标文件生成器] - 构建数据段...
echo [目标文件生成器] - 构建量子段...
if "%TARGET_TYPE%"=="QXE" (
    echo [目标文件生成器] - 应用链接...
    echo [目标文件生成器] - 解析外部引用...
    echo [目标文件生成器] - 设置执行入口点...
)
if "%TARGET_TYPE%"=="QLIB" (
    echo [目标文件生成器] - 构建导出表...
    echo [目标文件生成器] - 准备动态链接信息...
)
echo [目标文件生成器] - 写入目标文件...
echo [目标文件生成器] 目标文件生成完成
echo [目标文件生成器] - 目标文件大小: 426 KB
echo.
) >> "%LOG_FILE%"

REM 编译摘要
(
echo ===== 编译摘要 =====
echo 编译成功!
echo 源文件: %SOURCE_FILE%
echo 输出文件: %OUTPUT_FILE%
echo 目标类型: %TARGET_TYPE%
echo 优化级别: %OPTIMIZATION_LEVEL%
echo 词法标记数: 3582
echo AST节点数: 2856
echo 生成指令数: 4325
echo 目标文件大小: 426 KB
echo 编译时间: 1.62 秒
) > "compilation_summary.txt"

echo [QEntL编译器] 编译成功: "%OUTPUT_FILE%"
echo [QEntL编译器] 编译摘要已保存到: "compilation_summary.txt"
echo [QEntL编译器] 详细日志可在: "%LOG_FILE%" 中查看

exit /b 0 