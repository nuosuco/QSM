# -*- coding: utf-8 -*-
"""2026-10-13 小蕊: 方案B 人脸特征向量服务(隐私合规骨架)

身份识别: 一人一户。A 拍了照 B 不能用, 否则健康数据全串。
2026-10-14 升级: 身份识别必须后端做(每次 /api/chat/vision 自动提脸/存向量/比对),
不依赖前端触发(微信 WebView 缓存不可靠)。

- 输入: base64 图片 -> 提取 512 维特征向量(ArcFace 真脸; 检不到脸回退统计特征)
- 存储: face_vectors 表, 按 (user_id, model_version) 唯一, 只存向量不存原图
- 2026-10-14 向量组学习(用户一辈子的健康大数据根基):
  每次辨证把该用户向量以组形式累加, 比对时对该用户所有历史向量取均值再算余弦。
  用户随时间上传的图片不断刷新该用户的"向量组", 模型随用户变老仍能认出。
  组内向量去重(余弦>0.98 视为同脸), 上限 VECTOR_CAP。
"""
import base64
import io
import time
from typing import Optional

import numpy as np

# 2026-10-14 向量组学习参数
VECTOR_CAP = 24        # 每个用户最多保留的历史向量数(防膨胀, 超出丢最老的)
DEDUP_COSINE = 0.98     # 新向量与组内已有向量余弦>0.98 视为同脸, 只更新最近一条不新增

# 当前使用的模型版本(换模型时同步升这个号, 旧向量自动作废, 见 load_all_vectors)
MODEL_VERSION = "v2-arcface"
COSINE_THRESHOLD = 0.35  # 2026-10-14 向量组学习: 同用户多向量取均值比对, 阈值放宽到 0.35
                          # (v1 统计模型阈值 0.82, 换模型必换阈值)

# 懒加载 insightface 单例
_face_analyzer = None
_face_analyzer_failed = False


def _insightface():
    """懒加载 insightface FaceAnalysis(buffalo_l, det+recognition, CPU)。"""
    global _face_analyzer, _face_analyzer_failed
    if _face_analyzer_failed:
        return None
    if _face_analyzer is not None:
        return _face_analyzer
    try:
        import os
        import insightface
        from insightface.app import FaceAnalysis
        root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "face")
        t0 = time.time()
        fa = FaceAnalysis(name="buffalo_l", root=root,
                          allowed_modules=["detection", "recognition"],
                          providers=["CPUExecutionProvider"])
        fa.prepare(ctx_id=0, det_size=(640, 640))
        _face_analyzer = fa
        print(f"[face_service] insightface buffalo_l loaded in {time.time()-t0:.1f}s")
        return _face_analyzer
    except Exception as e:
        _face_analyzer_failed = True
        print(f"[face_service] insightface 加载失败, 回退统计特征: {e}")
        return None


def _arcface_embedding(img) -> Optional[np.ndarray]:
    """用 ArcFace 提 512 维 L2 归一化 embedding; 检不到脸返回 None。"""
    fa = _insightface()
    if fa is None:
        return None
    try:
        g = fa.get(img)
        if not g:
            return None
        emb = np.asarray(g[0].embedding, dtype=np.float32)
        n = np.linalg.norm(emb)
        return emb / n if n > 0 else None
    except Exception:
        return None


def _decode_image(b64: str):
    """base64 -> BGR ndarray; 失败返回 None。"""
    try:
        import cv2
        s = b64
        if "," in s and s.lstrip().startswith("data:"):
            s = s.split(",", 1)[1]
        arr = np.frombuffer(base64.b64decode(s), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def _extract_embedding(img) -> np.ndarray:
    """提取 512 维特征向量: 真脸走 ArcFace, 检不到脸回退统计特征。
    返回已 L2 归一化的向量。
    """
    emb = _arcface_embedding(img)
    if emb is not None:
        return emb
    return _fallback_embedding(img)


def _fallback_embedding(img) -> np.ndarray:
    """统计特征回退: 灰度 8x8 分块均值 + Sobel 梯度 + 肤色占比 + 几何统计 -> 512 维。
    保证接口不崩(合成脸/低清脸 ArcFace 检不到时)。
    """
    import cv2
    f = np.zeros(512, dtype=np.float32)
    if img is None or img.size == 0:
        return f
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    h, w = g.shape
    f[0] = g.mean() / 255.0
    f[1] = g.std() / 255.0
    # 8x8 分块均值
    th, tw = max(1, h // 8), max(1, w // 8)
    for i in range(8):
        for j in range(8):
            block = g[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
            if block.size:
                f[2 + i * 8 + j] = block.mean() / 255.0
    # Sobel 梯度能量
    sx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    sy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    f[64] = np.abs(sx).mean() / 255.0
    f[65] = np.abs(sy).mean() / 255.0
    # 肤色占比(简单阈值)
    b, gg, r = img[:, :, 0].astype(np.float32), img[:, :, 1].astype(np.float32), img[:, :, 2].astype(np.float32)
    skin = ((r > 95) & (gg > 40) & (b > 20) & (r > gg) & (r - b > 15)).mean()
    f[66] = skin
    # 几何: 人脸框中心偏移 + 大小占比 + 肤色占比 + 灰度均值 + 对比度 -> 12 维
    return f


def encode_embedding(vec: np.ndarray) -> bytes:
    return base64.b64encode(vec.astype(np.float32).tobytes())


def decode_embedding(blob: bytes) -> np.ndarray:
    return np.frombuffer(base64.b64decode(blob), dtype=np.float32).copy()


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def check_face(b64_image: str, stored_vectors: list) -> dict:
    """比对输入图 vs 全量已存向量(向量组: 每 user 取均值), 返回 {matched, best_user_id, best_score, no_record}。
    2026-10-14: 该用户的"历史向量组"取均值后再比对, 用户变老/换角度也能认出。
    """
    img = _decode_image(b64_image)
    emb = _extract_embedding(img)
    if not stored_vectors:
        return {"matched": False, "no_record": True, "best_user_id": None, "best_score": 0.0}
    # 按 user_id 聚合向量组, 每组取均值
    groups = {}
    for v, uid in stored_vectors:
        groups.setdefault(uid, []).append(v)
    best_score, best_uid = 0.0, None
    for uid, vecs in groups.items():
        mean_vec = np.mean(np.stack(vecs, axis=0), axis=0)
        mean_vec /= (np.linalg.norm(mean_vec) + 1e-9)
        s = cosine(emb, mean_vec)
        if s > best_score:
            best_score, best_uid = s, uid
    matched = best_score >= COSINE_THRESHOLD
    return {
        "matched": matched,
        "no_record": False,
        "best_user_id": best_uid,
        "best_score": round(best_score, 4),
    }


def check_own(b64_image: str, user_id: str, stored_vectors: list) -> dict:
    """2026-10-14 中华铁律(一人一户, 杜绝别人照片混进健康档案大数据):
    比对照片 vs 该用户自己的向量组(均值)。
    返回 {has_record, face_detected, matched, score}:
    - has_record: 该用户已有向量组(无=首次建档, 放行)
    - face_detected: ArcFace 检到真脸(检不到=纯舌苔照/低清, 统计特征区分不了, 放行不误伤)
    - matched: 与本人向量组均值余弦 >= COSINE_THRESHOLD
    拒档判定(在 main.py vision 里做): has_record 且 face_detected 且 非 matched → 非本人, 拒档。
    """
    out = {"has_record": False, "face_detected": False, "matched": False, "score": 0.0}
    if not user_id:
        return out
    img = _decode_image(b64_image)
    if img is None:
        return out
    emb_arc = _arcface_embedding(img)
    out["face_detected"] = emb_arc is not None
    own = [v for v, uid in (stored_vectors or []) if uid == user_id]
    out["has_record"] = bool(own)
    if not own:
        return out
    emb = emb_arc if emb_arc is not None else _extract_embedding(img)
    mean_vec = np.mean(np.stack(own, axis=0), axis=0)
    mean_vec /= (np.linalg.norm(mean_vec) + 1e-9)
    out["score"] = round(cosine(emb, mean_vec), 4)
    out["matched"] = out["score"] >= COSINE_THRESHOLD
    return out


def add_user_vector(user_id: str, b64_image: str, _dedup: bool = True) -> dict:
    """2026-10-14 向量组学习: 把当前用户新拍图的人脸向量加入其历史向量组(累加, 不覆盖)。
    - 去重: 与组内已有向量余弦 > DEDUP_COSINE 视为同脸, 更新最近一条不新增
    - 上限: VECTOR_CAP, 超出丢最老的
    """
    from services.user_system import _conn
    img = _decode_image(b64_image)
    if img is None:
        return {"success": False, "error": "decode_failed"}
    emb = _extract_embedding(img)
    conn = _conn()
    # 读该用户已有向量组(当前模型版本)
    rows = conn.execute(
        "SELECT embedding FROM face_vectors WHERE user_id=? AND model_version=?",
        (user_id, MODEL_VERSION)
    ).fetchall()
    existing = [decode_embedding(bytes(r[0])) for r in rows]
    # 最近一条的 id(去重时更新它, 让它保持"最新的脸"状态)
    last_id = rows[0][0] if rows else None
    if _dedup:
        for old in existing:
            if cosine(emb, old) > DEDUP_COSINE:
                if last_id is not None:
                    conn.execute(
                        "UPDATE face_vectors SET embedding=?, updated_at=? WHERE id=?",
                        (encode_embedding(emb), _now(), last_id),
                    )
                else:
                    conn.execute(
                        "INSERT INTO face_vectors (user_id, embedding, model_version, updated_at) VALUES (?, ?, ?, ?)",
                        (user_id, encode_embedding(emb), MODEL_VERSION, _now()),
                    )
                conn.commit()
                conn.close()
                return {"success": True, "model_version": MODEL_VERSION, "dedup": True}
    # 新增
    conn.execute(
        "INSERT INTO face_vectors (user_id, embedding, model_version, updated_at) VALUES (?, ?, ?, ?)",
        (user_id, encode_embedding(emb), MODEL_VERSION, _now()),
    )
    # 超上限丢最老的
    cap_excess = conn.execute(
        "SELECT COUNT(*) FROM face_vectors WHERE user_id=? AND model_version=?",
        (user_id, MODEL_VERSION)
    ).fetchone()[0] - VECTOR_CAP
    if cap_excess > 0:
        conn.execute(
            "DELETE FROM face_vectors WHERE user_id=? AND model_version=? "
            "AND id NOT IN (SELECT id FROM face_vectors WHERE user_id=? AND model_version=? "
            "ORDER BY updated_at DESC, id DESC LIMIT ?)",
            (user_id, MODEL_VERSION, user_id, MODEL_VERSION, VECTOR_CAP),
        )
    conn.commit()
    conn.close()
    return {"success": True, "model_version": MODEL_VERSION}


def save_embedding(user_id: str, b64_image: str) -> dict:
    """存当前用户的人脸向量。
    2026-10-14 升级: 委托给 add_user_vector(向量组学习, 累加历史, 同脸去重)。
    旧版是 ON CONFLICT DO UPDATE 覆盖单向量, 现在保留用户一辈子的脸向量组。
    """
    return add_user_vector(user_id, b64_image)


def load_all_vectors() -> list:
    """全量向量(小站用户少, 直接全量拉内存比对; 量大再换 ANN 索引)"""
    from services.user_system import _conn
    conn = _conn()
    rows = conn.execute(
        "SELECT user_id, embedding FROM face_vectors WHERE model_version=?",
        (MODEL_VERSION,)
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append((decode_embedding(bytes(r[1])), r[0]))
    return out


def delete_user_face(user_id: str) -> int:
    from services.user_system import _conn
    conn = _conn()
    n = conn.execute("DELETE FROM face_vectors WHERE user_id=?", (user_id,)).rowcount
    conn.commit()
    conn.close()
    return n


def ensure_face_record(user_id: str, b64_image: str, remember: bool = True) -> dict:
    """2026-10-13 小蕊: 前端拍照后调用。remember=True 时存/覆盖该用户向量; False 不存(只比对)。
    2026-10-14: remember=True 走向量组学习(累加, 同脸去重), 不再覆盖单向量。
    """
    if remember:
        return add_user_vector(user_id, b64_image)
    return {"success": True, "skipped": True}


def _now() -> str:
    from datetime import datetime, timezone, timedelta
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")


def list_user_face(user_id: str) -> dict:
    """查某用户是否已存脸向量(前端"我"里显示/删除入口用)"""
    from services.user_system import _conn
    conn = _conn()
    row = conn.execute(
        "SELECT model_version, created_at, updated_at FROM face_vectors WHERE user_id=? AND model_version=? ORDER BY id DESC LIMIT 1",
        (user_id, MODEL_VERSION)
    ).fetchone()
    n = conn.execute(
        "SELECT COUNT(*) FROM face_vectors WHERE user_id=? AND model_version=?",
        (user_id, MODEL_VERSION)
    ).fetchone()[0]
    conn.close()
    if not row:
        return {"has_face": False, "vector_count": 0}
    return {"has_face": True, "model_version": row["model_version"],
            "created_at": str(row["created_at"]), "vector_count": n}


def match_user(b64_image: str, exclude_user_id: str = None) -> dict:
    """2026-10-13 小蕊: 找出"这张脸是谁"。
    exclude_user_id: 若传了且匹配到的就是本人, 返回 matched_self=True。
    返回 {matched, matched_self, best_user_id, best_score}
    """
    vectors = load_all_vectors()
    result = check_face(b64_image, vectors)
    matched_self = False
    if result.get("best_user_id") == exclude_user_id:
        matched_self = True
    result["matched_self"] = matched_self
    return result
