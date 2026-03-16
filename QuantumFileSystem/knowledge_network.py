#!/usr/bin/env python3
"""
量子知识网络
版本: 0.1.0
描述: 基于QEntL设计的知识图谱系统

核心特性：
1. 知识节点管理
2. 关系边构建
3. 路径查询
4. 子图提取
"""

import time
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import threading

@dataclass
class KnowledgeNode:
    """知识节点"""
    node_id: str
    content: str
    node_type: str  # 概念、实体、主题、属性等
    labels: List[str]
    reliability: float = 1.0
    created_time: float = 0.0
    updated_time: float = 0.0
    source_refs: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

@dataclass
class KnowledgeEdge:
    """知识边"""
    edge_id: str
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    confidence: float = 1.0
    bidirectional: bool = False
    evidence: List[str] = field(default_factory=list)

@dataclass
class KnowledgePath:
    """知识路径"""
    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge]
    length: int
    strength: float

@dataclass
class Subgraph:
    """子图"""
    nodes: List[KnowledgeNode]
    edges: List[KnowledgeEdge]
    center_node_id: str
    depth: int

class QuantumKnowledgeNetwork:
    """量子知识网络"""
    
    def __init__(self):
        # 存储结构
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        
        # 索引
        self.node_out_edges: Dict[str, List[str]] = defaultdict(list)  # 节点ID -> 出边ID列表
        self.node_in_edges: Dict[str, List[str]] = defaultdict(list)   # 节点ID -> 入边ID列表
        self.type_nodes: Dict[str, List[str]] = defaultdict(list)      # 类型 -> 节点ID列表
        
        # 配置
        self.config = {
            "max_nodes": 1000000,
            "max_edges": 5000000,
            "min_relation_threshold": 0.65,
            "cleanup_threshold": 0.4,
        }
        
        # 统计
        self.stats = {
            "nodes_added": 0,
            "edges_added": 0,
            "paths_queried": 0,
            "subgraphs_extracted": 0,
        }
        
        # 线程锁
        self._lock = threading.RLock()
        
        print("🧠 量子知识网络初始化完成")
    
    def add_node(self, content: str, node_type: str = "概念", 
                 labels: List[str] = None) -> KnowledgeNode:
        """添加知识节点"""
        with self._lock:
            node_id = self._generate_id()
            now = time.time()
            
            node = KnowledgeNode(
                node_id=node_id,
                content=content,
                node_type=node_type,
                labels=labels or [],
                reliability=1.0,
                created_time=now,
                updated_time=now,
            )
            
            self.nodes[node_id] = node
            self.type_nodes[node_type].append(node_id)
            self.stats["nodes_added"] += 1
            
            # 自动关联已有知识
            if len(self.nodes) > 1:
                self._auto_link_node(node)
            
            print(f"✅ 添加节点: {content[:30]}... (ID: {node_id})")
            return node
    
    def add_edge(self, source_id: str, target_id: str, 
                 relation_type: str = "关联", weight: float = 1.0,
                 bidirectional: bool = False) -> KnowledgeEdge:
        """添加知识边"""
        with self._lock:
            if source_id not in self.nodes or target_id not in self.nodes:
                raise ValueError("源节点或目标节点不存在")
            
            edge_id = self._generate_id()
            
            edge = KnowledgeEdge(
                edge_id=edge_id,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                bidirectional=bidirectional,
            )
            
            self.edges[edge_id] = edge
            self.node_out_edges[source_id].append(edge_id)
            self.node_in_edges[target_id].append(edge_id)
            self.stats["edges_added"] += 1
            
            # 如果是双向边，添加反向边
            if bidirectional:
                reverse_edge_id = self._generate_id()
                reverse_edge = KnowledgeEdge(
                    edge_id=reverse_edge_id,
                    source_id=target_id,
                    target_id=source_id,
                    relation_type=relation_type,
                    weight=weight,
                    bidirectional=True,
                )
                self.edges[reverse_edge_id] = reverse_edge
                self.node_out_edges[target_id].append(reverse_edge_id)
                self.node_in_edges[source_id].append(reverse_edge_id)
                self.stats["edges_added"] += 1
            
            return edge
    
    def query_nodes(self, query: str, max_results: int = 10) -> List[KnowledgeNode]:
        """查询相关节点"""
        with self._lock:
            results = []
            query_lower = query.lower()
            
            for node in self.nodes.values():
                # 简单的内容匹配
                score = 0.0
                content_lower = node.content.lower()
                
                if query_lower in content_lower:
                    score = 0.8
                elif any(label.lower() in query_lower for label in node.labels):
                    score = 0.6
                elif self._word_overlap(query_lower, content_lower) > 0.3:
                    score = 0.4
                
                if score >= self.config["min_relation_threshold"]:
                    results.append((node, score))
            
            # 按分数排序
            results.sort(key=lambda x: x[1], reverse=True)
            return [r[0] for r in results[:max_results]]
    
    def get_path(self, source_id: str, target_id: str, 
                 max_depth: int = 5) -> List[KnowledgePath]:
        """获取两个节点间的路径"""
        with self._lock:
            if source_id not in self.nodes or target_id not in self.nodes:
                return []
            
            # BFS搜索路径
            paths = []
            queue = [(source_id, [source_id], [])]
            visited = set()
            
            while queue and len(paths) < 10:
                current, path_nodes, path_edges = queue.pop(0)
                
                if current == target_id:
                    # 构建路径对象
                    nodes = [self.nodes[n] for n in path_nodes]
                    edges = [self.edges[e] for e in path_edges]
                    strength = sum(e.weight for e in edges) / len(edges) if edges else 0
                    
                    paths.append(KnowledgePath(
                        nodes=nodes,
                        edges=edges,
                        length=len(path_nodes) - 1,
                        strength=strength,
                    ))
                    continue
                
                if len(path_nodes) > max_depth:
                    continue
                
                # 探索邻居
                for edge_id in self.node_out_edges.get(current, []):
                    edge = self.edges[edge_id]
                    next_node = edge.target_id
                    
                    if next_node not in path_nodes:  # 避免循环
                        queue.append((
                            next_node,
                            path_nodes + [next_node],
                            path_edges + [edge_id],
                        ))
            
            self.stats["paths_queried"] += 1
            return paths
    
    def get_subgraph(self, center_id: str, depth: int = 2) -> Optional[Subgraph]:
        """获取节点的子图"""
        with self._lock:
            if center_id not in self.nodes:
                return None
            
            nodes: Set[str] = {center_id}
            edges: Set[str] = set()
            
            # BFS扩展
            current_level = {center_id}
            for _ in range(depth):
                next_level = set()
                for node_id in current_level:
                    # 出边
                    for edge_id in self.node_out_edges.get(node_id, []):
                        edge = self.edges[edge_id]
                        if edge.target_id not in nodes:
                            next_level.add(edge.target_id)
                            nodes.add(edge.target_id)
                        if edge_id not in edges:
                            edges.add(edge_id)
                    # 入边
                    for edge_id in self.node_in_edges.get(node_id, []):
                        edge = self.edges[edge_id]
                        if edge.source_id not in nodes:
                            next_level.add(edge.source_id)
                            nodes.add(edge.source_id)
                        if edge_id not in edges:
                            edges.add(edge_id)
                current_level = next_level
            
            self.stats["subgraphs_extracted"] += 1
            
            return Subgraph(
                nodes=[self.nodes[n] for n in nodes],
                edges=[self.edges[e] for e in edges],
                center_node_id=center_id,
                depth=depth,
            )
    
    def get_related_nodes(self, node_id: str, relation_type: str = None) -> List[KnowledgeNode]:
        """获取相关节点"""
        with self._lock:
            related = []
            
            # 出边目标节点
            for edge_id in self.node_out_edges.get(node_id, []):
                edge = self.edges[edge_id]
                if relation_type is None or edge.relation_type == relation_type:
                    if edge.target_id in self.nodes:
                        related.append(self.nodes[edge.target_id])
            
            # 入边源节点
            for edge_id in self.node_in_edges.get(node_id, []):
                edge = self.edges[edge_id]
                if relation_type is None or edge.relation_type == relation_type:
                    if edge.source_id in self.nodes:
                        related.append(self.nodes[edge.source_id])
            
            return related
    
    def cleanup(self) -> int:
        """清理低可靠性节点"""
        with self._lock:
            to_remove = []
            
            for node_id, node in self.nodes.items():
                if node.reliability < self.config["cleanup_threshold"]:
                    to_remove.append(node_id)
            
            for node_id in to_remove:
                self._remove_node(node_id)
            
            print(f"🧹 清理了 {len(to_remove)} 个低可靠性节点")
            return len(to_remove)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": {k: len(v) for k, v in self.type_nodes.items()},
        }
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        timestamp = str(time.time()).encode()
        random_bytes = str(hash(time.time())).encode()
        return hashlib.md5(timestamp + random_bytes).hexdigest()[:12]
    
    def _auto_link_node(self, new_node: KnowledgeNode):
        """自动关联新节点"""
        # 简单的自动关联：寻找相似内容的节点
        for node_id, node in self.nodes.items():
            if node_id == new_node.node_id:
                continue
            
            # 计算相似度
            similarity = self._word_overlap(
                new_node.content.lower(), 
                node.content.lower()
            )
            
            if similarity > 0.5:
                self.add_edge(
                    new_node.node_id, 
                    node_id, 
                    "相关", 
                    weight=similarity
                )
    
    def _word_overlap(self, text1: str, text2: str) -> float:
        """计算词汇重叠度"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _remove_node(self, node_id: str):
        """移除节点"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            
            # 从类型索引移除
            if node.node_type in self.type_nodes:
                if node_id in self.type_nodes[node.node_type]:
                    self.type_nodes[node.node_type].remove(node_id)
            
            # 移除相关边
            for edge_id in self.node_out_edges.get(node_id, []):
                self.edges.pop(edge_id, None)
            for edge_id in self.node_in_edges.get(node_id, []):
                self.edges.pop(edge_id, None)
            
            # 清理索引
            self.node_out_edges.pop(node_id, None)
            self.node_in_edges.pop(node_id, None)
            
            # 移除节点
            del self.nodes[node_id]


def main():
    """演示知识网络"""
    print("=" * 60)
    print("🧠 量子知识网络 v0.1.0")
    print("=" * 60)
    
    # 创建知识网络
    network = QuantumKnowledgeNetwork()
    
    print("\n📝 添加知识节点...")
    
    # 添加概念节点
    quantum = network.add_node("量子计算", "概念", ["计算", "物理"])
    file_system = network.add_node("文件系统", "概念", ["存储", "数据"])
    semantic = network.add_node("语义搜索", "概念", ["搜索", "NLP"])
    
    # 添加实体节点
    qubit = network.add_node("量子比特", "实体", ["量子", "比特"])
    superposition = network.add_node("叠加态", "实体", ["量子态"])
    
    print("\n🔗 添加知识边...")
    
    # 添加关系
    network.add_edge(quantum.node_id, qubit.node_id, "包含", 0.9)
    network.add_edge(quantum.node_id, superposition.node_id, "使用", 0.8)
    network.add_edge(file_system.node_id, semantic.node_id, "支持", 0.7, bidirectional=True)
    
    print("\n🔍 查询节点...")
    results = network.query_nodes("量子")
    print(f"查询 '量子' 结果: {[n.content for n in results]}")
    
    print("\n🛤️ 查询路径...")
    paths = network.get_path(quantum.node_id, superposition.node_id)
    if paths:
        path = paths[0]
        print(f"路径长度: {path.length}, 强度: {path.strength:.2f}")
        print(f"路径: {' → '.join(n.content for n in path.nodes)}")
    
    print("\n📊 提取子图...")
    subgraph = network.get_subgraph(quantum.node_id, depth=2)
    if subgraph:
        print(f"子图节点数: {len(subgraph.nodes)}")
        print(f"子图边数: {len(subgraph.edges)}")
    
    print("\n📈 网络统计:")
    stats = network.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    main()
