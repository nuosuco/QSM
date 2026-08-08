#!/bin/bash
# 持续构建看门狗: 检测新算法文件并自动编译
cd /root/QSM || exit 1
while true; do
    for f in examples/*.qentl; do
        name=$(basename "$f")
        if [ ! -f "build/auto_$name.qbc" ]; then
            cp "$f" input.qentl
            rm -f output.qbc
            if timeout 40 bin/qcl_bootstrap run build/qcl.qbc 2>/dev/null | grep -q "errors=0" && [ -f output.qbc ]; then
                cp output.qbc "build/auto_$name.qbc"
                echo "[$(date +%H:%M:%S)] 编译成功: $name"
            fi
        fi
    done
    sleep 5
done