import pandas as pd
import os
import sys

# 添加项目根目录到路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

def read_yi_excel_files():
    """读取Yi Wen目录中的Excel文件，提取彝文内容"""
    yi_wen_dir = os.path.join(PROJECT_ROOT, 'Models', 'training_data', 'source', 'Yi Wen')
    
    print("正在读取彝文Excel文件...")
    print(f"目录: {yi_wen_dir}")
    
    all_yi_chars = set()
    
    for filename in os.listdir(yi_wen_dir):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(yi_wen_dir, filename)
            print(f"\n正在读取: {filename}")
            
            try:
                # 读取Excel文件
                df = pd.read_excel(file_path)
                print(f"文件列名: {list(df.columns)}")
                print(f"数据行数: {len(df)}")
                
                # 遍历所有列，查找彝文字符
                for col in df.columns:
                    if df[col].dtype == 'object':  # 文本列
                        for value in df[col].dropna():
                            value_str = str(value)
                            # 查找彝文字符 (Unicode范围: U+A000-U+A48F)
                            for char in value_str:
                                if '\uA000' <= char <= '\uA48F':
                                    all_yi_chars.add(char)
                
                print(f"在 {filename} 中找到 {len([c for c in all_yi_chars if c in str(df.values)])} 个彝文字符")
                
            except Exception as e:
                print(f"读取 {filename} 时出错: {e}")
    
    print(f"\n总共找到 {len(all_yi_chars)} 个不同的彝文字符:")
    yi_chars_list = sorted(list(all_yi_chars))
    print(''.join(yi_chars_list))
    
    return yi_chars_list

if __name__ == '__main__':
    yi_chars = read_yi_excel_files()
    
    # 保存到文件
    output_file = os.path.join(os.path.dirname(__file__), 'yi_chars_from_excel.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(yi_chars))
    
    print(f"\n彝文字符已保存到: {output_file}") 