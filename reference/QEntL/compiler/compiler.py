#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QEntL编译器 - 用于编译量子纠缠模板语言文件为实际配置
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

# 添加父目录到路径，以便导入parser
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from parser.parser import QEntLParser
from parser.validator import QEntLValidator

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", ".logs", "qentl_compiler.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QEntLCompiler")

class QEntLCompiler:
    """QEntL编译器，用于编译量子纠缠模板语言文件为实际可执行配置"""
    
    def __init__(self, template_dir: Optional[str] = None, output_dir: Optional[str] = None):
        """
        初始化编译器
        
        Args:
            template_dir: 模板目录路径
            output_dir: 输出目录路径
        """
        self.template_dir = template_dir or os.path.join(os.path.dirname(__file__), "..", "templates")
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), "..", "compiled")
        self.parser = QEntLParser(template_dir=self.template_dir)
        self.validator = QEntLValidator()
        self.templates_cache = {}
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"初始化QEntL编译器，模板目录: {self.template_dir}, 输出目录: {self.output_dir}")
    
    def compile_file(self, file_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        编译QEntL文件并返回编译后的配置数据
        
        Args:
            file_path: QEntL文件路径
            output_file: 输出文件路径
            
        Returns:
            编译后的配置数据
        """
        logger.info(f"开始编译文件: {file_path}")
        
        try:
            # 解析QEntL文件
            parsed_data = self.parser.parse_file(file_path)
            
            # 验证解析后的数据
            valid, errors = self.validator.validate(parsed_data)
            if not valid:
                for error in errors:
                    logger.error(f"验证错误: {error}")
                raise ValueError(f"QEntL文件验证失败: {errors[0]}")
            
            # 编译解析的数据
            compiled_data = self._compile_parsed_data(parsed_data, file_path)
            
            # 保存编译后的数据
            if output_file:
                output_path = output_file
            else:
                file_name = os.path.basename(file_path)
                name_without_ext = os.path.splitext(file_name)[0]
                output_path = os.path.join(self.output_dir, f"{name_without_ext}_compiled.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(compiled_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"编译完成，保存到: {output_path}")
            return compiled_data
            
        except Exception as e:
            logger.error(f"编译文件 {file_path} 时出错: {str(e)}")
            raise
    
    def _compile_parsed_data(self, parsed_data: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        """
        编译解析后的QEntL数据
        
        Args:
            parsed_data: 解析后的QEntL数据
            source_path: 源文件路径
            
        Returns:
            编译后的配置数据
        """
        # 处理imports，加载模板数据
        imports = parsed_data.get("imports", {})
        for alias, path in imports.items():
            if path not in self.templates_cache:
                try:
                    template_path = path
                    template_data = self.parser.parse_file(template_path)
                    self.templates_cache[path] = template_data
                except Exception as e:
                    logger.error(f"加载模板 {path} 时出错: {str(e)}")
                    raise ValueError(f"无法加载模板 {alias} ({path}): {str(e)}")
        
        # 处理body中的include语句，应用模板
        compiled_body = self._process_includes(parsed_data.get("body", {}), imports)
        
        # 构建结果
        result = {
            "metadata": parsed_data.get("metadata", {}),
            "compiled_at": self._get_timestamp(),
            "source_file": source_path,
            "body": compiled_body
        }
        
        return result
    
    def _process_includes(self, body: Dict[str, Any], imports: Dict[str, str]) -> Dict[str, Any]:
        """
        处理include语句，应用模板
        
        Args:
            body: QEntL主体内容
            imports: 导入的模板
            
        Returns:
            处理后的主体内容
        """
        result = {}
        
        for block_type, block_data in body.items():
            if isinstance(block_data, dict) and "content" in block_data:
                content = block_data["content"]
                
                # 检查是否有include字段
                if isinstance(content, dict) and "include" in content and "params" in content:
                    template_alias = content["include"]
                    params = content["params"]
                    
                    # 获取模板数据
                    template_path = imports.get(template_alias)
                    if not template_path or template_path not in self.templates_cache:
                        logger.error(f"引用的模板 {template_alias} 不存在或未加载")
                        continue
                    
                    template_data = self.templates_cache[template_path]
                    template_body = template_data.get("body", {})
                    
                    # 找到对应类型的模板
                    template_content = None
                    for t_type, t_data in template_body.items():
                        if t_type.lower() == block_type.lower():
                            template_content = t_data.get("content", {})
                            break
                    
                    if template_content:
                        # 应用模板，替换变量
                        compiled_content = self._apply_template(template_content, params)
                        
                        # 合并其他字段
                        for key, value in content.items():
                            if key not in ["include", "params"]:
                                compiled_content[key] = value
                        
                        # 更新block数据
                        result[block_type] = {
                            "name": block_data.get("name"),
                            "content": compiled_content
                        }
                    else:
                        logger.warning(f"在模板 {template_alias} 中找不到类型 {block_type} 的内容")
                        result[block_type] = block_data
                else:
                    result[block_type] = block_data
            else:
                result[block_type] = block_data
        
        # 处理数组中的嵌套include
        for block_type, block_data in result.items():
            if isinstance(block_data, dict) and "content" in block_data:
                content = block_data["content"]
                
                for key, value in content.items():
                    if isinstance(value, list):
                        compiled_list = []
                        for item in value:
                            if isinstance(item, dict) and "include" in item and "params" in item:
                                template_alias = item["include"]
                                params = item["params"]
                                
                                # 获取模板数据
                                template_path = imports.get(template_alias)
                                if not template_path or template_path not in self.templates_cache:
                                    logger.error(f"引用的模板 {template_alias} 不存在或未加载")
                                    compiled_list.append(item)
                                    continue
                                
                                template_data = self.templates_cache[template_path]
                                template_body = template_data.get("body", {})
                                
                                # 根据key找相应的模板类型
                                template_type = ""
                                if key == "nodes":
                                    template_type = "node"
                                elif key == "channels":
                                    template_type = "channel"
                                elif key == "protocols":
                                    template_type = "protocol"
                                else:
                                    template_type = key[:-1] if key.endswith('s') else key
                                
                                # 找到对应类型的模板
                                template_content = None
                                for t_type, t_data in template_body.items():
                                    if t_type.lower() == template_type.lower():
                                        template_content = t_data.get("content", {})
                                        break
                                
                                if template_content:
                                    # 应用模板，替换变量
                                    compiled_item = self._apply_template(template_content, params)
                                    
                                    # 合并其他字段
                                    for i_key, i_value in item.items():
                                        if i_key not in ["include", "params"]:
                                            compiled_item[i_key] = i_value
                                    
                                    compiled_list.append(compiled_item)
                                else:
                                    logger.warning(f"在模板 {template_alias} 中找不到类型 {template_type} 的内容")
                                    compiled_list.append(item)
                            else:
                                compiled_list.append(item)
                        
                        content[key] = compiled_list
        
        return result
    
    def _apply_template(self, template_content: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用模板，替换变量
        
        Args:
            template_content: 模板内容
            params: 参数
            
        Returns:
            替换变量后的内容
        """
        # 创建内容副本
        result = json.loads(json.dumps(template_content))
        
        # 递归替换变量
        def replace_vars(obj):
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    obj[k] = replace_vars(v)
                return obj
            elif isinstance(obj, list):
                return [replace_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('$'):
                var_name = obj[1:]
                if var_name in params:
                    return params[var_name]
                else:
                    logger.warning(f"未定义的变量: {var_name}")
                    return obj
            else:
                return obj
        
        return replace_vars(result)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def compile_directory(self, dir_path: str, recursive: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        编译目录中的所有QEntL文件
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归处理子目录
            
        Returns:
            编译结果字典，键为文件路径，值为编译后的数据
        """
        logger.info(f"开始编译目录: {dir_path}, 递归: {recursive}")
        results = {}
        
        if recursive:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.qentl'):
                        file_path = os.path.join(root, file)
                        try:
                            results[file_path] = self.compile_file(file_path)
                        except Exception as e:
                            logger.error(f"编译文件 {file_path} 失败: {str(e)}")
                            results[file_path] = {"error": str(e)}
        else:
            for file in os.listdir(dir_path):
                if file.endswith('.qentl'):
                    file_path = os.path.join(dir_path, file)
                    try:
                        results[file_path] = self.compile_file(file_path)
                    except Exception as e:
                        logger.error(f"编译文件 {file_path} 失败: {str(e)}")
                        results[file_path] = {"error": str(e)}
        
        logger.info(f"目录编译完成，处理了 {len(results)} 个文件")
        return results


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='QEntL编译器')
    parser.add_argument('input', help='要编译的QEntL文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件路径')
    parser.add_argument('-t', '--template-dir', help='模板目录路径')
    parser.add_argument('-d', '--output-dir', help='输出目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理目录')
    args = parser.parse_args()
    
    try:
        compiler = QEntLCompiler(
            template_dir=args.template_dir,
            output_dir=args.output_dir
        )
        
        if os.path.isdir(args.input):
            results = compiler.compile_directory(args.input, args.recursive)
            success_count = sum(1 for r in results.values() if "error" not in r)
            logger.info(f"编译完成，成功: {success_count}/{len(results)}")
            print(f"编译完成，成功: {success_count}/{len(results)}")
            return 0 if success_count == len(results) else 1
        else:
            compiler.compile_file(args.input, args.output)
            logger.info("编译完成")
            print(f"编译完成，输出保存到: {args.output or os.path.join(compiler.output_dir, os.path.splitext(os.path.basename(args.input))[0] + '_compiled.json')}")
            return 0
    except Exception as e:
        logger.error(f"编译过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"编译失败: {str(e)}")
        return 2


if __name__ == "__main__":
    sys.exit(main()) 
"""
量子基因编码: QE-COM-AEF04F8351DA
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""