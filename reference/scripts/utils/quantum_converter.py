#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子转换工具 - 增强版项目转换工具

此脚本整合了现有的转换功能，并添加了新的特性，如：
- 批量转换整个项目
- 智能识别文件类型和依赖关系
- 更准确的量子基因编码和纠缠信道生成
- 自动保留项目历史版本
- 支持更多文件类型转换（Markdown、JSON、XML等）
- 转换进度可视化
"""

import os
import sys
import re
import json
import shutil
import logging
import argparse
import datetime
import random
import uuid
import hashlib
import fnmatch
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union, Any

# 目录设置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REFERENCE_DIR = os.path.join(ROOT_DIR, 'reference')
LOG_DIR = os.path.join(ROOT_DIR, '.logs')
HISTORY_DIR = os.path.join(ROOT_DIR, '.history')

# 创建必要的目录
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REFERENCE_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'quantum_converter.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Quantum-Converter')

# 项目模块和优先级
PROJECT_MODULES = [
    "QSM",      # 主服务，最先转换
    "WeQ",      # 量子社交服务
    "SOM",      # 量子经济服务
    "Ref",      # 量子自反省服务
    "world",    # 世界服务
    "quantum_core",  # 量子核心
    "quantum_ui",    # 量子UI
    "quantum_data",  # 量子数据
    "quantum_shared",  # 量子共享
    "quantum_economy", # 量子经济
    "scripts",  # 脚本工具
    "api",      # API服务
    "core",     # 核心组件
    "tests",    # 测试文件
]

# 模块内部优先级（目录）
DIRECTORY_PRIORITY = [
    "models",    # 模型定义最先转换
    "api",       # API接口
    "services",  # 服务实现
    "utils",     # 工具函数
    "controllers", # 控制器
    "templates", # 模板文件
    "static",    # 静态资源
]

# 文件类型优先级
FILE_TYPE_PRIORITY = [
    ".py",       # Python文件最先转换
    ".js",       # JavaScript文件
    ".css",      # CSS文件
    ".html",     # HTML文件
    ".md",       # Markdown文件
    ".json",     # JSON文件
    ".xml",      # XML文件
    ".txt",      # 纯文本文件
]

# 扩展的转换规则
CONVERSION_RULES = {
    '.py': '.qpy',     # Python转QPy
    '.js': '.qjs',     # JavaScript转QJS
    '.css': '.qcss',   # CSS转QCSS
    '.html': '.qentl', # HTML转QEntl模板
    '.md': '.qentl',   # Markdown转QEntl文档
    '.json': '.qjson', # JSON转QJson
    '.xml': '.qxml',   # XML转QXml
    '.txt': '.qtxt',   # 纯文本转QTxt
}

# 排除的文件和目录模式
EXCLUDE_PATTERNS = [
    '*.pyc', '*.pyo', '*.so', '*.dll', '*.exe', '*.bin', '*.dat', '*.db',
    '__pycache__', '.git', '.venv', 'node_modules', 'reference', '.history',
    '.idea', '.vscode', 'dist', 'build', '*.egg-info', '.env',
]

# 文件类型识别
FILE_TYPE_MAPPING = {
    '.py': 'CODE',
    '.js': 'UI',
    '.css': 'STYLE',
    '.html': 'TEMPLATE',
    '.md': 'DOC',
    '.json': 'DATA',
    '.xml': 'DATA',
    '.txt': 'DOC',
}

# 量子基因编码和纠缠信道模板
QG_TEMPLATE = """
# 量子基因编码
QG-{type}-{module}-{function}-{version}
"""

QE_TEMPLATE = """
# 量子纠缠信道
@quantum_entangle
  channel_id: QE-{type}-{module}-{timestamp}
  state: ACTIVE
  strength: {strength}
  objects: [
{objects}
  ]
"""

# 语法转换规则
SYNTAX_RULES = {
    'python': {
        'self': 'this',
        'def ': '@method ',
        'class ': '@class ',
        '__init__': '@constructor',
        'import ': '@import ',
        'from ': '@from ',
    },
    'javascript': {
        'function ': '@function ',
        'class ': '@class ',
        'constructor': '@constructor',
        'var ': 'let ',
        'const ': '@const ',
    },
    'css': {
        '@media': '@quantum_media',
        '@keyframes': '@quantum_keyframes',
        '@import': '@quantum_import',
    },
    'html': {
        '<html': '<qentl',
        '</html>': '</qentl>',
        '<script': '<qscript',
        '</script>': '</qscript>',
        '<style': '<qstyle',
        '</style>': '</qstyle>',
    },
    'markdown': {
        '# ': '@heading1 ',
        '## ': '@heading2 ',
        '### ': '@heading3 ',
        '#### ': '@heading4 ',
        '##### ': '@heading5 ',
        '###### ': '@heading6 ',
    }
}

# 版本信息
VERSION = "1.0.0"

# ============================== 核心功能函数 ==============================

def generate_quantum_gene_code(file_path: str) -> str:
    """为文件生成更精确的量子基因编码
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 量子基因编码
    """
    # 解析文件类型和模块
    file_name = os.path.basename(file_path)
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    parts = rel_path.split(os.sep)
    
    # 确定文件类型
    file_ext = os.path.splitext(file_path)[1]
    file_type = FILE_TYPE_MAPPING.get(file_ext, 'DOC')
    
    # 确定模块
    if len(parts) > 1:
        module = parts[0].upper()
    else:
        module = 'CORE'
    
    # 确定功能名称
    function = get_function_name(file_path)
    
    # 生成一致但独特的版本号（基于文件路径的哈希）
    file_hash = hashlib.md5(rel_path.encode()).hexdigest()
    version = f"{chr(65 + int(file_hash[0], 16) % 26)}{1 + int(file_hash[1], 16) % 9}"\
              f"{chr(65 + int(file_hash[2], 16) % 26)}{1 + int(file_hash[3], 16) % 9}"
    
    return QG_TEMPLATE.format(
        type=file_type,
        module=module,
        function=function,
        version=version
    )

def get_function_name(file_path: str) -> str:
    """从文件路径提取功能名称
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 功能名称
    """
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    
    # 处理特殊文件名模式
    if '_' in base_name:
        parts = base_name.split('_')
        if len(parts) >= 2:
            # 检查是否是特定类型的文件
            if any(suffix in parts[-1] for suffix in ['model', 'api', 'service', 'controller', 'util']):
                return parts[0].upper()
            else:
                return parts[0].upper()
    
    # 对于其他文件，使用整个基本名称
    return base_name.upper()

def analyze_file_dependencies(file_path: str) -> List[str]:
    """分析文件依赖关系
    
    Args:
        file_path: 文件路径
        
    Returns:
        List[str]: 依赖文件列表
    """
    file_ext = os.path.splitext(file_path)[1]
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    parts = rel_path.split(os.sep)
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]
    dependencies = []
    
    # 根据文件类型和位置识别依赖关系
    if file_ext == '.py':
        # 读取文件内容以分析导入
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 提取import语句
            import_pattern = r'^(?:from\s+([.\w]+)\s+import|import\s+([.\w]+))'
            imports = []
            
            for line in content.split('\n'):
                match = re.match(import_pattern, line)
                if match:
                    module = match.group(1) or match.group(2)
                    if any(module.startswith(m) for m in PROJECT_MODULES):
                        imports.append(module)
            
            # 将导入模块转换为可能的文件路径
            for module in imports:
                module_parts = module.split('.')
                if len(module_parts) > 1:
                    # 尝试找到相应的文件
                    module_path = os.path.join(ROOT_DIR, *module_parts) + '.py'
                    if os.path.exists(module_path):
                        dependencies.append(module_path)
                    else:
                        # 尝试作为包来导入
                        init_path = os.path.join(ROOT_DIR, *module_parts, '__init__.py')
                        if os.path.exists(init_path):
                            dependencies.append(init_path)
        except Exception as e:
            logger.warning(f"分析文件 {file_path} 依赖关系时出错: {str(e)}")
    
    # 基于文件路径猜测相关文件
    if 'models' in rel_path:
        # 模型文件可能与API、服务相关
        api_path = os.path.join(ROOT_DIR, parts[0], 'api', f"{base_name.replace('_model', '')}_api.py")
        service_path = os.path.join(ROOT_DIR, parts[0], 'services', f"{base_name.replace('_model', '')}_service.py")
        
        if os.path.exists(api_path):
            dependencies.append(api_path)
        
        if os.path.exists(service_path):
            dependencies.append(service_path)
    
    elif 'api' in rel_path:
        # API文件可能与模型、前端模板相关
        model_path = os.path.join(ROOT_DIR, parts[0], 'models', f"{base_name.replace('_api', '')}_model.py")
        template_path = os.path.join(ROOT_DIR, 'world', 'templates', parts[0].lower(), f"{base_name.replace('_api', '')}.html")
        
        if os.path.exists(model_path):
            dependencies.append(model_path)
        
        if os.path.exists(template_path):
            dependencies.append(template_path)
    
    elif 'services' in rel_path:
        # 服务文件可能与模型、API相关
        model_path = os.path.join(ROOT_DIR, parts[0], 'models', f"{base_name.replace('_service', '')}_model.py")
        api_path = os.path.join(ROOT_DIR, parts[0], 'api', f"{base_name.replace('_service', '')}_api.py")
        
        if os.path.exists(model_path):
            dependencies.append(model_path)
        
        if os.path.exists(api_path):
            dependencies.append(api_path)
    
    return dependencies

def generate_quantum_entangle_channel(file_path: str) -> str:
    """为文件生成量子纠缠信道，包含更准确的依赖关系
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 量子纠缠信道
    """
    # 解析文件类型和模块
    file_name = os.path.basename(file_path)
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    parts = rel_path.split(os.sep)
    file_ext = os.path.splitext(file_path)[1]
    
    # 确定文件类型
    file_type = FILE_TYPE_MAPPING.get(file_ext, 'DOC')
    
    # 确定模块
    if len(parts) > 1:
        module = parts[0].upper()
    else:
        module = 'CORE'
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    
    # 生成一致的强度（基于文件路径的哈希）
    file_hash = hashlib.md5(rel_path.encode()).hexdigest()
    strength = 0.90 + float(int(file_hash[:4], 16) % 900) / 10000
    strength = round(strength, 2)
    
    # 分析依赖关系
    dependencies = analyze_file_dependencies(file_path)
    
    # 准备相关对象列表
    related_objects = []
    
    for dep in dependencies:
        # 转换为量子格式的路径
        dep_ext = os.path.splitext(dep)[1]
        if dep_ext in CONVERSION_RULES:
            quantum_ext = CONVERSION_RULES[dep_ext]
            quantum_path = os.path.splitext(dep)[0] + quantum_ext
            # 转换为相对路径
            rel_quantum_path = os.path.relpath(quantum_path, ROOT_DIR)
            related_objects.append(f'    "{rel_quantum_path}"')
    
    # 如果没有找到相关文件，添加默认相关对象
    if not related_objects:
        related_objects.append(f'    "QSM/api/qsm_api.qpy"')
        related_objects.append(f'    "world/templates/base.qentl"')
    
    return QE_TEMPLATE.format(
        type=file_type,
        module=module,
        timestamp=timestamp,
        strength=strength,
        objects="\n".join(related_objects)
    )

# ============================== 转换功能函数 ==============================

def convert_python_to_qpy(content: str) -> str:
    """将Python代码转换为QPy格式
    
    Args:
        content: Python代码内容
        
    Returns:
        str: QPy格式的代码
    """
    # 替换语法元素
    for old, new in SYNTAX_RULES['python'].items():
        content = content.replace(old, new)
    
    # 替换装饰器
    content = re.sub(r'@(\w+)\((.*?)\)', r'@\1(\2)', content)
    
    # 处理导入语句
    import_lines = []
    lines = content.split('\n')
    clean_lines = []
    in_import_block = False
    import_block_lines = []
    
    for line in lines:
        if line.startswith('@import ') or line.startswith('@from '):
            if not in_import_block:
                in_import_block = True
                import_block_lines.append('@imports')
            
            # 清理导入语句格式
            if line.startswith('@import '):
                module = line.replace('@import ', '').strip()
                if ',' in module:
                    modules = [m.strip() for m in module.split(',')]
                    for m in modules:
                        import_block_lines.append(f'  standard: [{m}]')
                else:
                    import_block_lines.append(f'  standard: [{module}]')
            
            elif line.startswith('@from '):
                parts = line.split(' import ')
                if len(parts) == 2:
                    from_module = parts[0].replace('@from ', '').strip()
                    imports = parts[1].strip()
                    
                    if ',' in imports:
                        imports = [i.strip() for i in imports.split(',')]
                        import_str = ', '.join(imports)
                        import_block_lines.append(f'  {from_module}: [{import_str}]')
                    else:
                        import_block_lines.append(f'  {from_module}: [{imports}]')
        else:
            if in_import_block:
                in_import_block = False
                import_lines.extend(import_block_lines)
                import_block_lines = []
            clean_lines.append(line)
    
    # 如果还有导入块尚未处理，添加到导入行列表
    if import_block_lines:
        import_lines.extend(import_block_lines)
    
    # 重新组织内容
    if import_lines:
        # 找到shebang和编码行的位置
        shebang_index = -1
        encoding_index = -1
        docstring_end_index = -1
        
        for i, line in enumerate(clean_lines):
            if line.startswith('#!'):
                shebang_index = i
            elif line.startswith('# -*-') or line.startswith('# coding='):
                encoding_index = i
            elif line.startswith('"""') or line.startswith("'''"):
                if docstring_end_index == -1:  # 找到docstring开始
                    for j, search_line in enumerate(clean_lines[i+1:], i+1):
                        if search_line.endswith('"""') or search_line.endswith("'''"):
                            docstring_end_index = j
                            break
        
        insert_index = max(shebang_index, encoding_index, docstring_end_index) + 1
        
        if insert_index >= 0:
            clean_lines = clean_lines[:insert_index] + [''] + import_lines + [''] + clean_lines[insert_index:]
        else:
            clean_lines = import_lines + [''] + clean_lines
    
    # 替换旧的Python常量定义
    constants_block = []
    i = 0
    while i < len(clean_lines):
        line = clean_lines[i]
        if re.match(r'^[A-Z_]+\s*=', line) and not '@' in line:
            if not constants_block:
                constants_block.append('@constants')
            
            const_line = line.split('=', 1)
            const_name = const_line[0].strip()
            const_value = const_line[1].strip() if len(const_line) > 1 else ''
            
            constants_block.append(f'  {const_name} = {const_value}')
            clean_lines.pop(i)
        else:
            i += 1
    
    # 如果有常量块，插入到文件前部
    if constants_block:
        import_end_index = -1
        for i, line in enumerate(clean_lines):
            if '@imports' in line:
                for j, search_line in enumerate(clean_lines[i:], i):
                    if search_line.strip() == '' and j > i:
                        import_end_index = j
                        break
        
        if import_end_index >= 0:
            clean_lines = clean_lines[:import_end_index] + [''] + constants_block + [''] + clean_lines[import_end_index:]
        else:
            clean_lines = [''] + constants_block + [''] + clean_lines
    
    # 替换类初始化方法
    content = '\n'.join(clean_lines)
    content = re.sub(r'@constructor\s*\(\s*self\s*,', '@constructor(', content)
    
    # 替换main入口
    content = content.replace('if __name__ == "__main__":', 'if __name__ == "__main__":')
    
    return content

def convert_javascript_to_qjs(content: str) -> str:
    """将JavaScript代码转换为QJS格式
    
    Args:
        content: JavaScript代码内容
        
    Returns:
        str: QJS格式的代码
    """
    # 替换语法元素
    for old, new in SYNTAX_RULES['javascript'].items():
        content = content.replace(old, new)
    
    # 处理导入语句
    lines = content.split('\n')
    clean_lines = []
    import_lines = []
    
    for line in lines:
        if line.strip().startswith('import ') or line.strip().startswith('require('):
            if "import " in line:
                parts = line.split('import')
                if len(parts) == 2:
                    modules = parts[1].strip().replace('{', '').replace('}', '').replace(';', '').split(',')
                    modules = [m.strip() for m in modules if m.strip()]
                    if modules:
                        import_lines.append(f'@import quantum_ui: [{", ".join(modules)}]')
            elif "require(" in line:
                match = re.search(r'require\([\'"](.+?)[\'"]\)', line)
                if match:
                    module = match.group(1)
                    import_lines.append(f'@import quantum_ui: [{module}]')
        else:
            clean_lines.append(line)
    
    # 添加导入语句块
    if import_lines:
        content = '\n'.join(import_lines) + '\n\n' + '\n'.join(clean_lines)
    else:
        content = '\n'.join(clean_lines)
    
    # 添加量子组件声明
    if '@class' in content:
        content = content.replace('@class', '@quantum_component\n@class')
    
    return content

def convert_css_to_qcss(content: str) -> str:
    """将CSS代码转换为QCSS格式
    
    Args:
        content: CSS代码内容
        
    Returns:
        str: QCSS格式的代码
    """
    # 替换语法元素
    for old, new in SYNTAX_RULES['css'].items():
        content = content.replace(old, new)
    
    # 量子主题变量
    theme_vars = """
@quantum_theme
  --q-primary: #3a86ff
  --q-secondary: #8338ec
  --q-success: #38b000
  --q-warning: #f8b400
  --q-danger: #ef233c
  --q-info: #4cc9f0
  --q-light: #f8f9fa
  --q-dark: #212529
  --q-background: #ffffff
  --q-text: #212529
  --q-border-radius: 4px
  --q-transition: 0.3s ease-in-out
  --q-shadow: 0 2px 5px rgba(0, 0, 0, 0.1)

@quantum_theme[dark]
  --q-primary: #90b4ff
  --q-secondary: #be9ef8
  --q-success: #7ae582
  --q-warning: #f9c74f
  --q-danger: #ef476f
  --q-info: #a2d6f9
  --q-light: #343a40
  --q-dark: #f8f9fa
  --q-background: #121212
  --q-text: #f8f9fa
  --q-border-radius: 4px
  --q-transition: 0.3s ease-in-out
  --q-shadow: 0 2px 5px rgba(255, 255, 255, 0.1)
"""
    
    # 检查是否已经有主题变量
    if '@quantum_theme' not in content:
        content = theme_vars + '\n\n' + content
    
    # 转换选择器为量子选择器
    content = re.sub(r'\.([a-zA-Z\-_]+)\s*{', r'@quantum_selector .\1 {', content)
    content = re.sub(r'#([a-zA-Z\-_0-9]+)\s*{', r'@quantum_selector #\1 {', content)
    
    # 添加量子动画
    content = re.sub(r'@quantum_keyframes\s+([a-zA-Z\-_0-9]+)\s*{', r'@quantum_animation \1 {', content)
    
    return content

def convert_html_to_qentl(content: str) -> str:
    """将HTML代码转换为QEntl模板格式
    
    Args:
        content: HTML代码内容
        
    Returns:
        str: QEntl模板格式的代码
    """
    # 替换语法元素
    for old, new in SYNTAX_RULES['html'].items():
        content = content.replace(old, new)
    
    # 添加量子模板指令
    content = re.sub(r'<qentl.*?>', r'<qentl @quantum_template>', content)
    
    # 转换条件和循环
    content = re.sub(r'{%\s*if\s+(.*?)\s*%}', r'@if (\1)', content)
    content = re.sub(r'{%\s*else\s*%}', r'@else', content)
    content = re.sub(r'{%\s*endif\s*%}', r'@endif', content)
    content = re.sub(r'{%\s*for\s+(.*?)\s+in\s+(.*?)\s*%}', r'@for (\1 in \2)', content)
    content = re.sub(r'{%\s*endfor\s*%}', r'@endfor', content)
    
    # 转换变量
    content = re.sub(r'{{\s*(.*?)\s*}}', r'@{{\1}}', content)
    
    # 添加量子状态声明
    if '<qentl @quantum_template>' in content:
        insert_pos = content.find('<qentl @quantum_template>') + len('<qentl @quantum_template>')
        quantum_state = """

@quantum_state
  page: {
    title: "量子页面",
    description: "基于量子纠缠原理的网页"
  }
  user: {
    isLoggedIn: false,
    name: ""
  }
  theme: "light"
  loading: false

"""
        content = content[:insert_pos] + quantum_state + content[insert_pos:]
    
    # 添加量子事件处理
    content = re.sub(r'onclick="(.*?)"', r'@quantum_click="\1"', content)
    content = re.sub(r'onchange="(.*?)"', r'@quantum_change="\1"', content)
    content = re.sub(r'onsubmit="(.*?)"', r'@quantum_submit="\1"', content)
    
    return content

def convert_markdown_to_qentl(content: str) -> str:
    """将Markdown转换为QEntl文档格式
    
    Args:
        content: Markdown内容
        
    Returns:
        str: QEntl文档格式的内容
    """
    # 替换标题
    for old, new in SYNTAX_RULES['markdown'].items():
        content = re.sub(rf'^{old}(.*?)$', rf'{new}\1', content, flags=re.MULTILINE)
    
    # 转换链接
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'@link(url="\2"){\1}', content)
    
    # 转换图片
    content = re.sub(r'!\[(.*?)\]\((.*?)\)', r'@image(src="\2", alt="\1")', content)
    
    # 转换强调
    content = re.sub(r'\*\*(.*?)\*\*', r'@strong{\1}', content)
    content = re.sub(r'\*(.*?)\*', r'@emphasis{\1}', content)
    
    # 转换列表
    content = re.sub(r'^- (.*?)$', r'@list_item{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^\d+\. (.*?)$', r'@ordered_item{\1}', content, flags=re.MULTILINE)
    
    # 转换代码块
    content = re.sub(r'```(\w*)\n(.*?)```', r'@code_block(language="\1"){\2}', content, flags=re.DOTALL)
    
    # 转换行内代码
    content = re.sub(r'`(.*?)`', r'@code{\1}', content)
    
    # 添加文档结构
    content = '@quantum_document\n\n' + content
    
    return content

def convert_content(content: str, file_ext: str) -> str:
    """根据文件类型调用相应的转换函数
    
    Args:
        content: 文件内容
        file_ext: 文件扩展名
        
    Returns:
        str: 转换后的内容
    """
    if file_ext == '.py':
        return convert_python_to_qpy(content)
    elif file_ext == '.js':
        return convert_javascript_to_qjs(content)
    elif file_ext == '.css':
        return convert_css_to_qcss(content)
    elif file_ext == '.html':
        return convert_html_to_qentl(content)
    elif file_ext == '.md':
        return convert_markdown_to_qentl(content)
    elif file_ext == '.json':
        # JSON只需要添加量子标记，不需要转换内容
        return '@quantum_data\n\n' + content
    elif file_ext == '.xml':
        # XML转换为量子XML格式
        return '@quantum_xml\n\n' + content
    elif file_ext == '.txt':
        # 纯文本转换为量子文本格式
        return '@quantum_text\n\n' + content
    else:
        # 对于不支持的格式，保持原样
        return content

def backup_file(file_path: str) -> bool:
    """备份文件到历史目录
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 获取相对路径
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        
        # 创建带时间戳的目标路径
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = os.path.join(HISTORY_DIR, timestamp)
        target_path = os.path.join(target_dir, rel_path)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # 复制文件
        shutil.copy2(file_path, target_path)
        logger.debug(f"已备份: {file_path} -> {target_path}")
        return True
    
    except Exception as e:
        logger.error(f"备份文件 {file_path} 时出错: {str(e)}")
        return False

def move_to_reference(file_path: str, dry_run: bool = False) -> bool:
    """将文件移动到参考目录
    
    Args:
        file_path: 要移动的文件路径
        dry_run: 如果为True，则不实际移动，只输出日志
        
    Returns:
        bool: 是否成功
    """
    try:
        # 获取相对路径
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        
        # 确定目标路径
        target_path = os.path.join(REFERENCE_DIR, rel_path)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        if dry_run:
            logger.info(f"[DRY RUN] 将移动: {file_path} -> {target_path}")
            return True
        
        # 移动文件
        shutil.move(file_path, target_path)
        logger.info(f"已移动: {file_path} -> {target_path}")
        return True
    
    except Exception as e:
        logger.error(f"移动文件 {file_path} 时出错: {str(e)}")
        return False

def convert_file(file_path: str, output_format: Optional[str] = None, dry_run: bool = False) -> Tuple[bool, Optional[str]]:
    """转换文件为量子格式
    
    Args:
        file_path: 文件路径
        output_format: 输出格式，默认根据文件扩展名确定
        dry_run: 是否只模拟执行
        
    Returns:
        tuple: (是否成功, 输出文件路径)
    """
    try:
        # 确定输出格式
        file_ext = os.path.splitext(file_path)[1]
        if output_format is None:
            if file_ext in CONVERSION_RULES:
                output_format = CONVERSION_RULES[file_ext]
            else:
                logger.warning(f"无法确定文件 {file_path} 的输出格式，跳过转换")
                return False, None
        
        # 备份文件
        if not dry_run:
            backup_file(file_path)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 生成量子基因编码和纠缠信道
        qg_code = generate_quantum_gene_code(file_path)
        qe_channel = generate_quantum_entangle_channel(file_path)
        
        # 转换内容
        converted_content = convert_content(content, file_ext)
        
        # 构建新文件的内容
        shebang_line = "#!/usr/bin/env qentl\n# -*- coding: utf-8 -*-\n\n"
        
        # 检查是否已经有shebang行
        if not converted_content.startswith('#!'):
            # 查找文件文档字符串
            docstring_match = re.search(r'^("""|\'\'\')(.*?)("""|\'\'\')', converted_content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(0)
                docstring_pos = converted_content.find(docstring) + len(docstring)
                new_content = converted_content[:docstring_pos] + "\n" + qg_code + "\n" + qe_channel + "\n" + converted_content[docstring_pos:]
                final_content = shebang_line + new_content
            else:
                final_content = shebang_line + converted_content + "\n" + qg_code + "\n" + qe_channel
        else:
            # 文件已经有shebang行，查找适当位置插入量子编码
            lines = converted_content.split('\n')
            insert_pos = 0
            
            # 查找合适的插入位置
            for i, line in enumerate(lines):
                if line.startswith('#') or line.strip() == '':
                    insert_pos = i + 1
                else:
                    break
            
            # 寻找docstring
            docstring_start = -1
            docstring_end = -1
            for i, line in enumerate(lines[insert_pos:], insert_pos):
                if (line.startswith('"""') or line.startswith("'''")) and docstring_start == -1:
                    docstring_start = i
                    continue
                if (line.endswith('"""') or line.endswith("'''")) and docstring_start != -1:
                    docstring_end = i
                    break
            
            # 在适当位置插入量子编码
            if docstring_end != -1:
                insert_pos = docstring_end + 1
            
            lines.insert(insert_pos, qe_channel)
            lines.insert(insert_pos, qg_code)
            final_content = '\n'.join(lines)
        
        # 确定输出文件路径
        base_name = os.path.splitext(file_path)[0]
        output_file = base_name + output_format
        
        if dry_run:
            logger.info(f"[DRY RUN] 将转换: {file_path} -> {output_file}")
            return True, output_file
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 写入转换后的内容
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        logger.info(f"已转换: {file_path} -> {output_file}")
        return True, output_file
    
    except Exception as e:
        logger.error(f"转换文件 {file_path} 时出错: {str(e)}")
        return False, None

# ============================== 批量转换函数 ==============================

def should_exclude(path: str, exclude_patterns: List[str] = None) -> bool:
    """检查路径是否应该被排除
    
    Args:
        path: 文件或目录路径
        exclude_patterns: 排除模式列表
        
    Returns:
        bool: 是否应该排除
    """
    if exclude_patterns is None:
        exclude_patterns = EXCLUDE_PATTERNS
    
    # 获取相对路径，避免完整路径匹配问题
    rel_path = os.path.relpath(path, ROOT_DIR)
    
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or any(part for part in rel_path.split(os.sep) if fnmatch.fnmatch(part, pattern)):
            return True
    
    return False

def get_module_files(module_path: str, priority_dirs: List[str] = None, priority_exts: List[str] = None) -> List[str]:
    """获取模块内的文件，按优先级排序
    
    Args:
        module_path: 模块路径
        priority_dirs: 优先级目录列表
        priority_exts: 优先级文件类型列表
        
    Returns:
        list: 排序后的文件路径列表
    """
    if not os.path.exists(module_path):
        logger.warning(f"模块路径不存在: {module_path}")
        return []
    
    if priority_dirs is None:
        priority_dirs = DIRECTORY_PRIORITY
    
    if priority_exts is None:
        priority_exts = FILE_TYPE_PRIORITY
    
    # 收集所有文件
    all_files = []
    
    for root, dirs, files in os.walk(module_path):
        # 跳过被排除的目录
        if should_exclude(root):
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 跳过被排除的文件
            if should_exclude(file_path):
                continue
            
            # 排除已经转换过的文件
            if any(file.endswith(ext) for ext in ['.qpy', '.qjs', '.qcss', '.qentl', '.qjson', '.qxml', '.qtxt']):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, module_path)
            _, ext = os.path.splitext(file)
            
            # 检查是否是支持的文件类型
            if ext not in CONVERSION_RULES:
                continue
            
            # 计算优先级
            dir_priority = float('inf')
            for i, dir_name in enumerate(priority_dirs):
                if f"/{dir_name}/" in f"/{rel_path}/":
                    dir_priority = i
                    break
            
            ext_priority = float('inf')
            for i, ext_type in enumerate(priority_exts):
                if file.endswith(ext_type):
                    ext_priority = i
                    break
            
            all_files.append((file_path, dir_priority, ext_priority))
    
    # 按优先级排序
    all_files.sort(key=lambda x: (x[1], x[2]))
    
    return [file_path for file_path, _, _ in all_files]

def convert_directory(dir_path: str, pattern: str = None, exclude: str = None, dry_run: bool = False) -> Tuple[int, int]:
    """转换目录中的文件为量子格式
    
    Args:
        dir_path: 要转换的目录路径
        pattern: 文件匹配模式（支持通配符）
        exclude: 要排除的文件模式
        dry_run: 如果为True，则不实际转换，只输出日志
        
    Returns:
        tuple: (成功数, 失败数)
    """
    success_count = 0
    error_count = 0
    
    # 获取所有要转换的文件（已排序）
    files = get_module_files(dir_path)
    total_files = len(files)
    
    if total_files == 0:
        logger.info(f"目录 {dir_path} 中没有找到需要转换的文件")
        return 0, 0
    
    logger.info(f"目录 {dir_path} 中找到 {total_files} 个文件需要转换")
    
    # 显示进度条
    for i, file_path in enumerate(files):
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        progress = (i + 1) / total_files * 100
        
        # 自定义过滤
        if pattern and not fnmatch.fnmatch(os.path.basename(file_path), pattern):
            continue
        
        if exclude and fnmatch.fnmatch(os.path.basename(file_path), exclude):
            continue
        
        logger.info(f"[{progress:.1f}%] 转换文件: {rel_path}")
        
        # 转换文件
        success, output_file = convert_file(file_path, dry_run=dry_run)
        
        if success:
            # 移动原文件到参考目录
            if move_to_reference(file_path, dry_run=dry_run):
                success_count += 1
            else:
                error_count += 1
        else:
            error_count += 1
    
    success_rate = success_count / total_files * 100 if total_files > 0 else 0
    logger.info(f"目录 {dir_path} 转换完成。成功: {success_count}/{total_files}，失败: {error_count}，成功率: {success_rate:.1f}%")
    
    return success_count, error_count

def convert_module(module_name: str, dry_run: bool = False) -> bool:
    """转换单个模块
    
    Args:
        module_name: 模块名称
        dry_run: 如果为True，则不实际转换，只输出日志
        
    Returns:
        bool: 是否成功
    """
    module_path = os.path.join(ROOT_DIR, module_name)
    
    if not os.path.exists(module_path):
        logger.warning(f"模块不存在: {module_path}")
        return False
    
    logger.info(f"开始转换模块: {module_name}")
    
    success_count, error_count = convert_directory(module_path, dry_run=dry_run)
    
    success = error_count == 0
    return success

def convert_project(modules: List[str] = None, dry_run: bool = False) -> Tuple[List[str], List[str]]:
    """转换整个项目
    
    Args:
        modules: 要转换的模块列表，默认为所有模块
        dry_run: 如果为True，则不实际转换，只输出日志
        
    Returns:
        tuple: (成功模块列表, 失败模块列表)
    """
    if modules is None:
        modules = PROJECT_MODULES
    
    logger.info(f"开始转换项目，包含 {len(modules)} 个模块")
    start_time = time.time()
    
    success_modules = []
    error_modules = []
    
    for module_name in modules:
        logger.info(f"\n{'='*50}\n开始处理模块: {module_name}\n{'='*50}")
        
        if convert_module(module_name, dry_run):
            success_modules.append(module_name)
        else:
            error_modules.append(module_name)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    logger.info(f"\n{'='*50}")
    logger.info(f"项目转换完成，耗时: {elapsed_time:.2f} 秒")
    logger.info(f"成功模块: {len(success_modules)}/{len(modules)}")
    
    if success_modules:
        logger.info(f"成功模块列表: {', '.join(success_modules)}")
    
    if error_modules:
        logger.warning(f"失败模块列表: {', '.join(error_modules)}")
    
    return success_modules, error_modules

def run_command(command: str, dry_run: bool = False) -> int:
    """运行命令
    
    Args:
        command: 要运行的命令
        dry_run: 如果为True，则不实际运行，只输出日志
        
    Returns:
        int: 命令退出码
    """
    if dry_run:
        logger.info(f"[DRY RUN] 将运行命令: {command}")
        return 0
    
    try:
        logger.info(f"运行命令: {command}")
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"命令执行成功，退出码: {result.returncode}")
        if result.stdout:
            logger.debug(f"标准输出:\n{result.stdout}")
        if result.stderr:
            logger.debug(f"标准错误:\n{result.stderr}")
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败，退出码: {e.returncode}")
        if e.stdout:
            logger.error(f"标准输出:\n{e.stdout}")
        if e.stderr:
            logger.error(f"标准错误:\n{e.stderr}")
        return e.returncode

# ============================== 命令行接口 ==============================

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='量子转换工具 - 将项目文件转换为量子格式'
    )
    
    # 基本选项
    parser.add_argument(
        'path',
        type=str,
        nargs='?',
        help='要转换的文件或目录路径（默认为整个项目）'
    )
    
    # 转换模式
    mode_group = parser.add_mutually_exclusive_group()
    
    mode_group.add_argument(
        '--file', '-f',
        action='store_true',
        help='指定路径为单个文件'
    )
    
    mode_group.add_argument(
        '--directory', '-d',
        action='store_true',
        help='指定路径为目录'
    )
    
    mode_group.add_argument(
        '--module', '-m',
        action='store_true',
        help='指定路径为模块名'
    )
    
    mode_group.add_argument(
        '--project', '-p',
        action='store_true',
        help='转换整个项目（默认行为）'
    )
    
    # 模块选项
    parser.add_argument(
        '--modules',
        type=str,
        nargs='+',
        help='要转换的模块列表（默认为全部）'
    )
    
    # 文件过滤选项
    parser.add_argument(
        '--pattern',
        type=str,
        help='文件匹配模式（支持通配符，仅在转换目录时有效）'
    )
    
    parser.add_argument(
        '--exclude',
        type=str,
        help='要排除的文件模式（支持通配符，仅在转换目录时有效）'
    )
    
    # 输出选项
    parser.add_argument(
        '--output-format', '-o',
        type=str,
        help='指定输出格式（如.qpy, .qjs, .qcss, .qentl）'
    )
    
    # 执行选项
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='不实际转换，只输出日志'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )
    
    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f'量子转换工具 v{VERSION}'
    )
    
    return parser.parse_args()

def main() -> int:
    """主函数
    
    Returns:
        int: 退出码
    """
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 显示欢迎信息
    logger.info(f"===== 量子转换工具 v{VERSION} =====")
    logger.info(f"运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确定转换模式
    if args.file:
        if not args.path:
            logger.error("文件模式需要指定文件路径")
            return 1
        
        logger.info(f"转换单个文件: {args.path}")
        success, output_file = convert_file(args.path, args.output_format, args.dry_run)
        
        if success:
            if move_to_reference(args.path, args.dry_run):
                logger.info(f"转换成功: {args.path} -> {output_file}")
                return 0
            else:
                logger.error(f"转换成功但移动失败: {args.path}")
                return 1
        else:
            logger.error(f"转换失败: {args.path}")
            return 1
    
    elif args.directory:
        if not args.path:
            logger.error("目录模式需要指定目录路径")
            return 1
        
        logger.info(f"转换目录: {args.path}")
        success_count, error_count = convert_directory(
            args.path, 
            pattern=args.pattern,
            exclude=args.exclude,
            dry_run=args.dry_run
        )
        
        return 0 if error_count == 0 else 1
    
    elif args.module:
        if not args.path:
            logger.error("模块模式需要指定模块名")
            return 1
        
        logger.info(f"转换模块: {args.path}")
        success = convert_module(args.path, args.dry_run)
        
        return 0 if success else 1
    
    else:  # 项目模式（默认）
        logger.info("转换整个项目")
        modules = args.modules if args.modules else PROJECT_MODULES
        success_modules, error_modules = convert_project(modules, args.dry_run)
        
        return 0 if not error_modules else 1

# ============================== 脚本入口 ==============================

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n操作被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"执行过程中发生未处理的错误: {str(e)}")
        sys.exit(1) 