#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第20篇配套 · test_private_kb.py
验证：文档入库 → 语义检索 → 私有问答 → 清空

运行: python test_private_kb.py
"""

import os

from knowledge_base.kb_core import kb
from agent_core import agent


def main():
    print("=" * 64)
    print("🧪 本地私有知识库测试")
    print("=" * 64)

    # 1. 清空
    kb.clear_kb()
    print("\n[1] 清空知识库")

    # 2. 入库
    doc = "knowledge_base/upload_doc/product.txt"
    assert os.path.exists(doc), f"示例文档不存在：{doc}"
    result = kb.add_doc_file(doc)
    print(f"[2] 入库：{result}")
    print(f"    统计：{kb.stats()}")

    # 3. 检索
    print("\n[3] 语义检索测试：")
    for q in ["定价多少", "部署需要什么配置", "支持哪些文档格式"]:
        hits = kb.search(q, top_k=2)
        print(f"\n   问：{q}")
        for h in hits:
            print(f"     [{h['score']}] {h['source']}#{h['chunk_idx']}：{h['content'][:50]}...")

    # 4. Agent问答
    print("\n[4] Agent私有问答测试：")
    for q in ["标准版多少钱？", "部署要求是什么？"]:
        res = agent.run(q, [])
        print(f"\n   问：{q}")
        print(f"   答：{res['final_answer'][:200]}")

    # 5. 入库意图
    print("\n[5] 通过Agent入库意图测试：")
    res = agent.run(f"把 {doc} 加入知识库", [])
    print(f"   结果：{res['final_answer'][:100]}")

    # 6. 清空
    kb.clear_kb()
    print(f"\n[6] 清空后统计：{kb.stats()}")

    print("\n✅ 私有知识库测试完成")


if __name__ == "__main__":
    main()
