#!/bin/bash
# QEntL 双重保险启动器 (qvm_boot.sh)
# 使用方式: ./qvm_boot.sh [program.qentl]
#
# 启动链:
#   第一层: C种子 (bin/q_bootstrap) - 永不退役，冗余备份
#   第二层: QVM自举 (qvm.qentl) - 主力启动
#   第三层: QCL自举 (qcl.qentl) - 编译器
#
# 工作原理:
#   1. 如果没有参数，QVM加载自身并运行target.qbc（自举模式）
#   2. 如果有程序参数，用QCL编译并运行
#   3. 自动管理symlink target.qbc → run/qvm.qbc

cd "$(dirname "$0")"

# 确保run目录存在
mkdir -p run

# 创建/更新symlink: target.qbc → run/qvm.qbc
ln -sf run/qvm.qbc target.qbc

# 检查关键文件
if [ ! -f "bin/q_bootstrap" ]; then
    echo "错误: 找不到 bin/q_bootstrap (C种子)"
    exit 1
fi

if [ ! -f "run/qvm.qbc" ]; then
    echo "错误: 找不到 run/qvm.qbc (QVM)"
    exit 1
fi

if [ ! -f "run/qcl.qbc" ]; then
    echo "错误: 找不到 run/qcl.qbc (QCL)"
    exit 1
fi

# 如果有传入的QEntL程序，用QCL编译并运行
if [ $# -gt 0 ]; then
    INPUT="$1"
    if [ ! -f "$INPUT" ]; then
        echo "错误: 找不到输入文件 $INPUT"
        exit 1
    fi
    
    echo "[BOOT] 编译: $INPUT → output.qbc (使用QCL)"
    rm -f output.qbc target.qbc input.qentl
    
    # 设置QCL作为虚拟机，用户程序作为输入
    cp run/qcl.qbc target.qbc
    cp "$INPUT" input.qentl
    
    # 运行QVM，QVM会运行QCL，QCL编译用户程序→output.qbc
    bin/q_bootstrap run run/qvm.qbc
    
    if [ ! -f "output.qbc" ]; then
        echo "错误: QCL编译失败"
        exit 1
    fi
    
    echo "[BOOT] 运行: output.qbc"
    # 保留input.qentl，仅复制output.qbc到target.qbc
    cp output.qbc target.qbc
    rm -f input.qentl  # 只在最终运行时清理
    
    # 重新运行QVM执行程序
    bin/q_bootstrap run run/qvm.qbc
    exit $?
fi

# 自举模式：QVM加载自身
echo "[BOOT] QVM自举启动 (双重保险模式)"
echo "[BOOT] 第一层: C种子 (bin/q_bootstrap) - 冗余备份"
echo "[BOOT] 第二层: QVM自举 (run/qvm.qbc) - 主力启动"
echo "[BOOT] ====================================="

bin/q_bootstrap run run/qvm.qbc
