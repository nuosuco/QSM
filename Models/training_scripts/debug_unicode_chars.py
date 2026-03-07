#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Unicode字符范围
"""

def analyze_unicode_chars(text):
    """分析文本中的Unicode字符"""
    print(f"分析文本: {text}")
    print(f"文本长度: {len(text)}")
    
    for i, char in enumerate(text):
        try:
            unicode_val = ord(char)
            print(f"字符 {i}: '{char}' (Unicode: {unicode_val:06X})")
            
            # 检查字符类型
            if 0x1F200 <= unicode_val <= 0x1F6FF:
                print(f"  -> 彝文字符 (0x1F200-0x1F6FF)")
            elif 0x1F900 <= unicode_val <= 0x1F9FF:
                print(f"  -> 彝文字符 (0x1F900-0x1F9FF)")
            elif 0x4E00 <= unicode_val <= 0x9FFF:
                print(f"  -> 中文字符")
            elif 0x0041 <= unicode_val <= 0x005A or 0x0061 <= unicode_val <= 0x007A:
                print(f"  -> 英文字符")
            else:
                print(f"  -> 其他字符")
                
        except (TypeError, ValueError) as e:
            print(f"字符 {i}: 无法解析 - {e}")

# 测试一些示例字符
test_chars = [
    "󲜐",  # 从模型输出中看到的字符
    "󲜑",
    "󲜚",
    "󲜷",
    "󲞮",
    "󲞭",
    "󲫀"
]

print("=== Unicode字符分析 ===")
for char in test_chars:
    analyze_unicode_chars(char)
    print() 