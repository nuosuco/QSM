#!/bin/bash
# QSM系统启动脚本 - Linux/Mac版

echo "正在启动QSM系统..."

# 创建必要的目录
mkdir -p QSM/logs
mkdir -p Ref/logs
mkdir -p Ref/data
mkdir -p Ref/backup/files

# 检查是否安装了watchdog库
python3 -c "import watchdog" &>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装必要的依赖..."
    pip3 install watchdog
fi

# 启动QSM系统
python3 QSM/main.py "$@"

echo "QSM系统已停止" 
#
量子基因编码: QE-STA-5C0397D5E8A9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
