# QSCL真训练方法 — 基于论文的正确步骤
# 输入: 字形像素图 (不是码点数字!)
# 来源: Hot-Start Visual Glyphs(2024), Glyph-aware Embedding(2017), NITI(2024)

## 核心概念

### 1. 输入: 像素图, 不是码点
- 字符 → 渲染为N×N位图 → 展开为向量
- 不是 `encode(code) = code`, 而是 `x = bitmap(char)`
- 例子: 彝文 U+A000 → 8×8像素图 → 64维0/1向量

### 2. 网络: 从像素学特征
- 单层感知机: W[类别数×输入维]
- 多层MLP: 输入→隐藏层→输出 (更强大的特征提取)
- 不是 `pred = code - b` (这是减法，不是认字!)

### 3. 训练: 梯度下降
- 前向: logits = W·x
- 损失: cross-entropy (选最大logits为预测)
- 反向: 正确类权重+lr×x, 错误类权重-lr×x
- 迭代多轮，误差收敛

### 4. 叠加态: 4态不同起点
- 4个独立网络，不同初始权重
- 各自训练，学到不同特征子集
- 坍缩投票/平均，综合所有态知识

### 5. 部署: 纯权重推理
- 加载权重文件
- 输入像素图 → 前向计算 → argmax → 标签
- 不查表、不硬编码

## QEntL实现

### Step 1: 生成训练数据
```python
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("lingyi.ttf", 40)
for label in range(16):
    char = chr(0xA000 + label)
    img = Image.new('L', (32, 32), 255)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), char, fill=0, font=font)
    img8 = img.resize((8, 8))
    bitmap = [0 if p > 128 else 1 for p in img8.getdata()]
    # 保存: label:pixel0,pixel1,...,pixel63
```

### Step 2: 训练脚本框架
```qentl
var g_LR = 1000  # 学习率(大步长快速收敛)
var g_EP = 100   # 训练轮数

# 权重: 64×16 = 1024
var g_W[1024]
# 像素: 16×64
var g_P[1024]
# logits
var g_L[16]

# 前向: logits[j] = sum(W[j*64+i] * P[i])
def forward(idx):
    var base = idx * 64
    var j = 0
    while (j < 16):
        var sum = 0
        var i = 0
        while (i < 64):
            sum = sum + g_W[j * 64 + i] * g_P[base + i]
            i = i + 1
        end
        g_L[j] = sum
        j = j + 1
    end
end

# 训练: delta(W) = lr * (target - pred) * input
def train_one(idx):
    forward(idx)
    var label = idx
    var pred = argmax(g_L, 16)
    if (pred == label): return 0 end
    var base = idx * 64
    var i = 0
    while (i < 64):
        if (g_P[base + i] > 0):
            g_W[label * 64 + i] = g_W[label * 64 + i] + g_LR
            g_W[pred * 64 + i] = g_W[pred * 64 + i] - g_LR
        end
        i = i + 1
    end
    return 1
end
```

### Step 3: 不同起点叠加态
```qentl
# 4态从不同初始权重出发
def train_state(sid):
    g_W_init(sid)  # 不同种子初始化
    var ep = 0
    while (ep < g_EP):
        var s = 0
        while (s < 16):
            train_one(s)
            s = s + 1
        end
        ep = ep + 1
    end
    save_weights(sid)
end

# 态0: 随机种子1
# 态1: 随机种子101
# 态2: 随机种子202
# 态3: 随机种子303
```

### Step 4: 坍缩合并
```qentl
# 投票坍缩
def collapse_vote():
    var votes[16]
    var s = 0
    while (s < 4):
        load_weights(s)
        var i = 0
        while (i < 16):
            g_P[i*64 .. i*64+63] = test_pixels[i]
            forward(i)
            var pred = argmax(g_L, 16)
            votes[pred] = votes[pred] + 1
            i = i + 1
        end
        s = s + 1
    end
    # 多数决
    var best = 0
    var bv = 0
    var j = 0
    while (j < 16):
        if (votes[j] > bv):
            bv = votes[j]
            best = j
        end
        j = j + 1
    end
    return best
end
```

## 关键差异：之前错在哪

| 项目 | 之前(错误) | 正确(论文) |
|------|-----------|-----------|
| 输入 | 码点数字993040 | 8×8像素位图 |
| 编码 | position encoding → 还原码点 | pixel vector → 视觉特征 |
| 网络 | pred = encode(code) - b | logits = W·x + bias |
| 学习 | b收敛到993040 | W学到像素到类别的映射 |
| 结果 | 减法查表 | 真正的模式识别 |

## 为什么之前训练不出来

1. **U+A000段字符在8×8像素下太相似** → 单层感知机不够区分
2. **需要更多类别或更大输入尺寸** → 16x16像素或更多训练样本
3. **需要多层网络** → MLP 64→32→16→16 才能提取足够特征

## 下一步

- [ ] 增加输入尺寸: 8×8 → 16×16 (256维)
- [ ] 增加隐藏层: 单层 → MLP 2层
- [ ] 多态训练: 4态不同种子 → 投票坍缩
- [ ] 验证: 保存权重 → 服务器加载 → /api/yi 测试
