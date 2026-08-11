#!/bin/bash
# QEntL自举升级脚本
# 用法: ./upgrade.sh [源文件]
# 默认源文件: qcl.qentl 或 qvm.qentl

set -e
cd "$(dirname "$0")"

SRC="${1:-qcl.qentl}"
if [ ! -f "$SRC" ]; then
    echo "用法: $0 [源文件]"
    echo "  例: $0 qcl.qentl"
    echo "  例: $0 qvm.qentl"
    exit 1
fi

VERSION=$(cat .current_version)
ARCHIVE_DIR=$(cat .archive_dir)
echo "=== QEntL 自举升级 v$VERSION ==="
echo "源文件: $SRC"
echo "C种子:  bin/q_bootstrap"
echo "运行中:  run/qcl.qbc + run/qvm.qbc"
echo "存档:    archive/$ARCHIVE_DIR/"

# 备份当前run
echo "=== 备份当前版本 ==="
if [ "$ARCHIVE_DIR" = "archive_a" ]; then
    cp -f run/qcl.qbc "archive/a/qcl_v${VERSION}.qbc"
    cp -f run/qvm.qbc "archive/a/qvm_v${VERSION}.qbc"
else
    cp -f run/qcl.qbc "archive/b/qcl_v${VERSION}.qbc"
    cp -f run/qvm.qbc "archive/b/qvm_v${VERSION}.qbc"
fi

# 生成新qbc
echo "=== 编译中... ==="
cp run/qcl.qbc target.qbc
cp "$SRC" input.qentl
rm -f output.qbc
bin/q_bootstrap run run/qvm.qbc

if [ ! -f output.qbc ]; then
    echo "✗ 编译失败"
    exit 1
fi

# 新文件写入run目录
cp output.qbc "run/$(basename "$SRC" .qentl).qbc"
echo "✓ 新 $(basename "$SRC" .qentl).qbc 已生成"

# 版本递增
VERSION=$((VERSION + 1))
echo "$VERSION" > .current_version
echo "=== v$VERSION 完成 ==="
echo ""
echo "下一步: 验证新版本"
echo "  bin/q_bootstrap run run/qvm.qbc   (运行测试)"
echo "  git commit -m 'upgrade to v$VERSION'"
