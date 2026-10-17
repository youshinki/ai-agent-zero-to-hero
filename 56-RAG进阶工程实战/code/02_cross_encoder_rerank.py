# -*- coding: utf-8 -*-
# Cross-Encoder 精排：对粗排候选做 query-document 全交互打分
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")


def rerank(query, candidates, top_k=4):
    # candidates: [(doc_id, text, fused_score), ...]
    pairs = [(query, text) for _, text, _ in candidates]
    scores = reranker.predict(pairs)   # 0~1 相关度
    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True,
    )
    return ranked[:top_k]   # 精排后只取 3~4 条喂给大模型
