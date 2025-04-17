@echo off
echo 正在运行QEntL代码库修复脚本...
powershell -ExecutionPolicy Bypass -File "%~dp0fix_codebase.ps1"
echo.
echo 修复脚本已运行完成。
echo 按任意键退出...
pause > nul 