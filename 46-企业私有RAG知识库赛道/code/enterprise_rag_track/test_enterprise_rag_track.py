#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第46篇配套 · test_enterprise_rag_track.py
验证：客户画像/价值话术/报价/RAG问答/交付流程/复购点

运行: python test_enterprise_rag_track.py
"""

from enterprise_rag_track import (
    CLIENT_PROFILES, VALUE_MAP, PRICING, MiniRAG,
    DELIVERY_FLOW, REVENUE_POINTS, demo,
)


def main():
    print("=" * 66)
    print("🧪 企业私有RAG赛道方案测试")
    print("=" * 66)

    # 1. 客户画像
    print(f"\n[1] 客户画像：{len(CLIENT_PROFILES)} 类")
    assert len(CLIENT_PROFILES) == 6
    for name, info in CLIENT_PROFILES.items():
        assert info["pain"] and info["need"]
    print("   ✅ 6类画像完整（痛点/需求/付费意愿）")

    # 2. 价值话术
    print(f"\n[2] 痛点方案：{len(VALUE_MAP)} 组")
    assert len(VALUE_MAP) == 4
    for pain, info in VALUE_MAP.items():
        assert "solution" in info and "script" in info
    print("   ✅ 痛点→方案→话术完整")

    # 3. 报价
    print(f"\n[3] 分级报价：{len(PRICING)} 档")
    assert "轻量基础版" in PRICING and "长期托管运维" in PRICING
    print(f"   轻量：{PRICING['轻量基础版']['price']}")
    print(f"   标准：{PRICING['企业标准版']['price']}")

    # 4. RAG 问答
    print("\n[4] 私有RAG演示：")
    rag = MiniRAG()
    rag.add("手册.txt", "考勤规则：每日9:00-18:00，迟到超过30分钟扣半天工资。")
    rag.add("报价.txt", "标准版定价19800元，支持20个用户。")
    a1 = rag.answer("考勤规则是什么")
    print(f"   {a1[:60]}...")
    assert "考勤" in a1
    a2 = rag.answer("股票代码是多少")
    print(f"   无关问题：{a2}")
    assert "暂无" in a2

    # 5. 交付与复购
    print(f"\n[5] 交付流程：{len(DELIVERY_FLOW)} 步")
    print(f"   复购点：{len(REVENUE_POINTS)} 个")
    assert len(DELIVERY_FLOW) == 6 and len(REVENUE_POINTS) == 5

    print("\n[6] 完整演示：")
    demo()

    print("\n✅ 企业私有RAG赛道方案测试通过")


if __name__ == "__main__":
    main()
