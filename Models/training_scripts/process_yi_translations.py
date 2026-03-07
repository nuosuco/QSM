#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
滇川黔贵通用彝文三语对照表生成脚本
Process Yi Script (Dian-Chuan-Qian-Gui) Characters with English Translations
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

class YiTranslationProcessor:
    def __init__(self):
        self.translation_dict = {
            # 基础动词
            "舔": "lick",
            "卷": "curl, roll",
            "埋怨": "complain, blame",
            "裱褙": "mount, frame",
            "分开": "separate, part",
            "绊": "trip, stumble",
            "指": "point, indicate",
            "指向": "point to, direct",
            "包": "pack, wrap",
            "扎": "tie, bind",
            "爬": "crawl, climb",
            "攀": "climb, scale",
            "登": "ascend, mount",
            "飘": "float, drift",
            "惊": "startle, shock",
            "翻": "turn over, flip",
            "爆": "burst, explode",
            "逃": "escape, flee",
            "唱": "sing",
            "熄灭": "extinguish",
            "缝": "sew, stitch",
            "开辟": "open up, develop",
            "咳": "cough",
            "供奉": "offer, worship",
            "计较": "argue, care about",
            "靠": "lean, depend on",
            "选择": "choose, select",
            "蠕动": "wriggle, crawl",
            "钻": "drill, bore",
            "穿": "pierce, penetrate",
            "制度": "system, institution",
            "玩": "play",
            "耍": "play, fool around",
            "摇动": "shake, rock",
            "锯": "saw, cut",
            "割": "cut, reap",
            "蹲": "squat, crouch",
            "晒": "dry in sun, expose",
            "行走": "walk, travel",
            "承受": "bear, endure",
            "开": "drive, operate",
            "耕": "plow, cultivate",
            "叛": "rebel, betray",
            "萌": "sprout, bud",
            "流": "flow, stream",
            "起": "rise, get up",
            "歧视": "discriminate",
            "鄙视": "despise, look down",
            "传递": "pass, transmit",
            "恨": "hate, resent",
            "添补": "add, supplement",
            "增添": "add, increase",
            "搂": "embrace, hug",
            "小跑": "trot, jog",
            "慢跑": "jog slowly",
            "向后仰": "lean back",
            "吃草": "graze",
            "升": "rise, ascend",
            "悬挂": "hang, suspend",
            "连接": "connect, link",
            "凑在一起": "gather together",
            "穿衣": "dress, wear clothes",
            "下": "descend, go down",
            "降": "fall, drop",
            "抵": "resist, support",
            "顶": "top, support",
            "撑": "prop up, support",
            "支持": "support",
            "争夺": "compete, fight for",
            "歪曲": "distort, twist",
            "埋": "bury",
            "葬": "bury, inter",
            "晃荡": "sway, rock",
            "产生": "produce, generate",
            "缝": "sew, stitch",
            "涂": "apply, smear",
            "抹": "wipe, apply",
            "敷": "apply, spread",
            "脱": "shed, fall off",
            "落": "fall, drop",
            "跟": "follow",
            "随": "follow, accompany",
            "伴": "accompany",
            "相信": "believe, trust",
            "沾": "stick to, get stained",
            "拧": "twist, wring",
            "扭": "twist, turn",
            "祷告": "pray",
            
            # 基础名词
            "陷害": "frame, trap, set up",
            "兔子": "rabbit",
            "便宜": "cheap, inexpensive",
            "木": "wood",
            "渣": "dregs, residue",
            "尾": "tail",
            "末": "end, tip",
            "雪": "snow",
            "舌": "tongue",
            "人": "person, people",
            "物": "object, thing",
            "这里": "here",
            "惊恐": "terror, panic",
            "禁闭": "confinement, detention",
            "八角": "star anise",
            "幼": "young, juvenile",
            "膨胀": "expansion, swelling",
            "高祖": "great-grandfather",
            "象声词": "onomatopoeia",
            "枪弹": "bullet",
            "宝剑": "precious sword",
            "兄弟": "brother",
            "长者": "elder",
            "大": "big, large",
            "马": "horse",
            "火": "fire",
            "篾箩": "bamboo basket",
            "乾坤": "heaven and earth",
            "宇宙": "universe",
            "空间": "space",
            "地名": "place name",
            "人名": "person name",
            "地": "place, location",
            "区": "district, area",
            "心": "heart, mind",
            "股": "strand, share",
            "语气助词": "modal particle",
            "笑声": "laughter",
            "灰": "ash, gray",
            "色": "color",
            "胛骨": "shoulder blade",
            "锄头": "hoe",
            "草": "grass",
            "蝙蝠": "bat",
            "眼": "eye",
            "钹": "cymbal",
            "匪": "bandit",
            "研究": "research",
            "商议": "discuss, negotiate",
            "下方": "below, underneath",
            "惬意草": "pleasant grass",
            "土蚕子": "earthworm",
            "白杨树": "poplar tree",
            "鹰": "eagle",
            "管": "tube, pipe",
            "筒": "tube, cylinder",
            "右": "right",
            "凹": "concave",
            "笔管草": "horsetail grass",
            "绵羊": "sheep",
            "毛": "hair, wool",
            "棉": "cotton",
            "野葱": "wild onion",
            "苦蒜": "bitter garlic",
            "松球": "pine cone",
            "葵花": "sunflower",
            "麻": "hemp, numb",
            "纱": "gauze, yarn",
            "线": "thread, line",
            "额头": "forehead",
            "土茯苓": "smilax",
            "庄稼": "crops",
            "古语": "ancient saying",
            "粉": "powder",
            "末": "powder, end",
            "面": "flour, noodles",
            "稗": "barnyard grass",
            "流": "flow, stream",
            "星": "star",
            "豹": "leopard",
            "狼": "wolf",
            "光": "light",
            "山楂鸟": "hawthorn bird",
            "手": "hand",
            "镯": "bracelet",
            "蜘蛛": "spider",
            "纽扣": "button",
            "蒿枝": "wormwood branch",
            "水蒸气": "steam, water vapor",
            "犀": "rhinoceros",
            "牛": "cow, ox",
            "箍": "hoop, ring",
            "沉淀物": "sediment",
            "雄性": "male",
            "禽类": "poultry, birds",
            "墙": "wall",
            "君": "lord, ruler",
            "条": "strip, item",
            "牛犁": "ox plow",
            "担": "shoulder pole",
            "牲畜": "livestock",
            "野外": "outdoors, wild",
            "谎": "lie, falsehood",
            "甲": "armor, first",
            "天干": "heavenly stem",
            "镰刀": "sickle",
            "边": "edge, side",
            "方": "square, direction",
            "面": "face, surface",
            "颊": "cheek",
            "天": "sky, heaven",
            "王": "king",
            "蚱蜢": "grasshopper",
            "板栗": "chestnut",
            "二": "two",
            "十": "ten",
            "晴": "sunny, clear",
            "太阳神": "sun god",
            "他们": "they, them",
            "领导": "leader",
            "丛": "cluster, grove",
            "簇": "cluster, bunch",
            "蛾子": "moth",
            "兄": "elder brother",
            "祖母": "grandmother",
            "奶奶": "grandma",
            "壬": "ninth heavenly stem",
            "魔芋": "konjac",
            "火草": "fire grass",
            "酒": "wine, alcohol",
            "泥巴": "mud",
            
            # 形容词
            "锐利": "sharp, keen",
            "特地": "specially",
            "专门": "specifically",
            "熟": "cooked, ripe",
            "透": "through, thorough",
            "焦": "charred, burnt",
            "干": "dry",
            "脆": "crisp, brittle",
            "总是": "always",
            "斜": "oblique, slanted",
            "认真": "serious, earnest",
            "丰盛": "abundant, rich",
            "像": "like, similar",
            "相同": "same, identical",
            "松弛": "loose, relaxed",
            "轻快": "light, quick",
            "成活": "survive, take root",
            "溜": "slip, slide",
            "滑": "smooth, slippery",
            "稳当": "steady, stable",
            "清洁": "clean, sanitary",
            "连续不断": "continuous",
            "笑呵呵": "laughing happily",
            "手": "hand",
            "巧": "skillful, clever",
            "人多": "crowded",
            "拥挤": "crowded",
            "重叠": "overlapping",
            "麻木": "numb, insensitive",
            "和睦": "harmonious",
            "友好": "friendly",
            "爱好": "hobby, interest",
            "果断": "decisive, resolute",
            "害羞": "shy, bashful",
            "单": "single, alone",
            "独": "alone, solitary",
            "纯净": "pure, clean",
            "络绎不绝": "in endless stream",
            "宽": "wide, broad",
            "幼": "young",
            "寒": "cold",
            "冷": "cold",
            "失望": "disappointed",
            
            # 量词和其他
            "一": "one",
            "二": "two",
            "三": "three",
            "四": "four",
            "五": "five",
            "六": "six",
            "七": "seven",
            "八": "eight",
            "九": "nine",
            "十": "ten",
            "百": "hundred",
            "千": "thousand",
            "万": "ten thousand",
            
            # 抽象概念
            "意识": "consciousness",
            "智慧": "wisdom",
            "觉醒": "awakening",
            "状态": "state, condition",
            "系统": "system",
            "内核": "kernel, core",
            "进程": "process",
            "内存": "memory",
            "文件": "file",
            "硬件": "hardware",
            "平等": "equality",
            "分配": "distribution",
            "经济": "economy",
            "资源": "resource",
            "共享": "sharing",
            "调度": "scheduling",
            "函数": "function",
            "变量": "variable",
            "返回": "return",
            "如果": "if",
            "否则": "else",
            "循环": "loop",
            "类型": "type",
            "类": "class",
            "通信": "communication",
            "网络": "network",
            "协调": "coordination",
            "分布": "distribution",
            "连接": "connection",
            "反省": "reflection",
            "监控": "monitoring",
            "优化": "optimization",
            "反馈": "feedback",
            "学习": "learning",
        }
        
        # 特殊句式翻译
        self.pattern_translations = {
            r"1、(.+?)；2、(.+?)": r"1. \1; 2. \2",
            r"（(.+?)）(.+?)": r"(\1) \2",
            r"(.+?)（(.+?)）": r"\1 (\2)",
            r"、": ", ",
            r"；": "; ",
        }
    
    def translate_chinese_to_english(self, chinese_text: str) -> str:
        """将中文翻译为英文"""
        # 先处理特殊句式
        english_text = chinese_text
        for pattern, replacement in self.pattern_translations.items():
            english_text = re.sub(pattern, replacement, english_text)
        
        # 处理标点符号
        english_text = english_text.replace("，", ", ")
        english_text = english_text.replace("。", ".")
        english_text = english_text.replace("？", "?")
        english_text = english_text.replace("！", "!")
        
        # 查找词典中的翻译
        for chinese_word, english_word in self.translation_dict.items():
            if chinese_word in english_text:
                english_text = english_text.replace(chinese_word, english_word)
        
        return english_text
    
    def process_jsonl_file(self, input_file: str, output_file: str) -> None:
        """处理JSONL文件，为每个条目添加英文翻译"""
        processed_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                try:
                    # 解析JSON行
                    data = json.loads(line.strip())
                    
                    # 提取彝文字符和中文翻译
                    yi_char = data['messages'][0]['content']
                    chinese_translation = data['messages'][1]['content']
                    
                    # 生成英文翻译
                    english_translation = self.translate_chinese_to_english(chinese_translation)
                    
                    # 创建三语对照条目
                    trilingual_entry = {
                        "messages": [
                            {"role": "user", "content": yi_char},
                            {"role": "assistant", "content": f"{chinese_translation} | {english_translation}"}
                        ],
                        "foreignKey": f"trilingual_yi_{line_num}",
                        "metadata": {
                            "yi_character": yi_char,
                            "chinese": chinese_translation,
                            "english": english_translation,
                            "script_type": "滇川黔贵通用彝文",
                            "source_line": line_num
                        }
                    }
                    
                    # 写入输出文件
                    outfile.write(json.dumps(trilingual_entry, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                    # 进度提示
                    if processed_count % 500 == 0:
                        print(f"已处理 {processed_count} 个字符...")
                        
                except json.JSONDecodeError:
                    print(f"警告：第 {line_num} 行JSON格式错误，跳过")
                    continue
                except Exception as e:
                    print(f"警告：处理第 {line_num} 行时出错：{e}")
                    continue
        
        print(f"处理完成！共处理 {processed_count} 个滇川黔贵通用彝文字符")
    
    def create_vocabulary_summary(self, jsonl_file: str, summary_file: str) -> None:
        """创建词汇表摘要"""
        vocabulary_stats = {
            "总字符数": 0,
            "字符类别": {
                "动词": 0,
                "名词": 0,
                "形容词": 0,
                "数词": 0,
                "语气词": 0,
                "其他": 0
            },
            "翻译质量": {
                "完整翻译": 0,
                "部分翻译": 0,
                "需要人工审核": 0
            },
            "示例字符": []
        }
        
        with open(jsonl_file, 'r', encoding='utf-8') as infile:
            for line_num, line in enumerate(infile, 1):
                try:
                    data = json.loads(line.strip())
                    yi_char = data['metadata']['yi_character']
                    chinese = data['metadata']['chinese']
                    english = data['metadata']['english']
                    
                    vocabulary_stats["总字符数"] += 1
                    
                    # 添加前50个字符作为示例
                    if line_num <= 50:
                        vocabulary_stats["示例字符"].append({
                            "彝文": yi_char,
                            "中文": chinese,
                            "英文": english
                        })
                    
                    # 简单分类（可以进一步完善）
                    if any(word in chinese for word in ["动词", "、", "1、", "2、"]):
                        vocabulary_stats["字符类别"]["动词"] += 1
                    elif any(word in chinese for word in ["名词", "子", "头", "草", "树"]):
                        vocabulary_stats["字符类别"]["名词"] += 1
                    elif any(word in chinese for word in ["形容词", "的", "好", "大", "小"]):
                        vocabulary_stats["字符类别"]["形容词"] += 1
                    elif any(word in chinese for word in ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]):
                        vocabulary_stats["字符类别"]["数词"] += 1
                    elif any(word in chinese for word in ["语气", "助词", "词"]):
                        vocabulary_stats["字符类别"]["语气词"] += 1
                    else:
                        vocabulary_stats["字符类别"]["其他"] += 1
                    
                    # 评估翻译质量
                    if len(english) > 10 and not english.startswith(chinese):
                        vocabulary_stats["翻译质量"]["完整翻译"] += 1
                    elif len(english) > 3:
                        vocabulary_stats["翻译质量"]["部分翻译"] += 1
                    else:
                        vocabulary_stats["翻译质量"]["需要人工审核"] += 1
                        
                except Exception as e:
                    continue
        
        # 写入摘要文件
        with open(summary_file, 'w', encoding='utf-8') as outfile:
            json.dump(vocabulary_stats, outfile, ensure_ascii=False, indent=2)
        
        print(f"词汇表摘要已保存到：{summary_file}")
        print(f"总字符数：{vocabulary_stats['总字符数']}")
        print(f"完整翻译：{vocabulary_stats['翻译质量']['完整翻译']}")

def main():
    """主函数"""
    processor = YiTranslationProcessor()
    
    # 文件路径 (相对于当前脚本位置)
    data_dir = "../training_data/datasets/yi_wen"
    input_file = f"{data_dir}/通用彝文彝汉对照训练表(2.0.4.22).jsonl"
    output_file = f"{data_dir}/滇川黔贵通用彝文三语对照表.jsonl"
    summary_file = f"{data_dir}/滇川黔贵通用彝文词汇表摘要.json"
    
    print("开始处理滇川黔贵通用彝文字符...")
    print(f"输入文件：{input_file}")
    print(f"输出文件：{output_file}")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在")
        return
    
    # 处理JSONL文件
    processor.process_jsonl_file(input_file, output_file)
    
    # 创建词汇表摘要
    processor.create_vocabulary_summary(output_file, summary_file)
    
    print("处理完成！")
    print(f"✓ 三语对照表：{output_file}")
    print(f"✓ 词汇表摘要：{summary_file}")

if __name__ == "__main__":
    main() 