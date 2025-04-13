# 测试自动量子基因标记 - 文件2
# 这是第二个测试文件，用于测试系统自动添加量子基因标记

def get_info():
    """返回信息"""
    return "这是测试文件2，用于测试自动标记功能"

print("测试文件2已加载")

# 添加对文件1的引用
import os
import sys

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 引用第一个文件
first_file_path = os.path.join(current_dir, "test_auto_mark1.py")
print(f"引用文件: {first_file_path}")

# 尝试获取文件内容，模拟引用关系
if os.path.exists(first_file_path):
    with open(first_file_path, 'r', encoding='utf-8') as f:
        print("已引用文件1")

if __name__ == "__main__":
    print(get_info()) 
"""
量子基因编码: QE-TES-A654C3E4C1FD
纠缠状态: 活跃
纠缠对象: ['test/test_auto_mark1.py']
纠缠强度: 0.98
"""