"""2026-10-13 小蕊: 方案B 人脸特征向量服务(隐私合规骨架)

设计:
- 输入: base64 图片 -> 提取 512 维特征向量(OpenCV Facemark 不可用则降级用 DNN 人脸检测 + 简单特征)
- 存储: 只存向量(base64 压缩的 float32), 不存原图
- 比对: 余弦相似度, 阈值 0.55
- 用户可一键删除自己的向量

说明: 生产环境应换用 insightface/ArcFace 这类强模型(需要 1-3GB 模型文件 + onnxruntime)。
本骨架先用 OpenCV 内置的 DNN face detector + 灰度统计特征做可行性验证,
让接口先跑通, 后续替换为强模型只需改 _extract_embedding 一个函数。
"""
import base64, io, struct, numpy as np
import cv2

MODEL_VERSION = "v1-opencv-stats"  # 后续升级 insightface 时改成 "v2-arcface"
COSINE_THRESHOLD = 0.82  # 2026-10-13 调高: 同图=1.0, 不同图合成测试约0.72, 生产用 insightface 时再校准


def _decode_image(b64: str):
    try:
        raw = b64
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[1]
        # 修 base64 padding: 长度不是4的倍数会报 Incorrect padding, 补 pad
        if len(raw) % 4:
            raw += "=" * (4 - len(raw) % 4)
        arr = base64.b64decode(raw, validate=False)
        buf = np.frombuffer(arr, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def _extract_embedding(img) -> np.ndarray:
    """提取 512 维特征向量。
    当前骨架: 灰度分块均值 + 边缘 + 肤色占比 + 几何中心偏移, 拼到 512 维。
    生产替换: 用 insightface 的 ArcFace embedding(已是 512 维), 直接 replace 本函数体。
    """
    if img is None:
        return np.zeros(512, dtype=np.float32)
    # 人脸检测: 用 OpenCV 的 Haar 级联
    import os
    cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
    if not os.path.exists(cascade_path):
        # headless 版可能不带级联文件, 直接走全图统计(不报错)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        roi = gray
        x = 0
        y = 0
        w = gray.shape[1]
        h = gray.shape[0]
        _face_detected = False
    else:
        cascade = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        if len(faces) == 0:
            roi = gray
            x = 0
            y = 0
            w = gray.shape[1]
            h = gray.shape[0]
            _face_detected = False
        else:
            x, y, w, h = faces[0]
            roi = gray[y:y+h, x:x+w]
            _face_detected = True

    # 分 16x16 块均值 -> 256 维
    roi_small = cv2.resize(roi, (16, 16)).astype(np.float32) / 255.0
    block_feats = roi_small.flatten()  # 256

    # Sobel 边缘 12x12 -> 144 维
    sobel = cv2.Sobel(roi, cv2.CV_32F, 1, 1, ksize=3).astype(np.float32)
    sobel_small = cv2.resize(sobel, (12, 12)).flatten()  # 144
    sobel_small = sobel_small - sobel_small.mean()
    sobel_small = sobel_small / (np.std(sobel_small) + 1e-6)

    # 几何: 人脸框中心偏移 + 大小占比 + 肤色占比 + 灰度均值 + 对比度 -> 12 维
    H, W = gray.shape
    cx = (x + w/2) / W
    cy = (y + h/2) / H
    size_ratio = (w*h) / (H*W)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    skin = cv2.inRange(hsv, (0, 40, 80), (25, 220, 255))
    skin_ratio = np.count_nonzero(skin) / skin.size
    gray_mean = float(roi.mean()) / 255.0
    gray_std = float(roi.std()) / 255.0
    # 水平/垂直灰度梯度比(方向特征)
    grad_x = np.abs(cv2.Sobel(roi, cv2.CV_32F, 1, 0, ksize=3)).mean()
    grad_y = np.abs(cv2.Sobel(roi, cv2.CV_32F, 0, 1, ksize=3)).mean()
    geo_feats = np.array([cx, cy, size_ratio, skin_ratio, gray_mean, gray_std,
                          grad_x/255.0, grad_y/255.0,
                          grad_x/(grad_x+grad_y+1e-6), grad_y/(grad_x+grad_y+1e-6),
                          0.0, 0.0], dtype=np.float32)  # 12 维

    vec = np.concatenate([
        block_feats,   # 256
        sobel_small,   # 144
        geo_feats,     # 12
        np.zeros(512 - 256 - 144 - 12, dtype=np.float32)  # 100 维补零
    ])
    vec = vec.astype(np.float32)
    # L2 归一化
    n = np.linalg.norm(vec)
    if n > 1e-9:
        vec = vec / n
    return vec


def encode_embedding(vec: np.ndarray) -> bytes:
    """512 维 float32 -> base64 blob(~512*4 字节 ~ 2KB)"""
    return base64.b64encode(vec.tobytes())


def decode_embedding(blob: bytes) -> np.ndarray:
    arr = base64.b64decode(blob)
    vec = np.frombuffer(arr, dtype=np.float32)
    n = np.linalg.norm(vec)
    return vec / n if n > 1e-9 else vec


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def check_face(b64_image: str, stored_vectors: list) -> dict:
    """比对: 输入图片特征 vs 已存向量。
    stored_vectors: [(vector, user_id), ...]
    返回: {matched: bool, no_record: bool, best_user_id, best_score}
    """
    img = _decode_image(b64_image)
    if img is None:
        return {"matched": False, "no_record": len(stored_vectors) == 0, "error": "decode_failed"}
    emb = _extract_embedding(img)
    best = (0.0, None)
    for vec, uid in stored_vectors:
        s = cosine(emb, vec)
        if s > best[0]:
            best = (s, uid)
    matched = best[0] >= COSINE_THRESHOLD
    return {
        "matched": matched,
        "no_record": len(stored_vectors) == 0,
        "best_user_id": best[1],
        "best_score": round(best[0], 4),
    }


def save_embedding(user_id: str, b64_image: str) -> dict:
    """存当前用户的人脸向量(覆盖旧的)。"""
    from services.user_system import _conn
    img = _decode_image(b64_image)
    if img is None:
        return {"success": False, "error": "decode_failed"}
    emb = _extract_embedding(img)
    conn = _conn()
    conn.execute(
        "INSERT INTO face_vectors (user_id, embedding, model_version) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, model_version) DO UPDATE SET embedding=excluded.embedding",
        (user_id, encode_embedding(emb), MODEL_VERSION),
    )
    conn.commit()
    conn.close()
    return {"success": True, "model_version": MODEL_VERSION}


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
