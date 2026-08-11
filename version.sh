#!/bin/bash
# QEntL版本管理脚本（支持components结构）
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
        echo "--- components (组件) ---"
        find components -name "*.qentl" -o -name "*.qbc" 2>/dev/null | while read f; do
            echo "  $f ($(stat -c%s "$f" 2>/dev/null || echo "?") 字节)"
        done
        echo ""
        echo "--- versions (历史版本) ---"
        ls -d versions/v* 2>/dev/null | while read dir; do
            VER=$(basename $dir)
            COUNT=$(find "$dir" -name "*.qbc" 2>/dev/null | wc -l)
            echo "  $VER: $COUNT 个qbc文件"
        done
        echo ""
        echo "--- archive ---"
        echo "archive/a: $(ls archive/a/*.qbc 2>/dev/null | wc -l) 文件"
        echo "archive/b: $(ls archive/b/*.qbc 2>/dev/null | wc -l) 文件"
        ;;
    snapshot)
        echo "创建版本快照 v${VERSION}..."
        mkdir -p "versions/v${VERSION}/components"
        
        # 复制所有组件到版本快照
        if [ -d components ]; then
            cp -r components "versions/v${VERSION}/"
        fi
        
        # 复制库文件
        if [ -d lib ]; then
            mkdir -p "versions/v${VERSION}/lib"
            cp -r lib/*.qentl "versions/v${VERSION}/lib/" 2>/dev/null || true
        fi
        
        # 复制examples
        if [ -d examples ]; then
            mkdir -p "versions/v${VERSION}/examples"
            cp -r examples/*.qentl "versions/v${VERSION}/examples/" 2>/dev/null || true
        fi
        
        echo "✓ 快照完成: versions/v${VERSION}/"
        ;;
    new)
        NEW_VERSION=$((VERSION + 1))
        echo "$NEW_VERSION" > .current_version
        mkdir -p "versions/v${NEW_VERSION}"
        echo "✓ 创建版本 v${NEW_VERSION}"
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
        SRC="${2:-}"
        if [ -z "$SRC" ]; then
            echo "用法: $0 upgrade <源文件>"
            echo "  例: $0 upgrade components/qcl/qcl.qentl"
            exit 1
        fi
        
        if [ ! -f "$SRC" ]; then
            echo "错误: 文件不存在: $SRC"
            exit 1
        fi
        
        echo "=== QEntL 升级 v${VERSION} -> v$((VERSION+1)) ==="
        echo "源文件: $SRC"
        
        # 获取组件名
        COMPONENT_DIR=$(dirname "$SRC")
        COMPONENT_NAME=$(basename "$COMPONENT_DIR")
        SOURCE_NAME=$(basename "$SRC" .qentl)
        
        # 备份当前版本到归档
        if [ "$CURRENT_ARCHIVE" = "archive_a" ]; then
            # 备份当前运行的产物
            for f in run/*.qbc; do
                [ -f "$f" ] && cp -f "$f" "archive/a/$(basename $f .qbc)_v${VERSION}.qbc"
            done
        else
            for f in run/*.qbc; do
                [ -f "$f" ] && cp -f "$f" "archive/b/$(basename $f .qbc)_v${VERSION}.qbc"
            done
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
        
        # 复制到components目录
        if [ -f output.qbc ]; then
            cp -f output.qbc "$COMPONENT_DIR/${SOURCE_NAME}.qbc"
            echo "✓ ${COMPONENT_NAME}/${SOURCE_NAME}.qbc 已更新"
        fi
        
        # 创建版本快照
        NEW_VERSION=$((VERSION + 1))
        ./version.sh snapshot
        
        echo "$NEW_VERSION" > .current_version
        echo "✓ v${NEW_VERSION} 完成"
        ;;
    *)
        echo "用法: $0 [status|new|snapshot|switch|clean|fullclean|upgrade <src>]"
        echo ""
        echo "示例:"
        echo "  $0 status                    # 查看状态"
        echo "  $0 snapshot                  # 创建快照"
        echo "  $0 upgrade components/qcl/qcl.qentl  # 升级QCL"
        ;;
esac
