#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QEntL解析器 - 用于解析量子纠缠模板语言文件
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", ".logs", "qentl_parser.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QEntLParser")

class QEntLParser:
    """QEntL文件解析器，用于解析量子纠缠模板语言文件"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        初始化解析器
        
        Args:
            template_dir: 模板目录路径
        """
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "..", "templates")
        self.imported_templates = {}
        self.current_file = ""
        self.variables = {}
        logger.info(f"初始化QEntL解析器，模板目录: {self.template_dir}")
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析QEntL文件并返回结构化数据
        
        Args:
            file_path: QEntL文件路径
            
        Returns:
            解析后的结构化数据
        """
        logger.info(f"开始解析文件: {file_path}")
        self.current_file = file_path
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, file_path)
        except Exception as e:
            logger.error(f"解析文件 {file_path} 时出错: {str(e)}")
            raise
    
    def parse_content(self, content: str, source_path: str) -> Dict[str, Any]:
        """
        解析QEntL内容并返回结构化数据
        
        Args:
            content: QEntL文件内容
            source_path: 源文件路径（用于解析导入）
            
        Returns:
            解析后的结构化数据
        """
        # 解析元数据
        metadata = self._parse_metadata(content)
        
        # 解析导入语句
        imports = self._parse_imports(content, source_path)
        
        # 解析主体内容
        body = self._parse_body(content)
        
        result = {
            "metadata": metadata,
            "imports": imports,
            "body": body
        }
        
        logger.debug(f"解析结果: {json.dumps(result, indent=2)}")
        return result
    
    def _parse_metadata(self, content: str) -> Dict[str, str]:
        """解析QEntL文件元数据"""
        metadata = {}
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('import'):
                continue
                
            if ':' in line and not line.startswith('{') and not line.endswith('}'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().rstrip(',')
                
            # 如果遇到第一个结构体定义，停止解析元数据
            if '{' in line and any(block in line for block in ['network', 'node', 'channel', 'protocol']):
                break
                
        return metadata
    
    def _parse_imports(self, content: str, source_path: str) -> Dict[str, str]:
        """解析导入语句并加载模板"""
        imports = {}
        import_pattern = r'import\s+"([^"]+)"\s+as\s+(\w+)'
        
        for match in re.finditer(import_pattern, content):
            path, alias = match.groups()
            
            # 解析相对路径
            if path.startswith(".."):
                # 相对于当前文件的路径
                abs_path = os.path.normpath(os.path.join(os.path.dirname(source_path), path))
            else:
                # 相对于模板目录的路径
                abs_path = os.path.normpath(os.path.join(self.template_dir, path))
            
            logger.info(f"导入模板: {path} 作为 {alias}, 绝对路径: {abs_path}")
            
            # 加载模板文件
            if os.path.exists(abs_path):
                with open(abs_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # 解析模板并存储
                self.imported_templates[alias] = self.parse_content(template_content, abs_path)
                imports[alias] = abs_path
            else:
                logger.error(f"无法找到导入的模板文件: {abs_path}")
                imports[alias] = f"ERROR: 文件不存在 - {abs_path}"
        
        return imports
    
    def _parse_body(self, content: str) -> Dict[str, Any]:
        """解析QEntL文件主体内容"""
        # 移除注释
        content = re.sub(r'//.*?/n', '\n', content)
        
        # 寻找主要定义块
        block_pattern = r'(\w+)\s+(?:"([^"]+)")?\s*{([^}]+)}'
        blocks = {}
        
        for match in re.finditer(block_pattern, content, re.DOTALL):
            block_type, block_name, block_content = match.groups()
            blocks[block_type] = {
                "name": block_name,
                "content": self._parse_block_content(block_content.strip())
            }
            
        return blocks
    
    def _parse_block_content(self, content: str) -> Dict[str, Any]:
        """解析内容块，处理嵌套结构"""
        result = {}
        lines = content.split('\n')
        current_key = None
        current_content = []
        in_nested_block = False
        nested_braces = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 处理嵌套块的开始
            if ':' in line and '{' in line and not in_nested_block:
                key, _ = line.split(':', 1)
                current_key = key.strip()
                current_content = [line.split(':', 1)[1].strip()]
                in_nested_block = True
                nested_braces = line.count('{') - line.count('}')
                continue
                
            # 在嵌套块内
            if in_nested_block:
                current_content.append(line)
                nested_braces += line.count('{') - line.count('}')
                
                # 嵌套块结束
                if nested_braces <= 0:
                    in_nested_block = False
                    nested_content = '\n'.join(current_content)
                    
                    # 递归解析嵌套内容
                    if nested_content.strip().startswith('{'):
                        result[current_key] = self._parse_nested_content(nested_content)
                    else:
                        result[current_key] = nested_content.strip().rstrip(',')
                    
                    current_key = None
                    current_content = []
                continue
                
            # 普通键值对
            if ':' in line and not in_nested_block:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().rstrip(',')
                
                # 处理数组
                if value.startswith('[') and value.endswith(']'):
                    value = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
                
                # 处理嵌套对象引用
                if value.startswith('{') and value.endswith('}'):
                    value = self._parse_nested_content(value)
                
                # 尝试转换数值
                elif value.replace('.', '', 1).isdigit():
                    value = float(value) if '.' in value else int(value)
                
                # 处理布尔值
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                # 处理字符串（移除引号）
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                result[key] = value
        
        return result
    
    def _parse_nested_content(self, content: str) -> Dict[str, Any]:
        """解析嵌套内容，处理大括号内的结构"""
        # 去除外层大括号
        if content.strip().startswith('{') and content.strip().endswith('}'):
            content = content.strip()[1:-1].strip()
        
        return self._parse_block_content(content)
    
    def resolve_template(self, template_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析模板，替换参数
        
        Args:
            template_data: 模板数据
            params: 替换参数
            
        Returns:
            解析后的模板实例
        """
        # 创建一个副本以避免修改原模板
        result = json.loads(json.dumps(template_data))
        
        # 递归替换所有变量
        def replace_vars(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = replace_vars(v)
                return obj
            elif isinstance(obj, list):
                return [replace_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('$'):
                var_name = obj[1:]
                return params.get(var_name, obj)
            else:
                return obj
        
        return replace_vars(result)
    
    def export_json(self, parsed_data: Dict[str, Any], output_path: str) -> None:
        """
        将解析后的数据导出为JSON文件
        
        Args:
            parsed_data: 解析后的数据
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        logger.info(f"已导出JSON到: {output_path}")


def main():
    """命令行入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QEntL文件解析器')
    parser.add_argument('file', help='要解析的QEntL文件路径')
    parser.add_argument('-o', '--output', help='输出JSON文件路径')
    parser.add_argument('-t', '--template-dir', help='模板目录路径')
    args = parser.parse_args()
    
    try:
        qentl_parser = QEntLParser(template_dir=args.template_dir)
        parsed_data = qentl_parser.parse_file(args.file)
        
        if args.output:
            qentl_parser.export_json(parsed_data, args.output)
        else:
            print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
            
        return 0
    except Exception as e:
        logger.error(f"解析过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
"""
量子基因编码: QE-PAR-9720CFEE94FD
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""