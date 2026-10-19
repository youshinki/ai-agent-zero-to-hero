#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第71篇配套 · test_vector_db.py
"""

import random

from vector_db import (
    Doc, random_vec, cosine, FlatIndex, IVFIndex, HNSWIndex,
    ShardedIndex, diagnose, TUNING, demo,
)


def main():
    print("=" * 66)
    print("🧪 向量库选型与调优测试")
    print("=" * 66)

    random.seed(0)
    docs = [Doc(i, random_vec(128, i), {"tag": "a" if i % 2 else "b"})
            for i in range(100)]
    q = random_vec(128, 777)

    print("\n[1] Flat（100%召回）：")
    flat = FlatIndex(docs)
    res_flat = flat.search(q, 5)
    assert len(res_flat) == 5
    # 暴力结果是基准
    print(f"   Top3：{[r[0] for r in res_flat[:3]]}")

    print("\n[2] IVF（簇内搜索）：")
    ivf = IVFIndex(docs, 4)
    res_ivf = ivf.search(q, 5, n_probe=2)
    assert len(res_ivf) == 5
    print(f"   Top3：{[r[0] for r in res_ivf[:3]]}")

    print("\n[3] HNSW（图搜索）：")
    hnsw = HNSWIndex(docs, m=6)
    res_hnsw = hnsw.search(q, 5, ef=20)
    assert len(res_hnsw) == 5
    print(f"   Top3：{[r[0] for r in res_hnsw[:3]]}")

    print("\n[4] 过滤查询：")
    res_f = flat.search(q, 3, filter_fn=lambda m: m["tag"] == "a")
    assert all(next(d.metadata["tag"] for d in docs if d.id == i) == "a"
               for i, _ in res_f)
    print(f"   ✅ 过滤后只返回tag=a：{[r[0] for r in res_f]}")

    print("\n[5] 分片：")
    sh = ShardedIndex(docs, 4)
    dist = sh.size_distribution()
    assert sum(dist) == 100
    res_sh = sh.search(q, 3)
    # 分片全扫结果应与Flat一致
    assert [r[0] for r in res_sh] == [r[0] for r in flat.search(q, 3)]
    print(f"   ✅ 分片分布：{dist}，全扫结果与Flat一致")

    print("\n[6] 召回诊断：")
    d = diagnose("查询慢")
    assert len(d["suggestions"]) >= 3
    assert diagnose("未知问题")["suggestions"] == []
    print(f"   ✅ 查询慢建议：{d['suggestions'][:2]}")

    print("\n[7] 选型：")
    assert len(TUNING) == 3
    assert TUNING["Flat"]["recall"] == "100%"
    print("   ✅ 3种索引对比完整")

    print("\n[8] 演示：")
    demo()
    print("\n✅ 向量库测试通过")


if __name__ == "__main__":
    main()
