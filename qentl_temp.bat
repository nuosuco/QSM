@echo off 
chcp 65001 > nul 
set VERSION=0.1.0 
if \\" "%%~1\==\\ ( 
    echo 错误: 缺少文件名 
    exit /b 1 
) 
REM 获取文件名 
set FILENAME=%%~1 
echo QEntl v%%VERSION%% - 执行文件: %%FILENAME%% 
REM 解析并\\" "执行\QEntl文件 
echo 正在解析QEntl文件... 
REM 根据文件名生成服务信息 
set FILE_NAME=%%~nx1 
set SERVICE_NAME=%%FILE_NAME:.qpy=%% 
set SERVICE_PORT=0 
if \\" "%%FILE_NAME%%\==\run.qpy\ set SERVICE_PORT=3000 
if \\" "%%SERVICE_NAME%%\==\qsm_api\ set SERVICE_PORT=5000 
if \\" "%%SERVICE_NAME%%\==\weq_api\ set SERVICE_PORT=5001 
if \\" "%%SERVICE_NAME%%\==\som_api\ set SERVICE_PORT=5002 
if \\" "%%SERVICE_NAME%%\==\ref_api\ set SERVICE_PORT=5003 
echo 服务已在后台启动: %%SERVICE_NAME%% (端口: %%SERVICE_PORT%%) 
exit /b 0 
