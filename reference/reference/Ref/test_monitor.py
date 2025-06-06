#!/usr/bin/env python3
"""
测试文件完整性监控系统的基本功能
"""
import os
import sys
import tempfile
import shutil

# 添加Ref目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Ref.utils.file_integrity_monitor import get_monitor
from Ref.utils.file_organization_guardian import get_guardian

# 测试数据
TEST_FILE_CONTENT = """#!/usr/bin/env python3
\"\"\"
这是一个测试文件
\"\"\"

def hello():
    print("Hello, World!")

if __name__ == "__main__":
    hello()
"""

SIMILAR_FILE_CONTENT = """#!/usr/bin/env python3
\"\"\"
这是一个非常相似的测试文件
\"\"\"

def hello_world():
    print("Hello, World! This is a test.")

if __name__ == "__main__":
    hello_world()
"""

DIFFERENT_FILE_CONTENT = """#!/usr/bin/env python3
\"\"\"
这是一个完全不同的测试文件
\"\"\"

import datetime

def get_current_time():
    return datetime.datetime.now()

def display_time():
    print(f"当前时间: {get_current_time()}")

if __name__ == "__main__":
    display_time()
"""


def test_file_integrity_monitor():
    """测试文件完整性监控器"""
    print("=== 测试文件完整性监控器 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建临时目录: {temp_dir}")
    
    try:
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test_file.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(TEST_FILE_CONTENT)
        print(f"创建测试文件: {test_file}")
        
        # 创建注册表路径
        registry_path = os.path.join(temp_dir, "registry.json")
        
        # 获取监控器
        monitor = get_monitor(registry_path)
        print(f"初始化监控器，注册表路径: {registry_path}")
        
        # 注册文件
        result = monitor.register_file(
            test_file,
            TEST_FILE_CONTENT,
            "测试文件",
            []
        )
        print(f"注册文件结果: {result}")
        
        # 检查冲突（相同文件）
        conflict = monitor.check_conflicts(test_file, TEST_FILE_CONTENT)
        print(f"检查相同内容冲突: {conflict}")
        
        # 检查冲突（相似文件）
        conflict = monitor.check_conflicts(test_file, SIMILAR_FILE_CONTENT)
        print(f"检查相似内容冲突: {type(conflict)} {conflict}")
        
        # 检查冲突（不同文件）
        conflict = monitor.check_conflicts(test_file, DIFFERENT_FILE_CONTENT)
        print(f"检查不同内容冲突: {conflict}")
        
        # 测试查找相似文件
        similar_file = os.path.join(temp_dir, "similar_file.py")
        with open(similar_file, "w", encoding="utf-8") as f:
            f.write(SIMILAR_FILE_CONTENT)
        print(f"创建相似文件: {similar_file}")
        
        # 注册相似文件
        monitor.register_file(
            similar_file,
            SIMILAR_FILE_CONTENT,
            "相似的测试文件",
            []
        )
        
        # 检查相似文件
        similar_files = monitor._find_similar_purpose_files(
            os.path.join(temp_dir, "new_file.py"),
            TEST_FILE_CONTENT
        )
        print(f"找到相似文件: {len(similar_files)}")
        for sf in similar_files:
            print(f"  - {sf['path']} (相似度: {sf['similarity']:.2f})")
        
        # 测试扫描目录
        scan_result = monitor.scan_directory(temp_dir)
        print(f"扫描结果:")
        print(f"  - 已注册文件: {len(scan_result['registered'])}")
        print(f"  - 未注册文件: {len(scan_result['unregistered'])}")
        print(f"  - 已更改文件: {len(scan_result['changed'])}")
        
        # 测试提取关键词
        keywords = monitor._extract_keywords(TEST_FILE_CONTENT)
        print(f"提取的关键词: {keywords[:10]}")
    
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"清理临时目录: {temp_dir}")


def test_file_organization_guardian():
    """测试文件组织监护器"""
    print("\n=== 测试文件组织监护器 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建临时目录: {temp_dir}")
    
    try:
        # 创建测试目录结构
        os.makedirs(os.path.join(temp_dir, "Ref", "data"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "Ref", "backup", "files"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "Ref", "logs"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "WeQ", "templates"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "SOM", "global", "js"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "global", "js"), exist_ok=True)
        
        print("创建测试目录结构")
        
        # 创建测试文件
        test_files = [
            (os.path.join(temp_dir, "WeQ", "test_file1.py"), TEST_FILE_CONTENT),
            (os.path.join(temp_dir, "SOM", "test_file2.py"), SIMILAR_FILE_CONTENT),
            (os.path.join(temp_dir, "Ref", "test_file3.py"), DIFFERENT_FILE_CONTENT),
            (os.path.join(temp_dir, "SOM", "global", "js", "common.js"), "// 组件全局JS文件"),
            (os.path.join(temp_dir, "global", "js", "common.js"), "// 主全局JS文件"),
        ]
        
        for filepath, content in test_files:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        
        print(f"创建测试文件: {len(test_files)}个")
        
        # 获取监护器
        registry_path = os.path.join(temp_dir, "Ref", "data", "file_registry.json")
        backup_dir = os.path.join(temp_dir, "Ref", "backup", "files")
        
        guardian = get_guardian(
            workspace_root=temp_dir,
            registry_path=registry_path,
            backup_dir=backup_dir
        )
        
        print(f"初始化监护器")
        
        # 注册现有文件
        stats = guardian.register_existing_files()
        print(f"注册文件统计:")
        print(f"  - 扫描: {stats['scanned']}")
        print(f"  - 注册: {stats['registered']}")
        print(f"  - 跳过: {stats['skipped']}")
        print(f"  - 失败: {stats['failed']}")
        
        # 测试安全创建文件
        test_create_file = os.path.join(temp_dir, "WeQ", "new_file.py")
        success, message = guardian.safe_create_file(
            test_create_file,
            DIFFERENT_FILE_CONTENT,
            "新创建的测试文件"
        )
        print(f"安全创建文件: {success}, {message}")
        
        # 测试检查标准
        results = guardian.enforce_project_standards()
        print(f"标准检查结果:")
        print(f"  - 检查项目数: {results['checked']}")
        print(f"  - 问题数: {len(results['issues'])}")
        
        # 测试项目报告
        report = guardian.scan_project_and_report()
        print(f"项目报告:")
        for component, stats in report['component_stats'].items():
            print(f"  - {component}: {stats['registered']}个已注册文件")
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"清理临时目录: {temp_dir}")


if __name__ == "__main__":
    test_file_integrity_monitor()
    test_file_organization_guardian() 

"""

"""
量子基因编码: QE-TES-6E5F447D95BA
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
