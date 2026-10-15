# -*- coding: utf-8 -*-
"""
服务端渲染分享图(2026-10-16 中华要求: 微信内辨证分享/商品分享都要能用)

背景: 前端 canvas 在微信 WebView 里画跨域图(淘宝/天猫图片)会污染 canvas,
toDataURL() 被浏览器安全策略拒绝 → 微信内点「分享图」无反应。
方案: 分享图改由服务端 Pillow 渲染, 前端只负责 POST 数据、回显 PNG,
长按保存/系统分享都正常, 彻底绕开 canvas 跨域。

两张图:
- 辨证图 /api/share/content-image : 绿色养生模板 + 文案 + som.top 小程序码
- 商品图 /api/share/product-image : 商品主图 + 标题/价格/店铺 + 淘宝链接二维码

中文字体: /usr/share/fonts/NotoSansSC-Regular.ttf (已确认存在)
"""
import io
import re
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

FONT_PATH = "/usr/share/fonts/NotoSansSC-Regular.ttf"
SITE = "https://som.top/"
W = 750  # 宽, 与前端模板一致


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def _fit_font(text: str, max_width: int, start: int, min_size: int,
              draw: ImageDraw.ImageDraw) -> int:
    """单行文本自适应字号: 从 start 往下找能放进 max_width 的最大字号"""
    size = start
    while size > min_size:
        f = _font(size)
        if draw.textlength(text, font=f) <= max_width:
            return size
        size -= 2
    return min_size


def _wrap(text: str, font, draw: ImageDraw.ImageDraw, max_width: int):
    """按像素宽度换行(中文逐字, 英文按词)"""
    lines = []
    for raw in text.split("\n"):
        raw = raw.strip()
        if not raw:
            lines.append("")
            continue
        line = ""
        for ch in raw:
            test = line + ch
            if draw.textlength(test, font=font) > max_width and line:
                lines.append(line)
                line = ch
            else:
                line = test
        lines.append(line)
    return [l for l in lines if l != ""]


def _qr_png(url: str, size: int = 150) -> Image.Image:
    """URL → 二维码 PNG (白底黑码), 失败返回 None"""
    try:
        qr = qrcode.QRCode(box_size=8, border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#000000", back_color="#ffffff").convert("RGB")
        return img.resize((size, size), Image.LANCZOS)
    except Exception:
        return None


def _load_remote_image(url: str, size: int = 420) -> Image.Image:
    """拉取商品主图并裁成正方形; 失败返回 None(前端不传图也能出卡)"""
    if not url or url in ("#", "about:blank"):
        return None
    if url.startswith("//"):
        url = "https:" + url
    try:
        r = requests.get(url, timeout=6,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; SOM-share/1.0)"})
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        # 裁正方形(居中)
        w, h = img.size
        side = min(w, h)
        img = img.crop(((w - side) // 2, (h - side) // 2,
                        (w - side) // 2 + side, (h - side) // 2 + side))
        return img.resize((size, size), Image.LANCZOS)
    except Exception:
        return None


def render_content_share_image(text: str, site_url: str = SITE) -> bytes:
    """辨证内容分享图: 绿底模板 + 换行文案 + som.top 二维码"""
    # 去掉 markdown 符号, 提升可读性
    text = re.sub(r"[#*`>]", "", text).strip()
    lines = [l for l in text.split("\n") if l.strip()]
    lines = [l.strip() for l in lines]
    if not lines:
        lines = ["养生参考"]
    if len(lines) > 30:
        lines = lines[:30]

    pad = 50
    fs = 28
    lh = 40
    f_title = _font(40)
    f_sub = _font(24)
    f_body = _font(fs)
    f_qr = _font(26)
    f_foot = _font(22)

    # 先用临时画布测宽
    tmp = Image.new("RGB", (W, 10))
    td = ImageDraw.Draw(tmp)
    wrapped = []
    for l in lines:
        wrapped.extend(_wrap(l, f_body, td, W - pad * 2))
    headerH, footerH = 130, 240
    bodyH = len(wrapped) * lh + 40
    H = headerH + bodyH + footerH

    img = Image.new("RGB", (W, H), "#f0f7f2")
    d = ImageDraw.Draw(img)
    grad_top, grad_bot = (240, 247, 242), (227, 240, 232)
    for y in range(H):
        t = y / max(H - 1, 1)
        d.line([(0, y), (W, y)], fill=tuple(int(grad_top[i] + (grad_bot[i] - grad_top[i]) * t) for i in range(3)))

    # 头部
    d.text((pad, 55), "🌾 小麦SOM · 养生辨证", font=f_title, fill=(58, 125, 92))
    d.text((pad, 100), "中医辨证 · 有机养生", font=f_sub, fill=(123, 168, 146))

    # 正文
    y = headerH + 30
    for l in wrapped:
        d.text((pad, y), l, font=f_body, fill=(45, 59, 51))
        y += lh

    # 底部: 二维码 + 文案
    d.text((W // 2, H - 195), "扫码体验 SOM 松麦 · 你的养生助手",
           font=f_qr, fill=(58, 125, 92), anchor="mm")
    qr = _qr_png(site_url, 140)
    if qr:
        img.paste(qr, (W // 2 - 70, H - 230))
    d.text((W // 2, H - 80), "som.top · 以上为养生文化参考，不构成医疗诊断",
           font=f_foot, fill=(155, 184, 168), anchor="mm")

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def render_product_share_image(title: str, price: str, shop: str,
                               image_url: str, buy_url: str,
                               site_url: str = SITE) -> bytes:
    """商品分享图: 商品图 + 标题/价格/店铺 + 淘宝购买链接二维码"""
    pad = 40
    f_title = _font(34)
    f_price = _font(30)
    f_shop = _font(22)
    f_qr = _font(24)
    f_foot = _font(20)

    headerH, footerH = 130, 260
    imgW = 420
    H = headerH + imgW + 150 + footerH

    img = Image.new("RGB", (W, H), "#f0f7f2")
    d = ImageDraw.Draw(img)
    grad_top, grad_bot = (240, 247, 242), (227, 240, 232)
    for y in range(H):
        t = y / max(H - 1, 1)
        d.line([(0, y), (W, y)], fill=tuple(int(grad_top[i] + (grad_bot[i] - grad_top[i]) * t) for i in range(3)))

    # 头部
    d.text((pad, 55), "🛍️ 小麦SOM · 有机好物", font=_font(40), fill=(58, 125, 92))
    d.text((pad, 100), "有机认证 · 淘宝同源", font=f_shop, fill=(123, 168, 146))

    # 商品图(左侧), 失败画占位
    pic = _load_remote_image(image_url, imgW)
    top = headerH
    if pic:
        img.paste(pic, (pad, top))
    else:
        d.rectangle([pad, top, pad + imgW, top + imgW], outline=(123, 168, 146), width=2, fill=(235, 243, 239))
        d.text((pad + imgW // 2, top + imgW // 2), "商品图", font=_font(28),
               fill=(123, 168, 146), anchor="mm")

    # 右侧: 标题(自动换行/缩字号) + 价格 + 店铺
    rx = pad + imgW + 30
    rw = W - rx - pad
    td = d  # 同画布
    shown_title = title or "未命名商品"
    tsize = 30
    while tsize > 18 and d.textlength(shown_title, font=_font(tsize)) > rw:
        tsize -= 2
    tf = _font(tsize)
    tw = _wrap(shown_title, tf, d, rw)[:3]
    ty = top + 20
    for l in tw:
        d.text((rx, ty), l, font=tf, fill=(45, 59, 51))
        ty += tsize + 8
    ty += 10
    if price:
        d.text((rx, ty), "¥ " + str(price), font=f_price, fill=(217, 83, 44))
        ty += 44
    if shop:
        d.text((rx, ty), shop[:24], font=f_shop, fill=(120, 120, 120))

    # 底部: 二维码 + 文案
    d.text((W // 2, top + imgW + 60), "淘宝扫码购买 / som.top 看更多",
           font=f_qr, fill=(58, 125, 92), anchor="mm")
    qr = _qr_png(buy_url or SITE, 150)
    if qr:
        img.paste(qr, (W // 2 - 75, top + imgW + 90))
    d.text((W // 2, H - 40), "som.top · 以上商品信息仅供参考",
           font=f_foot, fill=(155, 184, 168), anchor="mm")

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()
