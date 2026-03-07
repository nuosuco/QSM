#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彝文字符显示测试脚本
测试彝文字符的显示和转换功能
"""

import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def test_yi_characters():
    """测试彝文字符的显示"""
    print("=== 彝文字符显示测试 ===")
    
    # 测试彝文字符
    yi_chars = ['󲜐', '󲜑', '󲜒', '󲜓', '󲜔']
    
    print("原始彝文字符:")
    for char in yi_chars:
        print(f"字符: {char}, Unicode: U+{ord(char):X}")
    
    print("\n字符编码信息:")
    for char in yi_chars:
        code = ord(char)
        print(f"字符: {char}")
        print(f"  Unicode: U+{code:X}")
        print(f"  十进制: {code}")
        print(f"  二进制: {bin(code)}")
        print(f"  是否在彝文范围: {0xF0000 <= code <= 0xFFFFF}")
        print()

def create_yi_char_image(char, size=100):
    """创建彝文字符图片"""
    # 创建图片
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", size//2)
    except:
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            # 使用默认字体
            font = ImageFont.load_default()
    
    # 绘制边框
    draw.rectangle([0, 0, size-1, size-1], outline='red', width=2)
    
    # 绘制字符
    text = char
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    return img

def save_yi_char_images():
    """保存彝文字符图片"""
    print("=== 创建彝文字符图片 ===")
    
    # 彝文字符及其含义
    yi_chars_with_meanings = {
        '󲜐': '陷害',
        '󲜑': '兔子',
        '󲜒': '卷',
        '󲜓': '舔',
        '󲜔': '便宜',
        '5': '埋怨',
        '6': '裱褙',
        '7': '渣',
        '8': '尾',
        '9': '分开'
    }
    
    # 创建输出目录
    output_dir = "yi_char_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建图片
    for char, meaning in yi_chars_with_meanings.items():
        img = create_yi_char_image(char)
        filename = f"{output_dir}/yi_char_{ord(char):X}.png"
        img.save(filename)
        print(f"保存: {filename} - {meaning}")
    
    print(f"\n图片已保存到 {output_dir} 目录")

def test_unicode_ranges():
    """测试Unicode范围"""
    print("=== Unicode范围测试 ===")
    
    ranges = [
        ("彝文补充", 0xF0000, 0xFFFFF),
        ("彝文字符", 0x10A00, 0x10A5F),
        ("彝文扩展", 0x10A60, 0x10A7F),
        ("彝文扩展B", 0x10A80, 0x10A9F),
        ("彝文扩展C", 0x10AA0, 0x10ABF),
    ]
    
    for name, start, end in ranges:
        print(f"{name}: U+{start:X} - U+{end:X}")
        print(f"  字符数量: {end - start + 1}")
        print(f"  示例字符: {chr(start)}")
        print()

def test_browser_compatibility():
    """测试浏览器兼容性"""
    print("=== 浏览器兼容性测试 ===")
    
    # 测试不同范围的字符
    test_chars = [
        ('基本彝文', '󲜐'),
        ('表情符号', '😀'),
        ('中文字符', '你'),
        ('英文字符', 'A'),
        ('数字', '1'),
    ]
    
    for category, char in test_chars:
        code = ord(char)
        print(f"{category}: {char} (U+{code:X})")
        print(f"  是否在彝文范围: {0xF0000 <= code <= 0xFFFFF}")
        print()

def create_html_test_page():
    """创建HTML测试页面"""
    print("=== 创建HTML测试页面 ===")
    
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>彝文字符测试</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .char-box { 
            display: inline-block; 
            margin: 10px; 
            padding: 15px; 
            border: 2px solid #333; 
            background: #f0f0f0;
            font-size: 24px;
            text-align: center;
            min-width: 60px;
        }
        .canvas-box {
            display: inline-block;
            margin: 10px;
            border: 2px solid #666;
            background: #fff;
        }
    </style>
</head>
<body>
    <h1>彝文字符显示测试</h1>
    
    <h2>直接显示彝文字符</h2>
    <div id="direct-chars"></div>
    
    <h2>Canvas渲染彝文字符</h2>
    <div id="canvas-chars"></div>
    
    <script>
        // 彝文字符列表
        const yiChars = ['󲜐', '󲜑', '󲜒', '󲜓', '4'];
        
        // 直接显示
        const directContainer = document.getElementById('direct-chars');
        yiChars.forEach(char => {
            const div = document.createElement('div');
            div.className = 'char-box';
            div.textContent = char;
            directContainer.appendChild(div);
        });
        
        // Canvas渲染
        const canvasContainer = document.getElementById('canvas-chars');
        yiChars.forEach(char => {
            const canvas = document.createElement('canvas');
            canvas.width = 60;
            canvas.height = 60;
            canvas.className = 'canvas-box';
            
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, 60, 60);
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 2;
            ctx.strokeRect(0, 0, 60, 60);
            
            ctx.fillStyle = '#000';
            ctx.font = 'bold 24px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(char, 30, 30);
            
            canvasContainer.appendChild(canvas);
        });
    </script>
</body>
</html>
"""
    
    with open("yi_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("HTML测试页面已创建: yi_test.html")

def main():
    """主函数"""
    print("彝文字符显示测试工具")
    print("=" * 50)
    
    # 运行各种测试
    test_yi_characters()
    test_unicode_ranges()
    test_browser_compatibility()
    save_yi_char_images()
    create_html_test_page()
    
    print("\n测试完成！")
    print("请查看生成的图片和HTML文件来验证彝文字符显示。")

if __name__ == "__main__":
    main() 