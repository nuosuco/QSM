@echo off 
chcp 65001 > nul 
set VERSION=0.1.0 
if \\" "%%~1\==\\ ( 
    echo ����: ȱ���ļ��� 
    exit /b 1 
) 
REM ��ȡ�ļ��� 
set FILENAME=%%~1 
echo QEntl v%%VERSION%% - ִ���ļ�: %%FILENAME%% 
REM ������\\" "ִ��\QEntl�ļ� 
echo ���ڽ���QEntl�ļ�... 
REM �����ļ������ɷ�����Ϣ 
set FILE_NAME=%%~nx1 
set SERVICE_NAME=%%FILE_NAME:.qpy=%% 
set SERVICE_PORT=0 
if \\" "%%FILE_NAME%%\==\run.qpy\ set SERVICE_PORT=3000 
if \\" "%%SERVICE_NAME%%\==\qsm_api\ set SERVICE_PORT=5000 
if \\" "%%SERVICE_NAME%%\==\weq_api\ set SERVICE_PORT=5001 
if \\" "%%SERVICE_NAME%%\==\som_api\ set SERVICE_PORT=5002 
if \\" "%%SERVICE_NAME%%\==\ref_api\ set SERVICE_PORT=5003 
echo �������ں�̨����: %%SERVICE_NAME%% (�˿�: %%SERVICE_PORT%%) 
exit /b 0 
