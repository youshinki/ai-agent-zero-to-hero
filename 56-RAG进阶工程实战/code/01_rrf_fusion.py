# -*- coding: utf-8 -*-
# RRF（Reciprocal Rank Fusion）：融合 BM25 与向量两路召回，只看排名不加权
def rrf_fuse(bm25_hits, vec_hits, k=60, top_n=10):
    """
    bm25_hits: [(doc_id, score), ...] 已按分数降序
    vec_hits:  [(doc_id, score), ...] 已按分数降序
    k: RRF 平滑常数，论文默认 60
    """
    scores = {}
    for rank, (doc_id, _) in enumerate(bm25_hits):
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
    for rank, (doc_id, _) in enumerate(vec_hits):
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]
