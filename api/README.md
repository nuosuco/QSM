# QSM Yi Translation API

彝文翻译API服务 - 基于训练好的LoRA模型

## 服务状态

✅ **已部署**: `http://服务器IP:8000`

## 端点

### 1. 服务信息
```
GET /
```

响应示例:
```json
{
  "status": "ok",
  "service": "QSM Yi Translation API",
  "model": "Qwen3-0.6B + LoRA",
  "endpoints": {
    "translate": "POST /translate",
    "health": "GET /"
  }
}
```

### 2. 健康检查
```
GET /health
```

响应示例:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. 翻译请求
```
POST /translate
Content-Type: application/json

{
  "text": "要翻译的文本",
  "direction": "yi2zh" 或 "zh2yi"
}
```

参数说明:
- `text`: 要翻译的文本（彝文或中文）
- `direction`: 翻译方向
  - `yi2zh`: 彝文转中文
  - `zh2yi`: 中文转彝文

响应示例:
```json
{
  "success": true,
  "original": "ꀊ",
  "translated": "人",
  "direction": "yi2zh"
}
```

## 部署信息

- **模型**: Qwen3-0.6B + LoRA (合并后)
- **模型大小**: 2.3GB
- **训练数据**: 4120条彝文三语对照
- **端口**: 8000
- **进程PID**: 检查 `ps aux | grep qsm_yi_api`

## 使用示例

### cURL
```bash
# 彝文转中文
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"ꀊ","direction":"yi2zh"}'

# 中文转彝文
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text":"人","direction":"zh2yi"}'
```

### Python
```python
import requests

# 彝文转中文
response = requests.post(
    "http://localhost:8000/translate",
    json={"text": "ꀊ", "direction": "yi2zh"}
)
print(response.json())

# 中文转彝文
response = requests.post(
    "http://localhost:8000/translate",
    json={"text": "人", "direction": "zh2yi"}
)
print(response.json())
```

## 管理命令

```bash
# 启动服务
cd /root/.openclaw/workspace/QSM/api
python3 qsm_yi_api.py

# 后台运行
nohup python3 qsm_yi_api.py > api.log 2>&1 &

# 查看日志
tail -f api.log

# 停止服务
pkill -f qsm_yi_api
```

## 注意事项

1. 首次请求需要模型加载时间（约10秒）
2. 服务器无GPU，推理在CPU上进行
3. 建议在生产环境使用GPU加速

---

**创建时间**: 2026-04-09
**模型版本**: QSM V3 (Qwen3-0.6B + LoRA)
