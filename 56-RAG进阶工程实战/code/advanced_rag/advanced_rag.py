#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
第56篇配套完整项目代码 · advanced_rag.py
RAG 进阶工程：混合检索、召回偏差与检索重排

  1. BM25 关键词检索
  2. 向量语义检索（bigram 近似）
  3. RRF 融合排序
  4. Cross-Encoder 重排（模拟）
  5. MMR 多样性去重
==========================================================================
"""

import math
import re
from collections import Counter
from typing import Dict, List, Tuple


# ======================================================================
# 一、文档与分词
# ======================================================================

def tokenize(text: str) -> List[str]:
    """中文：单字 + bigram；英文/数字：按词"""
    text = text.lower()
    zh = re.findall(r"[\u4e00-\u9fa5]+", text)
    en = re.findall(r"[a-z0-9]+", text)
    tokens = en[:]
    for seg in zh:
        tokens.extend(seg)
        tokens.extend(seg[i:i+2] for i in range(len(seg) - 1))
    return tokens


class Doc:
    def __init__(self, doc_id: str, content: str):
        self.id = doc_id
        self.content = content
        self.tokens = tokenize(content)


# ======================================================================
# 二、BM25
# ======================================================================

class BM25:
    def __init__(self, docs: List[Doc], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.df = Counter()
        for d in docs:
            for t in set(d.tokens):
                self.df[t] += 1
        self.avgdl = sum(len(d.tokens) for d in docs) / max(len(docs), 1)
        self.N = len(docs)
    
    def score(self, query: str, doc: Doc) -> float:
        q_tokens = tokenize(query)
        tf = Counter(doc.tokens)
        s = 0.0
        for t in q_tokens:
            if tf[t] == 0:
                continue
            idf = math.log(1 + (self.N - self.df[t] + 0.5) / (self.df[t] + 0.5))
            denom = tf[t] + self.k1 * (1 - self.b + self.b * len(doc.tokens) / (self.avgdl or 1))
            s += idf * tf[t] * (self.k1 + 1) / denom
        return s
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        scored = [(d.id, self.score(query, d)) for d in self.docs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# ======================================================================
# 三、向量检索（bigram 哈希）
# ======================================================================

class VectorIndex:
    DIM = 256
    
    def __init__(self, docs: List[Doc]):
        self.docs = docs
        self.vectors = {d.id: self._embed(d.content) for d in docs}
    
    @classmethod
    def _embed(cls, text: str) -> List[float]:
        vec = [0.0] * cls.DIM
        for t in tokenize(text):
            h = hash(t)
            vec[abs(h) % cls.DIM] += 1.0 if h >= 0 else -1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
    
    @staticmethod
    def _cos(a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        q = self._embed(query)
        scored = [(d.id, self._cos(q, self.vectors[d.id])) for d in self.docs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# ======================================================================
# 四、RRF 融合
# ======================================================================

def rrf_fuse(rankings: List[List[Tuple[str, float]]], k: int = 60) -> List[Tuple[str, float]]:
    """Reciprocal Rank Fusion：无需归一化分数"""
    scores: Dict[str, float] = {}
    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ======================================================================
# 五、交叉编码器重排（模拟）
# ======================================================================

class CrossEncoderReranker:
    """模拟 Cross-Encoder：对 (query, doc) 联合打分"""
    
    @staticmethod
    def score(query: str, content: str) -> float:
        q_tokens = set(tokenize(query))
        c_tokens = set(tokenize(content))
        if not q_tokens:
            return 0.0
        overlap = len(q_tokens & c_tokens) / len(q_tokens)
        # 长文档轻微惩罚
        length_penalty = 1.0 / (1 + len(content) / 1000)
        return round(overlap * (0.8 + 0.2 * length_penalty), 4)
    
    def rerank(self, query: str, doc_ids: List[str],
               doc_map: Dict[str, Doc], top_k: int = 3) -> List[Tuple[str, float]]:
        scored = [(i, self.score(query, doc_map[i].content)) for i in doc_ids]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# ======================================================================
# 六、MMR 多样性
# ======================================================================

def mmr(query_vec, candidate_ids, vectors, lambda_: float = 0.7,
        top_k: int = 3) -> List[str]:
    selected: List[str] = []
    candidates = list(candidate_ids)
    while candidates and len(selected) < top_k:
        best, best_score = None, -1e9
        for cid in candidates:
            rel = sum(x * y for x, y in zip(query_vec, vectors[cid]))
            div = max((sum(x * y for x, y in zip(vectors[cid], vectors[s]))
                       for s in selected), default=0.0)
            score = lambda_ * rel - (1 - lambda_) * div
            if score > best_score:
                best, best_score = cid, score
        selected.append(best)
        candidates.remove(best)
    return selected


# ======================================================================
# 演示
# ======================================================================

def demo():
    docs = [
        Doc("d1", "RAG 通过检索私有资料增强生成，显著降低幻觉"),
        Doc("d2", "混合检索结合 BM25 关键词与向量语义，提升召回"),
        Doc("d3", "RRF 融合多路检索结果，无需分数归一化"),
        Doc("d4", "Cross-Encoder 重排对查询与文档联合打分，精度更高"),
        Doc("d5", "MMR 多样性算法避免召回内容重复冗余"),
        Doc("d6", "上下文压缩可降低 Token 消耗，防止窗口溢出"),
    ]
    doc_map = {d.id: d for d in docs}
    query = "混合检索怎么提升召回"
    
    bm25 = BM25(docs)
    vec = VectorIndex(docs)
    bm25_rank = bm25.search(query, 5)
    vec_rank = vec.search(query, 5)
    
    print("=" * 66)
    print("🔬 RAG 进阶工程演示")
    print("=" * 66)
    print(f"\n查询：{query}")
    print(f"\n[BM25] {[(i, round(s,3)) for i,s in bm25_rank]}")
    print(f"[向量] {[(i, round(s,3)) for i,s in vec_rank]}")
    
    fused = rrf_fuse([bm25_rank, vec_rank])
    print(f"\n[RRF融合] {[(i, round(s,4)) for i,s in fused[:5]]}")
    
    reranker = CrossEncoderReranker()
    reranked = reranker.rerank(query, [i for i, _ in fused[:5]], doc_map, 3)
    print(f"\n[重排] {[(i, s) for i, s in reranked]}")
    
    q_vec = VectorIndex._embed(query)
    vecs = {d.id: VectorIndex._embed(d.content) for d in docs}
    diversified = mmr(q_vec, [i for i, _ in reranked], vecs, top_k=2)
    print(f"\n[MMR多样性] {diversified}")
    
    print(f"\n最终结果：")
    for doc_id in diversified:
        print(f"   [{doc_id}] {doc_map[doc_id].content}")


if __name__ == "__main__":
    demo()
