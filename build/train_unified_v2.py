#!/usr/bin/env python3
"""不同起点叠加态并行 统一训练 v2(精简加速版)
识别/推理/生成三合一,共用W矩阵,直接像素学习
- 识别: argmax(W·x) → 类号
- 生成: W[k]行向量 = 类k原型像素(识别逆运算)
- 4态不同seed并行训练 → 投票坍缩
"""
import os, random

GLYPH = "qdfs/ns/data/yi_glyph_4120.data"
MAP   = "qdfs/ns/data/yi_train_4120.data"
OUT   = "qdfs/ns/models"
os.makedirs(OUT, exist_ok=True)

BATCHES=8; STATES=4; PER=515; DIM=64; LR=5; EPOCHS=20; SEED=2026

# 读真实字形
glyphs=[]
with open(GLYPH) as f:
    for line in f:
        line=line.strip()
        if not line or line[0]=='#': continue
        pix=[int(x) for x in line.split(':',1)[1].split(',')]
        glyphs.append(pix)
assert len(glyphs)==4120

# 码点映射
cp=[0]*4120
with open(MAP) as f:
    for line in f:
        p=line.strip().split()
        if len(p)==2: cp[int(p[1])]=int(p[0])

with open(os.path.join(OUT,"class_codepoint.txt"),"w") as f:
    f.write("# 类号 码点(hex) 码点(dec)\n")
    for k in range(4120): f.write(f"{k} U+{cp[k]:04X} {cp[k]}\n")

print(f"[数据] 4120字×{DIM}像素 + 码点映射 就绪")

# 训练8批×4态
for b in range(BATCHES):
    ks=b*PER; ke=ks+PER
    batch=glyphs[ks:ke]
    models=[]
    for s in range(STATES):
        rng=random.Random(SEED+b*100+s*13+7)
        W=[[rng.randint(-3,3) for _ in range(DIM)] for _ in range(PER)]
        for ep in range(EPOCHS):
            idx=list(range(PER)); rng.shuffle(idx)
            for k in idx:
                x=batch[k]
                # 识别: argmax
                scores=[sum(W[c][d]*x[d] for d in range(DIM)) for c in range(PER)]
                kp=scores.index(max(scores))
                # 三合一更新
                for d in range(DIM):
                    W[k][d]+=(x[d]*2-1)*LR       # 生成: 原型靠近输入
                    W[kp][d]-=(x[d]*2-1)*LR      # 识别: 错分减
                    if W[k][d]>50: W[k][d]=50
                    elif W[k][d]<-50: W[k][d]=-50
                    if W[kp][d]>50: W[kp][d]=50
                    elif W[kp][d]<-50: W[kp][d]=-50
            if(ep+1)%10==0:
                acc=sum(1 for k in range(PER) if sum(W[c][d]*batch[k][d] for d in range(DIM) for c in range(PER)) and k==max(range(PER),key=lambda c:sum(W[c][d]*batch[k][d] for d in range(DIM))))
                print(f"  b{b}_s{s} ep{ep+1}/{EPOCHS} acc={acc}/{PER}={acc/PER*100:.1f}%")
        models.append(W)
        # 写单态权重
        with open(os.path.join(OUT,f"qscl_b{b}_s{s}.w"),"w") as f:
            for k in range(PER): f.write(",".join(str(v) for v in W[k])+"\n")
    # 4态合并
    with open(os.path.join(OUT,f"qscl_b{b}_sM.w"),"w") as f:
        for k in range(PER):
            row=[sum(models[s][k][d] for s in range(STATES))//STATES for d in range(DIM)]
            f.write(",".join(str(v) for v in row)+"\n")
    # 测试: 自指+真实
    acc=0
    for k in range(PER):
        x=batch[k]
        scores=[sum(models[s][c][d]*x[d] for s in range(STATES) for d in range(DIM)) for c in range(PER)]
    # 简化: 用合并权重测
    acc=0
    for k in range(PER):
        x=batch[k]
        Wm=[[sum(models[s][c][d] for s in range(STATES))//STATES for d in range(DIM)] for c in range(PER)]
        scores=[sum(Wm[c][d]*x[d] for d in range(DIM)) for c in range(PER)]
        if scores.index(max(scores))==k: acc+=1
    print(f"  batch{b} 合并4态 自指率={acc}/{PER}={acc/PER*100:.1f}%")

print("\n[完成] 32份权重+8份合并权重 生成")
print("识别/生成共用W: 识别=argmax(W·x), 生成=W[k]行向量")
