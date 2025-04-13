#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为quantum_gene_marker.py生成修复后的scan_directory方法
"""

def print_fixed_scan_directory():
    """打印修复后的scan_directory方法"""
    
    # 新的scan_directory方法，包含忽略以点开头的目录的逻辑
    fixed_method = '''
    def scan_directory(self, directory: str, patterns: List[str] = None, recursive: bool = True) -> Dict[str, Any]:
        """扫描目录并为文件添加量子基因标记
        
        Args:
            directory: 要扫描的目录
            patterns: 文件匹配模式列表
            recursive: 是否递归扫描子目录
            
        Returns:
            包含扫描结果的字典
        """
        # 使用内部实现
        results = {
            'total_files': 0,
            'marked_files': 0,
            'errors': 0,
            'files': [],
            'details': []
        }
        
        if patterns is None:
            # 默认匹配所有支持的文件类型
            patterns = []
            for ext in self.SUPPORTED_FILE_TYPES.keys():
                patterns.append(f"*{ext}")
        
        # 使用Path.glob或Path.rglob扫描文件
        try:
            path = Path(directory)
            if not path.exists():
                raise FileNotFoundError(f"目录不存在: {directory}")
            
            # 创建文件列表
            files = []
            
            # 检查目录是否应该被忽略（以点开头）
            def should_skip_dir(dir_path):
                # 获取目录名（不含路径）
                dir_name = os.path.basename(os.path.normpath(dir_path))
                # 如果目录名以点开头，且不是当前目录 (.) 或上级目录 (..)，则跳过
                return dir_name.startswith('.') and dir_name not in ['.', '..']
            
            if recursive:
                # 手动递归遍历目录，跳过以点开头的目录
                for root, dirs, found_files in os.walk(path):
                    # 移除以点开头的目录，防止进一步遍历
                    dirs[:] = [d for d in dirs if not should_skip_dir(d)]
                    
                    # 检查文件扩展名
                    for file in found_files:
                        if any(file.endswith(ext) for ext in self.SUPPORTED_FILE_TYPES.keys()):
                            file_path = os.path.join(root, file)
                            files.append(Path(file_path))
            else:
                # 非递归模式下，直接使用glob
                for pattern in patterns:
                    for file_path in path.glob(pattern):
                        if file_path.is_file():
                            files.append(file_path)
            
            # 处理文件
            for file_path in files:
                file_str = str(file_path)
                results['total_files'] += 1
                
                try:
                    # 添加量子基因标记
                    if self.add_quantum_gene_marker(file_str):
                        results['marked_files'] += 1
                        results['files'].append(file_str)
                        results['details'].append({
                            'path': file_str,
                            'status': 'marked'
                        })
                    else:
                        results['details'].append({
                            'path': file_str,
                            'status': 'skipped'
                        })
                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'path': file_str,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            logger.error(f"扫描目录时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            results['errors'] += 1
            results['details'].append({
                'error': str(e)
            })
            return results
    '''
    
    print(fixed_method)

if __name__ == "__main__":
    print_fixed_scan_directory() 

    """
    # 
"""
量子基因编码: QE-QUA-E86CDE388864
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
    """
    