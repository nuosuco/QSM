#!/usr/bin/env python3
# QSM v0.0.4 自举生长引擎 — 看/写/画/识 一套4态并行整数点积, 不分类, 永不停止
# 用法: python3 build/qbootstrap.py [--steps N] [--seeds 3,13 4,13] [--no-gate]
import os, sys, re, random, argparse
from collections import Counter
os.chdir("/root/QSM/QLife")

def parse_w(fn):
    return [int(x) for x in open(fn).read().split("\n") if x.strip() and x.strip().lstrip("-").isdigit()]
def parse_w2(fn):
    n=parse_w(fn); return n[2:6563], n[6564:13125]
ROOT="qdfs/ns/models"
LM={s:parse_w2(f"{ROOT}/qscl_lm3_s{s}.w") for s in "0123"}
INV={s:parse_w(f"{ROOT}/qscl_inv_s{s}.w")[2:5186] for s in "0123"}
CLS={s:parse_w(f"{ROOT}/qscl_cls_s{s}.w")[2:5186] for s in "0123"}
EOS={1,80}

def next_class(p1,p2,prev,temp=4):
    score=[0]*81
    for s in "0123":
        W1,W2=LM[s]
        for c in range(81): score[c]+=W1[p1*81+c]+W2[p2*81+c]
    if prev in EOS: score[1]-=20; score[80]-=20
    if temp<=0: return score.index(max(score))
    scaled=[sc//temp for sc in score]; m=min(scaled); scaled=[x-m for x in scaled]
    total=sum(scaled)
    if total<=0: return score.index(max(score))
    r=random.randint(0,total-1) if total>1 else 0
    acc=0
    for c in range(81):
        acc+=scaled[c]
        if acc>r: return c
    return 80

def draw(cls):
    return [1 if sum(1 for s in "0123" if INV[s][cls*64+k]>0)>=2 else 0 for k in range(64)]

def recog(px):
    preds=[]
    for s in "0123":
        W=CLS[s]; row=[sum(px[k]*W[k*81+cc] for k in range(64)) for cc in range(81)]
        preds.append(row.index(max(row)))
    return Counter(preds).most_common(1)[0][0]

def gate(cls): return recog(draw(cls))==cls

def showc(px):
    return "\n    ".join("".join("#" if px[r*8+k] else "." for k in range(8)) for r in range(8))

def d2c(d):
    d2cp={}
    for l in open("qdfs/ns/data/cp2d.txt"):
        p=l.strip().split()
        if len(p)>=2: d2cp[int(p[1])]=int(p[0])
    cph2cls={}
    for l in open("qdfs/ns/corpus/vocab_map.txt"):
        p=l.strip().split()
        if len(p)>=2: cph2cls[p[1]]=int(p[0])
    return cph2cls.get("F"+format(d2cp.get(d,0)&0xFFFF,"04X"),3)


def run_quiet(steps=12, seeds=[[3,13]]):
    seq=[]
    st=seeds[0]; sen=[st[0],st[1]]; p1,p2=st
    for _ in range(steps):
        nc=next_class(p1,p2,sen[-1]); seq.append(nc); sen.append(nc); p1,p2=p2,nc
        if nc in EOS:
            import random as _r
            sen=[seeds[0][0],seeds[0][1]]; p1,p2=seeds[0]; break
    print("SEQ="+",".join(str(x) for x in seq))

def run(steps=60, seeds=[[3,13],[4,13],[5,13]], no_gate=False):
    print("="*48)
    print("  QSM v0.0.4 自举生长引擎 (不分类,4态并行)")
    print("  看/写/画/识 一套整数点积, 永不停止")
    print("="*48)
    st=seeds[0]; sen=[st[0],st[1]]; p1,p2=st
    total=0; gate_ok=0; uniq=set(); sentences=0
    seed_cycle=0
    for _ in range(steps):
        nc=next_class(p1,p2,sen[-1]); total+=1; uniq.add(nc)
        g=gate(nc) if not no_gate else True
        if g: gate_ok+=1
        if not g and not no_gate:
            seed_cycle=(seed_cycle+1)%len(seeds); st=seeds[seed_cycle]; sen=[st[0],st[1]]; p1,p2=st
            continue
        sen.append(nc); p1,p2=p2,nc
        if nc in EOS:
            sentences+=1
            seed_cycle=(seed_cycle+1)%len(seeds); st=seeds[seed_cycle]; sen=[st[0],st[1]]; p1,p2=st
    print(f"\n  生成步数={total}  生成类多样={len(uniq)}/81  句数={sentences}")
    print(f"  识别门控通过率={gate_ok}/{total}={round(100*gate_ok/total)}%")
    # 展示最后一句(含画+识)
    print(f"\n  最后一句演示 看→写→画→识:")
    p1,p2=seeds[0]
    show_sen=[]
    for _ in range(8):
        nc=next_class(p1,p2,sen[-1]); show_sen.append(nc); p1,p2=p2,nc
        if nc in EOS: break
    for nc in show_sen:
        px=draw(nc); rc=recog(px)
        glyph="".join("#" if px[r*8+k] else "." for r in range(8) for k in range(8))
        mark="\u2713" if rc==nc else "\u25b3"
        print(f"    \u7c7b{nc:3d} -> \u8bc6{rc:3d} {mark} | {glyph}")
    print(f"\n  自举生长引擎运行完毕. 接入 --loop 可无限持续.")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--steps",type=int,default=60)
    ap.add_argument("--seeds",nargs="*",default=["3,13","4,13"])
    ap.add_argument("--no-gate",action="store_true")
    ap.add_argument("--quiet",action="store_true")
    args=ap.parse_args()
    seeds=[[int(x) for x in s.split(",")] for s in args.seeds]
    if args.quiet:
        run_quiet(args.steps,seeds)
    else:
        run(args.steps,seeds,args.no_gate)
