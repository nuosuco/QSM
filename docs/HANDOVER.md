# SOM松麦项目交接文档

## 项目概述

SOM松麦是一个中医辨证+有机食品推荐平台，通过AI助手"小麦SOM"为用户提供个性化养生方案，并推荐有机认证的食品产品。

**核心功能：**
- 用户描述症状 → AI辨证分析 → 推荐养生方案 → 推荐有机产品（淘宝/京东联盟）
- 网页版：som.top
- 微信小程序（开发中）
- AI购物助手集成（规划中）

---

## 当前进度

### ✅ 已完成
1. **后端API服务** - FastAPI框架，已测试通过
2. **辨证引擎** - 16种症状匹配，24味药食同源食材，9种体质分类
3. **知识库** - 23个食疗方案
4. **淘宝联盟API** - 已测试通过，可正常搜索商品
5. **网页版前端** - 响应式设计，支持手机/电脑访问
6. **Nginx配置** - 已配置反向代理

### ⏸️ 待完成
1. **京东联盟API** - 应用审核中，审核通过后即可使用
2. **微信小程序** - 框架搭建
3. **AI购物助手集成** - 接口对接
4. **部署到正式服务器** - 需要迁移到腾讯云服务器

---

## 技术架构

```
前端（网页/小程序）
    ↓
Nginx反向代理（80端口）
    ↓
FastAPI后端（8000端口）
    ↓
├── 辨证引擎（bianzheng.py）
├── 知识库（knowledge.py）
├── 商品服务（shop.py）
│   ├── 淘宝联盟API
│   └── 京东联盟API
└── 对话接口（main.py）
```

---

## 项目文件结构

```
/data/SOM/
├── server/                    # 后端服务
│   ├── main.py               # FastAPI入口，API路由
│   ├── config.json           # 配置文件（API密钥）
│   ├── requirements.txt      # Python依赖
│   └── services/
│       ├── __init__.py
│       ├── bianzheng.py      # 辨证引擎（核心）
│       ├── knowledge.py      # 知识库服务
│       └── shop.py           # 商品搜索服务
├── web/                       # 网页前端
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── docs/                      # 文档
│   ├── MASTER_PLAN.md        # 项目总方案
│   └── API_INTEGRATION_GUIDE.md  # API调用指南
└── scripts/                   # 测试脚本
    └── test_api_full.py
```

---

## 核心代码说明

### 1. 辨证引擎（bianzheng.py）

**功能：** 根据用户描述的症状，匹配证型和体质，推荐食材

**数据结构：**
- `SYMPTOM_RULES`：16种症状映射规则
- `YAOSHI_TONGYUAN`：24味药食同源食材（性味、归经、功效、禁忌）
- `TIZHI_LIST`：9种体质分类

**核心方法：**
```python
engine = BianzhengEngine()
result = engine.analyze("我最近失眠，口干")
# 返回：
# {
#   "reply": "根据你的描述...",
#   "tizhi": "阴虚质",
#   "zhengxing": "阴虚火旺",
#   "recommendations": [{"name": "酸枣仁", ...}]
# }
```

### 2. 商品服务（shop.py）

**功能：** 调用淘宝/京东联盟API搜索商品

**淘宝API（已测试通过）：**
- 接口：`taobao.tbk.dg.material.optional.upgrade`
- 地址：`https://eco.taobao.com/router/rest`
- 方法：GET
- 签名：MD5（参数排序 + app_secret前后拼接）

**京东API（待审核）：**
- 接口：`jd.union.open.goods.query`
- 地址：`https://api.jd.com/routerjson`
- 方法：POST
- 签名：MD5
- 注意：时间戳必须是北京时间（UTC+8）

**调用示例：**
```python
shop = ShopService()
items = shop.search("有机枸杞", platform="taobao", page_size=10)
# 返回：
# [
#   {
#     "item_id": "xxx",
#     "title": "有机枸杞500g",
#     "price": "59.9",
#     "image": "https://...",
#     "url": "https://s.click.taobao.com/...",  # 推广链接
#     "platform": "taobao",
#     "commission_rate": "240",  # 佣金比例2.4%
#     "shop_name": "xxx旗舰店"
#   }
# ]
```

### 3. API路由（main.py）

**主要接口：**

1. **对话接口** - `POST /api/chat`
   - 输入：用户消息
   - 输出：辨证结果 + 推荐商品
   - 用途：小麦SOM核心功能

2. **商品搜索** - `GET /api/products/search`
   - 参数：keyword, platform, page, page_size
   - 输出：商品列表

3. **知识库接口**
   - `GET /api/knowledge/yaoshi` - 药食同源食材
   - `GET /api/knowledge/tizhi` - 体质分类
   - `GET /api/knowledge/shiliao` - 食疗方案

4. **健康检查** - `GET /api/health`

---

## API配置

### 淘宝联盟（已验证可用）
```json
{
  "app_key": "34975006",
  "app_secret": "4bbf7dda72ea0a07bbac05005b46c75f",
  "pid": "mm_52057803_3155250154_115831100360",
  "adzone_id": "115831100360",
  "site_id": "3155250154"
}
```

### 京东联盟（审核中）
```json
{
  "app_key": "1c790ba72292dc6723a8145c3ac994f7",
  "app_secret": "bbb6957c76224ca78db994daf03d90d5",
  "site_id": "2035806496"
}
```

---

## 测试结果

### 淘宝API测试（2026-07-22）
```
✅ 商品搜索：成功
✅ 数据解析：正确（已修复字段映射）
✅ 推广链接：正常返回
✅ 佣金信息：正常返回

示例商品：
- 标题：【有机枸杞】杞里香枸杞子500g
- 价格：¥59.9
- 佣金：2.4%
- 店铺：杞里香滋补养生旗舰店
- 推广链接：https://s.click.taobao.com/...
```

### 京东API测试（2026-07-22）
```
⏸️ 状态：应用审核中
⏸️ 错误码：2000（pin for api Limited）
⏸️ 原因：应用未上线
✅ 预期：审核通过后即可正常使用
```

---

## 关键注意事项

### 1. 淘宝API坑点
- **必须用升级版API**：`taobao.tbk.dg.material.optional.upgrade`，不是旧版`taobao.tbk.item.get`
- **返回数据结构**：升级版API的字段名完全不同
  - 价格：`price_promotion_info.zk_final_price`（不是`reserve_price`）
  - 佣金：`publish_info.income_info.commission_rate`（不是`commission_rate`）
  - 推广链接：`publish_info.click_url`（不是`click_url`）
  - 商品ID：顶层`item_id`（不是`item_basic_info.item_id`）

### 2. 京东API坑点
- **时间戳**：必须是北京时间（UTC+8），用`datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))`
- **请求方式**：POST（不是GET）
- **参数格式**：`360buy_param_json`是JSON字符串，需要`json.dumps()`
- **返回数据**：`result`字段是JSON字符串，需要二次解析

### 3. 签名算法（两个平台通用）
```python
def sign(params, app_secret):
    sorted_params = sorted(params.items())
    sign_str = app_secret + ''.join(f"{k}{v}" for k, v in sorted_params) + app_secret
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
```

---

## 部署说明

### 本地测试
```bash
cd /data/SOM/server
pip3 install -r requirements.txt
python3 main.py
# 访问 http://localhost:8000
```

### 生产部署
1. 安装依赖：`pip3 install -r requirements.txt`
2. 配置Nginx反向代理（80端口 → 8000端口）
3. 启动服务：`nohup python3 main.py > server.log 2>&1 &`
4. 配置域名解析（som.top → 服务器IP）

---

## 待开发功能

### 1. 微信小程序
- 页面：首页、小麦SOM对话、商品搜索、个人中心
- 调用后端API：`/api/chat`、`/api/products/search`

### 2. AI购物助手集成
- 将SOM封装为Skill
- 提供标准API接口供AI助手调用
- 支持腾讯AI搜索授权

### 3. 游戏化功能（第二期）
- 护眼训练
- 节气养生挑战
- 积分商城

### 4. 养生谷（第三期）
- 种药材游戏
- 社区系统
- 师徒系统

---

## 常见问题

### Q1: 淘宝API返回空数据？
A: 检查以下几点：
1. API方法名是否正确（必须是`taobao.tbk.dg.material.optional.upgrade`）
2. 权限包是否已申请（16516）
3. 签名算法是否正确
4. 返回数据解析是否使用了正确的字段名

### Q2: 京东API返回错误码2000？
A: 应用未上线，需要到京东联盟后台提交上线审核

### Q3: 如何测试API？
A: 运行测试脚本：`python3 scripts/test_api_full.py`

---

## 联系方式

如有问题，请参考：
- 项目总方案：`/data/SOM/docs/MASTER_PLAN.md`
- API调用指南：`/data/SOM/docs/API_INTEGRATION_GUIDE.md`
- 测试脚本：`/data/SOM/scripts/test_api_full.py`

---

**文档版本：** v1.0  
**更新日期：** 2026-07-22  
**项目状态：** 后端核心功能已完成，淘宝API已调通，京东API待审核
