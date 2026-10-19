#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第48篇配套 · test_ecommerce_agent.py
验证：商品库/意图识别/标准化回复/人工转接/订单查询

运行: python test_ecommerce_agent.py
"""

from ecommerce_agent import (
    ProductKB, EcommerceAgent, detect_intent, query_order, demo,
)


def main():
    print("=" * 66)
    print("🧪 电商AI顾问测试")
    print("=" * 66)

    # 1. 商品库
    print("\n[1] 商品知识库：")
    kb = ProductKB()
    kb.add("P001", "智能蓝牙耳机", 299,
           {"蓝牙": "5.3", "续航": "30小时"}, 100, "1年质保")
    kb.add("P002", "无线充电宝", 149, {"容量": "20000mAh"}, 0)
    assert len(kb.all_products()) == 2
    assert kb.find_by_name("耳机")["price"] == 299
    print("   ✅ 2款商品，按名称可检索")

    # 2. 意图识别
    print("\n[2] 意图识别：")
    cases = {
        "耳机多少钱": "price",
        "续航多久": "spec",
        "有货吗": "stock",
        "保修多久": "warranty",
        "怎么退货": "return",
        "什么时候发货": "logistics",
        "有优惠吗": "discount",
    }
    for text, expected in cases.items():
        intent = detect_intent(text)
        assert intent == expected, f"{text} → {intent}，期望 {expected}"
        print(f"   ✅ {text} → {intent}")

    # 3. 标准化回复
    print("\n[3] 标准化回复：")
    agent = EcommerceAgent(kb)
    r = agent.reply("智能蓝牙耳机多少钱")
    assert "299" in r["answer"] and "亲" in r["answer"]
    print(f"   {r['answer']}")
    r2 = agent.reply("充电宝有货吗")
    assert "缺货" in r2["answer"]
    print(f"   {r2['answer']}")

    # 4. 人工转接
    print("\n[4] 人工转接：")
    r3 = agent.reply("能开发票吗？")
    assert r3["intent"] == "general" and "人工" in r3["answer"]
    assert agent.escalated == 1
    print(f"   {r3['answer']}")

    # 5. 订单查询
    print("\n[5] 订单查询：")
    print(f"   {query_order('ORD-001')}")
    print(f"   {query_order('ORD-999')}")
    assert "已发货" in query_order("ORD-001")
    assert "未查询到" in query_order("ORD-999")

    print("\n[6] 完整演示：")
    demo()

    print("\n✅ 电商AI顾问测试通过")


if __name__ == "__main__":
    main()
