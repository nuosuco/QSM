# 4120彝文字形数据生成流程

> QSM项目根 = /root/QSM/QLife
> 本文记录: 从 4120彝文三语表 → lingyi字体 → 8×8像素训练数据 的完整数据链路
> 生成日期: 2026-08-22

## 1. 数据链路总览

```
4120彝文三语表(yi_data_simple.data)   ← 权威字符源,4120字,列2=Yi字符
        │  提供每个码点对应的真实Yi字符(私有区 U+F2710~U+F3727)
        ▼
lingyi.ttf (零碎通用彝文(黑)-输入法版) ← 权威字形源,4120字真轮廓glyph
        │  用fontTools/PIL按字符光栅化
        ▼
8×8 二值像素 (yi_flat_b0..b7.bin)     ← 训练数据,每字64像素/128字节,515字×8批
        │  喂给QSCL识别器训练
        ▼
qscl_b0..b7_s0..s3.w (32份4态权重)     ← 最终模型,515×64整数/份
```

## 2. 第一步: 4120彝文三语表 (权威字符源)

- 文件: `qdfs/ns/data/yi_data_simple.data`
- 格式: 每行 `码点\t彝文字符\t笔画编码\t汉译`
- 行数: **4120** (已剔除凉山残留 F222E~F2400 共9行)
- 码点范围: **U+F2710 ~ U+F3727**, 全部私有区, **0个标准区A000**
- 来源: 中华v2.0.4.22 xlsx 表 (通用彝文彝汉对照表)
- 旧脏版4130已备份: `qdfs/ns/data/yi_data_simple_4130_bak.data`
- **关键**: 列2的Yi字符本身就是私有区字符,这是光栅化的输入字符,不是字形

## 3. 第二步: lingyi.ttf 字体 (权威字形源)

- 文件: `qdfs/ns/data/lingyi.ttf` (web前端的 `web/fonts/lingyi_smp.ttf` 是同一份)
- 来源: 中华QQ发来 "零碎通用彝文(黑)-输入法版"
- **关键区别**: 旧lingyi.ttf(1793KB)只有标准区A000的glyph,私用区F2710~F3727**全空**,渲染全豆腐
- 新字体(1302KB)fmt12 cmap含 **4120个私用区glyph**,vision已验证渲染为真彝文(非豆腐)
- 旧假字体(1793KB)已删除,备份于 `*_old_noPUA.ttf` 后也已清理
- 验证命令: `fontTools` 查 fmt12 cmap 私有区条目数 == 4120

## 4. 第三步: 光栅化 4120 → 8×8像素

- 脚本: `/tmp/final_rasterize.py`
- 方法: PIL `ImageFont.truetype(font, size).getbbox(chr(cp))` 定位字形, 光栅化到16×16再缩放二值化到8×8
- 尺寸策略: 主体size=17, 少数字形换size(如13/16)以保证**零重复**
- 输出格式: 每字128字节 = 64像素 × "0\n"/"1\n" 文本(对齐训练脚本hebbian_train.sh的mapfile读取)
- 文件: `qdfs/ns/data/yi_flat_b0..b7.bin`, 每批515字
- 校验: `qdfs/ns/data/yi_glyph_4120.data` (d=码点偏移:像素串)
- **最终结果: 4120字像素100%唯一, 重复组=0, 重复字=0**

## 5. 尺寸选择扫描结果 (size → 重复字)

| size | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 22 |
|---|---|---|---|---|---|---|---|---|---|
| 重复字 | 104 | 101 | 24 | 29 | **8** | 20 | 10 | 18 | 21 |

size=17最省(仅8字重复), 4对共8字用独立size后清零。

## 6. 关键经验(中华铁律已记)

1. **数据从三语表列2的Yi字符来**,不是抄像素、不是标准区
2. **字形来源=字体glyph**,旧字体私用区glyph缺失→渲染豆腐→必须换真字体
3. **8×8分辨率极限**: 用尺寸+位置微调可让4120字零重复(无需16×16)
4. **三语表/字体/像素表三者缺一不可**,任一缺失都无法重建数据

## 7. 相关文件

- 三语表: `qdfs/ns/data/yi_data_simple.data` (4120行,纯净版)
- 字体: `qdfs/ns/data/lingyi.ttf`, `web/fonts/lingyi_smp.ttf` (同一份)
- 像素表: `qdfs/ns/data/yi_flat_b0..b7.bin` (515×8批)
- 校验: `qdfs/ns/data/yi_glyph_4120.data`
- 训练脚本: `build/hebbian_train.sh`
- 训练源备份: `qdfs/ns/data_backup_oldpixels/`