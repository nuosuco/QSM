# SOM 人脸识别 · 向量积累 · 健康画像 实现方案

> 2026-10-14 中华要求沉淀。一人一户健康大数据的根基：身份识别必须后端做，
> 别人照片拒档、本人向量组随时间学习、健康画像多维时间线。

## 1. 身份识别（谁做的）

**不是小麦（LLM）做的，是服务端本地 ArcFace 小模型做的。**

- 小麦（LLM，SenseNova）只负责看舌苔/面色/患处做**辨证分析**（阴阳虚实等），**不认脸**。
- 认脸走 `server/services/face_service.py`，本地跑 **insightface buffalo_l**（ArcFace 识别 + det_10g 检测，onnxruntime CPU，懒加载 ~1.8s）。
- 隐私合规：**只存 512 维特征向量（base64 ~2KB），不存原图**；用户删账号时一并清脸。

## 2. 向量提取（ArcFace 512 维）

`face_service.py`：

- `_insightface()`：懒加载单例。
  ```python
  fa = FaceAnalysis(name='buffalo_l', root='server/models/face',
                    allowed_modules=['detection','recognition'],
                    providers=['CPUExecutionProvider'])
  fa.prepare(ctx_id=0, det_size=(640, 640))
  ```
- `_arcface_embedding(img)`：`fa.get(img)` 取 `g[0].embedding`，L2 归一化。检不到脸返回 None。
- `_extract_embedding(img)`：真脸走 ArcFace；检不到脸回退**统计特征**（灰度 8x8 分块 + Sobel 梯度 + 肤色占比 + 几何统计 → 512 维），保证接口不崩。
- **注意**：统计回退特征**不是真脸**，只能写进 `tizhi_records.photo_features`（趋势展示），**不能进 `face_vectors` 向量组**（会稀释组均值、让拒档变迟钝）。

## 3. 向量组学习（随用户变老仍能认出）

`face_vectors` 表，按 `(user_id, model_version)` 命名空间，一个用户可存多条历史向量：

- `add_user_vector`：累加（不覆盖）。与组内余弦 > `DEDUP_COSINE(0.98)` 视为同脸，只刷新最近一条；上限 `VECTOR_CAP(24)`，超出丢最老。
- 比对时对该用户**全部历史向量取均值**再算余弦 → 用户变老/换角度/换光线仍能认出。
- 换模型版本（`MODEL_VERSION`）= 新命名空间，旧向量自动作废。

**入库前置校验（堵死污染，2026-10-14 关键防护）**：
- 该用户**已有向量组**时，新脸向量必须同时满足：① ArcFace 检到真脸（`_arcface_embedding` 非 None）；② 与组均值余弦 ≥ `COSINE_THRESHOLD`。全过才入库，否则拒存（`rejected_not_self`）。
- 首次建档（组空）放行。
- 这是最后一道闸门：即使 vision 拒档漏了、前端 `/api/face/ensure`/`/api/face/save` 被乱调，别人的脸也进不了组。

## 4. 非本人照片拒档

`main.py /api/chat/vision` 体质存档前判定：

- `check_own(首图, user_id, 全库)` → `rejected = has_record 且 face_detected 且 非 matched`。
- **阈值铁律**：`COSINE_THRESHOLD = 0.42`（实测：本人参考 0.966、别人照片 0.397，0.35 太宽会被别人脸混过）。换模型/向量组变化后**必须重测两组余弦再定阈值**。
- 拒档行为：
  - 不写 `tizhi_records`（不污染健康档案）
  - 不把别人的脸向量塞进向量组（不污染识别）
  - 小麦大白话提示"这不是你本人的照片，请用本人真实照片重新拍"
  - `face_identity.rejected = true`，前端可读取
- 放行不误伤：首次建档（无组）放行；检不到脸（纯舌苔照）写真档案放行但向量拒存；本人照片（余弦≥阈值）放行存档。

**历史坑**：拒档曾反复失效，根因不是阈值，是**别人的脸向量被先存进组**（旧代码"先存后判"），组被污染后余弦被拉高（0.70），拒档永远显示"本人"，恶性循环。修法：`add_user_vector` 改"先判后存"。排查拒档失效时**先查组内向量两两余弦**（异类 <0.35 = 混了别人的脸），别一上来就调阈值。

## 5. 健康画像（多维时间线）

用户随时间变老，照片向量也在变。SOM 在个人中心出"健康画像"：

- **数据列**：`tizhi_records.photo_features`（该次拍照第一张图的 512 维视觉特征）+ `photo_hash`（短指纹，趋势去重展示）。仅拍照辨证（`source='vision_chat'`）填，文字辨证为 NULL。
- **接口**：`GET /api/health/portrait?user_id=&days=0&offset=0`
  - ① 辨证时间线（相邻两次有照片行算 `visual_delta` = 1-余弦，0≈几乎一样、越大越不同）
  - ② 人脸向量组规模/首末时间
  - ③ 体质分布
  - ④ 首末体质趋势（changed）
  - ⑤ 注册天数
  - **口径**：`days=0` = 全量（与体质记录卡片条数统一），不再只算近 90 天。
  - **分页**：`offset` 真翻页（上一页/下一页），每页 10 条。
- **前端**：`web/js/app.js` `loadHealthPortrait()` → `fetchPortraitPage()`，真翻页器（上一页/第X页共Y页/下一页）。
- **时区**：库内时间统一北京时间（UTC+8），前端直接用，不再双重换算。

## 6. 验证矩阵

- `python3 -c "import ast; ast.parse(open('services/face_service.py').read())"` 语法过
- 重启服务后日志出现 `[face_service] insightface buffalo_l loaded`（模型加载成功）
- **拒档**：别人脸照 → `face_identity.rejected=true`、`tizhi_records` 不新增、`face_vectors` 不新增
- **本人**：自己脸照 → `rejected=false`、`tizhi_records` 新增、`face_vectors` 新增
- **纯舌苔照（无脸）** → 写真档案放行、向量拒存
- **首次建档** → 写真档案放行、向量放行（第一条脸）
- 组内向量两两余弦应 >0.8（同人）；若出现 <0.35 的异类 = 混了别人的脸，需清洗

## 7. 与相邻模块分工

- 微信登录/账号统一/匿名合并 → 见 som-wechat-login-unify
- 体质记录 1:1 规则 → som-wechat-login-unify
- 商品搜索/购买跳转 → som-taobao-search-debug
