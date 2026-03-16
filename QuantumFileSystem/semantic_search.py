#!/usr/bin/env python3
"""
量子语义搜索引擎
版本: 0.1.0
描述: 基于QEntL设计的语义搜索引擎

核心特性：
1. 自然语言查询
2. 多维索引搜索
3. 同义词扩展
4. 量子叠加态搜索
"""

import re
import time
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import threading

@dataclass
class SearchResult:
    """搜索结果"""
    file_id: str
    title: str
    content_summary: str
    matched_paragraphs: List[str]
    relevance_score: float
    matched_keywords: List[str]
    categories: List[str]
    metadata: Dict = field(default_factory=dict)

@dataclass
class SearchOptions:
    """搜索选项"""
    query: str
    filters: Dict = field(default_factory=dict)
    sort_by: str = "相关性"  # 相关性、日期、重要性
    max_results: int = 50
    offset: int = 0
    highlight: bool = True
    include_metadata: bool = True
    time_range: Optional[Tuple[float, float]] = None
    relevance_threshold: float = 0.6
    expand_synonyms: bool = True

@dataclass
class SearchStats:
    """搜索统计"""
    total_matches: int
    search_time_ms: int
    query_parse_time_ms: int
    retrieval_time_ms: int
    ranking_time_ms: int
    cache_hit: bool
    result_distribution: Dict[str, int] = field(default_factory=dict)

class QuantumSemanticSearch:
    """量子语义搜索引擎"""
    
    def __init__(self, quantum_file_system):
        self.qfs = quantum_file_system
        
        # 索引状态
        self.inverted_index: Dict[str, List[str]] = defaultdict(list)  # 关键词 -> 文件ID列表
        self.file_keywords: Dict[str, List[str]] = {}  # 文件ID -> 关键词列表
        
        # 搜索缓存
        self.cache: Dict[str, Tuple[List[SearchResult], float]] = {}
        self.cache_max_size = 1000
        self.cache_expire_seconds = 3600
        
        # 查询历史
        self.query_history: List[Dict] = []
        
        # 同义词库（可扩展）
        self.synonyms = {
            "quantum": ["量子", "quantum", "叠加态", "superposition"],
            "file": ["文件", "file", "文档", "document"],
            "search": ["搜索", "search", "查找", "find", "query"],
            "system": ["系统", "system", "体系"],
            "data": ["数据", "data", "信息", "information"],
        }
        
        # 量子搜索参数
        self.quantum_superposition_depth = 3
        self.quantum_retrieval_threshold = 0.75
        
        # 线程锁
        self._lock = threading.RLock()
        
        print("🔍 量子语义搜索引擎初始化完成")
    
    def build_index(self):
        """构建倒排索引"""
        with self._lock:
            self.inverted_index.clear()
            
            for file_id, semantic_index in self.qfs.semantic_indices.items():
                keywords = semantic_index.keywords
                self.file_keywords[file_id] = keywords
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if file_id not in self.inverted_index[keyword_lower]:
                        self.inverted_index[keyword_lower].append(file_id)
            
            print(f"📊 索引构建完成: {len(self.inverted_index)} 关键词")
    
    def search(self, options: SearchOptions) -> Tuple[List[SearchResult], SearchStats]:
        """执行语义搜索"""
        start_time = time.time()
        
        # 检查缓存
        cache_key = self._get_cache_key(options)
        if cache_key in self.cache:
            cached_results, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_expire_seconds:
                stats = SearchStats(
                    total_matches=len(cached_results),
                    search_time_ms=0,
                    query_parse_time_ms=0,
                    retrieval_time_ms=0,
                    ranking_time_ms=0,
                    cache_hit=True
                )
                return cached_results, stats
        
        # 解析查询
        parse_start = time.time()
        query_tokens = self._tokenize(options.query)
        expanded_tokens = self._expand_synonyms(query_tokens) if options.expand_synonyms else query_tokens
        parse_time = int((time.time() - parse_start) * 1000)
        
        # 检索
        retrieval_start = time.time()
        candidate_files = self._retrieve(expanded_tokens)
        retrieval_time = int((time.time() - retrieval_start) * 1000)
        
        # 排序
        ranking_start = time.time()
        results = self._rank(candidate_files, expanded_tokens, options)
        ranking_time = int((time.time() - ranking_start) * 1000)
        
        # 过滤低相关性结果
        results = [r for r in results if r.relevance_score >= options.relevance_threshold]
        
        # 应用偏移和限制
        total_matches = len(results)
        results = results[options.offset:options.offset + options.max_results]
        
        total_time = int((time.time() - start_time) * 1000)
        
        # 缓存结果
        self._cache_result(cache_key, results)
        
        # 记录查询历史
        self.query_history.append({
            "query": options.query,
            "time": time.time(),
            "results": len(results)
        })
        
        stats = SearchStats(
            total_matches=total_matches,
            search_time_ms=total_time,
            query_parse_time_ms=parse_time,
            retrieval_time_ms=retrieval_time,
            ranking_time_ms=ranking_time,
            cache_hit=False
        )
        
        return results, stats
    
    def quantum_search(self, query: str, depth: int = 3) -> List[SearchResult]:
        """量子叠加态搜索"""
        # 在多个维度同时搜索
        results = []
        
        # 第一层：精确匹配
        exact_options = SearchOptions(query=query, relevance_threshold=0.9)
        exact_results, _ = self.search(exact_options)
        results.extend(exact_results)
        
        # 第二层：语义扩展
        if depth >= 2:
            expanded_query = self._expand_query_semantic(query)
            semantic_options = SearchOptions(query=expanded_query, relevance_threshold=0.7)
            semantic_results, _ = self.search(semantic_options)
            for r in semantic_results:
                if r.file_id not in [sr.file_id for sr in results]:
                    results.append(r)
        
        # 第三层：关联搜索
        if depth >= 3:
            related_options = SearchOptions(query=query, relevance_threshold=0.5)
            related_results, _ = self.search(related_options)
            for r in related_results:
                if r.file_id not in [sr.file_id for sr in results]:
                    results.append(r)
        
        return results
    
    def _tokenize(self, query: str) -> List[str]:
        """分词"""
        # 简单分词：按空格和标点分割
        tokens = re.findall(r'\w+', query.lower())
        return tokens
    
    def _expand_synonyms(self, tokens: List[str]) -> List[str]:
        """扩展同义词"""
        expanded = set(tokens)
        
        for token in tokens:
            for key, synonyms in self.synonyms.items():
                if token in synonyms or token == key:
                    expanded.update(synonyms)
        
        return list(expanded)
    
    def _expand_query_semantic(self, query: str) -> str:
        """语义扩展查询"""
        tokens = self._tokenize(query)
        expanded_tokens = self._expand_synonyms(tokens)
        return " ".join(expanded_tokens)
    
    def _retrieve(self, tokens: List[str]) -> List[str]:
        """检索候选文件"""
        candidate_scores: Dict[str, int] = defaultdict(int)
        
        for token in tokens:
            if token in self.inverted_index:
                for file_id in self.inverted_index[token]:
                    candidate_scores[file_id] += 1
        
        # 按分数排序
        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return [f[0] for f in sorted_candidates]
    
    def _rank(self, file_ids: List[str], tokens: List[str], 
              options: SearchOptions) -> List[SearchResult]:
        """排序搜索结果"""
        results = []
        
        for file_id in file_ids:
            if file_id not in self.qfs.file_descriptors:
                continue
            
            descriptor = self.qfs.file_descriptors[file_id]
            semantic = self.qfs.semantic_indices.get(file_id)
            
            if not semantic:
                continue
            
            # 计算相关性分数
            matched_keywords = []
            score = 0.0
            
            for token in tokens:
                if token.lower() in [k.lower() for k in semantic.keywords]:
                    score += 1.0
                    matched_keywords.append(token)
            
            if semantic.keywords:
                score = score / len(semantic.keywords) * 2  # 归一化
            
            # 时间衰减
            if options.time_range:
                start_time, end_time = options.time_range
                if start_time <= descriptor.modified_time <= end_time:
                    score *= 1.2
                else:
                    score *= 0.8
            
            # 创建搜索结果
            result = SearchResult(
                file_id=file_id,
                title=descriptor.path,
                content_summary=f"量子状态: {descriptor.quantum_state}",
                matched_paragraphs=[],
                relevance_score=min(score, 1.0),
                matched_keywords=matched_keywords,
                categories=semantic.categories,
            )
            
            results.append(result)
        
        # 排序
        if options.sort_by == "相关性":
            results.sort(key=lambda x: x.relevance_score, reverse=True)
        elif options.sort_by == "日期":
            results.sort(key=lambda x: self.qfs.file_descriptors[x.file_id].modified_time, reverse=True)
        
        return results
    
    def _get_cache_key(self, options: SearchOptions) -> str:
        """生成缓存键"""
        key_str = f"{options.query}_{options.max_results}_{options.relevance_threshold}_{options.expand_synonyms}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _cache_result(self, key: str, results: List[SearchResult]):
        """缓存结果"""
        with self._lock:
            if len(self.cache) >= self.cache_max_size:
                # 删除最旧的缓存
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (results, time.time())
    
    def get_stats(self) -> Dict:
        """获取搜索引擎统计"""
        return {
            "index_size": len(self.inverted_index),
            "indexed_files": len(self.file_keywords),
            "cache_size": len(self.cache),
            "query_history_size": len(self.query_history),
            "synonym_groups": len(self.synonyms),
        }


def main():
    """演示语义搜索"""
    from quantum_file_system import QuantumFileSystem
    
    print("=" * 60)
    print("🔍 量子语义搜索引擎 v0.1.0")
    print("=" * 60)
    
    # 创建文件系统和搜索引警
    qfs = QuantumFileSystem("./qfs_search_demo")
    search_engine = QuantumSemanticSearch(qfs)
    
    print("\n📝 创建测试文件...")
    
    # 创建测试文件
    qfs.create_file("quantum/intro.txt", b"Quantum computing uses quantum mechanics for computation", "心")
    qfs.create_file("quantum/file_system.txt", b"Quantum file system stores data in superposition states", "乾坤")
    qfs.create_file("docs/search.txt", b"Semantic search understands the meaning of queries", "天")
    qfs.create_file("docs/data.txt", b"Data storage and retrieval in quantum systems", "火")
    
    print("\n🔍 构建索引...")
    search_engine.build_index()
    
    print("\n🔎 测试搜索...")
    
    # 测试搜索
    options = SearchOptions(query="quantum data", max_results=10)
    results, stats = search_engine.search(options)
    
    print(f"\n📊 搜索统计:")
    print(f"  总匹配数: {stats.total_matches}")
    print(f"  搜索时间: {stats.search_time_ms}ms")
    print(f"  缓存命中: {stats.cache_hit}")
    
    print(f"\n📋 搜索结果 ({len(results)} 个):")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.title}")
        print(f"     相关度: {result.relevance_score:.2f}")
        print(f"     匹配关键词: {result.matched_keywords}")
    
    print("\n🔮 测试量子搜索...")
    quantum_results = search_engine.quantum_search("quantum", depth=3)
    print(f"量子搜索结果: {len(quantum_results)} 个")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    main()
