#!/bin/bash
# QEntL 双重保险启动器 (qvm_boot.sh) v2 — 真自举链
# 使用方式: ./qvm_boot.sh <program.qentl>
#    或:   ./qvm_boot.sh  (自举模式)
#
# 启动链 (真自举):
#   bin/q_bootstrap run run/qvm.qbc   ← C种子只做启动器
#     → QVM加载 target.qbc(=run/qcl.qbc) ← QEntL写的编译器
#       → QCL 编译 input.qentl → output.qbc  ← 真正编译
#
# 双重保险:
#   第一层: C种子 (bin/q_bootstrap) - 永不退役，冗余
#   第二层: QVM+QCL (QEntL写) - 主力启动
#
# ⚠️ 关键: 编译必须走QVM→QCL自举链，
#    绝不能用 bin/q_bootstrap compile (那是C种子内置编译器)

cd "$(dirname "$0")"

# 检查关键文件
for f in "bin/q_bootstrap" "run/qvm.qbc" "run/qcl.qbc"; do
    if [ ! -f "$f" ]; then
        echo "错误: 找不到 $f"
        exit 1
    fi
done

# 编译并运行一个QEntL程序（真自举链）
# 参数: $1 = QEntL源文件路径
run_program() {
    local INPUT="$1"
    if [ ! -f "$INPUT" ]; then
        echo "错误: 找不到输入文件 $INPUT"
        exit 1
    fi

    echo "[BOOT] 自举编译: $INPUT → output.qbc"
    echo "[BOOT]   C种子(启动器) → QVM → QCL(编译) → output.qbc"
    rm -f output.qbc target.qbc

    # 设置QCL为虚拟机目标，用户程序为输入 → 真自举编译
    cp run/qcl.qbc target.qbc
    cat "$INPUT" > input.qentl  # 用cat安全读取，不依赖路径
    bin/q_bootstrap run run/qvm.qbc

    if [ ! -f "output.qbc" ]; then
        echo "错误: 自举编译失败"
        exit 1
    fi
    echo "[BOOT] 编译成功: $(stat -c%s output.qbc) 字节"
}

# 有参数: 编译并运行程序
if [ $# -gt 0 ]; then
    run_program "$1"
    echo "[BOOT] 运行: output.qbc"
    rm -f input.qentl
    cp output.qbc target.qbc
    bin/q_bootstrap run run/qvm.qbc
    exit $?
fi

# 无参数: QVM自举模式（加载自身）
echo "[BOOT] QVM自举启动 (双重保险模式)"
echo "[BOOT] 第一层: C种子 (bin/q_bootstrap) - 冗余备份"
echo "[BOOT] 第二层: QVM+QCL (QEntL写) - 主力启动"
rm -f output.qbc input.qentl
cp run/qvm.qbc target.qbc
bin/q_bootstrap run run/qvm.qbc