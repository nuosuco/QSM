#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子基因标记器方法修复工具
修复_parse_entangled_objects方法
"""

import os
import re
import sys
import logging
import json
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # 确定文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(current_dir, '..', 'utils', 'quantum_gene_marker.py')
    
    if not os.path.exists(target_file):
        logger.error(f"目标文件不存在: {target_file}")
        return 1
    
    # 读取文件内容
    try:
        with open(target_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        return 1
        
    # 要替换的方法
    old_method = r'''    def _parse_entangled_objects\(self, content: str\) -> List\[str\]:
.*?(?=\s+def update_file_path|\s*# 创建单例实例)'''
    
    # 新的正确方法实现
    new_method = '''    def _parse_entangled_objects(self, content: str) -> List[str]:
        """从文件内容中提取纠缠对象列表

        Args:
            content: 文件内容

        Returns:
            纠缠对象列表
        """
        pattern = r"# 纠缠对象: \\[(.*?)\\]"
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return []

        # 提取并解析纠缠对象
        objects_str = match.group(1).strip()
        if not objects_str:
            return []

        # 尝试解析为Python列表
        try:
            # 替换单引号为双引号以符合JSON格式
            objects_str = objects_str.replace("'", '"')
            return json.loads(f"[{objects_str}]")
        except:
            # 如果解析失败，尝试通过分割来解析
            return [obj.strip().strip("'\\"") for obj in objects_str.split(',') if obj.strip()]'''
    
    # 尝试替换方法
    try:
        new_content = re.sub(old_method, new_method, content, flags=re.DOTALL)
        
        # 检查是否成功替换
        if new_content == content:
            logger.warning("未能找到需要替换的方法")
            return 1
        
        # 写回文件
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info("成功修复_parse_entangled_objects方法")
        return 0
    except Exception as e:
        logger.error(f"修复失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 

    """
    # 
"""
量子基因编码: QE-FIX-D8A704DC38EB
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
    """
    