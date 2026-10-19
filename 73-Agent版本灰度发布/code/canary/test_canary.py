#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第73篇配套 · test_canary.py
"""

import random

from canary import (
    CanaryRouter, ABTracker, ReleaseGate, ReleaseManager, demo,
)


def main():
    print("=" * 66)
    print("🧪 版本灰度发布测试")
    print("=" * 66)

    print("\n[1] 路由：")
    r = CanaryRouter(v2_weight=0.0, whitelist=["beta"])
    assert r.route() == "v1"
    assert r.route("beta") == "v2"
    r.set_weight(1.0)
    assert r.route() == "v2"
    print("   ✅ 权重0/1 + 白名单")

    print("\n[2] A/B指标：")
    t = ABTracker()
    for _ in range(100):
        t.record("v1", 100, True, converted=True)
        t.record("v2", 110, True, converted=True)
    # 制造错误
    t.record("v2", 120, False)
    m1, m2 = t.metrics("v1"), t.metrics("v2")
    assert m1["requests"] == 100 and m2["requests"] == 101
    assert m2["error_rate"] > 0
    cmp = t.compare()
    assert 9.9 <= cmp["latency_diff"] <= 10.2
    print(f"   ✅ v1错误{m1['error_rate']}% v2错误{m2['error_rate']}%")

    print("\n[3] 门槛判定：")
    gate = ReleaseGate(max_error_rate=5.0, max_latency_increase=50,
                       min_conversion_drop=-2)
    ok = gate.evaluate({"v1": {"error_rate": 1, "avg_latency": 100,
                               "conversion_rate": 20, "requests": 100},
                        "v2": {"error_rate": 2, "avg_latency": 110,
                               "conversion_rate": 21, "requests": 100},
                        "error_diff": 1, "latency_diff": 10,
                        "conversion_diff": 1})
    assert ok["pass"] and ok["decision"] == "promote"
    bad = gate.evaluate({"v1": {"error_rate": 1, "avg_latency": 100,
                                "conversion_rate": 20, "requests": 100},
                         "v2": {"error_rate": 10, "avg_latency": 300,
                                "conversion_rate": 5, "requests": 100},
                         "error_diff": 9, "latency_diff": 200,
                         "conversion_diff": -15})
    assert not bad["pass"] and bad["decision"] == "rollback"
    assert len(bad["reasons"]) == 3
    print(f"   ✅ 通过→promote，超标→rollback（{len(bad['reasons'])}条原因）")

    print("\n[4] 分阶段放量：")
    router = CanaryRouter(v2_weight=0.01)
    tracker = ABTracker()
    for _ in range(50):
        tracker.record("v1", 100, True, True)
        tracker.record("v2", 102, True, True)
    mgr = ReleaseManager(tracker, gate, router)
    assert mgr.current_weight() == 0.01
    rec = mgr.step()
    assert rec["action"] == "promote" and rec["weight"] == 0.1
    print(f"   ✅ 1% → 10%")

    print("\n[5] 自动回滚：")
    t2 = ABTracker()
    for _ in range(50):
        t2.record("v1", 100, True)
        t2.record("v2", 500, False)  # 高错误高延迟
    m2 = ReleaseManager(t2, gate, CanaryRouter(v2_weight=0.1))
    rec = m2.step()
    assert rec["action"] == "rollback"
    assert m2.router.v2_weight == 0.0
    print("   ✅ 指标超标自动回滚")

    print("\n[6] 演示：")
    random.seed(1)
    demo()
    print("\n✅ 灰度发布测试通过")


if __name__ == "__main__":
    main()
