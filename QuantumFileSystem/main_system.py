#!/usr/bin/env python3
"""
量子动态文件系统 - 主系统整合
版本: 0.2.0
描述: 整合文件系统、语义搜索、知识网络的完整系统

核心特性：
1. 统一接口
2. 模块协同
3. 智能推荐
4. 量子加速
"""

import os
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# 导入三大核心模块
from quantum_file_system import QuantumFileSystem
from semantic_search import QuantumSemanticSearch
from knowledge_network import QuantumKnowledgeNetwork

class QuantumDynamicFileSystem:
    """量子动态文件系统主系统"""
    
    def __init__(self, root_path: str = "./qfs_main"):
        print("=" * 60)
        print("🌟 量子动态文件系统 v0.2.0")
        print("=" * 60)
        
        # 初始化三大核心模块
        self.file_system = QuantumFileSystem(root_path)
        self.search_engine = QuantumSemanticSearch(self.file_system)
        self.knowledge_network = QuantumKnowledgeNetwork()
        
        # 构建搜索索引
        self.search_engine.build_index()
        
        # 量子核心状态
        self.quantum_states = {
            "心": "\U000f2737",  # 量子意识核心
            "乾坤": "\U000f2735",  # 量子态空间
            "天": "\U000f27ad",   # 量子网络
            "火": "\U000f27ae",   # 量子能量
            "王": "\U000f27b0",   # 量子控制器
        }
        
        # 统计
        self.stats = {
            "files_created": 0,
            "files_read": 0,
            "searches_performed": 0,
            "knowledge_nodes_added": 0,
        }
        
        print("\n✅ 量子动态文件系统初始化完成")
        print(f"📁 根路径: {Path(root_path).absolute()}")
    
    def create_quantum_file(self, path: str, content: bytes, 
                           quantum_state: str = "心",
                           knowledge_labels: List[str] = None) -> Dict:
        """创建量子文件（整合三大模块）"""
        # 1. 创建文件
        descriptor = self.file_system.create_file(path, content, quantum_state)
        
        # 2. 添加到知识网络
        node = self.knowledge_network.add_node(
            content=f"文件:{path}",
            node_type="文件",
            labels=knowledge_labels or [quantum_state]
        )
        
        # 3. 更新搜索索引
        self.search_engine.build_index()
        
        self.stats["files_created"] += 1
        self.stats["knowledge_nodes_added"] += 1
        
        return {
            "file_id": descriptor.file_id,
            "knowledge_node_id": node.node_id,
            "quantum_state": quantum_state,
        }
    
    def read_quantum_file(self, file_id: str) -> Optional[bytes]:
        """读取量子文件（触发智能推荐）"""
        content = self.file_system.read_file(file_id)
        
        if content:
            self.stats["files_read"] += 1
            
            # 获取预测的相关文件
            predicted = self.file_system.get_predicted_files(file_id)
            print(f"🔮 推荐相关文件: {len(predicted)} 个")
        
        return content
    
    def smart_search(self, query: str, use_knowledge: bool = True) -> List[Dict]:
        """智能搜索（整合搜索和知识网络）"""
        from semantic_search import SearchOptions
        
        # 1. 语义搜索
        options = SearchOptions(query=query, max_results=20)
        search_results, stats = self.search_engine.search(options)
        
        # 2. 知识网络增强
        if use_knowledge:
            knowledge_nodes = self.knowledge_network.query_nodes(query)
            
            # 合并结果
            result_file_ids = {r.file_id for r in search_results}
            for node in knowledge_nodes:
                # 如果知识节点关联到文件
                related = self.knowledge_network.get_related_nodes(node.node_id)
                for rel_node in related:
                    # 查找对应的文件
                    for file_id, desc in self.file_system.file_descriptors.items():
                        if desc.path in rel_node.content:
                            if file_id not in result_file_ids:
                                result_file_ids.add(file_id)
        
        self.stats["searches_performed"] += 1
        
        # 格式化结果
        results = []
        for result in search_results:
            results.append({
                "file_id": result.file_id,
                "path": result.title,
                "relevance": result.relevance_score,
                "matched_keywords": result.matched_keywords,
            })
        
        return results
    
    def get_file_knowledge(self, file_id: str, depth: int = 2) -> Dict:
        """获取文件的知识图谱"""
        if file_id not in self.file_system.file_descriptors:
            return {}
        
        descriptor = self.file_system.file_descriptors[file_id]
        
        # 查找知识节点
        knowledge_nodes = self.knowledge_network.query_nodes(descriptor.path)
        
        result = {
            "file_id": file_id,
            "path": descriptor.path,
            "quantum_state": descriptor.quantum_state,
            "knowledge_nodes": [],
        }
        
        # 获取每个知识节点的子图
        for node in knowledge_nodes[:3]:  # 最多3个
            subgraph = self.knowledge_network.get_subgraph(node.node_id, depth)
            if subgraph:
                result["knowledge_nodes"].append({
                    "node_id": node.node_id,
                    "content": node.content,
                    "related_count": len(subgraph.nodes),
                })
        
        return result
    
    def quantum_sync(self) -> Dict:
        """量子同步（确保三大模块数据一致）"""
        # 1. 重建搜索索引
        self.search_engine.build_index()
        
        # 2. 为每个文件创建/更新知识节点
        for file_id, descriptor in self.file_system.file_descriptors.items():
            # 检查是否已有对应的知识节点
            existing_nodes = self.knowledge_network.query_nodes(descriptor.path)
            
            if not existing_nodes:
                # 创建新节点
                self.knowledge_network.add_node(
                    content=f"文件:{descriptor.path}",
                    node_type="文件",
                    labels=[descriptor.quantum_state] if descriptor.quantum_state else []
                )
        
        # 3. 清理低质量知识节点
        cleaned = self.knowledge_network.cleanup()
        
        return {
            "indexed_files": len(self.file_system.file_descriptors),
            "knowledge_nodes": len(self.knowledge_network.nodes),
            "cleaned_nodes": cleaned,
        }
    
    def get_system_stats(self) -> Dict:
        """获取系统统计"""
        fs_stats = self.file_system.get_stats()
        search_stats = self.search_engine.get_stats()
        kn_stats = self.knowledge_network.get_stats()
        
        return {
            "file_system": fs_stats,
            "search_engine": search_stats,
            "knowledge_network": kn_stats,
            "operations": self.stats,
        }
    
    def list_all_files(self) -> List[Dict]:
        """列出所有文件（增强版）"""
        files = []
        
        for file_id, descriptor in self.file_system.file_descriptors.items():
            # 获取预测
            predicted = self.file_system.get_predicted_files(file_id)
            
            files.append({
                "file_id": file_id,
                "path": descriptor.path,
                "size": descriptor.size,
                "quantum_state": descriptor.quantum_state,
                "predicted_count": len(predicted),
            })
        
        return files


def main():
    """演示量子动态文件系统"""
    print("=" * 60)
    print("🌟 量子动态文件系统 v0.2.0 - 完整演示")
    print("=" * 60)
    
    # 创建系统
    qfs = QuantumDynamicFileSystem("./qfs_main_demo")
    
    print("\n📝 创建量子文件...")
    
    # 创建文件
    result1 = qfs.create_quantum_file(
        "quantum/intro.txt", 
        b"Quantum computing uses superposition and entanglement",
        "心",
        ["量子", "计算", "叠加态"]
    )
    
    result2 = qfs.create_quantum_file(
        "docs/search.txt",
        b"Semantic search understands query meaning",
        "天",
        ["搜索", "语义", "NLP"]
    )
    
    result3 = qfs.create_quantum_file(
        "data/knowledge.txt",
        b"Knowledge graph connects related concepts",
        "乾坤",
        ["知识图谱", "概念", "关联"]
    )
    
    print("\n📖 读取文件...")
    content = qfs.read_quantum_file(result1["file_id"])
    if content:
        print(f"内容: {content[:50]}...")
    
    print("\n🔍 智能搜索...")
    results = qfs.smart_search("quantum knowledge")
    print(f"搜索结果: {len(results)} 个")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r['path']} (相关度: {r['relevance']:.2f})")
    
    print("\n📊 获取文件知识图谱...")
    knowledge = qfs.get_file_knowledge(result1["file_id"])
    print(f"文件: {knowledge.get('path', 'N/A')}")
    print(f"量子状态: {knowledge.get('quantum_state', 'N/A')}")
    print(f"知识节点: {len(knowledge.get('knowledge_nodes', []))} 个")
    
    print("\n🔄 量子同步...")
    sync_result = qfs.quantum_sync()
    print(f"索引文件: {sync_result['indexed_files']}")
    print(f"知识节点: {sync_result['knowledge_nodes']}")
    print(f"清理节点: {sync_result['cleaned_nodes']}")
    
    print("\n📈 系统统计:")
    stats = qfs.get_system_stats()
    print(f"文件系统:")
    print(f"  总文件: {stats['file_system']['total_files']}")
    print(f"  缓存命中率: {stats['file_system']['cache_hit_rate']:.2%}")
    print(f"搜索引擎:")
    print(f"  索引大小: {stats['search_engine']['index_size']}")
    print(f"知识网络:")
    print(f"  总节点: {stats['knowledge_network']['total_nodes']}")
    print(f"  总边: {stats['knowledge_network']['total_edges']}")
    
    print("\n📋 所有文件:")
    files = qfs.list_all_files()
    for f in files:
        print(f"  {f['path']} - 量子态: {f['quantum_state']} - 推荐: {f['predicted_count']} 个")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    main()
