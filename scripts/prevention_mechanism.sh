#!/bin/bash
# QSM项目防欺骗+防休眠系统机制
# 绝对禁止欺骗与休眠

echo "=== QSM项目防欺骗+防休眠系统启动 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查git提交记录
cd /root/QSM
echo "=== 最近5次提交 ==="
git log --oneline -5
echo ""

# 检查QEntL文件数量
echo "=== QEntL文件数量 ==="
find QEntL -name "*.qentl" | wc -l
echo ""

# 检查磁盘空间
echo "=== 磁盘使用情况 ==="
df -h / | tail -1
echo ""

# 检查是否有未提交的文件
echo "=== 未提交的文件 ==="
git status --short | head -10
echo ""

# 检查子代理状态
echo "=== 子代理状态 ==="
ps aux | grep delegate | head -5
echo ""

# 检查定时任务
echo "=== 定时任务 ==="
crontab -l 2>/dev/null | head -10
echo ""

echo "=== 防欺骗+防休眠系统检查完成 ==="
