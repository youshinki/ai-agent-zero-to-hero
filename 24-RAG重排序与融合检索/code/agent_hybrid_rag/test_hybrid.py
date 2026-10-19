#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第24篇配套 · test_hybrid.py
验证三段式高精度检索：
  1. 多路扩召（Top10）
  2. 双权重重排序（语义0.7 + 关键词0.3）
  3. 去重融合（剔除冗余，保留差异化信息）
并对比"纯向量检索"与"高精度检索"的排名差异。

运行: python test_hybrid.py
"""

import os

from knowledge_base.kb_core import (
    kb, INIT_RECALL_TOPK, FINAL_TOPK,
    SIMILARITY_WEIGHT, KEYWORD_WEIGHT,
)

UPLOAD_DIR = "knowledge_base/upload_doc"


DOCS = {
    "product.txt": """产品手册：智能知识库系统
本系统支持文档入库、语义检索、知识库问答。
标准版定价 19800 元，支持 20 个用户。
部署方式支持内网私有化部署。
售后提供交付后 7 天免费维护。""",
    "faq.txt": """常见问题
问：系统多少钱？
答：基础版 9800 元，标准版 19800 元，企业版 39800 元起。
问：支持哪些格式？
答：支持 txt、md、pdf、docx 四种格式。
问：数据安全吗？
答：全部数据保存在本地内网，不出网。""",
    "tech.txt": """技术架构说明
检索层采用向量语义检索，配合关键词匹配重排序。
生成层严格基于检索资料，降低幻觉。
记忆层支持长期记忆与智能压缩。""",
    "noise.txt": """其他说明
系统界面美观，操作简单，适合团队使用。
我们提供培训服务，帮助团队快速上手。
联系方式：support@example.com。""",
}


def main():
    print("=" * 68)
    print("🧪 RAG 重排序与融合检索测试")
    print("=" * 68)
    print(f"参数：扩召={INIT_RECALL_TOPK} 最终={FINAL_TOPK} "
          f"语义权重={SIMILARITY_WEIGHT} 关键词权重={KEYWORD_WEIGHT}")

    kb.clear_kb()
    for f in os.listdir(UPLOAD_DIR):
        if f.endswith((".txt", ".md", ".docx")):
            os.remove(os.path.join(UPLOAD_DIR, f))
    for name, content in DOCS.items():
        with open(os.path.join(UPLOAD_DIR, name), "w", encoding="utf-8") as f:
            f.write(content)
    log = kb.scan_all_update()
    print(f"\n[1] 入库：{len(log)} 个文件，{kb.stats()['chunks']} 个块")

    # 2. 纯向量检索 vs 双权重重排
    query = "标准版多少钱"
    print(f"\n[2] 检索：{query}")

    # 纯向量（模拟旧逻辑）
    q = kb.get_embedding(query)
    raw = [{
        "score": kb.calc_similarity(q, d["vector"]),
        "content": d["content"], "source": d["source"],
        "chunk_idx": d.get("chunk_idx", 0),
    } for d in kb.store["doc_list"]]
    raw.sort(key=lambda x: x["score"], reverse=True)

    print("\n   ❌ 纯向量检索 Top3：")
    for i, item in enumerate(raw[:3], 1):
        print(f"     {i}. [{item['score']:.4f}] {item['source']} | {item['content'][:40].replace(chr(10), ' ')}")

    # 三段式高精度
    reranked = kb.rerank_results(query, raw[:INIT_RECALL_TOPK])
    fused = kb.fuse_dup_content(reranked)

    print("\n   ✅ 双权重重排序 Top5：")
    for i, item in enumerate(reranked[:5], 1):
        print(f"     {i}. 综合{item['total_score']:.4f} "
              f"(语义{item['sim_score']:.3f}/关键词{item['keyword_score']:.3f}) "
              f"{item['source']} | {item['content'][:40].replace(chr(10), ' ')}")

    print("\n   ✅ 去重融合后最终 Top3：")
    for i, item in enumerate(fused, 1):
        print(f"     {i}. 综合{item['total_score']} {item['source']} | {item['content'][:50].replace(chr(10), ' ')}")

    # 3. 关键词排序是否把定价文档提前
    top_sources = [x["source"] for x in fused]
    print(f"\n[3] 最终来源：{top_sources}")
    assert any(s in ("faq.txt", "product.txt") for s in top_sources), "定价内容应被召回"

    # 4. 高精度格式化输出
    print("\n[4] 高精度检索格式化输出：")
    print(kb.search_high_precision("支持哪些文档格式"))

    # 5. 去重融合验证
    print("[5] 去重融合验证：")
    dup_results = [
        {"total_score": 0.9, "content": "AAAAAAAAAAAAAAAAAAAA", "source": "a"},
        {"total_score": 0.8, "content": "AAAAAAAAAAAAAAAAAAAA", "source": "b"},
        {"total_score": 0.7, "content": "BBBBBBBBBBBBBBBBBBBB", "source": "c"},
    ]
    fused_dup = kb.fuse_dup_content(dup_results)
    print(f"   输入3条（前2条完全相同）→ 输出{len(fused_dup)}条")
    assert len(fused_dup) == 2, "应剔除重复片段"

    print("\n✅ RAG 重排序与融合检索测试通过")


if __name__ == "__main__":
    main()
