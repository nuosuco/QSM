@echo off
REM 量子叠加态模型系统 - 自动模板监视器启动脚本

echo 正在启动量子叠加态模型系统自动模板监视器...
cd /d %~dp0..\..python frontend/tools/start_template_watcher.py
echo 监视器已在后台启动!
