#!/bin/bash
# SOM 松麦 - 一键部署脚本
# 在你的正式服务器上运行: bash deploy.sh

set -e

echo "=== SOM 松麦 部署开始 ==="

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "安装 Python3..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# 2. 安装 Python 依赖
echo "安装 Python 依赖..."
cd /data/SOM/server
pip3 install -r requirements.txt

# 3. 安装 Nginx
if ! command -v nginx &> /dev/null; then
    echo "安装 Nginx..."
    apt-get update && apt-get install -y nginx
fi

# 4. 配置 Nginx
echo "配置 Nginx..."
cat > /etc/nginx/sites-available/som << 'NGINX'
server {
    listen 80;
    server_name som.top www.som.top;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/som /etc/nginx/sites-enabled/som
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx
systemctl enable nginx

# 5. 启动后端服务
echo "启动后端服务..."
cd /data/SOM/server

# 停止旧进程
pkill -f "python3 main.py" 2>/dev/null || true
sleep 1

# 后台启动
nohup python3 main.py > /var/log/som.log 2>&1 &
echo $! > /var/run/som.pid

sleep 3

# 6. 验证
echo "验证服务..."
if curl -s http://localhost:8000/api/health | grep -q "ok"; then
    echo "后端服务 ✓"
else
    echo "后端服务启动失败，请检查 /var/log/som.log"
    exit 1
fi

if curl -s http://localhost/ | grep -q "SOM"; then
    echo "网页前端 ✓"
else
    echo "网页前端异常"
    exit 1
fi

echo ""
echo "=== 部署完成 ==="
echo "访问 http://som.top 查看网站"
echo ""
echo "服务管理命令:"
echo "  查看日志: tail -f /var/log/som.log"
echo "  重启后端: kill \$(cat /var/run/som.pid) && cd /data/SOM/server && nohup python3 main.py > /var/log/som.log 2>&1 &"
echo "  重启Nginx: systemctl restart nginx"
