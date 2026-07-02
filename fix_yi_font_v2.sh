#!/bin/bash
# 彝文字体MIME类型修复脚本
# 清理重复条目并添加正确的字体MIME类型

# 备份原文件
cp /etc/nginx/mime.types /etc/nginx/mime.types.bak.$(date +%Y%m%d_%H%M%S)

# 清理重复条目并添加正确的字体MIME类型
grep -v "font/ttf\|font/otf" /etc/nginx/mime.types.bak > /tmp/mime.types.clean
echo "    font/ttf                                        ttf;" >> /tmp/mime.types.clean
echo "    font/otf                                        otf;" >> /tmp/mime.types.clean

# 移动修复后的文件
mv /tmp/mime.types.clean /etc/nginx/mime.types

# 测试Nginx配置
nginx -t

# 重载Nginx
systemctl reload nginx

echo "=== 彝文字体MIME类型修复完成 ==="
echo "请刷新浏览器页面查看彝文显示效果"