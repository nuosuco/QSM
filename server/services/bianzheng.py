"""
SOM 松麦 - 辨证引擎 v2
基于规则+RAG的中医辨证分析（升级：模糊匹配+症状权重+综合分析）
"""
import json
import os
import re
from typing import Optional, List, Tuple

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shared", "knowledge")

# ========== 加载知识库数据（优先JSON文件，fallback内联数据） ==========

def _load_json(filename, default=None):
    """从shared/knowledge加载JSON，失败时返回默认值"""
    path = os.path.join(KNOWLEDGE_DIR, filename)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[警告] 加载 {filename} 失败: {e}")
    return default if default is not None else {}

# ========== 症状→证型 映射规则 v2 ==========
SYMPTOM_RULES = {
    # 核心症状列表，每个症状有多个别名/说法
    "失眠": {"aliases": ["睡不着", "入睡困难", "睡不好", "失眠多梦", "夜间醒", "半夜醒来", "睡眠差", "多梦", "睡不着觉"], "zhengxing": ["心肾不交", "肝郁化火", "心脾两虚"], "tizhi": ["阴虚质", "气郁质"], "foods": ["酸枣仁", "百合", "莲子"], "weight": 0.9},
    "口干": {"aliases": ["口渴", "口干舌燥", "喝水不解渴", "口燥"], "zhengxing": ["阴虚火旺", "胃热"], "tizhi": ["阴虚质"], "foods": ["麦冬", "百合", "银耳"], "weight": 0.7},
    "上火": {"aliases": ["上火发炎", "冒痘", "喉咙痛", "牙龈肿", "口臭", "口舌生疮"], "zhengxing": ["实热", "虚火", "肺热"], "tizhi": ["湿热质", "阴虚质"], "foods": ["菊花", "金银花", "绿豆"], "weight": 0.8},
    "疲劳": {"aliases": ["疲倦", "乏力", "没精神", "总是困", "容易累", "精神不好", "嗜睡", "倦怠"], "zhengxing": ["气虚", "脾虚湿盛"], "tizhi": ["气虚质", "痰湿质"], "foods": ["黄芪", "党参", "山药"], "weight": 0.8},
    "胃口不好": {"aliases": ["食欲差", "吃不下", "不想吃饭", "厌食", "腹胀", "胃胀", "消化不良", "没胃口"], "zhengxing": ["脾胃虚弱", "肝郁气滞", "脾虚湿盛"], "tizhi": ["气虚质", "痰湿质", "气郁质"], "foods": ["山药", "茯苓", "陈皮"], "weight": 0.8},
    "手脚冰凉": {"aliases": ["怕冷", "畏寒", "寒凉", "冷手冷脚", "冬天手脚凉", "体温偏低"], "zhengxing": ["阳虚", "寒凝血瘀"], "tizhi": ["阳虚质"], "foods": ["生姜", "红枣", "桂圆"], "weight": 0.9},
    "便秘": {"aliases": ["大便干", "排便困难", "拉不出来", "干燥", "肠道不畅"], "zhengxing": ["肠燥", "气滞", "气血不足"], "tizhi": ["阴虚质", "气郁质"], "foods": ["蜂蜜", "黑芝麻", "火麻仁"], "weight": 0.7},
    "湿气重": {"aliases": ["身体沉重", "水肿", "大便黏腻", "舌苔厚", "头面部油", "出油多", "湿气大", "体内湿重"], "zhengxing": ["脾虚湿盛", "湿热"], "tizhi": ["痰湿质", "湿热质"], "foods": ["薏米", "赤小豆", "茯苓"], "weight": 0.9},
    "眼睛干涩": {"aliases": ["眼干", "眼睛干", "眼涩", "眼睛疲劳", "视物模糊", "眼疲劳"], "zhengxing": ["肝血不足", "肝肾阴虚"], "tizhi": ["阴虚质"], "foods": ["枸杞", "菊花", "桑葚"], "weight": 0.7},
    "头晕": {"aliases": ["眩晕", "头昏", "头部发晕", "天旋地转", "站立时晕"], "zhengxing": ["气血不足", "肝阳上亢", "痰湿中阻"], "tizhi": ["气虚质", "阴虚质", "痰湿质"], "foods": ["天麻", "枸杞", "红枣"], "weight": 0.7},
    "咳嗽": {"aliases": ["干咳", "有痰咳嗽", "反复咳嗽", "嗓子痒", "气管不舒服"], "zhengxing": ["肺燥", "风寒", "肺热"], "tizhi": ["阴虚质", "气虚质"], "foods": ["川贝", "梨", "百合"], "weight": 0.7},
    "痛经": {"aliases": ["月经痛", "来姨妈疼", "经期腹痛", "经前肚子疼", "小腹冷痛"], "zhengxing": ["寒凝血瘀", "气滞血瘀"], "tizhi": ["血瘀质", "阳虚质"], "foods": ["红糖", "生姜", "当归"], "weight": 0.9},
    "掉头发": {"aliases": ["脱发", "头发掉", "发量少", "掉发严重", "头发稀疏"], "zhengxing": ["肾精不足", "血虚", "湿热"], "tizhi": ["阴虚质", "血虚", "湿热质"], "foods": ["黑芝麻", "何首乌", "核桃"], "weight": 0.8},
    "长痘": {"aliases": ["长粉刺", "脸上起痘", "青春痘", "痤疮", "满脸痘痘", "皮肤不好"], "zhengxing": ["湿热", "肺热", "内分泌失调"], "tizhi": ["湿热质"], "foods": ["金银花", "蒲公英", "绿豆"], "weight": 0.7},
    "肥胖": {"aliases": ["体重超标", "偏胖", "肚子大", "腰粗", "怎么都不瘦", "虚胖"], "zhengxing": ["脾虚痰湿", "湿热"], "tizhi": ["痰湿质", "湿热质"], "foods": ["荷叶", "山楂", "薏米"], "weight": 0.8},
    "焦虑": {"aliases": ["紧张", "心情不好", "压力大", "烦躁", "爱生气", "情绪低落", "想太多", "心慌", "闷闷不乐"], "zhengxing": ["肝郁气滞", "心肾不交", "心脾两虚"], "tizhi": ["气郁质", "阴虚质"], "foods": ["玫瑰花", "合欢花", "佛手"], "weight": 0.9},
    "胃疼": {"aliases": ["胃痛", "胃酸", "烧心", "反酸", "胃不舒服"], "zhengxing": ["脾胃虚弱", "肝胃不和", "胃热"], "tizhi": ["气虚质", "气郁质"], "foods": ["山药", "陈皮", "茯苓"], "weight": 0.8},
    "腰酸背痛": {"aliases": ["腰疼", "腰酸痛", "背部疼痛", "浑身酸", "肌肉酸痛"], "zhengxing": ["肾虚", "寒湿阻络", "气血不足"], "tizhi": ["阳虚质", "气虚质"], "foods": ["杜仲", "核桃", "枸杞"], "weight": 0.7},
    "容易感冒": {"aliases": ["抵抗力差", "经常生病", "免疫力低", "感冒频繁"], "zhengxing": ["肺气虚弱", "气虚"], "tizhi": ["气虚质", "特禀质"], "foods": ["黄芪", "山药", "白术"], "weight": 0.7},
    "皮肤过敏": {"aliases": ["过敏", "起疹子", "荨麻疹", "皮肤痒", "湿疹"], "zhengxing": ["特禀", "湿热", "风热"], "tizhi": ["特禀质", "湿热质"], "foods": ["白鲜皮", "防风", "甘草"], "weight": 0.7},
    # v3新增症状
    "耳鸣": {"aliases": ["耳朵响", "嗡嗡响", "蝉鸣", "听力下降", "耳朵嗡嗡"], "zhengxing": ["肝肾阴虚", "肾精不足", "肝阳上亢"], "tizhi": ["阴虚质", "阳虚质"], "foods": ["黑芝麻", "枸杞", "桑葚"], "weight": 0.7},
    "口苦": {"aliases": ["嘴巴苦", "早上口苦", "嘴里发苦", "苦味"], "zhengxing": ["肝胆湿热", "肝火", "胃热"], "tizhi": ["湿热质", "气郁质"], "foods": ["菊花", "金银花", "蒲公英"], "weight": 0.7},
    "打嗝": {"aliases": ["嗳气", "打嗝不停", "胃气上逆", "呃逆"], "zhengxing": ["胃气上逆", "肝胃不和", "脾胃虚弱"], "tizhi": ["气郁质", "气虚质"], "foods": ["陈皮", "生姜", "佛手"], "weight": 0.6},
    "尿频": {"aliases": ["夜尿多", "总想上厕所", "小便次数多", "频繁小便", "憋不住尿"], "zhengxing": ["肾气不固", "肾阳虚", "膀胱湿热"], "tizhi": ["阳虚质", "气虚质"], "foods": ["山药", "核桃", "枸杞"], "weight": 0.7},
    "月经不调": {"aliases": ["月经推迟", "月经提前", "经量少", "经量多", "月经紊乱", "大姨妈不准", "月经过少"], "zhengxing": ["气血不足", "肝郁气滞", "寒凝血瘀"], "tizhi": ["血瘀质", "气郁质", "气虚质"], "foods": ["当归", "红枣", "红糖"], "weight": 0.8},
    "关节疼痛": {"aliases": ["膝盖疼", "关节痛", "风湿", "关节炎", "骨头痛", "关节不舒服"], "zhengxing": ["寒湿阻络", "肝肾不足", "血瘀"], "tizhi": ["阳虚质", "血瘀质"], "foods": ["杜仲", "生姜", "核桃"], "weight": 0.7},
    "白带异常": {"aliases": ["白带多", "带下", "白带黄", "分泌物多", "白带异味"], "zhengxing": ["湿热下注", "脾虚湿盛", "肾虚带下"], "tizhi": ["湿热质", "痰湿质", "气虚质"], "foods": ["薏米", "茯苓", "山药"], "weight": 0.7},
    "气短": {"aliases": ["喘不上气", "呼吸不畅", "上气不接下气", "胸闷气短", "提不上气"], "zhengxing": ["肺气虚弱", "气虚", "心气不足"], "tizhi": ["气虚质"], "foods": ["黄芪", "党参", "山药"], "weight": 0.8},
    "面色萎黄": {"aliases": ["脸色差", "面色不好", "面色发黄", "脸色暗沉", "面无血色"], "zhengxing": ["气血不足", "脾虚", "血虚"], "tizhi": ["气虚质", "血虚"], "foods": ["红枣", "桂圆", "山药"], "weight": 0.7},
    "健忘": {"aliases": ["记性差", "记忆力下降", "丢三落四", "容易忘事", "记不住东西"], "zhengxing": ["肾精不足", "心脾两虚", "痰湿蒙窍"], "tizhi": ["气虚质", "痰湿质", "阴虚质"], "foods": ["核桃", "黑芝麻", "桂圆"], "weight": 0.7},}

# 补充症状（非标准术语）
SYNONYM_MAP = {
    "没力气": "疲劳", "没精神": "疲劳", "困": "疲劳",
    "不想吃东西": "胃口不好", "肚子胀": "胃口不好",
    "懒": "疲劳", "累": "疲劳",
    "热": "上火",
    "胃不舒服": "胃疼", "拉肚子": "湿气重",
    "睡不好": "失眠", "做梦多": "失眠",
}

# 药食同源食材库（国家卫健委目录）
YAOSHI_TONGYUAN = {
    "枸杞": {"xingwei": "甘，平", "guijing": "肝、肾经", "gongxiao": "滋补肝肾，益精明目", "jinji": "外感实热、脾虚泄泻者慎用"},
    "红枣": {"xingwei": "甘，温", "guijing": "脾、胃经", "gongxiao": "补中益气，养血安神", "jinji": "湿热体质、痰湿体质慎用"},
    "山药": {"xingwei": "甘，平", "guijing": "脾、肺、肾经", "gongxiao": "补脾养胃，生津益肺，补肾涩精", "jinji": "湿盛中满者慎用"},
    "茯苓": {"xingwei": "甘、淡，平", "guijing": "心、肺、脾、肾经", "gongxiao": "利水渗湿，健脾宁心", "jinji": "阴虚津伤者慎用"},
    "薏米": {"xingwei": "甘、淡，凉", "guijing": "脾、胃、肺经", "gongxiao": "利水渗湿，健脾止泻", "jinji": "孕妇慎用"},
    "百合": {"xingwei": "甘，寒", "guijing": "心、肺经", "gongxiao": "养阴润肺，清心安神", "jinji": "风寒咳嗽、脾胃虚寒者慎用"},
    "莲子": {"xingwei": "甘、涩，平", "guijing": "脾、肾、心经", "gongxiao": "补脾止泻，益肾涩精，养心安神", "jinji": "便秘者慎用"},
    "陈皮": {"xingwei": "苦、辛，温", "guijing": "肺、脾经", "gongxiao": "理气健脾，燥湿化痰", "jinji": "气虚、阴虚燥咳者慎用"},
    "菊花": {"xingwei": "甘、苦，微寒", "guijing": "肺、肝经", "gongxiao": "散风清热，平肝明目", "jinji": "脾胃虚寒者慎用"},
    "金银花": {"xingwei": "甘，寒", "guijing": "肺、心、胃经", "gongxiao": "清热解毒，疏散风热", "jinji": "脾胃虚寒者慎用"},
    "桂圆": {"xingwei": "甘，温", "guijing": "心、脾经", "gongxiao": "补益心脾，养血安神", "jinji": "湿热、痰火者慎用"},
    "黑芝麻": {"xingwei": "甘，平", "guijing": "肝、肾、大肠经", "gongxiao": "补肝肾，益精血，润肠燥", "jinji": "脾虚便溏者慎用"},
    "桑葚": {"xingwei": "甘、酸，寒", "guijing": "心、肝、肾经", "gongxiao": "滋阴补血，生津润燥", "jinji": "脾胃虚寒便溏者慎用"},
    "酸枣仁": {"xingwei": "甘、酸，平", "guijing": "心、肝、胆经", "gongxiao": "养心补肝，宁心安神", "jinji": "实邪郁火者慎用"},
    "麦冬": {"xingwei": "甘、微苦，微寒", "guijing": "心、肺、胃经", "gongxiao": "养阴生津，润肺清心", "jinji": "脾胃虚寒泄泻者慎用"},
    "黄芪": {"xingwei": "甘，微温", "guijing": "肺、脾经", "gongxiao": "补气升阳，固表止汗", "jinji": "表实邪盛、阴虚阳亢者慎用"},
    "党参": {"xingwei": "甘，平", "guijing": "脾、肺经", "gongxiao": "补中益气，健脾益肺", "jinji": "实证、热证者慎用"},
    "生姜": {"xingwei": "辛，微温", "guijing": "肺、脾、胃经", "gongxiao": "解表散寒，温中止呕", "jinji": "阴虚内热者慎用"},
    "山楂": {"xingwei": "酸、甘，微温", "guijing": "脾、胃、肝经", "gongxiao": "消食健胃，行气散瘀", "jinji": "胃酸过多者慎用"},
    "荷叶": {"xingwei": "苦，平", "guijing": "心、肝、脾经", "gongxiao": "清暑化湿，升发清阳", "jinji": "脾胃虚寒者慎用"},
    "玫瑰花": {"xingwei": "甘、微苦，温", "guijing": "肝、脾经", "gongxiao": "行气解郁，和血止痛", "jinji": "阴虚火旺者慎用"},
    "赤小豆": {"xingwei": "甘、酸，平", "guijing": "心、小肠经", "gongxiao": "利水消肿，解毒排脓", "jinji": "阴虚津亏者慎用"},
    "银耳": {"xingwei": "甘、淡，平", "guijing": "肺、胃、肾经", "gongxiao": "滋阴润肺，养胃生津", "jinji": "风寒咳嗽者慎用"},
    "核桃": {"xingwei": "甘，温", "guijing": "肾、肺、大肠经", "gongxiao": "补肾温肺，润肠通便", "jinji": "痰热咳嗽者慎用"},
}

# 优先从JSON加载药食同源数据（扩展版含更多食材）
_json_yaoshi = _load_json('yaoshi_tongyuan.json', {})
if _json_yaoshi:
    YAOSHI_TONGYUAN = _json_yaoshi

# 体质分类
TIZHI_LIST = [
    {"name": "平和质", "desc": "体态适中，面色润泽，精力充沛", "yangsheng": "饮食有节，起居有常"},
    {"name": "气虚质", "desc": "容易疲劳，气短懒言，容易出汗", "yangsheng": "补气健脾，多吃山药、黄芪"},
    {"name": "阳虚质", "desc": "手脚冰凉，怕冷，面色苍白", "yangsheng": "温补阳气，多吃生姜、桂圆"},
    {"name": "阴虚质", "desc": "口干咽燥，手足心热，容易失眠", "yangsheng": "滋阴润燥，多吃百合、银耳"},
    {"name": "痰湿质", "desc": "体形肥胖，腹部肥满，口黏苔腻", "yangsheng": "健脾化湿，多吃薏米、茯苓"},
    {"name": "湿热质", "desc": "面垢油光，口苦口臭，大便黏滞", "yangsheng": "清热利湿，多吃绿豆、赤小豆"},
    {"name": "血瘀质", "desc": "肤色晦暗，色素沉着，容易出现瘀斑", "yangsheng": "活血化瘀，多吃山楂、玫瑰花"},
    {"name": "气郁质", "desc": "情绪低落，多愁善感，容易紧张", "yangsheng": "疏肝解郁，多吃玫瑰花、佛手"},
    {"name": "特禀质", "desc": "过敏体质，容易哮喘、荨麻疹", "yangsheng": "益气固表，避免过敏原"},
]

# 优先从JSON加载体质分类
_json_tizhi = _load_json('tizhi.json', [])
if _json_tizhi:
    TIZHI_LIST = _json_tizhi

# 食疗方案库 v2
SHILIAO_DB = {
    "心肾不交": {"name": "安神养心粥", "recipe": "酸枣仁15g、百合10g、莲子15g、粳米100g", "method": "酸枣仁先煎20分钟取汁，加入百合、莲子、粳米同煮至粥成"},
    "肝郁化火": {"name": "玫瑰菊花茶", "recipe": "玫瑰花5朵、菊花10g、枸杞10g", "method": "沸水冲泡，代茶频饮"},
    "心脾两虚": {"name": "黄芪党参粥", "recipe": "黄芪20g、党参15g、山药20g、桂圆肉10g、粳米100g", "method": "药材先煮取汁，加入粳米和桂圆煮粥"},
    "阴虚火旺": {"name": "百合银耳羹", "recipe": "百合20g、银耳15g、麦冬10g、冰糖适量", "method": "银耳泡发后与百合、麦冬同炖至粘稠，加冰糖调味"},
    "实热": {"name": "金银花绿豆汤", "recipe": "金银花15g、绿豆100g、冰糖适量", "method": "绿豆浸泡2小时后煮至开花，加金银花再煮10分钟"},
    "虚火": {"name": "麦冬枸杞茶", "recipe": "麦冬15g、枸杞10g、菊花5g", "method": "沸水冲泡，焖10分钟后代茶饮"},
    "胃热": {"name": "竹蔗茅根水", "recipe": "竹蔗2根、茅根30g、马蹄5个", "method": "所有材料洗净切段，加水煮沸30分钟"},
    "气虚": {"name": "黄芪党参鸡汤", "recipe": "黄芪30g、党参20g、山药30g、乌鸡半只、红枣5枚", "method": "药材洗净，乌鸡焯水，同入砂锅加水慢炖2小时，调味食用"},
    "脾虚湿盛": {"name": "薏米赤小豆粥", "recipe": "薏米50g、赤小豆50g、茯苓15g、粳米50g", "method": "薏米、赤小豆提前浸泡4小时，与茯苓同煮至烂熟"},
    "脾胃虚弱": {"name": "山药茯苓粥", "recipe": "山药50g、茯苓15g、陈皮6g、粳米100g", "method": "茯苓先煎取汁，加入山药、粳米煮粥，陈皮切丝后入"},
    "肝胃不和": {"name": "陈皮生姜水", "recipe": "陈皮6g、生姜5片、红枣3枚", "method": "所有材料加水煮15分钟，趁热饮用"},
    "阳虚": {"name": "姜枣桂圆茶", "recipe": "生姜3片、红枣6枚、桂圆肉15g、红糖适量", "method": "红枣去核，与生姜、桂圆同煮20分钟，加红糖调味"},
    "寒凝血瘀": {"name": "红糖姜枣茶", "recipe": "红糖30g、生姜5片、红枣8枚、山楂10g", "method": "红枣去核，与生姜、山楂同煮15分钟，加红糖"},
    "肠燥": {"name": "蜂蜜黑芝麻糊", "recipe": "黑芝麻30g、蜂蜜2勺、糯米粉20g", "method": "黑芝麻炒香磨碎，糯米粉炒熟，混合后加蜂蜜调糊食用"},
    "气滞": {"name": "陈皮玫瑰花茶", "recipe": "陈皮6g、玫瑰花5朵、佛手片5g", "method": "沸水冲泡，焖5分钟后代茶饮"},
    "气血不足": {"name": "天麻红枣炖蛋", "recipe": "天麻10g、红枣5枚、鸡蛋1个、枸杞10g", "method": "天麻先煎30分钟取汁，打入鸡蛋，加红枣、枸杞再煮10分钟"},
    "肝阳上亢": {"name": "天麻钩藤茶", "recipe": "天麻10g、菊花10g、枸杞15g", "method": "天麻切片先煎20分钟，加入菊花、枸杞焖泡"},
    "肝血不足": {"name": "枸杞菊花决明茶", "recipe": "枸杞15g、菊花10g、决明子10g", "method": "决明子微炒后与枸杞、菊花同泡，代茶饮"},
    "痰湿中阻": {"name": "陈皮薏米茶", "recipe": "陈皮10g、薏米20g、茯苓10g", "method": "薏米提前浸泡，与陈皮、茯苓同煮30分钟"},
    "肺燥": {"name": "川贝雪梨盅", "recipe": "川贝母6g、雪梨1个、冰糖适量", "method": "雪梨去核，纳入川贝粉和冰糖，隔水蒸1小时"},
    "风寒": {"name": "生姜葱白红糖水", "recipe": "生姜5片、葱白3段、红糖30g", "method": "生姜、葱白加水煮沸5分钟，加红糖溶化后趁热饮用"},
    "肺热": {"name": "金银花杏仁茶", "recipe": "金银花10g、杏仁10g、枇杷叶10g", "method": "药材洗净加水煮沸，转小火煮15分钟，代茶饮"},
    "肾虚": {"name": "黑豆核桃浆", "recipe": "黑豆30g、核桃仁20g、黑芝麻10g", "method": "所有材料浸泡后打成浆，煮沸饮用"},
    "湿热": {"name": "蒲公英绿豆汤", "recipe": "蒲公英15g、绿豆100g、薏米30g", "method": "绿豆、薏米浸泡后煮至半熟，加蒲公英再煮15分钟"},
    "内分泌失调": {"name": "玫瑰柚子茶", "recipe": "玫瑰花5朵、柚子皮10g、蜂蜜适量", "method": "沸水冲泡，放温后加蜂蜜"},
    "特禀": {"name": "玉屏风饮", "recipe": "黄芪20g、白术10g、防风10g", "method": "加水煮沸，小火煮20分钟，分两次饮用"},
    "风热": {"name": "薄荷银花饮", "recipe": "薄荷3g、金银花10g、甘草5g", "method": "金银花、甘草先煮10分钟，关火后加入薄荷焖5分钟"},
    "肺气虚弱": {"name": "黄芪山药饮", "recipe": "黄芪20g、山药30g、党参15g", "method": "材料洗净加水煮30分钟，代茶饮"},
    # v3新增食疗
    "肝肾阴虚": {"name": "桑葚枸杞茶", "recipe": "桑葚15g、枸杞10g、菊花5g", "method": "沸水冲泡，焖10分钟", "gongxiao": "滋补肝肾，明目润燥", "jijie": "适合眼干耳鸣、腰膝酸软者"},
    "肾精不足": {"name": "黑芝麻核桃糊", "recipe": "黑芝麻50g、核桃仁30g、黑米30g", "method": "黑芝麻、核桃仁炒香，与黑米同磨成粉，冲糊食用", "gongxiao": "补肾填精，乌发润肤", "jijie": "适合脱发白发、健忘者"},
    "肝胆湿热": {"name": "茵陈车前草茶", "recipe": "茵陈15g、车前草10g、菊花10g", "method": "药材洗净，加水煮沸15分钟，代茶饮", "gongxiao": "清利肝胆湿热", "jijie": "适合口苦、小便黄者"},
    "胃气上逆": {"name": "陈皮生姜苏梗茶", "recipe": "陈皮6g、生姜5片、紫苏梗10g", "method": "沸水冲泡，焖10分钟", "gongxiao": "降逆和胃，理气止嗝", "jijie": "适合打嗝、嗳气者"},
    "肾气不固": {"name": "金樱子芡实粥", "recipe": "金樱子15g、芡实20g、山药30g、粳米100g", "method": "金樱子先煎20分钟取汁，加入芡实、山药、粳米煮粥", "gongxiao": "固肾缩尿，健脾止泻", "jijie": "适合夜尿多、腰膝酸软者"},
    "寒湿阻络": {"name": "桂枝生姜羊肉汤", "recipe": "桂枝10g、生姜10片、当归10g、羊肉500g", "method": "羊肉焯水，与药材同入砂锅加水炖2小时，调味食用", "gongxiao": "温经散寒，通络止痛", "jijie": "适合关节冷痛、得热则缓者"},
    "湿热下注": {"name": "马齿苋薏米粥", "recipe": "马齿苋30g（鲜品60g）、薏米50g、粳米50g", "method": "薏米提前浸泡，与粳米同煮至粥将成，加入马齿苋再煮10分钟", "gongxiao": "清热利湿，解毒止带", "jijie": "适合白带异常、小便黄者"},
    "心气不足": {"name": "龙眼枣仁茶", "recipe": "桂圆肉15g、酸枣仁10g、红枣5枚", "method": "酸枣仁先煎20分钟，加入桂圆、红枣再煮10分钟", "gongxiao": "补心气，安心神", "jijie": "适合心悸气短、失眠者"},
    "痰湿蒙窍": {"name": "石菖蒲陈皮茶", "recipe": "石菖蒲6g、陈皮6g、茯苓10g", "method": "药材洗净，加水煮15分钟，代茶饮", "gongxiao": "化痰开窍，醒神益智", "jijie": "适合头重昏沉、健忘者"},
}

# 优先从JSON加载食疗方案
_json_shiliao = _load_json('shiliao.json', {})
if _json_shiliao:
    SHILIAO_DB = _json_shiliao


class BianzhengEngine:
    """辨证引擎 v2 - 基于模糊匹配+权重分析的中医辨证"""

    def analyze(self, message: str) -> dict:
        """
        分析用户描述，返回辨证结果
        """
        msg = message.strip()
        if not msg:
            return self._empty_response("请描述一下你的身体状况，比如最近有什么不舒服？")

        # 输入标准化
        msg_lower = msg.lower()

        # 1. 模糊匹配症状
        matched = self._match_symptoms_smart(msg_lower)

        if not matched:
            return self._no_match_response(msg, matched)

        # 2. 综合辨证 - 按证型和体质计分
        zhengxing_scores = {}
        tizhi_scores = {}
        all_foods = []

        for m in matched:
            food_weight = m["weight"] * m["rule"]["weight"]

            # 证型评分
            for z, freq in enumerate(m["rule"]["zhengxing"]):
                if freq not in zhengxing_scores:
                    zhengxing_scores[freq] = {"score": 0, "sources": []}
                zhengxing_scores[freq]["score"] += food_weight / (z + 1)  # 排名越前分数越高
                zhengxing_scores[freq]["sources"].append(m["symptom"])

            # 体质评分
            for t, freq in enumerate(m["rule"]["tizhi"]):
                if t not in tizhi_scores:
                    tizhi_scores[freq] = {"score": 0, "sources": []}
                tizhi_scores[freq]["score"] += food_weight / (t + 1)
                tizhi_scores[freq]["sources"].append(m["symptom"])

            # 收集食材
            for f in m["rule"]["foods"]:
                if f not in all_foods:
                    all_foods.append(f)

        # 3. 排序取Top结果
        top_zhengxing = sorted(zhengxing_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:3]
        top_tizhi = sorted(tizhi_scores.items(), key=lambda x: x[1]["score"], reverse=True)[:3]

        zhengxing_str = "、".join(z[0] for z in top_zhengxing)
        tizhi_str = "、".join(t[0] for t in top_tizhi)
        foods = all_foods[:6]

        # 4. 获取食材详情
        recommendations = []
        for food in foods:
            info = YAOSHI_TONGYUAN.get(food, {})
            rec = {
                "name": food,
                "xingwei": info.get("xingwei", ""),
                "gongxiao": info.get("gongxiao", ""),
                "jinji": info.get("jinji", ""),
            }
            # 从辨证结果中找食疗方
            for zheng in top_zhengxing:
                shiliao = SHILIAO_DB.get(zheng[0])
                if shiliao and food in shiliao.get("recipe", ""):
                    rec["shiliao"] = shiliao
                    break
            recommendations.append(rec)

        # 5. 生成回复
        symptoms_str = "、".join(m["symptom"] for m in matched)
        reply = self._build_reply(msg, symptoms_str, zhengxing_str, tizhi_str, foods, recommendations, matched)

        return {
            "reply": reply,
            "tizhi": tizhi_str,
            "zhengxing": zhengxing_str,
            "recommendations": recommendations,
            "confidence": self._calc_confidence(matched),
            "matched_symptoms": [m["symptom"] for m in matched],
        }

    def _build_reply(self, msg, symptoms_str, zhengxing_str, tizhi_str, foods, recommendations, matched):
        """构建友好的辨证回复 v3 - 多样化回复模板"""
        import random
        # 提取食疗方案
        food_dishes = []
        seen_recipe = set()
        for rec in recommendations:
            shiliao = rec.get("shiliao")
            if shiliao and shiliao["name"] not in seen_recipe:
                food_dishes.append(shiliao)
                seen_recipe.add(shiliao["name"])

        # 根据症状数量选择不同的回复风格
        symptom_count = len(matched)
        
        # 开场白模板
        if symptom_count >= 3:
            opener = f"你提到的{symptoms_str}，我帮你从中医角度综合分析一下：\n\n"
        elif symptom_count >= 2:
            opener = f"听起来{symptoms_str}，从中医角度看：\n\n"
        else:
            opener = f"关于你提到的{symptoms_str}，中医是这样看的：\n\n"

        parts = [opener]
        parts.append(f"📋 **辨证方向：** {zhengxing_str}\n")
        parts.append(f"🩺 **体质偏向：** {tizhi_str}\n\n")

        if food_dishes:
            dish = food_dishes[0]
            parts.append(f"🍲 **今日推荐食疗：{dish['name']}**\n")
            parts.append(f"   配方：{dish['recipe']}\n")
            parts.append(f"   做法：{dish['method']}\n")
            if dish.get('gongxiao'):
                parts.append(f"   功效：{dish['gongxiao']}\n")
            if dish.get('jijie'):
                parts.append(f"   💡 {dish['jijie']}\n")
            parts.append("\n")

        parts.append(f"💊 **建议食用的药食同源食材：** {', '.join(foods)}\n\n")
        
        # 随机选择一句温馨提示
        tips = [
            "⚠️ 提醒：以上为养生建议，不是医疗诊断。如果症状严重或持续，请及时就医。",
            "💡 小贴士：养生贵在坚持，建议配合规律作息效果更好。",
            "🌿 记住：药补不如食补，食补不如睡补。早睡早起是最好的养生。",
            "☀️ 每天晒晒太阳（上午10点前），补充维生素D，对改善体质很有帮助。",
            "💧 每天喝够1500ml温水，小口慢饮，养胃又养颜。",
        ]
        random.seed(len(msg) + len(foods))
        parts.append(random.choice(tips))

        return "".join(parts)

    def _match_symptoms_smart(self, msg: str) -> list:
        """智能匹配症状：支持别名、同义词、模糊匹配"""
        matched = []

        # 1. 先检查直接别名/同义词映射
        checked = set()

        for keyword, rule_data in SYMPTOM_RULES.items():
            if keyword in checked:
                continue

            aliases = rule_data.get("aliases", [])

            # 直接匹配关键词
            if keyword in msg:
                matched.append({"symptom": keyword, "rule": rule_data, "weight": rule_data["weight"]})
                checked.add(keyword)
                continue

            # 匹配别名
            for alias in aliases:
                if alias in msg:
                    matched.append({"symptom": keyword, "rule": rule_data, "weight": rule_data["weight"]})
                    checked.add(keyword)
                    break

        # 2. 检查同义词映射
        for syn, target in SYNONYM_MAP.items():
            if syn in msg and target not in checked:
                # target 应该在 SYMPTOM_RULES 中有定义
                if target in SYMPTOM_RULES:
                    matched.append({
                        "symptom": target,
                        "rule": SYMPTOM_RULES[target],
                        "weight": SYMPTOM_RULES[target]["weight"],
                    })
                    checked.add(target)

        # 3. 按权重降序排列
        matched.sort(key=lambda x: x["weight"], reverse=True)

        return matched

    def _no_match_response(self, msg: str, matched: list) -> dict:
        """未匹配到症状时的友好回复"""
        suggestions = ["失眠", "疲劳", "上火", "口干", "胃口不好", "手脚冰凉", "湿气重", "焦虑", "头痛", "掉头发"]
        return {
            "reply": (
                f"你说的\"{msg}\"，我不太确定对应什么症状。\n\n"
                f"可以试试这些说法：\n• {', '.join(suggestions[:6])}\n\n"
                f"也可以多说一点细节，比如：什么时候开始的？持续多久了？有什么诱因？"
            ),
            "recommendations": [],
            "confidence": 0.0,
        }

    def _empty_response(self, text: str) -> dict:
        return {
            "reply": text,
            "recommendations": [],
            "confidence": 0.0,
        }

    def _calc_confidence(self, matched: list) -> float:
        """计算辨证置信度"""
        if not matched:
            return 0.0
        total_weight = sum(m["weight"] for m in matched)
        return min(total_weight / (len(matched) * 0.9), 1.0)

    def get_yaoshi_info(self, name: str) -> Optional[dict]:
        return YAOSHI_TONGYUAN.get(name)

    def get_tizhi_list(self) -> list:
        return TIZHI_LIST
