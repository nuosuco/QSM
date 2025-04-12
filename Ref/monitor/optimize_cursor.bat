@echo off
echo 正在优化系统资源以提高Cursor性能...

:: 清理Windows临时文件
echo 清理临时文件...
del /q/f/s %TEMP%\*
del /q/f/s C:\Windows\Temp\*

:: 关闭不必要的后台进程
echo 关闭可能影响性能的后台进程...
taskkill /f /im "node.exe" /t 2>nul
taskkill /f /im "python.exe" /t 2>nul

:: 清理Cursor缓存
echo 清理Cursor缓存...
rmdir /s /q "%APPDATA%\Cursor\Code Cache" 2>nul
rmdir /s /q "%APPDATA%\Cursor\GPUCache" 2>nul
rmdir /s /q "%APPDATA%\Cursor\CachedData" 2>nul

:: 设置Cursor内存使用
echo 配置Cursor内存参数...
:: 如果需要，请将Cursor快捷方式参数添加到这里

echo 优化完成！现在可以启动Cursor了。
echo 请尝试使用以下命令行参数启动Cursor：
echo cursor.exe --max-old-space-size=8192 --js-flags="--expose-gc"
echo.
echo 或修改Cursor快捷方式，在"目标"字段末尾添加上述参数。
echo.
pause
