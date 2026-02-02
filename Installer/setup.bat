@echo off
chcp 65001 >nul 2>&1
:: QEntL Quantum Programming System - Working Installer
:: 可立即使用的工作版安装器

setlocal enabledelayedexpansion

title QEntL 工作版安装器

cls
echo.
echo ========================================================
echo   QEntL 量子编程系统 - 工作版安装器
echo   Working Installer v1.0.0
echo ========================================================
echo.

echo 系统信息:
echo - 操作系统: %OS%
echo - 架构: %PROCESSOR_ARCHITECTURE%
echo - 计算机: %COMPUTERNAME%
echo - 用户: %USERNAME%
echo.

:: Check admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] 管理员权限已获取
) else (
    echo [WARN] 未以管理员身份运行，某些功能可能受限
)

:: Check source directories
set "SOURCE_ROOT=f:\QSM"
set "QENTL_SOURCE=%SOURCE_ROOT%\QEntL"
set "DOCS_SOURCE=%SOURCE_ROOT%\docs"

echo.
echo 🔍 检查源文件...
if not exist "%QENTL_SOURCE%" (
    echo ❌ QEntL源目录不存在: %QENTL_SOURCE%
    pause
    exit /b 1
)
echo ✅ QEntL源目录: %QENTL_SOURCE%

if exist "%DOCS_SOURCE%" (
    echo ✅ 文档目录: %DOCS_SOURCE%
    set "HAS_DOCS=true"
) else (
    echo ⚠️  文档目录不存在: %DOCS_SOURCE%
    set "HAS_DOCS=false"
)

echo.
echo 请选择安装类型:
echo   1. 标准安装到 C:\QEntL (推荐)
echo   2. 自定义安装路径
echo   3. 静默安装 (无交互)
echo   4. 退出安装
echo.

set /p choice="请输入选择 (1-4): "

if "%choice%"=="1" goto standard_install
if "%choice%"=="2" goto custom_install
if "%choice%"=="3" goto silent_install
if "%choice%"=="4" goto exit_install
goto invalid_choice

:invalid_choice
echo.
echo [ERROR] 无效选择，请重试
timeout /t 2 >nul
goto :EOF

:standard_install
echo.
echo ========================================================
echo   标准安装模式
echo ========================================================
set "INSTALL_PATH=C:\QEntL"
goto confirm_install

:custom_install
echo.
echo ========================================================
echo   自定义安装模式
echo ========================================================
echo.
set /p INSTALL_PATH="安装路径 [C:\QEntL]: "
if "%INSTALL_PATH%"=="" set "INSTALL_PATH=C:\QEntL"
goto confirm_install

:silent_install
echo.
echo ========================================================
echo   静默安装模式
echo ========================================================
set "INSTALL_PATH=C:\QEntL"
echo 使用默认设置进行安装...
goto perform_install

:confirm_install
echo.
echo 安装配置确认:
echo - 安装路径: %INSTALL_PATH%
echo - QEntL源: %QENTL_SOURCE%
echo - 文档源: %DOCS_SOURCE%
echo - 包含文档: %HAS_DOCS%
echo.
set /p confirm="确认安装? (y/n) [y]: "
if "%confirm%"=="n" goto exit_install
if "%confirm%"=="N" goto exit_install

:perform_install
echo.
echo ========================================================
echo   🚀 开始安装 QEntL 量子编程系统
echo ========================================================
echo.

:: Create installation directory
echo 📁 创建安装目录...
if exist "%INSTALL_PATH%" (
    echo ℹ️  目录已存在，将进行覆盖安装
    set /p overwrite="确认覆盖现有安装? (y/n) [y]: "
    if "!overwrite!"=="n" goto exit_install
    if "!overwrite!"=="N" goto exit_install
)

if not exist "%INSTALL_PATH%" (
    mkdir "%INSTALL_PATH%" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ❌ 无法创建安装目录: %INSTALL_PATH%
        pause
        exit /b 1
    )
)
echo ✅ 安装目录: %INSTALL_PATH%

:: Install QEntL system
echo.
echo 📦 安装QEntL系统文件...
echo    源目录: %QENTL_SOURCE%
echo    目标目录: %INSTALL_PATH%
echo.

xcopy "%QENTL_SOURCE%\*" "%INSTALL_PATH%\" /E /H /C /I /Y /Q >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ QEntL系统文件安装完成
) else (
    echo ❌ QEntL系统文件安装失败
    pause
    exit /b 1
)

:: Install documentation if available
if "%HAS_DOCS%"=="true" (
    echo.
    echo 📄 安装文档文件...
    xcopy "%DOCS_SOURCE%\*" "%INSTALL_PATH%\docs\" /E /H /C /I /Y /Q >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ 文档文件安装完成
    ) else (
        echo ⚠️  文档文件安装失败，但不影响主程序
    )
)

:: Verify installation
echo.
echo 🔍 验证安装...
set "VERIFIED=true"

if exist "%INSTALL_PATH%\System\VM\bin\qentl_vm.bat" (
    echo ✅ 虚拟机: qentl_vm.bat
) else (
    echo ❌ 缺少: qentl_vm.bat
    set "VERIFIED=false"
)

if exist "%INSTALL_PATH%\System\Compiler\bin\qentl_Compiler.bat" (
    echo ✅ 编译器: qentl_Compiler.bat
) else (
    echo ❌ 缺少: qentl_Compiler.bat
    set "VERIFIED=false"
)

if exist "%INSTALL_PATH%\System\qbc\system\kernel.qsys" (
    echo ✅ 系统镜像: kernel.qsys
) else (
    echo ❌ 缺少: kernel.qsys
    set "VERIFIED=false"
)

:: Create shortcuts and scripts
echo.
echo 🔗 创建启动脚本...

:: Create QEntL launcher
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo title QEntL 量子编程环境
    echo cd /d "%INSTALL_PATH%"
    echo.
    echo :main_menu
    echo cls
    echo echo.
    echo echo ========================================
    echo echo   QEntL 量子编程环境启动器
    echo echo ========================================
    echo echo.
    echo echo 可用选项:
    echo echo   1. 启动QEntL虚拟机
    echo echo   2. 启动QEntL编译器
    echo echo   3. 运行系统镜像
    echo echo   4. 查看文档
    echo echo   5. 退出
    echo echo.
    echo set /p choice="请选择 (1-5): "
    echo if "%%choice%%"=="1" goto run_vm
    echo if "%%choice%%"=="2" goto run_compiler
    echo if "%%choice%%"=="3" goto run_system
    echo if "%%choice%%"=="4" goto show_docs
    echo if "%%choice%%"=="5" exit /b 0
    echo echo 无效选择，请重新选择...
    echo pause
    echo goto main_menu
    echo.
    echo :run_vm
    echo echo.
    echo echo 正在启动QEntL虚拟机...
    echo cd /d "%INSTALL_PATH%\System\VM\bin"
    echo if exist qentl_vm.bat (
    echo     call qentl_vm.bat
    echo ^) else (
    echo     echo 错误: 找不到虚拟机文件 qentl_vm.bat
    echo ^)
    echo pause
    echo goto main_menu
    echo.
    echo :run_compiler
    echo echo.
    echo echo 正在启动QEntL编译器...
    echo cd /d "%INSTALL_PATH%\System\Compiler\bin"
    echo if exist qentl_Compiler.bat (
    echo     call qentl_Compiler.bat
    echo ^) else (
    echo     echo 错误: 找不到编译器文件 qentl_Compiler.bat
    echo ^)
    echo pause
    echo goto main_menu
    echo.
    echo :run_system
    echo echo.
    echo echo 正在运行系统镜像...
    echo cd /d "%INSTALL_PATH%\System\VM\bin"
    echo if exist qentl_vm.bat (
    echo     if exist "%INSTALL_PATH%\System\qbc\system\kernel.qsys" (
    echo         call qentl_vm.bat "%INSTALL_PATH%\System\qbc\system\kernel.qsys"
    echo     ^) else (
    echo         echo 警告: 系统镜像文件不存在，使用默认配置启动...
    echo         call qentl_vm.bat
    echo     ^)
    echo ^) else (
    echo     echo 错误: 找不到虚拟机文件 qentl_vm.bat
    echo ^)
    echo pause
    echo goto main_menu
    echo.
    echo :show_docs
    echo echo.
    echo echo 正在打开文档...
    echo if exist "%INSTALL_PATH%\docs\README.md" (
    echo     start "" "%INSTALL_PATH%\docs\README.md"
    echo ^) else (
    echo     echo 错误: 找不到文档文件
    echo ^)
    echo pause
    echo goto main_menu
) > "%INSTALL_PATH%\QEntL_Launcher.bat"

echo ✅ 创建启动器: QEntL_Launcher.bat

:: Initialize user directories
echo.
echo 🏠 正在初始化用户目录...
echo 复制默认用户配置...

:: Ensure Users directory structure exists
if not exist "%INSTALL_PATH%\Users" mkdir "%INSTALL_PATH%\Users"
if not exist "%INSTALL_PATH%\Users\Default" mkdir "%INSTALL_PATH%\Users\Default"
if not exist "%INSTALL_PATH%\Users\Default\Documents" mkdir "%INSTALL_PATH%\Users\Default\Documents"
if not exist "%INSTALL_PATH%\Users\Default\Documents\QEntL_Projects" mkdir "%INSTALL_PATH%\Users\Default\Documents\QEntL_Projects"
if not exist "%INSTALL_PATH%\Users\Default\Documents\Scripts" mkdir "%INSTALL_PATH%\Users\Default\Documents\Scripts"
if not exist "%INSTALL_PATH%\Users\Default\Documents\Templates" mkdir "%INSTALL_PATH%\Users\Default\Documents\Templates"
if not exist "%INSTALL_PATH%\Users\Default\Programs" mkdir "%INSTALL_PATH%\Users\Default\Programs"
if not exist "%INSTALL_PATH%\Users\Default\Programs\Custom" mkdir "%INSTALL_PATH%\Users\Default\Programs\Custom"
if not exist "%INSTALL_PATH%\Users\Default\Programs\Extensions" mkdir "%INSTALL_PATH%\Users\Default\Programs\Extensions"
if not exist "%INSTALL_PATH%\Users\Default\Settings" mkdir "%INSTALL_PATH%\Users\Default\Settings"
if not exist "%INSTALL_PATH%\Users\Default\Data" mkdir "%INSTALL_PATH%\Users\Default\Data"
if not exist "%INSTALL_PATH%\Users\Default\Data\Cache" mkdir "%INSTALL_PATH%\Users\Default\Data\Cache"
if not exist "%INSTALL_PATH%\Users\Default\Data\Temp" mkdir "%INSTALL_PATH%\Users\Default\Data\Temp"
if not exist "%INSTALL_PATH%\Users\Default\Data\Quantum" mkdir "%INSTALL_PATH%\Users\Default\Data\Quantum"
if not exist "%INSTALL_PATH%\Users\Default\Desktop" mkdir "%INSTALL_PATH%\Users\Default\Desktop"
if not exist "%INSTALL_PATH%\Users\Default\Desktop\Shortcuts" mkdir "%INSTALL_PATH%\Users\Default\Desktop\Shortcuts"
if not exist "%INSTALL_PATH%\Users\Default\Desktop\Widgets" mkdir "%INSTALL_PATH%\Users\Default\Desktop\Widgets"
if not exist "%INSTALL_PATH%\Users\Templates" mkdir "%INSTALL_PATH%\Users\Templates"

:: Create a simple welcome project for the user
echo 创建欢迎项目...
(
    echo // QEntL 欢迎程序
    echo // 这是您的第一个QEntL项目
    echo.
    echo function main^(^) {
    echo     console.log^("欢迎使用QEntL量子编程环境！"^);
    echo     console.log^("您的用户目录位于: " + getUserHome^(^)^);
    echo     
    echo     // 量子叠加态示例
    echo     let qstate = quantum.superposition^([0, 1]^);
    echo     console.log^("量子状态: " + qstate.toString^(^)^);
    echo }
    echo.
    echo main^(^);
) > "%INSTALL_PATH%\Users\Default\Documents\QEntL_Projects\welcome.qentl"

echo ✅ 用户目录初始化完成

:: Installation summary
echo.
echo ========================================================
echo   🎉 QEntL 安装完成！
echo ========================================================
echo.
echo 📊 安装统计:
echo - 安装位置: %INSTALL_PATH%
echo - 安装验证: %VERIFIED%
echo - QEntL系统: ✅ 已安装
if "%HAS_DOCS%"=="true" echo - 文档资料: ✅ 已安装
echo - 启动器: ✅ 已创建
echo.
echo 🚀 下一步:
echo 1. 运行 %INSTALL_PATH%\QEntL_Launcher.bat 启动QEntL
echo 2. 或直接运行 %INSTALL_PATH%\System\VM\bin\qentl_vm.bat
echo 3. 查看文档 %INSTALL_PATH%\docs\README.md
echo.

if "%VERIFIED%"=="false" (
    echo ⚠️  注意: 发现缺失文件，请检查安装完整性
    echo.
)

pause
goto :EOF

:exit_install
echo.
echo 安装已取消。
pause
exit /b 0
