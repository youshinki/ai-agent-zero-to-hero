#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第59篇配套 · test_multi_agent.py
"""

from multi_agent import (
    Agent, MessageBus, Pipeline, Debate, Hierarchical, mock_agents, demo,
)


def main():
    print("=" * 66)
    print("🧪 多Agent协作架构测试")
    print("=" * 66)

    print("\n[1] 消息总线：")
    bus = MessageBus()
    bus.publish("a", "hello", "b")
    bus.publish("a", "broadcast")
    assert len(bus.read("b")) == 2
    assert len(bus.read("a")) == 0
    print("   ✅ 定向/广播/不回读自己")

    print("\n[2] 流水线：")
    a1 = Agent("a", "研究", lambda t: f"研究[{t}]")
    a2 = Agent("b", "写作", lambda t: f"写作[{t}]")
    a3 = Agent("c", "审核", lambda t: f"审核[{t}]")
    p = Pipeline([a1, a2, a3])
    r = p.run("任务")
    assert len(r["log"]) == 3
    assert r["log"][1]["input"] == r["log"][0]["output"]
    assert "审核" in r["final"]
    print(f"   3步传递：{r['final']}")

    print("\n[3] 审议：")
    judge = Agent("judge", "裁决", lambda t: f"裁决（{len(t)}字）")
    d = Debate([a1, a2], judge)
    r = d.run("问题")
    assert len(r["opinions"]) == 2 and "裁决" in r["verdict"]
    print(f"   {r['verdict']}")

    print("\n[4] 层级仲裁：")
    manager = Agent("m", "管理",
                    lambda t: "子A；子B" if "拆解" in t else f"汇总：{t[:20]}")
    h = Hierarchical(manager, [a1, a2])
    r = h.run("目标")
    assert len(r["subtasks"]) == 2 and len(r["results"]) == 2
    assert "汇总" in r["final"]
    print(f"   子任务：{r['subtasks']}")

    print("\n[5] 演示：")
    demo()
    print("\n✅ 多Agent协作测试通过")


if __name__ == "__main__":
    main()
