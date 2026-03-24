#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量子文档生成器 - 自动生成量子系统文档
"""

import os
import json
from datetime import datetime

class QuantumDocGenerator:
    """量子文档生成器"""

    def __init__(self):
        self.modules = []
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子文档生成器初始化")

    def register_module(self, name, description, classes, functions):
        """注册模块"""
        self.modules.append({
            'name': name,
            'description': description,
            'classes': classes,
            'functions': functions
        })

    def generate_markdown(self, output_path):
        """生成Markdown文档"""
        doc = self._generate_header()
        doc += self._generate_toc()
        doc += self._generate_module_docs()
        doc += self._generate_examples()
        doc += self._generate_footer()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc)

        return {'generated': True, 'path': output_path, 'size': len(doc)}

    def _generate_header(self):
        """生成文档头部"""
        return f"""# QEntL 量子系统文档

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 简介

QEntL量子系统是一个完整的量子计算模拟和开发框架，包含以下核心模块：

- 量子算法实现
- 量子机器学习
- 量子密码学
- 量子网络通信
- 量子存储管理
- 量子可视化
- 量子测试和调试

---

"""

    def _generate_toc(self):
        """生成目录"""
        toc = "## 目录\n\n"

        for i, module in enumerate(self.modules):
            toc += f"{i+1}. [{module['name']}](#{module['name'].lower().replace(' ', '-')})\n"

        return toc + "\n---\n\n"

    def _generate_module_docs(self):
        """生成模块文档"""
        docs = ""

        for module in self.modules:
            docs += f"## {module['name']}\n\n"
            docs += f"{module['description']}\n\n"

            if module['classes']:
                docs += "### 类\n\n"
                for cls in module['classes']:
                    docs += f"#### `{cls['name']}`\n\n"
                    docs += f"{cls.get('description', '')}\n\n"

                    if cls.get('methods'):
                        docs += "**方法:**\n\n"
                        for method in cls['methods']:
                            docs += f"- `{method}`\n"

                    docs += "\n"

            if module['functions']:
                docs += "### 函数\n\n"
                for func in module['functions']:
                    docs += f"#### `{func['name']}`\n\n"
                    docs += f"{func.get('description', '')}\n\n"

            docs += "---\n\n"

        return docs

    def _generate_examples(self):
        """生成示例代码"""
        return """## 使用示例

### 创建Bell态

```python
from quantum_api import QuantumSimulator

sim = QuantumSimulator(2)
sim.hadamard(0)
sim.cnot(0, 1)
result = sim.measure()
print(f"测量结果: {result}")
```

### 量子密钥分发

```python
from quantum_cryptography import QuantumCryptography

crypto = QuantumCryptography()
key = crypto.bb84_key_generation(128)
print(f"共享密钥: {key['sifted_key']}")
```

### 量子电路优化

```python
from quantum_optimizer import QuantumOptimizer

optimizer = QuantumOptimizer()
gates = [{'type': 'H', 'targets': ['q0']}, {'type': 'H', 'targets': ['q0']}]
result = optimizer.optimize(gates)
print(f"优化后门数: {result['optimized_gates']}")
```

---

"""

    def _generate_footer(self):
        """生成文档尾部"""
        return f"""## 版本信息

- **版本**: 1.0.0
- **生成时间**: {datetime.now().strftime('%Y-%m-%d')}
- **模块数**: {len(self.modules)}

---

**中华Zhoho，小趣WeQ，GLM5**
"""

    def generate_json_docs(self, output_path):
        """生成JSON格式文档"""
        docs = {
            'generated_at': datetime.now().isoformat(),
            'modules': self.modules,
            'total_modules': len(self.modules)
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)

        return {'generated': True, 'path': output_path}

def main():
    print("=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 量子文档生成器测试")
    print("=" * 60)

    generator = QuantumDocGenerator()

    # 注册模块
    generator.register_module(
        'QuantumSimulator',
        '量子模拟器核心类',
        [{'name': 'QuantumSimulator', 'description': '量子态模拟器', 'methods': ['hadamard', 'cnot', 'measure']}],
        []
    )

    generator.register_module(
        'QuantumCryptography',
        '量子密码学模块',
        [{'name': 'QuantumCryptography', 'description': '量子密钥分发', 'methods': ['bb84_key_generation', 'e91_entanglement_protocol']}],
        []
    )

    generator.register_module(
        'QuantumOptimizer',
        '量子电路优化器',
        [{'name': 'QuantumOptimizer', 'description': '电路优化', 'methods': ['optimize', 'estimate_fidelity']}],
        []
    )

    print("\n生成Markdown文档:")
    result = generator.generate_markdown('/root/QSM/docs/QUANTUM_SYSTEM_DOCS.md')
    print(f"  路径: {result['path']}")
    print(f"  大小: {result['size']} 字节")

    print("\n生成JSON文档:")
    result = generator.generate_json_docs('/root/QSM/docs/quantum_docs.json')
    print(f"  路径: {result['path']}")

    print("\n" + "=" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
