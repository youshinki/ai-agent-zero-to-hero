#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第55篇配套 · test_context_window.py
"""

from context_window import ContextManager, estimate_tokens, demo


def main():
    print("=" * 66)
    print("🧪 上下文窗口工程测试")
    print("=" * 66)

    print("\n[1] Token估算：")
    assert estimate_tokens("你好") == 4
    assert estimate_tokens("hello") >= 2
    print(f"   ✅ 中文/英文估算")

    print("\n[2] 无溢出：")
    cm = ContextManager(max_tokens=2000)
    cm.set_system("系统提示")
    cm.add("user", "你好")
    cm.add("assistant", "你好！")
    ctx = cm.build()
    assert ctx["tokens"] <= 2000 and not ctx["truncated"]
    print(f"   {len(ctx['messages'])}条 / {ctx['tokens']}token")

    print("\n[3] 摘要压缩：")
    cm = ContextManager(max_tokens=1000, keep_recent=4)
    cm.add("user", "我是一名产品经理")
    cm.add("assistant", "好的")
    for i in range(6):
        cm.add("user", f"问题{i}")
        cm.add("assistant", f"回答{i}")
    ctx = cm.build()
    assert "身份" in ctx["summary"] and "产品经理" in ctx["summary"]
    assert len(ctx["messages"]) <= 6  # 4 recent + system/summary
    print(f"   摘要：{ctx['summary']}")

    print("\n[4] 超限截断：")
    cm = ContextManager(max_tokens=60, keep_recent=10)
    for i in range(20):
        cm.add("user", f"这是第{i}条比较长的消息内容，用于测试截断")
        cm.add("assistant", "收到")
    ctx = cm.build()
    assert ctx["tokens"] <= 60
    assert ctx["truncated"]
    print(f"   截断后 {len(ctx['messages'])} 条 / {ctx['tokens']}token")

    print("\n[5] 优先级：")
    cm = ContextManager(max_tokens=120, keep_recent=4)
    cm.set_system("系统规则")
    cm.add("user", "我是一名工程师")
    for i in range(6):
        cm.add("user", f"消息{i}" * 5)
        cm.add("assistant", "答")
    ctx = cm.build()
    assert ctx["messages"][0]["content"] == "系统规则"
    print("   ✅ 系统消息始终保留")

    print("\n[6] 演示：")
    demo()
    print("\n✅ 上下文窗口测试通过")


if __name__ == "__main__":
    main()
