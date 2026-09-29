# -*- coding: utf-8 -*-
"""临时测试脚本：按 llm_providers.json 的 fallback 链实测模型（用 som-api 同款方式调 API）"""
import json, urllib.request, time

d = json.load(open('/root/SOM/server/llm_providers.json'))
providers = d['providers']
fallback = d.get('fallback_model', '')

img = "https://img.alicdn.com/imgextra/i1/O1CN01ZfJh0G1Kqyt3dJbZK_!!6000000001209-0-tps-256-256.jpg"

def call(base_url, api_key, model, content):
    url = base_url.rstrip('/') + '/chat/completions'
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": content}], "max_tokens": 30}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "***" + api_key})
    r = urllib.request.urlopen(req, timeout=40)
    return json.loads(r.read())['choices'][0]['message']['content'][:60]

print("=== 按 SOM fallback 顺序实测（priority 1→2，chat/vision 模型）===")
for p in providers:
    if not p.get('enabled'):
        continue
    print(f"\n--- provider={p['name']} priority={p.get('priority')} ---")
    for role in ['chat', 'vision']:
        m = p['models'].get(role)
        if not m:
            continue
        # 同一模型只测一次
        if role == 'vision' and p['models'].get('chat') == m:
            continue
        content = [{"type": "text", "text": "这张图里是什么颜色？"}, {"type": "image_url", "image_url": {"url": img}}] if role == 'vision' else "回复ok"
        for k in p.get('api_keys', [p.get('api_key')]):
            try:
                out = call(p['base_url'], k, m, content)
                print(f"  {role} {m}: ✅ {out}")
                break
            except Exception as e:
                print(f"  {role} {m}: ❌ key ...{k[-4:]} -> {str(e)[:60]}")
        time.sleep(0.5)

# 兜底模型本身（可能是跨 provider 的）
print(f"\n=== fallback_model={fallback} ===")
for p in providers:
    if p['models'].get('chat') == fallback or p['models'].get('vision') == fallback:
        for k in p.get('api_keys', [p.get('api_key')]):
            try:
                out = call(p['base_url'], k, fallback, "回复ok")
                print(f"  fallback 文字: ✅ {out}")
                break
            except Exception as e:
                print(f"  fallback 文字: ❌ {str(e)[:60]}")
