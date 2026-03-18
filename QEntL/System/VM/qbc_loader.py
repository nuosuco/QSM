#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子字节码加载器 v2
QEntL Quantum Bytecode Loader v2

创建时间: 2026-03-18
开发者: 小趣WeQ

功能:
- 加载QBC量子字节码文件
- 支持QBC\x01格式（包含源代码）
- 解析量子基因编码
- 提取源代码内容
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

# 量子基因编码常量
QUANTUM_GENE_ENCODING = {
    "心": "\U000f2737",  # 量子意识核心
    "乾坤": "\U000f2735",  # 量子态空间
    "天": "\U000f27ad",   # 量子网络
    "火": "\U000f27ae",   # 量子能量
    "王": "\U000f27b0",   # 量子控制器
}

@dataclass
class QBCProgram:
    """QBC程序"""
    filepath: str              # 文件路径
    magic: bytes               # 魔数
    source_code: str           # 源代码
    metadata: Dict             # 元数据
    
    def get_quantum_genes(self) -> List[str]:
        """提取量子基因编码"""
        genes = []
        for name, char in QUANTUM_GENE_ENCODING.items():
            if char in self.source_code:
                genes.append(name)
        return genes
    
    def get_functions(self) -> List[str]:
        """提取函数定义"""
        import re
        # 匹配函数定义: 函数 名字( 或 function name(
        pattern = r'(函数|function)\s+(\w+)\s*\('
        return re.findall(pattern, self.source_code)
    
    def get_classes(self) -> List[str]:
        """提取类定义"""
        import re
        # 匹配类定义: 类型 名字 { 或 quantum_class Name {
        pattern = r'(类型|type|quantum_class)\s+(\w+)\s*\{'
        return re.findall(pattern, self.source_code)


class QBCLoader:
    """QBC量子字节码加载器"""
    
    def __init__(self):
        self.quantum_genes = QUANTUM_GENE_ENCODING
    
    def load(self, filepath: str) -> QBCProgram:
        """
        加载QBC文件
        
        Args:
            filepath: QBC文件路径
            
        Returns:
            QBCProgram对象
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"QBC文件不存在: {filepath}")
        
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        # 验证魔数
        magic = raw_data[:4]
        if magic[:3] != b'QBC':
            raise ValueError(f"无效的QBC文件: 魔数不匹配")
        
        # 提取源代码（跳过4字节头）
        source_code = raw_data[4:].decode('utf-8', errors='ignore')
        
        # 解析元数据
        metadata = self._parse_metadata(source_code)
        
        print(f"✅ QBC文件加载成功: {os.path.basename(filepath)}")
        print(f"   魔数: {magic.hex()}")
        print(f"   源代码长度: {len(source_code)} 字符")
        
        return QBCProgram(
            filepath=filepath,
            magic=magic,
            source_code=source_code,
            metadata=metadata
        )
    
    def _parse_metadata(self, source: str) -> Dict:
        """解析源代码中的元数据"""
        metadata = {
            "has_config": "配置" in source or "config" in source.lower(),
            "has_functions": "函数" in source or "function" in source.lower(),
            "has_classes": "类型" in source or "quantum_class" in source,
            "line_count": source.count('\n') + 1,
        }
        return metadata
    
    def load_directory(self, dirpath: str) -> List[QBCProgram]:
        """加载目录下所有QBC文件"""
        programs = []
        for root, dirs, files in os.walk(dirpath):
            for f in files:
                if f.endswith('.qbc'):
                    filepath = os.path.join(root, f)
                    try:
                        prog = self.load(filepath)
                        programs.append(prog)
                    except Exception as e:
                        print(f"⚠️ 加载失败: {filepath} - {e}")
        return programs
    
    def analyze_all(self, dirpath: str) -> Dict:
        """分析目录下所有QBC文件"""
        programs = self.load_directory(dirpath)
        
        analysis = {
            "total_files": len(programs),
            "total_lines": sum(p.metadata["line_count"] for p in programs),
            "quantum_genes_used": {},
            "functions": [],
            "classes": [],
        }
        
        # 统计量子基因使用
        for prog in programs:
            for gene in prog.get_quantum_genes():
                analysis["quantum_genes_used"][gene] = \
                    analysis["quantum_genes_used"].get(gene, 0) + 1
            
            analysis["functions"].extend(prog.get_functions())
            analysis["classes"].extend(prog.get_classes())
        
        return analysis


def main():
    """测试函数"""
    print("🚀 QEntL量子字节码加载器 v2 测试")
    print("=" * 60)
    
    loader = QBCLoader()
    
    # 测试单个文件
    qbc_dir = "/root/QSM/qbc"
    test_file = f"{qbc_dir}/system/kernel/filesystem/access_control.qbc"
    
    if os.path.exists(test_file):
        print("\n📄 测试加载单个文件:")
        program = loader.load(test_file)
        print(f"\n源代码前200字符:")
        print(program.source_code[:200])
        print(f"\n量子基因: {program.get_quantum_genes()}")
        print(f"函数: {program.get_functions()[:5]}")
    
    # 分析所有文件
    print("\n" + "=" * 60)
    print("📊 分析所有QBC文件:")
    analysis = loader.analyze_all(qbc_dir)
    
    print(f"\n总文件数: {analysis['total_files']}")
    print(f"总行数: {analysis['total_lines']}")
    print(f"\n量子基因使用统计:")
    for gene, count in sorted(analysis["quantum_genes_used"].items(), 
                               key=lambda x: -x[1]):
        print(f"  {gene}: {count} 次")
    
    print(f"\n函数定义数: {len(analysis['functions'])}")
    print(f"类定义数: {len(analysis['classes'])}")
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()
