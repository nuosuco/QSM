@echo off
chcp 65001
setlocal enabledelayedexpansion

:: 设置工作目录
cd /d %~dp0..\..

:: 设置Python虚拟环境
call .venv\Scripts\activate.bat

:: 创建日志目录
if not exist .logs mkdir .logs

:: 启动所有服务
python scripts\services\start_all_services.py --services qsm weq som ref --retry 3 --health-check-interval 30 --log-level INFO --log-dir .logs

endlocal 