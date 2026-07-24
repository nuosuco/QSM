"""
SOM 松麦 - 辨证引擎
基于RAG知识库的中医辨证分析
"""
import json
import os
from typing import Optional

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "shared", "knowledge")

# 症状→证型 映射规则
SYMPTOM_RULES = {
    "失眠": {"zhengxing": "心肾不交/肝郁化火", "tizhi": "阴虚质/气郁质", "foods": ["酸枣仁", "百合", "莲子"]},
    "口干": {"zhengxing": "阴虚火旺", "tizhi": "阴虚质", "foods": ["麦冬", "百合", "银耳"]},
    "上火": {"zhengxing": "实热/虚火", "tizhi": "湿热质/阴虚质", "foods": ["菊花", "金银花", "绿豆"]},
    "疲劳": {"zhengxing": "气虚", "tizhi": "气虚质", "foods": ["黄芪", "党参", "山药"]},
    "胃口不好": {"zhengxing": "脾胃虚弱", "tizhi": "气虚质/痰湿质", "foods": ["山药", "茯苓", "陈皮"]},
    "手脚冰凉": {"zhengxing": "阳虚", "tizhi": "阳虚质", "foods": ["生姜", "红枣", "桂圆"]},
    "便秘": {"zhengxing": "肠燥/气滞", "tizhi": "阴虚质/气郁质", "foods": ["蜂蜜", "黑芝麻", "火麻仁"]},
    "湿气重": {"zhengxing": "脾虚湿盛", "tizhi": "痰湿质/湿热质", "foods": ["薏米", "赤小豆", "茯苓"]},
    "眼睛干涩": {"zhengxing": "肝血不足", "tizhi": "阴虚质/血虚", "foods": ["枸杞", "菊花", "桑葚"]},
    "头晕": {"zhengxing": "气血不足/肝阳上亢", "tizhi": "气虚质/阴虚质", "foods": ["天麻", "枸杞", "红枣"]},
    "咳嗽": {"zhengxing": "肺燥/风寒", "tizhi": "阴虚质/气虚质", "foods": ["川贝", "梨", "百合"]},
    "痛经": {"zhengxing": "寒凝血瘀", "tizhi": "血瘀质/阳虚质", "foods": ["红糖", "生姜", "当归"]},
    "掉头发": {"zhengxing": "肾精不足/血虚", "tizhi": "阴虚质/血虚", "foods": ["黑芝麻", "何首乌", "核桃"]},
    "长痘": {"zhengxing": "湿热/肺热", "tizhi": "湿热质", "foods": ["金银花", "蒲公英", "绿豆"]},
    "肥胖": {"zhengxing": "脾虚痰湿", "tizhi": "痰湿质", "foods": ["荷叶", "山楂", "薏米"]},
    "焦虑": {"zhengxing": "肝郁气滞", "tizhi": "气郁质", "foods": ["玫瑰花", "合欢花", "佛手"]},
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


class BianzhengEngine:
    """辨证引擎 - 基于规则+RAG的中医辨证"""

    def analyze(self, message: str) -> dict:
        """
        分析用户描述，返回辨证结果
        """
        msg = message.strip()
        if not msg:
            return {"reply": "请描述一下你的身体状况，比如最近有什么不舒服？", "recommendations": []}

        # 1. 匹配症状
        matched = self._match_symptoms(msg)

        if not matched:
            return {
                "reply": f"你说的\u201c{msg}\u201d，我不太确定对应什么症状。可以换个说法吗？比如：失眠、疲劳、上火、口干、胃口不好等。",
                "recommendations": []
            }

        # 2. 综合辨证
        zhengxing_list = list(set(m["zhengxing"] for m in matched))
        tizhi_list_found = list(set(m["tizhi"] for m in matched))
        foods = []
        for m in matched:
            for f in m["foods"]:
                if f not in foods:
                    foods.append(f)

        # 3. 获取食材详情
        recommendations = []
        for food in foods[:5]:
            info = YAOSHI_TONGYUAN.get(food, {})
            recommendations.append({
                "name": food,
                "xingwei": info.get("xingwei", ""),
                "gongxiao": info.get("gongxiao", ""),
                "jinji": info.get("jinji", ""),
            })

        # 4. 生成回复
        symptoms_str = "、".join(m["symptom"] for m in matched)
        zhengxing_str = "、".join(zhengxing_list)
        tizhi_str = "、".join(tizhi_list_found)
        foods_str = "、".join(foods[:5])

        reply = (
            f"根据你的描述（{symptoms_str}），从中医角度看，可能属于**{zhengxing_str}**的情况，"
            f"体质偏向**{tizhi_str}**。\n\n"
            f"建议你可以适当食用以下药食同源的食材：{foods_str}。\n\n"
            f"我帮你找了一些有机认证的相关产品，你可以看看。"
            f"不过要提醒你，这些是养生建议，如果症状严重还是要去看医生哦。"
        )

        return {
            "reply": reply,
            "tizhi": tizhi_str,
            "zhengxing": zhengxing_str,
            "recommendations": recommendations,
        }

    def _match_symptoms(self, msg: str) -> list:
        """匹配用户描述中的症状"""
        matched = []
        for symptom, rule in SYMPTOM_RULES.items():
            if symptom in msg:
                matched.append({"symptom": symptom, **rule})
        return matched

    def get_yaoshi_info(self, name: str) -> Optional[dict]:
        """获取食材信息"""
        return YAOSHI_TONGYUAN.get(name)

    def get_tizhi_list(self) -> list:
        """获取体质列表"""
        return TIZHI_LIST
