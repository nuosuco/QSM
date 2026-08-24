#!/bin/bash
# qscl_engine.sh v5 — QSCL不同起点叠加态并行 (8x8 + 16x16)
WS=/root/QSM/QLife/qdfs/ns/models
CPMAP=$WS/class_codepoint.txt
SIZE=8; WDIR=qscl_real_weights; DIM=64; PFX=qscl_real
for a in "$@"; do if [ "$a" = "--16" ]; then SIZE=16; WDIR=qscl_16x16_weights; DIM=256; PFX=qscl_16x16; fi; done
OP=$1; shift
mkcp(){ awk 'NR>1{print $3}' "$CPMAP" > /tmp/qscl_cpm.txt 2>/dev/null || true; }
Q='"'
NL='\n'
mkcp
case "$OP" in
argmax|img64)
  LC_ALL=C awk -v p="$*" -v WS=$WS -v WD=$WDIR -v PFX=$PFX -v DIM=$DIM -v SZ=$SIZE 'BEGIN{
    na=0; while((getline ln < "/tmp/qscl_cpm.txt")>0) cp_arr[na++]=ln+0
    n=split(p,_p,/[ ,\t]+/); for(j=0;j<DIM;j++) px[j]=int(_p[j+1])+0
    for(b=0;b<8;b++) for(s=0;s<4;s++){
      fp=WS"/"WD"/"PFX"_b"b"_s"s".w"; c=0
      while((getline ln < fp)>0){split(ln,r,","); for(j=0;j<DIM;j++) w[(b*4+s)*515*DIM+c*DIM+j]=r[j+1]+0; c++}
      close(fp)
    }
    best=-1e18; bk=0
    for(b=0;b<8;b++) for(c=0;c<515;c++){
      k=b*515+c; sum=0
      for(s=0;s<4;s++){ base=((b*4+s)*515*DIM+c*DIM)
        for(jj=0;jj<DIM;jj++) sum+=px[jj]*w[base+jj] }
      if(sum>best){ best=sum; bk=k }
    }
    print "class="bk" score="best" codepoint="cp_arr[bk]" batch="int(bk/515)" cls="bk%515" size="SZ
  }'
  ;;
gen|infer)
  K=$1
  LC_ALL=C awk -v k=$K -v WS=$WS -v WD=$WDIR -v PFX=$PFX -v DIM=$DIM -v SZ=$SIZE 'BEGIN{
    na=0; while((getline ln < "/tmp/qscl_cpm.txt")>0) cp_arr[na++]=ln+0
    b=int(k/515); c=k%515
    for(s=0;s<4;s++){
      fp=WS"/"WD"/"PFX"_b"b"_s"s".w"; cc=0
      while((getline ln < fp)>0){split(ln,r,","); if(cc==c) for(j=0;j<DIM;j++) wr[j+s*DIM]=r[j+1]+0; cc++}
      close(fp)
    }
    thr=0.005
    for(j=0;j<DIM;j++){ n1=0; for(s=0;s<4;s++) n1+=(wr[j+s*DIM]>=thr?1:0); raw[j]=(n1>=3)?1:0 }
    # 模型直接输出像素(空格分隔), 桌面CSS grid直接渲染
    printf "像素: "
    for(j=0;j<DIM;j++){if(j>0)printf " ";printf "%d",raw[j]}
    printf "\n"
  }'
  ;;
esac
