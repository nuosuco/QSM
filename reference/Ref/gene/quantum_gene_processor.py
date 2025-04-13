"""
量子基因处理器 - 为QSM系统中的所有元素提供量子基因编码和量子纠缠信道
这是量子自反省管理模型(Ref)的核心组件
"""

import os
import re
import time
import json
import hashlib
import random
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mimetypes

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Ref/logs/quantum_gene.log'),
        logging.StreamHandler()
    ]
)

# 量子基因编码的正则表达式模式
QG_PATTERN = r'QG-[A-Z0-9]{2,6}-[A-Z]{3,5}-\d{8,14}-[A-Z0-9]{6}-ENT\d{4}'

class QuantumGeneProcessor:
    """量子基因处理器 - 管理量子基因编码和量子纠缠信道"""
    
    def __init__(self):
        self.registry_file = "Ref/data/quantum_gene_registry.json"
        self.entanglement_file = "Ref/data/quantum_entanglement_registry.json"
        self.registry: Dict[str, Dict] = {}
        self.entanglement_registry: Dict[str, Dict] = {}
        self.QG_PATTERN = r'QG-[A-Z0-9]{2,6}-[A-Z]{3,5}-\d{8,14}-[A-Z0-9]{6}-ENT\d{4}'
        self.load_registries()
        self.setup_file_monitor()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Ref/logs/quantum_gene.log'),
                logging.StreamHandler()
            ]
        )

    def _load_registry(self) -> Dict:
        """加载量子基因注册表"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载基因注册表失败: {e}")
                return self._create_empty_registry()
        else:
            return self._create_empty_registry()
    
    def _create_empty_registry(self) -> Dict:
        """创建空的注册表结构"""
        return {
            "models": {},
            "files": {},
            "folders": {},
            "code": {},
            "data": {}
        }
    
    def _save_registry(self) -> None:
        """保存量子基因注册表"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存基因注册表失败: {e}")
    
    def _load_entanglement_registry(self) -> Dict:
        """加载量子纠缠注册表"""
        if os.path.exists(self.entanglement_file):
            try:
                with open(self.entanglement_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载纠缠注册表失败: {e}")
                return {"channels": {}}
        else:
            return {"channels": {}}
    
    def _save_entanglement_registry(self) -> None:
        """保存量子纠缠注册表"""
        try:
            with open(self.entanglement_file, 'w', encoding='utf-8') as f:
                json.dump(self.entanglement_registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存纠缠注册表失败: {e}")
    
    def generate_quantum_gene(self, model_id: str, entity_type: str, metadata: Dict = None) -> str:
        """
        生成量子基因编码
        
        Args:
            model_id: 模型ID (例如: QSM01, WEQ01, SOM01)
            entity_type: 实体类型 (例如: FILE, CODE, DOC, API)
            metadata: 元数据
            
        Returns:
            量子基因编码 (例如: QG-QSM01-FILE-20250401121530-E7A92F-ENT1289)
        """
        if metadata is None:
            metadata = {}
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 生成熵值 (哈希)
        entropy_seed = f"{model_id}:{entity_type}:{timestamp}:{random.random()}"
        for key, value in sorted(metadata.items()):
            entropy_seed += f":{key}={value}"
        entropy = hashlib.sha256(entropy_seed.encode()).hexdigest().upper()[:6]
        
        # 生成纠缠ID
        entanglement_id = f"ENT{random.randint(1000, 9999)}"
        
        # 组合形成量子基因编码
        quantum_gene = f"QG-{model_id}-{entity_type}-{timestamp}-{entropy}-{entanglement_id}"
        
        return quantum_gene
    
    def register_quantum_gene(self, entity_type: str, entity_path: str, quantum_gene: str, metadata: Dict = None) -> None:
        """
        注册量子基因
        
        Args:
            entity_type: 实体类别 (models, files, folders, code)
            entity_path: 实体路径
            quantum_gene: 量子基因编码
            metadata: 元数据
        """
        if metadata is None:
            metadata = {}
        
        if entity_type not in self.registry:
            self.registry[entity_type] = {}
        
        self.registry[entity_type][entity_path] = {
            "quantum_gene": quantum_gene,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        self._save_registry()
    
    def create_entanglement_channel(self, source_gene: str, target_gene: str, channel_type: str = "SYNC") -> str:
        """
        创建量子纠缠信道
        
        Args:
            source_gene: 源量子基因
            target_gene: 目标量子基因
            channel_type: 信道类型 (SYNC, ASYNC, DATA)
            
        Returns:
            信道ID
        """
        channel_id = f"QEC-{hashlib.md5((source_gene + target_gene).encode()).hexdigest()[:8]}"
        
        self.entanglement_registry["channels"][channel_id] = {
            "source_gene": source_gene,
            "target_gene": target_gene,
            "channel_type": channel_type,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self._save_entanglement_registry()
        return channel_id
    
    def process_file(self, file_path: str, model_id: str, entity_type: str) -> Tuple[str, List[str]]:
        """
        处理文件，添加量子基因编码和更新路径
        
        Args:
            file_path: 文件路径
            model_id: 模型ID
            entity_type: 实体类型
            
        Returns:
            量子基因编码和创建的纠缠信道列表
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查文件是否已有量子基因编码
            existing_gene = re.search(QG_PATTERN, content)
            quantum_gene = None
            
            if existing_gene:
                quantum_gene = existing_gene.group(0)
                print(f"文件已有量子基因编码: {quantum_gene}")
            else:
                # 生成新的量子基因编码
                file_name = os.path.basename(file_path)
                dir_name = os.path.dirname(file_path)
                
                metadata = {
                    "file_name": file_name,
                    "dir_name": dir_name,
                    "file_size": os.path.getsize(file_path),
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                
                quantum_gene = self.generate_quantum_gene(model_id, entity_type, metadata)
                
                # 注册量子基因
                self.register_quantum_gene("files", file_path, quantum_gene, metadata)
                
                # 更新文件内容，添加量子基因编码
                if file_path.endswith(('.py', '.js', '.ts')):
                    # 代码文件：添加到文件注释
                    if '"""' in content[:200] or "'''" in content[:200]:
                        # Python文件，已有文档字符串
                        pattern = r'("""|\'\'\')'
                        matches = list(re.finditer(pattern, content[:500]))
                        if len(matches) >= 2:
                            insert_pos = matches[1].end()
                            content = content[:insert_pos] + f"\n\n量子基因编码: {quantum_gene}\n" + content[insert_pos:]
                    elif '//' in content[:200]:
                        # JavaScript/TypeScript文件
                        lines = content.split('\n')
                        comment_end = 0
                        for i, line in enumerate(lines):
                            if line.strip() and not line.strip().startswith('//'):
                                comment_end = i
                                break
                        lines.insert(comment_end, f"// 量子基因编码: {quantum_gene}")
                        content = '\n'.join(lines)
                    else:
                        # 没有现成的注释，添加新的注释
                        if file_path.endswith('.py'):
                            content = f'"""\n量子基因编码: {quantum_gene}\n"""\n\n' + content
                        else:
                            content = f'// 量子基因编码: {quantum_gene}\n\n' + content
                
                elif file_path.endswith(('.md', '.txt')):
                    # Markdown/文本文件：添加到文件开头
                    if content.startswith('#'):
                        # Markdown文件标题之后
                        lines = content.split('\n')
                        title_end = 0
                        for i, line in enumerate(lines):
                            if line.startswith('#'):
                                title_end = i
                            elif line.strip() and not line.startswith('#'):
                                break
                        lines.insert(title_end + 1, f"\n> 量子基因编码: {quantum_gene}\n")
                        content = '\n'.join(lines)
                    else:
                        # 普通文本文件
                        content = f"> 量子基因编码: {quantum_gene}\n\n" + content
                
                # 写入更新后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"已添加量子基因编码: {quantum_gene} 到 {file_path}")
            
            # 建立与相关文件的量子纠缠信道
            entanglement_channels = []
            
            # 查找其他相关文件并建立纠缠信道
            related_files = self._find_related_files(file_path)
            for related_file in related_files:
                if related_file in self.registry.get("files", {}):
                    related_gene = self.registry["files"][related_file]["quantum_gene"]
                    channel_id = self.create_entanglement_channel(quantum_gene, related_gene)
                    entanglement_channels.append(channel_id)
                    print(f"已创建量子纠缠信道: {channel_id} 连接 {file_path} 和 {related_file}")
            
            return quantum_gene, entanglement_channels
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            return None, []
    
    def _find_related_files(self, file_path: str) -> List[str]:
        """寻找与当前文件相关的其他文件"""
        related_files = []
        
        # 根据文件类型和内容确定相关文件
        file_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)
        
        # 同目录下的文件可能相关
        try:
            for f in os.listdir(dir_name):
                if f != file_name and os.path.isfile(os.path.join(dir_name, f)):
                    related_files.append(os.path.join(dir_name, f))
                    if len(related_files) >= 5:  # 限制相关文件数量
                        break
        except:
            pass
        
        return related_files
    
    def update_file_paths(self, file_path: str, old_paths: Dict[str, str]) -> None:
        """
        更新文件中的路径引用
        
        Args:
            file_path: 文件路径
            old_paths: 旧路径到新路径的映射
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 更新路径引用
            updated_content = content
            for old_path, new_path in old_paths.items():
                # 注意：这里的替换需要考虑不同的路径格式
                # 绝对路径
                updated_content = updated_content.replace(f'"{old_path}"', f'"{new_path}"')
                updated_content = updated_content.replace(f"'{old_path}'", f"'{new_path}'")
                
                # 相对路径
                old_rel = os.path.basename(old_path)
                new_rel = os.path.basename(new_path)
                if old_rel != new_rel:
                    updated_content = updated_content.replace(f'"{old_rel}"', f'"{new_rel}"')
                    updated_content = updated_content.replace(f"'{old_rel}'", f"'{new_rel}'")
            
            # 写入更新后的内容
            if updated_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"已更新 {file_path} 中的路径引用")
                
        except Exception as e:
            print(f"更新文件 {file_path} 中的路径时出错: {e}")
    
    def process_directory(self, directory: str, model_id_map: Dict[str, str]) -> None:
        """
        处理目录，为所有文件添加量子基因编码
        
        Args:
            directory: 目录路径
            model_id_map: 目录到模型ID的映射
        """
        for root, dirs, files in os.walk(directory):
            # 过滤掉排除的目录
            for excluded_dir in self.excluded_dirs:
                if excluded_dir in dirs:
                    dirs.remove(excluded_dir)
            
            # 跳过二进制或特殊目录
            skip_dir = False
            for part in root.split(os.sep):
                if part in self.excluded_dirs or part.startswith('.'):
                    skip_dir = True
                    break
            
            if skip_dir:
                continue
            
            # 确定当前目录的模型ID
            current_model_id = "QSM01"  # 默认
            for dir_prefix, model_id in model_id_map.items():
                if root.startswith(dir_prefix):
                    current_model_id = model_id
                    break
            
            # 处理目录中的文件
            for file in files:
                file_path = os.path.join(root, file)
                
                # 跳过二进制文件和特殊文件
                if file.endswith(('.pyc', '.exe', '.dll', '.so', '.bin', '.dat', '.gif', '.jpg', '.png', '.ico')):
                    continue
                
                # 跳过隐藏文件
                if file.startswith('.'):
                    continue
                
                # 跳过大文件
                try:
                    if os.path.getsize(file_path) > 1024 * 1024:  # 大于1MB的文件
                        print(f"跳过大文件: {file_path}")
                        continue
                except:
                    continue
                
                # 确定实体类型
                entity_type = "FILE"
                if file.endswith(('.py', '.js', '.ts', '.css', '.html')):
                    entity_type = "CODE"
                elif file.endswith(('.md', '.txt', '.rst')):
                    entity_type = "DOC"
                
                # 处理文件
                self.process_file(file_path, current_model_id, entity_type)

    def print_stats(self) -> None:
        """打印统计信息"""
        file_count = len(self.registry.get("files", {}))
        code_count = sum(1 for item in self.registry.get("files", {}).values() 
                         if item.get("quantum_gene", "").find("-CODE-") > 0)
        doc_count = sum(1 for item in self.registry.get("files", {}).values() 
                        if item.get("quantum_gene", "").find("-DOC-") > 0)
        channel_count = len(self.entanglement_registry.get("channels", {}))
        
        print(f"===== 量子基因处理统计 =====")
        print(f"处理文件总数: {file_count}")
        print(f"代码文件: {code_count}")
        print(f"文档文件: {doc_count}")
        print(f"创建的量子纠缠信道: {channel_count}")
        print(f"=============================")

    def setup_file_monitor(self):
        """设置文件系统监控"""
        class FileHandler(FileSystemEventHandler):
            def __init__(self, processor):
                self.processor = processor

            def on_created(self, event):
                if not event.is_directory:
                    self.processor.process_new_file(event.src_path)
                else:
                    self.processor.process_new_directory(event.src_path)

            def on_modified(self, event):
                if not event.is_directory:
                    self.processor.process_modified_file(event.src_path)

        # 设置监控目录
        self.observer = Observer()
        self.observer.schedule(FileHandler(self), path=".", recursive=True)
        self.observer.start()
        logging.info("文件系统监控已启动")

    def process_new_file(self, file_path: str):
        """处理新创建的文件"""
        try:
            # 检查文件类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type:
                if mime_type.startswith('image/'):
                    self.process_image(file_path)
                elif mime_type.startswith('video/'):
                    self.process_video(file_path)
                elif mime_type.startswith('text/'):
                    self.process_text_file(file_path)
                else:
                    self.process_general_file(file_path)
        except Exception as e:
            logging.error(f"处理新文件时出错: {str(e)}")

    def process_new_directory(self, dir_path: str):
        """处理新创建的目录"""
        try:
            # 为目录创建量子基因编码
            gene = self.generate_quantum_gene(dir_path, "DIR")
            self.register_quantum_gene(gene, dir_path)
            
            # 创建与父目录的量子纠缠信道
            parent_dir = os.path.dirname(dir_path)
            if parent_dir and os.path.exists(parent_dir):
                parent_gene = self.extract_quantum_gene(parent_dir)
                if parent_gene:
                    self.create_entanglement_channel(parent_gene, gene)
            
            logging.info(f"已处理新目录: {dir_path}")
        except Exception as e:
            logging.error(f"处理新目录时出错: {str(e)}")

    def process_modified_file(self, file_path: str):
        """处理修改的文件"""
        try:
            # 检查文件是否已有量子基因编码
            if not self.has_quantum_gene(file_path):
                self.process_new_file(file_path)
            else:
                # 更新文件的量子基因编码
                gene = self.extract_quantum_gene(file_path)
                if gene:
                    self.update_quantum_gene(gene, file_path)
        except Exception as e:
            logging.error(f"处理修改文件时出错: {str(e)}")

    def process_image(self, file_path: str):
        """处理图片文件"""
        try:
            gene = self.generate_quantum_gene(file_path, "IMG")
            self.register_quantum_gene(gene, file_path)
            self.add_quantum_gene_to_image(file_path, gene)
            logging.info(f"已处理图片文件: {file_path}")
        except Exception as e:
            logging.error(f"处理图片文件时出错: {str(e)}")

    def process_video(self, file_path: str):
        """处理视频文件"""
        try:
            gene = self.generate_quantum_gene(file_path, "VID")
            self.register_quantum_gene(gene, file_path)
            self.add_quantum_gene_to_video(file_path, gene)
            logging.info(f"已处理视频文件: {file_path}")
        except Exception as e:
            logging.error(f"处理视频文件时出错: {str(e)}")

    def process_text_file(self, file_path: str):
        """处理文本文件"""
        try:
            gene = self.generate_quantum_gene(file_path, "TXT")
            self.register_quantum_gene(gene, file_path)
            self.add_quantum_gene_to_text(file_path, gene)
            logging.info(f"已处理文本文件: {file_path}")
        except Exception as e:
            logging.error(f"处理文本文件时出错: {str(e)}")

    def process_general_file(self, file_path: str):
        """处理其他类型的文件"""
        try:
            gene = self.generate_quantum_gene(file_path, "GEN")
            self.register_quantum_gene(gene, file_path)
            logging.info(f"已处理通用文件: {file_path}")
        except Exception as e:
            logging.error(f"处理通用文件时出错: {str(e)}")

    def add_quantum_gene_to_image(self, file_path: str, gene: str):
        """为图片添加量子基因编码"""
        # 这里可以添加图片处理逻辑，例如在图片元数据中添加量子基因编码
        pass

    def add_quantum_gene_to_video(self, file_path: str, gene: str):
        """为视频添加量子基因编码"""
        # 这里可以添加视频处理逻辑，例如在视频元数据中添加量子基因编码
        pass

    def add_quantum_gene_to_text(self, file_path: str, gene: str):
        """为文本文件添加量子基因编码"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果文件已经有量子基因编码，先移除
            content = re.sub(self.QG_PATTERN, '', content)
            
            # 添加新的量子基因编码
            new_content = f"量子基因编码: {gene}\n\n{content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            logging.error(f"添加量子基因编码到文本文件时出错: {str(e)}")

    def has_quantum_gene(self, file_path: str) -> bool:
        """检查文件是否已有量子基因编码"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return bool(re.search(self.QG_PATTERN, content))
        except:
            return False

    def update_quantum_gene(self, old_gene: str, file_path: str):
        """更新文件的量子基因编码"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换旧的量子基因编码
            new_gene = self.generate_quantum_gene(file_path, "UPD")
            new_content = re.sub(old_gene, new_gene, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # 更新注册表
            self.register_quantum_gene(new_gene, file_path)
        except Exception as e:
            logging.error(f"更新量子基因编码时出错: {str(e)}")

    def stop_monitoring(self):
        """停止文件系统监控"""
        self.observer.stop()
        self.observer.join()
        logging.info("文件系统监控已停止")


# 测试和使用示例
if __name__ == "__main__":
    processor = QuantumGeneProcessor()
    
    # 定义模型ID映射
    model_id_map = {
        "docs/QSM": "QSM01",
        "docs/WeQ": "WEQ01",
        "docs/SOM": "SOM01",
        "docs/quantum_core": "QCORE01",
        "docs/quantum_shared": "QSHARE01",
        "docs/Ref": "REF01",
        "QSM": "QSM01",
        "WeQ": "WEQ01",
        "SOM": "SOM01",
        "quantum_core": "QCORE01",
        "quantum_shared": "QSHARE01",
        "Ref": "REF01",
        "api": "API01",
        "frontend": "UI01",
    }
    
    # 定义旧路径到新路径的映射
    old_paths = {
        "docs/quantum_reflection": "docs/Ref",
        "quantum_reflection": "Ref",
    }
    
    # 处理整个项目
    print("开始处理QSM项目，添加量子基因编码和量子纠缠信道...")
    processor.process_directory(".", model_id_map)
    
    # 更新路径引用
    print("更新路径引用...")
    for file_path in processor.registry.get("files", {}):
        processor.update_file_paths(file_path, old_paths)
    
    # 打印统计信息
    processor.print_stats() 
"""
量子基因编码: QE-QUA-C77E9902E9C4
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""