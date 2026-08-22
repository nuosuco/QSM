#!/usr/bin/env python3
# 端到端闭环验证: 看(识别)→写(自回归生成)→画(像素)  不分类 4态并行
# 重要: 画→看的回读不能对回原字(类→字多对一, 画的是类平均像素, 识别器认具体字),
# 这是映射设计决定的, 非bug. 要闭合成环需统一接口到类空间(阶段D深化)
import os, re, subprocess
os.chdir("/root/QSM/QLife")
d2cp={}
for l in open("qdfs/ns/data/cp2d.txt"):
    p=l.strip().split()
    if len(p)>=2: d2cp[int(p[1])]=int(p[0])
cph2cls={}
for l in open("qdfs/ns/corpus/vocab_map.txt"):
    p=l.strip().split()
    if len(p)>=2: cph2cls[p[1]]=int(p[0])
d2cls={d:cph2cls["F"+format(cp&0xFFFF,"04X")] for d,cp in d2cp.items() if "F"+format(cp&0xFFFF,"04X") in cph2cls}
def parse_w(fn,n):
    return [int(x) for x in open(fn).read().split("\n") if x.strip() and x.strip().lstrip("-").isdigit()]
def parse_w2(fn):
    n=parse_w(fn,2)
    return n[2:6563], n[6564:13125]
inv={s:parse_w(f"qdfs/ns/models/qscl_inv_s{s}.w",2) for s in "0123"}
lm={s:parse_w2(f"qdfs/ns/models/qscl_lm2_s{s}.w") for s in "0123"}
def see(d):
    r=subprocess.run(["bash","build/yi_infer_v4.sh",str(d)],capture_output=True,text=True)
    m=re.search(r"top=(\d+)",(r.stdout or "").strip())
    return int(m.group(1)), d2cls.get(int(m.group(1)),-1) if m else (-1,-1)
def next_class(p1,p2):
    votes=[0]*81
    for s in "0123":
        W1,W2=lm[s]; row=[W1[p1*81+c]+W2[p2*81+c] for c in range(81)]
        votes[row.index(max(row))]+=1
    return votes.index(max(votes))
def draw(cls):
    return [1 if sum(1 for s in "0123" if inv[s][cls*64+k]>0)>=2 else 0 for k in range(64)]
for d1,d2 in [(0,1),(2,3),(10,20)]:
    _,c1=see(d1); _,c2=see(d2)
    if c1<0 or c2<0: continue
    sen=[c1,c2]; p1,p2=c1,c2
    for _ in range(3):
        n=next_class(p1,p2); sen.append(n); p1,p2=p2,n
    px=draw(sen[-1])
    print(f"看[{d1},{d2}]→写{sen}→画类{sen[-1]}")
    for row in range(8): print("  "+"#." *[0])
