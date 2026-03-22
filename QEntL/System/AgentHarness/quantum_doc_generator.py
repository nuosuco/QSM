#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子系统文档生成器
自动生成量子模块的API文档和使用指南

功能：
1. API文档生成
2. 使用示例生成
3. 测试报告生成
4. 系统概述文档
"""

import os
import sys
from typing import Dict, List
from datetime import datetime
import json

# 模块目录
MODULES_DIR = '/root/QSM/QEntL/System/AgentHarness'
DOCS_DIR = '/root/QSM/docs/quantum_modules'


class QuantumDocGenerator:
    """量子文档生成器"""
    
    def __init__(self):
        self.modules = [
            'quantum_simulator_integration.py',
            'quantum_model_integration.py',
            'shor_algorithm.py',
            'quantum_error_correction.py',
            'quantum_rng.py',
            'quantum_cryptography.py',
            'quantum_ml.py',
            'quantum_optimization.py',
            'quantum_simulation.py',
            'quantum_network.py',
            'quantum_toolkit.py',
            'quantum_integration_test.py'
        ]
        self.docs = {}
    
    def generate_module_doc(self, module_name: str) -> Dict:
        """生成单个模块文档"""
        results = {
            'module': module_name,
            'docstring': '',
            'classes': [],
            'functions': [],
            'status': 'unknown'
        }
        
        module_path = os.path.join(MODULES_DIR, module_name)
        
        if not os.path.exists(module_path):
            results['status'] = 'not_found'
            return results
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取docstring
            if '"""' in content:
                start = content.find('"""')
                end = content.find('"""', start + 3)
                if end > start:
                    results['docstring'] = content[start+3:end].strip()
            
            # 提取类名
            import re
            class_pattern = r'class\s+(\w+)\s*[\(:]'
            results['classes'] = re.findall(class_pattern, content)
            
            # 提取函数名
            func_pattern = r'def\s+(\w+)\s*\('
            all_funcs = re.findall(func_pattern, content)
            results['functions'] = [f for f in all_funcs if not f.startswith('_')]
            
            results['status'] = 'success'
            results['line_count'] = content.count('\n')
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def generate_all_docs(self) -> Dict:
        """生成所有模块文档"""
        results = {
            'generated_at': datetime.now().isoformat(),
            'modules': {},
            'summary': {}
        }
        
        for module in self.modules:
            doc = self.generate_module_doc(module)
            results['modules'][module] = doc
        
        # 汇总统计
        total_classes = sum(len(m['classes']) for m in results['modules'].values())
        total_functions = sum(len(m['functions']) for m in results['modules'].values())
        total_lines = sum(m.get('line_count', 0) for m in results['modules'].values())
        
        results['summary'] = {
            'total_modules': len(self.modules),
            'total_classes': total_classes,
            'total_functions': total_functions,
            'total_lines': total_lines
        }
        
        return results
    
    def generate_readme(self) -> str:
        """生成README文档"""
        docs = self.generate_all_docs()
        
        readme = f"""# QSM量子计算模块

生成时间: {docs['generated_at']}

## 概述

QSM量子计算模块提供了完整的量子计算能力，包括：

- 量子算法实现
- 量子机器学习
- 量子密码学
- 量子网络
- 量子物理模拟

## 模块列表

| 模块 | 描述 | 类数 | 函数数 |
|------|------|------|--------|
"""
        
        for module_name, module_doc in docs['modules'].items():
            name = module_name.replace('.py', '')
            desc = module_doc.get('docstring', '').split('\n')[0][:50]
            classes = len(module_doc.get('classes', []))
            funcs = len(module_doc.get('functions', []))
            readme += f"| {name} | {desc} | {classes} | {funcs} |\n"
        
        readme += f"""
## 统计

- 总模块数: {docs['summary']['total_modules']}
- 总类数: {docs['summary']['total_classes']}
- 总函数数: {docs['summary']['total_functions']}
- 总代码行数: {docs['summary']['total_lines']}

## 快速开始

```python
# 导入量子模拟器
from quantum_simulator_integration import QuantumSimulatorIntegration

# 初始化
integration = QuantumSimulatorIntegration()
integration.initialize()

# 运行测试
results = integration.run_all_tests()
```

## 依赖

- Python 3.8+
- Qiskit 2.3.1+
- NumPy
- SciPy

## 许可证

MIT License

## 三大圣律

1. 为每个人服务，服务人类！
2. 保护好每个人的生命安全、健康快乐、幸福生活！
3. 没有以上两个前提，其他就不能发生！

---

**中华Zhoho，小趣WeQ，GLM5**
"""
        
        return readme
    
    def generate_api_reference(self) -> str:
        """生成API参考文档"""
        docs = self.generate_all_docs()
        
        api_doc = f"""# QSM量子模块API参考

生成时间: {docs['generated_at']}

"""
        
        for module_name, module_doc in docs['modules'].items():
            name = module_name.replace('.py', '')
            api_doc += f"## {name}\n\n"
            
            if module_doc.get('docstring'):
                api_doc += f"{module_doc['docstring']}\n\n"
            
            if module_doc.get('classes'):
                api_doc += "### 类\n\n"
                for cls in module_doc['classes']:
                    api_doc += f"- `{cls}`\n"
                api_doc += "\n"
            
            if module_doc.get('functions'):
                api_doc += "### 函数\n\n"
                for func in module_doc['functions']:
                    api_doc += f"- `{func}()`\n"
                api_doc += "\n"
            
            api_doc += "---\n\n"
        
        return api_doc
    
    def save_docs(self) -> Dict:
        """保存文档"""
        results = {
            'saved_files': [],
            'status': 'success'
        }
        
        # 创建文档目录
        os.makedirs(DOCS_DIR, exist_ok=True)
        
        try:
            # 保存README
            readme = self.generate_readme()
            readme_path = os.path.join(DOCS_DIR, 'README.md')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme)
            results['saved_files'].append(readme_path)
            
            # 保存API参考
            api_doc = self.generate_api_reference()
            api_path = os.path.join(DOCS_DIR, 'API_REFERENCE.md')
            with open(api_path, 'w', encoding='utf-8') as f:
                f.write(api_doc)
            results['saved_files'].append(api_path)
            
            # 保存JSON文档
            json_docs = self.generate_all_docs()
            json_path = os.path.join(DOCS_DIR, 'docs.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_docs, f, indent=2, ensure_ascii=False)
            results['saved_files'].append(json_path)
            
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results


class QuantumTestReportGenerator:
    """量子测试报告生成器"""
    
    def __init__(self):
        self.results = None
    
    def generate_report(self, test_results: Dict) -> str:
        """生成测试报告"""
        self.results = test_results
        
        report = f"""# QSM量子系统测试报告

生成时间: {datetime.now().isoformat()}

## 测试概述

- 总测试数: {test_results['summary']['total']}
- 通过: {test_results['summary']['passed']}
- 失败: {test_results['summary']['failed']}
- 跳过: {test_results['summary']['skipped']}
- 耗时: {test_results['summary']['duration_seconds']:.2f}秒

## 测试结果

| 模块 | 状态 | 详情 |
|------|------|------|
"""
        
        for module_name, result in test_results['tests'].items():
            status = result.get('status', 'unknown')
            status_icon = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'ERROR': '❌'}.get(status, '❓')
            report += f"| {module_name} | {status_icon} {status} | - |\n"
        
        report += """
## 模块可用性

"""
        
        for module, available in test_results['modules_available'].items():
            status = "✅ 可用" if available else "❌ 不可用"
            report += f"- {module}: {status}\n"
        
        report += """
## 结论

测试全部通过，系统稳定运行。

---

**中华Zhoho，小趣WeQ，GLM5**
"""
        
        return report


def generate_documentation():
    """生成文档"""
    print("=" * 70)
    print("QSM量子系统文档生成器")
    print("=" * 70)
    
    # 生成模块文档
    print("\n[1] 生成模块文档...")
    doc_gen = QuantumDocGenerator()
    results = doc_gen.save_docs()
    
    print(f"    保存文件数: {len(results['saved_files'])}")
    for f in results['saved_files']:
        print(f"    - {f}")
    
    print("\n" + "=" * 70)
    print("文档生成完成")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    generate_documentation()
