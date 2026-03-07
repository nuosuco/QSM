#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试彝文输入检测功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'QSM', 'src'))

from qsm_yi_wen_service import QsmYiWenChatbot

def test_yi_input_detection():
    """测试彝文输入检测"""
    print("=== 彝文输入检测测试 ===")
    
    # 初始化聊天机器人
    chatbot = QsmYiWenChatbot(model_dir="Models/QSM/bin")
    
    # 测试用例
    test_cases = [
        "你好",  # 普通中文
        "请用彝文回答",  # 关键词
        "󲜐󲜑󲜒",  # 彝文字符
        "中文：陷害 彝文：",  # 混合输入
        "翻译成彝文：兔子",  # 翻译请求
        "󲜐你好",  # 彝文+中文混合
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. 输入: {test_input}")
        response = chatbot.generate_response(test_input)
        print(f"   输出: {response}")
        
        # 检查是否包含彝文字符
        yi_chars = []
        for char in response:
            try:
                if len(char) == 1 and (0xF0000 <= ord(char) <= 0xFFFFF):
                    yi_chars.append(char)
            except (TypeError, ValueError):
                continue
        
        if yi_chars:
            print(f"   ✓ 包含彝文字符: {len(yi_chars)} 个")
        else:
            print("   ✗ 未生成彝文字符")

if __name__ == "__main__":
    test_yi_input_detection() 