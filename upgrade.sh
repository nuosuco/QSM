#!/bin/bash
# QEntL自举升级脚本（调用版本管理）
set -e
cd "$(dirname "$0")"

SRC="${1:-}"
if [ -z "$SRC" ]; then
    echo "用法: $0 <组件源码文件>"
    echo ""
    echo "可用组件:"
    echo "  components/qcl/qcl.qentl      # QCL编译器"
    echo "  components/qvm/qvm.qentl      # QVM运行时"
    echo "  components/qdfs/qdfs.qentl    # QDFS"
    echo "  components/qns/qns.qentl      # QNS"
    echo "  lib/*.qentl                    # 库文件"
    echo "  examples/*.qentl               # 示例"
    exit 1
fi

# 调用版本管理
./version.sh upgrade "$SRC"
