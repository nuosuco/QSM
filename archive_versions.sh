#!/bin/bash
# 版本归档管理脚本
# 用法: ./archive_versions.sh [switch|status]

set -e
cd "$(dirname "$0")"

case "${1:-status}" in
    status)
        echo "=== QEntL 版本状态 ==="
        echo "当前版本: $(cat .current_version)"
        echo "当前归档: $(cat .archive_dir)/"
        echo ""
        echo "--- archive/a/ ---"
        ls -la archive/a/*.qbc 2>/dev/null || echo "(空)"
        echo ""
        echo "--- archive/b/ ---"
        ls -la archive/b/*.qbc 2>/dev/null || echo "(空)"
        ;;
    switch)
        if [ "$(cat .archive_dir)" = "archive_a" ]; then
            echo "archive_b" > .archive_dir
            echo "切换到 archive/b/"
        else
            echo "archive_a" > .archive_dir
            echo "切换到 archive/a/"
        fi
        ;;
    clean)
        DIR="archive/$(cat .archive_dir)"
        COUNT=$(ls -1 "$DIR"/*.qbc 2>/dev/null | wc -l)
        if [ "$COUNT" -ge 20 ]; then
            echo "归档已满($COUNT)，清理最早5个..."
            ls -t "$DIR"/*.qbc | tail -5 | xargs rm -f
            echo "已清理"
        else
            echo "归档未满($COUNT/20)，无需清理"
        fi
        ;;
    *)
        echo "用法: $0 [status|switch|clean]"
        ;;
esac
