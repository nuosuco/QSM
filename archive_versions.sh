#!/bin/bash
# QEntL归档管理脚本
set -e
cd "$(dirname "$0")"

ACTION="${1:-status}"
VERSION=$(cat .current_version)
CURRENT_ARCHIVE=$(cat .archive_dir)

case "$ACTION" in
    status)
        echo "=== QEntL 版本状态 ==="
        echo "当前版本: v$VERSION"
        echo "当前归档: $CURRENT_ARCHIVE/"
        echo ""
        echo "--- archive/a/ ---"
        ls -la archive/a/*.qbc 2>/dev/null || echo "(空)"
        echo ""
        echo "--- archive/b/ ---"
        ls -la archive/b/*.qbc 2>/dev/null || echo "(空)"
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
    clean_oldest)
        # 删除当前归档的前两代
        DIR="archive/$CURRENT_ARCHIVE"
        COUNT=$(ls -1 "$DIR"/*.qbc 2>/dev/null | wc -l)
        if [ "$COUNT" -ge 2 ]; then
            echo "删除最老的两代..."
            ls -t "$DIR"/*.qbc | tail -2 | while read f; do rm -f "$f"; echo "  删除: $f"; done
        fi
        ;;
    fullclean)
        # 每100代清理
        if [ "$((VERSION % 100))" -eq 0 ] && [ "$VERSION" -gt 0 ]; then
            echo "清理所有归档..."
            rm -f archive/a/*.qbc archive/b/*.qbc
            echo "0" > .current_version
            echo "archive_a" > .archive_dir
        fi
        ;;
    *)
        echo "用法: $0 [status|switch|clean_oldest|fullclean]"
        ;;
esac
