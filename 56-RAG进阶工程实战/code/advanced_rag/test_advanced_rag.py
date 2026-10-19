#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第56篇配套 · test_advanced_rag.py
"""

from advanced_rag import (
    Doc, tokenize, BM25, VectorIndex, rrf_fuse,
    CrossEncoderReranker, mmr, demo,
)


def main():
    print("=" * 66)
    print("🧪 RAG 进阶工程测试")
    print("=" * 66)

    print("\n[1] 分词：")
    tokens = tokenize("RAG检索retrieval")
    assert "rag" in tokens and "retrieval" in tokens
    print(f"   ✅ {tokens[:6]}...")

    docs = [
        Doc("d1", "RAG 通过检索私有资料增强生成，显著降低幻觉"),
        Doc("d2", "混合检索结合 BM25 关键词与向量语义，提升召回"),
        Doc("d3", "RRF 融合多路检索结果，无需分数归一化"),
        Doc("d4", "Cross-Encoder 重排对查询与文档联合打分"),
    ]
    doc_map = {d.id: d for d in docs}

    print("\n[2] BM25：")
    bm = BM25(docs)
    rank = bm.search("混合检索提升召回", 4)
    assert rank[0][0] == "d2"
    print(f"   Top1：{rank[0][0]}")

    print("\n[3] 向量：")
    vi = VectorIndex(docs)
    vrank = vi.search("混合检索提升召回", 4)
    assert len(vrank) == 4
    print(f"   Top1：{vrank[0][0]}")

    print("\n[4] RRF 融合：")
    fused = rrf_fuse([rank, vrank])
    assert len(fused) == 4
    print(f"   Top3：{[i for i, _ in fused[:3]]}")

    print("\n[5] 重排：")
    rr = CrossEncoderReranker()
    reranked = rr.rerank("混合检索提升召回", [i for i, _ in fused], doc_map, 2)
    assert reranked[0][0] == "d2"
    print(f"   Top1：{reranked[0][0]}")

    print("\n[6] MMR：")
    q_vec = VectorIndex._embed("混合检索提升召回")
    vecs = {d.id: VectorIndex._embed(d.content) for d in docs}
    picked = mmr(q_vec, [i for i, _ in reranked] + ["d1", "d3"], vecs, top_k=3)
    assert len(picked) == 3 and len(set(picked)) == 3
    print(f"   多样性结果：{picked}")

    print("\n[7] 演示：")
    demo()
    print("\n✅ RAG 进阶测试通过")


if __name__ == "__main__":
    main()
