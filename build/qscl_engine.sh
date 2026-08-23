#!/bin/bash
# qscl_engine.sh v4 — QSCL不同起点叠加态并行多模态统一引擎
# 核心洞察: 生成=识别的对称反向, 共用W, 共用4态
#   识别:  像素 -> [32态=8批×4态 W[k]×像素 内积] -> 全局argmax -> 类序号k
#   生成:  类k -> W[k](该批4态直接读出) -> 4态投票(>=3) -> 64像素原型
#   推理:  类k -> W[k] + 4态坍缩 -> 8x8字形
# 权重: qscl_real_weights/qscl_real_b{0..7}_s{0..3}.w 每文件515类×64像素浮点(归一化原型+4扰动起点)
WS="/root/QSM/QLife/qdfs/ns/models"
CPMAP="$WS/class_codepoint.txt"
B=8; S=4; CB=515
OP="$1"; shift

mkcp(){
  awk 'NR>1{print $3}' "$CPMAP" > /tmp/qscl_cpm.txt 2>/dev/null || true
}

case "$OP" in
  argmax|img64)
    mkcp
    awk -v p="$*" -v WS="$WS" 'BEGIN{
      # 码点表(按类号顺序, 类k -> cp_arr[k])
      na=0
      while((getline ln < "/tmp/qscl_cpm.txt")>0) cp_arr[na++]=ln+0
      n=split(p,_p,/[ ,\t]+/)
      for(j=0;j<64;j++) px[j]=int(_p[j+1])+0
      for(b=0;b<8;b++) for(s=0;s<4;s++){
        fp=WS"/qscl_real_weights/qscl_real_b"b"_s"s".w"; c=0
        while((getline ln < fp)>0){split(ln,r,","); for(j=0;j<64;j++) w[(b*4+s)*32960 + c*64 + j]=r[j+1]+0; c++}
        close(fp)
      }
      best=-999999999; bk=0
      for(b=0;b<8;b++) for(c=0;c<515;c++){
        k=b*515+c; sum=0
        for(s=0;s<4;s++){ base=((b*4+s)*32960 + c*64)
          for(j=0;j<64;j++) sum+=px[j]*w[base+j] }
        if(sum>best){ best=sum; bk=k }
      }
      printf "{\"class\":%d,\"score\":%.2f,\"codepoint\":%d,\"batch\":%d,\"cls\":%d}", bk, best, cp_arr[bk+0], int(bk/515), bk%515
    }'
    ;;
  gen|infer)
    K="$1"
    mkcp
    LC_ALL=C awk -v k="$K" -v WS="$WS" 'BEGIN{
      na=0; while((getline ln < "/tmp/qscl_cpm.txt")>0) cp_arr[na++]=ln+0
      b=int(k/515); c=k%515
      for(s=0;s<4;s++){
        fp=WS"/qscl_real_weights/qscl_real_b"b"_s"s".w"; cc=0
        while((getline ln < fp)>0){split(ln,r,","); if(cc==c) for(j=0;j<64;j++) wr[j+s*64]=r[j+1]+0; cc++}
        close(fp)
      }
      for(j=0;j<64;j++){ n1=(wr[j]>0.05)+(wr[j+64]>0.05)+(wr[j+128]>0.05)+(wr[j+192]>0.05); raw[j]=(n1>=3) }
      # 码点 -> 4字节UTF-8 (反向映射: 生成真彝文字符, 纯awk算术)
      # 标准: b0=240+(cp>>18) b1=128+((cp>>12)&0x3F) b2=128+((cp>>6)&0x3F) b3=128+(cp&0x3F)
      # 直接对cp分位, 不要减0x10000! (减了会编码成 U+E2xxx 而非 U+F2xxx)
      cp=cp_arr[k+0]
      a0=240+int(cp/262144)
      a1=128+int(cp/4096)%64
      a2=128+int(cp/64)%64
      a3=128+cp%64
      printf "{\"class\":%d,\"batch\":%d,\"codepoint\":%d,\"char\":\"", k, b, cp
      printf "%c%c%c%c", a0, a1, a2, a3
      printf "\",\"binary\":[", k, b, cp_arr[k+0]
      for(j=0;j<63;j++) printf "%d,",raw[j]; printf "%d]",raw[63]
      printf ",\"art\":\""
      for(rr=0;rr<8;rr++){ if(rr>0) printf "\\n"; for(c2=0;c2<8;c2++) printf "%s",(raw[rr*8+c2]?"#":".") }
      printf "\"}"
    }'
    ;;
esac
