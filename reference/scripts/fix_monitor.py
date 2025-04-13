#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复system_monitor_enhancer.py文件的缩进问题
"""

import os
import sys
import re

def fix_indentation(input_file, output_file=None):
    """修复文件中的缩进问题"""
    if output_file is None:
        output_file = input_file
    
    print(f"正在修复文件: {input_file}")
    
    # 创建备份
    backup_file = f"{input_file}.bak"
    if not os.path.exists(backup_file):
        with open(input_file, 'r', encoding='utf-8') as f_in:
            with open(backup_file, 'w', encoding='utf-8') as f_out:
                f_out.write(f_in.read())
        print(f"已创建备份文件: {backup_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除所有多余的三引号块
    content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
    
    # 修复get_system_monitor函数的缩进
    content = re.sub(r'def get_system_monitor\(ref_core=None\):\s+"""获取系统监控增强器实例"""\s+return SystemMonitorEnhancer\(ref_core=ref_core\)',
                     'def get_system_monitor(ref_core=None):\n    """获取系统监控增强器实例"""\n    return SystemMonitorEnhancer(ref_core=ref_core)',
                     content)
    
    # 正确格式化量子基因信息
    content = re.sub(r'# """
量子基因编码: QE-SYS-EE5C3A53D3E9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.0
"""                     '# """
量子基因编码: QE-SYS-EE5C3A53D3E9
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.0
"""                     content, flags=re.DOTALL)
    
    # 删除整个文件最末尾的多余内容
    content = re.sub(r'# 开发团队：中华 ZhoHo ，Claude"""*\s*$',
                     '# 开发团队：中华 ZhoHo ，Claude', content)
    
    # 写入修复后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已完成修复: {output_file}")

def main():
    """主函数"""
    # 确定文件路径
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = os.path.join("Ref", "monitor", "system_monitor_enhancer.py")
    
    # 进行修复
    fix_indentation(input_file)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 