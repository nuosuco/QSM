#!/bin/bash
# 回收箱自动清理 — 删除7天前回收的junk文件
TRASH=/root/.local/share/Trash/files
find "$TRASH" -type f -name 'junk*' -mtime +7 -delete 2>/dev/null
echo "[$(date +%F' '%T)] 回收箱清理: 删除7天前junk文件完成, 剩余 $(ls "$TRASH" | wc -l) 份"
