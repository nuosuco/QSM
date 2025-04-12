# 
"""
"""
量子基因编码: Q-74EA-3227-DDAF
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
""""""
# 开发团队：中华 ZhoHo ，Claude


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QEntL示例脚本
演示量子基因标记功能
"""

import os
import sys
import re
import hashlib
import random
import time
from pathlib import Path

# 文件扩展名和对应的注释标记
COMMENT_MARKERS = {
    '.py': {'start': '# ', 'end': ''},
    '.js': {'start': '// ', 'end': ''},
    '.jsx': {'start': '// ', 'end': ''},
    '.ts': {'start': '// ', 'end': ''},
    '.tsx': {'start': '// ', 'end': ''},
    '.java': {'start': '// ', 'end': ''},
    '.c': {'start': '// ', 'end': ''},
    '.cpp': {'start': '// ', 'end': ''},
    '.h': {'start': '// ', 'end': ''},
    '.html': {'start': '<!-- ', 'end': ' -->'},
    '.md': {'start': '<!-- ', 'end': ' -->'},
    '.css': {'start': '/* ', 'end': ' */'},
    '.scss': {'start': '/* ', 'end': ' */'},
    '.php': {'start': '// ', 'end': ''},
    '.go': {'start': '// ', 'end': ''},
    '.rb': {'start': '# ', 'end': ''},
    '.rs': {'start': '// ', 'end': ''},
    '.sh': {'start': '# ', 'end': ''},
    '.swift': {'start': '// ', 'end': ''},
    '.kt': {'start': '// ', 'end': ''},
    '.json': {'start': '/* ', 'end': ' */'},
    '.xml': {'start': '<!-- ', 'end': ' -->'},
    '.yaml': {'start': '# ', 'end': ''},
    '.yml': {'start': '# ', 'end': ''},
}

def get_comment_markers(file_path: str):
    """获取文件的注释标记"""
    _, ext = os.path.splitext(file_path.lower())
    if ext in COMMENT_MARKERS:
        return COMMENT_MARKERS[ext]['start'], COMMENT_MARKERS[ext]['end']
    else:
        # 默认使用Python风格的注释
        return '# ', ''

def generate_quantum_gene_code(file_path: str, content: str = None):
    """生成量子基因编码"""
    # 如果没有提供文件内容，则读取文件
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            content = ""
    
    # 结合文件路径、内容和时间戳生成hash
    data = f"{file_path}:{content}:{time.time()}"
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()
    
    # 将hash转换为量子基因编码格式 Q-XXXX-XXXX-XXXX
    gene_code = f"Q-{hash_hex[:4].upper()}-{hash_hex[4:8].upper()}-{hash_hex[8:12].upper()}"
    return gene_code

def parse_entangled_objects(content: str):
    """从文件内容解析可能的纠缠对象"""
    entangled_objects = []
    
    # 检测Python导入
    import_pattern = r'(?:from|import)\s+([\w\.]+)(?:\s+import|\s*$)'
    for match in re.finditer(import_pattern, content):
        module = match.group(1).strip()
        if module and module not in ['os', 'sys', 're', 'time', 'random', 'hashlib', 'json']:
            entangled_objects.append(module)
    
    # 检测JavaScript/TypeScript导入
    js_import_pattern = r'(?:import|require)\s*[\({]?\s*[\'\"](.+?)[\'\"]'
    for match in re.finditer(js_import_pattern, content):
        module = match.group(1).strip()
        if module and not module.startswith('.') and not module.startswith('/'):
            entangled_objects.append(module)
    
    # 可以添加更多语言的规则
    
    return list(set(entangled_objects))[:5]  # 最多返回5个

def has_quantum_gene_marker(content: str):
    """检查文件内容是否已有量子基因标记"""
    return "        
        # 添加标记到文件开头
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(marker + content)
        
        return True
    
    except Exception as e:
        print(f"添加量子基因标记时出错: {file_path}, {str(e)}")
        return False

def update_quantum_gene_marker(file_path: str, entangled_objects = None, strength: float = 0.98):
    """更新文件的量子基因标记"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # 如果没有量子基因标记，则添加一个
        if not has_quantum_gene_marker(content):
            return add_quantum_gene_marker(file_path, entangled_objects, strength)
        
        # 获取文件的注释标记
        comment_start, comment_end = get_comment_markers(file_path)
        
        # 如果没有提供纠缠对象，则保留现有的
        current_entangled = re.search(r'纠缠对象: (.+?)(?:\n|$)', content)
        if entangled_objects is None and current_entangled:
            entangled_str = current_entangled.group(1).strip()
            if entangled_str != '无':
                entangled_objects = [obj.strip() for obj in entangled_str.split(',')]
        
        # 如果仍然没有纠缠对象，则自动检测
        if entangled_objects is None:
            entangled_objects = parse_entangled_objects(content)
        
        # 生成新的量子基因编码
        gene_code = generate_quantum_gene_code(file_path, content)
        
        # 创建新的量子基因标记
        marker = f"{comment_start}        
        # 移除旧的量子基因标记
<<<<<<< HEAD
        pattern = r"((?://*|#|//|<!--|''')?\s*        clean_content = re.sub(pattern, "", content, flags=re.DOTALL)
=======
        pattern = r"((?:/\*|#|//|<!--|''')?\s*        clean_content = re.sub(pattern, "", content, flags=re.DOTALL)
>>>>>>> c8ee4fc6e39ad3985ce941a8efbcb072b6ba0eea
        
        # 添加新的标记到文件开头
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(marker + clean_content)
        
        return True
    
    except Exception as e:
        print(f"更新量子基因标记时出错: {file_path}, {str(e)}")
        return False

def scan_and_mark_directory(directory: str, recursive: bool = False, file_patterns = None):
    """扫描目录并为文件添加量子基因标记"""
    if file_patterns is None:
        file_patterns = list(COMMENT_MARKERS.keys())
    
    result = {
        'total_files': 0,
        'marked_files': 0,
        'errors': 0
    }
    
    # 构建glob模式
    pattern = '**/*' if recursive else '*'
    
    # 扫描目录
    for path in Path(directory).glob(pattern):
        if not path.is_file():
            continue
        
        # 检查文件扩展名
        file_ext = path.suffix.lower()
        if file_ext not in file_patterns:
            continue
        
        result['total_files'] += 1
        
        # 添加量子基因标记
        try:
            success = add_quantum_gene_marker(str(path))
            if success:
                result['marked_files'] += 1
                print(f"已标记: {path}")
            else:
                result['errors'] += 1
        except Exception as e:
            result['errors'] += 1
            print(f"处理文件时出错: {path}, {str(e)}")
    
    return result

def main():
    """主函数"""
    print("QEntL量子基因标记示例")
    print("===================")
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"当前目录: {current_dir}")
    
    # 示例1：为单个文件添加量子基因标记
    self_path = os.path.abspath(__file__)
    print(f"\n示例1: 为本文件添加量子基因标记")
    print(f"文件路径: {self_path}")
    
    success = add_quantum_gene_marker(self_path, ["utils.py", "engine.py"], 0.95)
    if success:
        print("量子基因标记添加成功")
    else:
        print("量子基因标记添加失败")
    
    # 示例2：扫描目录添加量子基因标记
    print(f"\n示例2: 扫描目录添加量子基因标记")
    target_dir = current_dir
    print(f"目标目录: {target_dir}")
    
    result = scan_and_mark_directory(target_dir, recursive=True)
    print(f"扫描结果: 共 {result['total_files']} 个文件，添加标记 {result['marked_files']} 个，错误 {result['errors']} 个")

if __name__ == "__main__":
    main() 