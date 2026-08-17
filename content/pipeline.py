#!/usr/bin/env python3.11
"""
SOM 松麦 - 每日内容自动化流水线 v3
每天 06:00 cron 触发，自动生成：
  - 1篇公众号图文（800-1200字）
  - 1篇小红书种草（300字+标签）
  - 1条横屏视频（1-3分钟，含配音+字幕+配图）
"""

import json, os, sys, time, asyncio, subprocess, re, traceback, requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# === 路径 ===
BASE = Path("/root/SOM/content")
FONTS = BASE / "fonts"
LOGS = BASE / "logs"
ARTICLES = BASE / "articles"
IMAGES = BASE / "images"
VIDEOS = BASE / "videos"
AUDIO = BASE / "audio"

# 时区
TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ).strftime("%Y%m%d")
DATE_CN = datetime.now(TZ).strftime("%Y年%m月%d日")

# === 日志 ===
def log(msg):
    ts = datetime.now(TZ).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    (LOGS / f"{TODAY}.log").open("a", encoding="utf-8").write(line + "\n")

# === LLM 配置 ===
def get_provider(name):
    cfg = json.load(open("/root/SOM/server/llm_providers.json"))
    for p in cfg["providers"]:
        if p["name"] == name:
            return p
    return None

def call_llm(model_key, system_prompt, user_prompt, temperature=0.7, max_tokens=2000, timeout=90):
    """调用 Agnes 或 SenseNova 生成内容"""
    # 优先用 Agnes（实测更快更稳定），降级到 SenseNova
    for name in ["agnes", "sensenova"]:
        prov = get_provider(name)
        if not prov or not prov.get("enabled", True):
            continue
        
        api_key = prov.get("api_key", prov.get("api_keys", ""))
        base_url = prov["base_url"]
        model_id = prov["models"].get(model_key, prov["models"]["chat"])
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            log(f"调用 {name}/{model_id}...")
            resp = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                msg = resp.json()["choices"][0]["message"]
                content = msg.get("content", "")
                if content:
                    return content.strip()
                # SenseNova 可能把内容放在 reasoning 里
                reasoning = msg.get("reasoning", "")
                if reasoning:
                    log(f"{name} 从 reasoning 取内容")
                    return reasoning.strip()
                log(f"{name} 返回空 content")
            else:
                log(f"{name} {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            log(f"{name} 异常: {type(e).__name__}: {str(e)[:80]}")
        
        log(f"降级到下一 provider...")
        time.sleep(1)
    
    return None

def call_image_gen(prompt, size="1024x1024"):
    """调用图片生成模型（Agnes）"""
    prov = get_provider("agnes")
    model_id = prov["models"].get("image_gen", "agnes-image-2.1-flash")
    api_key = prov.get("api_key", prov.get("api_keys", ""))
    base_url = prov["base_url"]
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_id,
        "prompt": prompt,
        "n": 1,
        "size": size,
    }
    
    try:
        log(f"生成图片: {prompt[:40]}...")
        resp = requests.post(f"{base_url}/images/generations", json=payload, headers=headers, timeout=120)
        if resp.status_code == 200:
            return resp.json().get("data", [{}])[0].get("url")
        else:
            log(f"图片生成失败: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        log(f"图片生成异常: {e}")
    return None

def download_image(url, save_path):
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            # 下载后 resize 到 1920x1080
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(resp.content))
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            if img.width < 1920 or img.height < 1080:
                canvas = Image.new('RGB', (1920, 1080), (0, 0, 0))
                canvas.paste(img, ((1920 - img.width) // 2, (1080 - img.height) // 2))
                img = canvas
            img.save(save_path, 'JPEG', quality=90)
            log(f"图片已下载+Resize: {save_path.name} ({img.width}x{img.height})")
            return str(save_path)
    except Exception as e:
        log(f"图片下载异常: {e}")
    return None

# ============================================================
# 1. 热点采集 + 选题
# ============================================================
def get_current_solar_term():
    """从 jieqi 服务获取当前节气 + 下一个节气信息"""
    try:
        sys.path.insert(0, "/root/SOM/server")
        from services.jieqi import get_current_jieqi
        result = get_current_jieqi(datetime.now(TZ))
        cur = result["current"]
        nxt = result["next"]
        return {
            "name": cur["name"],
            "season": cur["season"],
            "desc": cur["desc"],
            "yangsheng": cur["yangsheng"],
            "foods": cur["foods"],
            "next_name": nxt["name"],
            "next_day": nxt["day"],
            "next_month": nxt["month"],
        }
    except Exception as e:
        log(f"节气获取失败: {e}")
        return {"name": "当季", "season": "夏", "desc": "", "yangsheng": "", "foods": [], "next_name": "", "next_day": 0, "next_month": 0}

def fetch_trends():
    """采集全网热点（微博热搜 + 百度热搜 + 头条热榜），返回热点标题列表"""
    trends = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # 1. 微博热搜
    try:
        resp = requests.get("https://weibo.com/ajax/side/hotSearch", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", {}).get("realtime", [])
            for item in data[:20]:
                word = item.get("word", "").strip()
                if word:
                    trends.append(f"[微博] {word}")
            log(f"微博热搜: {len(data[:20])} 条")
    except Exception as e:
        log(f"微博热搜获取失败: {type(e).__name__}")
    
    # 2. 百度热搜
    try:
        resp = requests.get("https://top.baidu.com/board?tab=realtime", headers=headers, timeout=10)
        if resp.status_code == 200:
            # 从 HTML 提取热搜标题
            titles = re.findall(r'"word":"([^"]+)"', resp.text)
            for t in titles[:20]:
                trends.append(f"[百度] {t}")
            log(f"百度热搜: {len(titles[:20])} 条")
    except Exception as e:
        log(f"百度热搜获取失败: {type(e).__name__}")
    
    # 3. 知乎热榜
    try:
        resp = requests.get("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20",
                           headers={**headers, "Accept": "application/json"}, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for item in data[:15]:
                title = item.get("target", {}).get("title", "").strip()
                if title:
                    trends.append(f"[知乎] {title}")
            log(f"知乎热榜: {len(data[:15])} 条")
    except Exception as e:
        log(f"知乎热榜获取失败: {type(e).__name__}")
    
    # 4. 头条热榜（备用）
    try:
        resp = requests.get("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
                           headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for item in data[:15]:
                title = item.get("Title", "").strip()
                if title:
                    trends.append(f"[头条] {title}")
            log(f"头条热榜: {len(data[:15])} 条")
    except Exception as e:
        log(f"头条热榜获取失败: {type(e).__name__}")
    
    # 去重
    seen = set()
    unique = []
    for t in trends:
        key = re.sub(r'^\[.*?\]\s*', '', t)
        if key not in seen:
            seen.add(key)
            unique.append(t)
    
    log(f"热点总计: {len(unique)} 条（去重后）")
    return unique

def generate_topic():
    """
    基于全网热点（不用节气），推理明天可能爆火的养生选题
    
    流程：热点分析 → 推理明天爆点 → 深度结合养生体质 → 产出选题
    
    注意：
    - 选题必须从热点出发，不用节气/时令作为主要切入点
    - 标题必须蹭到热点，让人以为是看新闻，不经意间学到养生
    """
    trends = fetch_trends()
    
    system_prompt = """你是松麦养生的内容策划专家，擅长蹭热点做养生科普。

你的任务：
1. 分析当前全网热点，推理出【明天最可能全网爆火】的1-2个话题方向
2. 找到热点与中医养生的结合点（体质/症状/食疗/穴位）
3. 生成一个既有热点流量、又有养生干货的选题

【重要规则】
- 选题必须从热点出发，不能用节气/时令作为主要切入点
- 标题必须蹭到热点，让人以为是看新闻，不经意间学到养生
- 内容必须深度结合：热点事件→健康风险→体质分析→具体症状→食疗方法
- 不能硬蹭，结合点要自然、有逻辑
- 输出纯JSON，不要markdown代码块

输出JSON格式：
{
  "title_cn": "中文标题（带热点钩子，蹭到流量）",
  "title_en": "英文标题",
  "description": "选题说明（30字以内）",
  "hot_trend_source": "蹭的哪个热点（如：微博热搜xxx）",
  "trend_reasoning": "为什么判断这个明天会火（50字以内）",
  "key_points": ["知识点1", "知识点2", "知识点3"],
  "target_condition": "针对的病痛/症状",
  "recommended_foods": ["食材1", "食材2", "食材3"]
}"""
    
    trends_text = "\n".join(trends[:40]) if trends else "（热点获取失败，请基于当前健康话题选题）"
    
    user_prompt = f"""【当前全网热点（实时采集）】
{trends_text}

请分析以上热点，按以下步骤思考（不要输出思考过程，只输出JSON）：
1. 哪些热点话题明天可能持续发酵或爆发？
2. 哪个热点最能自然嫁接养生内容？
3. 生成1个标题+养生内容

记住：
- 选题必须从热点出发，不用节气/时令作为主要切入点
- 标题必须蹭到热点，让人以为是看新闻，不经意间学到养生
- 输出纯JSON"""
    
    result = call_llm("chat", system_prompt, user_prompt, temperature=0.8, max_tokens=2000)
    
    if result:
        result = result.strip()
        if result.startswith("```"):
            result = re.sub(r'^```(?:json)?\s*', '', result)
            result = re.sub(r'\s*```$', '', result)
        # 提取第一个完整 JSON 对象（防止 LLM 输出截断或附带多余文字）
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            try:
                topic = json.loads(json_match.group())
                log(f"选题: {topic.get('title_cn', '?')}")
                log(f"热点来源: {topic.get('hot_trend_source', '未知')}")
                log(f"爆火推理: {topic.get('trend_reasoning', '无')}")
                return topic
            except json.JSONDecodeError:
                # 尝试修复截断的 JSON（补全缺失的括号）
                raw = json_match.group()
                for suffix in ['}', '"}', '"}]}', '"}]}"}']:
                    try:
                        topic = json.loads(raw + suffix)
                        log(f"JSON截断修复成功 (补 {suffix})")
                        log(f"选题: {topic.get('title_cn', '?')}")
                        return topic
                    except:
                        continue
                log(f"JSON解析失败，用默认选题: {result[:120]}")
        else:
            log(f"未找到JSON，用默认选题: {result[:120]}")
    
    # 兜底：大暑节气选题（不是立秋！）
    return {
        "title_cn": "大暑天湿气最重！这3件事千万别做，伤脾胃毁阳气",
        "title_en": "Great Heat: 3 Things That Damage Your Spleen and Yang",
        "description": "大暑节气祛湿养阳指南",
        "hot_trend_source": "节气当季（热点获取失败兜底）",
        "trend_reasoning": "大暑湿热交蒸，祛湿话题自带流量",
        "key_points": ["湿气重的5个信号", "大暑最伤脾胃的3件事", "祛湿食疗方"],
        "target_condition": "湿气重/脾胃虚弱",
        "recommended_foods": ["薏米", "赤小豆", "茯苓", "陈皮"],
    }

# ============================================================
# 2. 写文案
# ============================================================
def generate_article(topic):
    """生成公众号文章和小红书文案"""
    # 公众号长文
    sys_prompt = """你是松麦养生的中医科普作者。写专业易懂的养生科普文章。
要求：
- 800-1200字
- 开头要有钩子，中间有干货
- 结尾自然引导："不确定自己是什么体质？扫码问小麦，AI帮你辨证出方案"
- 最后列出推荐食材清单
- 只输出文章正文"""
    
    user_prompt = f"""标题：{topic['title_cn']}
针对问题：{topic['target_condition']}
核心知识点：{'、'.join(topic['key_points'])}
推荐食材：{'、'.join(topic['recommended_foods'])}}}"""
    
    article = call_llm("chat", sys_prompt, user_prompt, temperature=0.7, max_tokens=3000, timeout=120)
    article = article or f"# {topic['title_cn']}\n\n内容生成中..."
    
    # 小红书
    xhs_prompt = f"""写一篇小红书种草文案（300字以内），口语化，加emoji，结尾加标签。
标题：{topic['title_cn']}
推荐食材：{'、'.join(topic['recommended_foods'])}}}"""
    
    xhs = call_llm("chat", sys_prompt, xhs_prompt, temperature=0.8, max_tokens=1000, timeout=60)
    xhs = xhs or f"今天来聊聊{topic['title_cn']}...#养生 #中医食疗"
    
    return {"article": article, "xhs": xhs}

# ============================================================
# 3. 生成配图
# ============================================================
def generate_images(topic):
    """生成文章配图和视频封面"""
    today_dir = IMAGES / TODAY
    today_dir.mkdir(parents=True, exist_ok=True)
    images = {}
    
    # 封面图 — 1080p（避免4K速率限制）
    url = call_image_gen(f"传统中医养生风格，{topic['title_cn']}，自然食材，高清摄影，温暖色调", "1920x1080")
    if url:
        path = download_image(url, today_dir / "cover.jpg")
        if path: images["cover"] = path
    
    # 小红书配图（8张）— 1080p
    foods = topic.get("recommended_foods", [])
    for i in range(8):  # 生成8张配图
        if i < len(foods):
            prompt = f"高品质有机{foods[i]}摄影，自然光，木桌背景，极简，细节清晰"
        else:
            prompt = f"中医养生食材摄影，自然光，木桌背景，高清"
        url = call_image_gen(prompt, "1920x1080")
        if url:
            path = download_image(url, today_dir / f"xhs_{i}.jpg")
            if path: images[f"xhs_{i}"] = path
    
    # 视频封面 — 1080p
    url = call_image_gen(f"养生食疗视频封面，{topic['title_cn']}，温暖色调，文字留白，高清", "1920x1080")
    if url:
        path = download_image(url, today_dir / "video_cover.jpg")
        if path: images["video_cover"] = path
    
    return images

# ============================================================
# 4. 视频脚本
# ============================================================
def generate_video_script(topic):
    """生成视频脚本（6个镜头）"""
    system_prompt = """你是养生短视频编剧。输出纯JSON，不要markdown：
{"scenes": [
  {"scene": 1, "duration_sec": 15, "narration": "旁白台词", "visual": "画面描述"},
  {"scene": 2, "duration_sec": 15, "narration": "旁白台词", "visual": "画面描述"}
]}
要求：
- 6个镜头，总时长1-2分钟
- 旁白口语化，适合TTS朗读
- 结尾引导关注"""
    
    user_prompt = f"""标题：{topic['title_cn']}
针对：{topic['target_condition']}
知识点：{'、'.join(topic['key_points'])}
推荐食材：{'、'.join(topic['recommended_foods'])}}}"""
    
    result = call_llm("chat", system_prompt, user_prompt, temperature=0.7, max_tokens=2000, timeout=60)
    
    if result:
        result = result.strip()
        if result.startswith("```"):
            result = re.sub(r'^```(?:json)?\s*', '', result)
            result = re.sub(r'\s*```$', '', result)
        try:
            parsed = json.loads(result)
            if "scenes" in parsed and len(parsed["scenes"]) > 0:
                return parsed
        except:
            log(f"脚本JSON解析失败")
    
    # 默认脚本（中英双语）
    return {
        "scenes": [
            {"scene": 1, "duration_sec": 25, "narration": f"你是不是经常觉得身体沉重、没精神？这可能不是累，是湿气在作怪。中医讲'湿气重，百病生'，尤其在换季的时候，湿气最容易入侵。", "narration_en": "Do you often feel heavy and tired? This might not be fatigue, but dampness. TCM says 'dampness causes a hundred diseases', especially during seasonal changes.", "visual": "展示湿气重的人日常状态"},
            {"scene": 2, "duration_sec": 25, "narration": topic['key_points'][0] if len(topic['key_points']) > 0 else "湿气重的5个信号", "narration_en": "5 Signs of Dampness"},
            {"scene": 3, "duration_sec": 25, "narration": topic['key_points'][1] if len(topic['key_points']) > 1 else "夏天最伤脾胃的3件事", "narration_en": "3 Things That Damage Spleen in Summer"},
            {"scene": 4, "duration_sec": 25, "narration": topic['key_points'][2] if len(topic['key_points']) > 2 else "祛湿食疗方", "narration_en": "Dampness-Removing Food Therapy"},
            {"scene": 5, "duration_sec": 25, "narration": f"推荐大家试试{topic['recommended_foods'][0] if len(topic['recommended_foods']) > 0 else '薏米'}，搭配{topic['recommended_foods'][1] if len(topic['recommended_foods']) > 1 else '赤小豆'}，祛湿效果特别好。", "narration_en": f"We recommend trying {topic['recommended_foods'][0] if len(topic['recommended_foods']) > 0 else 'Coix Seed'}, paired with {topic['recommended_foods'][1] if len(topic['recommended_foods']) > 1 else 'Red Bean'}, for excellent dampness-removing effects.", "visual": f"展示食材"},
            {"scene": 6, "duration_sec": 25, "narration": "不确定自己什么体质？点链接让AI帮你看，3分钟出食疗方案。关注我，每天学点养生小常识。", "narration_en": "Not sure about your body type? Click the link for AI analysis, get personalized diet plan in 3 minutes. Follow us for daily wellness tips.", "visual": "引导关注"},
        ]
    }

# ============================================================
# 5. TTS 配音
# ============================================================
async def _tts_async(text, output_path, voice="zh-CN-XiaoxiaoNeural"):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def run_tts(text, output_path):
    try:
        asyncio.run(_tts_async(text, output_path))
        return True
    except Exception as e:
        log(f"TTS 失败: {e}")
        return False

# ============================================================
# 6. 视频合成
# ============================================================
def compose_video(scenes, topic, images_map, output_path):
    """视频合成：先拼音频 → 再合成视频 → 加字幕"""
    if not scenes:
        log("没有镜头，跳过视频合成")
        return None
    
    video_dir = VIDEOS / TODAY
    audio_dir = AUDIO / TODAY
    video_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    today_img_dir = IMAGES / TODAY
    
    # 字体路径
    font_path = "/root/SOM/content/fonts/NotoSansSC-Regular.ttf"
    
    # 1. 生成所有 TTS 音频
    tts_files = []
    for i, scene in enumerate(scenes):
        tts_path = audio_dir / f"scene_{i:03d}.mp3"
        narration = scene.get("narration", "")
        if narration.strip() and not tts_path.exists():
            if run_tts(narration, str(tts_path)):
                tts_files.append(str(tts_path))
            else:
                log(f"TTS scene {i} 失败")
        elif tts_path.exists():
            tts_files.append(str(tts_path))
    
    if not tts_files:
        log("没有 TTS 文件，无法合成视频")
        return None
    
    log(f"TTS: {len(tts_files)}/{len(scenes)} 段")
    
    # 2. 拼接所有音频
    concat_audio = audio_dir / "all.mp3"
    concat_list = audio_dir / "concat.txt"
    with open(concat_list, "w") as f:
        for tf in tts_files:
            f.write(f"file '{tf}'\n")
    
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(concat_audio)],
                   capture_output=True, timeout=30)
    
    if not concat_audio.exists():
        log("音频拼接失败")
        return None
    
    # 获取音频时长
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(concat_audio)],
                       capture_output=True, text=True)
    audio_duration = float(r.stdout.strip()) if r.stdout.strip() else 60
    log(f"音频总时长: {audio_duration:.1f}秒")
    
    # 3. 找背景图（使用多张图片轮换）
    bg_imgs = []
    if (today_img_dir / "cover.jpg").exists():
        bg_imgs.append(str(today_img_dir / "cover.jpg"))
    if (today_img_dir / "video_cover.jpg").exists():
        bg_imgs.append(str(today_img_dir / "video_cover.jpg"))
    for i in range(3):
        img = today_img_dir / f"xhs_{i}.jpg"
        if img.exists():
            bg_imgs.append(str(img))
    
    # 去重
    bg_imgs = list(dict.fromkeys(bg_imgs))
    
    if not bg_imgs:
        bg_imgs = [str(today_img_dir / "cover.jpg")] if (today_img_dir / "cover.jpg").exists() else None
    
    # 4. 生成字幕 SRT（中英双语）
    srt_file = video_dir / "subtitles.srt"
    srt_lines = []
    cur = 0
    for i, scene in enumerate(scenes):
        if i >= len(tts_files):
            break
        dur = scene.get("duration_sec", 15) * 1000
        narration_cn = scene.get("narration", "")
        narration_en = scene.get("narration_en", "")  # 英文翻译
        
        srt_lines.append(str(i + 1))
        srt_lines.append(f"{cur//3600000:02d}:{(cur%3600000)//60000:02d}:{(cur%60000)//1000:02d},{cur%1000:03d} --> "
                        f"{(cur+dur)//3600000:02d}:{((cur+dur)%3600000)//60000:02d}:{((cur+dur)%60000)//1000:02d},{(cur+dur)%1000:03d}")
        srt_lines.append(narration_cn)
        if narration_en:
            srt_lines.append(narration_en)
        srt_lines.append("")
        cur += dur
    srt_file.write_text("\n".join(srt_lines), encoding="utf-8")
    
    # 5. 合成视频（图片+音频）
    temp_video = video_dir / "temp.mp4"
    
    if bg_imgs and len(bg_imgs) > 0:
        # 构建图片列表文件，实现多张图片轮换（循环到音频时长）
        img_list_file = video_dir / "images.txt"
        # 计算需要多少张图片才能填满音频时长
        imgs_per_cycle = len(bg_imgs)
        duration_per_img = 5  # 每张图5秒
        total_img_duration = imgs_per_cycle * duration_per_img
        # 需要循环几次
        cycles_needed = max(1, int(audio_duration / total_img_duration) + 1)
        with open(img_list_file, "w") as f:
            for cycle in range(cycles_needed):
                for img in bg_imgs:
                    f.write(f"file '{img}'\n")
                    f.write(f"duration {duration_per_img}\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(img_list_file),
            "-i", str(concat_audio),
            "-c:v", "mpeg4", "-q:v", "3",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-shortest",
            "-movflags", "+faststart",
            str(temp_video),
        ]
    elif bg_imgs and len(bg_imgs) == 1:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", bg_imgs[0],
            "-i", str(concat_audio),
            "-c:v", "mpeg4", "-q:v", "3",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-shortest",
            "-movflags", "+faststart",
            str(temp_video),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x2d5016:s=1920x1080:d={int(audio_duration)+1}",
            "-i", str(concat_audio),
            "-c:v", "mpeg4", "-q:v", "3",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-movflags", "+faststart",
            str(temp_video),
        ]
    
    log("合成视频中...")
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    if r.returncode != 0:
        log(f"视频合成失败: {r.stderr.decode()[-200:]}")
        return None
    if not temp_video.exists():
        log("视频产物不存在")
        return None
    
    # 6. 生成标题帧（前5秒显示大标题）
    title_output = str(video_dir / "title_temp.mp4")
    if topic.get('title_cn'):
        title_frame = str(video_dir / "title_frame.jpg")
        # 生成标题背景图（纯背景+大标题文字）
        title_bg = str(video_dir / "title_bg.png")
        if not os.path.exists(title_bg):
            # 创建黑色背景图用于标题显示
            cmd_title_bg = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1920x1080:d=5",
                "-vf", f"drawtext=fontfile={font_path}:text='{topic['title_cn']}':fontsize=100:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.7:boxborderw=10",
                "-frames:v", "1", title_frame
            ]
            subprocess.run(cmd_title_bg, capture_output=True, timeout=30)
        
        # 创建标题视频片段（5秒）- 使用更稳定的方式
        cmd_title = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:d=5:r=1",
            "-c:v", "mpeg4", "-q:v", "5",
            "-shortest", title_output
        ]
        subprocess.run(cmd_title, capture_output=True, timeout=30)
    
    # 7. 加字幕（使用drawtext更可靠）
    final_output = str(output_path)
    
    if not os.path.exists(font_path):
        log("字体不存在，跳过字幕")
        os.rename(str(temp_video), final_output)
        return final_output
    
    # 逐段添加字幕（中英双语+标题）
    segments = []
    cur = 0
    
    # 先添加标题帧（前5秒显示大标题）
    title_text = topic.get('title_cn', '')
    if title_text:
        # 标题单独一行，fontsize=90，居中，前5秒显示
        segments.append((0, 5000, title_text, ''))
    
    for i, scene in enumerate(scenes):
        if i >= len(tts_files):
            break
        dur = scene.get("duration_sec", 15) * 1000
        narration_cn = scene.get("narration", "")
        narration_en = scene.get("narration_en", "")
        if narration_cn.strip():
            segments.append((cur, dur, narration_cn, narration_en))
        cur += dur
    
    if segments:
        # 构建drawtext滤镜链（中英双语）- 正确链式语法
        filter_parts = []
        labels = []
        for idx, (start, dur, text_cn, text_en) in enumerate(segments):
            # 中文drawtext（大字，底部，fontsize=70）
            if text_cn:
                escaped_cn = text_cn.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'")
                # 标题用居中位置（y=(h-text_h)/2），字幕用底部（y=h-200）
                if idx == 0 and dur == 5000:
                    y_pos = "(h-text_h)/2"  # 标题居中
                    fontsize = "100"  # 标题更大
                else:
                    y_pos = "h-200"  # 字幕底部
                    fontsize = "70"
                label_cn = f'cn_{idx}'
                filter_parts.append(f"drawtext=text={escaped_cn}:fontfile={font_path}:fontsize={fontsize}:fontcolor=white:x=(w-text_w)/2:y={y_pos}:box=1:boxcolor=black@0.7:boxborderw=5[{label_cn}]")
                labels.append(label_cn)
            # 英文drawtext（中字号，中文上方，fontsize=48）
            if text_en:
                escaped_en = text_en.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'")
                label_en = f'en_{idx}'
                filter_parts.append(f"drawtext=text={escaped_en}:fontfile={font_path}:fontsize=48:fontcolor=white@0.9:x=(w-text_w)/2:y=h-280:box=1:boxcolor=black@0.3:boxborderw=3[{label_en}]")
                labels.append(label_en)
        
        # 用 [v] 作为输入，[vout] 作为输出，链式连接所有字幕
        filter_chain = '[v]'
        for label in labels:
            filter_chain += f'[{label}]'
        filter_chain += '[vout]'
        
        filter_complex = ";".join(filter_parts) + filter_chain
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(temp_video),
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-c:v", "mpeg4", "-q:v", "3",
            "-c:a", "copy",
            "-movflags", "+faststart",
            final_output,
        ]
    else:
        # 没有字幕，直接复制
        os.rename(str(temp_video), final_output)
    
    if os.path.exists(final_output):
        size = os.path.getsize(final_output) / (1024 * 1024)
        log(f"✅ 视频完成: {final_output} ({size:.1f}MB, {audio_duration:.0f}秒)")
        return final_output
    
    return None

# ============================================================
# 7. 保存文章
# ============================================================

# ============================================================
# 6. 上传YouTube
# ============================================================
def upload_to_youtube(video_path, topic):
    """上传视频到YouTube"""
    try:
        from services.youtube_service import upload_video
        
        title = topic['title_cn']
        description = topic.get('description', '')
        keywords = topic.get('recommended_foods', []) + ['养生', '中医', '体质', '食疗']
        
        log(f"上传YouTube: {title}")
        result = upload_video(
            video_path=video_path,
            title=title,
            description=description,
            keywords=keywords,
            privacy_status='public'
        )
        
        if result.get('success'):
            log(f"✅ YouTube上传成功: {result.get('video_url')}")
            return result
        else:
            log(f"❌ YouTube上传失败: {result.get('error')}")
            # 上传失败时删除本地视频，避免堆积
            if os.path.exists(video_path):
                os.remove(video_path)
                log(f"🗑️ 已删除失败的本地视频: {video_path}")
            return None
    except Exception as e:
        log(f"❌ YouTube上传异常: {e}")
        # 上传异常时也删除本地视频
        if os.path.exists(video_path):
            os.remove(video_path)
            log(f"🗑️ 已删除异常的本地视频: {video_path}")
        return None


def save_article(topic, article_data, images):
    today_dir = ARTICLES / TODAY
    today_dir.mkdir(parents=True, exist_ok=True)
    
    article = article_data.get("article", "")
    cover_path = images.get("cover", "")
    
    article_md = f"""---
title: {topic['title_cn']}
date: {DATE_CN}
cover: {cover_path}
tags: {topic['target_condition']}
---

{article}

---
> 本文由松麦养生AI生成 · 仅供参考，不构成医疗诊断
"""
    (today_dir / "wechat_article.md").write_text(article_md, encoding="utf-8")
    (today_dir / "xiaohongshu.txt").write_text(article_data.get("xhs", ""), encoding="utf-8")
    
    topic_info = {**topic, "generated_at": datetime.now(TZ).isoformat()}
    (today_dir / "topic.json").write_text(json.dumps(topic_info, ensure_ascii=False, indent=2), encoding="utf-8")
    
    log(f"文章已保存: {today_dir}")
    return today_dir

# ============================================================
# 主流程
# ============================================================
def main():
    log("=" * 50)
    log(f"📅 松麦每日内容流水线 - {DATE_CN}")
    log("=" * 50)
    
    # 1. 选题
    log("\n--- 1. 选题 ---")
    topic = generate_topic()
    log(f"选题: {topic['title_cn']}")
    log(f"针对: {topic['target_condition']}")
    
    # 2. 写文案
    log("\n--- 2. 写文案 ---")
    article_data = generate_article(topic)
    log(f"文章: {len(article_data.get('article', ''))} 字")
    log(f"小红书: {len(article_data.get('xhs', ''))} 字")
    
    # 3. 生成配图
    log("\n--- 3. 生成配图 ---")
    images = generate_images(topic)
    log(f"配图: {len(images)} 张")
    
    # 4. 保存文章
    log("\n--- 4. 保存文章 ---")
    article_dir = save_article(topic, article_data, images)
    
    # 5. 生产视频
    log("\n--- 5. 生产视频 ---")
    script = generate_video_script(topic)
    scenes = script.get("scenes", [])
    log(f"视频脚本: {len(scenes)} 个镜头")
    
    video_path = compose_video(scenes, topic, images, str(VIDEOS / TODAY / "final.mp4"))
    
    # 6. 上传YouTube
    if video_path:
        youtube_result = upload_to_youtube(video_path, topic)
    else:
        youtube_result = None
    
    # 7. 输出摘要
    log("\n" + "=" * 50)
    log("📋 今日产出摘要")
    log("=" * 50)
    log(f"✅ 文章: {article_dir}")
    if video_path:
        log(f"✅ 视频: {video_path}")
    else:
        log("❌ 视频: 生成失败")
    log("=" * 50)
    log("⚠️ 自动发布需中华提供：")
    log("   1. 公众号 AppID + AppSecret")
    log("   2. Google Cloud 项目（YouTube API）")
    log("=" * 50)
    
    # 写入发布日志
    publish_log = {
        "date": TODAY,
        "topic": topic,
        "article": str(article_dir),
        "video": video_path,
        "images": list(images.keys()),
        "status": "generated",
        "published": {"wechat": False, "youtube": youtube_result is not None},
    }
    (LOGS / f"{TODAY}_publish.json").write_text(json.dumps(publish_log, ensure_ascii=False, indent=2), encoding="utf-8")
    
    return {
        "topic": topic,
        "article": article_data,
        "images": images,
        "video": video_path,
    }

if __name__ == "__main__":
    main()