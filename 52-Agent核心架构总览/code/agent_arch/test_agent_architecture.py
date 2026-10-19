#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第52篇配套 · test_agent_architecture.py
"""

from agent_architecture import (
    Agent, LLM, Perception, Planner, MemoryModule, ToolModule,
    Reflection, Executor, PATTERNS, demo,
)


def main():
    print("=" * 66)
    print("🧪 Agent 核心架构测试")
    print("=" * 66)

    print("\n[1] 组件：")
    assert LLM().think("x").startswith("[mock-llm]")
    assert Perception().parse("帮我写报告")["intent"] == "task"
    assert len(Planner().plan("目标")) == 5
    m = MemoryModule(); m.remember("a"); m.remember("b", True)
    assert m.recall("a") == ["a"]
    t = ToolModule()
    assert "搜索结果" in t.call("search", "q")
    assert "计算结果：3" in t.call("calc", "1+2")
    assert Reflection().check("短") == ["内容过短"]
    assert len(Executor().run(["收集"], t)) == 1
    print("   ✅ 7大组件全部可用")

    print("\n[2] 完整链路：")
    r = Agent().run("帮我整理周报")
    stages = [x[0] for x in r["trace"]]
    assert stages == ["感知", "记忆", "规划", "执行", "反思", "沉淀"]
    print(f"   链路：{' → '.join(stages)}")

    print("\n[3] 四范式：")
    assert len(PATTERNS) == 4
    print(f"   ✅ {', '.join(PATTERNS)}")

    print("\n[4] 演示：")
    demo()
    print("\n✅ 架构测试通过")


if __name__ == "__main__":
    main()
