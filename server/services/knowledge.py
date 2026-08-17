"""
SOM 松麦 - 知识库服务
提供药食同源、体质分类、食疗方案查询
"""
import json
import os
from typing import Optional, List

# 从辨证引擎导入基础数据（含JSON加载的fallback机制）
from services.bianzheng import YAOSHI_TONGYUAN, TIZHI_LIST, SYMPTOM_RULES, SHILIAO_DB


class KnowledgeService:
    """知识库查询服务"""

    def get_yaoshi_list(self) -> dict:
        """获取药食同源食材库（返回列表格式，方便前端展示）"""
        items = []
        for name, info in YAOSHI_TONGYUAN.items():
            items.append({
                "name": name,
                "xingwei": info.get("xingwei", ""),
                "guijing": info.get("guijing", ""),
                "gongxiao": info.get("gongxiao", ""),
                "jinji": info.get("jinji", ""),
            })
        return {
            "total": len(items),
            "source": "国家卫健委药食同源目录",
            "items": items
        }

    def get_tizhi_list(self) -> dict:
        """获取九种体质分类"""
        enhanced_list = []
        for t in TIZHI_LIST:
            enhanced_list.append({
                "name": t.get("name", ""),
                "desc": t.get("desc", ""),
                "features": t.get("desc", ""),
                "diet": t.get("yangsheng", ""),
            })
        return {
            "total": len(enhanced_list),
            "source": "中医体质分类与判定（中华中医药学会标准）",
            "items": enhanced_list
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