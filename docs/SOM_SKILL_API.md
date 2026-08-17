# som.skill API 文档

> SOM 松麦 · 养生能力开放平台  
> 版本：v1.1.1  
> 更新日期：2026-07-28

## 概述

som.skill 是 SOM 松麦平台的养生能力 API 层，将中医辨证、药食同源知识库、有机商品搜索等核心能力以标准 RESTful 接口对外提供，供购物助手、各端小程序、第三方应用调用。

**设计原则：**
- API 先行：所有能力先有干净的 REST 接口，前端只是调用方
- 能力解耦：辨证、测评、商品、用户各自独立模块，可单独调用
- 多端复用：网页和小程序共用同一套后端
- 开放预留：API 设计时考虑第三方调用（鉴权、限流、版本）

---

## 鉴权

### API Key 机制

所有 `/api/skill/*` 管理接口需要管理员权限。业务接口通过 `X-API-Key` 请求头鉴权。

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/skill/status` | GET | 查看开放平台状态 |
| `/api/skill/register-key` | POST | 注册新 API Key（`?name=xxx&rate_limit=60`） |
| `/api/skill/revoke-key` | POST | 撤销 API Key（`?api_key=***`） |

### 限流

- 默认限流：60 次/分钟（滑动窗口）
- 白名单：可配置不限流的 IP/Key
- 超限返回：`429 Too Many Requests`

---

## 核心能力接口

### 1. 中医辨证对话

**POST** `/api/chat`

对话式中医辨证，生成个性化养生方案。

**请求体：**
```json
{
  "message": "最近失眠多梦，口干，容易疲劳",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

**响应：**
```json
{
  "reply": "📋 辨证方向：心肾不交、气虚、阴虚火旺\n🩺 体质偏向：气虚质、阴虚质...",
  "tizhi": "气虚质、阴虚质、气郁质",
  "zhengxing": "心肾不交、气虚、阴虚火旺",
  "recommendations": [
    {
      "name": "酸枣仁",
      "xingwei": "甘、酸，平",
      "gongxiao": "养心补肝，宁心安神",
      "jinji": "实邪郁火者慎用",
      "shiliao": {
        "name": "安神养心粥",
        "recipe": "酸枣仁15g、百合10g、莲子15g、粳米100g",
        "method": "酸枣仁先煎20分钟取汁...",
        "gongxiao": "养心安神，交通心肾",
        "jijie": "适合失眠多梦、心悸不安者"
      }
    }
  ],
  "products": [
    {
      "title": "有机酸枣仁",
      "price": "29.9",
      "image": "https://...",
      "click_url": "https://s.click.taobao.com/...",
      "platform": "taobao"
    }
  ],
  "session_id": "default"
}
```

**引擎说明：**
- 规则辨证引擎（可控可审计，不依赖 LLM）
- RAG 知识库检索（药食同源 + 食疗方案）
- 云端 LLM 增强（商汤 SenseNova / Agnes，可选）

---

### 2. 图片辨证（舌诊）

**POST** `/api/chat/vision`

上传舌苔图片，结合症状进行辨证分析。

**请求体：**
```json
{
  "image_base64": "data:image/jpeg;base64,...",
  "message": "最近容易疲劳",
  "user_id": "optional"
}
```

**响应：** 同 `/api/chat`，额外包含舌象分析结果。

---

### 3. 药食同源知识库

**GET** `/api/knowledge/yaoshi`

返回国家卫健委药食同源目录食材库。

**响应：**
```json
{
  "total": 60,
  "items": [
    {
      "name": "酸枣仁",
      "xingwei": "甘、酸，平",
      "guijing": "心、肝、胆经",
      "gongxiao": "养心补肝，宁心安神",
      "jinji": "实邪郁火者慎用"
    }
  ]
}
```

---

### 4. 体质辨识体系

**GET** `/api/knowledge/tizhi`

返回中医九种体质分类及调养原则。

**响应：**
```json
{
  "total": 9,
  "items": [
    {
      "name": "气虚质",
      "features": "气短懒言、疲乏无力、易出汗",
      "diseases": "易患感冒、内脏下垂",
      "principles": "益气健脾，培补正气"
    }
  ]
}
```

---

### 5. 食疗方案库

**GET** `/api/knowledge/shiliao`

返回证型→食疗方案映射。

**响应：**
```json
{
  "total": 37,
  "items": [
    {
      "zhengxing": "心肾不交",
      "name": "安神养心粥",
      "recipe": "酸枣仁15g、百合10g、莲子15g、粳米100g",
      "method": "酸枣仁先煎20分钟取汁...",
      "gongxiao": "养心安神，交通心肾",
      "jijie": "适合失眠多梦、心悸不安者"
    }
  ]
}
```

---

### 6. 有机商品搜索

**GET** `/api/products/search?keyword=***&category=***`

实时并行搜索淘宝联盟有机商品。

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| category | string | 否 | 分类筛选 |
| page_size | int | 否 | 返回数量（默认20） |

**响应：**
```json
{
  "keyword": "有机红枣",
  "total": 15,
  "items": [
    {
      "title": "新疆有机红枣 500g",
      "price": "39.9",
      "image": "https://...",
      "click_url": "https://s.click.taobao.com/...",
      "shop_name": "xxx旗舰店",
      "platform": "taobao"
    }
  ]
}
```

**注意：** `click_url` 为淘宝联盟推广链接，保留佣金。

---

### 7. 节气养生

**GET** `/api/jieqi/current` — 当前节气养生方案  
**GET** `/api/jieqi/all` — 24节气全量数据

**响应示例：**
```json
{
  "jieqi": "大暑",
  "season": "夏",
  "desc": "一年中最热的时期",
  "yangsheng": "消暑化湿，益气养阴",
  "foods": ["绿豆", "薏米", "莲子", "百合"],
  "tea": "绿豆百合汤",
  "avoid": "避免贪凉伤阳",
  "next_jieqi": "立秋",
  "next_date": "8月7日"
}
```

---

### 8. 护眼训练

**GET** `/api/eye-exercise`

返回眼球运动训练方案 + 明目食疗推荐。

---

### 9. 用户系统

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/user/register` | POST | 用户注册 |
| `/api/tizhi/save` | POST | 保存体质评测记录 |
| `/api/tizhi/records` | GET | 查询体质记录（`?user_id=xxx&limit=5`） |
| `/api/checkin/status` | GET | 签到状态 |
| `/api/checkin/do` | POST | 执行签到 |

---

### 10. 系统状态

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/llm/status` | GET | LLM 服务商状态 |
| `/api/stats/dashboard` | GET | 数据统计面板 |
| `/api/cache/stats` | GET | 商品缓存统计 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.1.1 | 2026-07-28 | som.skill API 鉴权+限流；LLM 路由层；RAG 知识库；图片辨证；节气/护眼模块 |
| v1.1.0 | 2026-07-25 | 数据统计面板；用户反馈机制；缓存预热优化 |
| v1.0.1 | 2026-07-25 | 商品搜索并行优化；click_url 跳转修复 |
| v1.0.0 | 2026-07-23 | 初始版本：辨证引擎 + 商品搜索 + 知识库 |

---

## 接入指南

### 快速开始

```bash
# 1. 健康检查
curl https://som.top/api/health

# 2. 辨证对话
curl -X POST https://som.top/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ***" \
  -d '{"message": "失眠多梦，口干"}'

# 3. 搜索有机商品
curl "https://som.top/api/products/search?keyword=***"
```

### 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 401 | API Key 无效 |
| 429 | 超出限流 |
| 500 | 服务器内部错误 |

---

**文档维护：** SOM 开发团队  
**许可：** 内部使用，第三方接入需申请
