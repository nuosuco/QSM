# 测试自动量子基因标记 - 文件1
# 这是一个测试文件，用于测试系统自动添加量子基因标记

def test_function():
    """测试函数"""
    return "这是测试文件1，用于测试自动标记功能"

print("测试文件1已加载")

# 添加对文件2的引用
import os
import sys

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 引用第二个文件
second_file_path = os.path.join(current_dir, "test_auto_mark2.py")
print(f"引用文件: {second_file_path}")

# 尝试获取文件内容，模拟引用关系
if os.path.exists(second_file_path):
    with open(second_file_path, 'r', encoding='utf-8') as f:
        print("已引用文件2")

if __name__ == "__main__":
    print(test_function()) 
"""
量子基因编码: QE-TES-75B6FF8AC5FA
纠缠状态: 活跃
纠缠对象: ['test/test_auto_mark2.py']
纠缠强度: 0.98
"""