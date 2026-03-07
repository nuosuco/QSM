#!/bin/bash
# QSM Web服务升级脚本
# 从开发版本复制到服务版本

DEV_DIR="/root/QSM/Web"
SERVICE_DIR="/var/www/som.top"
BACKUP_DIR="/var/www/backup"

echo "════════════════════════════════════════════"
echo "  QSM Web服务升级脚本"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════"

# 检查开发目录
if [ ! -d "$DEV_DIR" ]; then
    echo "❌ 开发目录不存在: $DEV_DIR"
    exit 1
fi

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份当前服务版本
if [ -d "$SERVICE_DIR" ]; then
    BACKUP_NAME="som.top.$(date +%Y%m%d_%H%M%S)"
    echo "📦 备份当前版本到: $BACKUP_DIR/$BACKUP_NAME"
    cp -r $SERVICE_DIR "$BACKUP_DIR/$BACKUP_NAME"
fi

# 复制新版本
echo "📤 部署新版本..."
cp -r $DEV_DIR/* $SERVICE_DIR/

# 设置权限
echo "🔐 设置权限..."
chown -R nginx:nginx $SERVICE_DIR
chmod -R 755 $SERVICE_DIR

# 完成
echo "════════════════════════════════════════════"
echo "✅ Web服务升级完成！"
echo "📊 服务版本: $SERVICE_DIR"
echo "📅 升级时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════"
