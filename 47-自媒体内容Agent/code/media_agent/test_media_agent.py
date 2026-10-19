#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第47篇配套 · test_media_agent.py
验证：选题/人设脚本/平台适配/配图提示词/合规自检/排期

运行: python test_media_agent.py
"""

from media_agent import (
    generate_topics, generate_script, PERSONAS, PLATFORM_FORMATS,
    generate_cover_prompt, compliance_check, build_schedule, demo,
)


def main():
    print("=" * 66)
    print("🧪 自媒体内容Agent测试")
    print("=" * 66)

    # 1. 选题
    print("\n[1] 选题生成：")
    topics = generate_topics("AI工具", 7)
    assert len(topics) == 7
    topics30 = generate_topics("副业变现", 30)
    assert len(topics30) == 30
    print(f"   7天：{len(topics)} 条｜30天：{len(topics30)} 条")
    print(f"   D1：{topics[0]}")

    # 2. 人设脚本
    print("\n[2] 人设脚本：")
    assert len(PERSONAS) == 5
    for persona in PERSONAS:
        s = generate_script(topics[0], persona, "小红书")
        assert s["persona"] == persona and s["script"]
        print(f"   ✅ {persona}：{s['tone']}")

    # 3. 平台适配
    print("\n[3] 平台格式：")
    assert len(PLATFORM_FORMATS) == 4
    for platform, fmt in PLATFORM_FORMATS.items():
        s = generate_script("测试选题", "干货型", platform)
        print(f"   {platform}：{fmt['length']}｜{fmt['style']}")
        assert s["length"] == fmt["length"]
    # 不同平台生成不同格式
    a = generate_script("X", "干货型", "小红书")
    b = generate_script("X", "干货型", "公众号")
    assert a["length"] != b["length"]

    # 4. 配图
    print("\n[4] 配图提示词：")
    for style in ["科技蓝", "暖橙成长", "极简黑白"]:
        p = generate_cover_prompt(topics[0], style)
        assert style and "3:4" in p
        print(f"   ✅ {style}")

    # 5. 合规
    print("\n[5] 合规自检：")
    ok = compliance_check("这个方法很实用，建议收藏")
    assert ok["passed"] and ok["risk"] == "低"
    bad = compliance_check("最赚钱、百分百有效、零风险")
    assert not bad["passed"] and len(bad["violations"]) >= 3
    assert "***" in bad["fixed_text"] or "收益不错" in bad["fixed_text"]
    print(f"   正常内容：通过")
    print(f"   违规内容：{bad['violations']} → 已替换")
    print(f"   风险等级：{bad['risk']}")

    # 6. 排期
    print("\n[6] 排期：")
    rows = build_schedule(topics)
    assert len(rows) == 7 and all("date" in r and "platform" in r for r in rows)
    print(f"   {rows[0]['date']} {rows[0]['platform']}｜{rows[0]['topic'][:20]}...")

    print("\n[7] 完整演示：")
    demo()

    print("\n✅ 自媒体内容Agent测试通过")


if __name__ == "__main__":
    main()
