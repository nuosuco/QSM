#!/bin/bash
# QEntL自举升级脚本
set -e
cd "$(dirname "$0")"

SRC="${1:-qcl.qentl}"
if [ ! -f "$SRC" ]; then
    echo "用法: $0 [qcl.qentl|qvm.qentl]"
    exit 1
fi

VERSION=$(cat .current_version)
CURRENT_ARCHIVE=$(cat .archive_dir)
echo "=== QEntL 升级 v$VERSION -> v$((VERSION+1)) ==="
echo "源文件: $SRC"
echo "归档: $CURRENT_ARCHIVE/"

# 备份当前版本到归档
if [ "$ARCHIVE_DIR" = "archive_a" ]; then
    cp -f "run/qcl.qbc" "archive/a/qcl_v${VERSION}.qbc"
    cp -f "run/qvm.qbc" "archive/a/qvm_v${VERSION}.qbc"
else
    cp -f "run/qcl.qbc" "archive/b/qcl_v${VERSION}.qbc"
    cp -f "run/qvm.qbc" "archive/b/qvm_v${VERSION}.qbc"
fi

# 每10代切换到b归档，清理a的前两代
if [ "$((VERSION % 10))" -eq 0 ] && [ "$VERSION" -gt 0 ]; then
    ./archive_versions.sh switch
    ./archive_versions.sh clean_oldest
    echo "→ 第${VERSION}代，切换到新归档组"
fi

# 每100代清理全部
if [ "$((VERSION % 100))" -eq 0 ] && [ "$VERSION" -gt 0 ]; then
    ./archive_versions.sh fullclean
    echo "→ 第${VERSION}代，重置版本计数"
fi

# 编译新版本
cp run/qcl.qbc target.qbc
cp "$SRC" input.qentl
rm -f output.qbc
bin/q_bootstrap run run/qvm.qbc

NEW_VER=$((VERSION + 1))
echo "$NEW_VER" > .current_version
echo "✓ v$NEW_VER 完成"
