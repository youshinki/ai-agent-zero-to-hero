#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第71篇配套完整项目代码 · vector_db.py
向量库选型与性能调优：索引策略、分片、过滤查询、召回排查

  1. Flat / IVF / HNSW 索引策略模拟与对比
  2. 分片（哈希分片）
  3. 过滤查询（pre/post filter）
  4. 召回瓶颈诊断
  5. 参数调优建议
==========================================================================
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple


# ======================================================================
# 一、向量数据
# ======================================================================

def random_vec(dim: int = 128, seed: int = 0) -> List[float]:
    rnd = random.Random(seed)
    v = [rnd.gauss(0, 1) for _ in range(dim)]
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class Doc:
    def __init__(self, doc_id: int, vec: List[float], metadata: Dict):
        self.id = doc_id
        self.vec = vec
        self.metadata = metadata


# ======================================================================
# 二、索引实现
# ======================================================================

class FlatIndex:
    """暴力搜索：100%召回，速度慢"""
    name = "Flat"
    
    def __init__(self, docs: List[Doc]):
        self.docs = docs
    
    def search(self, q: List[float], top_k: int = 5,
               filter_fn=None) -> List[Tuple[int, float]]:
        scored = []
        for d in self.docs:
            if filter_fn and not filter_fn(d.metadata):
                continue
            scored.append((d.id, cosine(q, d.vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


class IVFIndex:
    """倒排聚类：先找最近簇再搜索，召回略降、速度更快"""
    name = "IVF"
    
    def __init__(self, docs: List[Doc], n_clusters: int = 4):
        self.docs = docs
        self.n_clusters = n_clusters
        self.centroids = [random_vec(128, seed=100 + i) for i in range(n_clusters)]
        self.buckets: Dict[int, List[Doc]] = {i: [] for i in range(n_clusters)}
        for d in docs:
            self.buckets[self._assign(d.vec)].append(d)
    
    def _assign(self, vec: List[float]) -> int:
        return max(range(self.n_clusters),
                   key=lambda i: cosine(vec, self.centroids[i]))
    
    def search(self, q: List[float], top_k: int = 5, n_probe: int = 1,
               filter_fn=None) -> List[Tuple[int, float]]:
        clusters = sorted(range(self.n_clusters),
                          key=lambda i: cosine(q, self.centroids[i]),
                          reverse=True)[:n_probe]
        scored = []
        for c in clusters:
            for d in self.buckets[c]:
                if filter_fn and not filter_fn(d.metadata):
                    continue
                scored.append((d.id, cosine(q, d.vec)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


class HNSWIndex:
    """分层导航图（简化模拟）：精度高、速度快"""
    name = "HNSW"
    
    def __init__(self, docs: List[Doc], m: int = 8):
        self.docs = docs
        self.m = m
        self.graph = self._build_graph()
    
    def _build_graph(self) -> Dict[int, List[int]]:
        graph = {}
        for d in self.docs:
            neighbors = sorted(
                (other.id for other in self.docs if other.id != d.id),
                key=lambda oid: cosine(d.vec, self._vec_of(oid)),
                reverse=True,
            )[:self.m]
            graph[d.id] = neighbors
        return graph
    
    def _vec_of(self, doc_id: int) -> List[float]:
        return next(d.vec for d in self.docs if d.id == doc_id)
    
    def search(self, q: List[float], top_k: int = 5,
               ef: int = 20) -> List[Tuple[int, float]]:
        # 入口：随机开始，贪心扩展
        entry = self.docs[0].id
        visited = {entry}
        candidates = [(entry, cosine(q, self._vec_of(entry)))]
        for _ in range(ef):
            candidates.sort(key=lambda x: x[1], reverse=True)
            current = candidates[0][0]
            expanded = False
            for nb in self.graph.get(current, []):
                if nb in visited:
                    continue
                visited.add(nb)
                candidates.append((nb, cosine(q, self._vec_of(nb))))
                expanded = True
            if not expanded:
                break
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]


# ======================================================================
# 三、分片
# ======================================================================

class ShardedIndex:
    """按ID哈希分片"""
    def __init__(self, docs: List[Doc], shards: int = 4):
        self.shards = [[] for _ in range(shards)]
        for d in docs:
            self.shards[d.id % shards].append(d)
        self.shard_count = shards
    
    def search(self, q: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        all_scored = []
        for shard in self.shards:
            for d in shard:
                all_scored.append((d.id, cosine(q, d.vec)))
        all_scored.sort(key=lambda x: x[1], reverse=True)
        return all_scored[:top_k]
    
    def size_distribution(self) -> List[int]:
        return [len(s) for s in self.shards]


# ======================================================================
# 四、召回诊断
# ======================================================================

def diagnose(symptom: str) -> Dict:
    table = {
        "召回少": ["检查 top_k 是否过小", "检查过滤条件是否过严",
                 "检查分片是否漏查", "检查 embedding 维度是否匹配"],
        "相关性差": ["更换 embedding 模型", "优化分块策略",
                  "增加重排序", "清洗文档噪声"],
        "查询慢": ["切换 IVF/HNSW 索引", "增加分片/节点",
                 "降低 top_k", "开启缓存"],
        "内存高": ["使用 PQ 量化", "分片存储", "清理冗余向量"],
    }
    return {"symptom": symptom, "suggestions": table.get(symptom, [])}


TUNING = {
    "Flat": {"recall": "100%", "speed": "慢", "memory": "高",
             "适合": "数据量<10万、高精度"},
    "IVF": {"recall": "95-99%", "speed": "快", "memory": "中",
            "适合": "大规模、可接受少量精度损失"},
    "HNSW": {"recall": "98-100%", "speed": "极快", "memory": "高",
             "适合": "高性能、精度速度平衡"},
}


def demo():
    print("=" * 66)
    print("🗄️ 向量库选型与调优演示")
    print("=" * 66)
    
    docs = [Doc(i, random_vec(128, i), {"tag": "a" if i % 2 else "b"})
            for i in range(200)]
    query = random_vec(128, 999)
    
    print("\n[1] 索引对比（Top5）：")
    for index in [FlatIndex(docs), IVFIndex(docs, 4), HNSWIndex(docs, 6)]:
        t0 = time.time()
        res = index.search(query, 5)
        ms = (time.time() - t0) * 1000
        print(f"   {index.name:5s} {ms:7.2f}ms → {[r[0] for r in res]}")
    
    print("\n[2] 过滤查询（只查tag=a）：")
    flat = FlatIndex(docs)
    res = flat.search(query, 3, filter_fn=lambda m: m["tag"] == "a")
    print(f"   {[r[0] for r in res]}")
    
    print("\n[3] 分片：")
    sharded = ShardedIndex(docs, 4)
    print(f"   分片大小：{sharded.size_distribution()}")
    res = sharded.search(query, 3)
    print(f"   Top3：{[r[0] for r in res]}")
    
    print("\n[4] 召回诊断：")
    for symptom in ["召回少", "查询慢"]:
        d = diagnose(symptom)
        print(f"   {symptom}：{d['suggestions'][:2]}")
    
    print("\n[5] 选型建议：")
    for name, info in TUNING.items():
        print(f"   {name}：召回{info['recall']}｜速度{info['speed']}｜{info['适合']}")


if __name__ == "__main__":
    demo()
