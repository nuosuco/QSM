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
import os
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


_LOGO_CACHE = None
_LOGO_FAILED = False
_LOGO_LOGGED = False

def _resolve_logo_path():
    """2026-10-19 小蕊修: 原 os.path.dirname(os.path.dirname(__file__)) 在部分
    CWD/导入方式下解析到 services/assets/ 导致静默失败。多路兜底保证命中
    server/assets/。"""
    cands = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'wheat_logo_256.png'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'wheat_logo_256.png'),
        os.path.join(os.getcwd(), 'server', 'assets', 'wheat_logo_256.png'),
        os.path.join(os.getcwd(), 'assets', 'wheat_logo_256.png'),
        '/root/SOM/server/assets/wheat_logo_256.png',
    ]
    for p in cands:
        if os.path.exists(p):
            return p
    return None

def _wheat_logo(size: int = 96):
    """小麦帽子小图(中华要求: 分享图开头加形象图)。
    2026-10-17 修: 加 _LOGO_FAILED 只试一次。
    2026-10-19 小蕊修(中华反馈 logo 没显示): 原成功分支 _LOGO_CACHE = bg 那行
    因缩进错误实际没执行到, 且 try 块整段成了死代码, 函数永远返回初始 None
    → logo 没画进图。现在路径多路兜底 + 显式赋值返回 + 首次加载打日志。"""
    global _LOGO_CACHE, _LOGO_FAILED, _LOGO_LOGGED
    if _LOGO_CACHE is not None:
        return _LOGO_CACHE
    if _LOGO_FAILED:
        return None
    try:
        lp = _resolve_logo_path()
        if not lp:
            raise FileNotFoundError('wheat_logo_256.png 未找到(多路候选都缺失)')
        if not _LOGO_LOGGED:
            print('[share_image] logo 加载成功: ' + lp, flush=True)
            _LOGO_LOGGED = True
        src_img = Image.open(lp).convert('RGB')
        # 自动裁白边
        px = src_img.load(); w, h = src_img.size
        xs, ys = [], []
        for yy in range(0, h, 2):
            for xx in range(0, w, 2):
                r, g, b = px[xx, yy]
                if not (r > 245 and g > 245 and b > 245):
                    xs.append(xx); ys.append(yy)
        if xs:
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            core = src_img.crop((max(0, x0 - 4), max(0, y0 - 4), min(w, x1 + 4), min(h, y1 + 4)))
        else:
            core = src_img
        # 白底圆角方(柔和)
        side = int(size * 1.15)
        bg = Image.new('RGBA', (side, side), (255, 255, 255, 0))
        d = ImageDraw.Draw(bg)
        d.rounded_rectangle([0, 0, side - 1, side - 1], radius=side // 8, fill=(255, 255, 255, 255),
                            outline=_C_HEADER_SUB, width=2)
        core = core.resize((size, size), Image.LANCZOS)
        bg.paste(core, ((side - size) // 2, (side - size) // 2))
        _LOGO_CACHE = bg
        return _LOGO_CACHE
    except Exception as e:
        print('[share_image] logo 加载失败(分享图将不带帽子图): ' + repr(e), flush=True)
        _LOGO_FAILED = True
        return None


def _header(img: Image.Image, main: str, sub: str, with_logo: bool = True):
    """共享头 v3(中华要求 2026-10-16): 小麦帽子小图 + 标题居中, 更美观。
    返回正文区顶 y。品牌名不含 emoji(Noto Sans SC 无 emoji 字形)。"""
    d = ImageDraw.Draw(img)
    if with_logo:
        logo = _wheat_logo(96)
        if logo:
            img.paste(logo, (46, 34), logo)
        tx = 46 + 112 + 22
    else:
        tx = 50
    d.text((tx, 52), main, font=_font(40), fill=_C_HEADER_TITLE)
    d.text((tx, 100), sub, font=_font(24), fill=_C_HEADER_SUB)
    return 150


def _footer_dual(img: Image.Image, H: int, left_url: str, left_label: str,
                 right_url: str, right_label: str, qr_size: int = 150):
    """共享尾 v3(中华要求 2026-10-16): 双码并排 — 左淘宝商品码 + 右服务号码,
    说明文字写在码【上方】(不再压码), 底部一行 som.top 免责。返回画布底部余量。"""
    d = ImageDraw.Draw(img)
    gap = 70
    total_w = qr_size * 2 + gap
    x0 = (W - total_w) // 2
    label_y = H - 235
    # 左
    d.text((x0 + qr_size // 2, label_y), left_label, font=_font(24), fill=_C_HEADER_TITLE, anchor="mm")
    ql = _qr_png(left_url, qr_size)
    if ql:
        img.paste(ql, (x0, H - 215))
        d = ImageDraw.Draw(img)
        d.rectangle([x0 - 4, H - 219, x0 + qr_size + 4, H - 211 + qr_size],
                    outline=_C_HEADER_TITLE, width=2)
    # 右
    xr = x0 + qr_size + gap
    d.text((xr + qr_size // 2, label_y), right_label, font=_font(24), fill=_C_HEADER_TITLE, anchor="mm")
    qr = _qr_png(right_url, qr_size)
    if qr:
        img.paste(qr, (xr, H - 215))
        d = ImageDraw.Draw(img)
        d.rectangle([xr - 4, H - 219, xr + qr_size + 4, H - 211 + qr_size],
                    outline=_C_HEADER_TITLE, width=2)
    d.text((W // 2, H - 30), "som.top · 以上信息仅供参考，不构成医疗诊断",
           font=_font(20), fill=_C_LIGHT, anchor="mm")
    return H - 250


def _clean_text(text: str, max_lines: int = 30) -> list:
    # 忌口匹配: 行内「忌...」到标点/行尾(模块内共用, 2026-10-19 修 UnboundLocalError)
    TABB_RX = re.compile(r"忌[^,，、;；。.]*(?:[。.]|$)")

    """去掉 markdown 符号, 压缩空白行, 限量。
    2026-10-19 小蕊修(中华反馈食疗配方与做法没分成两段/末尾没排版分段):
    (a) 一行内多个【X】小标题 → 从第 2 个【起独立成行;
    (b) 单【小标题】里同时含「食疗」+「做法」(如【食疗配方与做法】)
        → 拆成 食疗段/做法段/忌口段;
    (c) 无【】文本, 同行出现「食疗」「做法」→ 在「做法」前拆行, 忌口独立。
    注意: 逐行处理, 正则里不出现换行转义(避免写文件时 \n 丢失)。
    2026-10-20 中华反馈「分享图夹杂代码」根治: 前端现在传 detail.innerHTML
    (mdToHtml 渲染出的 <div>/<li>/<table> 等标签), 老代码只剥 markdown 符号,
    HTML 标签被 Pillow 原样画进图 → 图里满屏代码。先剥 HTML 再剥 markdown。"""
    text = text or ""
    # 块级闭合标签 → 换行(保住段落结构)
    text = re.sub(r"<\s*/\s*(p|div|li|ul|ol|tr|table|section|article|blockquote|h[1-6])\s*>", "\n", text, flags=re.I)
    # <br> → 换行
    text = re.sub(r"<\s*(br|hr)\s*/?\s*>", "\n", text, flags=re.I)
    # 剩余所有 HTML 标签直接删
    text = re.sub(r"<[^>]*>", "", text)
    # HTML 实体 → 可见字符
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "'").replace("&#39;", "'").replace("&nbsp;", " ")
    text = re.sub(r"[#*`]", "", text).strip()
    out = []
    for raw in text.split("\n"):
        l = raw.strip()
        if not l:
            continue
        idxs = [m.start() for m in re.finditer(r"【[^】]{1,20}】", l)]
        if len(idxs) > 1:
            # (a) 行内多【X】: 第 1 段 = 行首到第 2 个【前; 之后每【起一段
            segs = []
            prev = 0
            for i, ix in enumerate(idxs):
                end = idxs[i + 1] if i + 1 < len(idxs) else len(l)
                segs.append(l[prev:end].strip())
                prev = end
            out.extend(s for s in segs if s)
            continue
        if len(idxs) == 1:
            tag_m = re.match(r"^【([^】]+)】", l)
            tag = tag_m.group(1)
            # (b) 单个【食疗...做法】合并小标题: 拆 食疗段 + 做法段 + 忌口段
            # 忌口匹配: 行尾「忌」到行尾, 只拦在标点后(避免误伤「忌」单字夹中间)
            if "食疗" in tag:
                t_shi = "【" + re.split(r"与|及|和|、", tag)[0] + "】"
                mtab_all = TABB_RX.search(l)
                taboo = mtab_all.group(0).rstrip("。.").strip() if mtab_all else ""
                body = (l[:mtab_all.start()].rstrip().rstrip("。.；; ") if mtab_all else l).strip()
                mz = re.search(r"做法", body)
                if mz:
                    shi_part = body[:mz.start()].rstrip().rstrip("。.；; ")
                    zuo_part = body[mz.start():].lstrip()
                else:
                    shi_part, zuo_part = body, ""
                if shi_part:
                    out.append(t_shi + shi_part if not shi_part.startswith(t_shi) else shi_part)
                if zuo_part:
                    out.append("【做法】" + zuo_part if not zuo_part.startswith("【做法】") else zuo_part)
                if taboo:
                    out.append("【忌口】" + taboo if not taboo.startswith("【忌口】") else taboo)
                continue
            out.append(l)
            continue
        # (c) 无【】文本, 食疗/配方/养生参考...做法 拆行(2026-10-19 中华反馈"配方：... 做法：..."同行要拆成两段)
        m_food = re.search(r"食疗|配方|养生参考", l)
        m_zuo = re.search(r"做法", l)
        if m_food and m_zuo and m_food.start() < m_zuo.start():
            head = l[:m_zuo.start()].rstrip().rstrip("。.；; ")
            tail = l[m_zuo.start():].lstrip()
            mtab = TABB_RX.search(tail)
            if mtab:
                body = tail[:mtab.start()].rstrip().rstrip("。.；; ")
                taboo = mtab.group(0).rstrip("。.").strip()
                if head:
                    out.append(head)
                if body:
                    out.append(body if body.startswith("做法") else "做法：" + body)
                if taboo:
                    out.append(taboo if taboo.startswith("忌") else "忌口：" + taboo)
            else:
                out.extend(x for x in [head, tail] if x)
            continue
        out.append(l)
    out = [l for l in out if l and l.strip()]
    return out[:max_lines]

def render_content_share_image(text: str, site_url: str = SITE) -> bytes:
    """辨证内容分享图 v3(中华要求 2026-10-16):
    开头小麦帽子形象图 + 标题; 文案正文; 底部 som.top 服务号二维码,
    说明文字写在码【上方】不再压码。"""
    lines = _clean_text(text)
    # 2026-10-19 小蕊修(中华反馈"末尾提示语不要包括"): 剔除末尾的 AI 声明段
    # 匹配「AI提示」「AI 提示」「以上为…不构成医疗诊断」「仅供参考」等尾部免责行
    _TAIL_RX = re.compile(r"^(?:AI\s*提示|AI\s*说明|免责声明)?[：:]?\s*(?:以上|以上内容).{0,40}(?:仅供参考|不构成医疗|医疗诊断)|^AI\s*提示")
    _new_lines = []
    for _l in lines:
        if _TAIL_RX.match(_l.strip()):
            continue
        _new_lines.append(_l)
    lines = _new_lines
    if not lines:
        lines = ["养生参考"]

    pad = 50
    fs = 28
    lh = 40
    f_body = _font(fs)
    headerH, footerH = 150, 270

    # 2026-10-19 小蕊修(中华反馈食疗配方与做法没分段/末尾没排版):
    # 原来所有行等距 40px 连着排, 食疗/做法/AI提示这些独立段视觉上挤成一片。
    # 现在: (1) 段落间留 26px 额外空隙(以【X】小标题或食疗/做法/养生参考/AI提示开头的行
    # 视为新段起点); (2) 【X】小标题用标题绿+加粗渲染, 正文用深绿灰, 层次分明。
    def _is_para_start(l):
        s = l.strip()
        if s.startswith('\u3010') or s.startswith('【'):
            return True
        for kw in ('食疗', '配方', '做法', '养生参考', 'AI提示', '忌口', '忌', '注意事项'):
            if s.startswith(kw):
                return True
        return False

    tmp = ImageDraw.Draw(Image.new("RGB", (W, 10)))
    wrapped = []          # 每元素 (line, is_para_start)
    for l in lines:
        first, rest = True, []
        rest = _wrap(l, f_body, tmp, W - pad * 2)
        if not rest:
            continue
        wrapped.append((rest[0], _is_para_start(rest[0])))
        for r in rest[1:]:
            wrapped.append((r, False))
    PARA_GAP = 26
    body_extra = sum(PARA_GAP for _, s in wrapped[1:] if s)
    bodyH = len(wrapped) * lh + 40 + body_extra
    H = headerH + bodyH + footerH

    img = _new_canvas(H)
    _header(img, "小麦SOM · 养生辨证", "中医辨证 · 有机养生", with_logo=True)

    d = ImageDraw.Draw(img)
    f_title = _font(fs + 2)
    y = headerH + 20
    prev_start = True  # 首行前不计空隙
    for i, (l, s) in enumerate(wrapped):
        if s and not prev_start:
            y += PARA_GAP
        if l.strip().startswith('【'):
            # 小标题行整行用标题色; 有正文部分则正文随本行同色更清晰, 但【】内字放大
            d.text((pad, y), l, font=f_title, fill=_C_HEADER_TITLE)
        else:
            d.text((pad, y), l, font=f_body, fill=_C_BODY)
        y += lh
        prev_start = s

    # 底部单码居中, 说明文字在码上方
    d = ImageDraw.Draw(img)
    qr_size = 150
    qcx = W // 2
    d.text((qcx, H - 235), "扫码进 SOM 松麦 · 你的养生助手",
           font=_font(24), fill=_C_HEADER_TITLE, anchor="mm")
    qr = _qr_png(site_url, qr_size)
    if qr:
        img.paste(qr, (qcx - qr_size // 2, H - 215))
        d = ImageDraw.Draw(img)
        d.rectangle([qcx - qr_size // 2 - 4, H - 219, qcx + qr_size // 2 + 4, H - 211 + qr_size],
                    outline=_C_HEADER_TITLE, width=2)
    d.text((W // 2, H - 30), "som.top · 以上为养生文化参考，不构成医疗诊断",
           font=_font(20), fill=_C_LIGHT, anchor="mm")

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
    # v3 版式(中华要求 2026-10-16): 商品名写在图片【开头】, 图片单列全宽竖排;
    # 末尾双码: 左=淘宝商品码, 右=松麦服务号码, 说明文字在码上方不压码
    cell = 600
    gridX = 50
    name_block_H = 220            # 商品名区(图片开头): 名称(最多2行) + 店铺名
    nameTop = 160                 # 名称区顶边(头部之下)
    imgTop = nameTop + name_block_H + 10
    gap = 14
    H = imgTop + n * (cell + gap) + 300     # 尾部 300 = 双码区

    img = _new_canvas(H)
    _header(img, "小麦SOM · 有机好物", "有机认证 · 淘宝同源", with_logo=True)

    d = ImageDraw.Draw(img)

    # 商品名(图片开头, 放大, 自动缩字号最多2行) + 店铺名
    name = (title or "未命名商品").strip()
    nameW = W - 100
    f_name = _font(36)
    while f_name.size > 22 and d.textlength(name, font=f_name) > nameW:
        f_name = _font(f_name.size - 2)
    y = nameTop
    for l in _wrap(name, f_name, d, nameW)[:2]:
        d.text((gridX, y), l, font=f_name, fill=_C_HEADER_TITLE)
        y += f_name.size + 10
    if shop:
        d.text((gridX, y + 4), shop[:24], font=_font(22), fill=(120, 120, 120))

    # 商品图单列全宽竖排
    for i, u in enumerate(pics):
        gy = imgTop + i * (cell + gap)
        pic = _load_remote_image(u, cell)
        if pic:
            img.paste(pic, (gridX, gy))
            d = ImageDraw.Draw(img)
            d.rectangle([gridX, gy, gridX + cell, gy + cell],
                        outline=_C_HEADER_SUB, width=1)
        else:
            d.rectangle([gridX, gy, gridX + cell, gy + cell],
                        outline=_C_HEADER_SUB, width=2, fill=_C_PLACEHOLDER)
            d.text((gridX + cell // 2, gy + cell // 2),
                   "暂无图片" if not u else "图片加载失败",
                   font=_font(20), fill=_C_HEADER_SUB, anchor="mm")

    # 末尾双码: 左淘宝商品码 + 右松麦服务号码(中华要求), 说明文字在码上方不压码
    _footer_dual(img, H,
                 left_url=(buy_url or "https://item.taobao.com/"),
                 left_label="淘宝扫码购买",
                 right_url=site_url,
                 right_label="松麦服务号 · 更多好物")

    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue()
