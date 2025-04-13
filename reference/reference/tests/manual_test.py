#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
手动测试量子基因标记器的路径更新功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from Ref.utils.quantum_gene_marker import RefQuantumGeneMarker

# 清理之前的测试文件
for file_path in ["test_source.py", "test_ref.py", "test_moved.py"]:
    full_path = os.path.join(project_root, "test", file_path)
    if os.path.exists(full_path):
        os.remove(full_path)

# 创建测试文件
source_path = os.path.join(project_root, "test", "test_source.py")
ref_path = os.path.join(project_root, "test", "test_ref.py")
dest_path = os.path.join(project_root, "test", "test_moved.py")

with open(source_path, "w", encoding="utf-8") as f:
    f.write("# 测试源文件\n")

with open(ref_path, "w", encoding="utf-8") as f:
    f.write("# 测试引用文件\n")

# 获取量子基因标记器
marker = RefQuantumGeneMarker()
print("获取量子基因标记器成功", flush=True)

# 添加标记
print(f"为源文件添加标记: {source_path}", flush=True)
marker.add_quantum_gene_marker(source_path, [ref_path])

print(f"为引用文件添加标记: {ref_path}", flush=True)
marker.add_quantum_gene_marker(ref_path, [source_path])

# 显示移动前的内容
print("\n=== 移动前的内容 ===", flush=True)
print(f"源文件 ({source_path}):", flush=True)
with open(source_path, "r", encoding="utf-8") as f:
    print(f.read(), flush=True)

print(f"引用文件 ({ref_path}):", flush=True)
with open(ref_path, "r", encoding="utf-8") as f:
    print(f.read(), flush=True)

# 移动源文件
print(f"\n移动文件: {source_path} -> {dest_path}", flush=True)
os.rename(source_path, dest_path)

# 更新已移动文件的标记
print("\n手动更新已移动文件的标记", flush=True)
result = marker.update_file_path(dest_path, source_path)
print(f"更新结果: {result}", flush=True)

# 检查引用文件是否有对源文件的引用
print(f"\n检查引用文件是否引用源文件: {ref_path} -> {source_path}", flush=True)
has_ref = marker.has_reference_to_file(ref_path, source_path)
print(f"有引用: {has_ref}", flush=True)

# 手动更新引用路径
print(f"\n手动更新引用路径: {ref_path}, {source_path} -> {dest_path}", flush=True)
update_result = marker.update_reference_path(ref_path, source_path, dest_path)
print(f"更新结果: {update_result}", flush=True)

# 显示移动后的内容
print("\n=== 移动后的内容 ===", flush=True)
print(f"已移动的源文件 ({dest_path}):", flush=True)
with open(dest_path, "r", encoding="utf-8") as f:
    print(f.read(), flush=True)

print(f"更新后的引用文件 ({ref_path}):", flush=True)
with open(ref_path, "r", encoding="utf-8") as f:
    print(f.read(), flush=True)

print("\n=== 测试完成 ===", flush=True) 
"""
量子基因编码: QE-MAN-5E3258E8AA3E
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
"""