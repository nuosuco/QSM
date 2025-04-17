@echo off
echo 设置QEntL开发环境...

REM 添加MSYS2路径到环境变量
set PATH=C:\msys64\mingw64\bin;C:\msys64\usr\bin;%PATH%

REM 显示工具版本
echo 检查工具版本:
gcc --version
g++ --version
mingw32-make --version
cmake --version
qentl --version

echo 环境设置完成! 