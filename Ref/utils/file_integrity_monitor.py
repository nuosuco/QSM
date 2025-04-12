import os
import json
import hashlib
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from difflib import SequenceMatcher


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Ref/logs/file_integrity.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('FileIntegrityMonitor')


class FileIntegrityMonitor:
    """
    文件完整性监控器，用于防止在多次对话中发生重复创建和不一致修改
    """
    
    def __init__(self, registry_path: str = 'file_registry.json'):
        """
        初始化文件完整性监控器
        
        Args:
            registry_path: 文件注册表路径
        """
        self.registry_path = registry_path
        self.file_registry: Dict[str, Dict] = {}
        self.modification_history: Dict[str, List[Dict]] = {}
        
        # 加载现有注册表
        self._load_registry()
        
        logger.info(f"文件完整性监控器初始化完成，注册表路径: {self.registry_path}")
    
    def _load_registry(self):
        """从文件加载注册表"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_registry = data.get('registry', {})
                    self.modification_history = data.get('history', {})
                logger.info(f"已加载文件注册表，包含 {len(self.file_registry)} 个文件记录")
            except Exception as e:
                logger.error(f"加载文件注册表失败: {str(e)}")
                # 初始化为空注册表
                self.file_registry = {}
                self.modification_history = {}
        else:
            logger.info(f"注册表文件不存在，将创建新的注册表: {self.registry_path}")
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(self.registry_path)), exist_ok=True)
    
    def _save_registry(self):
        """保存注册表到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(os.path.abspath(self.registry_path)), exist_ok=True)
            
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'registry': self.file_registry,
                    'history': self.modification_history
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"已保存文件注册表，包含 {len(self.file_registry)} 个文件记录")
            return True
        except Exception as e:
            logger.error(f"保存文件注册表失败: {str(e)}")
            return False
    
    def compute_checksum(self, content: str) -> str:
        """
        计算内容的校验和
        
        Args:
            content: 文件内容
            
        Returns:
            MD5校验和
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def register_file(self, 
                     filepath: str, 
                     content: str, 
                     purpose: str = "", 
                     dependencies: List[str] = None) -> bool:
        """
        注册文件，记录其路径、内容和用途
        
        Args:
            filepath: 文件路径
            content: 文件内容
            purpose: 文件用途描述
            dependencies: 依赖的文件列表
            
        Returns:
            是否成功注册
        """
        # 标准化路径
        filepath = os.path.normpath(filepath)
        dependencies = dependencies or []
        
        # 计算校验和
        checksum = self.compute_checksum(content)
        
        # 获取当前时间
        timestamp = datetime.now().isoformat()
        
        # 如果文件已经注册，更新记录
        if filepath in self.file_registry:
            old_checksum = self.file_registry[filepath].get('checksum', '')
            
            # 内容有变化时更新记录
            if old_checksum != checksum:
                # 添加到修改历史
                if filepath not in self.modification_history:
                    self.modification_history[filepath] = []
                
                self.modification_history[filepath].append({
                    'timestamp': timestamp,
                    'old_checksum': old_checksum,
                    'new_checksum': checksum,
                    'action': 'update'
                })
                
                logger.info(f"更新文件记录: {filepath}")
            
            # 更新注册表
            self.file_registry[filepath] = {
                'checksum': checksum,
                'purpose': purpose or self.file_registry[filepath].get('purpose', ''),
                'last_updated': timestamp,
                'dependencies': dependencies or self.file_registry[filepath].get('dependencies', [])
            }
        else:
            # 添加新文件记录
            self.file_registry[filepath] = {
                'checksum': checksum,
                'purpose': purpose,
                'created': timestamp,
                'last_updated': timestamp,
                'dependencies': dependencies
            }
            
            # 初始化修改历史
            self.modification_history[filepath] = [{
                'timestamp': timestamp,
                'old_checksum': '',
                'new_checksum': checksum,
                'action': 'create'
            }]
            
            logger.info(f"添加新文件记录: {filepath}")
        
        # 保存注册表
        return self._save_registry()
    
    def check_conflicts(self, 
                       filepath: str, 
                       proposed_content: str) -> Union[bool, List[Dict]]:
        """
        检查文件是否存在冲突
        
        Args:
            filepath: 文件路径
            proposed_content: 提议的文件内容
            
        Returns:
            - True: 如果存在同名文件且内容差异较大
            - List: 如果找到具有相似用途的文件列表
            - False: 如果没有冲突
        """
        # 标准化路径
        filepath = os.path.normpath(filepath)
        
        # 计算提议内容的校验和
        proposed_checksum = self.compute_checksum(proposed_content)
        
        # 检查同名文件
        if filepath in self.file_registry:
            existing_checksum = self.file_registry[filepath].get('checksum', '')
            
            # 如果校验和不同，计算内容相似度
            if existing_checksum != proposed_checksum:
                existing_content = self._get_file_content(filepath)
                if existing_content:
                    similarity = self._calculate_content_similarity(existing_content, proposed_content)
                    
                    # 如果相似度低于阈值，认为有冲突
                    if similarity < 0.7:
                        logger.warning(f"文件冲突: {filepath} (相似度: {similarity:.2f})")
                        return True
        
        # 检查功能相似的文件
        similar_files = self._find_similar_purpose_files(filepath, proposed_content)
        if similar_files:
            logger.info(f"找到 {len(similar_files)} 个功能相似的文件")
            return similar_files
        
        return False
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        计算两个内容字符串的相似度
        
        Args:
            content1: 第一个内容
            content2: 第二个内容
            
        Returns:
            相似度（0-1）
        """
        # 使用difflib计算相似度
        return SequenceMatcher(None, content1, content2).ratio()
    
    def _get_file_content(self, filepath: str) -> Optional[str]:
        """
        获取已注册文件的内容
        
        Args:
            filepath: 文件路径
            
        Returns:
            文件内容，如果文件不存在则返回None
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {filepath}: {str(e)}")
            return None
    
    def _find_similar_purpose_files(self, 
                                   filepath: str, 
                                   content: str) -> List[Dict]:
        """
        查找具有相似用途的文件
        
        Args:
            filepath: 文件路径
            content: 文件内容
            
        Returns:
            相似文件列表，每项包含路径和相似度
        """
        similar_files = []
        
        # 提取文件名和扩展名
        filename = os.path.basename(filepath)
        _, ext = os.path.splitext(filename)
        
        # 从内容中提取关键词
        keywords = self._extract_keywords(content)
        
        # 遍历注册表中的所有文件
        for reg_path, reg_info in self.file_registry.items():
            # 跳过同名文件
            if reg_path == filepath:
                continue
            
            # 如果扩展名相同，进一步检查
            reg_filename = os.path.basename(reg_path)
            _, reg_ext = os.path.splitext(reg_filename)
            
            if reg_ext == ext:
                # 获取已注册文件的内容
                reg_content = self._get_file_content(reg_path)
                if not reg_content:
                    continue
                
                # 计算内容相似度
                similarity = self._calculate_content_similarity(content, reg_content)
                
                # 提取注册文件的关键词
                reg_keywords = self._extract_keywords(reg_content)
                
                # 计算关键词重叠率
                keyword_overlap = len(set(keywords) & set(reg_keywords)) / max(1, len(set(keywords) | set(reg_keywords)))
                
                # 综合评分 (内容相似度和关键词重叠的加权平均)
                combined_score = 0.7 * similarity + 0.3 * keyword_overlap
                
                # 如果综合评分高于阈值，认为是相似文件
                if combined_score > 0.6:
                    similar_files.append({
                        'path': reg_path,
                        'similarity': combined_score,
                        'content_similarity': similarity,
                        'keyword_overlap': keyword_overlap,
                        'purpose': reg_info.get('purpose', '')
                    })
        
        # 按相似度降序排序
        similar_files.sort(key=lambda x: x['similarity'], reverse=True)
        
        # 只返回相似度最高的几个
        return similar_files[:5]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        从内容中提取关键词
        
        Args:
            content: 文件内容
            
        Returns:
            关键词列表
        """
        # 分割成单词
        words = re.findall(r'\b\w+\b', content.lower())
        
        # 过滤掉常见词和太短的词
        stopwords = {'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with', 'by'}
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        # 返回出现频率最高的关键词
        keyword_freq = {}
        for word in keywords:
            keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前50个高频词
        return [kw[0] for kw in sorted_keywords[:50]]
    
    def verify_dependencies(self, filepath: str) -> Tuple[bool, List[str]]:
        """
        验证文件的依赖关系
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否所有依赖都存在的元组 (success, missing_deps)
        """
        if filepath not in self.file_registry:
            logger.warning(f"文件未注册: {filepath}")
            return False, []
        
        # 获取文件依赖
        dependencies = self.file_registry[filepath].get('dependencies', [])
        missing_deps = []
        
        # 检查每个依赖
        for dep in dependencies:
            if not os.path.exists(dep):
                missing_deps.append(dep)
        
        return len(missing_deps) == 0, missing_deps
    
    def get_file_history(self, filepath: str) -> List[Dict]:
        """
        获取文件的修改历史
        
        Args:
            filepath: 文件路径
            
        Returns:
            修改历史记录列表
        """
        # 标准化路径
        filepath = os.path.normpath(filepath)
        
        if filepath in self.modification_history:
            return self.modification_history[filepath]
        else:
            logger.warning(f"文件无修改历史: {filepath}")
            return []
    
    def scan_directory(self, 
                      directory: str, 
                      recursive: bool = True) -> Dict[str, List[str]]:
        """
        扫描目录中的文件，检查已注册文件的变化和未注册的文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            包含已注册、未注册和已更改文件列表的字典
        """
        # 标准化路径
        directory = os.path.normpath(directory)
        
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.error(f"目录不存在: {directory}")
            return {
                'registered': [],
                'unregistered': [],
                'changed': []
            }
        
        registered_files = []
        unregistered_files = []
        changed_files = []
        
        # 遍历目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                # 跳过隐藏文件和某些类型的文件
                if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.so', '.dll')):
                    continue
                
                filepath = os.path.normpath(os.path.join(root, file))
                
                # 检查文件是否已注册
                if filepath in self.file_registry:
                    registered_files.append(filepath)
                    
                    # 检查内容是否变化
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        current_checksum = self.compute_checksum(content)
                        registered_checksum = self.file_registry[filepath].get('checksum', '')
                        
                        if current_checksum != registered_checksum:
                            changed_files.append(filepath)
                    except Exception as e:
                        logger.error(f"检查文件变化失败 {filepath}: {str(e)}")
                else:
                    unregistered_files.append(filepath)
            
            # 如果不递归，终止遍历
            if not recursive:
                break
        
        return {
            'registered': registered_files,
            'unregistered': unregistered_files,
            'changed': changed_files
        }

    def suggest_organization(self) -> Dict[str, Any]:
        """
        基于现有文件注册表，提出项目组织改进建议
        
        Returns:
            包含组织建议的字典
        """
        # 查找具有相同用途的文件组
        purpose_groups = {}
        
        for filepath, info in self.file_registry.items():
            purpose = info.get('purpose', '')
            if purpose:
                if purpose not in purpose_groups:
                    purpose_groups[purpose] = []
                purpose_groups[purpose].append(filepath)
        
        # 筛选出包含多个文件的用途组
        duplicate_purposes = {
            purpose: files 
            for purpose, files in purpose_groups.items() 
            if len(files) > 1
        }
        
        # 查找没有依赖关系的孤立文件
        isolated_files = []
        
        for filepath, info in self.file_registry.items():
            # 检查是否有依赖
            has_deps = len(info.get('dependencies', [])) > 0
            
            # 检查是否被其他文件依赖
            is_depended = False
            for other_path, other_info in self.file_registry.items():
                if other_path != filepath and filepath in other_info.get('dependencies', []):
                    is_depended = True
                    break
            
            # 如果既没有依赖也不被依赖，认为是孤立文件
            if not has_deps and not is_depended:
                isolated_files.append(filepath)
        
        return {
            'duplicate_purposes': duplicate_purposes,
            'isolated_files': isolated_files
        }


# 单例实例
_instance = None

def get_monitor(registry_path: str = 'file_registry.json') -> FileIntegrityMonitor:
    """
    获取文件完整性监控器的单例实例
    
    Args:
        registry_path: 注册表文件路径
        
    Returns:
        FileIntegrityMonitor实例
    """
    global _instance
    if _instance is None:
        _instance = FileIntegrityMonitor(registry_path)
    return _instance 

"""

"""
量子基因编码: QE-FIL-DF753CA4E5B1
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
"""
"""

// 开发团队：中华 ZhoHo ，Claude 
