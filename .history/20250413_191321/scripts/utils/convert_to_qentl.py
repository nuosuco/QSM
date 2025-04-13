#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QEntl转换工具 - 将不同语言文件转换为QEntl格式

此脚本将项目中的其他语言文件（如.py、.js、.css、.html等）
转换为相应的QEntl语言格式（.qentl、.qpy、.qjs、.qcss等），
并将原始文件移动到参考目录。
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
from pathlib import Path

# 目录设置
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REFERENCE_DIR = os.path.join(ROOT_DIR, 'reference')
LOG_DIR = os.path.join(ROOT_DIR, '.logs')

# 创建日志目录
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.FileHandler(os.path.join(LOG_DIR, 'convert_to_qentl.log')),
    logging.StreamHandler()
  ]
)
logger = logging.getLogger('Convert-To-QEntl')

# 确保参考目录存在
os.makedirs(REFERENCE_DIR, exist_ok=True)

# 定义转换规则
CONVERSION_RULES = {
  '.py': '.qentl',   # Python转QEntl
  '.js': '.qjs',     # JavaScript转QJS
  '.css': '.qcss',   # CSS转QCSS
  '.html': '.qentl', # HTML转QEntl模板
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
  }
}

def generate_quantum_gene_code(file_path):
    """为文件生成量子基因编码
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 量子基因编码
    """
    # 解析文件类型和模块
    file_name = os.path.basename(file_path)
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    parts = rel_path.split(os.sep)
    
    # 确定类型
    if '.py' in file_path:
        file_type = 'CODE'
    elif '.js' in file_path:
        file_type = 'UI'
    elif '.css' in file_path:
        file_type = 'STYLE'
    elif '.html' in file_path:
        file_type = 'TEMPLATE'
    else:
        file_type = 'DOC'
    
    # 确定模块
    if len(parts) > 1:
        module = parts[0].upper()
    else:
        module = 'CORE'
    
    # 确定功能
    if '_' in file_name:
        function = file_name.split('_')[0].upper()
    else:
        function = file_name.split('.')[0].upper()
    
    # 随机版本号
    version = f"{chr(65 + random.randint(0, 25))}{random.randint(1, 5)}"\
              f"{chr(65 + random.randint(0, 25))}{random.randint(1, 5)}"
    
    return QG_TEMPLATE.format(
        type=file_type,
        module=module,
        function=function,
        version=version
    )

def generate_quantum_entangle_channel(file_path):
    """为文件生成量子纠缠信道
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 量子纠缠信道
    """
    # 解析文件类型和模块
    file_name = os.path.basename(file_path)
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    parts = rel_path.split(os.sep)
    
    # 确定类型
    if '.py' in file_path:
        file_type = 'CODE'
    elif '.js' in file_path:
        file_type = 'UI'
    elif '.css' in file_path:
        file_type = 'STYLE'
    elif '.html' in file_path:
        file_type = 'TEMPLATE'
    else:
        file_type = 'DOC'
    
    # 确定模块
    if len(parts) > 1:
        module = parts[0].upper()
    else:
        module = 'CORE'
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    
    # 随机强度
    strength = round(random.uniform(0.90, 0.99), 2)
    
    # 相关对象
    related_objects = []
    
    # 基于文件路径猜测相关文件
    if 'models' in rel_path:
        # 模型文件可能与API、服务相关
        parent_dir = os.path.dirname(rel_path)
        base_name = os.path.splitext(file_name)[0]
        
        api_path = f"{parts[0]}/api/{base_name.replace('_model', '')}_api.qentl"
        service_path = f"{parts[0]}/services/{base_name.replace('_model', '')}_service.qentl"
        
        related_objects.append(f'    "{api_path}"')
        related_objects.append(f'    "{service_path}"')
    
    elif 'api' in rel_path:
        # API文件可能与模型、前端模板相关
        parent_dir = os.path.dirname(rel_path)
        base_name = os.path.splitext(file_name)[0]
        
        model_path = f"{parts[0]}/models/{base_name.replace('_api', '')}_model.qentl"
        template_path = f"world/templates/{parts[0].lower()}/{base_name.replace('_api', '')}.qentl"
        
        related_objects.append(f'    "{model_path}"')
        related_objects.append(f'    "{template_path}"')
    
    elif 'services' in rel_path:
        # 服务文件可能与模型、API相关
        parent_dir = os.path.dirname(rel_path)
        base_name = os.path.splitext(file_name)[0]
        
        model_path = f"{parts[0]}/models/{base_name.replace('_service', '')}_model.qentl"
        api_path = f"{parts[0]}/api/{base_name.replace('_service', '')}_api.qentl"
        
        related_objects.append(f'    "{model_path}"')
        related_objects.append(f'    "{api_path}"')
    
    # 如果没有找到相关文件，添加默认相关对象
    if not related_objects:
        related_objects.append(f'    "QSM/api/qsm_api.qentl"')
        related_objects.append(f'    "world/templates/base.qentl"')
    
    return QE_TEMPLATE.format(
        type=file_type,
        module=module,
        timestamp=timestamp,
        strength=strength,
        objects="\n".join(related_objects)
    )

def convert_python_to_qentl(content):
    """将Python代码转换为QEntl格式
    
    Args:
        content: Python代码内容
        
    Returns:
        str: QEntl格式的代码
    """
    # 替换语法元素
    for old, new in SYNTAX_RULES['python'].items():
        content = content.replace(old, new)
    
    # 替换装饰器
    content = re.sub(r'@(\w+)\((.*?)\)', r'@\1(\2)', content)
    
    # 清理导入语句
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

def convert_javascript_to_qjs(content):
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

def convert_css_to_qcss(content):
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

def convert_html_to_qentl(content):
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

def convert_file(file_path, output_format=None, dry_run=False):
    """转换文件为QEntl格式
    
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
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 生成量子基因编码和纠缠信道
        qg_code = generate_quantum_gene_code(file_path)
        qe_channel = generate_quantum_entangle_channel(file_path)
        
        # 确定转换方法
        if file_ext == '.py':
            converted_content = convert_python_to_qentl(content)
        elif file_ext == '.js':
            converted_content = convert_javascript_to_qjs(content)
        elif file_ext == '.css':
            converted_content = convert_css_to_qcss(content)
        elif file_ext == '.html':
            converted_content = convert_html_to_qentl(content)
        else:
            # 对于不支持的格式，保持原样
            converted_content = content
        
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

def move_to_reference(file_path, dry_run=False):
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

def convert_directory(dir_path, pattern=None, exclude=None, dry_run=False):
    """转换目录中的文件为QEntl格式
    
    Args:
        dir_path: 要转换的目录路径
        pattern: 文件匹配模式（支持通配符）
        exclude: 要排除的文件模式
        dry_run: 如果为True，则不实际转换，只输出日志
        
    Returns:
        tuple: (成功数, 失败数)
    """
    import fnmatch
    
    success_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(dir_path):
        # 排除参考目录和其他不需要转换的目录
        if 'reference' in root or '.git' in root or '.venv' in root or '__pycache__' in root:
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1]
            
            # 检查是否匹配模式
            if pattern and not fnmatch.fnmatch(file, pattern):
                continue
            
            # 检查是否要排除
            if exclude and fnmatch.fnmatch(file, exclude):
                continue
            
            # 检查文件扩展名是否需要转换
            if file_ext in CONVERSION_RULES:
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
    
    return success_count, error_count

def parse_arguments():
    """解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(
        description='将文件转换为QEntl格式并移动原文件到参考目录'
    )
    
    parser.add_argument(
        'path',
        type=str,
        help='要转换的文件或目录路径'
    )
    
    parser.add_argument(
        '--pattern', '-p',
        type=str,
        help='文件匹配模式（支持通配符，仅在转换目录时有效）'
    )
    
    parser.add_argument(
        '--exclude', '-e',
        type=str,
        help='要排除的文件模式（支持通配符，仅在转换目录时有效）'
    )
    
    parser.add_argument(
        '--output-format', '-o',
        type=str,
        help='指定输出格式（如.qentl, .qpy, .qjs, .qcss）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='不实际转换，只输出日志'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    path = args.path
    pattern = args.pattern
    exclude = args.exclude
    output_format = args.output_format
    dry_run = args.dry_run
    
    logger.info("===== QEntl转换工具 =====")
    logger.info(f"路径: {path}")
    logger.info(f"匹配模式: {pattern}")
    logger.info(f"排除模式: {exclude}")
    logger.info(f"输出格式: {output_format}")
    logger.info(f"干运行模式: {'是' if dry_run else '否'}")
    
    # 检查路径是否存在
    if not os.path.exists(path):
        logger.error(f"路径不存在: {path}")
        return 1
    
    # 检查路径是文件还是目录
    if os.path.isfile(path):
        logger.info(f"转换文件: {path}")
        success, output_file = convert_file(path, output_format, dry_run)
        
        if success:
            # 移动原文件到参考目录
            if move_to_reference(path, dry_run):
                logger.info(f"转换成功: {path} -> {output_file}")
                return 0
            else:
                logger.error(f"转换成功但移动失败: {path}")
                return 1
        else:
            logger.error(f"转换失败: {path}")
            return 1
    
    elif os.path.isdir(path):
        logger.info(f"转换目录: {path}")
        success_count, error_count = convert_directory(path, pattern, exclude, dry_run)
        logger.info(f"转换完成。成功: {success_count}，失败: {error_count}")
        return 0 if error_count == 0 else 1
    
    else:
        logger.error(f"无效的路径类型: {path}")
        return 1

# 主入口
if __name__ == "__main__":
    sys.exit(main()) 