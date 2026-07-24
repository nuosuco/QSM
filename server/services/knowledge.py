"""
SOM 松麦 - 知识库服务
提供药食同源、体质分类、食疗方案查询
"""
import json
import os
from typing import Optional, List

# 从辨证引擎导入基础数据
from services.bianzheng import YAOSHI_TONGYUAN, TIZHI_LIST, SYMPTOM_RULES

# 食疗方案库
SHILIAO_DB = {
    "心肾不交": {
        "name": "安神养心粥",
        "recipe": "酸枣仁15g、百合10g、莲子15g、粳米100g",
        "method": "酸枣仁先煎20分钟取汁，加入百合、莲子、粳米同煮至粥成",
        "gongxiao": "养心安神，交通心肾",
        "jijie": "适合失眠多梦、心悸不安者"
    },
    "肝郁化火": {
        "name": "玫瑰菊花茶",
        "recipe": "玫瑰花5朵、菊花10g、枸杞10g",
        "method": "沸水冲泡，代茶频饮",
        "gongxiao": "疏肝清热，明目安神",
        "jijie": "适合烦躁易怒、失眠者"
    },
    "阴虚火旺": {
        "name": "百合银耳羹",
        "recipe": "百合20g、银耳15g、麦冬10g、冰糖适量",
        "method": "银耳泡发后与百合、麦冬同炖至粘稠，加冰糖调味",
        "gongxiao": "滋阴降火，润燥安神",
        "jijie": "适合口干咽燥、五心烦热者"
    },
    "实热": {
        "name": "金银花绿豆汤",
        "recipe": "金银花15g、绿豆100g、冰糖适量",
        "method": "绿豆浸泡2小时后煮至开花，加金银花再煮10分钟",
        "gongxiao": "清热解毒，降火除烦",
        "jijie": "适合口舌生疮、咽喉肿痛者"
    },
    "虚火": {
        "name": "麦冬枸杞茶",
        "recipe": "麦冬15g、枸杞10g、菊花5g",
        "method": "沸水冲泡，焖10分钟后代茶饮",
        "gongxiao": "滋阴清热，养肝明目",
        "jijie": "适合虚火上炎、眼干口苦者"
    },
    "气虚": {
        "name": "黄芪党参鸡汤",
        "recipe": "黄芪30g、党参20g、山药30g、乌鸡半只、红枣5枚",
        "method": "药材洗净，乌鸡焯水，同入砂锅加水慢炖2小时，调味食用",
        "gongxiao": "补气健脾，增强体力",
        "jijie": "适合气短乏力、容易疲劳者"
    },
    "脾胃虚弱": {
        "name": "山药茯苓粥",
        "recipe": "山药50g（鲜品100g）、茯苓15g、陈皮6g、粳米100g",
        "method": "茯苓先煎取汁，加入山药、粳米煮粥，陈皮切丝后入",
        "gongxiao": "健脾益气，和胃消食",
        "jijie": "适合食欲不振、腹胀便溏者"
    },
    "阳虚": {
        "name": "姜枣桂圆茶",
        "recipe": "生姜3片、红枣6枚、桂圆肉15g、红糖适量",
        "method": "红枣去核，与生姜、桂圆同煮20分钟，加红糖调味",
        "gongxiao": "温阳散寒，暖身养血",
        "jijie": "适合畏寒怕冷、手脚冰凉者"
    },
    "肠燥": {
        "name": "蜂蜜黑芝麻糊",
        "recipe": "黑芝麻30g、蜂蜜2勺、糯米粉20g",
        "method": "黑芝麻炒香磨碎，糯米粉炒熟，混合后加蜂蜜调糊食用",
        "gongxiao": "润肠通便，滋养肝肾",
        "jijie": "适合大便干结、皮肤干燥者"
    },
    "气滞": {
        "name": "陈皮玫瑰花茶",
        "recipe": "陈皮6g、玫瑰花5朵、佛手片5g",
        "method": "沸水冲泡，焖5分钟后代茶饮",
        "gongxiao": "理气解郁，和胃消胀",
        "jijie": "适合胸闷腹胀、嗳气者"
    },
    "脾虚湿盛": {
        "name": "薏米赤小豆粥",
        "recipe": "薏米50g、赤小豆50g、茯苓15g、粳米50g",
        "method": "薏米、赤小豆提前浸泡4小时，与茯苓同煮至烂熟",
        "gongxiao": "健脾祛湿，利水消肿",
        "jijie": "适合身体困重、水肿、大便黏腻者"
    },
    "肝血不足": {
        "name": "枸杞菊花决明茶",
        "recipe": "枸杞15g、菊花10g、决明子10g",
        "method": "决明子微炒后与枸杞、菊花同泡，代茶饮",
        "gongxiao": "养肝明目，润肠通便",
        "jijie": "适合眼睛干涩、视物模糊者"
    },
    "气血不足": {
        "name": "天麻红枣炖蛋",
        "recipe": "天麻10g、红枣5枚、鸡蛋1个、枸杞10g",
        "method": "天麻先煎30分钟取汁，打入鸡蛋，加红枣、枸杞再煮10分钟",
        "gongxiao": "益气养血，熄风止眩",
        "jijie": "适合头晕目眩、面色萎黄者"
    },
    "肝阳上亢": {
        "name": "天麻钩藤茶",
        "recipe": "天麻10g、菊花10g、枸杞15g",
        "method": "天麻切片先煎20分钟，加入菊花、枸杞焖泡",
        "gongxiao": "平肝潜阳，清热明目",
        "jijie": "适合头痛眩晕、面红目赤者"
    },
    "肺燥": {
        "name": "川贝雪梨盅",
        "recipe": "川贝母6g（研粉）、雪梨1个、冰糖适量",
        "method": "雪梨去核，纳入川贝粉和冰糖，隔水蒸1小时",
        "gongxiao": "润肺止咳，清热化痰",
        "jijie": "适合干咳少痰、咽干声哑者"
    },
    "风寒": {
        "name": "生姜葱白红糖水",
        "recipe": "生姜5片、葱白3段、红糖30g",
        "method": "生姜、葱白加水煮沸5分钟，加红糖溶化后趁热饮用",
        "gongxiao": "散寒解表，温中止咳",
        "jijie": "适合咳嗽痰白、鼻塞流清涕者"
    },
    "寒凝血瘀": {
        "name": "红糖姜枣茶",
        "recipe": "红糖30g、生姜5片、红枣8枚、山楂10g",
        "method": "红枣去核，与生姜、山楂同煮15分钟，加红糖",
        "gongxiao": "温经散寒，活血止痛",
        "jijie": "适合经前或经期小腹冷痛者"
    },
    "肾精不足": {
        "name": "黑芝麻核桃糊",
        "recipe": "黑芝麻50g、核桃仁30g、黑米30g",
        "method": "黑芝麻、核桃仁炒香，与黑米同磨成粉，冲糊食用",
        "gongxiao": "补肾填精，乌发润肤",
        "jijie": "适合脱发白发、腰膝酸软者"
    },
    "血虚": {
        "name": "红枣桂圆枸杞茶",
        "recipe": "红枣8枚、桂圆肉15g、枸杞15g、红糖适量",
        "method": "红枣去核，与桂圆、枸杞同煮20分钟，加红糖",
        "gongxiao": "补血养心，润泽容颜",
        "jijie": "适合面色苍白、心悸失眠者"
    },
    "湿热": {
        "name": "蒲公英绿豆汤",
        "recipe": "蒲公英15g、绿豆100g、薏米30g",
        "method": "绿豆、薏米浸泡后煮至半熟，加蒲公英再煮15分钟",
        "gongxiao": "清热利湿，解毒消痘",
        "jijie": "适合面部油腻、痤疮反复者"
    },
    "肺热": {
        "name": "金银花杏仁茶",
        "recipe": "金银花10g、杏仁10g、枇杷叶10g",
        "method": "药材洗净加水煮沸，转小火煮15分钟，代茶饮",
        "gongxiao": "清肺泄热，化痰消痤",
        "jijie": "适合痘痘红肿、便秘口臭者"
    },
    "脾虚痰湿": {
        "name": "荷叶山楂茶",
        "recipe": "荷叶10g、山楂15g、陈皮6g、决明子10g",
        "method": "药材洗净，沸水冲泡焖15分钟，代茶频饮",
        "gongxiao": "健脾化浊，消脂减重",
        "jijie": "适合体胖困重、血脂偏高者"
    },
    "肝郁气滞": {
        "name": "玫瑰合欢解郁茶",
        "recipe": "玫瑰花5朵、合欢花5g、佛手片5g、薄荷3g",
        "method": "沸水冲泡，焖5分钟后代茶饮，可加蜂蜜调味",
        "gongxiao": "疏肝解郁，安神定志",
        "jijie": "适合情绪低落、胸闷叹息者"
    },
}


class KnowledgeService:
    """知识库查询服务"""

    def get_yaoshi_list(self) -> dict:
        """获取药食同源食材库"""
        return {
            "total": len(YAOSHI_TONGYUAN),
            "source": "国家卫健委药食同源目录",
            "items": YAOSHI_TONGYUAN
        }

    def get_tizhi_list(self) -> dict:
        """获取九种体质分类"""
        return {
            "total": len(TIZHI_LIST),
            "source": "中医体质分类与判定（中华中医药学会标准）",
            "items": TIZHI_LIST
        }

    def get_shiliao(self, zhengxing: Optional[str] = None) -> dict:
        """
        获取食疗方案
        zhengxing: 证型名称，为空则返回全部
        """
        if zhengxing:
            # 模糊匹配证型
            results = {}
            for key, value in SHILIAO_DB.items():
                if key in zhengxing or zhengxing in key:
                    results[key] = value
            return {
                "zhengxing": zhengxing,
                "total": len(results),
                "items": results
            }
        return {
            "total": len(SHILIAO_DB),
            "items": SHILIAO_DB
        }

    def get_shiliao_by_symptom(self, symptom: str) -> Optional[dict]:
        """根据症状查找对应食疗方案"""
        rule = SYMPTOM_RULES.get(symptom)
        if rule:
            zhengxing = rule["zhengxing"]
            return self.get_shiliao(zhengxing)
        return None
