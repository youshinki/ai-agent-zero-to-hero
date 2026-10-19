#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第68篇配套 · test_observability.py
"""

import time

from observability import (
    Tracer, StructuredLogger, Metrics, AlertRules, demo,
)


def main():
    print("=" * 66)
    print("🧪 链路可观测测试")
    print("=" * 66)

    print("\n[1] 调用链：")
    tracer = Tracer()
    root = tracer.start_span("agent.run", "t1")
    child = tracer.start_span("llm.chat", "t1", "agent.run")
    time.sleep(0.002)
    child.finish(model="m")
    root.finish()
    spans = tracer.trace("t1")
    assert len(spans) == 2 and spans[1].parent_id == "agent.run"
    assert spans[1].duration_ms > 0
    print(f"   ✅ 父子Span，耗时{spans[0].duration_ms}ms")

    print("\n[2] 日志关联：")
    lg = StructuredLogger()
    lg.log("info", "t1", "开始", user="a")
    lg.log("error", "t1", "失败", code=500)
    lg.log("info", "t2", "其他")
    assert len(lg.by_trace("t1")) == 2
    print("   ✅ 按trace聚合")

    print("\n[3] 指标：")
    m = Metrics()
    for i, lat in enumerate([100, 200, 300, 400, 1500]):
        m.record(f"t{i}", lat, i < 4, tokens=100)
    s = m.summary()
    assert s["count"] == 5
    assert s["error_rate"] == "20.0%"
    assert s["p95_latency_ms"] >= 1500 or s["p95_latency_ms"] == 1500
    print(f"   {s}")

    print("\n[4] 告警：")
    alerts = AlertRules.evaluate({
        "error_rate": "8%", "p95_latency_ms": 1500, "total_tokens": 20000})
    assert len(alerts) == 3
    assert any(a["level"] == "critical" for a in alerts)
    no_alerts = AlertRules.evaluate({
        "error_rate": "1%", "p95_latency_ms": 300, "total_tokens": 100})
    assert no_alerts == []
    print(f"   ✅ 触发{len(alerts)}条告警，正常指标无告警")

    print("\n[5] 空指标：")
    assert Metrics().summary() == {"count": 0}

    print("\n[6] 演示：")
    demo()
    print("\n✅ 可观测测试通过")


if __name__ == "__main__":
    main()
