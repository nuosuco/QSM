#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成量子水印示例图像
用于用户指南展示量子水印编码
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import hashlib
import random
import os

def create_quantum_watermark_example():
    """创建量子水印示例图像"""
    
    # 创建一个放大版的量子水印示例
    width, height = 800, 400
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 绘制标题
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 20), "量子水印示例 (1000倍放大视图)", fill=(0, 0, 0), font=font)
    
    # 绘制说明文字
    draw.text((20, 60), "普通肉眼无法看到的量子水印，包含完整量子基因编码", fill=(80, 80, 80), font=font)
    
    # 创建随机的量子基因编码
    timestamp = "20250405123456"
    content_hash = "ABC123"
    entanglement_value = "XYZ789"
    quantum_gene = f"QG-QSM01-TEXT-{timestamp}-{content_hash}-ENT{entanglement_value}"
    
    # 绘制量子基因编码
    try:
        small_font = ImageFont.truetype("arial.ttf", 14)
    except:
        small_font = font
    
    draw.text((20, 100), f"量子基因编码: {quantum_gene}", fill=(0, 0, 128), font=small_font)
    
    # 创建一个模拟的量子水印放大视图
    # 在图像中央绘制一个区域，代表放大的量子水印
    magnifier_x, magnifier_y = 120, 160
    magnifier_width, magnifier_height = 560, 210
    
    # 绘制放大区域边框
    draw.rectangle([(magnifier_x-2, magnifier_y-2), 
                    (magnifier_x+magnifier_width+2, magnifier_y+magnifier_height+2)], 
                   outline=(200, 200, 200), width=2)
    
    # 填充背景
    draw.rectangle([(magnifier_x, magnifier_y), 
                    (magnifier_x+magnifier_width, magnifier_y+magnifier_height)], 
                   fill=(250, 250, 250))
    
    # 转换量子基因编码为二进制
    gene_binary = ''.join(format(ord(c), '08b') for c in quantum_gene)
    
    # 创建一个随机种子，基于量子基因编码
    seed = int(hashlib.md5(quantum_gene.encode()).hexdigest(), 16) % 1000000
    random.seed(seed)
    np.random.seed(seed)
    
    # 绘制模拟的量子水印微观结构
    # 方法1: 点阵模式
    for i in range(len(gene_binary)):
        x = magnifier_x + 10 + (i % 70) * 8
        y = magnifier_y + 20 + (i // 70) * 8
        
        if x < magnifier_x + magnifier_width - 10 and y < magnifier_y + magnifier_height - 10:
            dot_size = 3
            if gene_binary[i] == '1':
                draw.ellipse([(x-dot_size, y-dot_size), (x+dot_size, y+dot_size)], 
                            fill=(0, 0, 220, 150))
            else:
                draw.ellipse([(x-dot_size, y-dot_size), (x+dot_size, y+dot_size)], 
                            fill=(220, 0, 0, 150))
    
    # 方法2: 绘制一些随机的微小结构，模拟量子油墨分子
    for _ in range(300):
        x = magnifier_x + random.randint(10, magnifier_width-10)
        y = magnifier_y + random.randint(80, magnifier_height-10)
        
        structure_type = random.randint(0, 2)
        
        if structure_type == 0:  # 点
            size = random.randint(1, 2)
            opacity = random.randint(100, 180)
            draw.ellipse([(x-size, y-size), (x+size, y+size)], 
                         fill=(0, 0, 150, opacity))
        elif structure_type == 1:  # 短线
            length = random.randint(3, 6)
            angle = random.uniform(0, 3.14)
            end_x = x + int(length * np.cos(angle))
            end_y = y + int(length * np.sin(angle))
            draw.line([(x, y), (end_x, end_y)], 
                     fill=(0, 150, 0, 150), width=1)
        else:  # 小三角
            size = random.randint(2, 3)
            draw.polygon([(x, y-size), (x-size, y+size), (x+size, y+size)], 
                        fill=(150, 0, 150, 120))
    
    # 添加放大符号
    draw.text((magnifier_x+10, magnifier_y+magnifier_height-30), 
              "1000倍放大视图 - 实际水印肉眼不可见", 
              fill=(120, 120, 120), font=small_font)
    
    # 保存图像
    output_path = "quantum_watermark_example.png"
    image.save(output_path)
    print(f"已生成量子水印示例图像: {output_path}")
    
    # 移动到正确位置
    target_dir = "docs/QSM/images"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    target_path = os.path.join(target_dir, "quantum_watermark_example.png")
    if os.path.exists(output_path):
        import shutil
        shutil.move(output_path, target_path)
        print(f"图像已移动到: {target_path}")

if __name__ == "__main__":
    create_quantum_watermark_example() 
"""
量子基因编码: QE-QUA-3ED599577D57
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""