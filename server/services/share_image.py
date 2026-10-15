# -*- coding: utf-8 -*-
"""
服务端渲染分享图(2026-10-16 中华要求: 微信内辨证分享/商品分享都要能用)

背景: 前端 canvas 在微信 WebView 里画跨域图(淘宝/天猫图片)会污染 canvas,
toDataURL() 被浏览器安全策略拒绝 → 微信内点「分享图」无反应。
方案: 分享图改由服务端 Pillow 渲染, 前端只负责 POST 数据、回显 PNG,
长按保存/系统分享都正常, 彻底绕开 canvas 跨域。

模板与前端原版一致(750 宽, 绿底 #f0f7f2→#e3f0e8, 顶部「小麦SOM」,
底部 som.top 说明), 区别:
- 辨证图: 文案区 + 小程序码
- 商品图(2026-10-16 中华要求 v2): 头尾与辨证图完全一致(顶部标题+底部
  松麦服务号二维码), 正文换成商品全部图片(最多4张, 2x2 网格) + 商品名
  + 淘宝购买链接二维码, 不放价格(价格易变, 商品名+二维码够用)
- 顶部品牌名不含 emoji(Noto Sans SC 无 emoji 字形, 避免方框), 小程序码
  固定放底部正中央(中华确认)

中文字体: /usr/share/fonts/NotoSansSC-Regular.ttf (已确认存在)
"""
import io
import re
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/NotoSansSC-Regular.ttf"
SITE = "https://som.top/"
W = 750

# 与前端模板一致的颜色
_C_HEADER_TITLE = (58, 125, 92)   # #3a7d5c
_C_HEADER_SUB = (123, 168, 146)   # #7ba892
_C_BODY = (45, 59, 51)            # #2d3b33
_C_LIGHT = (155, 184, 168)        # #9bb8a8
_C_PLACEHOLDER = (235, 243, 239)  # 图片占位底色


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def _new_canvas(H: int) -> Image.Image:
    """绿底渐变画布(与前端模板一致: #f0f7f2 → #e3f0e8)"""
    img = Image.new("RGB", (W, H), "#f0f7f2")
    d = ImageDraw.Draw(img)
    grad_top, grad_bot = (240, 247, 242), (227, 240, 232)
    for y in range(H):
        t = y / max(H - 1, 1)
        d.line([(0, y), (W, y)],
               fill=tuple(int(grad_top[i] + (grad_bot[i] - grad_top[i]) * t) for i in range(3)))
    return img


def _qr_png(url: str, size: int = 150) -> Image.Image:
    """URL → 二维码 PNG (白底黑码), 失败返回 None"""
    try:
        qr = qrcode.QRCode(box_size=8, border=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#000000", back_color="#ffffff").convert("RGB")
        return img.resize((size, size), Image.LANCZOS)
    except Exception:
        return None


def _load_remote_image(url: str, size: int) -> Image.Image:
    """拉取商品图并裁成正方形; 失败返回 None"""
    if not url or url in ("#", "about:blank"):
        return None
    if url.startswith("//"):
        url = "https:" + url
    try:
        r = requests.get(url, timeout=6,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; SOM-share/1.0)"})
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        w, h = img.size
        side = min(w, h)
        img = img.crop(((w - side) // 2, (h - side) // 2,
                        (w - side) // 2 + side, (h - side) // 2 + side))
        return img.resize((size, size), Image.LANCZOS)
    except Exception:
        return None


def _wrap(text: str, font, draw: ImageDraw.ImageDraw, max_width: int) -> list:
    """按像素宽度换行(中文逐字, 英文按词)"""
    lines = []
    for raw in text.split("\n"):
        raw = raw.strip()
        if not raw:
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


def _header(img: Image.Image, main: str, sub: str):
    """共享头: 与辨证图同一模板(中华要求: 商品图头尾与内容分享一样)。
    品牌名不含 emoji(Noto Sans SC 无 emoji 字形, 避免方框)。"""
    d = ImageDraw.Draw(img)
    pad = 50
    d.text((pad, 55), main, font=_font(40), fill=_C_HEADER_TITLE)
    d.text((pad, 100), sub, font=_font(24), fill=_C_HEADER_SUB)


def _footer(img: Image.Image, H: int, qr_url: str, qr_label: str):
    """共享尾: 小程序码固定底部正中央(中华确认: 底部保留松麦服务号二维码)。
    返回二维码中心 x, 供商品图把淘宝码放到左侧不重叠。"""
    d = ImageDraw.Draw(img)
    d.text((W // 2, H - 195), qr_label, font=_font(26), fill=_C_HEADER_TITLE, anchor="mm")
    qr = _qr_png(qr_url, 130)
    qr_cx = W // 2
    if qr:
        img.paste(qr, (qr_cx - 65, H - 175))
    return qr_cx


def _clean_text(text: str, max_lines: int = 30) -> list:
    """去掉 markdown 符号, 压缩空白行, 限量"""
    text = re.sub(r"[#*`>]", "", text or "").strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[:max_lines]


def render_content_share_image(text: str, site_url: str = SITE) -> bytes:
    """辨证内容分享图: 头尾模板 + 换行文案 + som.top 小程序码"""
    lines = _clean_text(text)
    if not lines:
        lines = ["养生参考"]

    pad = 50
    fs = 28
    lh = 40
    f_body = _font(fs)
    headerH, footerH = 130, 240

    tmp = ImageDraw.Draw(Image.new("RGB", (W, 10)))
    wrapped = []
    for l in lines:
        wrapped.extend(_wrap(l, f_body, tmp, W - pad * 2))
    bodyH = len(wrapped) * lh + 40
    H = headerH + bodyH + footerH

    img = _new_canvas(H)
    _header(img, "小麦SOM · 养生辨证", "中医辨证 · 有机养生")

    d = ImageDraw.Draw(img)
    y = headerH + 30
    for l in wrapped:
        d.text((pad, y), l, font=f_body, fill=_C_BODY)
        y += lh

    _footer(img, H, site_url, "扫码体验 SOM 松麦 · 你的养生助手")
    d = ImageDraw.Draw(img)
    d.text((W // 2, H - 55), "som.top · 以上为养生文化参考，不构成医疗诊断",
           font=_font(22), fill=_C_LIGHT, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def _normalize_images(images, limit: int = 4) -> list:
    """images 入参归一: None/str/list → 去重去空, 限 limit 张"""
    if images is None:
        images = []
    elif isinstance(images, str):
        images = [images]
    seen, out = set(), []
    for u in images:
        u = (u or "").strip()
        if not u or u in ("#", "about:blank") or u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) == limit:
            break
    return out


def render_product_share_image(title: str, price: str, shop: str,
                               images, buy_url: str,
                               site_url: str = SITE) -> bytes:
    """商品分享图 v2(2026-10-16 中华要求):
    - 头尾与辨证图同一模板(顶部标题 + 底部 som.top 服务号二维码)
    - 正文: 商品全部图片(最多4张, 2x2 网格, 缺图占位)
    - 商品名(左侧, 自动换行最多3行) + 淘宝购买链接二维码(商品图区左上角)
    - 不放价格(价格易变, 商品名+二维码够用)
    price 参数保留签名兼容, 不渲染。
    """
    pics = _normalize_images(images)
    if not pics:
        pics = [""]

    n = len(pics)
    gridW = 260 if n > 1 else 300          # 2 列 / 单列网格总宽
    cell = (gridW - 12) // 2 if n > 1 else gridW
    gridX = 50                               # 网格左边距
    imgTop = 150                              # 图片区顶边(与标题对齐)

    nameX = gridX + gridW + 30               # 商品名区 x
    nameW = W - 50 - nameX                    # 商品名区宽(右留 50)
    if nameW < 120:
        nameX, nameW = 50, W - 100            # 网格放不下时商品名放上方单行

    H = max(imgTop + n * (cell + 12) + 140, imgTop + 400)

    img = _new_canvas(H)
    _header(img, "小麦SOM · 有机好物", "有机认证 · 淘宝同源")

    d = ImageDraw.Draw(img)

    # 商品图网格
    for i, u in enumerate(pics):
        col = i % 2
        row = i // 2
        gx = gridX + col * (cell + 12)
        gy = imgTop + row * (cell + 12)
        pic = _load_remote_image(u, cell)
        if pic:
            img.paste(pic, (gx, gy))
            d = ImageDraw.Draw(img)
            d.rectangle([gx, gy, gx + cell, gy + cell],
                        outline=_C_HEADER_SUB, width=1)
        else:
            d.rectangle([gx, gy, gx + cell, gy + cell],
                        outline=_C_HEADER_SUB, width=2, fill=_C_PLACEHOLDER)
            d.text((gx + cell // 2, gy + cell // 2),
                   "暂无图片" if not u else "图片加载失败",
                   font=_font(20), fill=_C_HEADER_SUB, anchor="mm")

    # 商品名(网格右侧, 自动缩字号 + 最多3行)
    name = (title or "未命名商品").strip()
    f_name = _font(30)
    while f_name.size > 18 and d.textlength(name, font=f_name) > nameW:
        f_name = _font(f_name.size - 2)
    y = imgTop + 4
    for l in _wrap(name, f_name, d, nameW)[:3]:
        d.text((nameX, y), l, font=f_name, fill=_C_BODY)
        y += f_name.size + 10
    if shop:
        d.text((nameX, min(y + 4, imgTop + 220)), (shop or "")[:16],
               font=_font(20), fill=(120, 120, 120))

    # 淘宝购买链接二维码(商品图区左上角, 白底绿框), 与底部 som.top 码区分
    tb_url = buy_url or "https://item.taobao.com/"
    qr = _qr_png(tb_url, 120)
    tx, ty = 50, imgTop + 4
    if qr:
        img.paste(qr, (tx, ty))
        d = ImageDraw.Draw(img)
        d.rectangle([tx - 4, ty - 4, tx + 124, ty + 124],
                    outline=_C_HEADER_TITLE, width=2)
    d.text((tx + 60, ty - 10), "淘宝扫码购买", font=_font(20),
           fill=_C_HEADER_TITLE, anchor="mm")

    # 共享尾: som.top 服务号二维码(底部正中央, 中华确认保留)
    _footer(img, H, site_url, "扫 松麦服务号 · 看更多养生好物")
    d = ImageDraw.Draw(img)
    d.text((W // 2, H - 55), "som.top · 以上商品信息仅供参考",
           font=_font(22), fill=_C_LIGHT, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()
