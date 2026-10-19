#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第53篇配套 · test_react_agent.py
"""

from react_agent import (
    Tools, parse_output, ReActAgent, REACT_PROMPT, demo,
)


def main():
    print("=" * 66)
    print("🧪 ReAct 模式测试")
    print("=" * 66)

    print("\n[1] 工具：")
    t = Tools()
    assert "搜索结果" in t.call("search", "q")
    assert "计算结果：1+2 = 3" in t.call("calculator", "1+2")
    assert "北京天气" in t.call("get_weather", "北京")
    assert "未知工具" in t.call("nope", "x")
    assert "计算结果" in t.describe() or "calculator" in t.describe()
    print("   ✅ 3工具 + 工具描述")

    print("\n[2] 解析器：")
    assert parse_output("Final Answer: 42")["type"] == "final"
    p = parse_output("Thought: 查天气\nAction: get_weather | 北京")
    assert p["type"] == "action" and p["tool"] == "get_weather"
    assert parse_output("Thought: 想想")["type"] == "thought"
    print("   ✅ Final/Action/Thought 解析")

    print("\n[3] 完整循环：")
    agent = ReActAgent(verbose=False)
    r = agent.run("北京天气怎么样")
    assert r["ok"] and "北京天气" in r["answer"]
    print(f"   天气 → {r['answer'][:40]}")

    r = agent.run("计算 (128+64)*3")
    assert r["ok"] and "576" in r["answer"]
    print(f"   计算 → {r['answer'][:40]}")

    r = agent.run("搜索AI资料")
    assert r["ok"] and "搜索结果" in r["answer"]
    print(f"   搜索 → {r['answer'][:40]}")

    print("\n[4] 最大步数兜底：")
    agent2 = ReActAgent(max_steps=1, verbose=False)
    # 第一步就是 action，步数用尽
    r = agent2.run("北京天气")
    assert r["ok"] is False or len(r["steps"]) == 1
    print(f"   {r['answer'][:30]}")

    print("\n[5] Prompt 模板：")
    assert "{tools}" in REACT_PROMPT and "{question}" in REACT_PROMPT

    print("\n[6] 演示：")
    demo()
    print("\n✅ ReAct 测试通过")


if __name__ == "__main__":
    main()
