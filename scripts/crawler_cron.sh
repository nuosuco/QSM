#!/bin/bash
# SOM 松麦 - 自动爬虫定时任务脚本
# 每20分钟执行一次，自动爬取商品数据到数据库

LOG_FILE="/root/SOM/server/logs/crawler_cron.log"
mkdir -p /root/SOM/server/logs

echo "=== $(date) ===" >> $LOG_FILE
echo "开始执行爬虫任务..." >> $LOG_FILE

cd /root/SOM/server

# 运行爬虫
python3.11 -c "
from services.product_crawler import crawl_all
crawl_all()
" >> $LOG_FILE 2>&1

echo "完成" >> $LOG_FILE
echo "" >> $LOG_FILE