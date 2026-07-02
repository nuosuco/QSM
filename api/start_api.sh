#!/bin/bash
# QSM Yi Translation API 启动脚本

cd /root/.openclaw/workspace/QSM/api

echo "=== 启动QSM彝文翻译API服务 ==="
echo ""
echo "端口: 8000"
echo "模型: Qwen3-0.6B + LoRA (合并后)"
echo ""

# 后台运行API服务
nohup python3 qsm_yi_api.py > api.log 2>&1 &
API_PID=$!

echo "API服务已启动 (PID: $API_PID)"
echo "日志文件: api.log"
echo ""
echo "等待服务启动..."
sleep 5

# 检查服务状态
if ps -p $API_PID > /dev/null 2>&1; then
    echo "✅ 服务运行中"
    echo ""
    echo "测试请求:"
    echo "curl http://localhost:8000/"
else
    echo "❌ 服务启动失败，查看日志:"
    cat api.log
fi
