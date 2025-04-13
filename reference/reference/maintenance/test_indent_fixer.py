#!/usr/bin/env python

# # """
量子基因编码: QE-TES-D7E072AA7961
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
""""""
缩进修复测试脚本

此脚本用于测试缩进修复功能，通过创建一些包含常见缩进错误的测试文件，
然后运行fix_indent_errors.py并验证修复结果。
"""

import os
import sys
import tempfile
import shutil
import subprocess

# 测试文件内容 - 包含各种缩进错误
TEST_FILES = {
    "docstring_indent_error.py": '''
class TestClass:
    def test_method(self):
        """
    这是一个多行文档字符串，
    它的缩进是错误的。
    每行应该和第一行保持相同的缩进。
        """
        print("This is a test")
        
def another_function():
    """
这个文档字符串缩进也是错误的
    它的第一行没有缩进
        这一行缩进过多
    """
    return True
''',
    
    "method_indent_error.py": '''
class BadClass:
def wrong_method(self):
    # 这个方法的缩进是错误的，应该缩进4个空格
    print("Method with wrong indentation")
    
    def nested_method():
        print("This is nested")
  print("This line has wrong indentation in the method body")
''',
    
    "quantum_marker_error.py": '''
class RefQuantumGeneMarker:
    def __init__(self, file_path=None):
    self.file_path = file_path
    self.gene_id = self._generate_quantum_gene_id()
        
    COMMENT_END_MARKERS = {
    '.py': '"""',
    '.js': '*/',
    '.css': '*/',
    '.html': '-->',
'.cpp': '*/',
    }
    
    def add_marker(self):
    """添加量子基因标记
    
        这个函数用于添加量子基因标记
    到文件中
    """
        return True
''',
    
    "special_case.py": '''
def resolve_path(path, base_dir=None):
    """解析路径
    
参数:
    path: 要解析的路径
    base_dir: 基础目录
返回:
    解析后的绝对路径
    """
    import os
return os.path.abspath(os.path.join(base_dir or ".", path))
'''
}

# 颜色定义
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def print_status(message):
    """打印状态消息"""
    print(f"{GREEN}[STATUS] {message}{RESET}")

def print_warning(message):
    """打印警告消息"""
    print(f"{YELLOW}[WARNING] {message}{RESET}")

def print_error(message):
    """打印错误消息"""
    print(f"{RED}[ERROR] {message}{RESET}")

def setup_test_environment():
    """设置测试环境，创建测试文件"""
    # 创建临时目录
    test_dir = tempfile.mkdtemp(prefix="indent_fix_test_")
    print_status(f"创建测试目录: {test_dir}")
    
    # 创建测试文件
    for filename, content in TEST_FILES.items():
        file_path = os.path.join(test_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print_status(f"创建测试文件: {filename}")
    
    return test_dir

def run_indent_fixer(test_dir):
    """运行缩进修复脚本"""
    # 复制修复脚本到测试目录
    fixer_path = "fix_indent_errors.py"
    test_fixer_path = os.path.join(test_dir, "fix_indent_errors.py")
    
    try:
        shutil.copy2(fixer_path, test_fixer_path)
        print_status(f"复制修复脚本到测试目录: {test_fixer_path}")
        
        # 修改脚本以扫描测试目录中的所有文件
        with open(test_fixer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换FILES_TO_CHECK为测试文件列表
        test_files = list(TEST_FILES.keys())
        files_list = "FILES_TO_CHECK = [\n    " + ",\n    ".join([f'"{f}"' for f in test_files]) + "\n]"
        content = content.replace("FILES_TO_CHECK = [", files_list, 1)
        
        with open(test_fixer_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 运行修复脚本
        print_status("运行缩进修复脚本...")
        os.chdir(test_dir)
        result = subprocess.run(["python", test_fixer_path], 
                               capture_output=True, 
                               text=True,
                               check=True)
        
        print(result.stdout)
        if result.stderr:
            print_warning(f"脚本警告/错误: {result.stderr}")
        
        return True
    except Exception as e:
        print_error(f"运行修复脚本时出错: {str(e)}")
        return False

def verify_results(test_dir):
    """验证修复结果"""
    print_status("验证修复结果...")
    
    all_passed = True
    
    # 检查每个测试文件
    for filename in TEST_FILES.keys():
        file_path = os.path.join(test_dir, filename)
        backup_path = f"{file_path}.bak"
        
        if not os.path.exists(file_path):
            print_error(f"文件不存在: {file_path}")
            all_passed = False
            continue
        
        if not os.path.exists(backup_path):
            print_warning(f"未找到备份文件: {backup_path}")
        
        # 读取修复后的文件
        with open(file_path, 'r', encoding='utf-8') as f:
            fixed_content = f.readlines()
        
        # 验证修复结果
        if filename == "docstring_indent_error.py":
            # 检查多行文档字符串的缩进
            for i, line in enumerate(fixed_content):
                if "这是一个多行文档字符串" in line and line.strip() == "这是一个多行文档字符串，":
                    indent = len(line) - len(line.lstrip())
                    if indent != 8:  # 应该有8个空格的缩进
                        print_error(f"文档字符串缩进修复失败: {filename}, 行 {i+1}")
                        all_passed = False
        
        elif filename == "method_indent_error.py":
            # 检查方法缩进
            for i, line in enumerate(fixed_content):
                if "def wrong_method" in line:
                    indent = len(line) - len(line.lstrip())
                    if indent != 4:  # 类中的方法应该缩进4个空格
                        print_error(f"方法缩进修复失败: {filename}, 行 {i+1}")
                        all_passed = False
        
        elif filename == "quantum_marker_error.py":
            # 检查__init__方法和字典缩进
            for i, line in enumerate(fixed_content):
                if "self.file_path =" in line:
                    indent = len(line) - len(line.lstrip())
                    if indent != 8:  # 方法体内应该缩进8个空格
                        print_error(f"__init__方法缩进修复失败: {filename}, 行 {i+1}")
                        all_passed = False
                
                if "'.py':" in line:
                    indent = len(line) - len(line.lstrip())
                    if indent != 8:  # 字典项应该缩进8个空格
                        print_error(f"字典缩进修复失败: {filename}, 行 {i+1}")
                        all_passed = False
        
        elif filename == "special_case.py":
            # 检查docstring参数缩进
            for i, line in enumerate(fixed_content):
                if "path:" in line:
                    indent = len(line) - len(line.lstrip())
                    if indent != 4:  # 参数描述应该缩进4个空格
                        print_error(f"参数缩进修复失败: {filename}, 行 {i+1}")
                        all_passed = False
    
    if all_passed:
        print_status("所有测试通过! 缩进修复成功。")
    else:
        print_error("有些测试未通过，请检查修复脚本。")
    
    return all_passed

def cleanup_test_environment(test_dir):
    """清理测试环境"""
    try:
        shutil.rmtree(test_dir)
        print_status(f"已清理测试目录: {test_dir}")
    except Exception as e:
        print_error(f"清理测试目录时出错: {str(e)}")

def main():
    """主函数"""
    print_status("开始测试缩进修复功能...")
    
    # 设置测试环境
    test_dir = setup_test_environment()
    
    try:
        # 运行修复脚本
        if run_indent_fixer(test_dir):
            # 验证结果
            verify_results(test_dir)
    finally:
        # 是否要清理测试环境？
        if "--keep" not in sys.argv:
            cleanup_test_environment(test_dir)
        else:
            print_status(f"保留测试目录: {test_dir}")
    
    print_status("测试完成!")

if __name__ == "__main__":
    main() 