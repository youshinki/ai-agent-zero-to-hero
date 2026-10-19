#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第49篇配套 · test_personal_assistant.py
验证：档案抽取/日程/笔记/习惯/简报/个性化回复

运行: python test_personal_assistant.py
"""

from datetime import datetime, timedelta

from personal_assistant import (
    Memory, Scheduler, PersonalAssistant, demo,
)


def main():
    print("=" * 66)
    print("🧪 个人专属AI助理测试")
    print("=" * 66)

    # 1. 档案抽取
    print("\n[1] 档案抽取：")
    m = Memory()
    m.extract_profile("我是一名AI开发者，喜欢简洁的回答风格，每天写代码")
    print(f"   {m.profile}")
    assert "身份" in m.profile and "偏好" in m.profile and "习惯" in m.profile

    # 2. 日程
    print("\n[2] 日程管理：")
    s = Scheduler()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    s.add(tomorrow, "09:30", "团队周会", "high")
    s.add(tomorrow, "14:00", "客户演示", "high")
    assert len(s.today(tomorrow)) == 2
    assert s.pending() == s.events
    assert s.mark_done("团队周会")
    print(f"   明日日程：{[e['title'] for e in s.today(tomorrow)]}")
    print(f"   已完成标记：{s.events[0]['done']}")

    # 3. 笔记
    print("\n[3] 笔记检索：")
    m.add_note("RAG笔记", "先扩召再重排", ["RAG", "检索"])
    m.add_note("成本笔记", "缓存+路由+压缩", ["成本"])
    hits = m.search_notes("RAG")
    assert len(hits) == 1 and hits[0]["title"] == "RAG笔记"
    print(f"   搜「RAG」：{len(hits)}条")

    # 4. 助理完整流程
    print("\n[4] 助理完整交互：")
    pa = PersonalAssistant()
    r = pa.handle("我是一名产品经理，喜欢简洁风格")
    assert "产品经理" in pa.memory.profile.get("身份", "")
    print(f"   档案：{pa.memory.profile}")
    r2 = pa.handle("明天 10:00 需求评审")
    assert "已添加日程" in r2
    print(f"   {r2}")
    r3 = pa.handle("记笔记：评审要点是边界清晰")
    assert "已保存" in r3
    r4 = pa.handle("搜笔记 评审")
    assert "评审" in r4
    print(f"   {r4}")

    # 5. 简报
    print("\n[5] 每日简报：")
    briefing = pa.daily_briefing()
    for key in ["每日简报", "今日日程", "待办", "档案"]:
        assert key in briefing
    print("   ✅ 简报含日程/待办/档案")

    # 6. 个性化
    print("\n[6] 个性化回复：")
    r5 = pa.handle("帮我总结今天的收获")
    assert "简洁" in r5
    print(f"   {r5}")

    print("\n[7] 完整演示：")
    demo()

    print("\n✅ 个人专属AI助理测试通过")


if __name__ == "__main__":
    main()
