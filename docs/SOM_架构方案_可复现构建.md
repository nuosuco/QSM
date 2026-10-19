# 松麦（SOM）平台 架构方案 —— 按本文可一模一样重建

> 更新时间：2026-10-20（版本戳 20261020x）
> 目标读者：拿到本文 + /root/SOM 代码仓库，可以在一台新机器上完整重建当前线上松麦。
> 维护约定：每完成一轮大功能/大修复，更新本文 + git tag som_vX.Y.Z + 推远程。

---

## 一、平台定位

松麦（som.top）是「小麦 SOM」中医养生健康服务号网页应用：
- 用户拍照/文字辨证（LLM 多模态），出「主证/兼证/体质倾向/食疗配方/养生参考」
- 辨证结果自动搜淘宝联盟好物，生成可长按保存的分享图
- 个人中心：体质记录、健康画像（人脸向量随时间积累）、签到积分、我的收藏（辨证内容+商品双区）、分享图生成
- 微信服务号 H5（som.top），微信内直接打开

## 二、技术架构（分层）

```
微信/浏览器 (som.top H5)
   │ 静态前端  web/index.html + js/app.js(单页, 4 tab: chat/products/profile/yangshenggu)
   ▼
nginx (som.top.conf)  HTTPS:443 证书 /etc/nginx/ssl/aliyun_som/som.top.pem
   │  静态 → /root/SOM/web
   │  /api/*、/wechat-callback、/wechat-message → proxy 127.0.0.1:8000
   ▼
som-api.service (systemd, python3.11 uvicorn main:app 0.0.0.0:8000)
   EnvironmentFile=/etc/default/llm-keys  (LLM/淘宝等密钥, 别进 git)
   ▼
server/main.py (3154 行, FastAPI 全部端点) + server/services/* (18 个模块)
   ▼
server/data/user_data.db (SQLite, 15 张业务表) + data/share_tmp (分享图落盘+去重)
```

## 三、数据层（user_data.db 全表）

| 表 | 作用 | 关键字段 |
|---|---|---|
| users | 用户主表（四种登录统一 user_id） | user_id, phone, nickname, email, wechat_openid, password_hash, account, is_anonymous, points |
| chat_history | 对话历史（辨证/养生问答） | session_id, user_message, assistant_reply, tizhi, zhengxing |
| tizhi_records | 体质辨证存档（1辨证=1对话=1条，advice 存完整分析） | tizhi, zhengxing, symptoms, advice, source(vision/text), photo_features, photo_hash |
| tizhi_test | 体质九分测试 | mode, result_key, result_name, score, answers |
| face_vectors | 人脸特征向量库（一人一户健康地基） | embedding, model_version, created/updated |
| checkin_records | 签到汇总 | last_date, total_points, streak |
| checkin_daily | 签到历史（2026-10-20 新增，streak 唯一事实源） | (user_id, check_date) 唯一键 |
| fav_content | 辨证内容收藏 | title, content, user_message, products, source, content_fp(去重指纹) |
| product_favorites | 商品收藏（多图） | item_id, title, price, image, images(JSON数组), platform, shop_name |
| search_history | 搜索历史 | keyword, platform |
| user_merge_log | 匿名→实名身份合并审计 | user_id_from, user_id_to, reason |
| auth_tokens / verify_codes / password_reset_tokens | 令牌/验证码/重置密码 | — |

## 四、后端模块（server/services/）职责

- **llm_router.py**：多 LLM 供应商路由+主备 failover（端点挂/模型名失效/key 缺失三种故障要能分清）
- **bianzheng.py / bianzheng_data.py**：辨证引擎 v3（四诊合参老中医口径；prompt 后处理铁律：排版归一/尾部三段固定/问诊历史跨会话全量接入）
- **chat_engine.py**：文字对话引擎（食材提取过滤词表：食量/份量类词防误当食材进商品搜索）
- **share_image.py（555行）**：服务端 Pillow 渲染分享图（微信 canvas 跨域污染的铁律解法）
- **shop.py / product_crawler.py**：淘宝联盟搜索+商品缓存（缓存 ~1GB 上限，cache_gc.py 自动 gc+VACUUM）
- **face_service.py**：人脸向量服务（识别必须后端做，不依赖前端触发）
- **auth_service.py / user_system.py / api_auth.py**：统一认证（微信/账密/邮箱/匿名四合一 user_id）
- **knowledge.py / rag.py**：知识库+RAG（食疗/体质/药食）
- **jieqi.py / jieqi_v2.py**：节气养生
- **stats.py / feedback.py**：数据统计+用户反馈
- **youtube_service.py**：YouTube 自动发布（运营侧）
- **cache_gc.py**：商品缓存膨胀治理（保持 ~1GB + VACUUM）

## 五、分享图体系（本轮修复的重点，铁律）

**链路**：前端 POST /api/share/content-image（辩证）或 /api/share/product-image（商品）
→ 服务端 Pillow 渲染 → JPEG 落盘 data/share_tmp → 返回 body + 响应头 `X-Share-Url`（http 直链）
→ 微信内隐藏原生分享按钮，引导长按图片保存。

当前参数（20261020x）：
- 辩证图：750 宽，字号 30px 起阶梯(30/28/25/22/20)，MAX_H 3600，pad 40，JPEG q75 → 约 355KB
- 商品图：750 宽，cell 650 铺满靠边（与辩证图正文区同宽），5 张竖排，JPEG q75 → 约 470KB
- 性能铁律：
  1. `_font_cache` 字体按尺寸缓存（不缓存渲染 1.25s，缓存后 0.4s）
  2. 商品图并发下载（ThreadPoolExecutor）+ 磁盘缓存（_load_remote_image）
  3. 同内容 10 分钟去重表（磁盘持久化，重启不丢，二次 0.017s）
  4. 直链必须支持 HEAD（微信识别先 HEAD 探测，不支持就只下 8KB 放弃整条链路）+ 7 天缓存头
  5. 内容渲染前 `_clean_text` 剥 HTML 标签 + 剥尾部系统提示（🛒推荐/免责/AI声明/---），正文一字不删
  6. 前端传 textContent（不是 innerHTML）从源头杜绝图里夹代码

## 六、个人中心（profile tab）功能清单

- 用户卡：头像/昵称/积分/注册时间
- **签到**：checkin-btn → POST /api/checkin/do；streak 显示「连续 N 天」
  - 铁律（2026-10-20 修）：streak 唯一事实源 = checkin_daily 表，签到时 INSERT OR IGNORE，从今天往回连续数；漏一天=从 1 重数（正确规则），但不漏绝不丢。旧 last_date 单字段算法已废（会因时区边界/重启误判归 1）
  - status 接口算 streak 时：查历史表必须在 conn.close() 之前（cursor 在已 close 连接上 execute 会炸）
- **我的收藏**（双区分页器）：
  - fav-group-content（辨证内容）+ fav-group-product（商品），各自独立页码（keepPage 翻页不跳回第 1 页）
  - 收藏卡片 hook 必须挂每次进页必走入口（loadProfile），别挂悬空调用函数
  - 整页重载 vs 同会话切 tab 要区分（重载后重拉，会话内缓存命中秒开，10 分钟 localStorage）
  - 辨证内容渲染用 mdToHtml（懒加载），商品卡多图轮播（首图 product.image 豁免指纹去重）
- **健康画像**：/api/health/portrait（照片视觉特征+辨证记录随时间积累的多维时间线）
- 体质记录 / 体质测试 / 养生谷（yangshenggu tab）

## 七、前端铁律（历次踩坑沉淀）

1. **版本戳**：index.html 里 `app.js?v=20261020x`，每次改前端升一个字母；用户杀微信后台重进才拉到新版——排查「功能没出现」先确认用户拉没拉到新戳，别归咎微信缓存
2. 微信缓存不可靠：身份识别/数据上报一律后端做
3. 一键到顶等滚动 UI：真实滚动容器是 main.main 不是 window
4. 内联 onclick 里的 JSON 要 escapeJsAttr（单引号转义炸 HTML 属性 → 红色 JS 错误条）
5. 全局错误看 error-trap.js；功能「没出现」三查：加载 hook 是否在必走入口 / 线上 js 是否含新函数 / ?v= 戳是否升级

## 八、部署清单（新机器重建）

1. 代码：git clone 仓库，checkout som 分支
2. Python 3.11 + uvicorn；`pip install -r server/requirements.txt`
3. 密钥：/etc/default/llm-keys（EnvironmentFile，字节级验证服务进程真拿到，缺 key 会 401）
4. systemd：som-api.service（WorkingDirectory=/root/SOM/server，ExecStart uvicorn main:app 0.0.0.0:8000，Restart=always）
5. nginx：som.top.conf（443 ssl + 证书 som.top.pem/key；静态 /root/SOM/web；/api/ 与 /wechat-callback、/wechat-message 代理 8000）
6. 数据库：server/data/user_data.db（首次运行 main.py 自动建表，含 checkin_daily）
7. 运营：cache_gc.py 定时跑（商品缓存 ~1GB + VACUUM）；微信服务号后台配菜单（URL 路由 ?tab=xxx）+ 网页授权
8. 验证：/api/health、/api/llm/status、/api/checkin/status、生成一张分享图看 X-Share-Url 直链 HEAD 200

## 九、版本与备份约定

- 每次功能轮：git commit（中文说明+版本戳）→ `git tag som_vX.Y.Z`（快照）→ `git push origin som`（remote: nuosuco/QSM）
- 当前基线：som_v0.0.6（10-15 前），本轮改动 10-16~10-20 共 8 个版本戳（u/x），最新 HEAD 待打 som_v0.1.0
- 遗留：qsm-v16-train.service failed（10-11 起，exit 200 数据文件缺失，与 som 无关，未处理）
