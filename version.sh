#!/bin/bash
# QEntL版本管理脚本
set -e
cd "$(dirname "$0")"

ACTION="${1:-status}"
VERSION=$(cat .current_version 2>/dev/null || echo "1")
CURRENT_ARCHIVE=$(cat .archive_dir 2>/dev/null || echo "archive_a")

case "$ACTION" in
    status)
        echo "=== QEntL 版本状态 ==="
        echo "当前版本: v$VERSION"
        echo "当前归档: $CURRENT_ARCHIVE/"
        echo ""
        echo "--- run (当前运行) ---"
        ls -la run/*.qbc 2>/dev/null || echo "(空)"
        echo ""
        echo "--- versions (历史版本) ---"
        ls -d versions/v* 2>/dev/null | while read dir; do
            VER=$(basename $dir)
            COUNT=$(ls "$dir"/*.qbc 2>/dev/null | wc -l)
            echo "  $VER: $COUNT 个qbc文件"
        done
        echo ""
        echo "--- archive ---"
        echo "archive/a: $(ls archive/a/*.qbc 2>/dev/null | wc -l) 文件"
        echo "archive/b: $(ls archive/b/*.qbc 2>/dev/null | wc -l) 文件"
        ;;
    new)
        # 创建新版本
        NEW_VERSION=$((VERSION + 1))
        echo "$NEW_VERSION" > .current_version
        mkdir -p "versions/v${NEW_VERSION}"
        echo "✓ 创建版本 v${NEW_VERSION}"
        ;;
    snapshot)
        # 创建当前版本的快照
        echo "创建版本快照 v${VERSION}..."
        mkdir -p "versions/v${VERSION}"
        cp -f qcl.qentl "versions/v${VERSION}/" 2>/dev/null || true
        cp -f qvm.qentl "versions/v${VERSION}/" 2>/dev/null || true
        cp -f run/qcl.qbc "versions/v${VERSION}/" 2>/dev/null || true
        cp -f run/qvm.qbc "versions/v${VERSION}/" 2>/dev/null || true
        echo "✓ 快照完成"
        ;;
    switch)
        if [ "$CURRENT_ARCHIVE" = "archive_a" ]; then
            echo "archive_b" > .archive_dir
            echo "切换到 archive/b/"
        else
            echo "archive_a" > .archive_dir
            echo "切换到 archive/a/"
        fi
        ;;
    clean)
        DIR="archive/$CURRENT_ARCHIVE"
        COUNT=$(ls -1 "$DIR"/*.qbc 2>/dev/null | wc -l)
        if [ "$COUNT" -ge 2 ]; then
            ls -t "$DIR"/*.qbc | tail -2 | while read f; do rm -f "$f"; echo "删除: $f"; done
        fi
        ;;
    fullclean)
        if [ "$((VERSION % 100))" -eq 0 ] && [ "$VERSION" -gt 0 ]; then
            rm -f archive/a/*.qbc archive/b/*.qbc
            echo "0" > .current_version
            echo "archive_a" > .archive_dir
            echo "✓ 清理完成，从v1重新开始"
        fi
        ;;
    upgrade)
        SRC="${2:-qcl.qentl}"
        echo "=== QEntL 升级 v${VERSION} -> v$((VERSION+1)) ==="
        echo "源文件: $SRC"
        
        # 保存当前版本到归档
        if [ "$CURRENT_ARCHIVE" = "archive_a" ]; then
            cp -f run/qcl.qbc "archive/a/qcl_v${VERSION}.qbc" 2>/dev/null || true
            cp -f run/qvm.qbc "archive/a/qvm_v${VERSION}.qbc" 2>/dev/null || true
        else
            cp -f run/qcl.qbc "archive/b/qcl_v${VERSION}.qbc" 2>/dev/null || true
            cp -f run/qvm.qbc "archive/b/qvm_v${VERSION}.qbc" 2>/dev/null || true
        fi
        
        # 每10代切换归档
        if [ "$((VERSION % 10))" -eq 0 ] && [ "$VERSION" -gt 0 ]; then
            ./version.sh switch
            ./version.sh clean
            echo "→ 第${VERSION}代，切换到新归档"
        fi
        
        # 每100代全清理
        if [ "$((VERSION % 100))" -eq 0 ] && [ "$VERSION" -gt 0 ]; then
            ./version.sh fullclean
            echo "→ 第${VERSION}代，重置版本"
        fi
        
        # 编译新版本
        cp run/qcl.qbc target.qbc
        cp "$SRC" input.qentl
        rm -f output.qbc
        bin/q_bootstrap run run/qvm.qbc
        
        # 复制到versions目录
        NEW_VERSION=$((VERSION + 1))
        mkdir -p "versions/v${NEW_VERSION}"
        if [ -f "$SRC" ]; then
            cp -f "$SRC" "versions/v${NEW_VERSION}/"
        fi
        if [ -f output.qbc ]; then
            BASENAME=$(basename "$SRC" .qentl)
            cp -f output.qbc "versions/v${NEW_VERSION}/${BASENAME}.qbc"
        fi
        
        echo "$NEW_VERSION" > .current_version
        echo "✓ v${NEW_VERSION} 完成"
        ;;
    *)
        echo "用法: $0 [status|new|snapshot|switch|clean|fullclean|upgrade <src>]"
        ;;
esac
