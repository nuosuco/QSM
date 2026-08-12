#!/bin/bash
# QEntL 双重保险启动器 (qvm_boot.sh) — 纯QEntL启动器的Shell包装
#
# 设计：用bash写轻量包装，QEntL写核心逻辑
# 这是目前最可靠的方式
#
# 双保险启动：
#   第一层: QVM+QCL自举链（主力）
#   第二层: 回退到C种子模式（冗余）

cd "$(dirname "$0")"

# 确保run目录存在
mkdir -p run

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

# 如果有传入的QEntL程序，通过文件传递参数给QEntL启动器
if [ $# -gt 0 ]; then
    INPUT="$1"
    if [ ! -f "$INPUT" ]; then
        echo "错误: 找不到输入文件 $INPUT"
        exit 1
    fi
    
    echo "[BOOT] 自举编译: $INPUT → output.qbc"
    rm -f output.qbc target.qbc input.qentl .qvm_boot_arg
    
    # 将程序路径写入标记文件
    echo "$INPUT" > .qvm_boot_arg
    
    # 运行QVM加载QCL，QCL编译用户程序→output.qbc
    cp run/qcl.qbc target.qbc
    cp "$INPUT" input.qentl
    bin/q_bootstrap run run/qvm.qbc
    
    if [ ! -f "output.qbc" ]; then
        echo "错误: QCL编译失败"
        exit 1
    fi
    
    echo "[BOOT] 编译成功: $(stat -c%s output.qbc) 字节"
    echo "[BOOT] 运行: output.qbc"
    rm -f input.qentl
    cp output.qbc target.qbc
    bin/q_bootstrap run run/qvm.qbc
    exit $?
fi

# 无参数：QVM自举模式
echo "[BOOT] QVM自举启动 (双重保险模式)"
echo "[BOOT] 第一层: QVM+QCL自举链 (主力)"
echo "[BOOT] 第二层: C种子启动器 (冗余备份)"
echo "[BOOT] ====================================="
rm -f output.qbc input.qentl
cp run/qvm.qbc target.qbc
bin/q_bootstrap run run/qvm.qbc
