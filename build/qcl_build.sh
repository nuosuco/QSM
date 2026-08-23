#!/bin/bash
# qcl_build.sh — 编译包装, 统一命名: 编译后自动 output.qbc → 同名.qbc
# 用法: qcl_build.sh server_v14.qentl   →  生成 server_v14.qbc
# 特点:
#   - 用C编译器 bin/qcl_bootstrap (QEntL版run/qcl.qbc有bug)
#   - input.qentl是编译器硬编码输入,先cp再编译
#   - output.qbc是编译器硬编码输出,编译后重命名
#   - 名字统一: .qentl → .qbc (无 output 前缀)
cd /root/QSM/QLife 2>/dev/null || cd /root/QSM/QLife
SRC="$1"
if [ -z "$SRC" ]; then
    echo "用法: $0 <源码.qentl> [输出.qbc]"
    echo "例: $0 build/server_v14.qentl → 生成 build/server_v14.qbc"
    exit 1
fi
BINDIR="$PWD/bin"
EXE=$(printf '%s' "$BINDIR/qcl_bootstrap")
if [ ! -f "$EXE" ]; then
    echo "错误: 编译器不存在" >&2; exit 1
fi
if [ ! -f "$SRC" ]; then
    echo "错误: 源码不存在: $SRC" >&2; exit 1
fi
# 1. cp到硬编码的input.qentl
cp "$SRC" input.qentl
# 2. 编译(output.qbc是硬编码输出)
OUT="$2"
"$EXE" compile input.qentl output.qbc 2>&1
RC=$?
if [ $RC -ne 0 ]; then
    echo "编译失败 (rc=$RC)" >&2
    exit $RC
fi
# 3. 统一命名: output.qbc → 与源码同名 或 指定名
BASE="${SRC%.*}"
if [ -z "$OUT" ]; then
    OUT="${BASE}.qbc"
fi
if [ "$BASE.qbc" != "output.qbc" ] && [ "$OUT" != "output.qbc" ]; then
    cp output.qbc "$OUT"
fi
echo "编译成功: $SRC → $OUT ($(wc -c <"$OUT") bytes)"
exit 0
