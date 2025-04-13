#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QEntL文件量子纠缠关系修复工具

此脚本用于修复以下目录中文档、文件和.qent文件之间的量子纠缠关系：
- docs/QEntL
- QEntL
- Ref/QEntL
- QSM/QEntL
- SOM/QEntL
- WeQ/QEntL
"""

import os
import re
import sys
import hashlib
import logging
from pathlib import Path
import json
from datetime import datetime

# 配置日志
logs_dir = '.logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, 'fix_qentl_relationships.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('QEntLFixer')

# 目录配置
DIRECTORIES = [
    'docs/QEntL',
    'QEntL',
    'Ref/QEntL',
    'QSM/QEntL',
    'SOM/QEntL',
    'WeQ/QEntL'
]

# 文件扩展名分组
EXTENSIONS = {
    'code': ['.qent', '.py', '.js', '.ts'],
    'docs': ['.md', '.txt', '.rst'],
    'configs': ['.json', '.yaml', '.yml', '.xml']
}

# 量子基因编码模式
QE_PATTERN = re.compile(r'/\*\s*"""
量子基因编码: QE-FIX-39C5366A86EF
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
def generate_quantum_gene(file_path, content_type):
    """生成QEntL兼容的量子基因编码"""
    # 基于文件路径生成唯一标识
    file_id = hashlib.md5(file_path.encode('utf-8')).hexdigest().upper()[:10]
    
    # 确定内容类型
    if content_type == 'code':
        type_prefix = 'CODE'
    elif content_type == 'docs':
        type_prefix = 'DOCS'
    elif content_type == 'configs':
        type_prefix = 'CONF'
    else:
        type_prefix = 'FILE'
    
    # 获取模块标识（从路径中提取）
    if 'docs/QEntL' in file_path:
        module = 'DOCSQE'
    elif '/QEntL' in file_path:
        path_parts = file_path.split('/')
        idx = path_parts.index('QEntL')
        if idx > 0:
            module = path_parts[idx-1].upper()[:3] + 'QE'
        else:
            module = 'COREQE'
    else:
        module = 'GENQE'
    
    return f"QE-{module}-{file_id}"

def create_qentl_annotation(gene, entangled_objects=None, status="活跃", strength=0.98):
    """创建QEntL标准的量子基因注释"""
    if entangled_objects is None:
        entangled_objects = []
        
    # 确保对象路径是绝对路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    entangled_objects_abs = []
    
    for obj in entangled_objects:
        if not obj.startswith('/') and not (obj.startswith('E:') or obj.startswith('C:')):
            obj_path = os.path.abspath(os.path.join(project_root, obj))
            entangled_objects_abs.append(obj_path)
        else:
            entangled_objects_abs.append(obj)
    
    entangled_objects_str = str(entangled_objects_abs).replace("'", '"')
    
    annotation = f"""/*
# """
量子基因编码: QE-FIX-39C5366A86EF
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""*/"""
    return annotation

def extract_quantum_gene(content):
    """从文件内容中提取量子基因编码信息"""
    match = QE_PATTERN.search(content)
    if match:
        gene = match.group(1)
        status = match.group(2)
        try:
            entangled_objects = json.loads(match.group(3))
        except json.JSONDecodeError:
            entangled_objects = []
        
        try:
            strength = float(match.group(4))
        except ValueError:
            strength = 0.98
            
        return gene, status, entangled_objects, strength
    
    return None, None, None, None

def get_related_files(file_path, all_files):
    """获取与当前文件相关的文件"""
    file_name = os.path.basename(file_path)
    file_stem = os.path.splitext(file_name)[0]
    dir_path = os.path.dirname(file_path)
    
    # 查找相关文件逻辑：
    # 1. 同目录下的同名不同扩展名文件
    # 2. 父目录或子目录中的相关文件
    # 3. 基于文件内容的相关性
    
    related_files = []
    
    # 同目录下的同名不同扩展名文件
    for f in all_files:
        f_name = os.path.basename(f)
        f_stem = os.path.splitext(f_name)[0]
        f_dir = os.path.dirname(f)
        
        # 同名不同扩展名
        if f_stem == file_stem and f != file_path:
            related_files.append(f)
            
        # 同目录下的文件
        elif f_dir == dir_path and f != file_path:
            related_files.append(f)
            
        # 相关模块文件（基于目录名）
        elif (('/QEntL/' in file_path and '/QEntL/' in f) or 
              ('/Ref/' in file_path and '/Ref/' in f) or
              ('/QSM/' in file_path and '/QSM/' in f) or
              ('/SOM/' in file_path and '/SOM/' in f) or
              ('/WeQ/' in file_path and '/WeQ/' in f)):
            related_files.append(f)
    
    # 限制相关文件数量，避免过多纠缠
    return related_files[:5]

def determine_content_type(file_path):
    """根据文件扩展名确定内容类型"""
    ext = os.path.splitext(file_path)[1].lower()
    
    for content_type, extensions in EXTENSIONS.items():
        if ext in extensions:
            return content_type
    
    return 'other'

def update_file_qentl_annotation(file_path, all_files):
    """更新文件的QEntL量子基因注释"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 确定内容类型
        content_type = determine_content_type(file_path)
        
        # 提取现有的量子基因编码
        gene, status, entangled_objects, strength = extract_quantum_gene(content)
        
        # 如果没有量子基因编码，则生成新的
        if not gene:
            gene = generate_quantum_gene(file_path, content_type)
            status = "活跃"
            strength = 0.98
            
            # 获取相关文件作为纠缠对象
            entangled_objects = get_related_files(file_path, all_files)
        else:
            # 更新相关的纠缠对象
            new_related_files = get_related_files(file_path, all_files)
            
            # 合并现有纠缠对象和新的相关文件
            combined_objects = set(entangled_objects + new_related_files)
            entangled_objects = list(combined_objects)
        
        # 创建新的量子基因注释
        new_annotation = create_qentl_annotation(gene, entangled_objects, status, strength)
        
        # 替换或添加注释
        if QE_PATTERN.search(content):
            # 替换现有注释
            updated_content = QE_PATTERN.sub(lambda _: new_annotation, content)
        else:
            # 添加新注释（文件末尾）
            updated_content = content
            
            # 确保文件末尾有换行
            if not updated_content.endswith('\n'):
                updated_content += '\n'
                
            updated_content += f"\n{new_annotation}\n"
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        logger.info(f"已更新文件量子基因注释: {file_path}")
        return gene, entangled_objects
        
    except Exception as e:
        logger.error(f"更新文件量子基因注释时出错 {file_path}: {str(e)}")
        return None, []

def create_qentl_channel_file(gene, target_entities=None):
    """创建QEntL量子纠缠信道配置文件"""
    try:
        if target_entities is None:
            target_entities = []
            
        # 生成QEntL格式的纠缠信道配置
        channel_config = {
            "sourceGene": gene,
            "targetEntities": target_entities,
            "channelType": "quantum",
            "protocol": "QEntL-v2",
            "coherenceTime": 31536000,  # 一年的秒数
            "fidelity": 0.98,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存纠缠信道配置到QEntL配置文件
        qentl_config_dir = os.path.join('QEntL', 'channels')
        os.makedirs(qentl_config_dir, exist_ok=True)
        
        channel_file = os.path.join(qentl_config_dir, f"{gene}.qchannel")
        with open(channel_file, 'w') as f:
            json.dump(channel_config, f, indent=2)
            
        logger.info(f"已创建QEntL量子纠缠信道配置文件: {channel_file}")
        return True
    except Exception as e:
        logger.error(f"创建QEntL量子纠缠信道配置文件时出错: {str(e)}")
        return False

def find_files(directories):
    """查找指定目录下的所有文件"""
    all_files = []
    
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                # 排除不需要处理的文件
                if (not file.startswith('.') and 
                    not file.endswith('.pyc') and 
                    '__pycache__' not in file_path):
                    all_files.append(file_path)
    
    return all_files

def main():
    """主函数"""
    logger.info("开始修复QEntL文件量子纠缠关系...")
    
    # 查找所有相关文件
    all_files = find_files(DIRECTORIES)
    logger.info(f"找到 {len(all_files)} 个文件")
    
    # 记录所有文件的量子基因编码和纠缠对象
    gene_map = {}
    
    # 第一遍：更新所有文件的量子基因注释
    for file_path in all_files:
        gene, entangled_objects = update_file_qentl_annotation(file_path, all_files)
        if gene:
            gene_map[file_path] = (gene, entangled_objects)
    
    # 第二遍：创建量子纠缠信道配置文件
    for file_path, (gene, _) in gene_map.items():
        # 收集所有引用此文件的其他文件的量子基因编码
        target_entities = []
        for other_path, (other_gene, other_entangled) in gene_map.items():
            if file_path in other_entangled and file_path != other_path:
                target_entities.append(other_gene)
        
        # 创建量子纠缠信道配置文件
        create_qentl_channel_file(gene, target_entities)
    
    logger.info("QEntL文件量子纠缠关系修复完成")

if __name__ == "__main__":
    main() 

    """
    # """
量子基因编码: QE-FIX-39C5366A86EF
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""    """
    