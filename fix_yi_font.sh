#!/bin/bash
# 彝文字体MIME类型修复脚本
# 运行此脚本修复彝文显示问题

echo "=== 彝文字体MIME类型修复 ==="

# 备份原文件
cp /etc/nginx/mime.types /etc/nginx/mime.types.bak

# 添加ttf和otf MIME类型（正确格式）
echo "" >> /etc/nginx/mime.types
echo "# 彝文字体支持" >> /etc/nginx/mime.types
echo "    font/ttf                                        ttf;" >> /etc/nginx/mime.types
echo "    font/otf                                        otf;" >> /etc/nginx/mime.types

# 测试配置
nginx -t

# 重载Nginx
systemctl reload nginx

echo "=== 修复完成 ==="
echo "请刷新浏览器页面查看彝文显示效果"
