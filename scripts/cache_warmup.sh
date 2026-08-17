#!/bin/bash
# SOM 松麦 - 商品缓存预热脚本
# 定时执行：爬取淘宝联盟商品，更新本地缓存
# 用法：crontab -e 添加：
# 0 */6 * * * /root/SOM/scripts/cache_warmup.sh

cd /root/SOM/server

LOG_FILE="/root/SOM/server/logs/cache_warmup.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "=========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始缓存预热" >> "$LOG_FILE"

# 运行爬虫
/usr/bin/python3.11 -c "
import sys
sys.path.insert(0, '.')
from services.product_crawler import crawl_all
crawl_all()
" >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 缓存预热完成" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"