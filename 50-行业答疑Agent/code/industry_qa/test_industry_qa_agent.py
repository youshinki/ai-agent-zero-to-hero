#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第50篇配套 · test_industry_qa_agent.py
验证：多行业/FAQ匹配/知识检索/免责声明/线索捕获/报价

运行: python test_industry_qa_agent.py
"""

from industry_qa_agent import INDUSTRY_KB, IndustryQAAgent, demo


def main():
    print("=" * 66)
    print("🧪 行业答疑Agent测试")
    print("=" * 66)

    # 1. 四行业
    print("\n[1] 支持行业：")
    assert len(INDUSTRY_KB) == 4
    for name, info in INDUSTRY_KB.items():
        assert info["expert"] and info["disclaimer"] and info["entries"] and info["faq"]
        print(f"   ✅ {name}（{info['expert']}，{len(info['entries'])}条知识，{len(info['faq'])}条FAQ）")

    # 2. FAQ 匹配
    print("\n[2] FAQ匹配：")
    agent = IndustryQAAgent("法律")
    q, expected = INDUSTRY_KB["法律"]["faq"][0]
    r = agent.ask(q)
    assert r["type"] == "answer" and expected[:10] in r["answer"]
    print(f"   问：{q}")
    print(f"   答：{r['answer'][:50]}...")

    # 3. 知识检索
    print("\n[3] 知识检索：")
    r = agent.ask("竞业限制最长多久")
    assert r["type"] == "answer" and "2年" in r["answer"]
    print(f"   答：{r['answer'][:60]}...")

    # 4. 免责声明
    print("\n[4] 免责声明：")
    assert "disclaimer" in r
    print(f"   ✅ {r['disclaimer']}")

    # 5. 线索捕获
    print("\n[5] 线索捕获：")
    agent2 = IndustryQAAgent("AI")
    r = agent2.ask("你们怎么收费？")
    assert r["type"] == "lead" and "10000" in r["answer"]
    assert agent2.leads == 1
    print(f"   答：{r['answer'][:60]}...")

    # 6. 超边界兜底
    print("\n[6] 超边界兜底：")
    r = agent.ask("今天天气怎么样")
    assert r["type"] == "fallback"
    print(f"   答：{r['answer'][:50]}...")

    # 7. 全行业演示
    print("\n[7] 全行业演示：")
    demo()

    print("\n✅ 行业答疑Agent测试通过")


if __name__ == "__main__":
    main()
