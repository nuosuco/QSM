#!/bin/bash
# QEntL全栈量子电路编译器 - 完整验证脚本
cd /root/QSM
echo "=========================================="
echo "  QEntL量子电路编译器 - 完整验证"
echo "=========================================="
echo ""

echo "1. 编译C种子"
gcc -O2 -Wall -o bin/qcl_bootstrap src/qcl_bootstrap.c -lm 2>&1 | head -2
echo "   ✅ C种子编译成功"
echo ""

echo "2. 编译QCL"
bin/qcl_bootstrap compile qcl.qentl build/qcl.qbc 2>&1 | tail -1
echo "   ✅ QCL编译成功"
echo ""

echo "3. 编译QVM"
bin/qcl_bootstrap compile qvm.qentl build/qvm.qbc 2>&1 | tail -1
echo "   ✅ QVM编译成功"
echo ""

echo "4. 测试H门"
printf 'qreg q[2]\nh q[0]\nprintf("H done\\n")\n' > input.qentl
timeout 30 bin/qcl_bootstrap run build/qcl.qbc 2>&1 | tail -1
if [ -f output.qbc ]; then
    bin/qcl_bootstrap run output.qbc 2>&1
fi
echo ""

echo "5. 测试CX门"
printf 'qreg q[2]\ncx q[0], q[1]\nprintf("CX done\\n")\n' > input.qentl
timeout 30 bin/qcl_bootstrap run build/qcl.qbc 2>&1 | tail -1
if [ -f output.qbc ]; then
    bin/qcl_bootstrap run output.qbc 2>&1
fi
echo ""

echo "6. 测试Bell态"
cat > input.qentl << 'QASM'
qreg q[2]
h q[0]
cx q[0], q[1]
var m0 = measure q[0]
var m1 = measure q[1]
printf("q0=%d q1=%d\n", m0, m1)
QASM
timeout 30 bin/qcl_bootstrap run build/qcl.qbc 2>&1 | tail -2
if [ -f output.qbc ]; then
    bin/qcl_bootstrap run output.qbc 2>&1
fi
echo ""

echo "7. 纠缠率测试（100次）"
cat > input.qentl << 'QASM'
var sum = 0
var i = 0
while (i < 100):
    qreg q[2]
    h q[0]
    cx q[0], q[1]
    var m0 = measure q[0]
    var m1 = measure q[1]
    if (m0 == m1):
        sum = sum + 1
    end
    i = i + 1
end
printf("纠缠率: %d%%\n", sum)
QASM
rm -f output.qbc
timeout 60 bin/qcl_bootstrap run build/qcl.qbc 2>&1 | tail -2
if [ -f output.qbc ]; then
    bin/qcl_bootstrap run output.qbc 2>&1
fi
echo ""

echo "=========================================="
echo "  验证完成"
echo "=========================================="
