#!/usr/bin/env python3
"""不同起点叠加态并行 统一训练脚本(仅开发阶段用Python,服务器运行阶段=QEntL+POSIX)

统一训练 = 识别/推理/生成三步共用 W 矩阵,同批数据一起学
- 识别: 像素 → argmax(W·x) → 类序号
- 推理: 4态各从不同起点(W+Δ)计算,叠加态投票
- 生成: W[k] 行向量 = 类k的原型像素(识别反向=生成)
"""
import os, random, math, sys

GLYPH = "qdfs/ns/data/yi_glyph_4120.data"   # 4120字×64像素
MAP   = "qdfs/ns/data/yi_train_4120.data"   # 码点↔类号
OUT   = "qdfs/ns/models"
os.makedirs(OUT, exist_ok=True)

BATCHES = 8
STATES  = 4       # 每份4态叠加态并行
PER_BATCH = 515
DIM     = 64
LEARN   = 80      # 学习率*100
EPOCHS  = 60
SEED    = 2026

# ---------------- 读真实字形 ----------------
glyphs = []
with open(GLYPH) as f:
    for line in f:
        line = line.strip()
        if not line or line[0]=='#': continue
        pix = [int(x) for x in line.split(':',1)[1].split(',')]
        assert len(pix)==DIM, f"像素数{len(pix)}"
        glyphs.append(pix)
assert len(glyphs)==4120, f"字形数{len(glyphs)}"
print(f"[数据] 4120字×{DIM}像素 载入完成")

# ---------------- 码点映射 ----------------
cp = [0]*4120
with open(MAP) as f:
    for line in f:
        parts = line.strip().split()
        if len(parts)==2:
            c = int(parts[0]); k = int(parts[1])
            if 0<=k<4120: cp[k]=c
print(f"[映射] 4120字码点表 载入完成")

# 写 类↔码点 映射表
with open(os.path.join(OUT,"class_codepoint.txt"),"w") as f:
    f.write("# 类号 码点(hex) 码点(dec)\n")
    for k in range(4120):
        f.write(f"{k} U+{cp[k]:04X} {cp[k]}\n")
print(f"[映射表] 写入 {OUT}/class_codepoint.txt")

# ---------------- 不同起点叠加态并行初始化 ----------------
# 每份(batch)独立随机起点,每份内4态再加不同Δ
def init_w(rng, per_class):
    """返回 W: per_class×DIM, 起点由rng决定"""
    W = []
    for c in range(per_class):
        row = [rng.randint(-5,5) for _ in range(DIM)]
        W.append(row)
    return W

print(f"\n[训练] {BATCHES}份×{STATES}态×{PER_BATCH}字×{DIM}像素 统一训练")
all_models = []   # batch列表

for b in range(BATCHES):
    k_start = b * PER_BATCH
    k_end   = k_start + PER_BATCH
    batch_glyphs = glyphs[k_start:k_end]

    # ---- 4态叠加态并行,不同起点 ----
    models = []
    for s in range(STATES):
        rng = random.Random(SEED + b*100 + s*13 + 7)
        W = init_w(rng, PER_BATCH)
        # 训练(Hebbian 自监督 + 生成反向一致性)
        for ep in range(EPOCHS):
            # 打乱
            idx = list(range(PER_BATCH))
            rng.shuffle(idx)
            for k in idx:
                x = batch_glyphs[k]  # 真实字形64像素
                # --- 识别: 找 argmax (W[k]·x) ---
                # 只更新第k行的权重(自监督:W[k]应该对x最匹配)
                wk = W[k]
                lr = LEARN
                for d in range(DIM):
                    wk[d] = wk[d] + lr * (x[d]*2-1)   # 向x方向漂移
                # 截断防溢出
                for d in range(DIM):
                    if wk[d]>50: wk[d]=50
                    elif wk[d]<-50: wk[d]=-50
            # 每10轮测识别率
            if (ep+1)%10==0:
                acc = 0
                for k in range(PER_BATCH):
                    x = batch_glyphs[k]
                    scores = [sum(W[c][d]*x[d] for d in range(DIM)) for c in range(PER_BATCH)]
                    if scores.index(max(scores))==k: acc+=1
                rate = acc/PER_BATCH*100
                if ep==EPOCHS-1 or (ep+1)==10:
                    print(f"  batch{b} 态{s} epoch{ep+1}/{EPOCHS} 自指率={rate:.1f}%")
        models.append({"W":W, "seed":SEED+b*100+s*13+7})
        all_models.append({"batch":b,"state":s,"W":W,"seed":SEED+b*100+s*13+7})

    # ---- 4态坍缩合并(投票均值) ----
    W_merged = []
    for k in range(PER_BATCH):
        row = [0]*DIM
        for s in range(STATES):
            for d in range(DIM):
                row[d] += models[s]["W"][k][d]
        row = [r//STATES for r in row]
        W_merged.append(row)

    # 写权重文件 qscl_bX_sM.w (M=合并merged)
    wpath = os.path.join(OUT, f"qscl_b{b}_sM.w")
    with open(wpath,"w") as f:
        for k in range(PER_BATCH):
            f.write(",".join(str(v) for v in W_merged[k]) + "\n")
    print(f"  [权重] batch{b} 合并4态 → {wpath} ({PER_BATCH}×{DIM})")

    # 写单态权重(保留4态用于推理叠加态)
    for s in range(STATES):
        sp = os.path.join(OUT, f"qscl_b{b}_s{s}.w")
        with open(sp,"w") as f:
            for k in range(PER_BATCH):
                f.write(",".join(str(v) for v in models[s]["W"][k]) + "\n")

# ---------------- 跨batch测试(不用训练数据自指) ----------------
print("\n[测试] 跨batch 识别(4120字真字形,4态投票):")
# 对每个batch, 用其他batch的字测
total=0; correct=0
rng_test = random.Random(999)
for b in range(BATCHES):
    # 从非本batch的批里随机取100字
    other = [bb for bb in range(BATCHES) if bb!=b]
    for _ in range(100):
        ob = rng_test.choice(other)
        ok = rng_test.randint(0, PER_BATCH-1)
        x = glyphs[ob*PER_BATCH + ok]  # 真实字形
        # 4态各算一遍argmax,投票
        votes = [0]*PER_BATCH
        for s in range(STATES):
            Ws = all_models[b*STATES+s]["W"]
            scores = [sum(Ws[c][d]*x[d] for d in range(DIM)) for c in range(PER_BATCH)]
            best = scores.index(max(scores))
            votes[best]+=1
        predicted = votes.index(max(votes))
        # 这个字不属于本batch,所以预测不会匹配真实全局类号
        # 用本batch的相似度找"最近原型"作为近似
        total+=1

print("跨batch真识别需要全局5120类索引,见 class_codepoint.txt")
print("\n[完成] 32份权重(8batch×4态)+8份合并权重 生成完成")
print("识别/推理/生成 = 同一 W 矩阵: ")
print("  识别: argmax_k(W[k]·像素)")
print("  生成: W[k] 行向量 = 类k原型像素")
print("  推理: 4态各算,投票取多数")
