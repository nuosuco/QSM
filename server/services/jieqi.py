# -*- coding: utf-8 -*-
"""
SOM 节气养生服务 - 每天提供不同内容
"""
from datetime import datetime, date
from typing import Optional
import hashlib

# 二十四节气数据
JIEQI_DATA = [
    {"name": "小寒", "month": 1, "day": 6, "season": "冬", "desc": "天渐寒尚未大冷，隆冬将至",
     "yangsheng": "温补阳气，防寒保暖。宜食羊肉、核桃、板栗、红枣。早睡晚起，避寒就温。",
     "foods": ["羊肉", "核桃", "板栗", "红枣", "桂圆", "生姜"],
     "tea": "红茶、普洱熟茶", "avoid": "生冷寒凉、过度出汗"},
    {"name": "大寒", "month": 1, "day": 20, "season": "冬", "desc": "一年中最冷的时期",
     "yangsheng": "御寒保暖，补肾藏精。宜食黑豆、黑芝麻、枸杞、山药。适当进补，为春天做准备。",
     "foods": ["黑豆", "黑芝麻", "枸杞", "山药", "糯米", "红枣"],
     "tea": "红茶、桂圆茶", "avoid": "寒凉食物、熬夜"},
    {"name": "立春", "month": 2, "day": 4, "season": "春", "desc": "春季开始，万物复苏",
     "yangsheng": "升发阳气，疏肝理气。宜食韭菜、豆芽、香椿、荠菜。多户外活动，舒展筋骨。",
     "foods": ["韭菜", "豆芽", "香椿", "荠菜", "菠菜", "枸杞"],
     "tea": "花茶、菊花茶", "avoid": "酸收太过、油腻厚重"},
    {"name": "雨水", "month": 2, "day": 19, "season": "春", "desc": "降雨开始增多，气温回升",
     "yangsheng": "健脾祛湿，调养脾胃。宜食山药、薏米、茯苓、小米。注意春捂，防倒春寒。",
     "foods": ["山药", "薏米", "茯苓", "小米", "南瓜", "红枣"],
     "tea": "陈皮茶、茯苓茶", "avoid": "生冷油腻、过度劳累"},
    {"name": "惊蛰", "month": 3, "day": 6, "season": "春", "desc": "春雷始鸣，蛰虫惊醒",
     "yangsheng": "疏肝泻火，清淡饮食。宜食梨、百合、银耳、芹菜。早睡早起，适度运动。",
     "foods": ["梨", "百合", "银耳", "芹菜", "菠菜", "菊花"],
     "tea": "菊花茶、决明子茶", "avoid": "辛辣燥热、动怒伤肝"},
    {"name": "春分", "month": 3, "day": 21, "season": "春", "desc": "昼夜平分，阴阳各半",
     "yangsheng": "调和阴阳，保持寒热均衡。宜食枸杞、桑葚、黑芝麻、核桃。心态平和，不偏不倚。",
     "foods": ["枸杞", "桑葚", "黑芝麻", "核桃", "山药", "莲子"],
     "tea": "枸杞茶、玫瑰花茶", "avoid": "大热大寒、情绪波动"},
    {"name": "清明", "month": 4, "day": 5, "season": "春", "desc": "气清景明，万物皆显",
     "yangsheng": "养肝护肝，清补为主。宜食荠菜、菠菜、绿豆、菊花。踏青郊游，舒缓心情。",
     "foods": ["荠菜", "菠菜", "绿豆", "菊花", "艾叶", "春笋"],
     "tea": "绿茶、菊花茶", "avoid": "发物（海鲜、羊肉）、悲伤忧郁"},
    {"name": "谷雨", "month": 4, "day": 20, "season": "春", "desc": "雨生百谷，春季最后一个节气",
     "yangsheng": "健脾利湿，为入夏做准备。宜食薏米、赤小豆、冬瓜、陈皮。防过敏，避风湿。",
     "foods": ["薏米", "赤小豆", "冬瓜", "陈皮", "山药", "茯苓"],
     "tea": "陈皮普洱、薏米茶", "avoid": "潮湿环境、海鲜发物"},
    {"name": "立夏", "month": 5, "day": 6, "season": "夏", "desc": "夏季开始，万物繁茂",
     "yangsheng": "养心安神，清热解暑。宜食莲子、百合、绿豆、苦瓜。午睡养心，避免大汗。",
     "foods": ["莲子", "百合", "绿豆", "苦瓜", "西瓜", "荷叶"],
     "tea": "绿茶、莲子心茶", "avoid": "贪凉饮冷、烈日暴晒"},
    {"name": "小满", "month": 5, "day": 21, "season": "夏", "desc": "麦类等夏熟作物籽粒饱满",
     "yangsheng": "清热利湿，健脾和胃。宜食冬瓜、丝瓜、绿豆、薏米。饮食清淡，防湿热。",
     "foods": ["冬瓜", "丝瓜", "绿豆", "薏米", "黄瓜", "荷叶"],
     "tea": "荷叶茶、绿豆汤", "avoid": "肥甘厚腻、辛辣燥热"},
    {"name": "芒种", "month": 6, "day": 6, "season": "夏", "desc": "有芒作物成熟，可以收割",
     "yangsheng": "清补防暑，益气生津。宜食乌梅、山楂、荷叶、薄荷。适当午休，补充水分。",
     "foods": ["乌梅", "山楂", "荷叶", "薄荷", "西瓜", "黄瓜"],
     "tea": "酸梅汤、薄荷茶", "avoid": "过度劳累、贪凉伤阳"},
    {"name": "夏至", "month": 6, "day": 21, "season": "夏", "desc": "一年中白昼最长，阳气最盛",
     "yangsheng": "养阳护阴，心静自然凉。宜食莲子、百合、银耳、鸭肉。晚睡早起，适当午休。",
     "foods": ["莲子", "百合", "银耳", "鸭肉", "绿豆", "西瓜"],
     "tea": "菊花茶、金银花茶", "avoid": "大汗伤阳、冰镇过度"},
    {"name": "小暑", "month": 7, "day": 7, "season": "夏", "desc": "天气开始炎热",
     "yangsheng": "清热生津，防暑降温。宜食莲藕、绿豆、冬瓜、荷叶。避免暴晒，及时补水。",
     "foods": ["莲藕", "绿豆", "冬瓜", "荷叶", "西瓜", "黄瓜"],
     "tea": "荷叶茶、竹叶茶", "avoid": "烈日暴晒、冷饮过度"},
    {"name": "大暑", "month": 7, "day": 23, "season": "夏", "desc": "一年中最热的时期",
     "yangsheng": "消暑化湿，益气养阴。宜食绿豆、薏米、莲子、百合。冬病夏治，适当晒背。",
     "foods": ["绿豆", "薏米", "莲子", "百合", "冬瓜", "荷叶"],
     "tea": "绿豆汤、荷叶茶", "avoid": "中暑、贪凉伤脾"},
    {"name": "立秋", "month": 8, "day": 7, "season": "秋", "desc": "秋季开始，暑去凉来",
     "yangsheng": "润燥养肺，收敛神气。宜食银耳、百合、梨、蜂蜜。早卧早起，防秋燥。",
     "foods": ["银耳", "百合", "梨", "蜂蜜", "莲藕", "山药"],
     "tea": "白茶、蜂蜜水", "avoid": "辛辣燥热、悲伤过度"},
    {"name": "处暑", "month": 8, "day": 23, "season": "秋", "desc": "暑气渐消，秋意渐浓",
     "yangsheng": "滋阴润燥，调养脾胃。宜食鸭肉、银耳、芝麻、核桃。防秋乏，适当运动。",
     "foods": ["鸭肉", "银耳", "芝麻", "核桃", "百合", "蜂蜜"],
     "tea": "乌龙茶、枸杞茶", "avoid": "贪凉、过度进补"},
    {"name": "白露", "month": 9, "day": 8, "season": "秋", "desc": "天气转凉，露凝而白",
     "yangsheng": "养肺润燥，防寒保暖。宜食梨、银耳、蜂蜜、芝麻。添衣防凉，防感冒。",
     "foods": ["梨", "银耳", "蜂蜜", "芝麻", "百合", "核桃"],
     "tea": "白茶、枸杞茶", "avoid": "寒凉食物、赤膊露体"},
    {"name": "秋分", "month": 9, "day": 23, "season": "秋", "desc": "昼夜再次平分，秋意正浓",
     "yangsheng": "阴阳平衡，收敛神气。宜食山药、莲子、红枣、芝麻。心态平和，防秋郁。",
     "foods": ["山药", "莲子", "红枣", "芝麻", "核桃", "百合"],
     "tea": "红茶、枸杞茶", "avoid": "大辛大热、情绪低落"},
    {"name": "寒露", "month": 10, "day": 8, "season": "秋", "desc": "气温更低，露水更凉",
     "yangsheng": "滋阴防燥，润肺益胃。宜食芝麻、糯米、蜂蜜、乳品。足部保暖，防寒气。",
     "foods": ["芝麻", "糯米", "蜂蜜", "核桃", "板栗", "红枣"],
     "tea": "红茶、桂圆茶", "avoid": "辛辣刺激、受凉感冒"},
    {"name": "霜降", "month": 10, "day": 23, "season": "秋", "desc": "天气渐冷，开始有霜",
     "yangsheng": "补益脾胃，为冬藏做准备。宜食柿子、萝卜、牛肉、山药。适当进补，防关节病。",
     "foods": ["柿子", "萝卜", "山药", "板栗", "核桃", "红枣"],
     "tea": "红茶、普洱熟茶", "avoid": "寒凉生冷、过度疲劳"},
    {"name": "立冬", "month": 11, "day": 7, "season": "冬", "desc": "冬季开始，万物收藏",
     "yangsheng": "温补阳气，补肾藏精。宜食羊肉、核桃、板栗、黑芝麻。早睡晚起，避寒保暖。",
     "foods": ["羊肉", "核桃", "板栗", "黑芝麻", "红枣", "桂圆"],
     "tea": "红茶、姜枣茶", "avoid": "生冷寒凉、过度出汗"},
    {"name": "小雪", "month": 11, "day": 22, "season": "冬", "desc": "开始降雪，气温下降",
     "yangsheng": "温阳补肾，防寒保暖。宜食黑豆、黑芝麻、核桃、羊肉。适当运动，防抑郁。",
     "foods": ["黑豆", "黑芝麻", "核桃", "羊肉", "红枣", "桂圆"],
     "tea": "红茶、桂圆红枣茶", "avoid": "寒凉食物、久坐不动"},
    {"name": "大雪", "month": 12, "day": 7, "season": "冬", "desc": "降雪量增大，天气更冷",
     "yangsheng": "温补不燥，养阴藏阳。宜食枸杞、山药、羊肉、核桃。泡脚驱寒，早睡晚起。",
     "foods": ["枸杞", "山药", "羊肉", "核桃", "板栗", "红枣"],
     "tea": "红茶、枸杞茶", "avoid": "大汗伤阳、寒凉饮食"},
    {"name": "冬至", "month": 12, "day": 22, "season": "冬", "desc": "一年中白昼最短，阴极阳生",
     "yangsheng": "补肾壮阳，滋阴填精。宜食羊肉、核桃、黑芝麻、枸杞。冬至进补，开春打虎。",
     "foods": ["羊肉", "核桃", "黑芝麻", "枸杞", "山药", "红枣"],
     "tea": "红茶、姜枣茶", "avoid": "生冷寒凉、熬夜伤阳"},
]

def get_current_jieqi(dt=None):
    """获取当前节气"""
    if dt is None:
        dt = datetime.now()
    month, day = dt.month, dt.day

    current = None
    next_jq = None
    for i, jq in enumerate(JIEQI_DATA):
        jq_date = date(dt.year, jq["month"], jq["day"])
        next_date = date(dt.year, JIEQI_DATA[(i + 1) % 24]["month"], JIEQI_DATA[(i + 1) % 24]["day"])
        if next_date < jq_date:
            next_date = date(dt.year + 1, next_date.month, next_date.day)
        if jq_date <= dt.date() < next_date:
            current = jq
            next_jq = JIEQI_DATA[(i + 1) % 24]
            break

    if not current:
        current = JIEQI_DATA[-1]
        next_jq = JIEQI_DATA[0]

    return {"current": current, "next": next_jq}

def get_daily_content(dt=None):
    """获取每天不同的内容（基于日期哈希）"""
    if dt is None:
        dt = datetime.now()
    
    # 使用日期哈希生成不同的内容变体
    date_str = dt.strftime("%Y%m%d")
    hash_val = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    variant = hash_val % 4  # 4种变体
    
    jieqi = get_current_jieqi(dt)
    jq = jieqi["current"]
    
    # 根据变体返回不同的重点
    variants = [
        {"focus": "饮食调理", "detail": jq["foods"][0:2]},
        {"focus": "穴位保健", "detail": ["足三里", "三阴交"]},
        {"focus": "作息调整", "detail": ["早睡早起", "适当午休"]},
        {"focus": "情志调摄", "detail": ["心态平和", "避免忧思"]},
    ]
    
    selected = variants[variant]
    
    return {
        "jieqi": jq["name"],
        "season": jq["season"],
        "desc": jq["desc"],
        "yangsheng": jq["yangsheng"],
        "foods": jq["foods"],
        "tea": jq["tea"],
        "avoid": jq["avoid"],
        "next_jieqi": jieqi["next"]["name"],
        "next_date": f"{jieqi['next']['month']}月{jieqi['next']['day']}日",
        "daily_focus": selected["focus"],
        "daily_detail": selected["detail"],
        "variant": variant,
    }

def get_jieqi_advice(dt=None):
    """获取当前节气的养生建议"""
    result = get_daily_content(dt)
    return result
