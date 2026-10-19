#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第72篇配套 · test_cost_monitor.py
"""

from cost_monitor import CostMonitor, demo


def main():
    print("=" * 66)
    print("🧪 成本精细化监控测试")
    print("=" * 66)

    print("\n[1] 成本计算：")
    assert CostMonitor.calc_cost("gpt-4", 1000, 0) == 0.21
    assert CostMonitor.calc_cost("qwen-turbo", 1000, 0) == 0.0015
    assert CostMonitor.calc_cost("gpt-4", 1000, 0) > CostMonitor.calc_cost(
        "deepseek-chat", 1000, 0)
    print("   ✅ gpt-4 > deepseek > qwen")

    print("\n[2] 多维度记账：")
    mon = CostMonitor(daily_budget=1.0)
    mon.record("t1", "task1", "plan", "gpt-4", 100, 50)
    mon.record("t1", "task1", "execute", "deepseek-chat", 200, 100)
    mon.record("t2", "task2", "plan", "qwen-turbo", 300, 200)
    assert mon.by_tenant["t1"]["calls"] == 2
    assert mon.by_task["task1"]["tokens"] == 450
    assert mon.by_step["plan"]["tokens"] == 650
    print(f"   ✅ 租户/任务/环节三维记账")

    print("\n[3] 异常检测：")
    mon2 = CostMonitor(daily_budget=1.0, alert_ratio=0.1)
    mon2.record("t1", "big", "execute", "gpt-4", 40000, 20000)
    alerts = mon2.check_anomaly("t1", tenant_quota=0.1)
    types = {a["type"] for a in alerts}
    assert "quota_exceeded" in types
    assert "budget_warning" in types
    assert "task_token_spike" in types
    print(f"   ✅ 检出 {len(alerts)} 类异常")

    print("\n[4] 拦截：")
    mon3 = CostMonitor(daily_budget=0.01)
    mon3.record("t1", "x", "s", "gpt-4", 500, 500)
    r = mon3.intercept("t1", 0.05)
    assert not r["allowed"]
    assert mon3.blocked == 1
    print(f"   ✅ 超预算拦截：{r['reason']}")

    print("\n[5] 配额拦截：")
    mon4 = CostMonitor(daily_budget=100)
    mon4.record("t1", "x", "s", "gpt-4", 1000, 1000)
    r = mon4.intercept("t1", 0.5, tenant_quota=0.1)
    assert not r["allowed"] and "租户配额" in r["reason"]
    print(f"   ✅ {r['reason']}")

    print("\n[6] 报表：")
    rep = mon.report()
    assert rep["calls"] == 3
    assert len(rep["tenants"]) == 2
    assert rep["top_steps"]
    print(f"   总成本¥{rep['total_cost']}，租户{len(rep['tenants'])}个")

    print("\n[7] 演示：")
    demo()
    print("\n✅ 成本监控测试通过")


if __name__ == "__main__":
    main()
