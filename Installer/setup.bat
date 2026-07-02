@echo off
rem QEntL 安装向导
rem 提供图形化安装界面

title QEntL 量子编程系统安装向导

echo.
echo ===========================================
echo    QEntL 量子编程系统安装向导
echo    Quantum Enhancement Language Setup
echo ===========================================
echo.

rem 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 需要管理员权限运行安装程序
    echo 请右键点击"以管理员身份运行"
    pause
    exit /b 1
)

echo 正在启动安装向导...
echo.

rem 设置默认安装路径
set "DEFAULT_INSTALL_PATH=C:\QEntL"
set "INSTALL_PATH=%DEFAULT_INSTALL_PATH%"

rem 显示安装选项
echo 安装选项:
echo 1. 完整安装 (推荐)
echo 2. 自定义安装
echo 3. 开发环境安装
echo 4. 服务器安装
echo 5. 集群节点安装
echo.

set /p "INSTALL_TYPE=请选择安装类型 (1-5): "

rem 根据选择设置安装参数
if "%INSTALL_TYPE%"=="1" (
    set "INSTALL_ARGS=/FULL"
    echo 选择: 完整安装
) else if "%INSTALL_TYPE%"=="2" (
    set "INSTALL_ARGS=/CUSTOM"
    echo 选择: 自定义安装
    goto :custom_options
) else if "%INSTALL_TYPE%"=="3" (
    set "INSTALL_ARGS=/DEV"
    echo 选择: 开发环境安装
) else if "%INSTALL_TYPE%"=="4" (
    set "INSTALL_ARGS=/SERVER"
    echo 选择: 服务器安装
) else if "%INSTALL_TYPE%"=="5" (
    set "INSTALL_ARGS=/CLUSTER"
    echo 选择: 集群节点安装
    goto :cluster_config
) else (
    echo 无效选择，使用默认完整安装
    set "INSTALL_ARGS=/FULL"
)

goto :confirm_install

:custom_options
echo.
echo 自定义安装选项:
echo.
set /p "CUSTOM_PATH=安装路径 (默认: %DEFAULT_INSTALL_PATH%): "
if not "%CUSTOM_PATH%"=="" set "INSTALL_PATH=%CUSTOM_PATH%"

set /p "DESKTOP_SHORTCUT=创建桌面快捷方式? (Y/N): "
set /p "START_MENU=创建开始菜单项? (Y/N): "
set /p "ADD_TO_PATH=添加到系统PATH? (Y/N): "
set /p "INSTALL_SERVICE=安装系统服务? (Y/N): "

if /i "%DESKTOP_SHORTCUT%"=="Y" set "INSTALL_ARGS=%INSTALL_ARGS% /DESKTOP"
if /i "%START_MENU%"=="Y" set "INSTALL_ARGS=%INSTALL_ARGS% /STARTMENU"
if /i "%ADD_TO_PATH%"=="Y" set "INSTALL_ARGS=%INSTALL_ARGS% /PATH"
if /i "%INSTALL_SERVICE%"=="Y" set "INSTALL_ARGS=%INSTALL_ARGS% /SERVICE"

goto :confirm_install

:cluster_config
echo.
echo 集群配置:
set /p "CLUSTER_ROLE=节点角色 (master/worker): "
set /p "MASTER_IP=主节点IP地址: "

set "INSTALL_ARGS=%INSTALL_ARGS% /ROLE=%CLUSTER_ROLE%"
if not "%MASTER_IP%"=="" set "INSTALL_ARGS=%INSTALL_ARGS% /MASTER=%MASTER_IP%"

goto :confirm_install

:confirm_install
echo.
echo 安装确认:
echo - 安装路径: %INSTALL_PATH%
echo - 安装参数: %INSTALL_ARGS%
echo.
set /p "CONFIRM=确认开始安装? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo 安装已取消
    pause
    exit /b 0
)

echo.
echo 正在启动安装程序...
echo.

rem 执行安装
qentl_installer.exe %INSTALL_ARGS% /D="%INSTALL_PATH%"

rem 检查安装结果
if %errorlevel% equ 0 (
    echo.
    echo ===========================================
    echo          安装成功完成！
    echo ===========================================
    echo.
    echo QEntL量子编程系统已成功安装到:
    echo %INSTALL_PATH%
    echo.
    echo 您现在可以:
    echo - 运行桌面上的"QEntL开发环境"
    echo - 在命令行中输入"qentl --help"
    echo - 访问用户手册: %INSTALL_PATH%\docs\user\
    echo.
    echo 感谢您选择QEntL量子编程系统！
) else (
    echo.
    echo ===========================================
    echo          安装失败
    echo ===========================================
    echo.
    echo 安装过程中发生错误，错误代码: %errorlevel%
    echo 请检查:
    echo - 磁盘空间是否充足
    echo - 是否具有管理员权限
    echo - 防病毒软件是否阻止了安装
    echo.
    echo 如需技术支持，请访问: https://support.qentl.org
)

echo.
pause
exit /b %errorlevel%
