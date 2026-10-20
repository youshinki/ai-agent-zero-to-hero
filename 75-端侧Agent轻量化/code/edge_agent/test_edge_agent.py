#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第75篇配套 · test_edge_agent.py
"""

from edge_agent import (
    Device,
    ModelSelector,
    EdgeCloudRouter,
    compare_edge_cloud,
    demo,
)


def main():
    print("=" * 66)
    print("🧪 端侧Agent轻量化测试")
    print("=" * 66)

    print("\n[1] 量化：")
    fp16 = ModelSelector.estimate_memory("phi3-mini", "FP16")
    int8 = ModelSelector.estimate_memory("phi3-mini", "INT8")
    int4 = ModelSelector.estimate_memory("phi3-mini", "INT4")
    assert fp16 > int8 > int4
    print(f"   FP16 {fp16}G → INT8 {int8}G → INT4 {int4}G")

    print("\n[2] 设备选型：")
    phone = Device("手机", 4, 64)
    r = ModelSelector.recommend(phone, "simple")
    assert r["model"] is not None
    low = Device("低端设备", 0.5, 8)
    r2 = ModelSelector.recommend(low)
    assert r2["model"] is None
    print(f"   手机→{r['model']}；低端→云端")

    print("\n[3] 端云路由：")
    d = Device("手机", 6, 64, online=True)
    router = EdgeCloudRouter(d, local_model="qwen2-1.5b")
    r1 = router.answer("你好")
    r2 = router.answer("请深度分析这份复杂报告并给出完整方案、风险评估和落地建议")
    assert r1["route"] == "edge"
    assert r2["route"] == "cloud"
    assert router.stats["edge"] == 1 and router.stats["cloud"] == 1
    print(f"   简单→{r1['route']}，复杂→{r2['route']}")

    print("\n[4] 离线降级：")
    off = Device("手机", 6, 64, online=False)
    router_off = EdgeCloudRouter(off, local_model="qwen2-0.5b")
    r = router_off.answer("你好")
    assert r["route"] == "edge" and "离线" in r["reason"]
    router_none = EdgeCloudRouter(off, local_model=None)
    r = router_none.answer("你好")
    assert r["route"] == "error"
    print(f"   ✅ 离线兜底 / 无模型友好提示")

    print("\n[5] 对比：")
    rows = compare_edge_cloud()
    assert len(rows) == 3
    assert rows[2]["cost_per_1k"] > 0
    print("   ✅ 端侧/云端 延迟成本隐私对比")

    print("\n[6] 演示：")
    demo()
    print("\n✅ 端侧轻量化测试通过")


if __name__ == "__main__":
    main()
