#!/bin/bash
# QEntL自举升级脚本（调用版本管理）
set -e
cd "$(dirname "$0")"

SRC="${1:-qcl.qentl}"
if [ ! -f "$SRC" ]; then
    echo "用法: $0 [qcl.qentl|qvm.qentl|qdfs.qentl|qns.qentl|...]"
    echo "  可升级的源码: qcl.qentl, qvm.qentl, qdfs.qentl, qns.qentl, lib/*.qentl, examples/*.qentl"
    exit 1
fi

# 调用版本管理
./version.sh upgrade "$SRC"
