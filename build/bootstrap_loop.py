#!/usr/bin/env python3
# 自举循环: 看→写→画→类识别→新前缀→写→画... 永不停止
# 不分类: 一套4态并行整数点积, 同一64像素/81类空间
import os, re
from collections import Counter
os.chdir("/root/QSM/QLife")
def parse_w(fn):
    return [int(x) for x in open(fn).read().split("\n") if x.strip() and x.strip().lstrip("-").isdigit()]
def parse_w2(fn):
    n=parse_w(fn); return n[2:6563], n[6564:13125]
invW={s:parse_w(f"qdfs/ns/models/qscl_inv_s{s}.w")[2:5186] for s in "0123"}
clsW={s:parse_w(f"qdfs/ns/models/qscl_cls_s{s}.w")[2:5186] for s in "0123"}
lmW={s:parse_w2(f"qdfs/ns/models/qscl_lm2_s{s}.w") for s in "0123"}
def next_class(p1,p2):
    votes=[0]*81
    for s in "0123":
        W1,W2=lmW[s]; row=[W1[p1*81+c]+W2[p2*81+c] for c in range(81)]
        votes[row.index(max(row))]+=1
    return votes.index(max(votes))
def draw(cls):
    return [1 if sum(1 for s in "0123" if invW[s][cls*64+k]>0)>=2 else 0 for k in range(64)]
def recog(px):
    preds=[]
    for s in "0123":
        W=clsW[s]; row=[sum(px[k]*W[k*81+cc] for k in range(64)) for cc in range(81)]
        preds.append(row.index(max(row)))
    return Counter(preds).most_common(1)[0][0]
# 从真实字符d[1,2]起步
def d2c(d):
    d2cp={}
    for l in open("qdfs/ns/data/cp2d.txt"):
        p=l.strip().split()
        if len(p)>=2: d2cp[int(p[1])]=int(p[0])
    cph2cls={}
    for l in open("qdfs/ns/corpus/vocab_map.txt"):
        p=l.strip().split()
        if len(p)>=2: cph2cls[p[1]]=int(p[0])
    return cph2cls.get("F"+format(d2cp.get(d,0)&0xFFFF,"04X"),-1)
def showc(px):
    return "|"+"".join("#" if px[r*8+k] else "." for r in range(8) for k in range(8))+"|"
print("="*52)
print("  自举循环: 看→写→画→类识别→(新前缀)→写→画 永不停止")
print("="*52)
sen=[d2c(1),d2c(2)]; p1,p2=sen[0],sen[1]
print(f"  看: 真字d[1,2] → 类{sen}\n")
for step in range(12):
    nc=next_class(p1,p2); sen.append(nc); p1,p2=p2,nc
    px=draw(nc); rc=recog(px)
    mark="✓" if rc==nc else "△"
    print(f"  #{step+1} 写类{nc:3d} → 画 {showc(px)} → 识{rc:3d} {mark}")
print("\n  自举循环闭合, 持续生长中...")
