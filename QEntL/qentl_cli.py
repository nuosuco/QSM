#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QEntL命令行工具 - 量子纠缠模板语言处理工具
提供解析、验证、编译和可视化QEntL文件的功能
"""

import os
import sys
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# 导入QEntL模块
from parser.parser import QEntLParser
from parser.validator import QEntLValidator
from compiler.compiler import QEntLCompiler

# 版本信息
VERSION = "2.0.0"

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), ".logs", "qentl_cli.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QEntLCLI")

class QEntLCLI:
    """QEntL命令行工具，提供解析、验证、编译和可视化QEntL文件的功能"""
    
    def __init__(self):
        """初始化CLI工具"""
        self.parser = None
        self.validator = None
        self.compiler = None
        
        # 确保日志目录存在
        os.makedirs(os.path.join(os.path.dirname(__file__), ".logs"), exist_ok=True)
        
        logger.info(f"QEntL CLI v{VERSION} 已初始化")
    
    def _get_parser(self, template_dir: Optional[str] = None) -> QEntLParser:
        """获取解析器实例"""
        if not self.parser:
            self.parser = QEntLParser(template_dir=template_dir)
        return self.parser
    
    def _get_validator(self, schema_dir: Optional[str] = None) -> QEntLValidator:
        """获取验证器实例"""
        if not self.validator:
            self.validator = QEntLValidator(schema_dir=schema_dir)
        return self.validator
    
    def _get_compiler(self, template_dir: Optional[str] = None, output_dir: Optional[str] = None) -> QEntLCompiler:
        """获取编译器实例"""
        if not self.compiler:
            self.compiler = QEntLCompiler(template_dir=template_dir, output_dir=output_dir)
        return self.compiler
    
    def parse_file(self, file_path: str, output_file: Optional[str] = None, template_dir: Optional[str] = None) -> int:
        """解析QEntL文件"""
        try:
            parser = self._get_parser(template_dir)
            parsed_data = parser.parse_file(file_path)
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, indent=2, ensure_ascii=False)
                print(f"✅ 解析成功，结果已保存到: {output_file}")
            else:
                print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
            
            return 0
        except Exception as e:
            logger.error(f"解析文件 {file_path} 时出错: {str(e)}")
            print(f"❌ 解析失败: {str(e)}")
            return 1
    
    def validate_file(self, file_path: str, schema_dir: Optional[str] = None) -> int:
        """验证QEntL JSON文件"""
        try:
            validator = self._get_validator(schema_dir)
            valid, errors = validator.validate_file(file_path)
            
            if valid:
                print("✅ 验证成功: 文件符合QEntL模式定义")
                return 0
            else:
                print(f"❌ 验证失败: 发现{len(errors)}个错误")
                for i, error in enumerate(errors, 1):
                    print(f"   错误 {i}: {error}")
                return 1
        except Exception as e:
            logger.error(f"验证文件 {file_path} 时出错: {str(e)}")
            print(f"❌ 验证失败: {str(e)}")
            return 2
    
    def compile_file(self, file_path: str, output_file: Optional[str] = None, 
                     template_dir: Optional[str] = None, output_dir: Optional[str] = None) -> int:
        """编译QEntL文件"""
        try:
            compiler = self._get_compiler(template_dir, output_dir)
            compiled_data = compiler.compile_file(file_path, output_file)
            
            output_path = output_file
            if not output_path:
                file_name = os.path.basename(file_path)
                name_without_ext = os.path.splitext(file_name)[0]
                output_path = os.path.join(compiler.output_dir, f"{name_without_ext}_compiled.json")
            
            print(f"✅ 编译成功，结果已保存到: {output_path}")
            return 0
        except Exception as e:
            logger.error(f"编译文件 {file_path} 时出错: {str(e)}")
            print(f"❌ 编译失败: {str(e)}")
            return 3
    
    def compile_directory(self, dir_path: str, recursive: bool = False,
                          template_dir: Optional[str] = None, output_dir: Optional[str] = None) -> int:
        """编译目录中的所有QEntL文件"""
        try:
            compiler = self._get_compiler(template_dir, output_dir)
            results = compiler.compile_directory(dir_path, recursive)
            
            success_count = sum(1 for r in results.values() if "error" not in r)
            
            if success_count == len(results):
                print(f"✅ 目录编译完成: {success_count}/{len(results)} 个文件成功")
                return 0
            else:
                print(f"⚠️ 目录编译部分成功: {success_count}/{len(results)} 个文件成功")
                
                # 打印失败的文件和错误信息
                print("\n失败的文件:")
                for file_path, result in results.items():
                    if "error" in result:
                        print(f"   - {file_path}: {result['error']}")
                
                return 4
        except Exception as e:
            logger.error(f"编译目录 {dir_path} 时出错: {str(e)}")
            print(f"❌ 目录编译失败: {str(e)}")
            return 5
    
    def generate_template(self, template_type: str, output_file: str) -> int:
        """生成QEntL模板文件"""
        try:
            # 检查模板类型
            template_type = template_type.lower()
            if template_type not in ["node", "channel", "network", "protocol"]:
                print(f"❌ 错误: 不支持的模板类型 '{template_type}'")
                print("   支持的类型: node, channel, network, protocol")
                return 6
            
            # 模板目录
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
            template_file = os.path.join(template_dir, f"{template_type}_template.qentl")
            
            if not os.path.exists(template_file):
                print(f"❌ 错误: 找不到模板文件 '{template_file}'")
                return 7
            
            # 复制模板文件
            with open(template_file, 'r', encoding='utf-8') as src:
                content = src.read()
                
            with open(output_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            print(f"✅ 成功生成 {template_type} 模板: {output_file}")
            return 0
        except Exception as e:
            logger.error(f"生成模板时出错: {str(e)}")
            print(f"❌ 生成模板失败: {str(e)}")
            return 8
    
    def visualize(self, file_path: str, output_file: Optional[str] = None) -> int:
        """可视化QEntL编译后的文件（生成GraphViz DOT文件）"""
        try:
            # 读取编译后的文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否是网络配置
            if "body" not in data or "network" not in data["body"]:
                print("❌ 错误: 此文件不是有效的网络配置文件")
                return 9
            
            # 生成GraphViz DOT内容
            dot_content = self._generate_dot(data)
            
            # 确定输出文件
            if not output_file:
                base_name = os.path.splitext(file_path)[0]
                output_file = f"{base_name}.dot"
            
            # 写入DOT文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(dot_content)
            
            print(f"✅ 已生成GraphViz可视化文件: {output_file}")
            print("   使用GraphViz工具可将其转换为图像，例如:")
            print(f"   dot -Tpng {output_file} -o {os.path.splitext(output_file)[0]}.png")
            
            return 0
        except Exception as e:
            logger.error(f"可视化文件 {file_path} 时出错: {str(e)}")
            print(f"❌ 可视化失败: {str(e)}")
            return 10
    
    def _generate_dot(self, data: Dict[str, Any]) -> str:
        """生成GraphViz DOT格式的网络可视化"""
        network = data["body"]["network"]
        network_name = network.get("name", "quantum_network")
        network_content = network.get("content", {})
        
        # DOT文件头
        dot = [
            f'digraph "{network_name}" {{',
            '  rankdir=LR;',
            '  node [shape=box, style="rounded,filled", color="#4472C4", fillcolor="#E6EEF8", fontname="Arial"];',
            '  edge [color="#70AD47", penwidth=1.5, fontname="Arial"];',
            '  graph [fontname="Arial", overlap=false, splines=true];',
            ''
        ]
        
        # 添加节点
        nodes = network_content.get("nodes", [])
        for node in nodes:
            node_id = node.get("id", "unknown")
            node_type = node.get("type", "unknown")
            node_label = f"{node_id}\\n({node_type})"
            
            # 根据节点类型设置不同的颜色
            node_color = "#4472C4"  # 默认蓝色
            if "processor" in node_type.lower():
                node_color = "#ED7D31"  # 处理器为橙色
            elif "memory" in node_type.lower():
                node_color = "#70AD47"  # 内存为绿色
            elif "controller" in node_type.lower():
                node_color = "#5B9BD5"  # 控制器为蓝色
            
            dot.append(f'  "{node_id}" [label="{node_label}", color="{node_color}"];')
        
        dot.append('')
        
        # 添加通道
        channels = network_content.get("channels", [])
        for channel in channels:
            source = channel.get("source", "")
            target = channel.get("target", "")
            channel_id = channel.get("id", "unknown")
            
            if source and target:
                dot.append(f'  "{source}" -> "{target}" [label="{channel_id}"];')
        
        dot.append('}')
        
        return '\n'.join(dot)
    
    def print_version(self) -> None:
        """打印版本信息"""
        print(f"QEntL CLI v{VERSION}")
        print("量子纠缠模板语言 (Quantum Entanglement Template Language) 工具集")
        print("作者: Quantum Systems Architecture Team")


def main():
    """命令行入口函数"""
    cli = QEntLCLI()
    
    # 创建主解析器
    parser = argparse.ArgumentParser(
        description="QEntL命令行工具 - 处理量子纠缠模板语言文件",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-v', '--version', action='store_true', help="显示版本信息")
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # parse命令
    parse_parser = subparsers.add_parser("parse", help="解析QEntL文件")
    parse_parser.add_argument('file', help="要解析的QEntL文件路径")
    parse_parser.add_argument('-o', '--output', help="输出JSON文件路径")
    parse_parser.add_argument('-t', '--template-dir', help="模板目录路径")
    
    # validate命令
    validate_parser = subparsers.add_parser("validate", help="验证QEntL JSON文件")
    validate_parser.add_argument('file', help="要验证的QEntL JSON文件路径")
    validate_parser.add_argument('-s', '--schema-dir', help="Schema目录路径")
    
    # compile命令
    compile_parser = subparsers.add_parser("compile", help="编译QEntL文件")
    compile_parser.add_argument('input', help="要编译的QEntL文件或目录路径")
    compile_parser.add_argument('-o', '--output', help="输出文件路径（仅用于单个文件）")
    compile_parser.add_argument('-t', '--template-dir', help="模板目录路径")
    compile_parser.add_argument('-d', '--output-dir', help="输出目录路径")
    compile_parser.add_argument('-r', '--recursive', action='store_true', help="递归处理目录")
    
    # generate命令
    generate_parser = subparsers.add_parser("generate", help="生成QEntL模板文件")
    generate_parser.add_argument('type', help="模板类型 (node, channel, network, protocol)")
    generate_parser.add_argument('output', help="输出文件路径")
    
    # visualize命令
    visualize_parser = subparsers.add_parser("visualize", help="可视化QEntL编译后的文件")
    visualize_parser.add_argument('file', help="要可视化的QEntL编译文件路径")
    visualize_parser.add_argument('-o', '--output', help="输出DOT文件路径")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理命令
    if args.version:
        cli.print_version()
        return 0
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == "parse":
        return cli.parse_file(args.file, args.output, args.template_dir)
    
    elif args.command == "validate":
        return cli.validate_file(args.file, args.schema_dir)
    
    elif args.command == "compile":
        if os.path.isdir(args.input):
            return cli.compile_directory(args.input, args.recursive, args.template_dir, args.output_dir)
        else:
            return cli.compile_file(args.input, args.output, args.template_dir, args.output_dir)
    
    elif args.command == "generate":
        return cli.generate_template(args.type, args.output)
    
    elif args.command == "visualize":
        return cli.visualize(args.file, args.output)
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main()) 
"""
量子基因编码: QE-QEN-E19888A853ED
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""