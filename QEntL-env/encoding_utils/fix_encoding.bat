@echo off
chcp 65001 > nul
echo 修复中文编码问题 - 转换为UTF-8

REM 设置目录
set TEST_DIR=%~dp0..\tests
set SRC_DIR=%~dp0..\src
set BIN_DIR=%~dp0..\bin

echo 正在处理测试文件...
powershell -Command "Get-ChildItem '%TEST_DIR%\*.c' | ForEach-Object { $content = Get-Content $_.FullName -Encoding Default; Set-Content $_.FullName $content -Encoding UTF8 }"

echo 正在处理源代码文件...
powershell -Command "Get-ChildItem '%SRC_DIR%\*.c' | ForEach-Object { $content = Get-Content $_.FullName -Encoding Default; Set-Content $_.FullName $content -Encoding UTF8 }"
powershell -Command "Get-ChildItem '%SRC_DIR%\*.h' | ForEach-Object { $content = Get-Content $_.FullName -Encoding Default; Set-Content $_.FullName $content -Encoding UTF8 }"

echo 正在处理批处理文件...
powershell -Command "Get-ChildItem '%BIN_DIR%\*.bat' | ForEach-Object { $content = Get-Content $_.FullName -Encoding Default; Set-Content $_.FullName $content -Encoding UTF8 }"
powershell -Command "Get-ChildItem '%TEST_DIR%\*.bat' | ForEach-Object { $content = Get-Content $_.FullName -Encoding Default; Set-Content $_.FullName $content -Encoding UTF8 }"

echo 完成！所有文件已转换为UTF-8编码。
echo 请重新编译测试文件以应用更改。 