#!/usr/bin/env python3
"""
QEntL编译器依赖分析工具
分析quantum_compiler_v2.qentl使用的语言特性，确定最小运行时需求
"""

import re
import sys
from typing import Set, Dict, List, Tuple
from collections import defaultdict

def analyze_source_file(filepath: str) -> Dict[str, Set[str]]:
    """分析QEntL源文件，提取使用的语言特性"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    features = {
        'keywords': set(),
        'operators': set(),
        'builtin_functions': set(),
        'control_flow': set(),
        'data_types': set(),
        'data_structures': set(),
        'function_patterns': set(),
        'error_patterns': set()
    }
    
    # 分析关键字使用
    keyword_patterns = {
        '配置': r'\b配置\b',
        '类型': r'\b类型\b',
        '函数': r'\b函数\b',
        '返回': r'\b返回\b',
        '如果': r'\b如果\b',
        '否则': r'\b否则\b',
        '循环': r'\b循环\b',
        'let': r'\blet\b',
        'import': r'\bimport\b',
        'quantum_class': r'\bquantum_class\b',
        'quantum_interface': r'\bquantum_interface\b',
        'quantum_enum': r'\bquantum_enum\b',
        'quantum_program': r'\bquantum_program\b',
        '新': r'\b新\b',
        'true': r'\btrue\b',
        'false': r'\bfalse\b',
        'null': r'\bnull\b'
    }
    
    for keyword, pattern in keyword_patterns.items():
        if re.search(pattern, content):
            features['keywords'].add(keyword)
    
    # 分析操作符使用
    # 数学操作符
    math_ops = re.findall(r'[+\-*/%]=?', content)
    features['operators'].update(math_ops)
    
    # 比较操作符
    comparison_ops = re.findall(r'[<>]=?|==|!=', content)
    features['operators'].update(comparison_ops)
    
    # 逻辑操作符
    logical_ops = re.findall(r'&&|\|\||!', content)
    features['operators'].update(logical_ops)
    
    # 赋值操作符
    assignment_ops = re.findall(r'=', content)
    features['operators'].update(assignment_ops)
    
    # 量子操作符
    quantum_ops = re.findall(r'[@|][>+]?', content)
    features['operators'].update(quantum_ops)
    
    # 分隔符
    separators = re.findall(r'[{}()\[\],;.:]', content)
    features['operators'].update(separators)
    
    # 分析控制流模式
    # 如果语句
    if_statements = re.findall(r'如果\s*\(', content)
    if len(if_statements) > 0:
        features['control_flow'].add('if_statement')
    
    # 否则分支
    else_branches = re.findall(r'否则\s*{', content)
    if len(else_branches) > 0:
        features['control_flow'].add('else_branch')
    
    # 循环语句
    loop_statements = re.findall(r'循环\s+\w+\s+在\s', content)
    if len(loop_statements) > 0:
        features['control_flow'].add('for_loop')
    
    # 函数调用模式
    function_calls = re.findall(r'(\w+)\(', content)
    # 过滤掉关键字
    builtin_candidates = [f for f in function_calls if f not in features['keywords']]
    
    # 常见内置函数模式
    builtin_patterns = [
        r'长度\(', r'日志\(', r'时间\.', r'数学\.', r'控制台\.',
        r'包含\(', r'添加\(', r'前进\(', r'期望\(', r'检查\('
    ]
    
    for pattern in builtin_patterns:
        if re.search(pattern, content):
            func_name = re.search(pattern, content).group(0).replace('(', '').replace('.', '')
            features['builtin_functions'].add(func_name)
    
    # 分析数据类型
    type_patterns = {
        '字符串': r':\s*字符串',
        '整数': r':\s*整数',
        '布尔': r':\s*布尔',
        '浮点数': r':\s*浮点数',
        '时间戳': r':\s*时间戳',
        '映射': r'映射<',
        '数组': r'数组<|\[\]'
    }
    
    for type_name, pattern in type_patterns.items():
        if re.search(pattern, content):
            features['data_types'].add(type_name)
    
    # 分析数据结构使用
    # 数组字面量
    array_literals = re.findall(r'\[[^\]]*\]', content)
    if len(array_literals) > 0:
        features['data_structures'].add('array_literal')
    
    # 对象字面量
    object_literals = re.findall(r'{[^}]*}', content)
    if len(object_literals) > 0:
        features['data_structures'].add('object_literal')
    
    # 分析函数模式
    # 函数定义
    function_defs = re.findall(r'函数\s+(\w+)\(', content)
    if len(function_defs) > 0:
        features['function_patterns'].add('function_definition')
    
    # 递归调用（自调用）
    for func in function_defs:
        if re.search(rf'\b{func}\(', content):
            features['function_patterns'].add('recursion')
            break
    
    # 高阶函数（函数作为参数）
    function_params = re.findall(r'函数\s*\(', content)
    if len(function_params) > 0:
        features['function_patterns'].add('higher_order_functions')
    
    # 分析错误处理模式
    error_patterns = [
        r'日志\("错误"', r'日志\("警告"', r'语法错误',
        r'未结束的', r'期望', r'错误：'
    ]
    
    for pattern in error_patterns:
        if re.search(pattern, content):
            features['error_patterns'].add('error_reporting')
            break
    
    return features

def generate_runtime_requirements(features: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """根据分析的特征生成运行时需求"""
    
    requirements = {
        'must_have': [],
        'should_have': [],
        'nice_to_have': [],
        'not_needed': []
    }
    
    # 核心关键字（必须支持）
    core_keywords = {'类型', '函数', '返回', '如果', '否则', '循环', 'let'}
    if features['keywords'].intersection(core_keywords):
        requirements['must_have'].append('核心控制流关键字')
    
    # 配置关键字（应该支持）
    if '配置' in features['keywords']:
        requirements['should_have'].append('配置块支持')
    
    # 量子关键字（锦上添花）
    quantum_keywords = {'quantum_class', 'quantum_interface', 'quantum_enum', 'quantum_program'}
    if features['keywords'].intersection(quantum_keywords):
        requirements['nice_to_have'].append('量子编程扩展')
    
    # 操作符需求
    math_ops = features['operators'].intersection({'+', '-', '*', '/', '%'})
    if math_ops:
        requirements['must_have'].append(f'数学操作符: {", ".join(sorted(math_ops))}')
    
    comparison_ops = features['operators'].intersection({'==', '!=', '<', '>', '<=', '>='})
    if comparison_ops:
        requirements['must_have'].append(f'比较操作符: {", ".join(sorted(comparison_ops))}')
    
    logical_ops = features['operators'].intersection({'&&', '||', '!'})
    if logical_ops:
        requirements['must_have'].append(f'逻辑操作符: {", ".join(sorted(logical_ops))}')
    
    # 量子操作符（如果使用）
    quantum_ops = features['operators'].intersection({'@', '|', '@>', '|>', '@<', '|+'})
    if quantum_ops:
        requirements['nice_to_have'].append(f'量子操作符: {", ".join(sorted(quantum_ops))}')
    
    # 控制流需求
    if 'if_statement' in features['control_flow']:
        requirements['must_have'].append('条件语句支持')
    
    if 'else_branch' in features['control_flow']:
        requirements['must_have'].append('否则分支支持')
    
    if 'for_loop' in features['control_flow']:
        requirements['must_have'].append('循环语句支持')
    
    # 数据类型需求
    if '字符串' in features['data_types']:
        requirements['must_have'].append('字符串类型支持')
    
    if '整数' in features['data_types']:
        requirements['must_have'].append('整数类型支持')
    
    if '布尔' in features['data_types']:
        requirements['must_have'].append('布尔类型支持')
    
    if '映射' in features['data_types']:
        requirements['should_have'].append('映射/字典类型支持')
    
    if '数组' in features['data_types']:
        requirements['must_have'].append('数组类型支持')
    
    # 数据结构需求
    if 'array_literal' in features['data_structures']:
        requirements['must_have'].append('数组字面量语法')
    
    if 'object_literal' in features['data_structures']:
        requirements['should_have'].append('对象字面量语法')
    
    # 函数模式需求
    if 'function_definition' in features['function_patterns']:
        requirements['must_have'].append('函数定义和调用')
    
    if 'recursion' in features['function_patterns']:
        requirements['must_have'].append('递归函数支持')
    
    if 'higher_order_functions' in features['function_patterns']:
        requirements['should_have'].append('高阶函数支持')
    
    # 错误处理需求
    if 'error_reporting' in features['error_patterns']:
        requirements['should_have'].append('错误报告机制')
    
    return requirements

def print_analysis_report(features: Dict[str, Set[str]], requirements: Dict[str, List[str]]):
    """打印分析报告"""
    
    print("=" * 80)
    print("QEntL编译器依赖分析报告")
    print("=" * 80)
    
    print(f"\n📊 分析文件: quantum_compiler_v2.qentl")
    print(f"   总关键字使用次数: {sum(len(v) for v in features.values())} 个不同特征")
    
    print("\n🔍 检测到的语言特性:")
    
    print(f"\n  关键字 ({len(features['keywords'])})：")
    for kw in sorted(features['keywords']):
        print(f"    • {kw}")
    
    print(f"\n  操作符 ({len(features['operators'])})：")
    ops_list = sorted(features['operators'])
    for i in range(0, len(ops_list), 8):
        print(f"    • {' '.join(ops_list[i:i+8])}")
    
    print(f"\n  内置函数 ({len(features['builtin_functions'])})：")
    for func in sorted(features['builtin_functions']):
        print(f"    • {func}")
    
    print(f"\n  控制流模式 ({len(features['control_flow'])})：")
    for cf in sorted(features['control_flow']):
        print(f"    • {cf}")
    
    print(f"\n  数据类型 ({len(features['data_types'])})：")
    for dt in sorted(features['data_types']):
        print(f"    • {dt}")
    
    print(f"\n  数据结构 ({len(features['data_structures'])})：")
    for ds in sorted(features['data_structures']):
        print(f"    • {ds}")
    
    print(f"\n  函数模式 ({len(features['function_patterns'])})：")
    for fp in sorted(features['function_patterns']):
        print(f"    • {fp}")
    
    print(f"\n  错误处理 ({len(features['error_patterns'])})：")
    for ep in sorted(features['error_patterns']):
        print(f"    • {ep}")
    
    print("\n" + "=" * 80)
    print("🎯 最小化运行时需求分析")
    print("=" * 80)
    
    print("\n🚨 必须支持 (Must Have):")
    if requirements['must_have']:
        for req in requirements['must_have']:
            print(f"  ✅ {req}")
    else:
        print("  (无)")
    
    print("\n📈 应该支持 (Should Have):")
    if requirements['should_have']:
        for req in requirements['should_have']:
            print(f"  ⚡ {req}")
    else:
        print("  (无)")
    
    print("\n✨ 锦上添花 (Nice to Have):")
    if requirements['nice_to_have']:
        for req in requirements['nice_to_have']:
            print(f"  💎 {req}")
    else:
        print("  (无)")
    
    print("\n❌ 不需要 (Not Needed):")
    if requirements['not_needed']:
        for req in requirements['not_needed']:
            print(f"  🚫 {req}")
    else:
        print("  (无)")
    
    print("\n" + "=" * 80)
    print("📋 实施建议")
    print("=" * 80)
    
    must_have_count = len(requirements['must_have'])
    should_have_count = len(requirements['should_have'])
    nice_to_have_count = len(requirements['nice_to_have'])
    
    print(f"\n阶段1 (核心功能，{must_have_count}项):")
    print("  实现所有'必须支持'的功能，使编译器能够基本运行")
    
    print(f"\n阶段2 (完整功能，{should_have_count}项):")
    print("  实现'应该支持'的功能，提高编译器性能和可用性")
    
    print(f"\n阶段3 (高级功能，{nice_to_have_count}项):")
    print("  实现'锦上添花'的功能，提供完整的QEntL语言支持")
    
    print(f"\n💡 最小化运行时核心功能:")
    print("  1. 变量声明和作用域 (let)")
    print("  2. 基础类型系统 (字符串、整数、布尔)")
    print("  3. 控制流语句 (如果、否则、循环)")
    print("  4. 函数定义和调用")
    print("  5. 数组和基本数据结构")
    print("  6. 错误报告机制")
    
    print("\n" + "=" * 80)

def main():
    """主函数"""
    
    compiler_file = "/root/QSM/QEntL/System/Compiler/quantum_compiler_v2.qentl"
    
    print("🔬 正在分析QEntL编译器依赖...")
    
    try:
        features = analyze_source_file(compiler_file)
        requirements = generate_runtime_requirements(features)
        print_analysis_report(features, requirements)
        
        # 生成实施优先级文件
        with open("/root/QSM/docs/RUNTIME_IMPLEMENTATION_PRIORITY.md", "w", encoding="utf-8") as f:
            f.write("# 运行时实施优先级\n\n")
            f.write("基于编译器依赖分析生成的实施路线图\n\n")
            
            f.write("## 必须支持 (立即实现)\n")
            for req in requirements['must_have']:
                f.write(f"- [ ] {req}\n")
            
            f.write("\n## 应该支持 (第二阶段实现)\n")
            for req in requirements['should_have']:
                f.write(f"- [ ] {req}\n")
            
            f.write("\n## 锦上添花 (第三阶段实现)\n")
            for req in requirements['nice_to_have']:
                f.write(f"- [ ] {req}\n")
        
        print(f"\n✅ 分析完成！详细优先级已保存到 docs/RUNTIME_IMPLEMENTATION_PRIORITY.md")
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)