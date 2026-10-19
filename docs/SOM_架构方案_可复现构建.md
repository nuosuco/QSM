# 松麦（SOM）平台 架构方案 —— 按本文可一模一样重建

> 更新时间：2026-10-20（版本戳 20261020x）
> 仓库：/root/SOM（git 分支 som，remote origin = github.com/nuosuco/QSM.git）
> 用途：拿本文 + 仓库代码，可在新机器完整重建当前线上松麦。
> 维护约定：每轮大功能/大修复 → 更新本文 → git tag som_vX.Y.Z（备份快照）→ push origin som。

---

## 一、平台定位

松麦（som.top）是「小麦SOM」中医养生健康服务号 H5 应用：
- 拍照/文字辨证（LLM 多模态），出「主证/兼证/体质倾向/食疗配方/养生参考」
- 辨证结果自动搜淘宝联盟好物，生成可长按保存的分享图
- 个人中心：体质记录、健康画像（人脸向量随时间积累）、签到积分、我的收藏（辨证内容+商品双区分页）、分享图生成
- 微信服务号 H5，微信内直接打开（som.top）

## 二、技术架构（分层）

```
微信/浏览器 (som.top H5)
  │  静态前端  web/index.html + web/js/app.js（单页, 4 个 tab: chat/products/profile/yangshenggu）
  ▼
nginx (/etc/nginx/conf.d/som.top.conf)  HTTPS:443, 证书 /etc/nginx/ssl/aliyun_som/som.top.pem
  │  静态 → /root/SOM/web
  │  /api/*、/wechat-callback、/wechat-message → proxy_pass 127.0.0.1:8000
  ▼
som-api.service (systemd, python3.11 uvicorn main:app 0.0.0.0:8000, Restart=always)
  │  EnvironmentFile=/etc/default/llm-keys （LLM/淘宝等密钥, 绝不进 git）
  ▼
server/main.py（约 3150 行, FastAPI 全部端点）+ server/services/*（18 个模块）
  ▼
server/data/user_data.db（SQLite, 15+ 张业务表）+ data/share_tmp（分享图落盘+去重表）
```

## 三、数据层（user_data.db 全表）

| 表 | 作用 | 关键字段 |
|---|---|---|
| users | 用户主表（微信/账密/邮箱/匿名 四合一 user_id） | phone, nickname, email, wechat_openid, password_hash, account, is_anonymous, points |
| chat_history | 对话历史（辨证/养生问答, 跨会话全量接入问诊） | session_id, user_message, assistant_reply, tizhi, zhengxing |
| tizhi_records | 体质辨证存档（1辨证=1对话=1条, 不做 session 去重, advice 存完整分析） | tizhi, zhengxing, symptoms, advice, source(vision/text), photo_features, photo_hash |
| tizhi_test | 体质九分测试 | mode, result_key, result_name, score, answers |
| face_vectors | 人脸特征向量库（一人一户健康地基, 随上传不断学习认到老） | embedding, model_version, created/updated |
| checkin_records | 签到汇总 | last_date, total_points, streak |
| checkin_daily | 签到历史（2026-10-20 新增, streak 唯一事实源） | (user_id, check_date) 唯一键 |
| fav_content | 辨证内容收藏 | title, content, user_message, products, source, content_fp(去重指纹) |
| product_favorites | 商品收藏（多图） | item_id, title, price, image, images(JSON数组), platform, shop_name |
| search_history | 搜索历史 | keyword, platform |
| user_merge_log | 匿名→实名身份合并审计 | user_id_from, user_id_to, reason |
| auth_tokens / verify_codes / password_reset_tokens | 令牌/验证码/重置密码 | — |

**时区铁律**：所有时间戳存 UTC+8 北京时间（som-timezone-unify skill），读/排时间顺序不要再 +8h 双重换算。

## 四、后端模块（server/services/）职责

| 模块 | 职责 |
|---|---|
| llm_router.py | 多 LLM 供应商路由+主备 failover（要分清「端点挂/模型名失效/key 缺失」三种故障） |
| bianzheng.py / bianzheng_data.py | 辨证引擎 v3（四诊合参老中医口径；见「辨证铁律」） |
| chat_engine.py | 文字对话引擎（食材提取过滤词表：食量/份量类词防误当食材进商品搜索） |
| share_image.py（555行） | 服务端 Pillow 渲染分享图（根治微信 canvas 跨域污染） |
| shop.py / product_crawler.py | 淘宝联盟搜索+商品缓存（缓存 ~1GB 上限, cache_gc.py 自动 gc+VACUUM） |
| face_service.py | 人脸向量服务（身份识别必须后端做, 不依赖前端触发） |
| auth_service.py / user_system.py / api_auth.py | 统一认证（四种登录方式归一到同一 user_id, 匿名数据自动合并） |
| knowledge.py / rag.py | 知识库+RAG（食疗/体质/药食） |
| jieqi.py / jieqi_v2.py | 节气养生 |
| stats.py / feedback.py | 数据统计（dashboard/checkin/users/products/chat）+用户反馈 |
| youtube_service.py | YouTube 自动发布（运营侧） |
| cache_gc.py | 商品缓存膨胀治理（保持 ~1GB + VACUUM） |

## 五、分享图体系（本轮修复重点, 全部铁律）

**链路**：前端 POST /api/share/content-image（辨证）或 /api/share/product-image（商品）
→ 服务端 Pillow 渲染 → JPEG 落盘 data/share_tmp → 响应体 + 响应头 `X-Share-Url`（http 直链）
→ 微信内隐藏原生分享按钮，引导长按图片保存。

**当前参数（20261020x）**：
- 辨证图：750 宽，字号 30px 起阶梯（30/28/25/22/20），MAX_H 3600，pad 40，JPEG q75 → 约 355KB（750×3472）
- 商品图：750 宽，cell 650 铺满靠边（与辨证图正文区完全同宽），最多 5 张竖排单张全宽，JPEG q75 → 约 470KB（750×4010）

**性能/正确性铁律**：
1. `_font_cache` 字体对象按尺寸缓存——不缓存时每次 `_font()` 都重新 truetype 加载，渲染 1.25s；缓存后 0.4s
2. 商品图并发下载（ThreadPoolExecutor）+ 磁盘缓存（_load_remote_image 内置），同商品二次分享秒出
3. 同内容 10 分钟去重表（磁盘持久化 share_dedup，重启不丢，二次 0.017s）
4. **直链必须支持 HEAD**：微信识别图片先发 HEAD 探测，不支持就只下 8KB 放弃整条链路（10-20 实锤根因）；直链带 7 天缓存头
5. 渲染前 `_clean_text`：剥 HTML 标签（前端传 textContent 从源头杜绝图里夹代码）+ 剥尾部系统提示（🛒推荐/免责/AI声明/---分隔线），正文一字不删；主证/兼证/体质倾向强制逐行断开，尾部三段顺序固定
6. 内容行数上限 200；超高图自适应压字号行距（微信对超高图下载/识别不稳）
7. 前端 generateProductShareImage 防连点锁（生成中再点提示等待, 防并发打架）

## 六、个人中心（profile tab）功能清单

- 用户卡：头像/昵称/积分/注册时间（统计一律读后端 /api/checkin/status、/api/user/profile，不读 localStorage）
- **签到**：checkin-btn → POST /api/checkin/do；显示「连续 N 天」
  - **铁律（2026-10-20 修 bug）**：streak 唯一事实源 = checkin_daily 表。签到时 INSERT OR IGNORE 一条当天日期；streak 从今天往回连续数。漏一天 = 从 1 重数（正确规则）；不漏绝不丢。
  - 旧算法只存 last_date 单字段：「last_date==昨天就 +1，否则归 1」——时区边界/服务重启/误判一次就直接归 1，累积连续天数全丢。已废。
  - /api/checkin/status 算 streak 时：查历史表必须在 conn.close() 之前（cursor 挂在已 close 的连接上 execute 会炸）
- **我的收藏**（双区分页器）：
  - fav-group-content（辨证内容）+ fav-group-product（商品），各自独立页码，翻页 keepPage 不跳回第 1 页
  - 收藏卡片加载 hook 必须挂每次进页必走入口（loadProfile），别挂悬空调用函数
  - 整页重载 vs 同会话切 tab 区分（重载后重拉；会话内 10 分钟 localStorage 缓存命中秒开，300ms 防抖防并发打三份接口）
  - 辨证内容 mdToHtml 渲染（懒加载）；商品卡多图轮播，首图 product.image 豁免指纹去重
  - 收藏写双通道：前端 localStorage + 后端 /api/favorites/content/add、/api/favorites/add（只写本地=「我」页永远看不到）
- **健康画像**：/api/health/portrait（照片视觉特征+辨证记录随时间积累的多维时间线）
- 体质记录 / 体质测试（health-test-tab）/ 养生谷（yangshenggu tab）

## 七、辨证铁律（som-vision-prompt-postproc skill 沉淀）

- 排版归一：服务端统一追加固定尾部三段（养生参考→🛒推荐→AI声明，剥掉 LLM 自带的/带下划线的尾部）；主证/兼证/体质倾向逐行断开；望诊节标题按节内实际出现项目重写
- 问诊历史：vision 端点按 user_id 跨会话全量接入 chat_history（不做 session 去重）
- 食疗方案商品搜索：食材提取走排除表（食量/份量/做法类词不搜商品），否则搜索灌入垃圾食材
- 拍照辨证：后端每次 /api/chat/vision 自动提脸/存向量/比对返回 face_identity（前端触发不可靠, 微信缓存会丢）；非本人照片拒档（rejected=true 不写 tizhi_records 不污染向量组）

## 八、前端铁律（历次踩坑沉淀）

1. **版本戳**：index.html 里 `app.js?v=20261020x`，每次改前端升一个字母；杀微信后台重进才拉到新版。排查「功能没出现」三查：加载 hook 是否挂必走入口 / 线上 js 是否含新函数 / ?v= 戳是否升级——别归咎微信缓存
2. 微信缓存不可靠：身份识别/数据上报一律后端做
3. 滚动 UI（一键到顶等）：真实滚动容器是 main.main 不是 window
4. 内联 onclick 里的 JSON 要 escapeJsAttr（单引号转义炸 HTML 属性 → 红色 JS 错误条）；收藏按钮用闭包绑定，去掉内联 JSON.stringify
5. 全局错误看 error-trap.js；分享图 new Image 预加载+10s 硬兜底（微信 onload 不触发）
6. 表格窄屏乱码：mdToHtml 表格转卡片；方案二/三商品按 plan 分组（appendGroupedProducts）

## 九、部署清单（新机器重建）

1. 代码：git clone github.com/nuosuco/QSM.git，checkout som 分支
2. Python 3.11 + uvicorn；`pip install -r server/requirements.txt`
3. 密钥：/etc/default/llm-keys（systemd EnvironmentFile；字节级验证服务进程真拿到, 缺 key 会 401——systemd-env-file-keys skill）
4. systemd：som-api.service（User=root, WorkingDirectory=/root/SOM/server, ExecStart=python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000, Restart=always, RestartSec=5, EnvironmentFile=/etc/default/llm-keys）
5. nginx：/etc/nginx/conf.d/som.top.conf（443 ssl + som.top 证书；`root /root/SOM/web`；location /api/、/wechat-callback、/wechat-message 代理 127.0.0.1:8000）
6. 数据库：server/data/user_data.db（首次跑 main.py 自动建表, 含 checkin_daily）
7. 运营：cache_gc.py 定时跑（商品缓存 ~1GB + VACUUM）；微信服务号后台配菜单（URL 路由 ?tab=xxx）+ 网页授权域名
8. 验证清单：GET /api/health、/api/llm/status、/api/checkin/status?user_id=xxx；POST 生成一张分享图看 X-Share-Url 直链 HEAD 200 + image/jpeg；前端首页确认版本戳

## 十、版本与备份约定

- 每轮功能：git commit（中文说明+版本戳）→ `git tag som_vX.Y.Z`（快照）→ `git push origin som <tag>`
- 备份 tag 序列：som_v0.0.6（10-15）→ **som_v0.1.0（10-20, 本次, 含分享图整轮+签到 bug）**
- 遗留事项：qsm-v16-train.service failed（10-11 起, exit 200 数据文件缺失, 与 som 无关, 未处理）
- 前端版本号戳与 git tag 独立：戳是灰度缓存破坏用（x/y/z...），tag 是代码快照用（som_vX.Y.Z）
