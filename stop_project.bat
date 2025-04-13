@echo off
chcp 65001 > nul
echo ===================================
echo 量子叠加态模型（QSM）项目停止脚本
echo ===================================

REM 设置环境变量
set QSM_ROOT=%~dp0
set QSM_LOG_DIR=%QSM_ROOT%.logs

echo 正在停止QSM项目...

REM 记录停止前的进程状态
echo 停止前的进程状态: > "%QSM_LOG_DIR%\stop_process.log"
wmic process where "commandline like '%%qentl.bat%%'" get processid,commandline >> "%QSM_LOG_DIR%\stop_process.log" 2>&1

REM 查找并终止所有QEntl进程
echo 正在停止所有QEntl服务...

REM 使用WMIC查找并终止QEntl进程
echo 查找QEntl进程...
wmic process where "commandline like '%%qentl.bat%%'" get processid,commandline

echo 终止QEntl进程...
for /f "tokens=1" %%p in ('wmic process where "commandline like '%%%%qentl.bat%%%%'" get processid ^| findstr /r "[0-9]"') do (
    echo 正在终止进程 %%p
    taskkill /F /PID %%p > nul 2>&1
)

REM 确保所有进程都已终止
timeout /t 2 > nul
echo 检查是否还有剩余进程...
wmic process where "commandline like '%%qentl.bat%%'" get processid,commandline > "%QSM_LOG_DIR%\remaining_processes.txt" 2>&1
if exist "%QSM_LOG_DIR%\remaining_processes.txt" (
    for /f %%i in ('type "%QSM_LOG_DIR%\remaining_processes.txt" ^| find /c /v ""') do (
        if %%i gtr 3 (
            echo 仍有进程未终止，正在强制终止...
            wmic process where "commandline like '%%qentl.bat%%'" call terminate > nul 2>&1
        )
    )
)

REM 清理PID文件
if exist "%QSM_ROOT%.pids" (
    echo 正在清理PID文件...
    del /F /Q "%QSM_ROOT%.pids\*.pid" > nul 2>&1
)

echo.
echo QSM项目已停止！

REM 检查是否还有QEntl进程在运行
wmic process where "commandline like '%%qentl.bat%%'" get processid > nul 2>&1
if not errorlevel 1 (
    echo 警告: 部分QEntl进程可能仍在运行，请手动检查。
    wmic process where "commandline like '%%qentl.bat%%'" get processid,commandline
) else (
    echo 所有QEntl进程已成功停止。
)

REM 清理日志目录中的旧临时文件
echo 清理临时日志文件...
if exist "%QSM_LOG_DIR%\remaining_processes.txt" del "%QSM_LOG_DIR%\remaining_processes.txt"

echo 按任意键退出此窗口...

pause > nul 