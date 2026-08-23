#!/bin/bash
# qscl_engine.sh v2 — 纯POSIX多模态引擎
# gen <k>:        生成 W[k]原型像素+4态投票坍缩→JSON{class,avg,binary,art}
# argmax <64px>:  识别 64像素→argmax类序号(4态加权和)
# img <file>:     图片/PDF→8x8灰度→二值化→argmax
# img64 <64px>:   同argmax
# render <64px>:  64像素→8x8 ASCII字形
# json_page <slug>: 生成HTML页面(status|index|ide|404)
WS="/root/QSM/QLife/qdfs/ns/models"
DATA="/root/QSM/QLife/qdfs/ns/data"
OP="$1"; shift
case "$OP" in
    gen)
        K="$1"
        awk -v k="$K" -v WS="$WS" 'BEGIN{
          for(s=0;s<4;s++){
            fp=WS"/qscl_b0_s" s ".w"; i=0
            while((getline line < fp)>0){
              if(i>=k*64 && i<k*64+64) wr[(i-k*64)+ s*64]=int(line)+0
              if(i>k*64+63) break
              i++
            }
            close(fp)
          }
          for(j=0;j<64;j++){
            n1=(wr[j]>0?1:0)+(wr[j+64]>0?1:0)+(wr[j+128]>0?1:0)+(wr[j+192]>0?1:0)
            raw[j]=(n1>=3?1:0)
            avg[j]=wr[j]
          }
          printf "{\"class\":%d,\"avg\":[", k
          for(j=0;j<63;j++) printf "%d,", avg[j]; printf "%d]", avg[63]
          printf ",\"binary\":[", k
          for(j=0;j<63;j++) printf "%d,", raw[j]; printf "%d]", raw[63]
          printf ",\"art\":\""
          for(r=0;r<8;r++){if(r>0)printf "\\\n"; for(c=0;c<8;c++) printf "%s",(raw[r*8+c]?"█":" ")}
          printf "\"}"
        }'
        ;;
    argmax|img64)
        P="$*"
        awk -v p="$P" -v WS="$WS" 'BEGIN{
          n=split(p,_p,/[ ,\t]+/)
          for(j=0;j<64;j++) px[j]=int(_p[j+1])+0
          for(s=0;s<4;s++){
            fp=WS"/qscl_b0_s" s ".w"; i=0
            while((getline line < fp)>0){w[s*32960+i]=int(line)+0; i++}
            close(fp)
          }
          for(c=0;c<515;c++){
            sum=0
            for(s=0;s<4;s++){
              dot=0; off=s*32960+c*64
              for(j=0;j<64;j++) dot+=px[j]*w[off+j]
              sum+=dot
            }
            sum4[c]=sum
          }
          best=-999999999; bc=0
          for(c=0;c<515;c++){if(sum4[c]>best){best=sum4[c]; bc=c}}
          printf "{\"class\":%d,\"score\":%d,\"codepoint\":%d}", bc, best, 993040+bc*10
        }'
        ;;
    img)
        FILE="$1"
        [ ! -f "$FILE" ] && echo '{"error":"file not found"}' >&2 && exit 1
        # ffmpeg转8x8灰度raw(64字节),od转十进制,awk>127→1
        PXS=$(ffmpeg -v error -y -i "$FILE" -vf "scale=8:8:flags=neighbor,format=gray" -f rawvideo -pix_fmt gray - 2>/dev/null | od -An -tu1 | tr -s ' ' '\n' | awk 'NF>=1{print ($1>127?1:0)}' | paste -sd, | head -c 128)
        [ -z "$PXS" ] && echo '{"error":"image decode failed"}' >&2 && exit 1
        build/qscl_engine.sh argmax "$PXS"
        ;;
    render)
        P="$*"
        awk -v p="$P" 'BEGIN{
          n=split(p,_p,/[ ,\t]+/)
          printf "\""
          for(r=0;r<8;r++){if(r>0) printf "\\\n"; for(c=0;c<8;c++) printf "%s",(int(_p[r*8+c+1])?"█":" ")}
          printf "\""
        }'
        ;;
    json_page)
        SLUG="$1"
        case "$SLUG" in
            status)
                echo '{"server":"QEntL/6.0","status":"running","model":"qscl","votes":"4-state","weights":"qscl_b{0-7}_s{0-3}.w x32","dim":"515x64","endpoints":["/api/generate","/api/recognize","/api/image","/api/yi","/api/xiaoqu"],"symmetry":"generate=W[k]反向argmax","engine":"qscl_engine.sh"}'
                ;;
            index)
                cat <<'HTML'
<!DOCTYPE html><html><head><meta charset='utf-8'><title>QSM多模态统一生成</title>
<style>body{font-family:monospace;background:#111;color:#eee;padding:20px}textarea,pre{background:#000;color:#0f0;padding:8px;white-space:pre-wrap;width:70%}
.row{margin:14px 0;border:1px solid #444;padding:12px}h1,h2{color:#0af}input,button{padding:4px 8px;font-family:monospace}</style></head><body>
<h1>QSM量子操作系统 · 多模态统一生成</h1>
<p>QEntL v6 · 32权重 4态真并行 · 生成=识别对称反向 · W=515×64</p>
<div class='row'><h2>🧠 生成(类序号0-514→彝文)</h2>
<input id='gk' placeholder='0' size='5'><button onclick="fetch('/api/generate?k='+document.getElementById('gk').value).then(r=>r.json()).then(j=>document.getElementById('go').innerText=JSON.stringify(j,null,2))">生成</button><pre id='go'></pre></div>
<div class='row'><h2>👁 识别(64像素→类序号)</h2>
<textarea id='rp' rows='2' cols='72' placeholder='64个0/1,逗号或空格分隔'></textarea>
<button onclick="fetch('/api/recognize',{method:'POST',body:document.getElementById('rp').value}).then(r=>r.json()).then(j=>document.getElementById('ro').innerText=JSON.stringify(j,null,2))">识别</button><pre id='ro'></pre></div>
<div class='row'><h2>🖼 图传识别</h2>
<input type='file' id='f'><button onclick="var r=new FileReader();r.onload=function(){fetch('/api/image',{method:'POST',body:r.result.split(',')[1]}').then(x=>x.text()).then(t=>document.getElementById('io').innerText=t)};r.readAsDataURL(document.getElementById('f').files[0])">识别图片</button><pre id='io'></pre></div>
<div class='row'><h2>💬 小麦助手</h2>
<textarea id='qm' rows='3' cols='72'></textarea>
<button onclick="fetch('/api/xiaoqu',{method:'POST',body:document.getElementById('qm').value}).then(r=>r.text()).then(t=>{document.getElementById('qo').innerText=t;document.getElementById('qm').value=''})">问</button><pre id='qo'></pre></div>
<a href='/ide'>QEntL IDE</a> · <a href='/api/status'>Status</a>
</body></html>
HTML
                ;;
            ide)
                cat <<'HTML'
<!DOCTYPE html><html><head><meta charset='utf-8'><title>QEntL IDE</title>
<style>body{font-family:monospace;background:#111;color:#eee;padding:20px}textarea{width:80%;height:300px;background:#000;color:#0f0;padding:8px}</style></head><body>
<h1>QEntL IDE</h1>
<textarea id='i' placeholder='输入QEntL代码...'></textarea><br>
<button onclick="fetch('/api/xiaoqu',{method:'POST',body:document.getElementById('i').value}).then(r=>r.text()).then(t=>{document.getElementById('o').innerText=t;document.getElementById('i').value=''})">运行</button>
<pre id='o' style='white-space:pre-wrap;background:#000;padding:8px'></pre>
</body></html>
HTML
                ;;
            xiaoqu)
                REPLY="$2"
                echo "小趣QSM多模态统一生成就绪|生成:GET /api/generate?k=N|识别:POST /api/recognize body=64像素|图传:POST /api/image"
                [ -n "$REPLY" ] && echo "你说: $REPLY"
                ;;
            *) echo '404' ;;
        esac
        ;;
    *)
        echo '{"error":"unknown op"}' >&2; exit 1
        ;;
esac
exit 0
