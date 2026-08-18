# QSCL字形训练完成报告 (2026-08-18)

## ✅ 成功成果

### 1. 单层感知机训练
- **架构**: 输入64像素 → 输出16类别
- **学习率**: 1000
- **收敛速度**: epoch 5-10
- **准确率**: 16/16 = 100%
- **脚本**: `qdfs/ns/train/qscl_glyph_train.qentl`
- **投票坍缩**: `qdfs/ns/train/qscl_glyph_vote_final.qentl`

### 2. 4态叠加态并行训练
- **种子**: 1, 101, 202, 303
- **结果**: 全部16/16 = 100%
- **坍缩**: 16/16 = 100% 全票一致
- **权重文件**: `qdfs/ns/models/glyph_state_{seed}_n16.w`

### 3. 数据生成
- **字体**: lingyi_smp.ttf (4094种不同字形)
- **渲染**: 48x48画布居中→NEAREST缩放至8x8
- **数据文件**: 
  - `yi_glyph_16_v3.data` (16字, 9.2像素激活)
  - `yi_glyph_40_v4.data` (40字, 38/40有效)

## ❌ 失败尝试

### 1. 20字训练
- **结果**: epoch9仅20%准确率
- **原因**: 样本增加后梯度震荡，需要更多epoch或更小lr

### 2. MLP多层网络(64→8→16)
- **结果**: 6%准确率，立即早停
- **原因**: QVM不支持反向传播，手动实现梯度更新有误

### 3. 40字训练
- **结果**: 超时（>180秒）
- **原因**: QVM数组池限制4096元素，40×64=2560超限

## 🔧 QVM限制发现

| Bug | 描述 | 解决方案 |
|-----|------|---------|
| 局部变量崩溃 | 函数内用var声明局部变量会崩溃 | 只用全局变量g_* |
| else if不支持 | QCL不支持else if语法 | 用嵌套if-else |
| 分号限制 | 不支持语句间分号分隔 | 换行分隔 |
| 三元运算符 | 不支持?:语法 | 用if-else |
| 数组池限制 | 最大4096元素 | N≤63 |

## 📊 当前最佳实践

```python
# 数据生成(Python临时工具)
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('/home/claude-worker/QSM/web/fonts/lingyi_smp.ttf', 48)
img = Image.new('1', (64, 64), 0)
draw = ImageDraw.Draw(img)
draw.text((x, y), char, font=font, fill=1)
img_small = img.resize((8, 8), Image.Resampling.NEAREST)

# 训练(QEntL)
# 单层感知机: lr=1000, epoch=10-20, N≤16
```

## 🚀 下一步方向

1. **增量训练**: 先训16字原型，再增量扩展到更多字
2. **分批训练**: 4120字分批次训练子模型
3. **特征工程**: 提取笔画、结构等高层特征
4. **性能优化**: 减少epoch数，优化QVM执行效率

## 提交记录

- `f417da46` - 4态叠加态并行训练成功: 全部16/16=100%, 投票坍缩16/16
- `61ab3e3d` - 生成真实字形像素数据(v2)
- `593c413b` - 推进40字字形训练+优化版训练器