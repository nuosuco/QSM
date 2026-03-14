@echo off
echo ================================================================
echo                QEntL Real Compiler Demo
echo          From Source Code to Bytecode Execution
echo ================================================================
echo.

echo [步骤1] 显示源文件信息
echo 源文件: qbc\tests\microkernel_core.qentl
dir qbc\tests\microkernel_core.qentl
echo.

echo [步骤2] 使用真实编译器进行编译
echo 编译命令: Build\VM\bin\qentl_real_compiler.exe
Build\VM\bin\qentl_real_compiler.exe qbc\tests\microkernel_core.qentl qbc\tests\microkernel_core_demo.qbc
echo.

echo [步骤3] 检查生成的字节码文件
echo 字节码文件: qbc\tests\microkernel_core_demo.qbc
dir qbc\tests\microkernel_core_demo.qbc
echo.

echo [步骤4] 分析字节码文件内容
echo 字节码十六进制内容:
powershell -Command "Format-Hex qbc\tests\microkernel_core_demo.qbc | Select-Object -First 5"
echo.

echo [步骤5] 使用虚拟机执行字节码
echo 执行命令: Build\VM\bin\qentl_vm.exe
Build\VM\bin\qentl_vm.exe qbc\tests\microkernel_core_demo.qbc
echo.

echo ================================================================
echo                     演示完成
echo      QEntL源码 -> 真实编译 -> 字节码 -> 虚拟机执行
echo ================================================================
pause
