#!/bin/bash
# SOM 公众号每日贴图稿(草稿) - 每天早上 08:00;周六让路给周更文章稿
set -euo pipefail
cd /root/SOM/server
# 抓当日百度热搜第一条能结合食疗的热点配图 → /tmp/som_hot_today.jpg
python3 - <<'HOTPY'
import requests, json
try:
    r = requests.get("https://top.baidu.com/api/board?platform=pc&tab=realtime",
                     headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json()
    best, best_score = None, 0
    for card in r.get('data', {}).get('cards', []):
        for x in card.get('content', []):
            w = x.get('word','')
            if not x.get('img'):
                continue
            score = 0
            for k in ['食','粮','菜','肉','奶','糖','血糖','长寿','养生','流感','食品','有机','体质','湿','脾','饮食','饭','粥','茶','药','医']:
                if k in w: score += 2
            for k in ['健康','心','血压','脂肪','运动','节食','瘦']:
                if k in w: score += 1
            try:
                hs = int(x.get('hotScore',0) or 0)
            except (TypeError, ValueError):
                hs = 0
            score += min(2, hs//5000000)  # 热度越高小幅加权
            if score > best_score:
                best, best_score = x, score
    if best:
        img = requests.get(best['img'], headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        open('/tmp/som_hot_today.jpg','wb').write(img.content)
        json.dump({'word': best['word'], 'score': best_score, 'img': best['img']},
                  open('/tmp/som_hot_meta.json','w'), ensure_ascii=False, indent=2)
        print(f"HOT OK: {best['word']} (score={best_score})")
    else:
        print("HOT: none matched, fallback to 节气养生 (skill 兜底)")
except Exception as e:
    print("HOT FAIL:", e)
HOTPYjson, os
try:
    r = requests.get("https://top.baidu.com/api/board?platform=pc&tab=realtime",
                     headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json()
    picked = None
    for card in r.get('data', {}).get('cards', []):
        for x in card.get('content', []):
            w = x.get('word','')
            kw_hit = any(k in w for k in ['食','粮','菜','肉','奶','糖','血糖','长寿','健康','养生','流感','食品','有机','药','医','体质','湿','脾'])
            if kw_hit and x.get('img'):
                picked = x
                break
        if picked:
            break
    if picked:
        img = requests.get(picked['img'], headers={"User-Agent":"Mozilla/5.0"}, timeout=15).content
        open('/tmp/som_hot_today.jpg','wb').write(img)
        json.dump({'word': picked['word'], 'img': picked['img']}, open('/tmp/som_hot_meta.json','w'), ensure_ascii=False, indent=2)
        print('HOT:', picked['word'])
    else:
        print('HOT: none matched, fallback to existing som_hot_today.jpg if any')
except Exception as e:
    print('HOT FAIL:', e)
HOTPY

if [ "$(date +%u)" -eq 6 ]; then
    echo "$(date '+%F %T') SATURDAY: skip daily pic, weekly article will run" >> /root/SOM/content/logs/cron.log
    exit 0
fi
python3 - <<'PYEOF'
import sys, json, requests, sqlite3, os, re
sys.path.insert(0, '/root/SOM/server')
from services.shop import ShopService
from services.share_image import render_content_share_image, render_product_share_image
shop = ShopService()
con = sqlite3.connect('/root/SOM/server/data/user_data.db'); con.row_factory = sqlite3.Row
advice = con.execute("SELECT advice FROM tizhi_records ORDER BY created_at DESC LIMIT 1").fetchone()['advice']
clean = re.sub(r'^\s*[-|#]+\s*$', '', advice, flags=re.M)
png = render_content_share_image(clean, 'https://som.top/')
open('/tmp/som_bianzheng_share.jpg', 'wb').write(png)
print('辨证分享图 OK', os.path.getsize('/tmp/som_bianzheng_share.jpg')//1024, 'KB')
out = []
for kw in ['黄芪', '当归', '西洋参']:
    items = shop.search_from_cache(kw, 1, 5, '')
    if not items:
        try:
            r = requests.get('http://127.0.0.1:8000/api/products/search',
                              params={'keyword': kw, 'platform': 'taobao', 'page': 1, 'page_size': 5},
                              timeout=30)
            items = r.json().get('items', [])
        except Exception:
            items = []
    if items:
        it = items[0]
        png = render_product_share_image(
            title=it.get('title', '')[:35], price=str(it.get('price', '')),
            shop=it.get('shop_name') or '', images=it.get('image') or it.get('images') or [],
            buy_url=it.get('click_url') or '')
        p = f"/tmp/som_jun_{kw}.jpg"
        open(p, 'wb').write(png)
        out.append({'food': kw, 'title': it.get('title', '')[:30], 'price': it.get('price', ''), 'img': p})
    else:
        out.append({'food': kw, 'img': None})
json.dump(out, open('/tmp/som_jun_imgs.json', 'w'), ensure_ascii=False, indent=2)
for o in out:
    print(o['food'], o.get('img') or 'MISSING')
PYEOF
python3 - <<'PYEOF'
import sys, json, requests, os
sys.path.insert(0, '/root/SOM/server')
cfg = json.load(open('/root/SOM/server/auth_config.json'))
tok = requests.post('https://api.weixin.qq.com/cgi-bin/token',
    params={'grant_type': 'client_credential', 'appid': cfg['wechat']['appid'], 'secret': cfg['wechat']['secret']},
    timeout=10).json()['access_token']
def upm(path, fname):
    with open(path, 'rb') as f:
        r = requests.post('https://api.weixin.qq.com/cgi-bin/material/add_material',
                          params={'access_token': tok, 'type': 'image'},
                          files={'media': (fname, f, 'image/jpeg')}, timeout=60).json()
        mid = r.get('media_id')
        if not mid:
            print('PERM FAIL:', fname, r.get('errmsg'))
            sys.exit(1)
        return mid
hot = upm('/tmp/som_hot_today.jpg', 'hot_today.jpg')
bz = upm('/tmp/som_bianzheng_share.jpg', 'bianzheng.jpg')
jun = json.load(open('/tmp/som_jun_imgs.json'))
j1 = upm(jun[0]['img'], f"jun_{jun[0]['food']}.jpg") if jun[0].get('img') else None
j2 = upm(jun[1]['img'], f"jun_{jun[1]['food']}.jpg") if jun[1].get('img') else None
j3 = upm(jun[2]['img'], f"jun_{jun[2]['food']}.jpg") if jun[2].get('img') else None
pics = f"""
<p>📌 <b>今日热点配图</b>（首图）</p>
<p>📋 第2张：辨证食养报告分享图</p>
<p>🛒 第3-5张：三方案主君有机好物——{jun[0]['food']} / {jun[1]['food']} / {jun[2]['food']}</p>
<hr>
<p><b>扫码关注松麦生态，领你的专属食疗方案</b></p>
<p>🌐 https://som.top</p>
"""
d = {"articles": [{
    "title": "松麦生态·今日辨证食养报告+三主君有机好物",
    "content": pics,
    "digest": "辨证食养报告+三主君有机好物（黄芪/当归/西洋参）配今日热点",
    "content_source_url": "https://som.top",
    "author": "小麦SOM",
    "thumb_media_id": hot,
    "need_open_comment": 0
}]}
rr = requests.post('https://api.weixin.qq.com/cgi-bin/draft/add',
                   params={'access_token': tok}, json=d, timeout=60).json()
mid = rr.get('media_id')
print('PIC_DRAFT:', mid or rr.get('errmsg'), rr.get('errcode'))
json.dump({'pic_draft': mid, 'mids': {'hot': hot, 'bz': bz, 'j1': j1, 'j2': j2, 'j3': j3}},
          open('/tmp/som_daily_result.json', 'w'), ensure_ascii=False, indent=2)
PYEOF
echo "$(date '+%F %T') daily pic draft done" >> /root/SOM/content/logs/cron.log
