#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QSM量子结果导出器
导出量子计算结果到多种格式

功能：
1. JSON导出
2. CSV导出
3. HTML报告导出
4. Markdown导出
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any


class QuantumResultExporter:
    """量子结果导出器"""
    
    def __init__(self, output_dir: str = '/root/QSM/results'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_json(self, 
                    data: Dict, 
                    filename: str = None,
                    pretty: bool = True) -> str:
        """导出为JSON"""
        if filename is None:
            filename = f"quantum_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        return filepath
    
    def export_csv(self,
                   data: List[Dict],
                   filename: str = None) -> str:
        """导出为CSV"""
        if filename is None:
            filename = f"quantum_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if not data:
            return filepath
        
        # 获取所有字段
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # 处理非字符串值
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, (list, dict)):
                        processed_row[key] = json.dumps(value)
                    else:
                        processed_row[key] = value
                writer.writerow(processed_row)
        
        return filepath
    
    def export_markdown(self,
                        data: Dict,
                        title: str = "QSM量子结果报告",
                        filename: str = None) -> str:
        """导出为Markdown"""
        if filename is None:
            filename = f"quantum_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        md_content = f"""# {title}

生成时间: {datetime.now().isoformat()}

"""
        
        # 处理数据
        md_content += self._dict_to_markdown(data, level=2)
        
        md_content += """
---

**中华Zhoho，小趣WeQ，GLM5**
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
    
    def _dict_to_markdown(self, data: Dict, level: int = 2) -> str:
        """将字典转换为Markdown"""
        md = ""
        prefix = "#" * level
        
        for key, value in data.items():
            if isinstance(value, dict):
                md += f"{prefix} {key}\n\n"
                md += self._dict_to_markdown(value, level + 1)
            elif isinstance(value, list):
                md += f"{prefix} {key}\n\n"
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        md += f"**{i+1}.**\n"
                        md += self._dict_to_markdown(item, level + 1)
                    else:
                        md += f"- {item}\n"
                md += "\n"
            else:
                md += f"{prefix} {key}\n\n{value}\n\n"
        
        return md
    
    def export_html(self,
                    data: Dict,
                    title: str = "QSM量子结果报告",
                    filename: str = None) -> str:
        """导出为HTML"""
        if filename is None:
            filename = f"quantum_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .success {{ color: #27ae60; }}
        .error {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .info {{ color: #3498db; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>生成时间: {datetime.now().isoformat()}</p>
        
        {self._dict_to_html(data)}
        
        <div class="footer">
            <p>中华Zhoho，小趣WeQ，GLM5</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _dict_to_html(self, data: Dict, depth: int = 0) -> str:
        """将字典转换为HTML"""
        html = ""
        
        for key, value in data.items():
            if isinstance(value, dict):
                html += f"<h{min(depth+2, 6)}>{key}</h{min(depth+2, 6)}>\n"
                html += self._dict_to_html(value, depth + 1)
            elif isinstance(value, list):
                html += f"<h{min(depth+2, 6)}>{key}</h{min(depth+2, 6)}>\n"
                html += "<ul>\n"
                for item in value:
                    if isinstance(item, dict):
                        html += "<li>" + self._dict_to_html(item, depth + 1) + "</li>\n"
                    else:
                        html += f"<li>{item}</li>\n"
                html += "</ul>\n"
            else:
                html += f"<p><strong>{key}:</strong> {value}</p>\n"
        
        return html
    
    def export_all(self, 
                   data: Dict,
                   base_name: str = None) -> Dict[str, str]:
        """导出所有格式"""
        if base_name is None:
            base_name = f"quantum_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results = {}
        
        # JSON
        results['json'] = self.export_json(data, f"{base_name}.json")
        
        # Markdown
        results['markdown'] = self.export_markdown(data, filename=f"{base_name}.md")
        
        # HTML
        results['html'] = self.export_html(data, filename=f"{base_name}.html")
        
        return results


def run_exporter_demo():
    """运行导出器演示"""
    print("=" * 70)
    print("QSM量子结果导出器演示")
    print("=" * 70)
    
    exporter = QuantumResultExporter()
    
    # 示例数据
    sample_data = {
        'test_results': {
            'total_tests': 10,
            'passed': 9,
            'failed': 1,
            'success_rate': 0.9
        },
        'algorithms': [
            {'name': 'Grover', 'success_rate': 0.95, 'time_ms': 120},
            {'name': 'QFT', 'success_rate': 0.92, 'time_ms': 85},
            {'name': 'Shor', 'success_rate': 1.0, 'time_ms': 200}
        ],
        'system_info': {
            'qiskit_version': '2.3.1',
            'python_version': '3.11.6',
            'platform': 'Linux'
        }
    }
    
    print("\n[1] 导出JSON...")
    json_path = exporter.export_json(sample_data)
    print(f"    保存至: {json_path}")
    
    print("\n[2] 导出Markdown...")
    md_path = exporter.export_markdown(sample_data)
    print(f"    保存至: {md_path}")
    
    print("\n[3] 导出HTML...")
    html_path = exporter.export_html(sample_data)
    print(f"    保存至: {html_path}")
    
    print("\n[4] 导出所有格式...")
    all_paths = exporter.export_all(sample_data, "demo_results")
    for fmt, path in all_paths.items():
        print(f"    {fmt}: {path}")
    
    print("\n" + "=" * 70)
    print("导出器演示完成")
    print("=" * 70)
    
    return exporter


if __name__ == "__main__":
    run_exporter_demo()
