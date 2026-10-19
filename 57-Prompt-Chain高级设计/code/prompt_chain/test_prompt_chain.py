#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第57篇配套 · test_prompt_chain.py
"""

from prompt_chain import (
    ChainStep, MockLLM, PromptChain, BranchChain, COMPARISON, demo,
)


def main():
    print("=" * 66)
    print("🧪 Prompt Chain 高级设计测试")
    print("=" * 66)

    print("\n[1] 顺序链：")
    chain = PromptChain()
    chain.add(ChainStep("classify", "请对用户问题分类：{question}",
                        validate=lambda x: x in ("售前", "售后", "其他")))
    chain.add(ChainStep("extract", "提取意图：{last}",
                        validate=lambda x: x.startswith("{")))
    chain.add(ChainStep("reply", "生成回复：{last}"))
    r = chain.run({"question": "我要退款"})
    assert r["ok"] and len(r["trace"]) == 3
    print(f"   ✅ 3步全部通过：{r['output'][:30]}")

    print("\n[2] 校验失败重试：")
    chain2 = PromptChain()
    chain2.add(ChainStep("bad", "请对用户问题分类：{question}",
                         validate=lambda x: x == "永不通过",
                         fallback="降级输出", max_retry=1))
    r2 = chain2.run({"question": "x"})
    assert not r2["ok"] and r2["output"] == "降级输出"
    assert r2["trace"][0]["attempts"] == 2
    print(f"   ✅ 重试2次后降级：{r2['output']}")

    print("\n[3] 条件分支：")
    bc = BranchChain()
    cases = {
        "这个耳机多少钱": "售前",
        "我要退款": "售后",
        "你们公司在哪里": "其他",
    }
    for q, expected in cases.items():
        r = bc.run(q)
        assert r["category"] == expected
        print(f"   {q} → {r['category']}")
    # 售后分支包含 extract + reply
    r = bc.run("我要退款")
    assert len(r["branch_trace"]) == 2
    print(f"   ✅ 售前/售后/其他分支正确")

    print("\n[4] Chain vs Agent：")
    assert len(COMPARISON) == 2
    assert "固定" in COMPARISON["Chain"]["控制"]
    assert "自主" in COMPARISON["Agent"]["控制"]
    print("   ✅ 边界对比完整")

    print("\n[5] 演示：")
    demo()
    print("\n✅ Prompt Chain 测试通过")


if __name__ == "__main__":
    main()
