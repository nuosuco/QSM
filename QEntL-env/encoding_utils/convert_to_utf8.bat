@echo off
chcp 65001 > nul
echo 正在将源文件转换为UTF-8编码...

rem 创建临时目录
set TEMP_DIR=%~dp0..\temp_encoding
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

rem 转换.c和.h文件
for %%f in ("%~dp0..\src\*.c" "%~dp0..\src\*.h" "%~dp0..\tests\*.c") do (
    echo 处理: %%~nxf
    powershell -Command "Get-Content '%%f' | Set-Content -Encoding UTF8 '%TEMP_DIR%\%%~nxf'"
    copy /y "%TEMP_DIR%\%%~nxf" "%%f" > nul
)

rem 转换.bat文件
echo 处理批处理文件...
for %%f in ("%~dp0..\bin\*.bat") do (
    echo 处理: %%~nxf
    powershell -Command "Get-Content '%%f' | Set-Content -Encoding UTF8 '%TEMP_DIR%\%%~nxf'"
    copy /y "%TEMP_DIR%\%%~nxf" "%%f" > nul
)

rem 清理临时目录
rmdir /s /q "%TEMP_DIR%"

echo 转换完成！所有文件已保存为UTF-8编码（无BOM）。
echo.
echo 注意：如果文件已经是UTF-8格式，此脚本不会改变它们的内容。
pause 