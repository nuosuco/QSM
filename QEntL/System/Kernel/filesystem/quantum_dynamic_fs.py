#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QEntL量子动态文件系统 - 核心存储引擎
QEntL Quantum Dynamic Filesystem - Core Storage Engine

创建时间: 2026-03-18
开发者: 小趣WeQ

功能:
- 统一文件存储池
- 量子哈希索引
- 智能分类系统
- 动态视图管理
"""

import os
import hashlib
import json
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import sqlite3
import shutil

# 量子基因编码
QUANTUM_GENES = {
    "心": "\U000f2737",
    "乾坤": "\U000f2735",
    "天": "\U000f27ad",
    "火": "\U000f27ae",
    "王": "\U000f27b0",
}


@dataclass
class FileMetadata:
    """文件元数据"""
    file_hash: str           # 量子哈希值
    file_path: str           # 实际文件路径
    file_size: int           # 文件大小
    content_hash: str        # 内容哈希
    file_type: str           # 文件类型
    tags: List[str]          # 标签列表
    created_time: float      # 创建时间
    modified_time: float     # 修改时间
    access_count: int        # 访问次数
    entangled_files: List[str] = field(default_factory=list)  # 纠缠文件
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "file_hash": self.file_hash,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "content_hash": self.content_hash,
            "file_type": self.file_type,
            "tags": self.tags,
            "created_time": self.created_time,
            "modified_time": self.modified_time,
            "access_count": self.access_count,
            "entangled_files": self.entangled_files,
        }


@dataclass
class DynamicDirectory:
    """动态目录"""
    name: str                # 目录名称
    rule: str                # 分类规则
    files: List[str]         # 文件哈希列表
    children: Dict           # 子目录
    created_time: float      # 创建时间
    last_access: float       # 最后访问
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "rule": self.rule,
            "files": self.files,
            "children": {k: v.to_dict() for k, v in self.children.items()},
            "created_time": self.created_time,
            "last_access": self.last_access,
        }


class QuantumHashIndex:
    """量子哈希索引系统"""
    
    def __init__(self):
        self.hash_to_file: Dict[str, FileMetadata] = {}
        self.path_to_hash: Dict[str, str] = {}
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.type_index: Dict[str, Set[str]] = defaultdict(set)
    
    def compute_quantum_hash(self, filepath: str) -> str:
        """计算量子哈希值"""
        # 结合文件路径、大小和内容的哈希
        path_hash = hashlib.sha256(filepath.encode()).hexdigest()[:16]
        
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            size_hash = hashlib.sha256(str(size).encode()).hexdigest()[:8]
            
            # 计算内容哈希（对于小文件）
            if size < 10 * 1024 * 1024:  # < 10MB
                with open(filepath, 'rb') as f:
                    content_hash = hashlib.sha256(f.read()).hexdigest()[:16]
            else:
                # 大文件只取首尾部分
                with open(filepath, 'rb') as f:
                    head = f.read(4096)
                    f.seek(-min(4096, size), 2)
                    tail = f.read(4096)
                content_hash = hashlib.sha256(head + tail).hexdigest()[:16]
        else:
            content_hash = "0" * 16
        
        return f"QH-{path_hash}-{size_hash}-{content_hash}"
    
    def add_file(self, metadata: FileMetadata):
        """添加文件索引"""
        self.hash_to_file[metadata.file_hash] = metadata
        self.path_to_hash[metadata.file_path] = metadata.file_hash
        
        # 更新标签索引
        for tag in metadata.tags:
            self.tag_index[tag].add(metadata.file_hash)
        
        # 更新类型索引
        self.type_index[metadata.file_type].add(metadata.file_hash)
    
    def search_by_tag(self, tag: str) -> List[FileMetadata]:
        """按标签搜索"""
        hashes = self.tag_index.get(tag, set())
        return [self.hash_to_file[h] for h in hashes if h in self.hash_to_file]
    
    def search_by_type(self, file_type: str) -> List[FileMetadata]:
        """按类型搜索"""
        hashes = self.type_index.get(file_type, set())
        return [self.hash_to_file[h] for h in hashes if h in self.hash_to_file]


class IntelligentClassifier:
    """智能分类引擎"""
    
    def __init__(self):
        # 文件类型映射
        self.type_mapping = {
            '.txt': '文本文件',
            '.doc': '文档', '.docx': '文档', '.pdf': '文档',
            '.jpg': '图片', '.png': '图片', '.gif': '图片',
            '.mp3': '音频', '.wav': '音频', '.ogg': '音频',
            '.mp4': '视频', '.avi': '视频', '.mkv': '视频',
            '.py': '代码', '.js': '代码', '.qentl': '代码',
            '.json': '数据', '.xml': '数据', '.yaml': '数据',
            '.zip': '压缩包', '.tar': '压缩包', '.gz': '压缩包',
        }
        
        # 关键词分类规则
        self.keyword_rules = {
            '项目': ['项目'],
            '报告': ['报告', '总结', '汇报'],
            '设计': ['设计', 'design', 'ui', 'ux'],
            '代码': ['代码', 'code', '源码', '程序'],
            '测试': ['测试', 'test', '检验'],
            '文档': ['文档', '文档', '说明', 'readme'],
            '配置': ['配置', 'config', '设置', 'setting'],
        }
    
    def classify_file(self, filepath: str, content: str = "") -> Tuple[str, List[str]]:
        """分类文件"""
        # 获取文件类型
        _, ext = os.path.splitext(filepath)
        file_type = self.type_mapping.get(ext.lower(), '其他')
        
        # 生成标签
        tags = [file_type]
        
        # 从文件名提取标签
        filename = os.path.basename(filepath)
        for category, keywords in self.keyword_rules.items():
            for kw in keywords:
                if kw.lower() in filename.lower():
                    tags.append(category)
                    break
        
        # 从内容提取标签（如果有）
        if content:
            for category, keywords in self.keyword_rules.items():
                for kw in keywords:
                    if kw.lower() in content.lower():
                        if category not in tags:
                            tags.append(category)
                        break
        
        # 添加时间标签
        mtime = os.path.getmtime(filepath) if os.path.exists(filepath) else time.time()
        time_tag = time.strftime("%Y-%m", time.localtime(mtime))
        tags.append(time_tag)
        
        return file_type, tags
    
    def find_related_files(self, file_hash: str, index: QuantumHashIndex) -> List[str]:
        """查找相关文件（量子纠缠）"""
        if file_hash not in index.hash_to_file:
            return []
        
        metadata = index.hash_to_file[file_hash]
        related = set()
        
        # 按标签找相关文件
        for tag in metadata.tags:
            for related_hash in index.tag_index.get(tag, set()):
                if related_hash != file_hash:
                    related.add(related_hash)
        
        return list(related)


class QuantumDynamicFilesystem:
    """量子动态文件系统"""
    
    def __init__(self, storage_root: str = "/tmp/qentl_fs"):
        """初始化文件系统"""
        self.storage_root = storage_root
        self.index = QuantumHashIndex()
        self.classifier = IntelligentClassifier()
        self.dynamic_dirs: Dict[str, DynamicDirectory] = {}
        
        # 创建存储目录
        os.makedirs(storage_root, exist_ok=True)
        os.makedirs(os.path.join(storage_root, "pool"), exist_ok=True)
        os.makedirs(os.path.join(storage_root, "index"), exist_ok=True)
        
        print(f"🔮 量子动态文件系统初始化完成")
        print(f"   存储根目录: {storage_root}")
    
    # ==================== 文件操作 ====================
    
    def add_file(self, filepath: str) -> Optional[str]:
        """添加文件到存储池"""
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            return None
        
        # 计算量子哈希
        qhash = self.index.compute_quantum_hash(filepath)
        
        # 分类文件
        file_type, tags = self.classifier.classify_file(filepath)
        
        # 创建元数据
        metadata = FileMetadata(
            file_hash=qhash,
            file_path=filepath,
            file_size=os.path.getsize(filepath),
            content_hash=hashlib.sha256(open(filepath, 'rb').read()).hexdigest()[:16],
            file_type=file_type,
            tags=tags,
            created_time=time.time(),
            modified_time=os.path.getmtime(filepath),
            access_count=0,
        )
        
        # 添加到索引
        self.index.add_file(metadata)
        
        # 更新动态目录
        self._update_dynamic_dirs(metadata)
        
        print(f"✅ 文件添加成功: {os.path.basename(filepath)}")
        print(f"   类型: {file_type}, 标签: {tags}")
        
        return qhash
    
    def add_directory(self, dirpath: str) -> int:
        """添加目录下所有文件"""
        count = 0
        for root, dirs, files in os.walk(dirpath):
            for f in files:
                filepath = os.path.join(root, f)
                if self.add_file(filepath):
                    count += 1
        print(f"✅ 共添加 {count} 个文件")
        return count
    
    # ==================== 搜索功能 ====================
    
    def search(self, query: str) -> List[FileMetadata]:
        """搜索文件"""
        results = []
        query_lower = query.lower()
        
        # 在文件名中搜索
        for metadata in self.index.hash_to_file.values():
            if query_lower in os.path.basename(metadata.file_path).lower():
                results.append(metadata)
            elif query_lower in ' '.join(metadata.tags).lower():
                results.append(metadata)
        
        return results
    
    def search_by_tags(self, *tags) -> List[FileMetadata]:
        """按标签搜索"""
        results = []
        for tag in tags:
            results.extend(self.index.search_by_tag(tag))
        return list({m.file_hash: m for m in results}.values())
    
    # ==================== 动态目录 ====================
    
    def _update_dynamic_dirs(self, metadata: FileMetadata):
        """更新动态目录"""
        for tag in metadata.tags:
            if tag not in self.dynamic_dirs:
                self.dynamic_dirs[tag] = DynamicDirectory(
                    name=tag,
                    rule=f"tag:{tag}",
                    files=[],
                    children={},
                    created_time=time.time(),
                    last_access=time.time(),
                )
            
            if metadata.file_hash not in self.dynamic_dirs[tag].files:
                self.dynamic_dirs[tag].files.append(metadata.file_hash)
    
    def get_dynamic_dir(self, name: str) -> Optional[DynamicDirectory]:
        """获取动态目录"""
        return self.dynamic_dirs.get(name)
    
    def list_dynamic_dirs(self) -> List[str]:
        """列出所有动态目录"""
        return list(self.dynamic_dirs.keys())
    
    # ==================== 状态查询 ====================
    
    def get_status(self) -> Dict:
        """获取文件系统状态"""
        return {
            "total_files": len(self.index.hash_to_file),
            "total_tags": len(self.index.tag_index),
            "dynamic_dirs": len(self.dynamic_dirs),
            "storage_root": self.storage_root,
        }
    
    def save_index(self, filepath: str):
        """保存索引"""
        data = {
            "files": {h: m.to_dict() for h, m in self.index.hash_to_file.items()},
            "dynamic_dirs": {k: v.to_dict() for k, v in self.dynamic_dirs.items()},
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 索引已保存: {filepath}")


def main():
    """测试函数"""
    print("=" * 60)
    print("🚀 QEntL量子动态文件系统测试")
    print("=" * 60)
    
    # 创建文件系统
    fs = QuantumDynamicFilesystem("/tmp/qentl_fs")
    
    # 测试添加文件
    print("\n📊 测试1: 添加文件")
    
    # 创建测试文件
    test_dir = "/tmp/test_qentl_files"
    os.makedirs(test_dir, exist_ok=True)
    
    test_files = [
        ("项目报告.txt", "这是一个项目报告"),
        ("设计文档.docx", "设计方案说明"),
        ("代码文件.py", "# Python code"),
        ("配置文件.json", '{"key": "value"}'),
    ]
    
    for name, content in test_files:
        filepath = os.path.join(test_dir, name)
        with open(filepath, 'w') as f:
            f.write(content)
        fs.add_file(filepath)
    
    # 测试搜索
    print("\n📊 测试2: 搜索文件")
    results = fs.search("项目")
    for r in results:
        print(f"  找到: {r.file_path}, 标签: {r.tags}")
    
    # 测试动态目录
    print("\n📊 测试3: 动态目录")
    dirs = fs.list_dynamic_dirs()
    print(f"  动态目录: {dirs}")
    
    # 状态
    print("\n📊 文件系统状态:")
    status = fs.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 保存索引
    fs.save_index("/tmp/qentl_fs/index/filesystem_index.json")
    
    print("\n🎉 测试完成!")


if __name__ == "__main__":
    main()
