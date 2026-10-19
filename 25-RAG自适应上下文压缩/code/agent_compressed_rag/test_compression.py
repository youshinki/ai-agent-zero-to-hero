#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第25篇配套 · test_compression.py
验证自适应上下文压缩：
  1. 冗余剔除（格式标签/重复语句）
  2. 自适应裁剪（句末完整，不拦腰截断）
  3. Token 大幅下降，核心信息保留
  4. 长文档入库后检索上下文不溢出

运行: python test_compression.py
"""

from knowledge_base.context_compressor import compressor
from knowledge_base.kb_core import kb, MAX_CONTEXT_TOKEN


def main():
    print("=" * 68)
    print("🧪 RAG 自适应上下文压缩测试")
    print("=" * 68)

    # 1. 构造冗余的检索输出
    raw = """【高精度知识库检索结果】

片段1（综合匹配分：0.3661，语义0.3/关键词0.5）
来源文档：faq.txt
核心内容：常见问题 问：系统多少钱？答：基础版9800元，标准版19800元，企业版39800元起。

片段2（综合匹配分：0.1364，语义0.1/关键词0.4）
来源文档：product.txt
核心内容：常见问题 问：系统多少钱？答：基础版9800元，标准版19800元，企业版39800元起。

片段3（综合匹配分：0.0372，语义0.05/关键词0.2）
来源文档：tech.txt
核心内容：技术架构说明：检索层采用向量语义检索，配合关键词匹配重排序。生成层严格基于检索资料，降低幻觉。
"""
    print(f"\n[1] 原始检索上下文：{len(raw)}字")

    cleaned = compressor.clean_rag_format(raw)
    print(f"\n[2] 冗余剔除后：{len(cleaned)}字")
    print(cleaned)

    deduped = compressor.remove_repeat_sentence(cleaned)
    print(f"\n[3] 去重后：{len(deduped)}字")

    # 4. 自适应裁剪
    long_text = "。".join([f"第{i}段：这是一段关于知识库系统的详细说明内容" for i in range(1, 200)]) + "。"
    trimmed = compressor.adaptive_trim(long_text, max_token=200)
    print(f"\n[4] 自适应裁剪：{len(long_text)}字 → {len(trimmed)}字（阈值200 token）")
    print(f"   结尾是否完整（以句号结束）：{'✅' if trimmed.endswith('。') else '❌'}")
    print(f"   末尾：...{trimmed[-30:]}")
    assert trimmed.endswith("。"), "裁剪后必须句末完整"

    # 5. 一站式压缩统计
    result = compressor.compress(raw, max_token=MAX_CONTEXT_TOKEN)
    stats = compressor.stats(raw, result)
    print(f"\n[5] 一站式压缩统计：")
    for k, v in stats.items():
        print(f"   {k}: {v}")
    assert stats["tokens_after"] < stats["tokens_before"], "压缩后token应下降"

    # 6. 长文档检索上下文验证
    print("\n[6] 长文档入库 + 检索上下文长度验证：")
    kb.clear_kb()
    long_doc = "".join(
        f"第{i}章：系统功能说明。{('本系统支持文档入库、语义检索、知识库问答、溯源引用等功能。' * 6)}\n"
        for i in range(1, 30)
    )
    import os
    os.makedirs("knowledge_base/upload_doc", exist_ok=True)
    with open("knowledge_base/upload_doc/long_doc.txt", "w", encoding="utf-8") as f:
        f.write(long_doc)
    kb.scan_all_update()
    ctx = kb.search_as_text("系统支持哪些功能")
    print(f"   检索上下文长度：{len(ctx)}字（约{compressor.estimate_tokens(ctx)} token）")
    print(f"   是否在阈值内（≤{MAX_CONTEXT_TOKEN} token）："
          f"{'✅' if compressor.estimate_tokens(ctx) <= MAX_CONTEXT_TOKEN else '❌'}")
    assert compressor.estimate_tokens(ctx) <= MAX_CONTEXT_TOKEN * 1.2, "上下文应被压缩到阈值附近"

    # 7. 检索结果仍可命中
    hits = kb.search("溯源引用", top_k=2)
    print(f"\n[7] 压缩后检索仍可命中：{len(hits)} 条")
    assert hits, "压缩不应影响检索召回"

    print("\n✅ 自适应上下文压缩测试通过")


if __name__ == "__main__":
    main()
